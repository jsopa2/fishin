# V0 Wisconsin pilot slice and data contract

**Status:** selected for bounded feasibility acquisition
**Selected on:** 2026-09-08  
**Scope:** Wisconsin-first freshwater feasibility audit; no production
pipeline, forecast, or performance claim

## Selected slice

| Dimension | Selection | Evidence and rationale |
| --- | --- | --- |
| Region / waterbody | Lake Winnebago System: Lake Winnebago plus the Upriver Lakes (Butte des Morts, Winneconne, and Poygan) | Wisconsin DNR identifies this as a single managed sturgeon system and publishes separate harvest reporting for Lake Winnebago and Upriver Lakes. |
| Species | Lake sturgeon (`Acipenser fulvescens`) | The DNR documents the system as one of North America's largest lake sturgeon populations and the fishery's conservation caps. |
| Fishing mode | Licensed ice spearing from a shelter | The DNR states that spearing occurs through the ice, requires a license, and may only be done from a shelter placed on ice. |
| Time window | Each annual Winnebago System spearing season, February; analyze 2016–2025 only if the archived reports expose comparable fields | The DNR publishes final harvest reports for 2016–2025 and current season dates. Do not mix future revisions or a changed reporting definition without a comparability record. |
| Outcome | Daily and season harvest count, plus harvest-to-license ratio only when the denominator is published for the same waterbody and season | This is an auditable aggregate outcome; it is not individual success probability or a forecast. |
| Primary source | Wisconsin DNR Winnebago System sturgeon spearing final harvest reports and season updates | Official public source, directly accessible without credentials or payment. |
| Environmental candidates | USGS Wisconsin water observations and NOAA/NWS public weather observations, joined at waterbody/day only after source coverage is measured | Reuses the prior environmental joinability findings, but freshwater station coverage must be proven for this slice. |

This slice is a **feasibility selection**, not evidence that the required
historical rows, denominators, or environmental joins already pass. The first
extraction must fail closed and report any unavailable season, waterbody,
denominator, or field.

## Source evidence

- Wisconsin DNR, [Winnebago System Sturgeon
  Spearing](https://dnr.wisconsin.gov/topic/fishing/sturgeon/WinnSysSturgeonSpear):
  describes the fishery, ice-only mode, Lake Winnebago/Upriver Lakes split,
  license rules, harvest caps, current harvest tables, and links to final
  harvest reports for 2016–2025.
- Wisconsin DNR, [fishing season
  dates](https://dnr.wisconsin.gov/topic/Fishing/seasons): identifies the
  Winnebago System spearing season as a February season.
- Wisconsin DNR, [lake
  sturgeon](https://dnr.wisconsin.gov/topic/Fishing/sturgeon/LakeSturgeon.html):
  documents the species and identifies the Winnebago System as a common
  Wisconsin range.
- [USGS Water Data for
  Wisconsin](https://waterdata.usgs.gov/wi/nwis/uv) and the prior
  `v0-environmental-data-joinability.md` review support public hydrology
  candidates, subject to station-distance and coverage checks.

Sources were checked on 2026-09-08. The DNR page and any linked report remain
authoritative for field meaning, publication revisions, and terms.

## Public-data contract

The extraction must preserve one row per `(season_year, waterbody, day)` when
the source provides daily data, and a separate season-level table. It must
retain the original report URL, downloaded filename, retrieval date, SHA-256,
source publication date, and page/table location.

Required fields, when present in the source:

| Field | Constraint |
| --- | --- |
| `season_year` | Integer; 2016–2025 candidate window |
| `waterbody` | Exactly `Lake Winnebago` or `Upriver Lakes`; never merge them silently |
| `date` / `day_of_season` | Source-defined day; retain local date and source label |
| `harvest_count` | Non-negative source value; missing is missing |
| `license_count` / `effort_denominator` | Source-defined denominator; never infer from a different waterbody |
| `harvest_cap` | Source-defined cap, retained as context rather than a target |
| `species` | Exact source label: lake sturgeon |
| `mode` | Exact source label: ice spearing |
| `source_locator` | URL plus page/table or row locator |

The primary reported statistic is the source-compatible harvest count. A
harvest rate is permitted only when numerator and denominator share the same
season, waterbody, and reporting definition.

## Join, support, and uncertainty rules

- Join environmental observations only on `waterbody` and local calendar day,
  using a versioned station-selection rule chosen before looking at harvest.
- Record station ID, coordinates, distance, observed interval, expected
  interval, coverage fraction, units, and source revision.
- A join is `high` confidence only when the pre-specified distance and
  coverage thresholds pass; otherwise retain the harvest row with
  `low`/`missing` join confidence.
- Do not claim that a land station or river gauge measures conditions inside a
  particular ice shanty.
- Do not calculate a baseline or model metric until every required season and
  field is accounted for, source definitions are comparable, and uncertainty
  is available from the source or a documented design-based procedure.
- No minimum support threshold is evidence of prediction quality. Support
  thresholds may screen candidate cells, but cannot convert sparse data into
  a claim.

## Inclusion and exclusion

Include only official DNR report rows whose season, waterbody, species, mode,
and field definitions match this contract. Exclude or count separately:

- future seasons, amended reports, or mixed definitions without an explicit
  comparability decision;
- rows that combine Lake Winnebago and Upriver Lakes when the source permits
  separation;
- inferred zeros, reconstructed denominators, or values copied from a
  different report;
- weather or hydrology observations outside the pre-specified station and
  date rule;
- individual license-holder or location data not publicly documented as
  available.

## Missingness, licensing, and reproducibility

Report missing counts and rates by season, waterbody, field, and source file
before producing any statistic. Missing harvest or denominator values remain
missing; they are never imputed or treated as zero. Missing environmental data
produces an unavailable join, not a substitute station selected after seeing
the outcome.

The DNR, USGS, NOAA/NWS, and linked report terms must be recorded with the
retrieval metadata. No paid service, API key, credential, or restricted
dataset is part of V0. A clean rerun must be possible from the public URLs,
fixed source hashes, exact parser version, and documented inclusion rules.

## Decision gate

The Wisconsin slice is ready for a baseline only if extraction proves
comparable multi-year coverage, waterbody separation, denominator semantics,
source support, and uncertainty. If any gate fails, document the failure and
stop; do not pivot back to North Carolina, broaden to the Midwest, build UI or
database infrastructure, or make a prediction/performance claim.
