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

## Academic theme

The folder `themes/academic` contains a copy of the
[Academic theme](https://github.com/gcushen/hugo-academic) (commit `4a2a754`, July 2017),
with changes for new Hugo versions. Files in `layouts` override the theme files.
