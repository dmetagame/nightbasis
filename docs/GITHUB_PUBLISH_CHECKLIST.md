# GitHub publish checklist

## Repository hygiene

- [ ] Confirm `git status --short --branch` contains only intended changes.
- [ ] Scan tracked files for private keys, API keys, access tokens, passwords,
      cookies, raw connection strings, and credential-bearing environment files.
- [ ] Confirm generated reports contain public market/event evidence only.
- [ ] Confirm no order-routing, account mutation, or execution credential path
      exists.

## Frozen evidence

- [ ] Confirm `reports/price-only-freeze.json` contains freeze hash
      `0898cca4374ae68dfbc85ae73138f710539d314800de8548d3b37f28fd0ba5a0`.
- [ ] Confirm the frozen price-only checkpoint remains commit `c92b9bd` and no
      thresholds, costs, universe, entry clock, model coefficients, or ledgers
      changed afterward.
- [ ] Confirm the submission says the control lost money at 15 bps per side and
      was not retuned.
- [ ] Confirm there are exactly three replay fixtures and four focus snapshots
      per fixture.

## Reproducibility

- [ ] Run `make demo-replay`; confirm it completes offline in under five minutes.
- [ ] Confirm the command prints `t`, `y`, `z`, `signed_info`,
      `event_id_or_none`, `label`, `reason`, `memo`, and explicit no-trade text.
- [ ] Run `PYTHONPATH=src python3 -m unittest discover -s tests -v`.
- [ ] Confirm all 12 records validate against `schemas/desk-record.schema.json`.
- [ ] Review `reports/judge-replay.md` against the machine transcripts.

## GitHub publication

- [ ] Add a repository remote; none is currently configured.
- [ ] Refresh `gh` authentication; the current stored credential is expired.
- [ ] Push the current branch without force-pushing or rewriting history.
- [ ] Verify the remote commit contains the freeze, README, three fixtures,
      three machine transcripts, human replay, schemas, tests, and Make target.
- [ ] Run `make demo-replay` from a fresh clone before sharing the repository.
