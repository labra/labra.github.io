# Labra's home page

This repo contains the source code of [Labra's homepage](https://labra.weso.es/).

## Local building Instructions

The site uses [Hugo](https://gohugo.io/installation/) version 0.170.1.
Install it and make sure that `hugo` is in your `PATH`:

```sh
make version
```

In order to build the pages in the `public` folder, run:

```sh
make build
```

In order to build and deploy the pages locally for testing, run:

```sh
make dev
```

## Tests

The folder `tests` contains tests for the generated site. They use only the
Python standard library (Python 3.11 or later). To build the site and run the
tests, run:

```sh
make test
```

The tests read `config.toml` and the `content` folder to know what the site must
contain, so you can add publications, talks and posts without changes to the
tests. The GitHub workflow runs the tests before it deploys the site.

To check the links to other sites (this needs network access and takes a
few minutes), run:

```sh
make check-links
```

Links to the old university pages (`www.di.uniovi.es/~labra`) go to copies in
the [Web Archive](https://web.archive.org/). To check that each link has a good
copy, run `make check-archive-links`. To put the date of the newest good copy in
each link, run `make pin-archive-links`.

## Filters on the lists of publications, talks and projects

The pages `/publication/`, `/talk/` and `/project/` have filters, a sort
button and a counter ("Showing 15 of 138 publications") that changes with
the filters. One partial (`layouts/partials/list_filters.html`) makes the
controls and one script (`static/js/list-filters.js`) makes them work.

- **Filter by tag** (publications and projects): type a part of the tag name
  in the search box (case and accents do not matter) and select the tag, or
  click one of the buttons of the 12 most used tags. Hugo makes the list of
  tags and the buttons from the content. The filter shows only when the
  pages of the list have tags, so if you add `tags` to talks, the talks page
  gets the filter too.
- **Filter by type** (publications).
- **Text search** (all lists): the list shows the items that contain all
  the words that you type, in any order. Case and accents do not matter.
  The search uses the title, authors, year and tags, and also the
  publication and abstract (publications), the event, place and abstract
  (talks) or the summary (projects).
- **Sort**: "Newest first" changes to "Oldest first" and back.

The URL keeps the filters and the order, so you can share a link to a
filtered list, for example `/publication/#tag=shex`,
`/publication/#2&tag=rdf&sort=oldest` or `/publication/#q=wikidata`.

The menu items Publications, Talks and Projects go to these pages. The text
of `content/<section>/_index.md` (for example the "Other lists" links in
`content/publication/_index.md`) shows after the counter.

To add the filters to another list, call the partial `list_filters` and give
each item the attribute `data-list-item` and the attributes of the partial
`list_item_data`. See `layouts/section/project.html` for a short example.

## BibTeX

Hugo makes a BibTeX entry for each publication from its front matter
(`layouts/partials/publication_bibtex.html`). You do not write the entries.

- The page of each publication shows the entry, with the buttons "Copy
  BibTeX" and "Download .bib". The file is `/publication/<name>/cite.bib`.
- `/publication/cite.bib` has the entries of all publications.
- The key is the name of the Markdown file, for example `2017_ShExSpec`.
- The entry type comes from `publication_types`:

  | Publication type | BibTeX entry | Field for `publication` |
  |---|---|---|
  | 1 Conference proceedings | `@inproceedings` | `booktitle` |
  | 2, 3 Journal | `@article` | `journal` |
  | 4 Technical report | `@techreport` | `institution` |
  | 5, 10 Book | `@book` | `publisher` |
  | 6 Book chapter | `@incollection` | `booktitle` |
  | 8 PhD thesis | `@phdthesis` | `note` |
  | 0, 7, 9, 11 Other | `@misc` | `howpublished` |

- `authors`, `title` and `date` give `author`, `title`, `year` and `month`.
  A date of 1 January gives no month, because it usually means that the
  month is not known.
- The DOI comes from the `doi` field, or from a doi.org or doi.acm.org link
  in `url_pdf`, `publication` or `url_custom`.
- `url` is the PDF (`url_pdf`), or else the page of the publication.
- To add more data, put these fields in the front matter with the same name
  as in BibTeX: `volume`, `number`, `pages`, `publisher`, `school`,
  `institution`, `isbn`, `address`, `editors`. For example, add
  `school = "Universidad de Oviedo"` to the PhD thesis.

## Schema.org microdata

The pages describe their content with [schema.org](https://schema.org/)
microdata, so search engines and other tools can read it.

| Page | schema.org type |
|---|---|
| Home page (about widget) | `Person` with name, job title, organization, image, social links (`sameAs`), interests (`knowsAbout`), education (`alumniOf`, `hasCredential`), email, telephone and address |
| Publication (page and lists) | From `publication_types`: `ScholarlyArticle` (conference, journal, preprint), `Book`, `Chapter`, `Report`, `Thesis`, `TechArticle` (specification) or `CreativeWork` |
| Talk (page and lists) | `Event`, with `superEvent` (the event), `location` and `performer` |
| Project (page and list) | `SoftwareSourceCode`, or `schema_type` in the front matter |
| Post (page and lists) | `BlogPosting` |
| Author page | `ProfilePage` with a `Person` as `mainEntity` |

Each person is a `Person` with a link to their author page. The `itemid`
of a person is the URL of the author page, and the `itemid` of a
publication, talk, project or post is the URL of its page. So all pages
use the same identifier for the same thing. The owner of the site
(`name` in config.toml) has the URL of their author page as `itemid` on
the home page too.

Talks and posts with no `authors` list have the owner of the site as
speaker or author. Projects can have an `authors` list too.

The tests check the microdata of all pages against a copy of the
schema.org vocabulary in `tests/schemaorg.json`, so they do not need the
network. `tests/microdata.py` reads the microdata. To use a newer
schema.org version, run `make update-schemaorg`. To check a page with the
official validator, paste its URL in https://validator.schema.org/.

## Author pages

Hugo makes a page `/authors/<name>/` for each name in the `authors` list of a
publication or a talk. The page lists all the publications and talks with that
author. Links to co-authors on the publication pages go to these pages.

Use the same spelling of a name in all the files. For example, "Prud'hommeaux"
and "Prud'Hommeaux" give two authors with the same page, and then the page
shows only the publications of one of them. The tests find this problem.

To add text to an author page, add the file `content/authors/<name>/_index.md`
with a `title` that is the name of the author. The folder name must be the
name in lowercase with `-` in place of spaces, for example
`content/authors/iovka-boneva/_index.md`.

## Academic theme

The folder `themes/academic` contains a copy of the
[Academic theme](https://github.com/gcushen/hugo-academic) (commit `4a2a754`, July 2017),
with changes for new Hugo versions. Files in `layouts` override the theme files.
