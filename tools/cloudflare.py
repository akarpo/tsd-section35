"""Cloudflare Pages + DNS for this site. Never prints credentials.

    python -I tools/cloudflare.py status    # last 3 deployments + custom-domain status (use after a push)
    python -I tools/cloudflare.py check     # token, zone, project and DNS record
    python -I tools/cloudflare.py deploy    # re-run the production build from main (rarely needed)
    python -I tools/cloudflare.py create    # one-time: create the Git-connected Pages project
    python -I tools/cloudflare.py domain    # one-time: attach the custom domain + proxied CNAME

Credentials live OUTSIDE the repo. Set CF_CRED_FILE to the owner's credentials text file, which has
labeled lines "Cloudflare Pages/DNS token: ...", "Cloudflare account: ..." and
"karpowitsch.org zone: ...". Never commit that file or print its values.

A push to main deploys by itself. Never run `wrangler pages deploy`: it creates a Direct Upload
deployment that shadows the Git one.
"""
import json, os, sys, uuid, urllib.request, urllib.error

PROJECT, OWNER, REPO, HOST = "tsd-section35", "akarpo", "tsd-section35", "tsd-section35.karpowitsch.org"
API = "https://api.cloudflare.com/client/v4"


def creds():
    path = os.environ.get("CF_CRED_FILE")
    if not path or not os.path.isfile(path):
        raise SystemExit("Set CF_CRED_FILE to the Cloudflare credentials file (kept outside the repo).")
    want = {"Cloudflare Pages/DNS token": "token", "Cloudflare account": "acct", "karpowitsch.org zone": "zone"}
    got = {}
    for line in open(path, encoding="utf-8-sig"):
        k, sep, v = line.partition(":")
        if sep and k.strip() in want:
            got[want[k.strip()]] = v.strip()
    missing = [n for n in ("token", "acct", "zone") if not got.get(n)]
    if missing:
        raise SystemExit(f"missing in credential file: {missing}")
    return got


C = creds()
A = f"/accounts/{C['acct']}"
P = f"{A}/pages/projects/{PROJECT}"


def call(method, path, body=None, multipart=None):
    headers = {"Authorization": f"Bearer {C['token']}", "User-Agent": "pages-setup/1.0"}
    data = None
    if multipart is not None:
        b = uuid.uuid4().hex
        parts = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n' for k, v in multipart.items()]
        data = ("".join(parts) + f"--{b}--\r\n").encode()
        headers["Content-Type"] = f"multipart/form-data; boundary={b}"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}


def errs(j):
    return [f"{e.get('code')}: {e.get('message')}" for e in (j.get("errors") or [])]


def check():
    s, j = call("GET", "/user/tokens/verify")
    print("token verify:", s, (j.get("result") or {}).get("status"), errs(j))
    s, j = call("GET", f"/zones/{C['zone']}")
    print("zone:", s, (j.get("result") or {}).get("name"), errs(j))
    s, j = call("GET", P)
    print(f"project {PROJECT}:", s, "exists" if s == 200 else errs(j))
    s, j = call("GET", f"/zones/{C['zone']}/dns_records?name={HOST}")
    print(f"dns records for {HOST}:", s, [(r["type"], r["content"], r["proxied"]) for r in (j.get("result") or [])], errs(j))


def create():
    body = {
        "name": PROJECT,
        "production_branch": "main",
        "build_config": {"build_command": "", "destination_dir": "public", "root_dir": ""},
        "source": {"type": "github", "config": {
            "owner": OWNER, "repo_name": REPO, "production_branch": "main",
            "deployments_enabled": True, "production_deployments_enabled": True,
            "preview_deployment_setting": "none", "pr_comments_enabled": False}},
    }
    s, j = call("POST", f"{A}/pages/projects", body)
    r = j.get("result") or {}
    print("create:", s, r.get("name"), r.get("subdomain"), errs(j))


def deploy():
    s, j = call("POST", f"{P}/deployments", multipart={"branch": "main"})
    r = j.get("result") or {}
    print("deploy:", s, r.get("id"), r.get("url"), (r.get("latest_stage") or {}).get("name"), errs(j))


def domain():
    s, j = call("GET", P)
    sub = (j.get("result") or {}).get("subdomain")
    if not sub:
        raise SystemExit(f"no project subdomain: {s} {errs(j)}")
    s, j = call("POST", f"{P}/domains", {"name": HOST})
    print("pages domain:", s, (j.get("result") or {}).get("status"), errs(j))
    s, j = call("GET", f"/zones/{C['zone']}/dns_records?name={HOST}")
    existing = j.get("result") or []
    if existing:
        print("dns already has:", [(r["type"], r["content"], r["proxied"]) for r in existing], "- not touching it")
        return
    s, j = call("POST", f"/zones/{C['zone']}/dns_records",
                {"type": "CNAME", "name": HOST, "content": sub, "proxied": True, "ttl": 1,
                 "comment": f"Cloudflare Pages project {PROJECT} (repo {OWNER}/{REPO})"})
    r = j.get("result") or {}
    print("dns create:", s, r.get("type"), r.get("name"), "->", r.get("content"), "proxied" if r.get("proxied") else "", errs(j))


def status():
    s, j = call("GET", f"{P}/deployments?per_page=3")
    for d in (j.get("result") or []):
        st = d.get("latest_stage") or {}
        commit = ((d.get("deployment_trigger") or {}).get("metadata") or {}).get("commit_hash", "")[:7]
        print("deployment:", d.get("id", "")[:8], d.get("environment"), commit, st.get("name"), st.get("status"), d.get("url"))
    s, j = call("GET", f"{P}/domains")
    for d in (j.get("result") or []):
        print("domain:", d.get("name"), d.get("status"))


CMDS = {"check": check, "create": create, "deploy": deploy, "domain": domain, "status": status}
if len(sys.argv) != 2 or sys.argv[1] not in CMDS:
    raise SystemExit(__doc__)
CMDS[sys.argv[1]]()
