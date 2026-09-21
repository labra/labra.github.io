+++

abstract = "RDF 1.2 introduces statement-level constructs, such as triple terms, reifiers, and descriptions, that pose new challenges for transforming RDF data into labeled property graphs (LPGs). This work presents and compares three algorithms for translating RDF 1.2 data into LPGs, each interpreting a different amount of the RDF 1.2 reification vocabulary. Algorithm Structural interprets no vocabulary and losslessly supports arbitrary RDF 1.2 graphs by representing triple terms explicitly as nodes; Direct interprets rdf:reifies to recover annotated edges while preserving reifiers as graph objects; and Fold additionally folds reifier descriptions into edge properties, resulting in a more concise, albeit lossy, LPG representation. We define the three translations, analyze which class of RDF 1.2 graphs each preserves, and experimentally evaluate their implementations. The experiments confirm the predicted trade-offs: all variants scale linearly on the tested workloads, the generality of Structural has no runtime penalty, and folding descriptions into edge records can significantly reduce the number of edges on description-heavy data."

authors = ["Maxime Jakubowski", "Dominik Tomaszuk", "Daniel Fernández-Álvarez", "Ruben Taelman", "Ruben Dedecker", "Jose Emilio Labra Gayo", "Katja Hose"]

date = "2026-09-05"
image_preview = ""
math = false
publication_types = ["1"]
publication = "*2nd International Workshop on Data Management for Knowledge Graphs*, DMKG26 co-located with *International Semantic Web Conference*, ISWC26"
publication_short = ""
selected = true
title = "Translating RDF 1.2 Graphs to Property Graphs"

url_code = "https://github.com/RDF-PG-Interoperability/rdf12-to-pg"
url_dataset = ""
url_pdf = "pdf/2026_RDF12_PG_DMKG.pdf"

url_project = ""
url_slides = ""
url_video = ""

[[url_custom]]
name = "Conference"
url = "https://dmkg-workshop.github.io/2026/"

tags=["RDF", "Property graphs", "Data modeling"]


+++


