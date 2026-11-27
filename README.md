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

## Publication filters

The page `/publication/` has two filters: by type and by tag. The tag filter
lists all the tags of publications, with the number of publications for each
tag. It changes when you add publications or tags, so you do not have to edit
it. The URL keeps the filters, so you can share a link to a filtered list, for
example `/publication/#tag=shex` or `/publication/#2&tag=rdf`.

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
