# V0 fishing-observation data availability

**Research question:** Can a reproducible V0 study obtain public fishing observations with
species, time, place, catch, and effort fields, then join them to public environmental
data without credentials or paid services?

**Scope and date:** Fishing-observation sources are the primary scope. Environmental
sources are listed only to assess likely joins. URLs and access constraints were checked
on 2026-09-08. No data was downloaded or modeled in this work.

## Findings

NOAA's Marine Recreational Information Program (MRIP) is the strongest documented
candidate for a first study. It publishes public-use survey microdata and calibrated
catch and effort estimates in CSV and SAS formats. The data is marine recreational
fishing on the Atlantic and Gulf coasts, not a universal log of all fishing trips.
The public files are organized by year and two-month sampling wave, so a defensible
first outcome must be wave-level rather than daily.

MRIP is suitable for a feasibility study, subject to survey-weight handling and a
careful choice of one species, area, mode, and time period. It does not by itself
establish that environmental conditions predict fishing success.

## Candidate fishing-observation sources

| Source | Coverage and granularity | Useful fields / join key | Access and licensing constraints | Limitations |
| --- | --- | --- | --- | --- |
| [NOAA MRIP public-use data downloads](https://www.fisheries.noaa.gov/recreational-fishing-data/recreational-fishing-data-downloads) | Atlantic and Gulf coasts; calibrated estimates begin in 1981. Microdata is organized by year and two-month wave. APAIS catch files contain one record per species per intercepted angler trip; trip files contain one record per intercepted trip; size files contain one record per measured fish. | Species, catch disposition/count, survey wave, fishing mode, area, design stratum, site-day PSU, trip identifier, and survey weights. The natural initial join is `(year, wave, state/subregion or area)`; exact coordinates are not promised by the public-use description. | Public downloads; CSV and SAS formats. NOAA provides a [data user handbook](https://www.fisheries.noaa.gov/resource/document/mrip-data-user-handbook) and R/SAS survey templates. No credential or paid service is required for the files. Treat NOAA publication terms and the dataset documentation as authoritative before redistribution. | Survey sample, not a census or continuous trip log. Catch and effort are estimated with complex survey weights; raw row counts are not catch totals. Coverage is coastal marine and regional, with no general freshwater coverage. Estimates and microdata have different uncertainty and use cases. |
| [NOAA MRIP Query Tool](https://www.fisheries.noaa.gov/data-tools/recreational-fisheries-statistics-queries) | Published recreational catch and effort statistics for MRIP regions, years, waves, species, modes, and areas. | A reproducible query can define species, year/wave, area, mode, catch type, and effort measure. Join to environmental data at the same region and wave. | Public web tool; results and definitions must be recorded with the query parameters. It is an interface to estimates, not raw observations. | Query output is aggregated. It cannot recover trip-level weather exposure or exact fishing location. |
| [NOAA Large Pelagics Survey downloads](https://apps-st.fisheries.noaa.gov/st1/recreational/LPS_Data/) | Atlantic large pelagic fisheries; monthly catch and effort products. The downloads page documents monthly files from 2011 onward and annual products, with earlier annual files. | Species, month, mode, catch disposition, intercepted trip/boat records, and monthly estimates. Natural join is `(year, month, region/species)`. | Public CSV/SAS downloads and variable guides; no credentials or paid service. | Narrow species and geographic scope; seasonal survey design and monthly (not daily) resolution. Not a general replacement for MRIP. |
| [State creel and angler surveys](https://www.fws.gov/program/national-survey-fishing-hunting-and-wildlife-associated-recreation) | Potentially detailed freshwater observations, but availability, schemas, licensing, and continuity vary by state and survey. The linked USFWS survey is a national participation survey, not a lake-level catch log. | Where available: water body, date, species, effort, and catch; likely joinable to station or water-body environmental data. | Must be assessed state by state; no single public, stable, cross-state schema was verified for this memo. | Fragmented coverage and methods make a cross-region V0 harder. Do not treat the national participation survey as a fishing-success outcome. |

### Source selection

Use MRIP for the initial feasibility sample. It has the clearest public documentation,
stable survey concepts, catch and effort in the same program, and explicit public-use
downloads. Use the Large Pelagics Survey only if a large-pelagic species is selected.
Do not combine state creel surveys into a pooled outcome until a specific state dataset
and its license, sampling frame, and schema have been verified.

MRIP's query documentation notes that the improved Fishing Effort Survey (FES) design
changes estimates released for 2026 and that revised/back-calibrated series are needed
for some comparisons. A study spanning that boundary must record which calibration
series it uses rather than assuming all published estimates are directly comparable.

## Environmental sources for joinability

These are candidate covariate sources, not evidence that a prediction target is useful.

| Source | Coverage and granularity | Likely join | Constraints and limitations |
| --- | --- | --- | --- |
| [NOAA Integrated Surface Database (ISD)](https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database) | More than 35,000 stations globally; observations as far back as 1901, with station-specific gaps; hourly surface observations where reported. | Assign a documented station or spatial buffer to the MRIP estimation region and aggregate observations to each two-month wave (or use daily summaries only as exploratory features). | Station observations are point measurements and may be inland or distant from an angler site. Coverage is uneven. The archive is large; a reproducible study must pin station IDs, variables, and retrieval dates. |
| [NOAA National Data Buoy Center](https://www.ndbc.noaa.gov/) | Coastal and offshore buoy/station observations, commonly at hourly or sub-hourly cadence depending on station and variable. | Map a selected MRIP coastal region to a pre-specified nearby buoy and aggregate to the MRIP wave. | Sparse and nonuniform station coverage; buoy conditions may not represent estuaries, shore sites, or inland waters. Station histories and missingness must be recorded. |
| [USGS Water Data for the Nation](https://waterdata.usgs.gov/) | US monitoring locations with continuous, daily, field, and discrete water data categories. | For a freshwater study, join a specified water body or basin to a monitoring location and aggregate to the observation period. | This is an environmental source, not a catch/effort source. A corresponding public freshwater fishing-observation dataset is still unverified. |
| [Copernicus ERA5 single levels](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels) | Global reanalysis from 1940 onward; hourly estimates on a 0.25-degree regular grid. | Select grid cells covering the MRIP region and aggregate hourly variables to each MRIP wave. | Reanalysis is modeled/assimilated, not a direct local observation. Copernicus account/API access may be required for bulk download, so access workflow and current license must be verified before committing to it. |

For a no-credential first pass, NOAA's public files and openly downloadable station
archives are lower-risk than designing around a service that requires an account or
token. Any actual extraction must preserve the source version, URL, retrieval date,
station/grid identifiers, and license terms.

## One measurable outcome

**Proposed outcome:** estimated total fish caught per 1,000 angler trips for one
MRIP species, fishing mode, area, and two-month wave, with the catch definition
explicitly chosen (for example, kept catch or total catch).

This is measurable because MRIP publishes catch and effort estimates and documents
the survey weights and variables needed to reproduce estimates. The unit is
interpretable as a wave-level catch rate, not an individual angler's probability of
catching a fish. The first analysis should compare this outcome with a simple
historical/seasonal baseline before considering environmental predictors.

**Important limitations:**

* The outcome is an estimate from a complex survey. It requires MRIP's prescribed
  weights and variance procedures; counting public-use rows is invalid.
* Two-month waves prevent a credible daily weather-to-trip causal interpretation.
* The result is conditional on MRIP's marine geography, species, modes, sampling
  design, and catch definitions.
* Release, discard, and kept-catch definitions must not be silently combined.
* A sparse species/area/mode cell may be unsuitable even if the overall MRIP program
  has long coverage. Cell-level sample sizes and estimate precision must be checked.

## Uncertainty and recommended next Issue

**Certain:** MRIP provides documented public-use catch and trip files, catch/effort
estimates, survey waves, and survey-weight guidance.

**Probable:** A wave-level MRIP outcome can be joined to weather/environmental
aggregates by a pre-specified area and time key.

**Unknown until sampled:** Which species/area/mode cell has enough observations and
acceptable precision; whether station or reanalysis conditions represent fishing
locations; and whether a baseline beats a naive seasonal expectation.

**Recommended next Issue:** select one Atlantic or Gulf species and one MRIP area/mode,
download a bounded set of MRIP CSV files plus one explicitly documented environmental
source, and produce a data dictionary, cell-count/precision audit, and reproducible
wave-level catch-rate baseline. Keep the result as a feasibility experiment; do not
build a product or claim predictive value until held-out evaluation supports it.
