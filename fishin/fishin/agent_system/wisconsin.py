"""Reproducible, fail-closed acquisition helpers for the Wisconsin pilot."""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import PurePosixPath
from typing import Callable
from urllib.parse import urljoin


LANDING_PAGE = (
    "https://dnr.wisconsin.gov/topic/fishing/sturgeon/WinnSysSturgeonSpear"
)
YEARS = tuple(range(2016, 2026))
WATERBODIES = ("Lake Winnebago", "Upriver Lakes")
SPECIES = "lake sturgeon"
MODE = "ice spearing"


@dataclass(frozen=True)
class SourceRecord:
    season_year: int
    url: str
    filename: str
    retrieval_date: str
    sha256: str
    content_type: str
    publication_date: str | None
    status: str
    reason: str | None = None


@dataclass(frozen=True)
class HarvestRow:
    season_year: int
    waterbody: str
    day_of_season: int | None
    date: str | None
    harvest_count: int | None
    license_count: int | None
    harvest_cap: int | None
    species: str
    mode: str
    source_locator: str


class _ReportLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join("".join(self._text).split())))
            self._href = None
            self._text = []


def discover_report_urls(html: str, landing_url: str = LANDING_PAGE) -> dict[int, str]:
    """Return only the DNR-linked final reports in the approved year window."""
    parser = _ReportLinkParser()
    parser.feed(html)
    found: dict[int, str] = {}
    for href, label in parser.links:
        match = re.search(r"\b(201[6-9]|202[0-5])\b", label)
        report_label = label.lower()
        if match and any(
            marker in report_label for marker in ("final", "summary", "harvest report")
        ):
            found[int(match.group(1))] = urljoin(landing_url, href)
    return dict(sorted(found.items()))


def acquire_sources(
    html: str,
    *,
    retrieval_date: str | None = None,
    downloader: Callable[[str], tuple[bytes, str]] | None = None,
) -> list[SourceRecord]:
    """Acquire report metadata; non-PDF responses are recorded, never parsed."""
    retrieved = retrieval_date or date.today().isoformat()
    download = downloader or _download
    records: list[SourceRecord] = []
    for year, url in discover_report_urls(html).items():
        payload, content_type = download(url)
        filename = PurePosixPath(url.split("?", 1)[0]).name or f"report-{year}"
        digest = hashlib.sha256(payload).hexdigest()
        is_pdf = "pdf" in content_type.lower() or payload.startswith(b"%PDF")
        records.append(
            SourceRecord(
                season_year=year,
                url=url,
                filename=filename,
                retrieval_date=retrieved,
                sha256=digest,
                content_type=content_type,
                publication_date=None,
                status="acquired" if is_pdf else "blocked",
                reason=None if is_pdf else "linked response is not a PDF",
            )
        )
    return records


def extract_season_rows(
    report_text: str, *, season_year: int, source_locator: str
) -> list[HarvestRow]:
    """Extract only explicit season totals; daily values remain absent, not zero."""
    patterns = {
        "Lake Winnebago": r"(?i)(\d[\d,]*)\s+lake sturgeon were harvested on Lake Winnebago",
        "Upriver Lakes": r"(?i)(\d[\d,]*)\s+lake sturgeon were (?:harvested|speared) on the Upriver Lakes",
    }
    rows: list[HarvestRow] = []
    for waterbody, pattern in patterns.items():
        match = re.search(pattern, report_text)
        if match:
            rows.append(
                HarvestRow(
                    season_year=season_year,
                    waterbody=waterbody,
                    day_of_season=None,
                    date=None,
                    harvest_count=int(match.group(1).replace(",", "")),
                    license_count=None,
                    harvest_cap=None,
                    species=SPECIES,
                    mode=MODE,
                    source_locator=source_locator,
                )
            )
    return rows


def audit(records: list[SourceRecord], rows: list[HarvestRow]) -> dict[str, object]:
    """Summarize support and block downstream metrics when the contract is unmet."""
    years = {record.season_year for record in records if record.status == "acquired"}
    row_keys = [(row.season_year, row.waterbody, row.day_of_season) for row in rows]
    duplicate_rows = len(row_keys) - len(set(row_keys))
    covered_years = sorted({row.season_year for row in rows})
    missing_years = [year for year in YEARS if year not in covered_years]
    separated = all(row.waterbody in WATERBODIES for row in rows)
    denominator_complete = bool(rows) and all(row.license_count is not None for row in rows)
    gates = {
        "report_links": years == set(YEARS),
        "coverage": not missing_years,
        "waterbody_separation": separated and bool(rows),
        "duplicate_free": duplicate_rows == 0,
        "denominator_semantics": denominator_complete,
        "uncertainty": False,
    }
    failed = [name for name, passed in gates.items() if not passed]
    return {
        "status": "blocked" if failed else "accepted",
        "gates": gates,
        "failed_gates": failed,
        "candidate_years": list(YEARS),
        "covered_years": covered_years,
        "missing_years": missing_years,
        "duplicate_rows": duplicate_rows,
        "rows": [asdict(row) for row in rows],
        "reason": "No baseline or rate is published until every gate passes.",
    }


def _download(url: str) -> tuple[bytes, str]:
    from urllib.request import Request, urlopen

    request = Request(url, headers={"User-Agent": "fishin-wisconsin-audit/0.1"})
    with urlopen(request, timeout=30) as response:
        return response.read(), response.headers.get("Content-Type", "")
