# Publish CIRPASS-2 Textile Ontology 2.0.0 documentation

Prepare versioned documentation from validated source candidate
[`a2bc264`](https://github.com/CIRPASS-2/ontologie-textiles/commit/a2bc2642627bf9223b1e39dc54a4e45c233e9232),
reviewed in [source PR #19](https://github.com/CIRPASS-2/ontologie-textiles/pull/19).

- Add `Textile/2.0.0/` with the network landing page, all twelve WIDOCO modules,
  complete assets and AJAX sections, 48 RDF downloads, WebVOWL data, 27 diagrams,
  and the manifest-selected package plus three attributed reference files.
- Copy 1,290 source assets byte-for-byte (121,026,018 bytes). The package comprises
  794 files (86,887,100 bytes), retaining the 791-member checksum contract.
- Update only Textile regions of the two root portal pages. Preserve historical
  Textile 1.1.2 and all legacy links. No CORE, Battery or Tyre ontology documentation,
  global navigation, licence or site infrastructure is replaced.
- Distinguish the October 2026 CORE alignment, package-specific MIREOT subsets and
  pending resolver coordination. Preserve all source attribution and licence notices.

Local validation uses HTTP at the real `/ontologies-docs/` base path and a headless
browser: twelve module pages, 84 AJAX sections, all annotation anchors, twelve
rendered WebVOWL graphs, 48 graph-isomorphic RDF exports, all committed copy hashes,
manifest/SHA-256 integrity and zero broken local links. All 37 previous sector
landing pages still return HTTP 200. The source candidate's 205-test records are
included unchanged; they are not represented as a fresh semantic test run here.

Persistent Textile IRI resolution under `w3id.org/eudpp` is being coordinated
separately within CIRPASS-2. This documentation PR does not deploy HTTP redirects
or content negotiation.

See `Textile/2.0.0/publication/PUBLICATION_REVIEW.md`, `transfer-inventory.json` and
`validation-results.json` for the exact transfer scope, expected URLs, checks and
limitations. GitHub Pages publishes from docs `main` at `/`; merge timing therefore
requires explicit publication approval. Local preparation does not deploy Pages.
