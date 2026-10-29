from __future__ import annotations

from html import escape
from pathlib import Path
import re

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS


ROOT = Path(__file__).resolve().parents[1]

ONTOLOGY_DIR = ROOT / "ontology"
TEMPLATE = ROOT / "widoco" / "index-template.html"
OUTPUT = ROOT / "docs" / "widoco" / "index.html"

MODULES = (
    "core",
    "connector",
    "associated-materials",
    "structure",
    "process",
    "context",
    "durability",
    "assessment",
    "indicator",
    "repairability",
    "recyclability",
    "soc",
)

SHORT_DESCRIPTIONS = {
    "core": (
        "Core textile product concepts, fibre composition "
        "and controlled textile vocabularies."
    ),
    "connector": (
        "Shared modelling infrastructure for quantitative values, "
        "provenance and cross-module patterns."
    ),
    "associated-materials": (
        "Non-textile components, packaging materials "
        "and textile chemical classifications."
    ),
    "structure": (
        "Characteristics of textile fibres, yarns, "
        "fabrics and assemblies."
    ),
    "process": (
        "Textile processes, executions, parameters "
        "and target specifications."
    ),
    "context": (
        "Use, care, storage, environmental exposure "
        "and user-related context."
    ),
    "durability": (
        "Durability characteristics, degradation phenomena "
        "and failure modes."
    ),
    "assessment": (
        "Assessment methods, executions, conditions, "
        "results and thresholds."
    ),
    "indicator": (
        "Derived and interpretive textile durability "
        "and use-related indicators."
    ),
    "repairability": (
        "Repairability evidence, services, design features "
        "and life-extension interventions."
    ),
    "recyclability": (
        "Route-specific recyclability, recycling events, "
        "recovered materials and recycled content."
    ),
    "soc": (
        "Textile-specific substance-of-concern presence, "
        "location, concentration and lifecycle information."
    ),
}


def first_text(graph: Graph, subject: URIRef, predicate) -> str:
    values = list(graph.objects(subject, predicate))

    if not values:
        return ""

    return str(values[0])


def ontology_subject(graph: Graph, path: Path) -> URIRef:
    subjects = [
        subject
        for subject in graph.subjects(RDF.type, OWL.Ontology)
        if isinstance(subject, URIRef)
    ]

    if len(subjects) != 1:
        raise RuntimeError(
            f"{path}: expected exactly one owl:Ontology, "
            f"found {len(subjects)}"
        )

    return subjects[0]


def ontology_version(graph: Graph, subject: URIRef) -> str:
    version_info = first_text(
        graph,
        subject,
        OWL.versionInfo,
    )

    if version_info:
        match = re.search(
            r"(\d+\.\d+\.\d+(?:[-A-Za-z0-9.]*)?)",
            version_info,
        )

        if match:
            return match.group(1)

        return version_info

    version_iris = list(
        graph.objects(subject, OWL.versionIRI)
    )

    if version_iris:
        return str(version_iris[0]).rstrip("/").split("/")[-1]

    return "—"


def entity_counts(graph: Graph) -> tuple[int, int, int, int]:
    classes = {
        subject
        for subject in graph.subjects(RDF.type, OWL.Class)
        if isinstance(subject, URIRef)
    }

    object_properties = {
        subject
        for subject in graph.subjects(
            RDF.type,
            OWL.ObjectProperty,
        )
        if isinstance(subject, URIRef)
    }

    data_properties = {
        subject
        for subject in graph.subjects(
            RDF.type,
            OWL.DatatypeProperty,
        )
        if isinstance(subject, URIRef)
    }

    individuals = {
        subject
        for subject in graph.subjects(
            RDF.type,
            OWL.NamedIndividual,
        )
        if isinstance(subject, URIRef)
    }

    # SKOS concepts behave as named controlled-vocabulary
    # individuals in the textile modules even when they are
    # not explicitly typed owl:NamedIndividual.
    individuals.update(
        subject
        for subject in graph.subjects(
            RDF.type,
            SKOS.Concept,
        )
        if isinstance(subject, URIRef)
    )

    individuals.difference_update(classes)
    individuals.difference_update(object_properties)
    individuals.difference_update(data_properties)

    return (
        len(classes),
        len(object_properties),
        len(data_properties),
        len(individuals),
    )


def module_row(slug: str) -> tuple[str, dict]:
    path = ONTOLOGY_DIR / f"textile-{slug}.ttl"

    if not path.is_file():
        raise FileNotFoundError(path)

    graph = Graph()
    graph.parse(path, format="turtle")

    ontology = ontology_subject(graph, path)

    title = (
        first_text(graph, ontology, DCTERMS.title)
        or first_text(graph, ontology, RDFS.label)
        or slug
    )

    description = SHORT_DESCRIPTIONS.get(
    slug,
    first_text(
        graph,
        ontology,
        DCTERMS.description,
    ),
)

    version = ontology_version(
        graph,
        ontology,
    )

    (
        class_count,
        object_property_count,
        data_property_count,
        individual_count,
    ) = entity_counts(graph)

    ontology_iri = str(ontology)

    row = f"""
<tr class="module-row">
  <td>
    <a
      class="ontology-title"
      href="{escape(slug)}/index-en.html">
      {escape(title)}
    </a>

    <p class="ontology-description">
      {escape(description)}
    </p>

    <div class="ontology-iri">
      <a href="{escape(ontology_iri)}">
        {escape(ontology_iri)}
      </a>
    </div>
  </td>

  <td class="version">
    {escape(version)}
  </td>

  <td class="number">
    {class_count}
  </td>

  <td class="number">
    {object_property_count}
  </td>

  <td class="number">
    {data_property_count}
  </td>

  <td class="number">
    {individual_count}
  </td>

  <td>
    <a href="{escape(slug)}/webvowl/index.html">
      WebVOWL
    </a>
  </td>
</tr>
""".strip()

    stats = {
        "module": slug,
        "version": version,
        "classes": class_count,
        "object_properties": object_property_count,
        "data_properties": data_property_count,
        "individuals": individual_count,
    }

    return row, stats


def network_metadata() -> tuple[str, str, str, str]:
    path = ONTOLOGY_DIR / "textile-ontology.ttl"

    graph = Graph()
    graph.parse(path, format="turtle")

    ontology = ontology_subject(
        graph,
        path,
    )

    title = (
        first_text(graph, ontology, DCTERMS.title)
        or first_text(graph, ontology, RDFS.label)
        or "CIRPASS Textile Ontology"
    )

    version = ontology_version(
        graph,
        ontology,
    )

    return (
        title,
        version,
        str(ontology),
        ", ".join(sorted(str(person) for person in graph.objects(ontology, DCTERMS.creator))),
    )


def main() -> None:
    if not TEMPLATE.is_file():
        raise FileNotFoundError(TEMPLATE)

    rows = []
    stats = []

    for slug in MODULES:
        row, module_stats = module_row(slug)

        rows.append(row)
        stats.append(module_stats)

    (
        network_title,
        network_version,
        network_iri,
        network_creators,
    ) = network_metadata()

    html = TEMPLATE.read_text(
        encoding="utf-8"
    )

    replacements = {
        "{{MODULE_COUNT}}": str(len(MODULES)),
        "{{NETWORK_TITLE}}": escape(network_title),
        "{{NETWORK_VERSION}}": escape(network_version),
        "{{NETWORK_IRI}}": escape(network_iri),
        "{{NETWORK_CREATORS}}": escape(network_creators),
        "{{MODULE_ROWS}}": "\n\n".join(rows),
    }

    for marker, value in replacements.items():
        if marker not in html:
            raise RuntimeError(
                f"Missing template marker: {marker}"
            )

        html = html.replace(
            marker,
            value,
        )

    unresolved = re.findall(
        r"\{\{[A-Z0-9_]+\}\}",
        html,
    )

    if unresolved:
        raise RuntimeError(
            "Unresolved template markers: "
            + ", ".join(sorted(set(unresolved)))
        )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        html,
        encoding="utf-8",
        newline="\n",
    )

    print()
    print("EU DPP Textile Ontology landing page")
    print("=" * 48)

    for item in stats:
        print(
            f"{item['module']:<22} "
            f"v{item['version']:<8} "
            f"C={item['classes']:<3} "
            f"OP={item['object_properties']:<3} "
            f"DP={item['data_properties']:<3} "
            f"I={item['individuals']:<3}"
        )

    print()
    print(f"Modules: {len(MODULES)}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
