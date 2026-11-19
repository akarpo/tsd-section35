"""Parse Section 35 lines from an MDE statewide State Aid Financial Status Report.
usage: parse_sr.py REPORT.pdf OUT.csv   (same columns as sources/parsed/s35_FY20yy.csv)"""
import sys; sys.path.append("/Users/Alex/Library/Python/3.9/lib/python/site-packages")
import fitz, re, csv
pdf, out = sys.argv[1], sys.argv[2]
d = fitz.open(pdf)
MONEY = re.compile(r"\(?-?[\d,]+\.\d\d\)?")
PCT = re.compile(r"-?[\d.]+\s*%")
rows = []
for i, p in enumerate(d):
    L = [x.strip() for x in p.get_text().split("\n")]
    t = "\n".join(L)
    m = re.search(r"District:\s*(\d{5})\s+ISD:\s*(\d+)", t)
    if not m: continue
    dist, isd = m.group(1), m.group(2)
    k0 = next(k for k, x in enumerate(L) if x.startswith("District:"))
    name = L[k0 + 1]
    pd = re.search(r"Payment Dated:\s*(\S+)", t)
    block = "current"
    for k, x in enumerate(L):
        if "PRIOR YEAR" in x.upper(): block = "prior"
        if "CURRENT YEAR" in x.upper(): block = "current"
        if re.fullmatch(r"35[a-z]?(\(\d+\))?", x):
            lab = L[k + 1]
            toks = " ".join(L[k + 2:k + 7])
            money = MONEY.findall(PCT.sub(" ", toks))[:3]
            pct = PCT.findall(toks)[:1]
            if len(money) < 3 or not pct:
                sys.exit(f"page {i+1} {dist} {x}: could not read amount/previous/current from {toks!r}")
            rows.append([pdf.split("/")[-1], pd.group(1) if pd else "", i + 1, dist, isd, name, block, x, lab,
                         money[0], money[1], money[2], pct[0].replace(" ", "")])
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["file", "payment_dated", "page", "district", "isd", "name", "block", "code", "label", "amount", "previous", "current", "pct"])
    w.writerows(rows)
print(len(rows), "rows ->", out)
