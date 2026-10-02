# Archive inspection, editing and repacking

Read when the requested mod needs data inside a game container. These are adapter
requirements, not a claim that Linn Modder already provides archive operations.
Current Koei profiles are planning only. Use the user's requested validation scope.

## Establish capability before writing

Record the exact game, build, language and expansion/PK edition, source hash,
format magic/version and the inspection tool's version. An extension alone does
not identify a format. Search documented formats and existing community tools first.

Keep separate evidence for these levels:

| Capability | Evidence required |
|---|---|
| Recognize | Header and version checks match known samples |
| Read | Index and payload boundaries validate; extracted entries decode correctly |
| Repack | Unchanged contents can be repacked and independently checked |
| Edit | A single modified entry repacks correctly while unrelated entries remain intact |
| Game verified | The particular output was loaded by the stated game build |

Support can differ by compression method or entry type within one archive. Report
unsupported encrypted, signed or unknown sections and their impact on writing.
Recognition or extraction alone does not establish repacking support.

## Required workflow

1. **Preserve the original.** Hash the source and snapshot the bounded affected folder.
   Service game roots remain read-only. Keep extracted resources and output containers
   under a separate staging directory; exclude stock assets from Git and releases.
2. **Inspect the structure.** Establish byte order, header/version, directory or entry
   table, IDs/names and their encoding, counts, offsets, alignment, padding, compression,
   checksums and references to other containers. Record assumptions separately from facts.
3. **Extract the minimum slice.** Read only entries needed for the requested change.
   Validate offsets/sizes against the source, bound decompressed sizes, and reject path
   traversal, duplicate output names and links before writing extraction files.
4. **Prove a no-change round trip first.** Read → repack to a new file → read again.
   Compare entry identities/order where significant, metadata and decoded payload hashes.
   Preserve unknown fields and untouched raw blocks. For lossless formats, require byte
   identity where deterministic; explain any permitted container-level differences such
   as recompression/timestamps and verify semantic identity. Do not use image similarity
   as proof of archive integrity. Prefer a second reader or established tool as a check.
5. **Modify one entry.** Map the stable character/asset ID to its original entry. Validate
   dimensions, mip levels, alpha, compression and encoding before insertion. Recompute
   changed lengths/offsets/checksums; preserve unrelated entries and required ordering.
6. **Repack and validate.** Write a new staged container, then re-open and validate all
   structural references and checksums. Compare modified and untouched entries against
   the intended change set. A failed build leaves the source and last valid output intact.
7. **Prepare deployment and recovery.** Produce a file/hash change manifest and explicit
   backup/restore instructions. Installation is a separate authorized step. If gameplay
   testing was not requested, mark the result as format-validated and game-unverified.

For CK3/Victoria II, first determine whether an additive mod folder can replace the
asset without repacking stock containers. For Romance of the Three Kingdoms and
Nobunaga's Ambition, establish the exact title and PK edition; do not transfer offsets
or compression assumptions across games or updates.

## Adapter acceptance criteria

An adapter should separate detection, read/index, bounded extraction, validation and
build into independently testable operations. It should report explicit read/write
capabilities and unsupported variants, plus source/output hashes and tool versions.
No generic `archive_import` or `archive_repack` service tool exists today.

Use synthetic legal fixtures for malformed counts, overlapping/out-of-range offsets,
truncated data, unsupported codecs, decompression limits, round trips, single-entry
replacement and write failures. Test unmodified entry preservation and source immutability.
Real samples, when authorized and available, supplement these fixtures outside the repo.
Measure extraction/repacking time, peak memory and output size on the same inputs before
introducing parallelism or caches; correctness and recoverability remain acceptance gates.

Output: versioned format findings, capability level, a reproducible round-trip report,
the staged modified container if supported, and a recovery manifest.
