# Wisconsin extraction audit

This bounded artifact discovers the Wisconsin DNR's linked 2016–2025 final
reports, records retrieval metadata and SHA-256 hashes, and extracts only
explicit season totals for `Lake Winnebago` and `Upriver Lakes`. It does not
infer daily harvest, licenses, caps, zeros, or uncertainty.

Use `agent_system.wisconsin.discover_report_urls`, `acquire_sources`,
`extract_season_rows`, and `audit` as the reproducible sequence. The DNR
landing page is the authoritative link index:

<https://dnr.wisconsin.gov/topic/fishing/sturgeon/WinnSysSturgeonSpear>

The current public page exposes links for all candidate years, but several
archived links resolve through Widen's HTML viewer rather than directly to a
PDF. The extractor records those responses as `blocked` instead of parsing
viewer markup. Report publication dates are not assumed when they are absent
from the downloaded artifact. Daily rows, same-waterbody license denominators,
harvest caps, and source-provided uncertainty are not yet proven across the
candidate window, so the audit remains fail-closed and publishes no rate or
baseline.

No environmental join is attempted until this harvest audit passes.
