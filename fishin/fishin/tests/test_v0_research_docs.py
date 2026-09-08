from pathlib import Path


def test_v0_environmental_joinability_research_doc_exists() -> None:
    root = Path(__file__).resolve().parents[1]
    doc = root / "docs" / "v0-environmental-data-joinability.md"

    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    assert "V0 Environmental Data Joinability Review" in text
    assert "NOAA NWS API" in text
    assert "Open-Meteo" in text
    assert "USGS NWIS" in text
    assert "Conservative evaluation design" in text


def test_v0_pilot_slice_contract_is_explicit() -> None:
    """Verify the selected slice and extraction safeguards are documented."""
    root = Path(__file__).resolve().parents[1]
    doc = root / "docs" / "v0-pilot-slice-and-data-contract.md"

    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    for required in (
        "Wisconsin",
        "Lake Winnebago System",
        "Lake sturgeon",
        "ice spearing",
        "2016–2025",
        "Public-data contract",
        "Missingness, licensing, and reproducibility",
        "Decision gate",
        "North Carolina",
        "production",
        "prediction",
    ):
        assert required in text
