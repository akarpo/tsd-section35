# tsd-section35

**Live:** <https://tsd-section35.karpowitsch.org>

An independent, source-linked look at Troy School District and Michigan's Section 35 literacy
grants (State School Aid Act). It confirms that Troy received none of Section 35j, the one-time
$140 million literacy grant of 2023–24 (22 of Oakland County's 28 local districts did), lists every
Section 35 dollar Troy has received since 2016–17, explains the new $1 million Section 35d
Orton-Gillingham grant, and asks the district questions.

## Layout

| Path | What it is |
|---|---|
| `public/` | The site. The **only** folder Cloudflare Pages deploys (build output dir = `public`, no build command). |
| `public/index.html` | The single page: inline CSS and JS, no external libraries. The chart data block between `/*DATA:BEGIN*/` and `/*DATA:END*/` is generated. |
| `public/assets/oakland-section35j.csv` | 35j by Oakland County local district. Generated; don't edit. |
| `public/assets/share-section35.png` | Social share image, 1200×630, rendered from `tools/share-card.html`. |
| `public/404.html`, `public/_headers`, `public/robots.txt` | Not-found page, security headers (CSP allows Cloudflare Web Analytics), robots. |
| `sources/state-aid/` | Pages extracted from MDE's State Aid Financial Status Reports: Troy FY2017–FY2026, Oakland districts FY2024–FY2026, the Nov. 20, 2026 Oakland ISD report. |
| `sources/parsed/` | Every Section 35 line from each statewide report, FY2017–FY2026 (and the Nov. 2026 ISD 63 report), as CSV. |
| `sources/statute/`, `sources/law/` | Sec. 35j (2023 PA 103), Sec. 35d (2026 PA 25), MCL texts, 2024 PA 146. |
| `sources/mde/` | MDE's 35j memo, its report to the Legislature, 35m grantee lists, the 35d page, the Nov. 17, 2026 literacy bulletin, an archived 35j page. |
| `sources/nces/` | NCES fall 2022 enrollment by grade (Troy, and all Michigan districts for the method check). |
| `sources/troy/`, `sources/hfa/` | Troy board documents; House Fiscal Agency FY2025-26 summary. |
| `tools/build_data.py` | Builds the CSV and the page's data block from `sources/`. It re-checks every Oakland district's 35j line against the PDF pages and checks the per-pupil method against NCES; it fails if either check fails. Run `python -I tools/build_data.py` (needs PyMuPDF). |
| `tools/share-card.html` | Source of the share image (open in Chrome at 1200×630 and screenshot). |
| `docs/FIGURES.md` | Every figure on the page, with its source document and page. |
| `docs/FINDINGS.md` | The research notes behind the page, including what was searched and not found. |

## Rules for changes

- Every number on the page appears in `docs/FIGURES.md` with a source. Add the row first.
- Chart and CSV data come from `tools/build_data.py`; never type them by hand.
- The status-report PDFs scramble their amount columns when converted to text. Render the page
  (PyMuPDF `get_pixmap`) and read it before quoting an amount; the same goes for MDE's 35m lists.
- Estimates are ours and stay labeled ("our estimate", "about").
- "Troy didn't apply" is an inference from MDE's wording, not a documented fact. Keep it labeled
  that way unless the district or a FOIA response says otherwise.
- After any edit, render at 1280 px and 390 px, light and dark, and check for overflow and heading
  order.

## When the numbers will change

| Expected | What to update |
|---|---|
| Each monthly state-aid payment (20th of the month) | Whether Troy's 2025–26 35m award ($1,173,876) has been paid: Oakland ISD report at `https://mdoe.state.mi.us/samspublic/Home/StatusReport` (ISD 63). |
| Spring 2027 | Section 35d application opens in NexSys (first-come, first-served). |
| Dec. 2026 | 2026–27 Section 35m formula grant applications (MDE). |
| Aug. 1, 2027; start of 2027–28 | PA 146 screening deadlines. |
| Any district answer to the questions | Replace the "likely" verdict with what the district says, with a link. |

## Hosting

Cloudflare Pages project `tsd-section35`, Git-connected to `akarpo/tsd-section35` (`main`), custom
domain `tsd-section35.karpowitsch.org` (proxied CNAME to the project's `pages.dev` host). A push to
`main` deploys. Never run `wrangler pages deploy`.
