from agent_system.wisconsin import audit, discover_report_urls, extract_season_rows


def test_report_discovery_is_bounded_to_final_summaries():
    html = """
    <a href="/2016.pdf">final harvest report 2016</a>
    <a href="/2025.pdf">season summary, 2025</a>
    <a href="/2026.pdf">season summary, 2026</a>
    <a href="/other.pdf">other report 2020</a>
    """
    assert discover_report_urls(html) == {
        2016: "https://dnr.wisconsin.gov/2016.pdf",
        2025: "https://dnr.wisconsin.gov/2025.pdf",
    }


def test_extraction_preserves_missing_daily_and_denominator_values():
    rows = extract_season_rows(
        "616 lake sturgeon were harvested on Lake Winnebago. "
        "325 lake sturgeon were speared on the Upriver Lakes.",
        season_year=2025,
        source_locator="report.pdf p. 3",
    )
    assert {row.waterbody for row in rows} == {"Lake Winnebago", "Upriver Lakes"}
    assert all(row.day_of_season is None for row in rows)
    assert all(row.license_count is None for row in rows)


def test_audit_blocks_incomplete_support_and_uncertainty():
    rows = extract_season_rows(
        "616 lake sturgeon were harvested on Lake Winnebago.",
        season_year=2025,
        source_locator="report.pdf p. 3",
    )
    result = audit([], rows)
    assert result["status"] == "blocked"
    assert "coverage" in result["failed_gates"]
    assert "denominator_semantics" in result["failed_gates"]
    assert "uncertainty" in result["failed_gates"]
