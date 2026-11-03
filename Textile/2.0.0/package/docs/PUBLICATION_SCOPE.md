# Publication scope and historical preservation

This local 2.0.0 candidate comprises 13 Textile modules and seven bounded MIREOT
graphs. Only that 20-graph import closure is used for current runtime validation.
Full current CORE snapshots and historical RDF are reference inputs, not runtime
imports. No release approval or publication is claimed.

`CURRENT_PACKAGE` in `PUBLICATION_MANIFEST.txt` enumerates owned package areas,
including the migration specification, reproducibility scripts, historical archive
and extracted historical runtime. SHA256SUMS covers every member except itself.
The archive has its own immutable per-member inventory and digest. Previous
version identities resolve to original bytes, and its standalone catalogue
reproduces the historical closure. Never mix historical and current runtimes.

`PRESERVED_REFERENCE_MATERIAL` lists the three earlier Graphwise reference files.
They remain outside current runtime and the direct checksum contract. Their
historical archive copies are preserved as ZIP members; unpacked Graphwise
copies are excluded from the current package inventory. No current catalogue
entry points to a Graphwise graph. The two earlier root Textile drafts remain
in Git history. See [dependencies](DEPENDENCIES.md) and
[migration treatment](CORE_2026_MIGRATION.md).
