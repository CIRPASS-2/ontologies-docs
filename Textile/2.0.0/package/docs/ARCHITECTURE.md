# Ontology architecture

The ontology is organised as a network of focused modules. Textile Core provides the central product hierarchy. Structure, Process, Durability, Assessment, Indicator and Context provide reusable domain layers. Associated Materials, Repairability, Recyclability and Textile Substances of Concern extend the core with specialised information. Connector contains patterns that are intentionally shared across modules.

The umbrella ontology `textile-ontology.ttl` is the recommended import for applications that require the complete network. Applications with a narrower scope may import individual modules and their declared dependencies.

## Modelling principles

- OWL classes represent entities, activities, information objects and measurable characteristics.
- SKOS is used for controlled value vocabularies.
- Quantitative observations use explicit value nodes, units and quantity kinds.
- Assessment methods, executions and results are represented separately.
- Substance identity is separated from product-specific presence and regulatory qualification.
- Product events are aligned with the EU DPP Event ontology through a MIREOT subset.

## October 2026 CORE boundary

The runtime has 20 graphs: 13 Textile modules and seven bounded subsets. SOC
owns substance identity, positive presence, criteria and instructions. CON owns
the selected product/presence/concentration relations. P_DPP owns quantitative
property, concentration/threshold anchors and carriers. SI supplies approved units.
Textile owns structured parts/material groups, scopes, threshold value roles,
evaluation, source references and free-text instructions. Generic chemicals and
process executions keep their existing independent types. No general IDENT,
COMP or LCA integration is added. See [migration guidance](CORE_2026_MIGRATION.md).
