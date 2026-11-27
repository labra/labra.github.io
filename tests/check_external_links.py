"""Check the external links of the generated site.

This script needs network access, so it is not part of the tests. It reads
the HTML files in the public folder, finds the links to other sites and
checks each link. It prints the links that do not work and the first page
that has each link.

Usage:

    hugo -DEF
    python3 tests/check_external_links.py

Some sites refuse requests from scripts (for example with status 403 or 999).
Check these links in a browser before you change them.
"""

import html
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_site as site  # noqa: E402

# Links that the theme makes on each page. They are not content links.
SKIP = (
    "facebook.com/sharer", "twitter.com/intent", "linkedin.com/shareArticle",
    "service.weibo.com", "cdnjs.cloudflare.com", "fonts.googleapis.com",
    "google-analytics.com", "gohugo.io", "github.com/gcushen",
)


def external_links():
    links = {}
    for file in sorted(site.SITE.rglob("*.html")):
        text = file.read_text(encoding="utf-8", errors="replace")
        if 'http-equiv="refresh"' in text[:500]:
            continue
        page = site.Page(text)
        for href in [h for h, _, _ in page.links] + page.srcs:
            href = html.unescape(href.strip())
            if href.startswith("//"):
                href = "https:" + href
            if not href.startswith(("http://", "https://")) or site.local_path(href) is not None:
                continue
            if any(s in href for s in SKIP):
                continue
            links.setdefault(href, str(file.relative_to(site.SITE)))
    return links


def check(url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; link-check)"}
    for method in ("HEAD", "GET"):
        try:
            request = urllib.request.Request(url, method=method, headers=headers)
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.status, ""
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue  # Some sites do not accept HEAD. Try GET.
            return e.code, e.reason
        except Exception as e:  # noqa: BLE001
            if method == "HEAD":
                continue
            return None, str(e)
    return None, "no answer"


def main():
    links = external_links()
    print(f"Checking {len(links)} external links...")
    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(lambda u: (u, *check(u)), links))
    broken = [(u, s, r) for u, s, r in results if s is None or s >= 400]
    for url, status, reason in sorted(broken):
        print(f"{status or 'ERROR'}\t{url}\t({reason})\tin {links[url]}")
    print(f"{len(broken)} of {len(links)} links do not work.")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
