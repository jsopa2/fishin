from agent_system.baseline import evaluate_baseline
from pytest import approx


def _audit(*, precision: bool, cells: list[dict[str, object]]) -> dict[str, object]:
    return {
        "acceptance": {
            "coverage": True,
            "grain": True,
            "cell_support": True,
            "precision": precision,
        },
        "cells": cells,
    }


def _cell(year: int, wave: int, rate: float, *, supported: bool = True):
    return {
        "year": year,
        "wave": wave,
        "sampled_trips": 30 if supported else 29,
        "disposition_trips": 10 if supported else 9,
        "weighted_catch": rate / 1000 * 100.0,
        "weighted_trips": 100.0,
        "catch_per_1000_trips": rate,
        "standard_error": 1.0,
        "ci_low": rate - 2.0,
        "ci_high": rate + 2.0,
    }


def test_baseline_is_blocked_when_precision_is_not_available():
    result = evaluate_baseline(
        [_audit(precision=False, cells=[_cell(2018, 3, 10.0)])]
    )

    assert result["status"] == "blocked"
    assert "precision" in result["failed_gates"]
    assert "metrics" not in result


def test_sparse_cells_are_blocked_instead_of_dropped():
    result = evaluate_baseline(
        [
            _audit(
                precision=True,
                cells=[_cell(2018, 3, 10.0), _cell(2019, 3, 12.0, supported=False)],
            )
        ]
    )

    assert result["status"] == "blocked"
    assert "cell_support" in result["failed_gates"]


def test_missing_outcome_is_blocked_as_missing_data():
    cell = _cell(2018, 3, 10.0)
    del cell["catch_per_1000_trips"]

    result = evaluate_baseline([_audit(precision=True, cells=[cell])])

    assert result["status"] == "blocked"
    assert "outcome" in result["failed_gates"]


def test_same_wave_reference_and_metrics_are_reproducible():
    result = evaluate_baseline(
        [
            _audit(
                precision=True,
                cells=[_cell(2018, 3, 10.0), _cell(2019, 3, 14.0)],
            )
        ]
    )

    assert result["status"] == "accepted"
    assert result["comparisons"][0]["baseline"] == approx(14.0)
    assert result["comparisons"][1]["baseline"] == approx(10.0)
    assert result["pooled_reference"] == approx(12.0)
    assert result["metrics"]["mae"] == approx(4.0)
