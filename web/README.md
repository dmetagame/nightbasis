# NightBasis Desk web

Production marketing and offline replay interface for the frozen NightBasis
Desk research. All displayed fixtures are transcribed from the repository's
judge replay and cached fixture records; the site has no order path and makes
no network request for market data.

## Local development

```bash
npm install
npm run dev
```

Or run `make site` from the repository root.

## Production build

```bash
npm ci
npm run build
```

The production build uses `/nightbasis/` as its base path for GitHub Pages and
writes the static site to `web/dist/`. The build also copies `index.html` to
`404.html` so direct links such as `/nightbasis/desk` return the React shell.

To publish without a repository workflow, build the site and deploy the
contents of `web/dist/` to a `gh-pages` branch, then choose that branch in
**Settings → Pages → Build and deployment**. Exact commands are included in the
project handoff and the final implementation report.

For a generic static host mounted at `/`, use:

```bash
npm run build:static
```

Upload the contents of `web/dist/`—not the `dist` directory itself—to the root
of the static host.
