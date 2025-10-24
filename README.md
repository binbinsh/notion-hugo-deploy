# Notion-Hugo Deploy

Write in Notion, publish with Hugo. Sync a Notion database to Hugo Markdown. Auto-deploy to Cloudflare Pages via GitHub Actions.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Hugo](https://img.shields.io/badge/hugo-0.148.0%2B-ff4088.svg)](https://gohugo.io/)
[![Notion API](https://img.shields.io/badge/Notion%20API-2025--09--03-black)](https://developers.notion.com/docs/upgrade-guide-2025-09-03)

## ✨ Features

- **Notion → Hugo Markdown**: Headings, lists, code, callouts, toggles, quotes
- **Media downloads**: Images, videos, audio saved under `static/` and referenced correctly
- **Math ready**: KaTeX partial included (`layouts/partials/math.html`)
- **Smart updates**: Caches and updates only changed content
- **Fast**: Concurrent downloads with progress

## 📋 Requirements

- Python 3.10+
- Hugo (extended)
- Notion integration token + a database
- Cloudflare Pages Project

## 🚀 Quick Start

1) Clone

```bash
git clone https://github.com/binbinsh/notion-hugo-deploy.git
cd notion-hugo-deploy
```

2) Notion + env

```bash
# Create integration at https://www.notion.so/my-integrations
# Share your database with the integration

# In project root:
cat > .env << 'EOF'
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_database_id
EOF
```

3) Install (uv) and sync

```bash
uv venv --python 3.10
uv pip install -r requirements.txt

# First sync (cleans existing posts)
uv run scripts/notion_sync.py --clean
```

4) Run Hugo locally

```bash
hugo server -D
```

Tip: Prefer `uv run` for Python commands. Alternatively, you can run `./setup.sh` to prepare the environment once.

## 🚢 GitHub Actions Auto Deploy

Automatic sync from Notion and deploy to Cloudflare Pages using GitHub Actions.

### 1) Add GitHub Actions Secrets

Path: Repository → Settings → Secrets and variables → Actions → New repository secret

- `NOTION_TOKEN`: Notion Internal Integration Token
- `NOTION_DATABASE_ID`: Notion database ID
- `CLOUDFLARE_API_TOKEN`: Cloudflare API token with Pages write permissions

### 2) Add GitHub Actions Variables

Path: Repository → Settings → Secrets and variables → Actions → New repository variable

- `CLOUDFLARE_ACCOUNT_ID` (required): Your Cloudflare Account ID
- `CLOUDFLARE_PAGES_PROJECT` (required): Your Cloudflare Pages project name

### 3) Workflow overview

Use a workflow (e.g., at `/.github/workflows/deploy.yml`) that:

- Triggers on push to `main`, manual dispatch, or a schedule
- Steps:
  - Ensure `uv` and Hugo (extended) are available in the runner
  - `uv run scripts/notion_sync.py --clean` to sync Notion content
  - `hugo --minify` to build the site into `public/`
  - `wrangler pages deploy ./public --project-name ${CLOUDFLARE_PAGES_PROJECT}` to deploy to Cloudflare Pages (uses the secrets/variables above)

Tip: To reproduce locally, run the sync and build commands and confirm `public/` exists.

### 4) Where to get the values

- Notion database ID: From the database page URL (32-char ID)
- Cloudflare Account ID: Cloudflare Dashboard → Overview
- Cloudflare API token: Dashboard → API Tokens → Create Token (Pages write perms)
- Cloudflare Pages project name: Pages project details

See also: `cloudflare/wrangler-action` and Cloudflare Pages docs.

## 📄 License

Apache-2.0. See `LICENSE` or `http://www.apache.org/licenses/LICENSE-2.0`.

## 📮 Support

Issues: `https://github.com/binbinsh/notion-hugo-deploy/issues`
