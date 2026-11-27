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

version:
	@echo "Expected: v$(HUGO_VERSION)"
	@$(HUGO) version

rm:
	rm -r $(LOCAL_GH_PAGES)* 
	
local:
	cp -r public/* $(LOCAL_GH_PAGES)/
