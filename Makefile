hugo=binaries/hugo
# Empty for now
dev:
	$(hugo) server --watch --buildDrafts

build:
	$(hugo) -D	
