# Handoff: start here

Last updated **2026-11-18**. The site is live and finished; nothing was left half-done. The local
working copy was deleted after everything was pushed, so GitHub is the only copy.

## Pick up in five steps

1. `gh repo clone akarpo/tsd-section35` and `cd tsd-section35`.
2. Read `README.md` (layout, rules, the dates when numbers change), then `docs/FIGURES.md` (every
   figure on the page with its source and page), then `docs/FINDINGS.md` (the research notes,
   including what was searched for and not found).
3. `pip install playwright pymupdf` if they're missing, then `python -I tools/qa.py` to render the
   page at 1280/390 px in light and dark mode (screenshots land in `qa-out/`, which is git-ignored).
4. Edit `public/index.html` (add the `docs/FIGURES.md` row first for any new number). Chart and CSV
   data come only from `python -I tools/build_data.py`, which re-checks the parsed CSVs against the
   PDF pages and fails on any mismatch. Run `python -I tools/qa.py` again and look at the screenshots.
5. Commit and push to `main`. Cloudflare Pages deploys in about a minute. Confirm with
   `python -I tools/cloudflare.py status` (needs `CF_CRED_FILE`, see below) and
   `python -I tools/qa.py --live --links`.

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
- **35m product:** MDE's list records Troy's choice as UFLI Foundations; the May 13, 2026 memo spends
  $1,093,710 of 35m on Collaborative Literacy: Being a Reader. Whether Troy amended its selection is
  not known.
- **Unexplained:** the status reports show 416 (FY2024) and 402 (FY2025) entities with a 35j line,
  vs. MDE's 434 and 420.
- **From the research pass, not re-checked by hand:** the 35m and 35d appropriation history and HB
  5081 (`docs/FINDINGS.md` says so). Re-check before putting any of it on the page.
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
