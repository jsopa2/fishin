# V0 Environmental Data Joinability Review

## Scope

This review is limited to public, verifiable datasets and a conservative feasibility assessment for fishing-condition prediction. It does not build product functionality, prediction models, or V1 logic.

## Executive summary

- Public historical weather and environmental datasets are available for a realistic V0 feasibility test, especially in the U.S.
- The most promising data sources are NOAA/NWS observations and forecasts, NOAA Climate Data Online (CDO), Open-Meteo/ERA5-Land historical archive, USGS streamflow and hydrology, and NOAA buoy/tide stations.
- The primary risk is not weather availability; it is constructing a valid trip-level outcome label and matching that label to a place and time with enough precision to avoid noisy joins.
- A conservative V0 path is to evaluate a binary outcome such as "caught fish during a trip" or "target species present" using a limited geography and a strict temporal/spatial split.

## Public candidate datasets

| Dataset | Coverage | Temporal resolution | Spatial resolution | Access and license | Likely join keys | Main risks |
|---|---|---:|---:|---|---|---|
| NOAA NWS API (`api.weather.gov`) | U.S. forecast and observation coverage, strong public API support | Hourly to daily, depending on endpoint | Point observations + forecast grid | Public, free, no payment required; API documentation says the data is intended to be open data and free to use | `lat/lon`, nearest forecast gridpoint, nearby station ID, `date`, `hour` | Forecast and observation data are not identical to a fishing spot; local microclimate and waterbody effects can differ from nearby land weather |
| NOAA Climate Data Online (CDO) | U.S. and some global climate station coverage; strong historical weather records | Daily and monthly summaries | Station-based | Public federal dataset; access through NOAA portals and APIs | `station_id`, `state`, `county`, `date` | Missing stations, sparse coverage in remote areas, and coarse daily summaries may hide diurnal fish activity |
| Open-Meteo historical archive (ERA5/ERA5-Land-backed) | Global historical weather; includes many countries and regions | Hourly and daily | Roughly 9-11 km grid (ERA5/ERA5-Land) | Public API; no API key required for the historical archive as validated through direct API calls | `lat/lon` nearest grid cell, `date`, `hour` | Approximate environmental conditions for a lake, river reach, or fishing point; poor local fidelity for microhabitats |
| USGS NWIS streamflow and water data | U.S. surface water and groundwater stations | 15-minute to daily depending on station | Station-based point data | Public U.S. federal resource; no payment required through USGS services | `station_id`, `lat/lon`, `date`, `hour` | Coverage is uneven; many rivers and lakes have no nearby station; data may be missing during outages |
| NOAA/NDBC buoy observations | Coastal and offshore marine stations | Sub-hourly to hourly | Station-based marine observations | Public NOAA data; no payment required | `station_id`, `lat/lon`, `date`, `hour` | Primarily coastal/offshore; weak inland coverage; marine conditions do not map cleanly to inland freshwater fishing |
| NOAA tides and currents | Coastal and estuarine waters | Hourly or sub-hourly | Station-based | Public NOAA data; no payment required | `station_id`, `lat/lon`, `date`, `time` | Limited to tidal/coastal environments; not useful for most freshwater fishing except estuary systems |
| Waterbody metadata (NHD, lake polygons, river reaches) | U.S. waterbody datasets | Static geometry | Polygon / reach geometry | Public federal GIS data; usually open/public | `waterbody_id`, `state`, `county`, `nearest waterbody` | Static geometry does not encode current conditions; requires careful spatial join to fishing observations |
| FishBase / species metadata | Global species ecology and taxonomy support | Static reference data | Species-level | Public scientific reference / open access | `species`, `taxonomy`, `habitat` | Useful for species context, not for trip-level outcomes or fishing success labels |
| iNaturalist / state species occurrence data | Geo-tagged species observations, varying temporal depth | Event-based | Point observations | Public data with platform terms; often open/public | `species`, `lat/lon`, `date` | Not direct fishing effort or catch data; can be noisy and biased toward where people observed species |
| State creel / fisheries survey data | State-level fisheries outcomes; often species and date linked | Daily or seasonal subsets | Site or region based | Public but inconsistent by state and often partially restricted | `site_id`, `species`, `date`, `region` | Highly variable quality, gaps, and inconsistent release/harvest definitions; may be the best-but-uneven label source |

## Evidence from public sources

### 1) NOAA NWS API is openly available and free

The NOAA/NWS API documentation states that the service is intended to be open data and free to use for any purpose, with only reasonable rate limits to prevent abuse.

Verified source:
- https://www.weather.gov/documentation/services-web-api
- Accessed 2026-09-08

This is strong evidence that weather forecasts and nearby observations are a viable public-source input layer for U.S. work.

### 2) NOAA CDO provides historical station-driven weather data

The NOAA Climate Data Online portal is a public historical weather archive for climate summaries and daily observations.

Verified source:
- https://www.ncei.noaa.gov/cdo-web/
- Accessed 2026-09-08

This supports historical daily or monthly weather features and is a strong source for station-based validation or a fallback if gridded data is too coarse.

### 3) Open-Meteo’s archive API is accessible without credentials

Direct API checks succeeded without API keys or secrets. A historical weather request to the archive API returned hourly temperature and precipitation values, confirming direct public access.

Verified source:
- https://archive-api.open-meteo.com/v1/archive
- Accessed 2026-09-08

This makes Open-Meteo a strong candidate for global historical weather features when local station data is limited.

### 4) NOAA NDBC buoy data is publicly accessible at station endpoints

Direct access to NOAA buoy data returned real marine observations for a live station endpoint.

Verified source:
- https://www.ndbc.noaa.gov/
- https://www.ndbc.noaa.gov/data/realtime2/46026.txt
- Accessed 2026-09-08

This confirms that marine weather and coastal surf conditions are available for a public, direct data pipeline.

### 5) USGS streamflow data is available through public APIs

A direct request to the USGS NWIS streamflow API returned site metadata and discharge data for a live station.

Verified source:
- https://waterservices.usgs.gov/nwis/iv/?sites=09380000&parameterCd=00060&period=P7D&format=json
- Accessed 2026-09-08

This makes streamflow and hydrology a realistic environmental layer for freshwater fishing analyses.

## Spatial-temporal joinability assessment

### What we can join reliably

- Weather and hydrology data can be joined to a fishing observation by `date` and nearest `lat/lon` or nearest station.
- For a trip log with a start time and end time, a practical approach is to compute the weather/hydrology features over a fixed window before the trip (for example: average temperature in the previous 6 hours, precipitation in the previous 24 hours, streamflow at nearest station).
- For daily or seasonal summaries, the join by `date` and `region` or `waterbody_id` is usually more stable than an exact point match.

### What is hard to join without noise

- Exact angler location is often not available or is intentionally rounded.
- Many fishers record a lake name, county, or general region rather than precise coordinates.
- Weather grid cells are a proxy, not a measurement at the exact cast point.
- Local water bodies experience different conditions than nearby land weather stations.
- Hydrology coverage is sparse relative to the full set of fishing destinations.

### Recommended join strategy

1. Start with a narrow geography and a single species or species family.
2. Join on `date` and whichever of these is available, in order:
   - exact `lat/lon` to nearest weather grid cell or station;
   - `waterbody_id` or nearest waterbody polygon;
   - `county` or `state` + `date` as a fallback only when finer signals are unavailable.
3. Use a short rolling window rather than a single instant reading:
   - previous 2-6 hours for temperature, pressure, and wind;
   - previous 24 hours for precipitation and river conditions;
   - same-day or prior-day features for daily presence/absence models.
4. Treat any join with >10-20 km distance or no nearby hydrology station as a lower-confidence sample for V0 testing.

## Missingness and coverage risks

- Weather is dense in populated U.S. areas but sparse in remote, mountainous, or rural fishing destinations.
- Marine and coastal forecast coverage is excellent, but inland freshwater habitat is more variable and less monitored.
- Flow gauges and water-level stations are not available everywhere; many lakes or streams have no nearby station.
- Trip-level catch logs often lack negative examples (days with zero fish caught), which can create a biased label distribution.
- Public observation data tends to be opportunistic and not a true probability sample of all fishing effort.
- Some datasets are aggregated to daily or monthly windows, which is too coarse for within-trip prediction if the actual action occurs in a few hours.

## Conservative evaluation design

The most defensible V0 design is not a black-box, all-purpose prediction model. It is a narrow, audited benchmark built against a clearly defined outcome.

### Recommended outcome definition

Use a binary or ordinal trip-level fishing outcome with direct evidence, for example:
- `y = 1` if the trip recorded at least one target-species catch or a successful catch event;
- `y = 0` if the trip recorded no target catch during the same trip or same location/day;
- For a richer design, use species-specific success or catch rate per trip.

The label should be tied to a place and time. Avoid loosely defined "good fishing" labels derived from broad region averages or counts alone.

### Recommended baseline and evaluation

1. Limit the initial study to a single region (for example, one state or one freshwater basin) and one or two relevant species.
2. Build a simple baseline that uses only calendar and site effects:
   - month or week-of-year;
   - day-of-week;
   - site or waterbody fixed effects;
   - species and region controls.
3. Add weather and hydrology features incrementally to determine whether they add signal above this baseline.
4. Split by time and geography to avoid leakage:
   - hold-out by future season or year;
   - optionally leave one waterbody or region out for a robustness check.
5. Report the following metrics:
   - AUC-ROC for binary catch/no-catch;
   - PR-AUC because positive events are often rare;
   - Brier score or calibration curve for probability quality;
   - average lift over a simple baseline.

### Minimal success bar for V0

A success case would be a consistent, reproducible improvement over the season-and-site baseline in a limited geography. That is a much more credible V0 claim than a broad product-level forecast claim.

A weak or inconclusive result is still valuable if it shows:
- data coverage is sparse;
- the outcome label is noisy;
- the join is too approximate;
- or there is no material lift above a simple baseline.

That result is still useful company memory and prevents premature product development.

## Candidate V0 path

1. Pick one public region with multiple fishing trips or observation records and consistent metadata.
2. Use NOAA weather + USGS hydrology + site metadata for the region.
3. Build a clean training set with trip-start time, site coordinates, and a binary catch outcome.
4. Test the simplest measurable model first (logistic regression or gradient boosting over 10-30 interpretable features).
5. Keep evaluation conservative and region-specific.
6. Only expand if the signal is materially stronger than a simple baseline and the missingness is manageable.

## Conclusion

Public weather and environmental data are available in sufficient quantity to support a serious V0 validation test. The main challenge is not data availability; it is data quality, join precision, and outcome definition. A narrow, time-aware, site-aware, and baseline-tested evaluation design is the right next step.

## References and evidence

- NOAA Weather API documentation: https://www.weather.gov/documentation/services-web-api
- NOAA Climate Data Online: https://www.ncei.noaa.gov/cdo-web/
- Open-Meteo historical weather API: https://open-meteo.com/en/docs/historical-weather-api
- ERA5-Land dataset documentation: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=overview
- USGS water data / NWIS services: https://waterservices.usgs.gov/
- NOAA National Data Buoy Center: https://www.ndbc.noaa.gov/
- NOAA Tides & Currents: https://www.tidesandcurrents.noaa.gov/

These sources are public and directly verifiable. No credentials or paid services were required for the retrieved public evidence used in this review.
