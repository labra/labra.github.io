# Hugo version that the site uses. Keep it the same as HUGO_VERSION in
# .github/workflows/hugo.yml. Install it from https://gohugo.io/installation/
HUGO_VERSION=0.170.1
HUGO=hugo
LOCAL_GH_PAGES=../../gh_pages/labra.github.io

dev:
	$(HUGO) server --watch --buildDrafts

build:
	$(HUGO) -DEF

# Build the site and test the result in the public folder
test: build
	python3 -m unittest discover -s tests -v

# Check the links to other sites (needs network access)
check-links: build
	python3 tests/check_external_links.py

# Check the Web Archive links (needs network access).
# Use "make pin-archive-links" to put the date of the newest good copy in each link.
check-archive-links:
	python3 tests/pin_archive_links.py

pin-archive-links:
	python3 tests/pin_archive_links.py --write

version:
	@echo "Expected: v$(HUGO_VERSION)"
	@$(HUGO) version

rm:
	rm -r $(LOCAL_GH_PAGES)* 
	
local:
	cp -r public/* $(LOCAL_GH_PAGES)/
