# Publish commands

Publish status: **blocked on `gh auth login`**.

GitHub authentication failed once during this session, so no repository,
remote, push, or tag was attempted. Run the following after the final local
checkpoint exists.

## Authenticate

```bash
cd /home/rouma/projects/nightbasis
gh auth login -h github.com -p https -w
gh auth status -h github.com
```

## Create the public repository and push main

```bash
cd /home/rouma/projects/nightbasis
gh repo create nightbasis --public --source=. --remote=origin
git push -u origin main
```

If you already created the empty repository in the GitHub UI, replace only the
`gh repo create` command with the exact URL GitHub shows you:

```bash
git remote add origin https://github.com/YOUR_GITHUB_USER/nightbasis.git
git push -u origin main
```

## Create and push the two annotated tags

Run these only after all final documentation commits are on `main`:

```bash
cd /home/rouma/projects/nightbasis
git tag -a freeze-price-only-0898cca c92b9bd -m "Frozen NightBasis price-only negative control 0898cca"
git tag -a desk-judge-replay "$(git rev-parse HEAD)" -m "NightBasis Desk judge-facing replay"
git push origin freeze-price-only-0898cca desk-judge-replay
```

The first tag points to the protected freeze commit. The second deliberately
resolves `HEAD` at execution time so it includes the complete judge-facing
repository and handoff documents.

## Verify publication

```bash
git remote -v
git status --short --branch
git rev-parse c92b9bd^{commit}
git rev-parse freeze-price-only-0898cca^{commit}
git rev-parse HEAD^{commit}
git rev-parse desk-judge-replay^{commit}
gh repo view --web
```

The two freeze commit outputs must match each other. The two judge-replay commit
outputs must also match each other. Do not force-push or force-move either tag.
