"""Tests for the generated site in the public folder.

The tests check the structure and the features of the site. They do not check
fixed numbers of publications, talks or posts. They read the content folder
and the config file to know what the site must contain, so you can add new
content without changes to the tests.

Usage:

    hugo -DEF                      # build the site into public/
    python3 -m unittest discover -s tests -v

Set SITE_DIR to test a different output folder:

    SITE_DIR=/tmp/site python3 -m unittest discover -s tests -v

The tests use only the Python standard library (Python 3.11 or later).
"""

import html
import os
import re
import tomllib
import unittest
import xml.etree.ElementTree as ET
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
SITE = Path(os.environ.get("SITE_DIR", ROOT / "public")).resolve()

CONFIG = tomllib.loads((ROOT / "config.toml").read_text(encoding="utf-8"))
BASE_URL = CONFIG["baseurl"].rstrip("/") + "/"
BASE_PATH = urlparse(BASE_URL).path  # "/" for this site


# ---------------------------------------------------------------------------
# Content helpers
# ---------------------------------------------------------------------------

FRONT_MATTER = re.compile(r"\A﻿?\s*\+\+\+\s*\n(.*?)\n\+\+\+", re.S)


class Content:
    """One Markdown file in the content folder."""

    def __init__(self, path):
        self.path = path
        text = path.read_text(encoding="utf-8")
        match = FRONT_MATTER.match(text)
        self.params = tomllib.loads(match.group(1)) if match else {}
        self.body = text[match.end():].strip() if match else text.strip()
        self.section = path.relative_to(CONTENT).parts[0]

    @property
    def title(self):
        return self.params.get("title", "")

    @property
    def date(self):
        value = self.params.get("date")
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str) and value:
            return date.fromisoformat(value[:10])
        return None

    @property
    def tags(self):
        return list(self.params.get("tags", []))

    @property
    def url_path(self):
        """The site path of the page, for example "/publication/2011_adonis/"."""
        if "url" in self.params:
            return "/" + self.params["url"].strip("/") + "/"
        slug = self.params.get("slug", self.path.stem)
        return f"/{self.section}/{slug.lower().replace(' ', '-')}/"


def pages_of(section):
    """All regular pages of a section (no _index.md files)."""
    folder = CONTENT / section
    return [Content(p) for p in sorted(folder.glob("*.md")) if p.name != "_index.md"]


def all_pages():
    return [Content(p) for p in sorted(CONTENT.glob("**/*.md")) if p.name != "_index.md"]


def norm_text(text):
    """Normalise text for comparison: decode entities, fold spaces and case."""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    # Smart punctuation (smartypants) changes quotes and dashes.
    text = text.translate(str.maketrans("\u2018\u2019\u201c\u201d\u2013\u2014\u00a0", "''\"\"-- "))
    return re.sub(r"\s+", " ", text).strip().lower()


def norm_term(text):
    """Normalise a taxonomy term. Hugo treats "Big data" and "Big-data" as one term."""
    return re.sub(r"[\s_-]+", "-", norm_text(text))


def plain_title(text):
    """A title as it shows in HTML (Markdown emphasis removed)."""
    return norm_text(re.sub(r"[*_`]", "", text))


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------


class Page(HTMLParser):
    """Collects the parts of an HTML page that the tests use."""

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.h1 = []
        self.links = []  # (href, text, section id)
        self.srcs = []
        self.sections = []
        self.elements = []  # (tag, attrs dict, section id)
        self._stack = []
        self._section = None
        self._capture = None
        self._text = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = {k: (v or "") for k, v in attrs}
        if tag == "section" and "id" in attrs:
            self._section = attrs["id"]
            self.sections.append(attrs["id"])
        self.elements.append((tag, attrs, self._section))
        if tag in ("img", "script", "iframe") and attrs.get("src"):
            self.srcs.append(attrs["src"])
        if tag == "link" and attrs.get("href"):
            self.srcs.append(attrs["href"])
        if tag in ("title", "h1", "a"):
            self._stack.append((tag, attrs, len(self._text)))

    def handle_endtag(self, tag):
        if tag == "section":
            self._section = None
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                _, attrs, start = self._stack.pop(i)
                text = " ".join("".join(self._text[start:]).split())
                if tag == "title" and not self.title:
                    self.title = text
                elif tag == "h1":
                    self.h1.append(text)
                elif tag == "a":
                    self.links.append((attrs.get("href", ""), text, self._section))
                break

    def handle_data(self, data):
        self._text.append(data)

    def links_in(self, section):
        return [(href, text) for href, text, sec in self.links if sec == section]

    def elements_in(self, section, tag=None):
        return [(t, a) for t, a, sec in self.elements if sec == section and (tag is None or t == tag)]


_cache = {}


def site_file(path):
    """Map a site path ("/talk/x/") to a file in the output folder."""
    path = unquote(path.split("#")[0].split("?")[0])
    if path.startswith(BASE_PATH):
        path = path[len(BASE_PATH):]
    target = SITE / path.lstrip("/")
    if path == "" or path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def page(path):
    file = site_file(path)
    if file not in _cache:
        _cache[file] = Page(file.read_text(encoding="utf-8"))
    return _cache[file]


def local_path(href):
    """The site path of an internal link, or None for an external link."""
    if not href or href.startswith(("#", "mailto:", "javascript:", "tel:", "data:")):
        return None
    if href.startswith("//"):
        return None
    if href.startswith(("http://", "https://")):
        for base in (BASE_URL, BASE_URL.replace("http://", "https://", 1)):
            if href.startswith(base):
                return "/" + href[len(base):]
        return None
    if href.startswith("/"):
        return href
    return None


def paginated(path):
    """The first page of a list and all its next pages (/page/2/, ...)."""
    pages = [page(path)]
    n = 2
    while site_file(f"{path}page/{n}/").exists():
        pages.append(page(f"{path}page/{n}/"))
        n += 1
    return pages


def linked_paths(pages, section=None):
    result = []
    for p in pages:
        links = p.links if section is None else [(h, t, s) for h, t, s in p.links if s == section]
        for href, _, _ in links:
            path = local_path(href)
            if path:
                result.append(path.split("#")[0])
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class SiteTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (SITE / "index.html").exists():
            raise unittest.SkipTest(f"No built site in {SITE}. Run 'hugo -DEF' first.")


class TestBasicFiles(SiteTestCase):
    def test_main_files_exist(self):
        for name in ["index.html", "404.html", "index.xml", "sitemap.xml", "CNAME"]:
            with self.subTest(name=name):
                self.assertTrue((SITE / name).is_file(), name)

    def test_static_files_are_copied(self):
        for file in STATIC.rglob("*"):
            if file.is_file():
                rel = file.relative_to(STATIC)
                with self.subTest(file=str(rel)):
                    self.assertTrue((SITE / rel).is_file(), f"Missing static file {rel}")

    def test_theme_assets_exist(self):
        home = page("/")
        for src in home.srcs:
            path = local_path(src)
            if path:
                with self.subTest(src=src):
                    self.assertTrue(site_file(path).is_file(), f"Missing asset {src}")
        css = [s for s in home.srcs if s.endswith(".css")]
        self.assertTrue(any("hugo-academic.css" in s for s in css), css)
        scripts = [s for s in home.srcs if s.endswith(".js")]
        self.assertTrue(any("hugo-academic.js" in s for s in scripts), scripts)

    def test_404_page(self):
        p = page("/404.html")
        self.assertIn(norm_text(CONFIG["title"]), norm_text(p.title))
        self.assertTrue(any(local_path(h) == "/" for h, _, _ in p.links), "404 page has no link to home")


class TestHomePage(SiteTestCase):
    def setUp(self):
        self.home = page("/")

    def test_title(self):
        self.assertIn(norm_text(CONFIG["title"]), norm_text(self.home.title))

    def test_canonical_and_feed_links(self):
        text = site_file("/").read_text(encoding="utf-8")
        self.assertRegex(text, r'<link rel="canonical" href="' + re.escape(BASE_URL) + '"')
        self.assertRegex(text, r'type="application/rss\+xml"')

    def widgets(self):
        result = []
        for c in pages_of("home"):
            if c.params.get("active", True) is False:
                continue
            result.append(c)
        return result

    def test_widget_sections_in_weight_order(self):
        widgets = self.widgets()
        for w in widgets:
            with self.subTest(widget=w.path.stem):
                self.assertIn(w.path.stem, self.home.sections)
        # Sections appear in weight order. Ties can be in any order.
        position = {sid: i for i, sid in enumerate(self.home.sections)}
        for a in widgets:
            for b in widgets:
                if a.params.get("weight", 0) < b.params.get("weight", 0):
                    with self.subTest(before=a.path.stem, after=b.path.stem):
                        self.assertLess(position[a.path.stem], position[b.path.stem])

    def test_widget_titles(self):
        for w in self.widgets():
            if w.title:
                with self.subTest(widget=w.path.stem):
                    h1 = [a for tag, a in self.home.elements_in(w.path.stem, "h1")]
                    self.assertTrue(h1, f"No heading in widget {w.path.stem}")

    def test_menu(self):
        menu = sorted(CONFIG["menu"]["main"], key=lambda m: m.get("weight", 0))
        nav = [(h, t) for h, t, s in self.home.links if h.endswith(tuple(m["url"] for m in menu))]
        nav_names = [norm_text(t) for _, t in nav]
        expected = [norm_text(m["name"]) for m in menu]
        # All entries are present and in weight order.
        positions = [nav_names.index(name) for name in expected]
        self.assertEqual(positions, sorted(positions), nav_names)
        for m in menu:
            with self.subTest(menu=m["name"]):
                self.assertTrue(any(h.endswith(m["url"]) and norm_text(t) == norm_text(m["name"]) for h, t in nav))
                if m["url"].startswith("#"):
                    self.assertIn(m["url"][1:], self.home.sections, f"Menu target {m['url']} has no section")
                elif local_path(m["url"]):
                    self.assertTrue(site_file(m["url"]).is_file(), f"Menu target {m['url']} has no page")

    def test_about_widget(self):
        about = self.home.elements_in("about")
        params = CONFIG["params"]
        styles = " ".join(a.get("style", "") for _, a in about)
        if params.get("avatar"):
            self.assertIn("img/" + params["avatar"], styles)
            self.assertTrue((SITE / "img" / params["avatar"]).is_file())
        text = site_file("/").read_text(encoding="utf-8")
        self.assertIn(html.escape(params["name"]), text)
        self.assertIn(params["role"], text)
        for org in params.get("organizations", []):
            self.assertIn(org["name"], text)

    def test_social_links(self):
        hrefs = [h for h, _ in self.home.links_in("about")]
        classes = " ".join(a.get("class", "") for _, a in self.home.elements_in("about", "i"))
        for social in CONFIG["params"].get("social", []):
            with self.subTest(icon=social["icon"]):
                self.assertIn(social["link"], hrefs)
                self.assertIn(f'{social["icon_pack"]}-{social["icon"]}', classes)

    def test_contact_widget(self):
        text = norm_text(site_file("/").read_text(encoding="utf-8"))
        params = CONFIG["params"]
        for key in ["email", "phone", "address", "skype", "office_hours"]:
            if params.get(key):
                with self.subTest(key=key):
                    self.assertIn(norm_text(params[key]), text)

    def _widget(self, name):
        for w in pages_of("home"):
            if w.params.get("widget") == name:
                return w
        self.skipTest(f"No {name} widget")

    def _item_links(self, widget, section):
        """Links in the widget that point to pages of a content section.
        Links to files, for example "cite.bib", are not counted."""
        found = []
        for href, _ in self.home.links_in(widget.path.stem):
            path = local_path(href)
            if path and path.startswith(f"/{section}/") and path != f"/{section}/" and path.endswith("/"):
                if path not in found:
                    found.append(path)
        return found

    def _check_list_widget(self, widget_name, section, eligible):
        w = self._widget(widget_name)
        items = self._item_links(w, section)
        expected = min(w.params.get("count", len(eligible)), len(eligible))
        self.assertEqual(len(items), expected, f"{widget_name} widget shows {len(items)} items, expected {expected}")
        known = {c.url_path: c for c in eligible}
        for path in items:
            self.assertIn(path, known, f"{widget_name} widget links to unknown page {path}")
            self.assertTrue(site_file(path).is_file())
        dates = [known[p].date for p in items]
        self.assertEqual(dates, sorted(dates, reverse=True), f"{widget_name} widget is not newest first")
        # The newest items are shown.
        if eligible:
            newest = max(c.date for c in eligible)
            self.assertEqual(known[items[0]].date, newest)

    def test_publications_widget(self):
        self._check_list_widget("publications", "publication", pages_of("publication"))

    def test_publications_widget_isotope_classes(self):
        w = self._widget("publications")
        items = [a for t, a in self.home.elements_in(w.path.stem, "li") if "isotope-item" in a.get("class", "")]
        self.assertTrue(items)
        # Items carry their tags as classes so that filters can work.
        tagged = [c for c in pages_of("publication") if c.tags]
        all_classes = " ".join(a["class"] for a in items)
        for c in tagged[:20]:
            for tag in c.tags:
                for word in tag.split():
                    self.assertIn(word, all_classes)

    def test_talks_widget(self):
        self._check_list_widget("talks", "talk", pages_of("talk"))

    def test_posts_widget(self):
        w = self._widget("posts")
        eligible = [c for c in pages_of("post") if not c.params.get("notonhomepage")]
        if w.params.get("tags"):
            eligible = [c for c in eligible if set(c.tags) & set(w.params["tags"])]
        self._check_list_widget("posts", "post", eligible)

    def test_projects_widget(self):
        w = self._widget("projects")
        projects = pages_of("project")
        links = [h for h, _ in self.home.links_in(w.path.stem)]
        for c in projects:
            with self.subTest(project=c.path.stem):
                if c.body:
                    self.assertTrue(any(local_path(h) == c.url_path for h in links), f"No link to {c.url_path}")
                elif c.params.get("external_link"):
                    self.assertIn(c.params["external_link"], links)
        items = [a for t, a in self.home.elements_in(w.path.stem) if "project-item" in a.get("class", "")]
        self.assertEqual(len(items), len(projects))
        filters = [a.get("data-filter") for t, a in self.home.elements_in(w.path.stem, "a") if "data-filter" in a]
        self.assertEqual(filters, [f["tag"] for f in w.params.get("filter", [])])

    def test_custom_widgets_render_markdown(self):
        for w in pages_of("home"):
            if w.params.get("widget", "custom") == "custom" and w.body:
                with self.subTest(widget=w.path.stem):
                    texts = [t for _, t in self.home.links_in(w.path.stem)]
                    md_links = re.findall(r"\[([^\]]+)\]\(", w.body)
                    for label in md_links[:10]:
                        self.assertIn(plain_title(label), [plain_title(t) for t in texts])


class TestContentPages(SiteTestCase):
    def _check_single(self, c):
        file = site_file(c.url_path)
        self.assertTrue(file.is_file(), f"No page for {c.path.relative_to(ROOT)} at {c.url_path}")
        p = page(c.url_path)
        if c.title:
            self.assertIn(plain_title(c.title), plain_title(p.title))
            self.assertIn(plain_title(c.title), [plain_title(h) for h in p.h1])
        return p

    def test_publication_pages(self):
        types = CONFIG["params"]["publication_types"]
        for c in pages_of("publication"):
            with self.subTest(publication=c.path.stem):
                p = self._check_single(c)
                text = norm_text(site_file(c.url_path).read_text(encoding="utf-8"))
                for author in c.params.get("authors", []):
                    self.assertIn(norm_text(author), text)
                hrefs = [h for h, _, _ in p.links]
                for key in ["url_pdf", "url_slides", "url_code", "url_dataset", "url_project", "url_video"]:
                    value = c.params.get(key, "")
                    if value:
                        self.assertTrue(any(h.endswith(value) for h in hrefs), f"No link for {key}={value}")
                for custom in c.params.get("url_custom", []):
                    if custom.get("url", "").strip():
                        self.assertTrue(any(h.endswith(custom["url"].strip()) for h in hrefs), f"No link for {custom['url']}")
                for t in c.params.get("publication_types", []):
                    self.assertIn(norm_text(types[int(t)]), text)
                if c.params.get("abstract"):
                    self.assertIn("pub-abstract", site_file(c.url_path).read_text(encoding="utf-8"))

    def test_talk_pages(self):
        for c in pages_of("talk"):
            with self.subTest(talk=c.path.stem):
                p = self._check_single(c)
                text = norm_text(site_file(c.url_path).read_text(encoding="utf-8"))
                for key in ["event", "location"]:
                    if c.params.get(key):
                        self.assertIn(plain_title(c.params[key])[:40], text)
                hrefs = [h for h, _, _ in p.links]
                for key in ["url_pdf", "url_slides", "url_video"]:
                    value = c.params.get(key, "")
                    if value:
                        self.assertTrue(any(h.endswith(value) for h in hrefs), f"No link for {key}={value}")

    def test_post_pages(self):
        for c in pages_of("post"):
            with self.subTest(post=c.path.stem):
                self._check_single(c)
                text = site_file(c.url_path).read_text(encoding="utf-8")
                self.assertIn("article-style", text)
                if CONFIG.get("disqusShortname"):
                    self.assertIn(CONFIG["disqusShortname"], text)

    def test_project_pages(self):
        for c in pages_of("project"):
            if c.body:
                with self.subTest(project=c.path.stem):
                    self._check_single(c)

    def test_markdown_is_rendered(self):
        """Pages with Markdown links in the body must show them as HTML links."""
        for c in pages_of("post") + pages_of("project") + pages_of("talk") + pages_of("publication"):
            links = re.findall(r"(?<!!)\[[^\]]+\]\((https?://[^)\s]+)\)", c.body)
            if links and site_file(c.url_path).is_file():
                with self.subTest(page=c.url_path):
                    hrefs = [unquote(h) for h, _, _ in page(c.url_path).links]
                    for url in links[:5]:
                        self.assertIn(unquote(html.unescape(url)), hrefs)


class TestListPages(SiteTestCase):
    def test_publication_list(self):
        p = page("/publication/")
        text = site_file("/publication/").read_text(encoding="utf-8")
        for c in pages_of("publication"):
            with self.subTest(publication=c.path.stem):
                self.assertIn(plain_title(c.title), norm_text(text))
        # Filter by publication type.
        options = [a.get("value") for t, a, _ in p.elements if t == "option"]
        used = sorted({int(t) for c in pages_of("publication") for t in c.params.get("publication_types", [])})
        for t in used:
            with self.subTest(pubtype=t):
                self.assertIn(str(t), options)
        types = sorted(i["type"] for i in list_items("/publication/"))
        self.assertEqual(types, sorted(str(c.params.get("publication_types", ["0"])[0]).strip()
                                       for c in pages_of("publication")))

    def test_talk_list(self):
        text = norm_text(site_file("/talk/").read_text(encoding="utf-8"))
        for c in pages_of("talk"):
            with self.subTest(talk=c.path.stem):
                self.assertIn(plain_title(c.title), text)
        years = re.findall(r"<h3>(\d{4})</h3>", site_file("/talk/").read_text(encoding="utf-8"))
        self.assertEqual(years, sorted(set(years), reverse=True))
        self.assertEqual(set(years), {str(c.date.year) for c in pages_of("talk")})

    def test_paginated_lists(self):
        size = CONFIG.get("paginate", 10)
        for section in ["post"]:
            with self.subTest(section=section):
                pages = paginated(f"/{section}/")
                paths = set(linked_paths(pages))
                for c in pages_of(section):
                    self.assertIn(c.url_path, paths, f"{c.url_path} not listed in /{section}/")
                expected_pages = max(1, -(-len(pages_of(section)) // size))
                self.assertEqual(len(pages), expected_pages)

    def test_pagination_aliases(self):
        # Hugo makes /section/page/1/ redirect to /section/.
        for section in ["post"]:
            with self.subTest(section=section):
                file = site_file(f"/{section}/page/1/")
                self.assertTrue(file.is_file())
                self.assertIn(f"/{section}/", file.read_text(encoding="utf-8"))

    def test_section_feeds(self):
        for section in ["post", "publication", "talk", "project"]:
            with self.subTest(section=section):
                self.assertTrue((SITE / section / "index.xml").is_file())


LIST_ITEM = re.compile(r'<[a-z]+[^>]*\sdata-list-item\s([^>]*)>')
ATTR = re.compile(r'([a-z-]+)="([^"]*)"')


def list_items(path):
    """The items of a list with filters, as dicts of their data attributes."""
    text = site_file(path).read_text(encoding="utf-8")
    return [{k[5:]: html.unescape(v) for k, v in ATTR.findall(m.group(1)) if k.startswith("data-")}
            for m in LIST_ITEM.finditer(text)]


class TestListFilters(SiteTestCase):
    """The lists of publications, talks and projects have filters, a sort
    button and a counter (layouts/partials/list_filters.html)."""

    LISTS = [("/publication/", "publication", "publications"),
             ("/talk/", "talk", "talks"),
             ("/project/", "project", "projects")]

    def test_controls(self):
        for path, section, noun in self.LISTS:
            with self.subTest(list=path):
                text = site_file(path).read_text(encoding="utf-8")
                p = page(path)
                self.assertRegex(text, r'<div class="list-filters" data-list="#[^"]+" data-noun="' + noun + '">')
                n = len(pages_of(section))
                self.assertIn(f"Showing {n} of {n} {noun}", norm_text(text).replace("showing", "Showing"))
                self.assertRegex(text, r'<button[^>]*class="[^"]*list-sort[^"]*"[^>]*data-order="newest"')
                self.assertTrue(any(src.endswith("list-filters.js") for src in p.srcs), "No script for the filters")
                self.assertTrue(any("list-filters.css" in src for src in p.srcs), "No CSS for the filters")
        self.assertIn('class="list-type"', site_file("/publication/").read_text(encoding="utf-8"))
        for path, _, _ in self.LISTS:
            with self.subTest(list=path):
                self.assertIn('class="list-text-search"', site_file(path).read_text(encoding="utf-8"),
                              "No text search box")

    def test_items_newest_first(self):
        for path, section, _ in self.LISTS:
            with self.subTest(list=path):
                dates = [i["date"] for i in list_items(path)]
                expected = sorted((c.date.strftime("%Y%m%d") for c in pages_of(section)), reverse=True)
                self.assertEqual(dates, expected)

    def test_items_have_their_tags(self):
        """For each tag, the items with the tag are the pages with the tag."""
        for path, section, _ in self.LISTS:
            items = list_items(path)
            by_tag = {}
            for c in pages_of(section):
                for t in {norm_term(t) for t in c.tags}:
                    by_tag.setdefault(t, []).append(c.date.strftime("%Y%m%d"))
            text = site_file(path).read_text(encoding="utf-8")
            select = re.search(r'<select class="list-tags-select"[^>]*>(.*?)</select>', text, re.S)
            if not by_tag:
                self.assertIsNone(select, f"{path} has a tag filter with no tags")
                continue
            self.assertIsNotNone(select, f"No tag filter on {path}")
            self.assertRegex(select.group(1), r'^\s*<option value="\*">', "First option must show all")
            options = re.findall(r'<option value="([^"*]+)">\s*([^<]*?)\s*\((\d+)\)\s*</option>', select.group(1))
            self.assertEqual(sorted(norm_term(label) for _, label, _ in options), sorted(by_tag),
                             f"One option for each tag of {path}")
            for name, label, count in options:
                with self.subTest(list=path, tag=label):
                    expected = sorted(by_tag[norm_term(label)])
                    self.assertEqual(int(count), len(expected), "Wrong number in the option label")
                    tagged = sorted(i["date"] for i in items if name in i["tags"].split())
                    self.assertEqual(tagged, expected, "Wrong items for the tag")
                    # The name is the name of the tag page, used in the URL hash (#tag=<name>).
                    self.assertTrue(site_file(f"/tags/{name}/").is_file(), f"No page /tags/{name}/")

    def test_most_used_tag_buttons(self):
        for path, _, _ in self.LISTS:
            text = site_file(path).read_text(encoding="utf-8")
            options = re.findall(r'<option value="([^"*]+)">\s*([^<]*?)\s*\((\d+)\)\s*</option>', text)
            counts = {name: int(count) for name, _, count in options}
            chips = re.findall(r'class="[^"]*list-tag-chip[^"]*" data-tag="([^"]+)">\s*(.*?)\s*</button>', text, re.S)
            with self.subTest(list=path):
                self.assertEqual(len(chips), min(12, len(counts)), "Wrong number of buttons for the most used tags")
                values = [v for v, _ in chips]
                for value, label in chips:
                    self.assertIn(value, counts, "The button has no option in the tag filter")
                    self.assertTrue(label.endswith(f"({counts[value]})"), "Wrong number on the button")
                self.assertEqual([counts[v] for v in values], sorted((counts[v] for v in values), reverse=True),
                                 "The buttons are not in order of use")
                if values:
                    smallest = min(counts[v] for v in values)
                    self.assertTrue(all(c <= smallest for v, c in counts.items() if v not in values),
                                    "A tag with more items has no button")

    def test_text_search_data(self):
        """The text for the search of each item has its title, authors, year
        and tags, and the publication and abstract when the page has them."""
        for path, section, _ in self.LISTS:
            items = list_items(path)
            for c in pages_of(section):
                with self.subTest(list=path, page=c.path.stem):
                    matches = [norm_text(i["text"]) for i in items
                               if i["date"] == c.date.strftime("%Y%m%d") and plain_title(c.title) in norm_text(i["text"])]
                    self.assertTrue(matches, "No item with the title in its search text")
                    expected = [str(c.date.year)] + [norm_text(a) for a in c.params.get("authors", [])]
                    expected += [norm_text(t).replace("-", " ").split()[0] for t in c.tags]
                    for field in ("publication", "abstract", "event", "summary"):
                        value = str(c.params.get(field, "")).strip()
                        # Markdown and HTML change in the text, so check only plain values.
                        if value and not re.search(r"[\[*<_`]", value):
                            expected.append(norm_text(value)[:30])
                    # Two pages can have the same title and date, so one of the items must match.
                    self.assertTrue(any(all(e in t.replace("-", " ") or e in t for e in expected) for t in matches),
                                    "The search text has not all the data of the page")

    def test_year_groups(self):
        """Talks are in groups by year. Each group has the talks of its year."""
        text = site_file("/talk/").read_text(encoding="utf-8")
        groups = re.split(r'data-list-group data-date="(\d{4})"', text)[1:]
        years = groups[0::2]
        self.assertEqual(years, sorted(set(years), reverse=True))
        for year, chunk in zip(groups[0::2], groups[1::2]):
            with self.subTest(year=year):
                dates = [m.group(1) for m in re.finditer(r'data-list-item data-date="(\d{8})"', chunk)]
                self.assertTrue(dates)
                self.assertTrue(all(d.startswith(year) for d in dates))

    def test_home_links_to_lists(self):
        """The home page links to the lists of publications, talks and projects."""
        links = linked_paths([page("/")])
        for path, _, _ in self.LISTS:
            with self.subTest(list=path):
                self.assertIn(path, links)

    def test_section_text_after_counter(self):
        """The text of the _index.md file of a list shows after the counter."""
        for path, section, _ in self.LISTS:
            index = CONTENT / section / "_index.md"
            body = Content(index).body if index.exists() else ""
            if not body:
                continue
            with self.subTest(list=path):
                text = site_file(path).read_text(encoding="utf-8")
                intro = re.search(r'<div class="article-style list-intro"[^>]*>(.*?)</div>', text, re.S)
                self.assertIsNotNone(intro, "The text of _index.md is not on the page")
                self.assertLess(text.index('class="list-count"'), intro.start(), "The text is not after the counter")
                shown = {unquote(html.unescape(h)) for h in re.findall(r'href="([^"]+)"', intro.group(1))}
                for href in re.findall(r"\]\((https?://[^)\s]+)\)", body):
                    self.assertIn(unquote(href), shown, "A link of _index.md is not on the page")


class TestTaxonomies(SiteTestCase):
    def tag_pages(self):
        """Map normalised tag name to its site path, from the tags list page."""
        result = {}
        for href, _, _ in page("/tags/").links:
            path = local_path(href)
            if path and path.startswith("/tags/") and path != "/tags/":
                path = path.rstrip("/") + "/"
                result[norm_term(unquote(path.split("/")[2]))] = path
        return result

    def test_every_tag_has_a_page(self):
        tag_pages = self.tag_pages()
        for tag in sorted({t for c in all_pages() for t in c.tags}):
            with self.subTest(tag=tag):
                self.assertIn(norm_term(tag), tag_pages, f"Tag {tag} not in /tags/")
                self.assertTrue(site_file(tag_pages[norm_term(tag)]).is_file())

    def test_tag_pages_list_their_content(self):
        tag_pages = self.tag_pages()
        by_tag = {}
        for c in all_pages():
            if c.section == "home":
                continue
            for t in c.tags:
                by_tag.setdefault(norm_term(t), []).append(c)
        for tag, contents in sorted(by_tag.items()):
            with self.subTest(tag=tag):
                path = tag_pages[tag]
                linked = set(linked_paths(paginated(path)))
                for c in contents:
                    self.assertIn(c.url_path, linked, f"{c.url_path} not listed in {path}")
                self.assertIn(tag, norm_term(page(path).title))

    def test_publication_type_pages(self):
        used = {str(t) for c in pages_of("publication") for t in c.params.get("publication_types", [])}
        for t in sorted(used):
            with self.subTest(pubtype=t):
                path = f"/publication_types/{t}/"
                self.assertTrue(site_file(path).is_file())
                linked = set(linked_paths(paginated(path)))
                for c in pages_of("publication"):
                    if t in [str(x) for x in c.params.get("publication_types", [])]:
                        self.assertIn(c.url_path, linked)

    def test_taxonomy_list_pages(self):
        for taxonomy in CONFIG["taxonomies"].values():
            with self.subTest(taxonomy=taxonomy):
                if any(c.params.get(taxonomy) for c in all_pages()):
                    self.assertTrue(site_file(f"/{taxonomy}/").is_file())


class TestFeedsAndSitemap(SiteTestCase):
    def test_rss_feed(self):
        root = ET.parse(SITE / "index.xml").getroot()
        channel = root.find("channel")
        self.assertIsNotNone(channel)
        self.assertIn(norm_text(CONFIG["title"]), norm_text(channel.findtext("title")))
        items = channel.findall("item")
        self.assertGreater(len(items), 0)
        for item in items:
            link = item.findtext("link")
            self.assertTrue(link.startswith(BASE_URL), link)
            self.assertTrue(site_file(local_path(link)).is_file(), link)

    def test_sitemap_lists_all_pages(self):
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        root = ET.parse(SITE / "sitemap.xml").getroot()
        locs = {unquote(e.text.strip()) for e in root.findall(".//s:loc", ns)}
        self.assertIn(BASE_URL, locs)
        for c in all_pages():
            if c.section == "home":
                continue
            with self.subTest(page=c.url_path):
                self.assertIn(BASE_URL + c.url_path.lstrip("/"), locs)


class TestAuthors(SiteTestCase):
    """Each name in the "authors" list of a page has an author page.

    The author page lists all the publications and talks with that author.
    """

    def author_pages(self):
        """Map normalised author name ("A B" and "A-B" are one author) to its site path, from the /authors/ page."""
        result = {}
        for href, text, _ in page("/authors/").links:
            path = local_path(href)
            if path and path.startswith("/authors/") and path.rstrip("/") != "/authors":
                result[norm_term(text)] = path.rstrip("/") + "/"
        return result

    def with_authors(self):
        return [c for c in pages_of("publication") + pages_of("talk") if c.params.get("authors")]

    def test_one_name_per_author_page(self):
        """Two spellings of a name (for example "Prud'hommeaux" and "Prud'Hommeaux")
        can get the same page, and then Hugo shows only the pages of one spelling.
        Use one spelling for each author."""
        seen = {}
        for href, text, _ in page("/authors/").links:
            path = local_path(href)
            if path and path.startswith("/authors/") and path.rstrip("/") != "/authors":
                path = path.rstrip("/") + "/"
                seen.setdefault(path, []).append(text)
        clashes = {p: names for p, names in seen.items() if len(names) > 1}
        self.assertEqual(clashes, {}, "Use one spelling for each author")

    def test_every_author_has_a_page(self):
        pages = self.author_pages()
        for name in sorted({a for c in self.with_authors() for a in c.params["authors"]}):
            with self.subTest(author=name):
                self.assertIn(norm_term(name), pages, f"{name} not in /authors/")
                self.assertTrue(site_file(pages[norm_term(name)]).is_file())

    def test_author_pages_list_their_content(self):
        pages = self.author_pages()
        for c in self.with_authors():
            for name in c.params["authors"]:
                with self.subTest(page=c.url_path, author=name):
                    path = pages[norm_term(name)]
                    self.assertIn(c.url_path, linked_paths(paginated(path)), f"{c.url_path} not listed in {path}")
                    self.assertIn(norm_term(name), [norm_term(h) for h in page(path).h1])

    def test_author_links_on_publication_pages(self):
        for c in pages_of("publication"):
            links = {norm_term(t): local_path(h) for h, t, _ in page(c.url_path).links
                     if (local_path(h) or "").startswith("/authors/")}
            for name in c.params.get("authors", []):
                with self.subTest(publication=c.path.stem, author=name):
                    self.assertIn(norm_term(name), links, f"No link to the page of {name}")
                    target = links[norm_term(name)]
                    self.assertTrue(site_file(target).is_file(), f"Broken author link {target}")
                    self.assertIn(c.url_path, linked_paths(paginated(target.rstrip("/") + "/")))

    def test_author_folders(self):
        """A folder content/authors/<name>/_index.md adds text to the author page."""
        pages = self.author_pages()
        for index in sorted((CONTENT / "authors").glob("*/_index.md")):
            c = Content(index)
            with self.subTest(author=index.parent.name):
                self.assertTrue(c.title, f"{index} has no title")
                self.assertIn(norm_term(c.title), pages, f"No author page for {index}")
                p = page(pages[norm_term(c.title)])
                self.assertIn(norm_term(c.title), [norm_term(h) for h in p.h1])
                for label in re.findall(r"\[([^\]]+)\]\(", c.body):
                    self.assertIn(plain_title(label), [plain_title(t) for _, t, _ in p.links])


# Publication type (see "publication_types" in config.toml) -> BibTeX entry
# type and field for the "publication" text.
BIBTEX_TYPES = {
    "0": ("misc", "howpublished"),
    "1": ("inproceedings", "booktitle"),
    "2": ("article", "journal"),
    "3": ("article", "journal"),
    "4": ("techreport", "institution"),
    "5": ("book", "publisher"),
    "6": ("incollection", "booktitle"),
    "7": ("misc", "howpublished"),
    "8": ("phdthesis", "note"),
    "9": ("misc", "howpublished"),
    "10": ("book", "publisher"),
    "11": ("misc", "howpublished"),
}


def parse_bibtex(text):
    """Parse BibTeX entries into a list of (type, key, fields).

    Field values are in braces, which can contain more braces, or they are
    one word (for example "month = jul"). Raise ValueError for bad syntax.
    """
    entries = []
    i = 0
    while True:
        start = text.find("@", i)
        if start < 0:
            if text[i:].strip():
                raise ValueError(f"text after the last entry: {text[i:i + 40]!r}")
            return entries
        if text[i:start].strip():
            raise ValueError(f"text between entries: {text[i:start][:40]!r}")
        m = re.compile(r"@(\w+)\{([^,\s]+),").match(text, start)
        if not m:
            raise ValueError(f"bad entry start: {text[start:start + 40]!r}")
        etype, key, i = m.group(1).lower(), m.group(2), m.end()
        fields = {}
        while True:
            m = re.compile(r"\s*(\}|(\w+)\s*=\s*)").match(text, i)
            if not m:
                raise ValueError(f"bad field in {key}: {text[i:i + 40]!r}")
            i = m.end()
            if m.group(1) == "}":
                break
            name = m.group(2).lower()
            if name in fields:
                raise ValueError(f"field {name} two times in {key}")
            if text[i] == "{":
                depth, j = 0, i
                while True:
                    if text[j] == "{" and text[j - 1] != "\\":
                        depth += 1
                    elif text[j] == "}" and text[j - 1] != "\\":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                    if j >= len(text):
                        raise ValueError(f"no closing brace in {key}.{name}")
                fields[name] = text[i + 1:j]
                i = j + 1
            else:
                m = re.compile(r"\w+").match(text, i)
                if not m:
                    raise ValueError(f"bad value in {key}.{name}")
                fields[name] = m.group(0)
                i = m.end()
            m = re.compile(r"\s*,?").match(text, i)
            i = m.end()
        entries.append((etype, key, fields))


def bibtex_text(value):
    """A BibTeX field value as plain text."""
    return re.sub(r"\\([&%#$_])", r"\1", value)


class TestBibTeX(SiteTestCase):
    """Each publication has a BibTeX entry made from its front matter."""

    def bib(self, c):
        return site_file(c.url_path + "cite.bib")

    def test_each_publication_has_a_bib_file(self):
        for c in pages_of("publication"):
            with self.subTest(publication=c.path.stem):
                file = self.bib(c)
                self.assertTrue(file.exists(), f"missing {file}")
                entries = parse_bibtex(file.read_text(encoding="utf-8"))
                self.assertEqual(len(entries), 1)
                etype, key, fields = entries[0]
                types = c.params.get("publication_types") or ["0"]
                expected_type, venue = BIBTEX_TYPES.get(str(types[0]).strip(), BIBTEX_TYPES["0"])
                self.assertEqual(etype, expected_type)
                self.assertEqual(key, c.path.stem)
                self.assertEqual(norm_text(bibtex_text(fields["title"])), norm_text(c.title))
                self.assertEqual(fields["year"], str(c.date.year))
                self.assertTrue(fields["url"].startswith(("http://", "https://")))
                names = [n.strip() for n in re.split(r"\s+and\s+", fields.get("author", fields.get("editor", "")))]
                self.assertEqual(names, [re.sub(r"\s+", " ", a.strip()) for a in c.params.get("authors", [])])
                if c.params.get("publication", "").strip():
                    self.assertIn(venue, fields)
                    self.assertNotRegex(fields[venue], r"[<>]|\]\(", "Markdown link or HTML in the BibTeX text")
                for name, value in fields.items():
                    if name not in ("url", "doi"):
                        self.assertNotRegex(value, r"(?<!\\)[&%#]", f"special character with no backslash in {name}")
                if "doi" in fields:
                    self.assertRegex(fields["doi"], r"^10\.\d{4,9}/\S+$")

    def test_doi_field(self):
        """A publication with a "doi" field or a DOI link has the DOI in its entry."""
        for c in pages_of("publication"):
            links = [c.params.get("doi", ""), c.params.get("url_pdf", ""), c.params.get("publication", "")]
            links += [u.get("url", "") for u in c.params.get("url_custom", [])]
            has_doi = bool(c.params.get("doi")) or any(re.search(r"(?i)doi\.(org|acm\.org)/10\.", link) for link in links)
            if has_doi:
                with self.subTest(publication=c.path.stem):
                    _, _, fields = parse_bibtex(self.bib(c).read_text(encoding="utf-8"))[0]
                    self.assertIn("doi", fields)

    def test_publication_page_shows_bibtex(self):
        for c in pages_of("publication"):
            with self.subTest(publication=c.path.stem):
                text = site_file(c.url_path).read_text(encoding="utf-8")
                m = re.search(r'<pre id="pub-bibtex"[^>]*>(.*?)</pre>', text, re.S)
                self.assertTrue(m, "no BibTeX entry on the page")
                self.assertEqual(html.unescape(m.group(1)).strip(), self.bib(c).read_text(encoding="utf-8").strip())
                self.assertIn('class="btn btn-primary btn-outline pub-cite-copy"', text)
                self.assertIn(f'href="{c.url_path}cite.bib"', text)

    def test_all_publications_bib_file(self):
        file = site_file("/publication/cite.bib")
        self.assertTrue(file.exists())
        entries = parse_bibtex(file.read_text(encoding="utf-8"))
        keys = [key for _, key, _ in entries]
        self.assertEqual(sorted(keys), sorted(c.path.stem for c in pages_of("publication")))
        self.assertEqual(len(keys), len(set(keys)), "two entries with the same key")
        self.assertIn('href="/publication/cite.bib"', site_file("/publication/").read_text(encoding="utf-8"))

    def test_bibtex_parser(self):
        """The test parser finds bad syntax."""
        good = "@misc{a,\n  title = {A {B} c},\n  month = jul,\n  year = {2020}\n}\n"
        self.assertEqual(parse_bibtex(good), [("misc", "a", {"title": "A {B} c", "month": "jul", "year": "2020"})])
        for bad in ("@misc{a,\n  title = {A {B c},\n}", "@misc{a,\n  title = {A},\n  title = {B}\n}", "x @misc{a,\n}"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    parse_bibtex(bad)


class TestLinks(SiteTestCase):
    # Documents that the content links to, but that are not in static/ yet.
    # Remove an entry when you add the file.
    KNOWN_MISSING = {
        "/pdf/2018_InferenceLatentShEx.pdf",
        "/pdf/2018_rdfshapeDemo.pdf",
    }

    def test_no_unsafe_urls(self):
        """Go templates write "#ZgotmplZ" for a URL that they think is unsafe."""
        bad = [str(f.relative_to(SITE)) for f in SITE.rglob("*.html") if "ZgotmplZ" in f.read_text(errors="replace")]
        self.assertEqual(bad, [], "Unsafe URLs (check for spaces at the start of URLs in front matter)")

    def test_internal_links_resolve(self):
        broken = {}
        for file in SITE.rglob("*.html"):
            text = file.read_text(encoding="utf-8", errors="replace")
            if 'http-equiv="refresh"' in text[:500]:
                continue  # alias redirect page
            p = Page(text)
            for href in [h for h, _, _ in p.links] + p.srcs:
                path = local_path(href)
                if not path or unquote(path) in self.KNOWN_MISSING:
                    continue
                if not site_file(path).exists():
                    broken.setdefault(path, str(file.relative_to(SITE)))
        self.maxDiff = None
        self.assertEqual(broken, {}, f"{len(broken)} broken internal links (target: first page)")


if __name__ == "__main__":
    unittest.main()
