+++

abstract = "We discuss Shape Expressions (ShEx), a concise, formal, modeling and validation language for RDF structures. For instance, a Shape Expression could prescribe that subjects in a given RDF graph that fall into the shape Paper are expected to have a section called Abstract, and any ShEx implementation can conform whether that is indeed the case for all such subjects within a given graph or subgraph. There are currently five actively maintained ShEx implementations. We discuss how we use the JavaScript, Scala and Python implementations in RDF data validation work flows in distinct, applied contexts. We present examples of how ShEx can be used to model and validate data from two different sources, the domain-specic Fast Healthcare Interoperability Resources (FHIR) and the domain-generic Wikidata knowledge base, which is the linked database built and maintained by the Wikimedia Foundation as a sister project to Wikipedia. Example projects that are using Wikidata as a data curation platform are presented as well, along with ways in which they are using ShEx for modeling and validation. When reusing RDF graphs created by others, it is important to know how the data is represented. Current practices of using human-readable descriptions or ontologies to communicate data structures often lack sufficient precision for data consumers to quickly and easily understand data representation details.  We provide concrete examples of how we use ShEx as a constraint and validation language that allows humans and machines to communicate unambiguously about data assets. We use ShEx to exchange and understand data models of different origins, and to express a shared model of a resource's footprint in a Linked Data source. We also use ShEx to agilely develop data models, test them against sample data, and revise or refine them. The expressivity of ShEx allows us to catch disagreement, inconsistencies, or errors eficiently, both at the time of input, and through batch inspections. ShEx addresses the need of the Semantic Web community to ensure data quality for RDF graphs. It is currently being used in the development of FHIR/RDF. The language is sufficiently expressive to capture constraints in FHIR, and the intuitive syntax helps people to quickly grasp the range of conformant documents. The publication work flow for FHIR tests all of these examples against the ShEx schemas, catching non-conformant data before they reach the public. ShEx is also currently used in Wikidata projects such as Gene Wiki and WikiCite to develop quality-control pipelines to maintain data integrity and incorporate or harmonize differences in data across different parts of the pipelines."
authors = ["Katherine Thornton", "Harold Solbrig", "Gregory Stupp", "Jose Emilio Labra Gayo", "Daniel Mietchen", "Eric Prud'Hommeaux", "Andra Waagmeester"]
date = "2019-06-04"
image_preview = ""
math = false
publication_types = ["1"]
publication = "In *Extended Semantic Web Conference*, ESWC2019."
publication_short = ""
selected = true
title = "Using Shape Expressions (ShEx) to Share RDF Data Models and to Guide Curation with Rigorous Validation"
url_code = ""
url_dataset = ""
url_pdf = "pdf/2019_eswc_ShEx.pdf"
url_project = ""
url_slides = ""
url_video = ""

tags=["RDF", "ShEx", "RDF-validation"]

+++


