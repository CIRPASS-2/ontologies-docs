# Final Textile 2.0.0 source synchronization

Source candidate: `3a77b6dc69cc8c1778e340f7afd1300639cb9378`, pushed to
[source PR #19](https://github.com/CIRPASS-2/ontologie-textiles/pull/19).
This updates the existing [documentation PR #1](https://github.com/CIRPASS-2/ontologies-docs/pull/1)
on `docs/textile-2.0.0`, from documentation baseline `74db33c0774101a18fc120c7dced9b2f27313b64`.

The accepted MAT bridges, two modelling-note replacements, three modified-date
replacements and obsolete local closeMatch declaration removal are copied
without further modelling changes. The final P1 changelog correction records
these corrections and links the finalization evidence. P2 is not implemented.
The unchanged pre-MAT baseline and complete seven-addition/six-removal RDF delta
are documented in [the source finalization record](../package/migration/PUBLICATION_CANDIDATE_FINALIZATION.md).

The source full suite passed **232 tests**, with zero assertion failures,
zero setup errors and 12 existing rdflib deprecation warnings. Both normal
full publication modes passed. Source validation evidence is copied unchanged.

## Exact committed transfer

The transfer inventory records **1,299 exact file copies**,
**120,821,879 bytes**, read from committed source Git blobs:
469 primary WIDOCO files, 27 diagram files,
800 package-contract members and three separately
inventoried reference files. The package has **800 manifest members and
799 SHA-256 rows**. Copied files are never manually edited or normalized.

All changes are restricted to `Textile/2.0.0/`. All **1,119 protected
repository entries** outside that tree retain baseline HEAD/index identity;
Git reports no protected working-tree changes. Root portals, historical Textile,
CORE/Battery/Tyre resources, public paths, redirects and configuration are
unchanged from the preceding documentation commit.

The established update workflow verifies every prior transfer hash before
copying the pinned source commit. Its exact source revision, update baseline
and transfer-count expectations are advanced for this synchronization;
preservation rules and the twelve LF/CRLF regression cases are unchanged.

## Completed validation

All **12 preservation tests** pass. The complete existing HTTP/browser workflow
passes: 1,299 HTTP asset hashes, all 48 graph-equivalent RDF exports,
twelve rendered module pages, 84 AJAX sections and
12 rendered WebVOWL graphs. Browser validation checks
7,188 local DOM references and 6,442 fragment targets,
with zero local link errors. All 37 historical/other-sector landing pages
return HTTP 200. Package structural validation and all checksums pass.

Reproduce with the existing preservation tests and HTTP/browser validator:

```powershell
python -B -m pytest Textile/2.0.0/publication/test_preservation.py -p no:cacheprovider
python -B Textile/2.0.0/publication/validate.py --browser-tools <dependency-directory> --temp-root <writable-directory>
```

The pinned websocket dependency is listed in requirements-browser.txt.
`transfer-inventory.json` and `validation-results.json` record exact results.
`changed-files.txt` lists the complete reviewed change scope.

## Review and publication state

Technical validation is complete; the existing PR is ready for human review.
The validation JSON records the pre-commit snapshot. Final commit hashes and
push results are reported separately, rather than rewriting that evidence.

External DNS is disabled in browser tests; external citations, remote ontology
loading, production CDN behavior and persistent IRI behavior are not claimed
verified. Previously documented source reasoner/profile limits remain unchanged.
No merge, tag, release, deployment or persistent redirect change is performed.
Only the existing source and documentation working branches are pushed.
