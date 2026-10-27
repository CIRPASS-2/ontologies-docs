# WIDOCO documentation sources

This directory contains the human-maintained sources used to generate
the CIRPASS-2 Textile ontology documentation.

## Structure

- `index-template.html` — template for the ontology-network landing page.
- `sections/<module>/` — human-authored WIDOCO editorial sections for each
  textile ontology module.

Generated documentation is written to `docs/widoco/`.

## Requirements

Documentation generation has been validated with:

- Java 17
- WIDOCO 1.4.25, JDK 17 distribution
- JAXB API 2.3.1
- Python with `rdflib`

The following local files are expected:

- `tools/widoco-1.4.25_JDK-17.jar`
- `tools/jaxb-api-2.3.1.jar`

The JAR files are local tooling dependencies and are intentionally excluded
from Git.

## Generate the documentation

From the repository root on Windows PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File ".\scripts\generate-widoco-docs.ps1"