# Figure log

Every figure on the page, with where it comes from. Copies of each source are in `sources/`.

**Abbreviations**
- **SR-yy**: MDE State Aid Financial Status Report, statewide final report for state FY 20yy (file `ALLyy11.pdf` in MDE's SAMS archive). Troy's pages for FY2017–FY2026 are in `sources/state-aid/Troy-63150-status-report-pages-FY2017-FY2026.pdf`; Oakland districts' pages for FY2024–FY2026 are in `sources/state-aid/Oakland-districts-status-report-pages-FY20yy.pdf`.
- **ISD63-1126**: MDE status report for Oakland ISD districts, payment dated 11/20/2026 (`sources/state-aid/ISD63-status-report-2026-11-20-...pdf`).
- **PA103**: 2023 PA 103, Sec. 35j, pp. 80–81 (`sources/statute/2023-PA-0103-pp80-81-Sec35j.pdf`).
- **MEMO**: MDE, Section 35j memo, Jan. 25, 2024 (`sources/mde/`).
- **RPT**: MDE, "35a Legislative Memo and Report 2024-25", Dec. 23, 2025 (`sources/mde/`).
- **NCES**: NCES Common Core of Data, fall 2022 enrollment by grade, via the Urban Institute Education Data API (`sources/nces/`).
- **SR-16**: the FY2016 statewide final report (`ALL1611.pdf`, payment dated 08/22/2016), parsed by `tools/parse_status_report.py` into `sources/parsed/s35_FY2016.csv` (all 510 rows: amount = previous + current).
- **parsed**: `sources/parsed/s35_FY20yy.csv`, every Section 35 line in each statewide report. Spot-checked against rendered pages (Troy FY2024/FY2025, Birmingham FY2024, Oakland Schools FY2024–FY2026); `tools/build_data.py` also re-checks 35j presence for all 28 Oakland districts against the PDF pages.

## Headline and findings

| Figure | Value | Source |
|---|---|---|
| Troy's 35j, 2023–24 and 2024–25 | $0 (no 35j line) | SR-24 p. 1124; SR-25 p. 1127 (Troy pages in `state-aid/Troy-...pdf`) |
| Oakland Schools (ISD 63000) 35j | none | SR-24 p. 1095 |
| Section 35j: up to $140,000,000, "for 2023-2024 only" | quote | PA103 Sec. 35j(1) |
| 22 of 28 Oakland local districts received 35j | calc | `tools/build_data.py` over parsed + PDF pages; non-recipients Pontiac, Clarenceville, Troy, South Lyon, Oak Park, Clawson |
| Birmingham FY2024 35j $506,286.00 (example) | | SR-24 p. 1097 (rendered and read) |
| "434 LEAs applied for and received funding"; $311.08 per pupil | quote | RPT, 35j section |
| "420 LEAs met the requirements and received their remaining funding"; "14 LEAs opted not to receive Year 2 funding or did not submit the required documentation"; "Since the grant expenditure period ended September 30, 2025, these 14 LEAs are no longer eligible to receive funding." | quote | RPT |
| Application window Jan. 26 – Feb. 23, 2024 (4:30 p.m.); "only be one (1) application window"; per-pupil on 2022-23 end-of-year PK-5 count; 50% 2023-24, 50% 2024-25 | quote | MEMO |
| Eligibility, ISD may apply "on behalf of their constituent districts"; conditions (a)–(d) | quote | PA103 Sec. 35j(2), (4) |
| Uses: PD for all PK-5 teachers, administrators, coaches; "comprehensive literacy system" | quote | PA103 Sec. 35j(3) |
| Work project ending Sept. 30, 2025 | | PA103 Sec. 35j(6) |
| Repealed by 2025 PA 15, immediate effect Oct. 7, 2025 | | MCL 388.1635j (`sources/statute/mcl-388-1635j.pdf`) |

## Oakland County chart and estimate

| Figure | Value | Source |
|---|---|---|
| Each district's FY2024, FY2025 35j and FY2026 adjustment | generated | parsed (SR-24, SR-25, SR-26) via `tools/build_data.py`; CSV `public/assets/oakland-section35j.csv` |
| FY2026 recaptures: Clarkston −$318,566.65; Rochester −$215,821.51; Walled Lake −$49,782.77 | | SR-26 (parsed) |
| Troy PK-5, fall 2022 | 5,217 (PK 133, K 868, 1: 753, 2: 821, 3: 838, 4: 867, 5: 937) | NCES, LEA 2634260 |
| Estimate 5,217 × $311.08 = $1,622,904.36 (calc) | | calc |
| Dilution-adjusted ≈ $1,604,300 (calc) | $140,000,000 ÷ 311.08 = 450,045 pupils; + 5,217 = 455,262; $140M ÷ 455,262 = $307.52; × 5,217 | calc |
| Method check: every recipient's total ÷ $311.08 = its NCES PK-5 count | 22 of 22 exact | `tools/build_data.py` (fails the build otherwise) |
| Troy would be third-largest (after Rochester 6,601 and Walled Lake 5,569 pupils) | calc | CSV |
| 416 entities with a 35j line in SR-24 (MDE: 434) | count | parsed |

## Troy's Section 35 history

| Figure | Value | Source |
|---|---|---|
| 35a(6) FY2016 (first year of 35a; added 2026-11-19) | $146,190.00 | SR-16 p. 1028 (`state-aid/Troy-63150-status-report-page-FY2016-p1028.pdf`; rendered and read; previous 132,886.71 + current 13,303.29) |
| 35a(5) FY2017–FY2025 | $135,630.00; $183,750.00; $181,460.14; $178,485.00; $173,896.00; $169,404.11; $170,226.00; $155,030.00; $176,655.00 | SR-17 p. 1127, SR-18 p. 1129, SR-19 p. 1135, SR-20 p. 1130, SR-21 p. 1123, SR-22 p. 1125, SR-23 p. 1132, SR-24 p. 1124, SR-25 p. 1127 |
| 35a(9) summer reading FY2020 | $25,629.84 | SR-20 p. 1130 |
| 35m "2025 LITERACY SUPPORTS" (prior-year adjustment) | $1,120,928.00 | SR-26 p. 1129; MDE 2024-25 35m grantee list p. 17 ("UFLI Foundations, 1st Edition", rendered and read) |
| 35m 2025-26 award | $1,173,876 ("UFLI Foundations, 1st Edition") | MDE FY-26 Section 35m grantees xlsx, sheet "Exhibit A" |
| Not paid as of 11/20/2026 (no 35m line on Troy's pages) | | ISD63-1126 pp. 32–33 |
| Birmingham "35m(1) 2026 LITERACY SUPPORTS" $720,411.00 paid 11/20/2026 | | ISD63-1126 p. 6; MDE FY-26 list ("Orton-Gillingham Plus (OG+), 2025", 720411) |
| 35a(5) eliminated FY2026: "Eliminates $19.9 million SAF" | quote | HFA FY2025-26 enacted summary (`sources/hfa/`) |
| Troy's Jan. 2026 amendment: 35(A) Early Literacy $176,655 → $0 | | TSD budget presentation, Jan. 20, 2026, p. 3 (`sources/troy/`) |
| Oakland Schools 35a(4) early literacy coaches $3,000,000 a year FY2024–FY2026 | | parsed (SR-24 p. 1095, SR-25 p. 1099, SR-26 p. 1098) |
| Memo: "Collaborative Literacy: Being a Reader at scale for all elementary students"; "$1,093,710"; "will come from our 35m grant allocation"; UFLI K-2 pilots ≈ $2,000 + $8,000 | quote | TSD memo, May 13, 2026, Director of Teaching & Learning to the Assistant Superintendent of Business (`sources/troy/`) |

## Section 35d and the dyslexia law

| Figure | Value | Source |
|---|---|---|
| Sec. 35d: $1,000,000 for 2026-2027 only, grants to districts and ISDs; first-come, first-served | quote | 2026 PA 25 p. 68 (`sources/statute/`); MDE Section 35d page (`sources/mde/mde_grants_section-35d.html`) |
| Approved providers MDI and IMSE; choose provider, number of staff | | MDE Section 35d page |
| "The 26-27 Section 35d Dyslexia Orton Gillingham Program Grant application will open for districts in NexSys in spring 2027. Districts will apply on a first-come, first-served basis until all funds are allocated." | quote | MDE GovDelivery, "MDE Literacy Unit K-12 Updates - November 2026", sent 11/17/2026 (`sources/mde/govdelivery_...html`) |
| 2024-25: "$400,000 to Michigan Dyslexia Institute (MDI) and $600,000 to the Institute for Multi-Sensory Education (IMSE)" | quote | RPT |
| 2023-24 Sec. 35d: $1,000,000, grants to districts and ISDs, first-come, first-served (as enacted) | | 2023 PA 103 p. 80 |
| Lapsed in 2025-26 | | HFA FY2025-26 summary, one-time items not continued ("Sec. 35d – Orton-Gillingham ($1.0 million SAF)") |
| PA 146: update screener selection "By not later than August 1, 2027"; K–3 dyslexia screening "By not later than the beginning of the 2027-2028 school year"; professional learning assurance by the same date | quote | 2024 PA 146, subsections (6), (15), (7) (`sources/law/`) |
| Troy board "PA 146 Legislative Overview", June 3, 2025 | | TSD board archive (`sources/troy/`) |
| No press release with "$1 million" found Nov. 16–18, 2026 | search | MDE, Governor and MiLEAP press pages searched 11/18/2026 (see `docs/FINDINGS.md`) |
| No Troy board document mentions 35j | search | tsd-boarddocs archive searches listed in `docs/FINDINGS.md` |

## The history page (`/history`)

Every budget amount on `public/history.html` comes from `sources/history/programs.json`, where each
grant-year carries a short quote and the source it is quoted from. `tools/build_history.py` fails
unless each quote is found in that source (acts in `sources/statute/acts/`, HFA line-item summaries
in `sources/hfa/line-items/`, the MDE report, MCL history notes, the Nov. 17, 2026 bulletin) and the
amount appears in the quote. The page prints the page number where the quote was found. Page
numbers are PDF page numbers of the full document (the excerpt files are named with them).

Payment figures on the page (paid, recipients, Troy, Oakland Schools) are computed from every
Section 35 line in `sources/parsed/s35_FY2016.csv` through `s35_FY2026.csv`; the build fails if any
line maps to no grant or to two. Payment facts named in the prose (e.g. "556 districts", "paid to
Livonia", "$50,000 to $212,000", "Five Oakland County districts ... READ") are `facts` entries in
`programs.json` and are checked against the same data. Facts quoted from documents (e.g. "561
districts", "115 applications", "$400,000 to MDI") are `checks` entries and are checked against
their source text.

| Figure (history page) | Value | Source |
|---|---|---|
| Total budgeted in Section 35, FY2016–FY2027 | $1,157,123,000 | sum of `programs.json` final amounts (35m FY2026 counted once; Literacy Essentials inside it is not added again) |
| By year | FY2016 $21.50M, FY2017 $24.90M, FY2018 $30.40M, FY2019 $31.65M, FY2020 $57.70M, FY2021 $60.42M, FY2022 $71.60M, FY2023 $75.90M, FY2024 $245.40M, FY2025 $180.90M, FY2026 $122.25M, FY2027 $234.50M | `tools/build_history.py` output |
| 27 grants with money (28 entries; 35q has none) | count | `programs.json` |
| $250,000 to $140 million | smallest/largest single-year amounts | 35b, 35e (library study); 35j |
| Troy received $2,817,284.09 from Section 35, FY2016–FY2026 | sum | parsed (all Troy lines); by report: FY2016 $146,190.00 … FY2026 $1,120,928.00 |
| Troy paid under exactly three grants (35a extra time, 35a(9) summer reading, 35m) | check | `troy_programs` in `programs.json`, checked by the build |
| "Only the literacy coaches have been funded every year"; "most lasted one or two budgets" (17 of 27 with ≤ 2 years) | count | `programs.json` |
| FY2016 Section 35a cut from $23.9M SAF to $19.0M SAF in June 2016; parent pilots ($1.0M) dropped; added time $17.5M → $13.6M | quote | 2015 PA 85 pp. 37–39; 2016 PA 249 pp. 43–45 |
| FY2016 coaches $3.0M (HFA's FY2015-16 summary says $3.5M; the act says $3,000,000.00 and the SAF total only adds up with $3.0M) | quote | 2015 PA 85 p. 39; 2016 PA 249 p. 44 |
| FY2020 amounts (coaches $31.5M, summer reading $5.0M restored, MEC and principals' training vetoed, 35c restored, 35d SEL pilot vetoed) | HFA | HFA FY2019-20 line-item summary pp. 15–16 (post-enrollment notes). 2019 PA 58 is a scanned image and 2019 PA 162 was not retrievable (legislature.mi.gov refused; Wayback 403) |
| FY2026 amounts (35a $52.0M = coaches $42.0M + LETRS $10.0M; 35e $250K; 35m $70.0M incl. $4.0M essentials and $1.6M MiMTSS) | HFA | HFA FY2025-26 line-item summary p. 14 (2025 PA 15 not retrievable the same way) |
| 35d paid first-come, first-served | statute | the clause is in Sec. 35d of 2020 PA 165, 2021 PA 48, 2022 PA 144, 2023 PA 103, 2024 PA 120 and 2026 PA 25 (checked by hand 11/19) |
