# Current State

## Current Objective

Validate whether a Wisconsin-first fishing benchmark can be supported by
public data.

## Phase

V0 — Wisconsin Prediction Feasibility

## Repository Status

The operating model and prior research artifacts are retained. Issue #16
resets the active pilot from the former North Carolina MRIP slice to the
Wisconsin DNR Winnebago System lake sturgeon ice-spearing slice.

## Active Work

The selected contract is documented in
`docs/v0-pilot-slice-and-data-contract.md`. The former MRIP extractor and
baseline evaluator are historical research only and must not be presented as
Wisconsin evidence.

## Blocked

No Wisconsin extraction has been completed. Comparable 2016–2025 report
coverage, waterbody separation, denominator semantics, environmental
joinability, and uncertainty remain unproven.

## Recent Findings

- Wisconsin DNR documents the Winnebago System as a major lake sturgeon
  population and publishes separate Lake Winnebago/Upriver Lakes harvest
  reporting, including final reports for 2016–2025.
- The selected mode is licensed ice spearing from a shelter; the selected
  window is the February annual spearing season.
- The first outcome is source-defined daily/season harvest, with a rate only
  when a same-waterbody denominator is published.
- USGS Wisconsin water observations and NOAA/NWS public weather are candidate
  environmental sources, but station coverage and distance must be measured
  for this freshwater slice.
- Missing harvest, denominator, and environmental values remain missing. No
  inferred zeros, fallback geography, or unsupported prediction claims are
  permitted.
- Other Midwest regions are expansion targets only after Wisconsin passes its
  evidence gates.

## Next Recommended Action

1. Acquire and audit the DNR-linked 2016–2025 final harvest reports.
2. Establish comparable fields, waterbody separation, denominators, and
   missingness before any baseline.
3. Evaluate Wisconsin hydrology/weather joinability only after the harvest
   audit passes.
4. Keep product work, broad Midwest rollout, UI, database, and agent runtime
   out of scope.

## Human Attention Required

No additional CEO-level decision is required for this Issue-authorized
research work. Any broader geography, paid service, credential, production
system, or externally significant performance claim requires escalation.

---

*This file is maintained collaboratively by CEO and Copilot. Each completed
work item or decision updates it.*
