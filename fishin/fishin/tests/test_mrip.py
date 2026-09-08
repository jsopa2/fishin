import json
import zipfile
from pathlib import Path

import pytest

from agent_system.mrip import ExtractionError, PilotSpec, extract_archive, write_audit


def _archive(path: Path, *, duplicate: bool = False) -> None:
    catch = (
        "SP_CODE,COMMON,YEAR,WAVE,ST,MODE_FX,AREA_X,ID_CODE,STRAT_ID,PSU_ID,WP_CATCH,HARVEST\n"
        "8835440901,RED DRUM,2018,3,37,3,5,a,s,p,2,1\n"
        + ("8835440901,RED DRUM,2018,3,37,3,5,a,s,p,2,1\n" if duplicate else "")
    )
    trip = (
        "YEAR,WAVE,ST,MODE_FX,AREA_X,ID_CODE,STRAT_ID,PSU_ID,WP_INT\n"
        "2018,3,37,3,5,a,s,p,4\n"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("catch_20183.csv", catch)
        archive.writestr("trip_20183.csv", trip)


def test_extract_applies_exact_species_and_returns_auditable_point_rate(tmp_path):
    archive = tmp_path / "pilot.zip"
    _archive(archive)
    result = extract_archive(
        archive,
        spec=PilotSpec(years=(2018,), waves=(3,)),
    )

    assert result["coverage"]["available_cells"] == 1
    assert result["grain"]["orphan_catch_ids"] == 0
    cell = result["cells"][0]
    assert cell["weighted_catch"] == 2
    assert cell["weighted_trips"] == 4
    assert cell["catch_per_1000_trips"] == 500
    assert result["acceptance"]["precision"] is False


def test_duplicate_catch_records_fail_grain_check(tmp_path):
    archive = tmp_path / "duplicate.zip"
    _archive(archive, duplicate=True)

    with pytest.raises(ExtractionError, match="duplicate catches=1"):
        extract_archive(archive, spec=PilotSpec(years=(2018,), waves=(3,)))


def test_audit_writer_is_json_and_deterministic(tmp_path):
    archive = tmp_path / "pilot.zip"
    output = tmp_path / "audit.json"
    _archive(archive)
    write_audit(
        extract_archive(archive, spec=PilotSpec(years=(2018,), waves=(3,))),
        output,
    )

    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["source"]["sha256"]
    assert output.read_text(encoding="utf-8").endswith("\n")
