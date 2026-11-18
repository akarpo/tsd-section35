"""Check the page before and after a push. Screenshots go to qa-out/ (git-ignored).

    python -I tools/qa.py                     # local public/index.html: structure + 1280/390 px, light/dark
    python -I tools/qa.py --live              # the live site (also checks the 404 page, share image, analytics)
    python -I tools/qa.py --links             # also request every external link on the page
    python -I tools/qa.py --card OUT.png      # render tools/share-card.html at 1200x630 to OUT.png

Needs Playwright (pip install playwright); it uses the bundled Chromium or falls back to installed
Chrome. Look at the screenshots too: the script finds overflow, console errors, broken in-page
anchors and heading-level skips, not label collisions or bad wording.
"""
import argparse, html, pathlib, re, sys, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser

SITE = "https://tsd-section35.karpowitsch.org/"
SECTIONS = ["findings", "oakland", "troy", "og"]          # also screenshotted on their own
ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "public" / "index.html"
OUT = ROOT / "qa-out"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
# Hosts that refuse scripted requests; listed as "check in a browser", not failed.
SKIP_HOSTS = {"www.sec.gov": "SEC blocks scripted requests that lack a contact User-Agent"}
VIEWS = [("desk-light", 1280, "light"), ("desk-dark", 1280, "dark"), ("phone-light", 390, "light"), ("phone-dark", 390, "dark")]


class Struct(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.heads, self.imgs, self.cur, self.txt = [], [], [], [], None, ""

    def handle_starttag(self, t, a):
        a = dict(a)
        if "id" in a: self.ids.append(a["id"])
        if t == "a" and "href" in a: self.hrefs.append(a["href"])
        if t in ("h1", "h2", "h3", "h4", "h5"): self.cur, self.txt = t, ""
        if t == "img": self.imgs.append(a)

    def handle_endtag(self, t):
        if t == self.cur:
            self.heads.append((t, re.sub(r"\s+", " ", self.txt).strip()[:70])); self.cur = None

    def handle_data(self, d):
        if self.cur: self.txt += d


def structure(src, problems):
    p = Struct(); p.feed(src)
    if 'lang="en"' not in src[:300]: problems.append("no lang attribute on <html>")
    dup = sorted({i for i in p.ids if p.ids.count(i) > 1})
    if dup: problems.append(f"duplicate ids: {dup}")
    broken = [h for h in p.hrefs if h.startswith("#") and len(h) > 1 and h[1:] not in p.ids]
    if broken: problems.append(f"broken in-page anchors: {broken}")
    noalt = [i.get("src") for i in p.imgs if not i.get("alt")]
    if noalt: problems.append(f"images without alt: {noalt}")
    lvl = 0
    for t, x in p.heads:
        n = int(t[1])
        if lvl and n > lvl + 1: problems.append(f"heading level skip to {t}: {x}")
        lvl = n
    print(f"structure: {len(p.heads)} headings, {len(p.ids)} ids, {len(p.hrefs)} links")
    return sorted({html.unescape(h) for h in p.hrefs if h.startswith("http")})


def fetch(url, method="GET"):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.headers.get("content-type", "")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, type(e).__name__


def render(url, live, problems):
    from playwright.sync_api import sync_playwright
    OUT.mkdir(exist_ok=True)
    tag = "live-" if live else ""
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:
            b = p.chromium.launch(channel="chrome")
        for name, w, scheme in VIEWS:
            pg = b.new_page(viewport={"width": w, "height": 900}, color_scheme=scheme)
            pg.on("console", lambda m, n=name: problems.append(f"{n} console {m.type}: {m.text}") if m.type in ("error", "warning") else None)
            pg.on("pageerror", lambda e, n=name: problems.append(f"{n} page error: {e}"))
            pg.goto(url, wait_until="networkidle" if live else "load"); pg.wait_for_timeout(800)
            pg.add_style_tag(content="header.top{position:static !important}")
            sw, cw = pg.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
            if sw > cw: problems.append(f"{name}: horizontal overflow {sw}>{cw}")
            if live and name == "desk-light" and not pg.evaluate("!!document.querySelector('script[src*=cloudflareinsights]')"):
                problems.append("live: Cloudflare Web Analytics beacon missing (check the CSP in public/_headers)")
            pg.screenshot(path=str(OUT / f"{tag}{name}.png"), full_page=True)
            for sec in SECTIONS:
                if pg.locator(f"#{sec}").count():
                    pg.locator(f"#{sec}").screenshot(path=str(OUT / f"{tag}{name}-{sec}.png"))
                else:
                    problems.append(f"section #{sec} not found")
            pg.close()
        b.close()


def card(out):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:
            b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        pg.goto((ROOT / "tools" / "share-card.html").as_uri()); pg.wait_for_timeout(500)
        pg.screenshot(path=str(out)); b.close()
    print("share card written:", out, "- give a changed card a NEW file name and update og:image/twitter:image")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--links", action="store_true")
    ap.add_argument("--card", metavar="OUT.png")
    a = ap.parse_args()
    if a.card:
        return card(pathlib.Path(a.card).resolve())
    problems = []
    links = structure(PAGE.read_text(encoding="utf-8"), problems)
    if a.live:
        s, ct = fetch(SITE); print("live page:", s)
        if s != 200: problems.append(f"live page returned {s}")
        s, _ = fetch(SITE + "qa-check-missing-page"); print("404 page:", s)
        if s != 404: problems.append(f"unknown path returned {s}, expected 404")
        for m in re.finditer(r'property="og:image" content="([^"]+)"', PAGE.read_text(encoding="utf-8")):
            s, ct = fetch(m.group(1)); print("share image:", s, ct)
            if s != 200: problems.append(f"share image {m.group(1)} returned {s}")
    render(SITE if a.live else PAGE.as_uri(), a.live, problems)
    if a.links:
        for u in links:
            host = urllib.parse.urlsplit(u).hostname or ""
            if host in SKIP_HOSTS:
                print(f"link not checked ({SKIP_HOSTS[host]}); check in a browser: {u}")
                continue
            s, _ = fetch(u)
            if s >= 400 or s == 0:
                s2, _ = fetch(u, "HEAD")
                if s2 >= 400 or s2 == 0:
                    problems.append(f"link {s}: {u}")
        print(f"links checked: {len(links)}")
    print(f"screenshots: {OUT}")
    print("\n".join(f"PROBLEM {x}" for x in problems) or "no problems found")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
