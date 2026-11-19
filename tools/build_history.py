"""Build the Section 35 history page (public/history.html) from sources/history/programs.json.

Checks, and fails on any miss:
  * every amount's quote ('q', 'q2', 'origq') appears in the cited source file, and the amount
    (or each of its 'parts') appears in the quote;
  * every 'checks' quote (facts used in the prose) appears in its source;
  * every Section 35 line in sources/parsed/s35_FY20yy.csv (FY2016-FY2026 statewide reports)
    maps to exactly one grant through the 'pay' lists;
  * every 'facts' entry (payment figures named in the prose) matches the payment data.

Writes:
  public/history.html                       between <!--GEN:x:BEGIN--> / <!--GEN:x:END--> markers
                                            and /*DATA:BEGIN*/ /*DATA:END*/
  public/assets/section35-grants-by-year.csv
  public/assets/section35-payments-by-year.csv
  and stamps ?v=<hash> on the CSV links in public/history.html

Run: python -I tools/build_history.py   (needs PyMuPDF)
"""
import csv, glob, hashlib, html, io, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
for p in ("/Users/Alex/Library/Python/3.9/lib/python/site-packages",):   # PyMuPDF user install
    if pathlib.Path(p).is_dir() and p not in sys.path:
        sys.path.append(p)
import fitz  # noqa: E402

DATA = ROOT / "sources" / "history" / "programs.json"
PAGE = ROOT / "public" / "history.html"
OUT_GRANTS = ROOT / "public" / "assets" / "section35-grants-by-year.csv"
OUT_PAY = ROOT / "public" / "assets" / "section35-payments-by-year.csv"
TROY, OAKSCH = "63150", "63000"
FIRST_FY, LAST_FY = 2016, 2027
CODE = re.compile(r"35[a-z]?(\(\d+\))?")
CHART = [("coaches", "Literacy coaches at ISDs (35a)"), ("time", "Extra reading time (35a)"),
         ("big", "Section 35j and 35m grants to districts"), ("other", "All other Section 35 grants")]

problems = []


def fail(msg):
    problems.append(msg)


def norm(s):
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-"), ("­", "")):
        s = s.replace(a, b)
    return re.sub(r"\s+", "", s)


_doc_cache = {}


def doc_pages(key, docs):
    if key not in _doc_cache:
        d = docs[key]
        f = ROOT / d["file"]
        if f.suffix == ".pdf":
            pages = [p.get_text() for p in fitz.open(f)]
        else:
            t = f.read_text(encoding="utf-8", errors="replace")
            t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
            pages = [html.unescape(re.sub(r"<[^>]+>", " ", t))]
        _doc_cache[key] = [norm(p) for p in pages]
    return _doc_cache[key]


def find(key, q, docs):
    """Page number (in the original document's numbering) where the quote appears, else None."""
    pages, nq = doc_pages(key, docs), norm(q)
    first = docs[key]["first"]
    for i, p in enumerate(pages):
        if nq in p:
            return first + i
    for i in range(len(pages) - 1):          # quote running across a page break
        if nq in pages[i] + pages[i + 1]:
            return first + i
    return None


def money_forms(v):
    v = float(v)
    out = [f"${v:,.2f}", f"{v:,.0f}"]
    if v >= 1e6:
        out.append(f"${v/1e6:.1f} million")
    return [norm(x) for x in out]


def amt(s):
    s = s.replace(",", "").replace("$", "").strip()
    neg = s.startswith("(") or s.startswith("-")
    return -float(s.strip("()-")) if neg else float(s.strip("()-"))


def fy_label(fy):
    return f"{fy-1}–{str(fy)[2:]}"


def usd(v, dec=0):
    s = f"${abs(v):,.{dec}f}"
    return ("−" if v < 0 else "") + s


def usd_compact(v):
    if v >= 1e6:
        x = v / 1e6
        return f"${x:,.1f}M" if x < 100 else f"${x:,.0f}M"
    if v >= 1e3:
        return f"${v/1e3:,.0f}K"
    return f"${v:,.0f}"


def prose(s):
    """Plain text with *bold* -> safe HTML, with typographic quotes and en dashes for ranges."""
    s = html.escape(s, quote=False)
    s = re.sub(r"\*(.+?)\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(\d{4})-(\d{2})\b", "\\1&ndash;\\2", s)          # 2015-16 -> 2015–16
    s = re.sub(r"\bpre-K-(\d)", "pre-K&ndash;\\1", s)
    s = re.sub(r"\b([K\d])-(\d)\b", "\\1&ndash;\\2", s)             # K-3, 2-3
    s = re.sub(r'(^|[\s(])"', "\\1&ldquo;", s)
    s = s.replace('"', "&rdquo;")
    s = re.sub(r"(\w)'(\w)", "\\1&rsquo;\\2", s)
    s = re.sub(r"(\w)'(?=[\s,.;:)]|$)", "\\1&rsquo;", s)
    return s


def main():
    J = json.loads(DATA.read_text(encoding="utf-8"))
    docs, progs = J["docs"], J["programs"]
    for k, d in docs.items():
        if not (ROOT / d["file"]).exists():
            fail(f"doc {k}: missing file {d['file']}")
    if problems:
        sys.exit("\n".join(problems))

    # ---------- 1. amounts and quotes ----------
    cites = {}      # (prog id, fy) -> list of (doc, page)
    for pr in progs:
        for y in pr["years"]:
            key = (pr["id"], y["fy"])
            cites[key] = []
            for qk, dk in (("q", "doc"), ("q2", "doc"), ("origq", "origdoc")):
                if qk not in y:
                    continue
                pg = find(y[dk], y[qk], docs)
                if pg is None:
                    fail(f"{pr['id']} FY{y['fy']}: quote not found in {y[dk]}: {y[qk][:80]!r}")
                else:
                    cites[key].append((y[dk], pg))
            qtext = norm(y.get("q", "") + y.get("q2", ""))
            if "parts" in y:
                if abs(sum(y["parts"]) - y["amt"]) > 0.5:
                    fail(f"{pr['id']} FY{y['fy']}: parts don't add to amt")
                for part in y["parts"]:
                    if not any(f in qtext for f in money_forms(part)):
                        fail(f"{pr['id']} FY{y['fy']}: part {part} not in quote")
            elif y["amt"]:
                if not any(f in qtext for f in money_forms(y["amt"])):
                    fail(f"{pr['id']} FY{y['fy']}: amount {y['amt']:,} not in quote")
            if y.get("orig") is not None:
                otext = norm(y.get("origq", "") + (y.get("q", "") if y["amt"] == 0 else ""))
                if not any(f in otext for f in money_forms(y["orig"])):
                    fail(f"{pr['id']} FY{y['fy']}: original amount {y['orig']:,} not in quote")
        for c in pr.get("checks", []):
            if find(c["doc"], c["q"], docs) is None:
                fail(f"{pr['id']}: check quote not found in {c['doc']}: {c['q'][:80]!r}")

    # ---------- 2. payments ----------
    pmap = {}
    for pr in progs:
        for pyr, code in pr.get("pay", []):
            if (pyr, code) in pmap:
                fail(f"payment key {(pyr, code)} mapped twice")
            pmap[(pyr, code)] = pr["id"]
    lines = []
    for f in sorted(glob.glob(str(ROOT / "sources" / "parsed" / "s35_FY20??.csv"))):
        rfy = int(re.search(r"FY(\d{4})", f).group(1))
        with open(f, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if not CODE.fullmatch(r["code"]):
                    continue                   # stray non-Section-35 rows in the parsed files
                if r["block"] == "prior":
                    m = re.match(r"(\d{4}) ", r["label"])
                    if not m:
                        fail(f"{f}: prior-year line without a year: {r}")
                        continue
                    pyr = int(m.group(1))
                else:
                    pyr = rfy
                pid = pmap.get((pyr, r["code"]))
                if not pid:
                    fail(f"unmapped payment line: report FY{rfy} program-year {pyr} {r['code']} {r['label']}")
                    continue
                lines.append({"pid": pid, "rfy": rfy, "pyr": pyr, "code": r["code"], "block": r["block"],
                              "d": r["district"], "isd": r["isd"], "name": r["name"], "v": amt(r["amount"])})
    seen = {(x["pyr"], x["code"]) for x in lines}
    for k, pid in pmap.items():
        if k not in seen:
            fail(f"{pid}: no payment lines for {k}")

    def sel(f):
        return [x for x in lines if x["pyr"] == f["pyr"] and x["code"] in f.get("codes", [f.get("code")])
                and (("block" not in f) or x["block"] == f["block"])]

    def by_dist(ls):
        out = {}
        for x in ls:
            out.setdefault(x["d"], [x["name"], x["isd"], 0.0])[2] += x["v"]
        return out

    for pr in progs:
        for f in pr.get("facts", []):
            t = f["t"]
            if t == "troy_range":
                vals = {}
                for x in lines:
                    if x["pid"] == pr["id"] and x["d"] == TROY and f["years"][0] <= x["pyr"] <= f["years"][1]:
                        vals[x["pyr"]] = vals.get(x["pyr"], 0) + x["v"]
                if len(vals) != f["years"][1] - f["years"][0] + 1 or round(min(vals.values()), 2) != f["min"] or round(max(vals.values()), 2) != f["max"]:
                    fail(f"{pr['id']} fact {f}: Troy by year = {vals}")
                continue
            if t == "range":
                ls = [x for x in lines if x["pid"] == pr["id"] and x["pyr"] in f["pyrs"] and x["code"] == f["code"] and x["block"] == f.get("block", x["block"])]
                per = {}
                for x in ls:
                    per[(x["pyr"], x["d"])] = per.get((x["pyr"], x["d"]), 0) + x["v"]
                vs = [round(v, 2) for v in per.values() if v > 0]
                if not vs or min(vs) != f["min"] or max(vs) != f["max"]:
                    fail(f"{pr['id']} fact {f}: got {min(vs) if vs else None}..{max(vs) if vs else None}")
                continue
            bd = {k: v for k, v in by_dist(sel(f)).items() if abs(v[2]) > 0.004}
            pos = {k: v for k, v in bd.items() if v[2] > 0}
            ok = True
            if t == "who":
                ok = len(pos) == 1 and list(pos.values())[0][0] == f["name"] and ("eq" not in f or round(list(pos.values())[0][2], 2) == f["eq"])
            elif t == "n":
                ok = len(pos) == f["eq"]
            elif t == "n_codes":
                ls2 = [x for x in lines if x["pyr"] == f["pyr"] and x["code"] in f["codes"] and x["pid"] == pr["id"]]
                ok = len({k for k, v in by_dist(ls2).items() if v[2] > 0}) == f["eq"]
            elif t == "troy":
                ok = round(bd.get(TROY, [0, 0, 0.0])[2], 2) == f["eq"]
            elif t == "names":
                ok = sorted(v[0] for v in pos.values()) == sorted(f["names"])
            elif t == "oakland_names":
                ok = sorted(v[0] for v in pos.values() if v[1] == "63") == sorted(f["names"])
            elif t == "amount_of":
                ok = [round(v[2], 2) for v in pos.values() if v[0] == f["name"]] == [f["eq"]]
            elif t == "each":
                ok = bool(pos) and all(round(v[2], 2) == f["eq"] for v in pos.values())
            elif t == "notin":
                ok = f["district"] not in pos
            else:
                ok = False
            if not ok:
                fail(f"{pr['id']} fact {f}: payment data = {sorted((v[0], round(v[2], 2)) for v in bd.values())[:12]}")

    troy_progs = sorted({x["pid"] for x in lines if x["d"] == TROY and abs(x["v"]) > 0.004})
    if troy_progs != sorted(J["troy_programs"]):
        fail(f"Troy was paid under {troy_progs}, page text says {J['troy_programs']}")
    if problems:
        sys.exit("FAILED:\n" + "\n".join(problems))

    # ---------- 3. aggregates ----------
    pay = {}   # pid -> pyr -> dict
    for x in lines:
        p = pay.setdefault(x["pid"], {}).setdefault(x["pyr"], {"net": 0.0, "rec": set(), "troy": 0.0, "oak": 0.0, "rfy": set()})
        p["net"] += x["v"]
        p["rfy"].add(x["rfy"])
        cc = next((pr.get("count_codes") for pr in progs if pr["id"] == x["pid"]), None)
        if x["v"] > 0 and (not cc or x["code"] in cc):
            p["rec"].add(x["d"])
        if x["d"] == TROY:
            p["troy"] += x["v"]
        if x["d"] == OAKSCH:
            p["oak"] += x["v"]
    totals = {fy: {c: 0.0 for c, _ in CHART} for fy in range(FIRST_FY, LAST_FY + 1)}
    within = {}
    for pr in progs:
        for y in pr["years"]:
            if y.get("within"):
                within[(y["within"], y["fy"])] = within.get((y["within"], y["fy"]), 0) + y["amt"]
    for pr in progs:
        cat = {"coaches": "coaches", "time": "time", "35j": "big", "35m": "big"}.get(pr["chart"], "other")
        for y in pr["years"]:
            v = y["amt"] - within.get((pr["id"], y["fy"]), 0)
            totals[y["fy"]][cat] += v
    grand = sum(sum(t.values()) for t in totals.values())
    troy_total = sum(x["v"] for x in lines if x["d"] == TROY)
    troy_by_year = {}
    for x in lines:
        if x["d"] == TROY:
            troy_by_year[x["rfy"]] = troy_by_year.get(x["rfy"], 0) + x["v"]
    funded = [pr for pr in progs if any(y["amt"] or y.get("orig") for y in pr["years"])]
    sizes = [y["amt"] for pr in funded for y in pr["years"] if y["amt"] and not y.get("within")]

    # ---------- 4. HTML ----------
    def src_links(pr):
        seen_docs = {}
        for y in pr["years"]:
            for dk, pg in cites[(pr["id"], y["fy"])]:
                seen_docs.setdefault(dk, set()).add(pg)
        out = []
        for dk, pgs in seen_docs.items():
            d = docs[dk]
            pp = sorted(pgs)
            pstr = ("p. " + str(pp[0])) if len(pp) == 1 else ("pp. " + ", ".join(str(p) for p in pp))
            if d["first"] == 1 and len(fitz.open(ROOT / d["file"])) == 1 or not d["file"].endswith(".pdf"):
                pstr = ""
            out.append(f'<a href="{html.escape(d["url"])}">{html.escape(d["label"])}</a>{(" " + pstr) if pstr else ""}')
        return "; ".join(out)

    def years_span(pr):
        fys = [y["fy"] for y in pr["years"] if y["amt"] or y.get("orig")]
        if not fys:
            return "2026&ndash;27"
        a, b = min(fys), max(fys)
        return fy_label(a) if a == b else f"{fy_label(a)} to {fy_label(b)}"

    def status_txt(y):
        s = y.get("status")
        return {"cut": "cut", "vetoed": "vetoed", "restored": "", "raised": ""}.get(s, "")

    # timeline grid
    grid = io.StringIO()
    grid.write('<div class="tl" role="table" aria-label="Section 35 grants by year">\n')
    grid.write('<div class="tl-row tl-head" role="row"><div class="tl-name" role="columnheader">Grant</div>')
    for fy in range(FIRST_FY, LAST_FY + 1):
        grid.write(f'<div class="tl-c" role="columnheader"><span class="yl">{fy_label(fy)}</span><span class="ys">&rsquo;{str(fy)[2:]}</span></div>')
    grid.write('</div>\n')
    for g in J["groups"]:
        members = [pr for pr in progs if pr["group"] == g["id"] and pr["years"]]
        if not members:
            continue
        grid.write(f'<div class="tl-group" role="row"><div role="cell">{html.escape(g["title"])}</div></div>\n')
        for pr in members:
            ys = {y["fy"]: y for y in pr["years"]}
            grid.write(f'<div class="tl-row" role="row"><div class="tl-name" role="rowheader"><a href="#{pr["id"]}">{prose(pr["name"])}</a><span class="tl-sec">Sec. {html.escape(", ".join(pr["letters"]))}</span></div>')
            for fy in range(FIRST_FY, LAST_FY + 1):
                y = ys.get(fy)
                if not y:
                    grid.write('<div class="tl-c" role="cell"><span class="sr">none</span></div>')
                    continue
                st = status_txt(y)
                if y["amt"] == 0:
                    lab = f'{fy_label(fy)}: {usd(y["orig"])} {st}'
                    grid.write(f'<div class="tl-c" role="cell"><span class="cell off" tabindex="0" data-t="{html.escape(pr["name"])}" data-v="{html.escape(lab)}"><span class="cv">{st}</span></span></div>')
                else:
                    lab = f'{fy_label(fy)}: {usd(y["amt"])}' + (" (inside 35m)" if y.get("within") else "")
                    cls = "cell in" if y.get("within") else "cell"
                    grid.write(f'<div class="tl-c" role="cell"><span class="{cls}" tabindex="0" data-t="{html.escape(pr["name"])}" data-v="{html.escape(lab)}"><span class="cv">{usd_compact(y["amt"])}</span></span></div>')
            grid.write('</div>\n')
    grid.write('<div class="tl-row tl-total" role="row"><div class="tl-name" role="rowheader">All Section 35</div>')
    for fy in range(FIRST_FY, LAST_FY + 1):
        grid.write(f'<div class="tl-c" role="cell"><span class="cv">{usd_compact(sum(totals[fy].values()))}</span></div>')
    grid.write('</div>\n</div>')

    # index of letters
    letters = {}
    for pr in progs:
        for L in pr["letters"]:
            letters.setdefault(L, []).append(pr)
    def lkey(L):
        return (len(L) > 2, L)
    idx = io.StringIO()
    for L in sorted(letters, key=lkey):
        items = ", ".join(f'<a href="#{p["id"]}">{prose(p["name"])}</a>' for p in letters[L])
        idx.write(f'<li><span class="lt">{"Sec. " + L}</span> {items}</li>\n')

    # cards
    cards = io.StringIO()
    for g in J["groups"]:
        members = [pr for pr in progs if pr["group"] == g["id"]]
        cards.write(f'<h2 class="grp" id="g-{g["id"]}">{html.escape(g["title"])}</h2>\n')
        if g["intro"]:
            cards.write(f'<p class="prose gi">{prose(g["intro"])}</p>\n')
        for pr in members:
            tot = sum(y["amt"] for y in pr["years"])
            cards.write(f'<article class="grant" id="{pr["id"]}">\n')
            cards.write(f'<div class="gh"><span class="sec">{prose(pr["cites"])}</span><span class="span">{years_span(pr)}</span></div>\n')
            cards.write(f'<h3>{prose(pr["name"])}</h3>\n')
            cards.write(f'<p class="sum">{prose(pr["summary"])}</p>\n')
            for para in pr["detail"]:
                cards.write(f'<p>{prose(para)}</p>\n')
            if pr["years"]:
                pp = pay.get(pr["id"], {})
                fys = sorted(set(y["fy"] for y in pr["years"]) | set(pp))
                has_pay = bool(pp)
                has_troy = any(abs(v["troy"]) > 0.004 for v in pp.values())
                has_oak = any(abs(v["oak"]) > 0.004 for v in pp.values())
                head = ["Year", "In the budget"]
                if has_pay:
                    head += ["Paid through state aid", "Recipients"]
                if has_troy:
                    head.append("Troy")
                if has_oak:
                    head.append("Oakland Schools")
                cards.write('<div class="tw"><table class="gt"><thead><tr>' + "".join(f'<th{" class=l" if i == 0 else ""}>{h}</th>' for i, h in enumerate(head)) + '</tr></thead><tbody>\n')
                ys = {y["fy"]: y for y in pr["years"]}
                for fy in fys:
                    y = ys.get(fy)
                    if y is None:
                        bud = '<span class="muted">second half of the 2023&ndash;24 grant</span>' if pr["id"] == "35j" else "&mdash;"
                    elif y["amt"] == 0:
                        bud = f'<span class="muted">{usd(y["orig"])}, {status_txt(y)}</span>'
                    else:
                        bud = usd(y["amt"]) + (f' <span class="muted">(first passed: {usd(y["orig"])})</span>' if y.get("orig") else "")
                    row = [fy_label(fy), bud]
                    p = pp.get(fy)
                    if has_pay:
                        row.append(usd(p["net"]) if p else "&mdash;")
                        n = len(p["rec"]) if p else 0
                        isds = p and all(d.endswith("000") for d in p["rec"])
                        noun = ("ISD" if n == 1 else "ISDs") if isds else ("district" if n == 1 else "districts and ISDs")
                        row.append(f"{n} {noun}" if n else "&mdash;")
                    if has_troy:
                        row.append(usd(p["troy"]) if p and abs(p["troy"]) > 0.004 else ("$0" if p else "&mdash;"))
                    if has_oak:
                        row.append(usd(p["oak"]) if p and abs(p["oak"]) > 0.004 else ("$0" if p else "&mdash;"))
                    cards.write("<tr>" + "".join(f'<td data-label="{html.escape(re.sub("<[^>]+>", "", head[i]))}"><span>{c}</span></td>' for i, c in enumerate(row)) + "</tr>\n")
                cards.write('</tbody></table></div>\n')
                nn = {}
                for y in pr["years"]:
                    if y.get("note"):
                        nn.setdefault(y["fy"], []).append(prose(y["note"]))
                for k, v in pr.get("paynotes", {}).items():
                    nn.setdefault(int(k), []).append(prose(v))
                notes = [f'<strong>{fy_label(k)}:</strong> {" ".join(v)}' for k, v in sorted(nn.items())]
                if notes:
                    cards.write('<p class="gn">' + " ".join(notes) + '</p>\n')
                if has_pay:
                    cards.write('<p class="gn">Paid: net of later adjustments, from MDE&rsquo;s State Aid Financial Status Reports.</p>\n')
            if pr["troy"]:
                cards.write(f'<p class="troy"><strong>Troy:</strong> {prose(pr["troy"])}</p>\n')
            if pr["years"]:
                cards.write(f'<p class="gs">Budget source: {src_links(pr)}</p>\n')
            cards.write('</article>\n')

    # KPI numbers
    kpi = {"grand": grand, "n": len(funded), "min": min(sizes), "max": max(sizes), "troy": troy_total}
    data = {"cats": [{"k": c, "n": n} for c, n in CHART],
            "years": [{"fy": fy, "l": fy_label(fy), **{c: round(v, 2) for c, v in totals[fy].items()}} for fy in range(FIRST_FY, LAST_FY + 1)],
            "troy": {str(k): round(v, 2) for k, v in sorted(troy_by_year.items())}}

    # ---------- 5. CSVs ----------
    if "--check" in sys.argv:
        pass
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["grant_id", "grant", "sections", "state_fy", "school_year", "amount", "first_passed_amount", "status", "note", "source", "source_page"])
    for pr in progs:
        for y in pr["years"]:
            c = cites[(pr["id"], y["fy"])][0]
            w.writerow([pr["id"], pr["name"], pr["cites"], y["fy"], fy_label(y["fy"]).replace("–", "-"), f'{y["amt"]:.2f}',
                        f'{y["orig"]:.2f}' if y.get("orig") is not None else "", y.get("status", ""),
                        (y.get("note", "") + (" Counted inside Section 35m." if y.get("within") else "")).strip(), docs[c[0]]["label"], c[1]])
    OUT_GRANTS.write_text(buf.getvalue(), encoding="utf-8")
    buf2 = io.StringIO()
    w = csv.writer(buf2, lineterminator="\n")
    w.writerow(["grant_id", "grant", "program_year", "school_year", "report_years", "paid_net", "recipients", "troy", "oakland_schools"])
    for pr in progs:
        for fy, p in sorted(pay.get(pr["id"], {}).items()):
            w.writerow([pr["id"], pr["name"], fy, fy_label(fy).replace("–", "-"), " ".join(f"FY{r}" for r in sorted(p["rfy"])),
                        f'{p["net"]:.2f}', len(p["rec"]), f'{p["troy"]:.2f}', f'{p["oak"]:.2f}'])
    OUT_PAY.write_text(buf2.getvalue(), encoding="utf-8")

    if "--check" in sys.argv:
        print("check only; nothing written to the page")
        print(f"total budgeted ${grand:,.0f}; Troy ${troy_total:,.2f}"); return
    # ---------- 6. write the page ----------
    page = PAGE.read_text(encoding="utf-8")
    def put(name, content):
        nonlocal page
        pat = re.compile(rf"(<!--GEN:{name}:BEGIN-->).*?(<!--GEN:{name}:END-->)", re.S)
        page, n = pat.subn(lambda m: m.group(1) + "\n" + content + "\n" + m.group(2), page)
        if n != 1:
            sys.exit(f"marker GEN:{name} not found exactly once in history.html")
    put("grid", grid.getvalue())
    put("index", idx.getvalue())
    put("cards", cards.getvalue())
    put("kpi-grand", f'${kpi["grand"]/1e9:.2f} billion' if kpi["grand"] >= 1e9 else f'${kpi["grand"]/1e6:,.0f} million')
    put("kpi-n", str(kpi["n"]))
    put("kpi-n2", str(kpi["n"]))
    put("kpi-range", f'{usd_compact(kpi["min"]).replace("K", ",000").replace("$250,000", "$250,000")} to {usd_compact(kpi["max"]).replace("M", " million")}')
    put("kpi-troy", f'${kpi["troy"]/1e6:.2f} million')
    block = "/*DATA:BEGIN*/var D=" + json.dumps(data, separators=(",", ":")) + ";/*DATA:END*/"
    page, n = re.subn(r"/\*DATA:BEGIN\*/.*?/\*DATA:END\*/", lambda m: block, page, flags=re.S)
    if n != 1:
        sys.exit("DATA markers not found exactly once in history.html")
    for out in (OUT_GRANTS, OUT_PAY):
        h = hashlib.sha256(out.read_bytes()).hexdigest()[:10]
        page, n = re.subn(rf'assets/{out.name}(\?v=[0-9a-f]+)?"', f'assets/{out.name}?v={h}"', page)
        if n < 1:
            sys.exit(f"no link to assets/{out.name} in history.html")
    PAGE.write_bytes(page.encode("utf-8"))

    print(f"{len(progs)} entries, {kpi['n']} grants with money; {sum(len(pr['years']) for pr in progs)} grant-years, all quotes found")
    print(f"{len(lines)} payment lines mapped; facts checked: {sum(len(pr.get('facts', [])) for pr in progs)}")
    print("by year: " + ", ".join(f"FY{fy} ${sum(t.values())/1e6:,.2f}M" for fy, t in totals.items()))
    print(f"total budgeted FY{FIRST_FY}-FY{LAST_FY}: ${grand:,.0f}; Troy received ${troy_total:,.2f}: " +
          ", ".join(f"FY{k} ${v:,.2f}" for k, v in sorted(troy_by_year.items())))


if __name__ == "__main__":
    main()
