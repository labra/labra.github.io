"""Read HTML microdata and check it against the schema.org vocabulary.

The module uses only the Python standard library. It follows the microdata
algorithm of the HTML standard
(https://html.spec.whatwg.org/multipage/microdata.html), with these limits:
it does not check for loops of itemref, and it uses the text of an element
with no special value attribute as the value.

Usage:

    from microdata import parse, Vocabulary
    items, orphans = parse(html_text)
    errors = Vocabulary.load().check(items, orphans)
"""

import json
import re
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

SCHEMA = "https://schema.org/"
VOCABULARY_FILE = Path(__file__).resolve().parent / "schemaorg.json"

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "source", "track", "wbr", "param", "keygen"}
SRC_VALUE = {"audio", "embed", "iframe", "img", "source", "track", "video"}
HREF_VALUE = {"a", "area", "link"}


class Element:
    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children = []
        self.text = []

    def get(self, name, default=None):
        return self.attrs.get(name, default)

    def text_content(self):
        parts = []
        for piece in self.text:
            parts.append(piece if isinstance(piece, str) else piece.text_content())
        return "".join(parts)

    def __repr__(self):
        return f"<{self.tag} {self.attrs}>"


class Tree(HTMLParser):
    """A simple DOM tree. HTML does not need closing tags for some elements,
    so an end tag closes the nearest open element with the same name."""

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Element("#document", {}, None)
        self.current = self.root
        self.by_id = {}
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        element = Element(tag, {k: (v if v is not None else "") for k, v in attrs}, self.current)
        self.current.children.append(element)
        self.current.text.append(element)
        if "id" in element.attrs:
            self.by_id.setdefault(element.attrs["id"], element)
        if tag not in VOID:
            self.current = element

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.current = self.current.parent

    def handle_endtag(self, tag):
        node = self.current
        while node is not None and node.tag != tag:
            node = node.parent
        if node is not None and node.parent is not None:
            self.current = node.parent

    def handle_data(self, data):
        self.current.text.append(data)


class Item:
    def __init__(self, element):
        self.element = element
        self.types = element.get("itemtype", "").split()
        self.id = element.get("itemid")
        self.properties = []  # list of (name, value, element); value is str or Item

    @property
    def type_names(self):
        return [t[len(SCHEMA):] if t.startswith(SCHEMA) else t for t in self.types]

    def values(self, name):
        return [v for n, v, _ in self.properties if n == name]

    def value(self, name, default=None):
        values = self.values(name)
        return values[0] if values else default

    def text(self, name, default=""):
        value = self.value(name)
        if isinstance(value, Item) or value is None:
            return default
        return re.sub(r"\s+", " ", value).strip()

    def __repr__(self):
        return f"Item({self.types}, id={self.id})"


def walk(element):
    yield element
    for child in element.children:
        yield from walk(child)


def property_value(element, base_url):
    tag = element.tag
    if tag == "meta":
        return element.get("content", "")
    if tag in SRC_VALUE:
        return urljoin(base_url, element.get("src", ""))
    if tag in HREF_VALUE:
        return urljoin(base_url, element.get("href", ""))
    if tag == "object":
        return urljoin(base_url, element.get("data", ""))
    if tag in ("data", "meter"):
        return element.get("value", "")
    if tag == "time" and "datetime" in element.attrs:
        return element.get("datetime")
    return element.text_content()


def parse(text, base_url=""):
    """Return (items, orphans): the top-level items of the page, and the
    elements with itemprop that are not properties of any item."""
    tree = Tree(text)
    items_by_element = {}
    reached = set()

    def make_item(element):
        if id(element) in items_by_element:
            return items_by_element[id(element)]
        item = Item(element)
        items_by_element[id(element)] = item
        # The properties are in the children and in the elements of itemref.
        pending = list(element.children)
        for ref in element.get("itemref", "").split():
            if ref in tree.by_id:
                pending.append(tree.by_id[ref])
        seen = set()
        found = []
        while pending:
            node = pending.pop(0)
            if id(node) in seen:
                continue
            seen.add(id(node))
            if "itemprop" in node.attrs:
                found.append(node)
            if "itemscope" not in node.attrs:
                pending.extend(node.children)
        for node in found:
            reached.add(id(node))
            value = make_item(node) if "itemscope" in node.attrs else property_value(node, base_url)
            for name in node.get("itemprop").split():
                item.properties.append((name, value, node))
        return item

    top = [make_item(e) for e in walk(tree.root)
           if "itemscope" in e.attrs and "itemprop" not in e.attrs]
    orphans = [e for e in walk(tree.root) if "itemprop" in e.attrs and id(e) not in reached]
    return top, orphans


def all_items(items):
    """The items and all the items in their properties."""
    seen = set()
    stack = list(items)
    while stack:
        item = stack.pop(0)
        if id(item) in seen:
            continue
        seen.add(id(item))
        yield item
        stack.extend(v for _, v, _ in item.properties if isinstance(v, Item))


def is_date(value):
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        pass
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


class Vocabulary:
    """The schema.org types and properties (see update_schemaorg.py)."""

    DATA_TYPES = {"Text", "URL", "Date", "DateTime", "Time", "Number", "Integer", "Float",
                  "Boolean", "DataType", "CssSelectorType", "XPathType", "PronounceableText"}

    def __init__(self, data):
        self.version = data["version"]
        self.types = data["types"]
        self.properties = data["properties"]
        self.members = data.get("members", {})

    @classmethod
    def load(cls, path=VOCABULARY_FILE):
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def ancestors(self, name):
        """The type and all its superclasses."""
        result, stack = [], [name]
        while stack:
            t = stack.pop()
            if t not in result:
                result.append(t)
                stack.extend(self.types.get(t, []))
        return result

    def check(self, items, orphans=()):
        """Return a list of error messages. An empty list means that the
        microdata use the schema.org vocabulary correctly."""
        errors = []
        for element in orphans:
            errors.append(f'itemprop="{element.get("itemprop")}" on <{element.tag}> is not in an item')
        for item in all_items(items):
            label = "/".join(item.type_names) or "(no type)"
            if not item.types:
                errors.append(f"item with no itemtype: {item.element}")
                continue
            for t in item.types:
                if not t.startswith(SCHEMA):
                    errors.append(f'itemtype "{t}" does not start with {SCHEMA}')
                elif t[len(SCHEMA):] not in self.types:
                    errors.append(f'unknown schema.org type "{t}"')
            if item.id is not None and not re.match(r"^https?://", item.id):
                errors.append(f'{label}: itemid "{item.id}" is not an absolute URL')
            supertypes = set()
            for t in item.type_names:
                supertypes.update(self.ancestors(t))
            for name, value, element in item.properties:
                where = f"{label}.{name}"
                prop = self.properties.get(name)
                if prop is None:
                    errors.append(f"{where}: unknown schema.org property")
                    continue
                if prop["superseded"]:
                    errors.append(f"{where}: the property is superseded")
                if not supertypes.intersection(prop["domain"]):
                    errors.append(f"{where}: not a property of {label} (domain: {', '.join(prop['domain'])})")
                ranges = set(prop["range"])
                if isinstance(value, Item):
                    value_types = set()
                    for t in value.type_names:
                        value_types.update(self.ancestors(t))
                    if not value_types.intersection(ranges):
                        errors.append(f"{where}: an item of type {'/'.join(value.type_names)} is not in the range "
                                      f"({', '.join(sorted(ranges))})")
                else:
                    if not value.strip():
                        errors.append(f"{where}: empty value")
                    if ranges and ranges <= {"Date", "DateTime"} and not is_date(value.strip()):
                        errors.append(f'{where}: "{value}" is not an ISO 8601 date')
                    if ranges == {"URL"} and element.tag not in HREF_VALUE | SRC_VALUE | {"meta", "object"}:
                        errors.append(f"{where}: a URL must be in href, src or content, not in <{element.tag}>")
        return errors
