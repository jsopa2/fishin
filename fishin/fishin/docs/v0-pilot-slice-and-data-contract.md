# V0 pilot slice and data contract

**Status:** provisional selection for the first bounded extraction  
**Selected on:** 2026-09-08  
**Scope:** MRIP wave-level feasibility audit only; no production pipeline or
prediction claim

## Selected slice

| Dimension | Selection | Reason |
| --- | --- | --- |
| Observation program | NOAA Marine Recreational Information Program (MRIP) general survey | Public-use catch/trip microdata, calibrated estimates, documented survey weights, and a public query tool |
| Species | Red drum (`Sciaenops ocellatus`); use the exact MRIP species label/code from the variable guide | A single named species keeps the target auditable and avoids pooling unlike taxa |
| Geography | North Carolina, state waters | NOAA lists North Carolina in the South Atlantic and defines state waters as inland salt/brackish waters plus the state territorial sea; the public data supports state-level estimates |
| Fishing mode | Shore | A single MRIP mode avoids mixing shore and private-boat effort and is explicitly covered by the Fishing Effort Survey |
| Waves | 3, 4, and 5 (May–October) | Three consecutive two-month waves cover the warm-season window without pretending MRIP supports daily exposure |
| Years | 2018–2025 | Eight complete years are available in the public MRIP series; 2025 is the latest final year documented by NOAA on the selection date |
| Initial outcome | Estimated red drum catch per 1,000 shore angler trips, using one explicitly chosen catch disposition | MRIP estimates are weighted population estimates; raw microdata row counts are not catch totals |

This is a **selection**, not a statement that the cell already has adequate
sample size or precision. The extraction must reject the slice, or narrow the
years/waves with an explicit decision record, if the checks below fail.

### Source evidence

NOAA's MRIP Query Tool documents filters for time series, geographic area,
species, mode, and other characteristics. NOAA's downloads page documents
general survey catch and trip microdata by year and two-month wave, the
`_id_code` trip key, design variables, and the catch/trip weights. NOAA's
glossary documents North Carolina's South Atlantic grouping, state waters,
shore effort, confidence intervals, and imputation.

- Query tool: <https://www.fisheries.noaa.gov/data-tools/recreational-fisheries-statistics-queries>
- Downloads and variable descriptions:
  <https://www.fisheries.noaa.gov/recreational-fishing-data/recreational-fishing-data-downloads>
- Glossary:
  <https://www.fisheries.noaa.gov/recreational-fishing-data/recreational-fishing-data-glossary>
- User handbook:
  <https://www.fisheries.noaa.gov/resource/document/mrip-data-user-handbook>
- Public estimate directory:
  <https://apps-st.fisheries.noaa.gov/st1/recreational/MRIP_Estimate_Data/>

All sources were checked on 2026-09-08. NOAA publication terms and the
current variable guide are authoritative when the extraction is implemented.

## Observation data contract

The extraction produces one row per `(year, wave, state, mode, species)` cell,
plus an audit table at the trip-record level. The required fields are:

| Field | Type/constraint | Meaning |
| --- | --- | --- |
| `year` | integer, 2018–2025 | Calendar year |
| `wave` | integer, 3–5 | MRIP two-month sampling wave |
| `species_code` / `species_label` | exact MRIP values | Red drum only; retain the source code and label |
| `state` | exact MRIP value | North Carolina only |
| `mode` | exact MRIP value | Shore only |
| `area` | exact MRIP value | State waters; do not silently substitute inland, ocean, or federal EEZ |
| `id_code` | non-null source trip identifier | Links catch records to a sampled angler trip |
| `catch_disposition` | source-coded categorical value | Preserves kept/released/discarded meaning |
| `catch_count` | non-negative numeric or source missing | Catch count in the selected disposition |
| `wp_catch` | positive numeric for weighted catch records | MRIP catch expansion weight |
| `wp_int` | positive numeric for trip/effort records | MRIP interview/trip expansion weight |
| `strat_id`, `psu_id` | non-null design identifiers where required | Survey design variables needed for auditing and prescribed estimation |

The published outcome is:

`1,000 × weighted red drum catch / weighted shore angler trips`

The numerator and denominator must use the same cell keys and compatible
survey definitions. The implementation must preserve the catch disposition
instead of combining kept and released catch by default. Variance and
confidence intervals must use NOAA's prescribed survey method/template; a
simple standard error from raw rows is not acceptable.

## Environmental join contract

The first environmental source is the public NOAA Integrated Surface Database
(ISD), joined only at the same `(year, wave, state)` cell. This is a
region/wave covariate join, not a claim about an individual angler's weather.

For each cell, retain:

| Field | Requirement |
| --- | --- |
| `environment_source` | `NOAA ISD` |
| `station_id` | Pre-specified North Carolina coastal station identifier(s) |
| `station_selection_rule` | Versioned rule and station metadata used to select the station(s) |
| `observation_start`, `observation_end` | Inclusive UTC bounds for the wave |
| `weather_coverage_fraction` | Observed expected intervals / expected intervals |
| environmental summaries | Only variables with documented units and coverage, such as temperature, precipitation, wind, and pressure |
| `join_confidence` | `high` only if the station rule and coverage threshold pass; otherwise `low`/`missing` |

The station must be selected before looking at catch outcomes. Do not use
exact trip locations: public MRIP documentation does not promise them.
Do not use a station farther than 20 km from the documented North Carolina
coastal study area without marking the cell low confidence. If no station
meets the rule, retain the MRIP cell with environmental fields missing rather
than substituting a different geography.

## Inclusion and exclusion rules

Include records only when all of the following hold:

1. The year, wave, state, mode, area, and species match the selected slice.
2. The source record is an eligible MRIP general-survey catch or trip record,
   not a published estimate accidentally treated as a trip observation.
3. The trip identifier is present and joins catch to the corresponding trip
   record without creating duplicate trip rows.
4. Catch counts and weights pass the source-domain checks (non-negative counts,
   positive applicable weights, and no impossible date/wave values).
5. The selected catch disposition is explicit and consistent across all cells.

Exclude and count separately:

- other species, states, areas, modes, and waves;
- records with missing keys or unusable survey weights;
- duplicate source rows that cannot be explained by the MRIP record grain;
- synthetic or imputed records when the source flag identifies them, unless a
  later analysis explicitly includes them and reports that choice;
- charter/headboat effort-only records, because the selected mode is shore;
- environmental observations outside the pre-specified station rule or time
  bounds.

No excluded record may silently become a zero catch. A missing catch value is
missing, not evidence of no catch.

## Missingness handling

The audit must report missing counts and rates by year, wave, field, and source
file before producing any outcome. Required keys, species, geography, mode,
and weights are **hard failures** when missing. Missing environmental
observations remain missing and produce a low-confidence or unavailable join;
they are not mean-imputed in V0. For optional environmental summaries, retain
the field-level missingness indicator and only calculate a summary when the
documented coverage threshold is met.

MRIP's published imputation flags must be retained as provenance. The first
result should report estimates with and without source-identified imputed
records if both are possible; neither result should be presented as an
individual-trip probability.

## Extraction acceptance checks

The bounded extraction is accepted only if it records pass/fail results for:

1. **Coverage:** all requested 2018–2025 wave files and the selected MRIP
   species/state/mode/area labels are present, or each unavailable cell is
   explicitly listed.
2. **Grain:** catch-to-trip joins are one-to-one at `id_code` after the
   documented record-grain rules; duplicate and orphan counts are zero or
   explained.
3. **Cell support:** every retained cell has at least 30 distinct sampled
   trips and at least 10 trips with the selected catch disposition. This is a
   screening floor, not a precision claim.
4. **Precision:** the weighted estimate has a finite, non-negative estimate,
   a finite standard error, and a finite 95% interval; report relative
   standard error and flag cells above 30% for review rather than deleting
   them silently.
5. **Weight integrity:** all weighted terms use the MRIP-design fields and
   agree with the applicable NOAA template/query definition.
6. **Joinability:** each environmental cell records its station IDs, distance,
   interval coverage, and missingness; no fallback station or geography is
   chosen after inspecting the outcome.
7. **Reproducibility:** source URLs, file names/versions, retrieval date,
   query parameters, variable-guide version, and the exact inclusion rules
   are saved with the audit.

Failure means the slice is not yet suitable for a baseline. The next action
would be a documented slice revision, not a model, UI, or performance claim.

## Known limitations and open questions

- The selected cell's actual sample support and precision are unknown until
  public files are extracted.
- MRIP waves are two months; environmental summaries cannot support a credible
  daily or within-trip causal interpretation.
- A North Carolina state-waters cell combines locations with different local
  conditions, and an ISD station is only a proxy.
- The 2026 FES revision creates a comparability boundary after the selected
  2018–2025 window. The extraction must use one documented calibration series
  and must not mix 2026 estimates into this pilot.
- If the species label/code, station coverage, or cell support fails, the
  failure must be reported before selecting a replacement slice.

This document intentionally does not define a production schema, implement
downloads, fit a prediction model, or claim predictive performance.
