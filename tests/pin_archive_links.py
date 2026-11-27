"""Check the Web Archive links of the site and, if you want, fix their dates.

A link like https://web.archive.org/web/<URL> (with no date) goes to the
newest copy of <URL> in the Web Archive. The newest copy can be an error
page (for example when the old server stopped). This script asks the Web
Archive for the newest copy with status 200 (a good copy) of each link.

It needs network access, so it is not part of the tests.

Usage:

    python3 tests/pin_archive_links.py          # only report
    python3 tests/pin_archive_links.py --write  # also change the files

With --write, each link with no date changes to a link with the date of the
newest good copy, for example
https://web.archive.org/web/20220627024356/https://di002.edv.uniovi.es/~labra/...
The script prints the links that have no good copy. Change or remove these
links by hand.
"""

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = sorted(list((ROOT / "content").rglob("*.md")) + list((ROOT / "static").rglob("*.html")))

# A Web Archive link with no date: https://web.archive.org/web/http...
LINK = re.compile(rb'https://web\.archive\.org/web/(https?://[^\s"\'()<>\]]+)')


def other_forms(url):
    """Forms of the same address on the old university servers."""
    forms = [url]
    match = re.match(r"https?://(?:www\.)?di(?:002\.edv)?\.uniovi\.es(/~labra.*)", url)
    if match:
        path = match.group(1)
        for host in ("di002.edv.uniovi.es", "www.di.uniovi.es"):
            for scheme in ("https", "http"):
                form = f"{scheme}://{host}{path}"
                if form not in forms:
                    forms.append(form)
    return forms


def newest_good_copy(url):
    """Return (timestamp, archived URL) of the newest copy with status 200, or None."""
    for form in other_forms(url):
        query = urllib.parse.urlencode({
            "url": form, "output": "json", "filter": "statuscode:200", "limit": "-1",
        })
        request = urllib.request.Request(
            "https://web.archive.org/cdx/search/cdx?" + query,
            headers={"User-Agent": "Mozilla/5.0 (compatible; archive-link-check)"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    rows = json.loads(response.read() or b"[]")
                break
            except Exception as e:  # noqa: BLE001
                if attempt == 2:
                    print(f"  could not ask the Web Archive about {form}: {e}")
                    rows = []
                time.sleep(5)
        if len(rows) > 1:
            header, row = rows[0], rows[-1]
            item = dict(zip(header, row))
            return item["timestamp"], item["original"]
        time.sleep(1)  # Be polite to the Web Archive.
    return None


def main():
    write = "--write" in sys.argv
    links = {}
    for file in FILES:
        for match in LINK.finditer(file.read_bytes()):
            links.setdefault(match.group(1).decode(), []).append(file)

    print(f"{len(links)} Web Archive links with no date.")
    missing = []
    found = {}
    for url, files in sorted(links.items()):
        address, hash_mark, fragment = url.partition("#")
        copy = newest_good_copy(address)
        if copy:
            found[url] = f"https://web.archive.org/web/{copy[0]}/{copy[1]}{hash_mark}{fragment}"
            print(f"OK       {url} -> {copy[0]}")
        else:
            missing.append(url)
            print(f"NO COPY  {url} (in {', '.join(str(f.relative_to(ROOT)) for f in files)})")

    if write and found:
        for file in FILES:
            data = file.read_bytes()
            new = LINK.sub(lambda m: found.get(m.group(1).decode(), m.group(0).decode()).encode(), data)
            if new != data:
                file.write_bytes(new)
                print(f"Changed {file.relative_to(ROOT)}")

    print(f"{len(found)} links have a good copy. {len(missing)} links have no good copy.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
