"""Bounded, reproducible extraction of the Issue 8 MRIP pilot slice.

The extractor intentionally operates on user-downloaded NOAA CSV archives. It
does not silently download, impute, or replace source records.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator, Mapping


ARCHIVE_URL = (
    "https://apps-st.fisheries.noaa.gov/st1/recreational/"
    "MRIP_Survey_Data/CSV/"
)
RED_DRUM_CODE = "8835440901"
RED_DRUM_LABEL = "RED DRUM"


@dataclass(frozen=True)
class PilotSpec:
    years: tuple[int, ...] = tuple(range(2018, 2026))
    waves: tuple[int, ...] = (3, 4, 5)
    state_code: str = "37"
    state_label: str = "North Carolina"
    mode_code: str = "3"
    mode_label: str = "Shore"
    area_code: str = "5"
    area_label: str = "State waters"
    species_code: str = RED_DRUM_CODE
    species_label: str = RED_DRUM_LABEL
    catch_disposition: str = "HARVEST"


class ExtractionError(ValueError):
    """Raised when a source archive cannot satisfy the pilot contract."""


def _text(value: str | None) -> str:
    return (value or "").strip()


def _number(value: str, field: str, *, positive: bool = False) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ExtractionError(f"{field} is not numeric: {value!r}") from exc
    if positive and number <= 0:
        raise ExtractionError(f"{field} must be positive: {value!r}")
    return number


def _rows(archive: zipfile.ZipFile, member: str) -> Iterator[dict[str, str]]:
    with archive.open(member) as handle:
        reader = csv.DictReader(
            (line.decode("utf-8-sig") for line in handle),
        )
        if reader.fieldnames is None:
            raise ExtractionError(f"{member} has no header")
        reader.fieldnames = [field.strip().upper() for field in reader.fieldnames]
        for row in reader:
            yield {key.strip().upper(): _text(value) for key, value in row.items()}


def _required(row: Mapping[str, str], fields: Iterable[str], member: str) -> None:
    missing = [field for field in fields if not _text(row.get(field))]
    if missing:
        raise ExtractionError(f"{member} has missing required fields: {missing}")


def _member_map(archive: zipfile.ZipFile) -> dict[tuple[int, int, str], str]:
    members: dict[tuple[int, int, str], str] = {}
    pattern = re.compile(r"^(catch|trip)_(\d{4})(\d)\.csv$", re.I)
    for name in archive.namelist():
        match = pattern.match(Path(name).name)
        if match:
            kind, year, wave = match.groups()
            members[(int(year), int(wave), kind.lower())] = name
    return members


def _filtered(
    rows: Iterable[dict[str, str]],
    spec: PilotSpec,
    *,
    member: str,
    kind: str,
) -> list[dict[str, str]]:
    required = (
        "ID_CODE",
        "YEAR",
        "WAVE",
        "ST",
        "MODE_FX",
        "AREA_X",
        "STRAT_ID",
        "PSU_ID",
    )
    required += ("WP_INT",) if kind == "trip" else ()

    selected: list[dict[str, str]] = []
    for row in rows:
        _required(row, required, member)
        if not (
            int(row["YEAR"]) in spec.years
            and int(row["WAVE"]) in spec.waves
            and row["ST"] == spec.state_code
            and row["MODE_FX"] == spec.mode_code
            and row["AREA_X"] == spec.area_code
        ):
            continue
        if kind == "catch":
            if (
                row.get("SP_CODE") != spec.species_code
                or row.get("COMMON", "").upper() != spec.species_label
            ):
                continue
            _required(
                row,
                ("SP_CODE", "COMMON", "WP_CATCH", spec.catch_disposition),
                member,
            )
        selected.append(row)
    return selected


def _cell(rows: Iterable[dict[str, str]]) -> Counter[tuple[int, int]]:
    return Counter((int(row["YEAR"]), int(row["WAVE"])) for row in rows)


def extract_archive(
    archive_path: str | Path,
    *,
    spec: PilotSpec = PilotSpec(),
) -> dict[str, object]:
    """Extract and audit one NOAA MRIP CSV archive.

    The returned object contains only filtered source rows and cell summaries;
    it is JSON serializable and includes the archive SHA-256 for provenance.
    """

    path = Path(archive_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    expected_cells = {(year, wave) for year in spec.years for wave in spec.waves}

    with zipfile.ZipFile(path) as archive:
        members = _member_map(archive)
        available = {
            cell for cell in expected_cells if (cell[0], cell[1], "catch") in members
        }
        missing = sorted(expected_cells - available)
        catch_rows: list[dict[str, str]] = []
        trip_rows: list[dict[str, str]] = []
        for year, wave in sorted(available):
            catch_rows.extend(
                _filtered(
                    _rows(archive, members[(year, wave, "catch")]),
                    spec,
                    member=members[(year, wave, "catch")],
                    kind="catch",
                )
            )
            trip_rows.extend(
                _filtered(
                    _rows(archive, members[(year, wave, "trip")]),
                    spec,
                    member=members[(year, wave, "trip")],
                    kind="trip",
                )
            )

    trip_by_id: dict[str, dict[str, str]] = {}
    duplicate_trip_ids: list[str] = []
    for row in trip_rows:
        identifier = row["ID_CODE"]
        if identifier in trip_by_id:
            duplicate_trip_ids.append(identifier)
        trip_by_id[identifier] = row

    catch_ids = [row["ID_CODE"] for row in catch_rows]
    duplicate_catch_ids = [
        identifier for identifier, count in Counter(catch_ids).items() if count > 1
    ]
    orphan_catch_ids = sorted(set(catch_ids) - set(trip_by_id))
    if duplicate_trip_ids or duplicate_catch_ids or orphan_catch_ids:
        raise ExtractionError(
            "catch/trip grain check failed: "
            f"duplicate trips={len(duplicate_trip_ids)}, "
            f"duplicate catches={len(duplicate_catch_ids)}, "
            f"orphan catches={len(orphan_catch_ids)}"
        )

    cells: list[dict[str, object]] = []
    for year, wave in sorted(available):
        trips = [
            row for row in trip_rows
            if int(row["YEAR"]) == year and int(row["WAVE"]) == wave
        ]
        catches = [
            row for row in catch_rows
            if int(row["YEAR"]) == year and int(row["WAVE"]) == wave
        ]
        weighted_catch = (
            sum(
                _number(row[spec.catch_disposition], spec.catch_disposition)
                * _number(row["WP_CATCH"], "WP_CATCH", positive=True)
                for row in catches
            )
            if catches
            else None
        )
        weighted_trips = sum(
            _number(row["WP_INT"], "WP_INT", positive=True) for row in trips
        )
        cells.append(
            {
                "year": year,
                "wave": wave,
                "sampled_trips": len(trips),
                "disposition_trips": len(catches),
                "weighted_catch": weighted_catch,
                "weighted_trips": weighted_trips,
                "catch_per_1000_trips": (
                    1000 * weighted_catch / weighted_trips
                    if weighted_trips and weighted_catch is not None
                    else None
                ),
                "precision_status": "not_computed",
            }
        )

    return {
        "source": {
            "archive": path.name,
            "sha256": digest,
            "archive_url": ARCHIVE_URL + path.name,
        },
        "spec": asdict(spec),
        "coverage": {
            "requested_cells": len(expected_cells),
            "available_cells": len(available),
            "missing_cells": [
                {"year": year, "wave": wave} for year, wave in missing
            ],
        },
        "grain": {
            "catch_rows": len(catch_rows),
            "trip_rows": len(trip_rows),
            "duplicate_trip_ids": len(duplicate_trip_ids),
            "duplicate_catch_ids": len(duplicate_catch_ids),
            "orphan_catch_ids": len(orphan_catch_ids),
        },
        "cells": cells,
        "acceptance": {
            "coverage": not missing,
            "grain": not (
                duplicate_trip_ids or duplicate_catch_ids or orphan_catch_ids
            ),
            "cell_support": all(
                cell["sampled_trips"] >= 30 and cell["disposition_trips"] >= 10
                for cell in cells
            ) and len(cells) == len(expected_cells),
            "precision": False,
            "precision_reason": (
                "NOAA survey variance/template analysis is not implemented by "
                "this bounded extractor; point rates are not a baseline result."
            ),
        },
    }


def write_audit(result: Mapping[str, object], output_path: str | Path) -> None:
    """Write a deterministic, indented JSON audit artifact."""

    Path(output_path).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
