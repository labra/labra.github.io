+++

abstract = "Querying the RDF Portal knowledge graph maintained by DBCLS-which aggregates approximately 60 life-science databases-requires proficiency in both SPARQL and database-specific RDF schemas, placing this resource beyond the reach of most researchers. Large Language Models (LLMs) can, in principle, translate natural-language questions into executable SPARQL, but without schema-level context, they frequently fabricate non-existent predicates or fail to resolve entity names to database-specific identifiers. We present TogoMCP, a system that recasts the LLM as a protocol-driven inference engine orchestrating specialized tools via the Model Context Protocol (MCP). Two mechanisms are essential to its design: (i) the MIE (Metadata-Interoperability-Exchange) file, a concise YAML document that dynamically supplies the LLM with each target database's structural and semantic context at query time; and (ii) a two-stage workflow separating entity resolution via external REST APIs from schema-guided SPARQL generation. On a benchmark of 50 biologically grounded questions spanning five types and 23 databases, TogoMCP achieved a large improvement over an unaided baseline (Cohen's $d = 1.82$, Wilcoxon $P > .001$), with win rates exceeding 80% for question types with precise, verifiable answers. An ablation study shows that all component configurations deliver significant improvements, with MIE schema files providing the largest marginal contribution on mean per-question score (Delta = +0.50 relative to a no-MIE condition, two-sided Wilcoxon P = .067; 90% bootstrap CI [+0.04,+0.94] excludes zero); a one-line instruction to load the relevant MIE file recovers the same mean improvement as a full procedural protocol, while the protocol additionally reduces downside risk (loss rate 1.6% vs. 4.8%, Fisher $P = .036$). These results suggest a general design principle: concise, dynamically delivered schema context is more valuable than complex orchestration logic for mean score performance, while procedural guidance plays a complementary role in narrowing variance."
authors = ["Akira R Kinjo", "Yasunori Yamamoto", "Samuel Bustamante-Larriet", "Jose-Emilio Labra-Gayo", "Takatomo Fujisawa"]
date = "2026-07-24"
image_preview = ""
math = false
publication_types = ["2"] 
publication = "Database"
publication_short = "Database"
selected = false
title = "TogoMCP: natural language querying of life-science knowledge graphs via schema-guided LLMs and the Model Context Protocol"
url_code = ""
url_dataset = ""
url_project = "https://togomcp.rdfportal.org/"
url_slides = ""
url_video = ""

tags=["MCP", "Model Context Protocol", "RDF", "TogoMCP", "LLM", "SPARQL", "Knowledge Graphs", "Life Sciences"]

url_pdf = "pdf/2025_MCP_server_tools_shapes.pdf"

[[url_custom]]
name = "Journal"
url = "https://academic.oup.com/database/article/doi/10.1093/database/baag042/8741313"

[[url_custom]]
name = "doi"
url = "https://doi.org/10.1093/database/baag042"

+++