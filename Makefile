hugo=binaries/hugo_old
# Empty for now
dev:
	$(hugo) server --watch --buildDrafts

build:
	$(hugo) -D	
