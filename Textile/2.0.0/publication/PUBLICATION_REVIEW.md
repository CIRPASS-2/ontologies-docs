# Textile Ontology 2.0.0 documentation publication review

This is local preparation for a dedicated documentation PR. Nothing has been
pushed, submitted as a remote PR, merged, tagged, released or deployed.

Source: CIRPASS-2/ontologie-textiles at
`a2bc2642627bf9223b1e39dc54a4e45c233e9232`,
[source PR #19](https://github.com/CIRPASS-2/ontologie-textiles/pull/19).
Documentation baseline: `5c76af4448093cdc9e57d2bb3bfdf1416b8876eb`.
Local documentation branch: `docs/textile-2.0.0`.

## Scope and bytes

The committed-source transfer inventory records **1,290 exact file copies**:
469 primary WIDOCO files, all 27 diagram files, 791 current-package members and
three separately inventoried reference files. Their total uncompressed file
content is **121,026,018 bytes**. The validation-ready package is **794 files**,
**86,887,100 bytes**: 791 checksum-contract members plus the three attributed
references. SHA256SUMS has 790 entries because it does not checksum itself.
No ZIP was built, and these byte totals are not compressed archive sizes.

Every source asset was read from committed Git blobs at the approved SHA,
never from the source working tree. The untracked source publication plan is
excluded. The complete package keeps its original paths, manifest and checksums;
it intentionally contains its own documentation and diagrams in addition to the
primary Pages copies. All original licences, source notices and references remain.
The version-local .gitattributes disables text normalization to preserve bytes.

All added files are below `Textile/2.0.0/`. Outside that tree, only the Textile
regions of `index.html` and `ontologies.html` change. All 1,117 other previously
tracked files are preserved, including CORE, Battery, Tyre, legacy Textile,
.nojekyll and LICENSE. All old portal Textile links remain. The original catalogue
and its original generation-date/count label remain as a historical snapshot;
the new Textile group explicitly distinguishes the added 2.0.0 pages.

The portal separates the 2.0.0 candidate's October 2026 CORE alignment (including
SOC 2.2.0) from independently published CORE documentation and historical Textile
1.1.2. Seven direct package-MIREOT links avoid directory listings. Textile licensing
and pending persistent-IRI coordination are explicit. No page claims that Textile
w3id resolution is deployed.

## Validation and expected URLs

[Machine-readable results](validation-results.json) record actual loopback HTTP
serving with the `/ontologies-docs/` prefix, directory indexes disabled and exact
case-sensitive paths enforced. All 1,290 copied files must return HTTP 200 and the
expected committed hash. The package structural validator and its original
manifest/SHA-256 contract must pass. All 48 HTTP RDF exports must be graph-isomorphic
to canonical sources.

Headless Microsoft Edge is driven through Chrome DevTools Protocol. All twelve
module pages must render, all 84 AJAX sections must return HTTP 200, every local
annotation-property anchor must exist uniquely, and all twelve WebVOWL pages must
load their local JSON and render SVG graph nodes. Empty namespace fragments remain
empty exactly as committed; successful zero-byte HTTP responses are distinguished
from failed loading. Rendered DOM links and fragment targets, local CSS URL targets,
and all 37 prior sector landing pages are checked over HTTP.

Expected deployment root (not deployed by this task):
`https://cirpass-2.github.io/ontologies-docs/Textile/2.0.0/`.
Each module is at `<module>/index-en.html`, its graph at
`<module>/webvowl/index.html`, and downloads at `<module>/ontology.ttl`,
`ontology.owl`, `ontology.nt` and `ontology.jsonld`. Diagrams are under `diagrams/`;
the 794-file package is under `package/`. Every exact percent-encoded expected URL
is included in [the transfer inventory](transfer-inventory.json).

For a new local validation, from the documentation repository root, install
`Textile/2.0.0/publication/requirements-browser.txt` in an isolated Python environment
and run:

```powershell
python -B Textile/2.0.0/publication/validate.py
```

Edge's default Windows installation is used unless `--edge` is supplied. An
isolated `websocket-client` installation can be supplied through `--browser-tools`.
The validator serves only loopback HTTP and closes its isolated browser afterward.
`prepare.py` is an assembly tool for a fresh branch based on the recorded docs
baseline, not a command to regenerate approved source ontologies.

External DNS is disabled in browser runs to isolate local publication assets.
External badges, citations, ReSpec delivery, remote ontology loading and public
resolver behavior are not claimed verified. Production Pages/CDN behavior and
persistent-IRI routing need separately authorized post-deployment checks. The
unchanged source's 205-test evidence is included; the semantic suite was not rerun
for this byte-preserving documentation transfer.

## Approval boundary

Authenticated read-only settings inspection confirmed legacy GitHub Pages from
`main`, folder `/`, at `https://cirpass-2.github.io/ontologies-docs/`, with no CNAME.
The remote main SHA was fetched rather than assumed. The only listed workflow is
the existing dynamic pages-build-deployment workflow; it is not changed here.
Merging into docs main would trigger publication. Source PR review/merge,
documentation-branch push, remote documentation PR creation and any Pages
publication require the owner's next authorization. Resolver deployment remains
with the existing namespace maintainers. Existing CORE redirects are untouched.

[Prepared PR description](PR_DESCRIPTION.md). A local commit records this review;
its SHA is reported to the owner separately, avoiding a self-referential hash.
