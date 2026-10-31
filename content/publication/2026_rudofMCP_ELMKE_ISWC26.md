+++

abstract = "The convergence between Large Language Models (LLMs) and Knowledge Graphs (KGs) constitutes a promising research frontier, constrained by the limited ability of LLMs to reason directly over the structure of KGs. Existing Model Context Protocol (MCP) servers for Knowledge Graph Engineering only partially address this problem, as they specialize in a single capability. This work presents rudofMCP, an MCP server that exposes the main capabilities of the rudof library (reading, writing and converting between RDF formats; node inspection; SPARQL query execution; ShEx, SHACL validation) to any client that supports the protocol, allowing models to delegate Knowledge Graph Engineering operations to a specialized system while leaving an explicit, inspectable audit trail of every invoked operation and its result. The effect of the server on model performance is measured through an adaptation of the LLM-KG-Bench 3.0 benchmark. The adaptation adds a new agentic MCP connector and a new ShEx validation task. A single model is evaluated across two arms (without and with access to the MCP server) and the results are analyzed with non-parametric rank tests and Cliff’s delta as the effect size. The results show that the effect is task-dependent: large improvements when the task admits delegating the work to a formal  operation, deterioration when conciseness is required, and, in all cases, an additional cost in latency and token consumption."

authors = ["Samuel Bustamante-Larriet", "Álvaro García-Fernández", "Jose Emilio Labra Gayo"]

date = "2026-10-28"
image_preview = ""
math = false
publication_types = ["1"]
publication = "*ELMKE: Evaluation of Language Models in Knowledge Engineering*, co-located with *International Semantic Web Conference*, ISWC26"
publication_short = ""
selected = true
title = "rudofMCP: A Model Context Protocol Server Exposing Knowledge Graph Engineering Capabilities to Large Language Models"

url_code = "https://github.com/rudof-project/rudof"
url_dataset = ""
url_pdf = "pdf/2026_rudofMCP_ELMKE_ISWC_2026.pdf"

url_project = "https://github.com/rudof-project/rudof"
url_slides = ""
url_video = ""

[[url_custom]]
name = "Conference"
url = "https://sites.google.com/view/elmke/2026"

tags=["Large Language Models", "Knowledge Graphs", "Model Context Protocol", "RDF", "SPARQL", "ShEx", "SHACL"]


+++


