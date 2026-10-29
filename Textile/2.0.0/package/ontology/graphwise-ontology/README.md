# Earlier Graphwise ontology work

Earlier Graphwise ontology work preserved for reference and project continuity. This directory is separate from the current JRC-grounded Textile ontology. The current entry point is [textile-ontology.ttl](../textile-ontology.ttl).

These reference graphs are outside the current package catalogue, import closure, validation scope and 1.1.2 checksum contract. Load them separately; do not combine them indiscriminately with the current model. Original technical content follows.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Reviews and Proposals](#reviews-and-proposals)
    - [UNTP Ontologies Review](#untp-ontologies-review)
    - [Cirpass Ontologies Review](#cirpass-ontologies-review)
    - [MVP Textile Review](#mvp-textile-review)
- [MVP Ontology](#mvp-ontology)

<!-- markdown-toc end -->

# Reviews and Proposals

## UNTP Ontologies Review
We have reviewed comprehensively the United Nations Transparency Protocol (UNTP) ontologies (DPP, DFR etc):
- [UNTP Ontology Review](https://docs.google.com/document/d/1R3yqaYCO3JTpWsIckSzbumzyQgwRvd5X4Ewg-9Ax4yU/edit) (United Nations Transparency Protocol)
  - Issues posted on the [UNTP gitlab at UNICC](https://opensource.unicc.org/un/unece/uncefact/spec-untp/-/issues)
  - [Ontologies saved as turtle](https://github.com/VladimirAlexiev/untp-ontologies) at github

Bibliographic record:
```bibtex
@TechReport{AlexievEtAl-Cirpass2-Review-2025,
  author       = {Vladimir Alexiev and Elio Hbeich and Robert David},
  title        = {UNTP Ontology Review},
  institution  = {Graphwise and GS1},
  year         = 2025,
  month        = {oct},
  url          = {https://docs.google.com/document/d/1R3yqaYCO3JTpWsIckSzbumzyQgwRvd5X4Ewg-9Ax4yU/edit},
  keywords     = {DPP, ontology, ontology review, semantic modeling, UNTP},
  date         = {2025-10-23},
  abstract     = {The document is a review of the United Nations Transparency Protocol (UNTP) ontologies, identifying problems and areas for improvement. Purpose: The review aims to help the EU Cirpass2 project assess UNTP ontology suitability; and to facilitate posting issues to UNTP (at UNICC GitLab). Parts: Describes the current UNTP domains (core, dcc, dfr, dia, dpp, dte). Links to a github repo with Turtle variants and some analysis. Outlines issues in 16 detailed subsections. After general approval at the UNTP mailing list, all the issues were posted on the UNTP gitlab},
}
```

## Cirpass Ontologies Review
We also reviewed the  Cirpass2 ontologies:
- [Cirpass2 Ontology Review: Core and Substances of Concern](https://docs.google.com/document/d/1yGp35EHM_54bdIllKz_iXvdFDFs7ahfm9OOcXjZDUWc/edit)

Bibliographic record:
```bibtex
@TechReport{AlexievEtAl-Cirpass2-Review-2025,
  author       = {Vladimir Alexiev and Elio Hbeich and Ivo Ladenius},
  title        = {Cirpass2 Ontology Review: Core and Substances of Concern},
  institution  = {Graphwise and GS1},
  year         = 2025,
  month        = {oct},
  url          = {https://docs.google.com/document/d/1yGp35EHM_54bdIllKz_iXvdFDFs7ahfm9OOcXjZDUWc/edit},
  keywords     = {Cirpass, Cirpass2, DPP, ontology, ontology review, semantic modeling, UNTP},
  date         = {2025-10-23},
  abstract     = {This document is a review of the Cirpass2 core ontology, which is the first iteration of the EU Digital Product Passport (DPP) core ontology proposal. The review highlights several issues, including: Lack of reuse of UNTP ontologies: The document suggests that reusing UNTP ontologies would save development time and broaden the global reach of Cirpass DPP ontologies. Namespace and Naming problems: Issues such as using http instead of https for namespaces, non-permanent URLs, inconsistent spelling, and poorly named classes and properties. Ontology Metadata issues: Problems with author representation, empty contributor values, and comments attached to blank nodes. Modularity Errors: The core ontology is formed by concatenating modules, leading to redundant metadata and version information. The reviewer suggests using owl:import and potentially a single namespace for better modularity. Syntax Errors and Typos: Examples include mistyped ontology URLs and spelling mistakes. Description Errors: Comments with incorrect language tags, unclosed parentheses, misspellings, poor line breaks, and imprecise or misleading descriptions. It also suggests moving source information to dc:source and links to rdfs:seeAlso. Descriptive Omissions: Many terms lack rdfs:label and rdfs:comment, making them unclear. External Property Errors: Misspelling of skos:exactMatch and improper redefinition of owl:topDataProperty. Modeling Problems and Omissions: Issues with rdfs:subPropertyOf owl:topObjectProperty declarations, unelaborated dimensions and quality indicators, role modeling problems, missing links for permissions, no relation to Verifiable Credentials, inverse property naming, and failure to reuse GS1 Digital Link types. QuantitativeProductProperty Modeling Problems: These properties are often not elaborated, and there's a need for a more flexible way to capture what is being measured. It also points out that QuantityValue lacks defined MeasurementUnit and QuantityKind, suggesting the use of QUDT classes. Identifiers Not Modeled Adequately: Inconsistent ID property ranges and a lack of clear structure for identifier schemes. Recommendations include using adms:Identifier and considering W3C DIDs and/or GS1 identifiers. Unwarranted Union Datatypes: The use of union datatypes for uniqueProductID and webLink is considered unwarranted. Undefined classes and properties: The ontology includes undefined classes and properties like Type, hasType, and participatesInEvent. Duplication of annotation properties: Due to merging modules, standard annotation properties are defined multiple times.},
}
```

## MVP Textile Review
The [MVP Textile DPP](https://dpp.vocabulary-hub.eu/message-model/MessageModel_b564fa30-31bc-4849-bea9-3712ba84b6cf) is a data ("message") model at the [CIRPASS-2 Digital Product Passport Vocabulary Hub](https://dpp.vocabulary-hub.eu/)
that describes a tentative "minimum viable model" for Cirpass Textile DPPs.
The MVP Textile DPP so far has 2 versions:
- Version 1 was a flat data model from the Kezzler pilot, ingested "as-is" into the DPP Vocabulary Hub
- Version 2 (2025-12-04) transformed the flat v1 model into a hierarchical model, but IMHO doesn't go nearly far enough.

I downloaded MVP v2 as a sheet from [CP2 DPP textile data.xlsx](https://dpp.vocabulary-hub.eu/api/file-object/FileObject_b433e028-8486-4d65-a7a7-8d42854f680b/download/CP2%20DPP%20textile%20data.xlsx), and made:
- Sheet [MVP Textile DPP Review](https://docs.google.com/spreadsheets/d/1NsB8gzLI9XmpU1oO3jQexFkmYQwyDMar8C6R2X7EnSg/edit?gid=0#gid=0) with detailed comments by Graphwise and GS1
  - A very substantive discussion wit Cirpass project partners has ensued in additional columns of that sheet
  - Some rows link to [issues](https://github.com/CIRPASS-2/dpp-textiles/issues)
- Document [MVP Textile DPP Review and Proposal](https://docs.google.com/document/d/1pv0GGC3Wfs-U33O-EdtuC-_30z3b0e1Gu3O-OwGfIPo/edit), Vladimir Alexiev, 2026-01-09. It includes:
  - Higher-level critique of some aspects
  - Some proposed generic concepts, most importantly 
    - `Identifier` (and `IdentifierSchme`)
    - `Classification` (and `ClassificationScheme`)
    - `ProductAgentRelationOrEvent`

# MVP Ontology
[ontology.ttl](ontology.ttl) is an initial version of the MVP ontology.

Authors:
- Viktor Senderov [0000-0003-3340-5963](https://orcid.org/0000-0003-3340-5963): started and added StandardsMap concepts
- Robert David [0000-0002-3244-5341](https://orcid.org/0000-0002-3244-5341): loading in GraphDB and PoolParty
- Vladimir Alexiev [0000-0001-7508-7428](https://orcid.org/0000-0001-7508-7428): initial idea and overall editing
- Albin Ahmeti [0000-0001-8766-4069](https://orcid.org/0000-0001-8766-4069): LLM ontology generation from the initial idea

The ontology and related taxonomies:
- Are loaded in GraphDB at TODO
- Can be viewd in PoolParty at TODO
