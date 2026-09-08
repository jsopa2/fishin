# V0 Wisconsin extraction handoff

The former North Carolina MRIP extraction is no longer an active V0 path.
Issue #16 resets the pilot to the Wisconsin DNR Winnebago System lake
sturgeon ice-spearing slice defined in
`v0-pilot-slice-and-data-contract.md`.

The old MRIP extractor and research remain historical evidence only. They must
not be reused as a Wisconsin parser or treated as evidence for Wisconsin
coverage. A Wisconsin extractor must acquire the DNR-linked 2016–2025 final
harvest reports, preserve source hashes and locations, and fail closed when a
report is unavailable or changes shape.

The first implementation should produce an acquisition audit, not a model:

1. enumerate the DNR report URLs and publication dates;
2. extract season, waterbody, daily/season harvest, and any published effort
   denominator without inventing absent fields;
3. report coverage, duplicate rows, source changes, missingness, and
   Lake-Winnebago/Upriver-Lakes separation;
4. defer environmental joins until the harvest audit passes;
5. publish no baseline, forecast, or performance number unless the contract's
   support and uncertainty gates pass.

The DNR page is the authoritative starting point:
<https://dnr.wisconsin.gov/topic/fishing/sturgeon/WinnSysSturgeonSpear>
