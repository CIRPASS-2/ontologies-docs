# Textile 2.0.0 MAT alignment documentation update

Source candidate: `e9cf8542d104fefccf339761d138fcf9c32bc904`, successfully pushed to
[source PR #19](https://github.com/CIRPASS-2/ontologie-textiles/pull/19).
This updates the existing [documentation PR #1](https://github.com/CIRPASS-2/ontologies-docs/pull/1)
from documentation commit `9f859e801e8d64afdfee48c6a402522069996c35`.

The only canonical RDF additions are the approved FibreTypeConcept subclass of
CORE MaterialType and hasFibreType subproperty of CORE hasMaterialType.
All 22 fibre concepts infer MAT typing. The source regression suite passed:
221 tests, zero assertion failures, zero setup errors, 12 deprecation warnings.
Both public validation modes passed. Source evidence is copied in the package.

## Exact committed transfer

The transfer inventory records **1,295 exact file copies**,
**120,716,465 bytes**, read from committed source Git blobs.
There are 469 primary WIDOCO files,
27 diagram files and 799 package files.
The package checksum contract contains 796 members
and 795 checksum entries; three separately
inventoried reference files retain their source bytes.

All changed files remain within `Textile/2.0.0/`. Root portals, navigation,
historical Textile and CORE/Battery/Tyre documentation remain byte-identical to
the previous documentation commit. The public base remains
`https://cirpass-2.github.io/ontologies-docs/Textile/2.0.0/`.

The assembly tool's `--update` mode verifies every prior inventory hash before
overwriting approved assets. The validator additionally compares every tracked
file outside the versioned Textile tree with the previous documentation commit.

## Validation

Run the existing HTTP/browser validator with its pinned websocket dependency:

```powershell
python -B Textile/2.0.0/publication/validate.py --browser-tools <dependency-directory> --temp-root <writable-directory>
```

The temporary-root option avoids the inaccessible system temporary storage
encountered during source validation. It does not suppress any browser check.
All 1,295 copied files must pass HTTP hashes; all twelve module pages, 84 AJAX
sections and twelve rendered WebVOWL graphs must load. All 48 RDF exports must
be isomorphic to canonical source graphs. Local links, CSS targets, legacy pages,
source creators, version identities and package integrity remain checked.
Exact results are recorded in `validation-results.json` after the run.

External DNS is disabled in browser tests. External badges, citations, ReSpec,
remote ontology loading, production CDN behavior and persistent IRI resolution
are outside these local checks. OWL RL tests are not a complete OWL DL proof.
No merge, release, deployment or persistent redirect change is performed.
The existing documentation branch push is owner-authorized after validation.

## Preservation contract and completed validation

Repository preservation compares protected path names, modes and Git object IDs
in HEAD and the index with the recorded baseline. Unauthorized committed or
staged changes, additions, deletions and conflicts fail. Git also checks for
unstaged content edits and unauthorized untracked files. Windows checkout EOL
representation is separate from repository identity; no protected file is
rewritten or normalized. All 1,119 protected repository entries are unchanged.

Textile publication integrity remains stricter at the byte level: all 1,295
source-derived assets match exact Git blobs from source commit
`e9cf8542d104fefccf339761d138fcf9c32bc904` and their SHA-256 hashes, both on disk
and through HTTP. No byte normalization or asset exceptions are allowed.

All 12 preservation regression cases pass across LF and CRLF checkouts. Controls
reject genuine unstaged edits, staged edits even after restoring the working
file, committed edits, staged additions and staged deletions.

The complete HTTP/browser workflow passed: all twelve module pages, 84 AJAX
sections, twelve rendered WebVOWL graphs, 48 graph-isomorphic RDF exports,
1,295 HTTP hash checks, the 796-member manifest with 795 checksum rows, 7,192
local DOM references and 6,446 fragments. Zero local link errors occurred; all
37 historical/other-sector landing pages returned HTTP 200. Both MAT bridges
are present in canonical Core RDF, WIDOCO HTML and WebVOWL relationship data.

Remote source PR #19 was verified at the exact required source commit before
preparing this documentation commit. All 43 changed files are restricted to
`Textile/2.0.0/`; changed-files.txt is the exact reviewed list. Source ontologies,
protected sectors, historical versions, root navigation, configuration and
redirects are unchanged. validation-results.json records the pre-commit test
snapshot; the final commit SHA and push result are reported separately.

Technical validation is complete and the existing PR is ready for human review.
No merge, release, tag, deployment or persistent resolver change is authorized
or performed by this task. External DNS/CDN and public resolver behavior remain
outside local validation. OWL RL validation is not a complete OWL DL proof.
