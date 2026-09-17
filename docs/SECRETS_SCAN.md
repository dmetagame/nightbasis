# Secrets scan

## Pre-submission tracked-history scan — 2026-09-17

Starting commit: `a25bacd4ea2531c0292ebf2f6f991ea28552dd75`.
Read-only scan of all reachable local Git refs: **39 commits, 182 unique file
blobs, 9,781,251 bytes**. Compressed market JSON was additionally decompressed
for content checks. No sensitive filenames or credential-pattern matches were
found; nothing required removal, rotation, or a history rewrite.

Checks covered `.env` and key/cookie/credential filenames; private-key headers;
GitHub, provider `sk-`, Slack, AWS and Google key formats; JWTs;
credential-bearing URLs; and literal key/secret/token/password assignments.
Output contained only counts, filenames and rule identifiers, never candidate
secret values. This pattern-based result does not prove that arbitrary unlabeled
strings cannot be secrets. Unreachable Git objects and credentials outside the
repository were not inspected.

The worktree-only statements below are historical evidence from 2026-09-14,
not an inventory of today's ignored build or dependency directories.

## Original worktree scan

Initial scan: `2026-09-14T14:28:58+01:00`

Final scan after all submission files existed: `2026-09-14T14:38:05+01:00`

Scope: the NightBasis worktree excluding `.git/`, covering 50 tracked files,
untracked files, hidden environment filenames, and ignored-file status. The scan
printed file paths and marker classes only, never candidate values.

## Clean files

- No `.env`, cookie, credential, secret, PEM, private-key, PKCS#12, or key files
  were found.
- No high-confidence private-key headers, GitHub tokens, OpenAI/Qwen-style
  `sk-` tokens, Slack tokens, AWS access keys, Google API keys, JWTs, or URLs
  with embedded credentials were found.
- No Qwen, DashScope, Bitget API-secret/passphrase, UID, user-ID, session-token,
  access-token, or refresh-token markers were found in project data or source.
- Generic credential words appeared only in documentation that discusses safe
  publication: this report, `docs/GITHUB_PUBLISH_CHECKLIST.md`,
  `docs/WHAT_YOU_DO_NEXT.md`, and `docs/PROJECT_STATE.md`. They are checklist or
  security labels, not values.
- The only ignored worktree paths were Python `__pycache__/` directories, which
  are covered by `.gitignore` and contain no submission material.

## Blocked files

None. No sensitive file required relocation or a new ignore rule.

Repeat this scan immediately before pushing because this result covers the
worktree at the timestamp above, not future edits.
