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
npm run build:static
```

Primary production host: https://nightbasis.vercel.app

Vercel serves the site at the domain root. Import the repository with **Root
Directory** set to `web`; `web/vercel.json` then runs `npm ci`, calls only
`npm run build:static`, publishes `dist`, and rewrites client routes to
`index.html`. The deployment contains only the web project—Python source,
research data, and reports are outside the configured root directory.

Deploy from this directory with an authenticated Vercel CLI:

```bash
npx vercel --yes --prod --cwd .
```

## Optional GitHub Pages build

The default `npm run build` keeps `/nightbasis/` as its base path and writes to
`web/dist/`. The build also copies `index.html` to `404.html` so direct links
such as `/nightbasis/desk` return the React shell.

To publish without a repository workflow, build the site and deploy the
contents of `web/dist/` to a `gh-pages` branch, then choose that branch in
**Settings → Pages → Build and deployment**. Exact commands are included in the
project handoff and the final implementation report.

For Vercel or another static host mounted at `/`, use:

```bash
npm run build:static
```

Upload the contents of `web/dist/`—not the `dist` directory itself—to the root
of the static host.
