# Personal web pages

These pages are based on: [hugo-academic templates](https://github.com/gcushen/hugo-academic)

In order to create the web pages, run:

> hugo

This command will create a folder "public" which contains the web site.

For development, run:

> hugo server --watch

# Automatic deploy using Travis

Steps described [here](https://haruair.github.io/post/setup-hugo-blog-on-github-pages-with-travis-ci/)

Note: I had [a problem](https://github.com/travis-ci/travis-ci/issues/4746) using Windows when generating the ssh-key gen, so I had to use a Linux virtual machine.
