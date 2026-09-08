# V0 MRIP pilot extraction

This is the bounded Issue #8 acquisition and audit artifact for the approved
slice: NOAA MRIP general survey, red drum (`Sciaenops ocellatus`), North
Carolina state waters, shore mode, waves 3–5, years 2018–2025.

## Reproduce

1. Download the NOAA public CSV archives from the directory below. The 2018
   and 2019 files are in `ps_2015_2019_csv.zip`; each later year has its own
   archive. Do not rename or edit the archives.
2. Run the extractor from the repository root:

   ```powershell
   python -c "from agent_system.mrip import extract_archive,write_audit; write_audit(extract_archive('ps_2020_csv.zip'), 'mrip-2020-audit.json')"
   ```

   A full 2018–2025 audit requires invoking it for each archive and retaining
   each JSON audit. The extractor records the archive SHA-256, URL, selected
   labels/codes, coverage, missing cells, grain checks, and weighted point
   rates.

Source directory:
<https://apps-st.fisheries.noaa.gov/st1/recreational/MRIP_Survey_Data/CSV/>

NOAA's downloads page and variable guide are authoritative for file meaning,
survey design fields, publication revisions, and terms:
<https://www.fisheries.noaa.gov/recreational-fishing-data/recreational-fishing-data-downloads>

## Contract safeguards

- Filters are exact source values: `ST=37`, `MODE_FX=3`, `AREA_X=5`,
  `SP_CODE=8835440901`, `COMMON=RED DRUM`, and waves 3–5.
- `HARVEST` is the explicit selected catch disposition. Missing keys,
  non-positive weights, and catch/trip duplicates or orphans fail loudly.
- The audit keeps the trip/catch grain distinct and computes only the
  weighted point rate `1,000 * weighted HARVEST / weighted WP_INT`.
- Missing requested year/wave files are listed rather than treated as zero.
- A cell with no selected catch rows retains missing weighted catch/rate values;
  it is not converted to a zero catch outcome.
- The extractor does not impute missing values, substitute geography, or claim
  a daily or individual-trip result.

## Current limitations

The source archives were accessible publicly on 2026-09-08, but no NOAA data
files are committed to this repository. The extractor does not implement
NOAA's complex-survey variance templates, so `precision` is deliberately
reported as failed and `precision_status` is `not_computed`. The weighted
point rates are therefore an acquisition/audit diagnostic, not an accepted
baseline or predictive result. Environmental ISD joins are not included in
this artifact; they remain a separate, pre-specified follow-up after the MRIP
cell audit passes.

## Issue #9 baseline gate

The reference baseline is a same-wave historical rate: for each `(year,
wave)` cell, compare its rate with the pooled weighted rate from other accepted
years in the same wave. The report also includes one pooled weighted reference
across all accepted cells. Species, state waters, shore mode, and the selected
catch disposition remain fixed by the pilot contract. The evaluator is
`agent_system.baseline.evaluate_baseline`.

It fails closed. It publishes no baseline metric when any requested coverage,
catch/trip grain, support, survey precision, or uncertainty gate fails.
Uncertainty requires finite per-cell standard errors and confidence limits from
the applicable NOAA complex-survey procedure; raw-row standard errors are not
accepted. With the current Issue #8 artifact, `precision=false` and these
fields are absent, so Issue #9 cannot make a defensible baseline claim. The
correct result is **baseline not estimable from the acquired evidence**, not a
zero rate, an imputed value, or a weakened threshold.
