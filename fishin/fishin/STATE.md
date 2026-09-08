# Current State

## Current Objective

Validate whether fishing conditions can be predicted using public data.

## Phase

V0 — Prediction Feasibility

## Repository Status

✅ Refactored from OpenHands-centric to GitHub/Copilot-centric operating model

**Completed:**
- Created comprehensive operating manual (COPILOT.md)
- Created lightweight role definitions (agent-roles/)
- Removed OpenHands SDK dependencies and infrastructure
- Cleaned up agent_system/ (kept only context utility)
- Updated README.md, pyproject.toml, DECISIONS.md
- Updated .env.example (removed deprecated credentials)
- All remaining tests pass

**Repository is clean and ready for manager-directed V0 execution through authorized Issues.**

## Active Work

Issue #4 research complete: public fishing-observation data availability, measurable
outcome definition, and environmental/weather joinability review.

## Blocked

None.

## Decisions Needed

None currently. This work remains within V0 research scope and does not require a product or budget gate.

## Recent Findings

- NOAA MRIP is the strongest documented public candidate: it provides catch and
  effort estimates plus public-use microdata for Atlantic and Gulf recreational
  fishing, organized at two-month wave resolution.
- A defensible first outcome is estimated catch per 1,000 angler trips for one
  species, area, mode, and wave. It requires survey weights and cell-level
  precision checks; it is not an individual catch probability.
- Environmental joins are plausible at region/wave level, but exact fishing
  locations and daily weather exposure are not established by the public MRIP
  documentation.
- Detailed evidence and source constraints are recorded in
  `docs/fishing-observation-data-availability.md`.
- Public weather and hydrology datasets are available without paid services, including NOAA/NWS, NOAA CDO, Open-Meteo historical archive, USGS NWIS, and NOAA buoy observations.
- The main feasibility risk is not missing weather data; it is building a valid trip-level outcome label and joining that label to the correct time and place without introducing noise.
- Marine/coastal datasets are relatively mature, while inland freshwater data quality depends heavily on nearby station coverage, waterbody IDs, and record completeness.
- A conservative V0 evaluation should use a narrow region, a binary catch-based outcome, and a before/after baseline comparison rather than broad product claims.

## Next Recommended Action

1. Select one MRIP species, area, and mode with adequate public sample coverage.
2. Run a bounded, reproducible MRIP extraction and cell-count/precision audit, joined only to one explicitly documented environmental source.
3. Establish the wave-level catch-rate baseline before considering predictors.
4. Keep all later work within the same research-first, evidence-based approach until a meaningful baseline is proven.

## Human Attention Required

No CEO approval gate was triggered by this research-only work. Paid services,
credentials, sensitive data, and externally significant performance claims remain
out of scope.

---

*Note: This file is maintained collaboratively by CEO and Copilot. Each completed work item or decision updates this file. Copilot updates STATE.md in the final PR of each work item.*
