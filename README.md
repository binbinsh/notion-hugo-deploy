# Notion-Hugo Deploy

Write in Notion, publish with Hugo. Sync a Notion database to Hugo Markdown. Auto-deploy to Cloudflare Pages via GitHub Actions.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Hugo](https://img.shields.io/badge/hugo-0.148.0%2B-ff4088.svg)](https://gohugo.io/)
[![Notion API](https://img.shields.io/badge/Notion%20API-2025--09--03-black)](https://developers.notion.com/docs/upgrade-guide-2025-09-03)

## ✨ What it does

- **Sync Notion → Hugo Markdown** (titles, dates, tags, rich text)
- **Download media** to `static/` and update references
- **Incremental updates** with caching
- **CI/CD to Cloudflare Pages** via GitHub Actions

## 📋 Requirements

- Python 3.10+
- Hugo (extended)
- Notion integration token + a database
- Cloudflare Pages Project

## 🚀 Usage

Follow these six steps to set up a new site from this repo.

1) Clone and create a branch

```bash
git clone https://github.com/binbinsh/notion-hugo-deploy.git
cd notion-hugo-deploy
git checkout -b my-site
```

2) Initialize a Hugo site at the repo root

Use `--force` because the directory is not empty.

```bash
hugo new site . --force
```

Create a minimal config (choose one filename; example uses TOML):

```toml
baseURL = "https://<your-domain>"
languageCode = "en-us"
title = "My Blog"
theme = "hugo-trainsh"
```

3) Add a theme via git submodule (example: binbinsh/hugo-trainsh)

```bash
git submodule add https://github.com/binbinsh/hugo-trainsh.git themes/hugo-trainsh
git submodule update --init --recursive
```

4) Set up Cloudflare Pages and GitHub secrets/vars

- Create a Pages project and an API token in your Cloudflare account.
- In your GitHub repository Settings → Secrets and variables:
  - Secrets: `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`
  - Variables: `CLOUDFLARE_PAGES_PROJECT` (your Pages project name)
- Reference: [Cloudflare Pages](https://pages.cloudflare.com/)

5) Create a Notion integration and configure your Blog database

- Create an integration and copy its Internal Integration Token.
- Add/ensure the following database properties (names/types):
  - `Title` (title)
  - `Published` (checkbox)
  - `Date` (date)
  - `Slug` (rich_text)
  - `Tags` (multi_select)
- Share the database with the integration.
- In GitHub repository Secrets, add:
  - `NOTION_TOKEN`
  - `NOTION_DATABASE_ID`
- Reference: [Notion Integrations](https://www.notion.so/profile/integrations)

6) Enable GitHub Actions from the example workflow

- Copy the example to your active workflow:

```bash
cp .github/workflows/deploy-example.yml .github/workflows/deploy.yml
```

- In `.github/workflows/deploy.yml`, enable triggers, e.g. push to your branch:

```yaml
on:
  push:
    branches: [ my-site ]
```

The workflow uses `uv` to install dependencies, runs `uv run scripts/notion_sync.py`, builds with Hugo, and deploys with `cloudflare/wrangler-action@v3` to your Cloudflare Pages project.

Optional: run locally before pushing

```bash
uv venv --python 3.10
uv pip install -r requirements.txt
uv run scripts/notion_sync.py
hugo server -D

# Tip: For a full rebuild locally, you can pass --clean once
# uv run scripts/notion_sync.py --clean
```

## 🧩 Secrets and variables recap

- GitHub Secrets:
  - `NOTION_TOKEN`
  - `NOTION_DATABASE_ID`
  - `CLOUDFLARE_API_TOKEN`
  - `CLOUDFLARE_ACCOUNT_ID`
- GitHub Variables:
  - `CLOUDFLARE_PAGES_PROJECT`

## 🧠 Caching & Incremental Sync

- Media cache: images/videos/audio are stored under `static/` using stable filenames.
  - Notion-hosted files use the file UUID as the filename, so re-runs won’t re-download the same file even if the signed URL changes.
  - External URLs are keyed by the URL; if the file already exists locally, it is reused.
- State: `.notion_cache.json` records media mappings and last sync time.
- CI cache: the workflow restores/saves cache for `.notion_cache.json` and `static/*` so unchanged media aren’t re-downloaded between runs.

## 🖼️ HTML rendering in content

This project’s converter intentionally outputs HTML for images, videos, audio and links (e.g. `<figure>`, `<img>`, `<video>`, `<audio>`, `<a>`), to provide better control and compatibility. To render these safely from trusted Notion content, enable Goldmark’s unsafe HTML rendering in your site config:

```toml
[markup.goldmark.renderer]
  unsafe = true
```

If you prefer to avoid `unsafe = true`, you can modify the converter to emit pure Markdown for images/links (losing some HTML-only features like `target="_blank"`) or rely on theme render hooks.

## 👤 Author & Links

- Author: [Binbin Shen](https://github.com/binbinsh)
- Issues: https://github.com/binbinsh/notion-hugo-deploy/issues
- License: http://www.apache.org/licenses/LICENSE-2.0
