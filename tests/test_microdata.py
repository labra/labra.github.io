"""Tests for the microdata reader and the schema.org check in microdata.py.
They do not need a built site."""

import unittest

from microdata import Vocabulary, parse

VOCABULARY = Vocabulary.load()

GOOD = """
<div itemscope itemtype="https://schema.org/ScholarlyArticle" itemid="https://example.org/p/1/">
  <h1 itemprop="name">A paper</h1>
  <span itemprop="author" itemscope itemtype="https://schema.org/Person" itemid="https://example.org/authors/ana/">
    <a itemprop="url" href="/authors/ana/"><span itemprop="name">Ana</span></a>
  </span>
  <time itemprop="datePublished" datetime="2020-05-01">2020</time>
  <meta itemprop="keywords" content="RDF">
  <span itemprop="isPartOf" itemscope itemtype="https://schema.org/Periodical">
    <span itemprop="name">A journal</span>
  </span>
</div>
<div itemscope itemtype="https://schema.org/Person" itemref="mail">
  <span itemprop="name">Bob</span>
</div>
<p id="mail" itemprop="email">bob at example dot org</p>
"""


class TestParse(unittest.TestCase):
    def test_items_and_values(self):
        items, orphans = parse(GOOD, "https://example.org/")
        self.assertEqual(orphans, [])
        self.assertEqual(len(items), 2)
        paper, bob = items
        self.assertEqual(paper.type_names, ["ScholarlyArticle"])
        self.assertEqual(paper.id, "https://example.org/p/1/")
        self.assertEqual(paper.text("name"), "A paper")
        self.assertEqual(paper.text("datePublished"), "2020-05-01")
        self.assertEqual(paper.text("keywords"), "RDF")
        author = paper.value("author")
        self.assertEqual(author.text("name"), "Ana")
        self.assertEqual(author.text("url"), "https://example.org/authors/ana/")
        self.assertEqual(paper.value("isPartOf").text("name"), "A journal")
        # itemref adds properties from other parts of the page.
        self.assertEqual(bob.text("email"), "bob at example dot org")

    def test_orphan_property(self):
        _, orphans = parse('<div><span itemprop="name">x</span></div>')
        self.assertEqual(len(orphans), 1)

    def test_unclosed_elements(self):
        items, _ = parse('<ul itemscope itemtype="https://schema.org/Person"><li><span itemprop="name">A</span>'
                         '<p>no end tag<li>more</ul><span itemprop="name">B</span>')
        self.assertEqual([i.text("name") for i in items], ["A"])


class TestVocabulary(unittest.TestCase):
    def errors(self, html):
        return VOCABULARY.check(*parse(html, "https://example.org/"))

    def test_good_markup(self):
        self.assertEqual(self.errors(GOOD), [])

    def test_bad_markup(self):
        cases = {
            "unknown type": '<div itemscope itemtype="https://schema.org/Paper"></div>',
            "http instead of https": '<div itemscope itemtype="http://schema.org/Person"></div>',
            "no type": '<div itemscope><span itemprop="name">x</span></div>',
            "unknown property": '<div itemscope itemtype="https://schema.org/Person"><span itemprop="authors">x</span></div>',
            "wrong domain": '<div itemscope itemtype="https://schema.org/Person"><span itemprop="datePublished">2020-01-01</span></div>',
            "wrong range": '<div itemscope itemtype="https://schema.org/Book"><span itemprop="author" itemscope '
                           'itemtype="https://schema.org/Book"></span></div>',
            "bad date": '<div itemscope itemtype="https://schema.org/Book"><span itemprop="datePublished">May 2020</span></div>',
            "URL in text": '<div itemscope itemtype="https://schema.org/Book"><span itemprop="url">x</span></div>',
            "orphan": '<span itemprop="name">x</span>',
            "relative itemid": '<div itemscope itemtype="https://schema.org/Book" itemid="/b/"></div>',
            "empty value": '<div itemscope itemtype="https://schema.org/Book"><span itemprop="name"> </span></div>',
        }
        for name, html in cases.items():
            with self.subTest(case=name):
                self.assertNotEqual(self.errors(html), [], name)

    def test_subtypes(self):
        # "abstract" is a property of CreativeWork, so it is good for Thesis.
        html = '<div itemscope itemtype="https://schema.org/Thesis"><p itemprop="abstract">x</p></div>'
        self.assertEqual(self.errors(html), [])
        # A Periodical is a CreativeWork, so it is good for isPartOf.
        self.assertIn("CreativeWork", VOCABULARY.ancestors("Periodical"))


if __name__ == "__main__":
    unittest.main()
