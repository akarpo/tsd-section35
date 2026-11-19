# Handoff: start here

Last updated **2026-11-19** (twice). The site is live and finished; nothing was left half-done.

## 2026-11-19: the `/history` page

Added `public/history.html` (<https://tsd-section35.karpowitsch.org/history>): every grant in
Section 35 since it began in 2015–16, 27 grants in 12 budgets ($1.157 billion budgeted
FY2016–FY2027), each with what it paid for, who could get it, budget by year, payments by year
from the status reports (with recipients, Troy, Oakland Schools), and sources. Built by
`python -I tools/build_history.py` from `sources/history/programs.json`; see `docs/FIGURES.md`
("The history page") and `docs/FINDINGS.md` §8. Also fixed on the main page: **Troy's 2015–16
35a(6) payment of $146,190 was missing** from "Every Section 35 dollar Troy received" (the first
pass started at FY2017). The 404 page had a garbled sentence; rewritten.

**Each year:** add the new budget act's Section 35 amounts to `programs.json` (quote + doc),
add the new final status report's parsed CSV to `sources/parsed/` (`tools/parse_status_report.py`),
map any new report codes in the grants' `pay` lists (the build names every unmapped line), and
rebuild. `legislature.mi.gov` refuses connections after rapid requests; fetch one file at a time,
or use the Wayback Machine (`https://web.archive.org/web/2026id_/<url>`).

## 2026-11-19 (later): what each of Troy's grants paid for

The main page's `#troy` section now has one article per grant Troy received money from
(`#grant-35a5` extra reading time, `#grant-35a9` summer reading, `#grant-35m` literacy materials):
what the law paid for, how a district qualified and how much, and **what Troy's board records show**,
with links to each board document and to the moment in each meeting video. Findings:
- **35m** is fully documented, from the June 2025 PA 146 overview to the May 19, 2026 purchase. The
  district amended its 35m application from UFLI to Collaborative Literacy: Being a Reader (Apr. 28,
  2026 workshop). That answers most of the old "did Troy change its selection?" question.
- **35a(5)** has no record of what it paid for; the page shows the literacy MTSS the grant required,
  from Troy's Oct. 2018 and Oct. 2019 third-grade reading presentations, and says so plainly.
- **35a(9)** has no board record at all beyond a "Summer Learning" agenda item in Sept. 2020.
- `/history`: 35a(9) now quotes 2019 PA 162 (new source doc `PA2019-162`); the 35m description has the
  2024-25 two-part award; the Troy lines for 35a, 35a(9), 35m and LETRS were updated.
- Fixed on both pages: the hero had no side gutter (`.hero{padding:56px 0 40px}` overrode `.wrap`).

**How the board records were searched:** the tsd-boarddocs D1 database (FTS table `chunks`, and
`transcript_utts` for meeting transcripts), queried with
`npx wrangler d1 execute tsd-boarddocs --remote --json --command "..."` from `~/Downloads/tsd-boarddocs`.
Every query, including the ones that found nothing, is listed in `docs/FINDINGS.md` §6. Board
documents are linked at `media.karpowitsch.org/troysd-boarddocs/...`; copies of the pages used are in
`sources/troy/`, and transcript excerpts with offsets are in `sources/troy/transcripts/`. The
transcripts are machine-made: check the speaker against context before quoting (the public-comment
speakers on 2025-06-03 are attributed to the chair), and keep the "[35m]"/"[UFLI]" brackets.

## Pick up in five steps

1. `gh repo clone akarpo/tsd-section35` and `cd tsd-section35`.
2. Read `README.md` (layout, rules, the dates when numbers change), then `docs/FIGURES.md` (every
   figure on the page with its source and page), then `docs/FINDINGS.md` (the research notes,
   including what was searched for and not found).
3. `pip install playwright pymupdf` if they're missing, then `python -I tools/qa.py` to render the
   page at 1280/390 px in light and dark mode (screenshots land in `qa-out/`, which is git-ignored).
4. Edit `public/index.html` (add the `docs/FIGURES.md` row first for any new number) or, for
   `/history`, `sources/history/programs.json` and then `python -I tools/build_history.py`. Chart and CSV
   data come only from `python -I tools/build_data.py`, which re-checks the parsed CSVs against the
   PDF pages and fails on any mismatch. Run `python -I tools/qa.py` again and look at the screenshots.
5. Commit and push to `main`. Cloudflare Pages deploys in about a minute. Confirm with
   `python -I tools/cloudflare.py status` (needs `CF_CRED_FILE`, see below) and
   `python -I tools/qa.py --live --links`. `qa.py` covers both pages, at 1280, 390 and 360 px, and
   fails on any on-screen text under 12.5 px.

## What the site says (as of 2026-11-18)

- **35j, confirmed:** Troy received **$0** of Section 35j, the one-time $140M literacy grant
  (2023 PA 103), paid at $311.08 per pre-K–5 pupil to districts that applied between Jan. 26 and
  Feb. 23, 2024. Troy's status-report pages for FY2024 and FY2025 have no 35j line, and Oakland
  Schools got none either. **22 of Oakland County's 28 local districts got it**; the other five
  without it are Pontiac, Clarenceville, South Lyon, Oak Park and Clawson.
- **Estimate:** 5,217 pre-K–5 pupils (NCES fall 2022) × $311.08 = **about $1.6M**, which would have
  made Troy the county's third-largest recipient. The method holds: every recipient's total ÷ $311.08
  equals its NCES count exactly (22 of 22).
- **"Troy didn't apply" is an inference**, labeled "likely, not documented." MDE says "434 LEAs
  applied for and received funding" and mentions no denials; no Troy board document mentions 35j.
- **Unrecoverable:** the grant period ended Sept. 30, 2025, and 35j was repealed (2025 PA 15,
  effective Oct. 7, 2025).
- **Troy's other Section 35 money:** 35a(5) of about $155–184K a year ended in FY2026; 35m paid
  $1,120,928 (2024-25 award). The **2025-26 35m award of $1,173,876 was unpaid in the Nov. 20, 2026
  status report**, when Birmingham's ($720,411) and other Oakland districts' were paid.
- **35d, the $1M Orton-Gillingham grant:** $1,000,000 statewide for 2026-27 (2026 PA 25), first-come,
  first-served, applications in NexSys in spring 2027 (MDE's Nov. 17, 2026 literacy bulletin). **No
  press release** with "$1M for Orton-Gillingham" was found; if one turns up, compare it and cite it.
- **Questions:** seven questions for the district on the page; no one is named.

## Open items and watch list

- **Each month around the 20th:** whether the 2025-26 35m award has been paid (Oakland ISD report at
  `https://mdoe.state.mi.us/samspublic/Home/StatusReport`, ISD 63, Troy = district 63150). Update the
  page and `docs/FIGURES.md` when it is.
- **Dec. 2026:** 2026-27 35m applications open. **Spring 2027:** 35d applications open.
  **Aug. 1, 2027 and the start of 2027-28:** PA 146 screening deadlines.
- **Did Troy apply for 35j?** Unanswered. A FOIA request to Troy or MDE for 35j application records
  would settle it. If the district answers, replace the "likely" verdict with what it says, with a
  link.
- **35m product:** answered in part. At the Apr. 28, 2026 workshop the Director of Teaching &
  Learning said "we amended our grant application, and it was approved" (video 1:03:33); the board
  approved the $1,093,710 Being a Reader purchase 7-0 on May 19, 2026. **Still unknown:** which award
  (2024-25 or 2025-26) was amended and whether the amount changed; MDE's lists record UFLI for both.
  It is question 5 on the page.
- **Unexplained:** the status reports show 416 (FY2024) and 402 (FY2025) entities with a 35j line,
  vs. MDE's 434 and 420.
- **From the research pass, not re-checked by hand:** the 35m and 35d appropriation history and HB
  5081 (`docs/FINDINGS.md` says so). Re-check before putting any of it on the page.
- **`/history` uses the main page's share card.** A history-specific card would need a new file
  name (see the share-card pitfall below).
- **Not fetched:** 2025 PA 15 (FY2026 figures come from HFA's line-item summary instead). 2019 PA 162
  was fetched on 11/19 afternoon; its Sec. 35a pages are in `sources/statute/acts/`.
- **Not done, only offered:** a link between this site and the sibling site
  <https://tsd-mpsers.karpowitsch.org> (repo `akarpo/mpsers`).

## Pitfalls already hit (don't repeat them)

- **MDE status-report PDFs and the 35m grantee lists scramble their columns** in pdftotext (one 35m
  amount came out as $410,204 instead of $1,120,928). Render the page (PyMuPDF `get_pixmap`) and
  read the image before quoting an amount.
- Never type chart or CSV values by hand; `tools/build_data.py` writes the `/*DATA:BEGIN*/` block
  and `public/assets/oakland-section35j.csv`.
- Keep estimates labeled ("our estimate", "about") and keep Troy's chart bar visibly different
  (dashed outline) from received money.
- **Everything in `public/` is deployed.** Keep scratch output elsewhere; `qa-out/` is git-ignored.
- A changed share card needs a **new file name** (and updated `og:image`/`twitter:image`) or link
  previews keep the old one. `python -I tools/qa.py --card public/assets/<new-name>.png` renders it.
- **Never run `wrangler pages deploy`**; it shadows the Git-connected deployment.

## Credentials

Cloudflare API credentials are never in this repo. `tools/cloudflare.py` reads the text file named
by the `CF_CRED_FILE` environment variable (labeled lines "Cloudflare Pages/DNS token",
"Cloudflare account", "karpowitsch.org zone"). The site owner keeps that file. Never print or
commit its values. Day-to-day work doesn't need it: a push to `main` deploys.
