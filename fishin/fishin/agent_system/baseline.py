"""Fail-closed wave-level baseline evaluation for the MRIP pilot.

The baseline is a same-wave historical reference: for each cell, use the
pooled weighted rate from other accepted years in that wave. Results are published only
when the extraction contains the required support and survey-precision
evidence.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable, Mapping


REQUIRED_GATES = ("coverage", "grain", "cell_support", "precision")
REQUIRED_UNCERTAINTY_FIELDS = ("standard_error", "ci_low", "ci_high")


def _finite_number(value: object, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    return number


def _valid_outcome(cell: Mapping[str, object]) -> bool:
    try:
        weighted_catch = _finite_number(cell["weighted_catch"], "weighted_catch")
        weighted_trips = _finite_number(cell["weighted_trips"], "weighted_trips")
        rate = _finite_number(cell["catch_per_1000_trips"], "catch_per_1000_trips")
        return (
            weighted_catch >= 0
            and weighted_trips > 0
            and rate >= 0
            and math.isclose(rate, 1000 * weighted_catch / weighted_trips)
        )
    except (KeyError, TypeError, ValueError):
        return False


def _valid_uncertainty(cell: Mapping[str, object]) -> bool:
    try:
        standard_error = _finite_number(
            cell["standard_error"], "standard_error"
        )
        low = _finite_number(cell["ci_low"], "ci_low")
        high = _finite_number(cell["ci_high"], "ci_high")
        return standard_error >= 0 and high >= low
    except (KeyError, TypeError, ValueError):
        return False


def _cells(audits: Iterable[Mapping[str, object]]) -> list[Mapping[str, object]]:
    selected: list[Mapping[str, object]] = []
    seen: set[tuple[int, int]] = set()
    for audit in audits:
        acceptance = audit.get("acceptance")
        if not isinstance(acceptance, Mapping):
            raise ValueError("audit is missing acceptance gates")
        for cell in audit.get("cells", ()):
            if not isinstance(cell, Mapping):
                raise ValueError("audit contains a non-object cell")
            key = (int(cell["year"]), int(cell["wave"]))
            if key in seen:
                raise ValueError(f"duplicate baseline cell: {key}")
            seen.add(key)
            selected.append(cell)
    return selected


def evaluate_baseline(
    audits: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    """Evaluate the approved reference baseline without weakening gates.

    A blocked result contains the reference definition and failed gates but no
    rate or performance metric. This makes an incomplete extraction explicit
    instead of turning missing or imprecise cells into evidence.
    """

    audit_list = list(audits)
    gates = {
        gate: all(
            isinstance(audit.get("acceptance"), Mapping)
            and bool(audit["acceptance"].get(gate))
            for audit in audit_list
        )
        for gate in REQUIRED_GATES
    }
    cells = _cells(audit_list)
    try:
        support_ok = all(
            int(cell["sampled_trips"]) >= 30
            and int(cell["disposition_trips"]) >= 10
            for cell in cells
        )
    except (KeyError, TypeError, ValueError):
        support_ok = False
    gates["cell_support"] = gates["cell_support"] and bool(cells) and support_ok
    gates["outcome"] = bool(cells) and all(_valid_outcome(cell) for cell in cells)

    uncertainty_ok = bool(cells) and all(_valid_uncertainty(cell) for cell in cells)
    gates["uncertainty"] = uncertainty_ok

    reference = (
        "For each (year, wave) cell, use the pooled weighted rate from other "
        "accepted years in the same wave; if no other year exists, use the "
        "accepted same-wave weighted rate. The pooled reference is the "
        "weighted rate across all accepted cells. Geography, "
        "species, mode, area, and disposition remain fixed by the pilot spec."
    )
    failed = [name for name, passed in gates.items() if not passed]
    result: dict[str, object] = {
        "status": "blocked" if failed else "accepted",
        "reference": reference,
        "gates": gates,
        "failed_gates": failed,
        "cell_count": len(cells),
    }
    if failed:
        result["reason"] = (
            "Baseline metrics and uncertainty are withheld until every "
            "coverage, grain, support, survey-precision, and uncertainty "
            "gate passes."
        )
        return result

    by_wave: dict[int, list[Mapping[str, object]]] = defaultdict(list)
    for cell in cells:
        by_wave[int(cell["wave"])].append(cell)

    def weighted_rate(group: Iterable[Mapping[str, object]]) -> float:
        group_list = list(group)
        catch = sum(_finite_number(cell["weighted_catch"], "weighted_catch")
                    for cell in group_list)
        trips = sum(_finite_number(cell["weighted_trips"], "weighted_trips")
                    for cell in group_list)
        return 1000 * catch / trips

    result["pooled_reference"] = weighted_rate(cells)

    comparisons: list[dict[str, float | int]] = []
    for cell in cells:
        wave = int(cell["wave"])
        year = int(cell["year"])
        rate = _finite_number(cell["catch_per_1000_trips"], "catch_per_1000_trips")
        peers = [
            other
            for other in cells
            if int(other["wave"]) == wave and int(other["year"]) != year
        ]
        baseline = weighted_rate(peers or by_wave[wave])
        comparisons.append(
            {"year": year, "wave": wave, "observed": rate, "baseline": baseline}
        )

    errors = [item["observed"] - item["baseline"] for item in comparisons]
    result["comparisons"] = comparisons
    result["metrics"] = {
        "mae": sum(abs(error) for error in errors) / len(errors),
        "rmse": math.sqrt(sum(error * error for error in errors) / len(errors)),
        "mean_standard_error": sum(
            _finite_number(cell["standard_error"], "standard_error")
            for cell in cells
        )
        / len(cells),
    }
    return result
