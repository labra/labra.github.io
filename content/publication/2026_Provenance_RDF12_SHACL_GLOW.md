+++

abstract = "Knowledge Graph augmentation from unstructured text requires extracted assertions to be aligned with an ontology, semantically checked, and linked to their source. Large Language Models (LLMs) can automate extraction, but may generate unsupported, duplicated, or structurally inconsistent knowledge. We propose an agentic framework in which an LLM interacts with a semantic backend through the Model Context Protocol (MCP) to explore an existing graph, generate RDF 1.2 annotated statements, and use SHACL validation to iteratively correct candidate assertions before integration. Statement annotations record the generating model, the source document, and the validation method, while structural and provenance constraints are enforced through rudof. A pilot prototype implements the core LLM–MCP–SHACL workflow using a fragment of the FoCOSA ontology and deepseek-chat, evaluated on a short corpus describing six foods across ten dietary categories. The system produced typed and labelled individuals for all six foods, linked them only to the four diet classes declared in the ontology, correctly omitted the undeclared categories, and emitted a graph that independently passed SHACL validation."

authors = ["Alex Vigani", "Samuel Bustamante-Larriet", "Nina Hosseini-Kivanani", "Jose Emilio Labra Gayo", "Anisa Rula"]

date = "2026-10-28"
image_preview = ""
math = false
publication_types = ["1"]
publication = "*Graph-enhanced LLMs for trustwOrthy Web data management*, GLOW co-located with *International Semantic Web Conference*, ISWC26"
publication_short = ""
selected = true
title = "A Provenance-Aware Agentic Framework for Knowledge Graph Augmentation Using RDF 1.2 and SHACL"

url_code = "https://github.com/rudof-project/rudof"
url_dataset = ""
url_pdf = "pdf/2026_Provenance_RDF12_SHACL_GLOW.pdf"

url_project = ""
url_slides = ""
url_video = ""

[[url_custom]]
name = "Conference"
url = "https://glow-workshop.github.io/iswc2026/"

tags=[ "Knowledge Graph augmentation", "Large Language Models", "agentic systems", "data provenance", "RDF 1.2", "SHACL validation", "Model Context Protocol", "semantic data integration" ]


+++


