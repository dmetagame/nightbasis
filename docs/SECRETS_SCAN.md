# Secrets scan

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
