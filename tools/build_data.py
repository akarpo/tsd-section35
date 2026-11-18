"""Build the Section 35j data for the page from the sources in this repo.

Inputs (all in sources/):
  parsed/s35_FY2024.csv, s35_FY2025.csv, s35_FY2026.csv  Section 35 lines parsed from MDE's
      statewide State Aid Financial Status Reports (ALL2411/ALL2511/ALL2611.pdf).
  state-aid/Oakland-districts-status-report-pages-FY2024.pdf / FY2025.pdf  the same districts'
      pages, extracted from those reports. Used to re-check, district by district, whether a
      35j line is present, independently of the parsed CSV.
  nces/enr_2022_*.json  NCES Common Core of Data, fall 2022 enrollment, Troy (LEA 2634260).

Outputs:
  public/assets/oakland-section35j.csv
  public/index.html, between /*DATA:BEGIN*/ and /*DATA:END*/

Run: python -I tools/build_data.py
"""
import csv, json, pathlib, re, sys
import fitz

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "sources"
RATE = 311.08  # MDE: "a per-pupil allocation of $311.08" (35a legislative report, Dec. 23, 2025, p. 6)

# Display names for the 28 Oakland County local districts (labels only; codes are the key).
NAMES = {
    "63010": "Birmingham", "63020": "Ferndale", "63030": "Pontiac", "63040": "Royal Oak",
    "63050": "Berkley", "63060": "Southfield", "63070": "Avondale", "63080": "Bloomfield Hills",
    "63090": "Clarenceville", "63100": "Novi", "63110": "Oxford", "63130": "Hazel Park",
    "63140": "Madison", "63150": "Troy", "63160": "West Bloomfield", "63180": "Brandon",
    "63190": "Clarkston", "63200": "Farmington", "63210": "Holly", "63220": "Huron Valley",
    "63230": "Lake Orion", "63240": "South Lyon", "63250": "Oak Park", "63260": "Rochester",
    "63270": "Clawson", "63280": "Lamphere", "63290": "Walled Lake", "63300": "Waterford",
}


def amt(s):
    s = s.strip().replace("$", "").replace(",", "")
    neg = s.startswith("(") and s.endswith(")")
    v = float(s.strip("()") or 0)
    return -v if neg else v


def parsed_35j(fy):
    out, names = {}, {}
    with open(SRC / "parsed" / f"s35_FY{fy}.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["code"] == "35j":
                out[r["district"]] = out.get(r["district"], 0) + amt(r["amount"])
                names[r["district"]] = r["name"]
    return out, names


def pdf_has_35j(fy):
    """district code -> True/False: does that district's page carry a 35j line?"""
    d = fitz.open(SRC / "state-aid" / f"Oakland-districts-status-report-pages-FY{fy}.pdf")
    res, cur = {}, None
    for p in d:
        t = p.get_text()
        m = re.search(r"District:\s*(\d{5})", t)
        if m:
            cur = m.group(1)
            res.setdefault(cur, False)
        if cur and re.search(r"^35j\b", t, re.M):
            res[cur] = True
    return res


def main():
    fy24, full_names = parsed_35j(2024)
    fy25, _ = parsed_35j(2025)
    fy26, _ = parsed_35j(2026)
    chk24, chk25 = pdf_has_35j(2024), pdf_has_35j(2025)

    rows = []
    for code, short in NAMES.items():
        if code not in chk24 or code not in chk25:
            sys.exit(f"{code} {short}: page not found in the extracted Oakland pages")
        a, b = fy24.get(code, 0.0), fy25.get(code, 0.0)
        if (a != 0) != chk24[code] or (b != 0) != chk25[code]:
            sys.exit(f"{code} {short}: parsed CSV and PDF disagree about a 35j line")
        rows.append({"code": code, "name": short, "fy24": a, "fy25": b,
                     "adj26": fy26.get(code, 0.0), "total": a + b})
    received = [r for r in rows if r["total"] > 0]
    if len(rows) != 28:
        sys.exit("expected 28 Oakland local districts")

    # Troy's PK-5 count (NCES fall 2022) and the equal-per-pupil estimate
    pk5 = 0
    for g in ["pk", "k", "1", "2", "3", "4", "5"]:
        j = json.load(open(SRC / "nces" / f"enr_2022_{g}.json", encoding="utf-8"))
        pk5 += sum(x["enrollment"] for x in j["results"] if str(x["leaid"]) == "2634260")
    est = round(pk5 * RATE, 2)

    # Check the estimation method: every recipient's total / $311.08 should equal its NCES PK-5 count.
    d = json.load(open(SRC / "nces" / "dir_oakland_2022.json", encoding="utf-8"))
    lea_to_code = {str(r["leaid"]): str(r["state_leaid"]).split("-")[-1][-5:] for r in d["results"] if r.get("state_leaid")}
    nces = {}
    for g in ["pk", "k", "1", "2", "3", "4", "5"]:
        j = json.load(open(SRC / "nces" / f"enr_mi_2022_{g}.json", encoding="utf-8"))
        for x in j["results"]:
            c = lea_to_code.get(str(x["leaid"]))
            if c and x.get("enrollment") and x["enrollment"] > 0:
                nces[c] = nces.get(c, 0) + x["enrollment"]
    for r in received:
        if abs(r["total"] / RATE - nces.get(r["code"], -1)) >= 0.6:
            sys.exit(f"{r['code']} {r['name']}: total/rate does not match NCES PK-5 ({nces.get(r['code'])})")
    if nces.get("63150") != pk5:
        sys.exit("Troy PK-5 differs between the Troy files and the statewide files")

    # CSV download
    out = ROOT / "public" / "assets" / "oakland-section35j.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["district_code", "district", "fy2024_35j", "fy2025_35j", "fy2026_adjustment",
                    "two_year_total", "implied_pk5_pupils_at_311.08", "received_35j"])
        for r in sorted(rows, key=lambda r: -r["total"]):
            w.writerow([r["code"], full_names.get(r["code"], r["name"]), f"{r['fy24']:.2f}", f"{r['fy25']:.2f}",
                        f"{r['adj26']:.2f}", f"{r['total']:.2f}",
                        f"{r['total']/RATE:.1f}" if r["total"] else "", "yes" if r["total"] else "no"])

    # JS data block
    js = {"rate": RATE, "troyPk5": pk5, "troyEst": est,
          "oak": [{"c": r["code"], "n": r["name"], "v": round(r["total"], 2), "y1": round(r["fy24"], 2),
                   "y2": round(r["fy25"], 2), "a": round(r["adj26"], 2)}
                  for r in sorted(rows, key=lambda r: (-r["total"], r["name"]))]}
    block = "/*DATA:BEGIN*/var D=" + json.dumps(js, separators=(",", ":")) + ";/*DATA:END*/"
    page = ROOT / "public" / "index.html"
    html = page.read_text(encoding="utf-8")
    new, n = re.subn(r"/\*DATA:BEGIN\*/.*?/\*DATA:END\*/", lambda m: block, html, flags=re.S)
    if n != 1:
        sys.exit("DATA markers not found exactly once in index.html")
    page.write_bytes(new.encode("utf-8"))

    print(f"{len(received)} of {len(rows)} Oakland local districts received 35j; "
          f"non-recipients: {', '.join(r['name'] for r in rows if not r['total'])}")
    print(f"Troy PK-5 (NCES fall 2022) = {pk5}; x ${RATE} = ${est:,.2f}")
    print(f"Oakland recipients' 2-year total: ${sum(r['total'] for r in rows):,.2f}")


if __name__ == "__main__":
    main()
