# Upstream integration

Linn Modder incorporates selected fixes and field notes from
[universal-modder](https://github.com/rehan-remade/universal-modder), under the
repository's MIT license. The current reference is
[`3c4ac6c` (2026-11-06)](https://github.com/rehan-remade/universal-modder/tree/3c4ac6c38e411b8c543bce217eae197039516bfc).
Changes are adapted to the shared service and single-entry manuals rather than
merged as a replacement directory tree.

## Reliability and retrieval

Knowledge sync now downloads a single revision into a separate staging directory.
It rejects an empty or truncated tree and keeps the previous cache when a request
fails. Downloads use at most eight workers, with a 20-second timeout per request;
progress is written to stderr. Cache replacement can roll back if publication
fails. Checkout notes and the wheel's offline snapshot remain the default sources.

Knowledge checks reject missing folders, empty collections and missing note files.
Numbered Gotchas subheadings count as numbered entries. Quoted CLI topics can match
the exact phrase or all of its words in one note, while separate arguments remain
alternatives. Results retain Linn Modder's game filters, version metadata and exact
section ranges; the structured query interface keeps its existing keyword semantics.

The PE reader checks the declared data-directory count before interpreting a CLR
entry. Section-table bytes no longer turn a native executable into a false .NET match.

The source changes are
[cache sync](https://github.com/rehan-remade/universal-modder/commit/0d65ff96d3d519263355366adf0899acd5cb76bf),
[empty checks](https://github.com/rehan-remade/universal-modder/commit/54c5cc23ba2394074b6007cf91d705dc11aeccb1),
[Gotchas headings](https://github.com/rehan-remade/universal-modder/commit/de4d1dcd3f48948913c10e761a88cacabb2d6007),
[topic queries](https://github.com/rehan-remade/universal-modder/commit/c6cc16b1044aea22835f8b737bd74b9b2da771bb)
and [PE directories](https://github.com/rehan-remade/universal-modder/commit/0e0fc3ea31cc9023eff6908d9f8568f59970da52).

## Field-note collection

The collection contains 359 notes: 346 newly imported reports, 11 refreshed upstream
reports, and two local references retained unchanged. Game investigations live under
`knowledge/games/`; cross-game methods live under `knowledge/techniques/`. The existing
[knowledge entry](../knowledge/README.md) and regenerated [index](../knowledge/INDEX.md)
provide one route into the collection, without adding discoverable skills.

Original authors, dates, statuses, game versions and verification limits are retained.
Each upstream note has a pinned `upstream` source in its metadata. Five screenshots
remain with the reports they support. Links use local knowledge or existing skill
routes where available; upstream examples remain links to the pinned source instead
of implying that their code ships here. The shared MIT notice is retained in
[LICENSE](../LICENSE).

These are the original authors' findings, not new game acceptance by Linn Modder.
A report may use a command or engine label that this fork does not implement. In
particular, the four IW-engine reports are useful reference material, not a claim
that the scanner supports IW. Existing project workflows take precedence over a
report's choice of generation provider, segmentation method or agent arrangement.
No game installation, extracted assets, model weights or upstream executables are
included in this import.

The generated JSON index is larger than a single manual. Its read limit is 1 MiB;
individual manuals retain their 256 KiB limit and existing paging behavior.

## Earlier ports

The 2026-10-07 integration used upstream `baff1e5`. It preserved partial alpha,
shared PowerShell and Steam-registry discovery, improved game-name routing and
word-start search, reported invalid YAML dates, expanded key-pattern checks, and
accepted pre-1980 backup timestamps. Those changes remain in place. Same-second
snapshot protection, restore validation and bounded scanning use this fork's own
implementations.

The recorded acceptance for that integration was 127 passing tests and two skipped
native Windows checks, plus documentation, knowledge-index, publish, build and
installed-wheel checks. Those figures describe the earlier integration only.

Current checks cover cache failure and replacement, bounded downloads, native and
managed PE fixtures, knowledge validation, query ranking, section reads and installed
resources. They use synthetic inputs; imported game behavior has not been replayed.
