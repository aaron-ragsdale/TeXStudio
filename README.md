# TeXStudio

A free, browser-based academic writing workspace powered by [TeXlyre](https://github.com/TeXlyre/texlyre).

**[Open TeXStudio](https://aaron-ragsdale.github.io/TeXStudio/)** (after Pages deployment).

## Features
- Local WebAssembly LaTeX and Typst compilation, PDF preview, project files, syntax highlighting and bibliography tools.
- Project archive import/export, local browser storage, templates and optional collaboration.
- No required paid account or compilation server. Package downloads and optional networking features may use upstream services.

## Deploy
Open [Settings → Pages](https://github.com/aaron-ragsdale/TeXStudio/settings/pages) and select **GitHub Actions** as the source. Then open **Actions → Deploy TeXStudio → Run workflow**. The workflow checks out the pinned upstream source, applies TeXStudio configuration and builds static assets. The upstream source is not copied into this repository; its pinned revision and configuration are in the workflow.

## First test
Use Chrome or Edge, create a blank project, compile the sample document and export its PDF. Import an Overleaf source ZIP to test package compatibility. Export source ZIP backups regularly: browser data can be cleared and is not automatically synchronized across devices.

## Source and licensing
TeXlyre is AGPL-3.0-or-later, copyright its contributors. The deployment retains upstream license notices. Corresponding source: [pinned upstream revision](https://github.com/TeXlyre/texlyre/tree/6bf1f23b31997a9c6183f3700bb38d18d39bc23e) plus the configuration changes in [this workflow](.github/workflows/deploy.yml). Not affiliated with Overleaf or the TeXstudio desktop editor.
