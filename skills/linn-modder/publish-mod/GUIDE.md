# Publish a mod

## Minimum workflow
1. Identify the target loader/platform, supported game build and requested publication destination.
2. Run `um publish check <mod>`; add `--game <install>` when a local comparison is available.
3. Resolve failures and document warnings; include only distributable code/assets or patches.
4. Prepare the package, README, version/changelog, credits and an honest verification statement.
5. Publish within existing user authorization; otherwise show the complete draft before requesting approval.

Never ship keys, game files, extracted assets or decompiled code. A runtime-untested package
must say so. A video or public post is optional unless requested.

## Read when needed
| Task | Read |
|---|---|
| Lint findings or loader/platform layouts | [Lint and package](references/lint-and-package.md) |
| README, versions, credits or release post | [Release notes](references/release-notes.md) |
| A requested demo video | [showcase-video](../showcase-video/GUIDE.md) |

Output: a reviewable package and release instructions; publish only in the authorized destination.
