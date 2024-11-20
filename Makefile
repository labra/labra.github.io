HUGO=binaries/hugo_old
LOCAL_GH_PAGES=../../gh_pages/labra.github.io
# Empty for now
dev:
	$(HUGO) server --watch --buildDrafts

build:
	$(HUGO) -D	

rm:
	rm -r $(LOCAL_GH_PAGES)* 
	
local:
	cp -r public/* $(LOCAL_GH_PAGES)/

