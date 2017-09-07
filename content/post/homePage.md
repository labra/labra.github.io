+++
date = "2017-08-21T10:39:00"
draft = false
tags = ["academic", "homePage"]
title = "Home page revamped"
math = false
summary = """
Description of my new home page  
"""

+++

These days, in my spare time while on vacation, I decided to rewrite my home page.
 The task was not easy as I was doing it in a hotel in Lanzarote, without internet connection in my room, 
 and using [Hugo](http://gohugo.io/), a website framework, that I hadn't used before.

Anyway, Hugo seems quite intuitive and is very fast to compile and run, so it is funny for trial-and-error.
Also, there is a very nice [Academic theme](https://github.com/gcushen/hugo-academic) which facilitated
the quick creation of the fist draft.

Once I did the first draft and started to add content, 
 I noticed that I had a long list of publications that required 
 some extra-information like the journal, year or authors, so I had 
 to customize the academic theme.

In order to browse Hugo documentation while being offline, I found useful [this project](https://github.com/hamoid/long-hugo-doc), 
 which generated all Hugo documentation in a single HTML page. 
 
It seems that the customization can be easily done by replacing 
 the pages that are in the themes folder by the equivalent ones in the root folder.
 
I had to change the pages: 

- `layouts/widgets/publication`: declares how to visualize publications in the home page. I added a link at the end to show all publications.
 I had also added some code to add filtering by tags, but the result is not nice, so I commented it. It seems that commenting code in HTML in Hugo requires to remove the `{{` in the comments.
 
- `layouts/partials/publication_li_simple.html`: defines how to visualize a single publication (I added there the authors, publication and year)

- `layouts/section/publication.html`: declares how to filter publications by type and repeats the previous code. It would be better to use a partial, but I didn't want to break things from the academic theme.

I also managed to integrate Travis with github so when I push some changes to github, it automatically deploys the content via Travis.
 Notice that there are 2 branches, the `source` branch contains the source code, and the `master` branch contains the result (in Hugo, the result is by default created in the folder `/public`)

The source code is located [here](https://github.com/labra/labra.github.io) and 
 the resulting web page is [here](http://www.di.uniovi.es/~labra). 
 
 


