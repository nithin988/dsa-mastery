"""Check that every external link in the Systems modules (sources and real-life cases) still loads.

404 and connection failures fail the check; 403 and 429 (sites that block scripts) are reported as warnings.
"""
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "build"))
sys.path.insert(0, HERE)
from sys_record import live_modules  # noqa: E402


def check(url, tries=2):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # network trouble: retry once
        if tries > 1:
            return check(url, tries - 1)
        if shutil.which("curl"):  # Python's TLS stack sometimes fails where curl works
            r = subprocess.run(["curl", "-sL", "-m", "25", "-A", "Mozilla/5.0", "-o", os.devnull, "-w", "%{http_code}", url], capture_output=True, text=True)
            if r.stdout.strip().isdigit() and r.stdout.strip() != "000":
                return int(r.stdout.strip())
        return "ERR " + type(e).__name__


def main():
    urls = {}
    for m in live_modules():
        for s in m.get("sources", []):
            urls.setdefault(s["url"], m["id"])
        for c in m.get("cases", []):
            if c.get("url"):
                urls.setdefault(c["url"], m["id"])
    bad = 0
    for url, mid in sorted(urls.items()):
        st = check(url)
        ok = st == 200
        warn = st in (403, 429, 401)
        print(f"{'OK  ' if ok else ('WARN' if warn else 'FAIL')} {st} [{mid}] {url}")
        if not ok and not warn:
            bad += 1
    print(f"links: {len(urls) - bad}/{len(urls)} fine")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
