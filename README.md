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

## 🔀 Branch split: main vs trainsh

- **main (engine)**: generic Notion→Hugo toolchain. No site-specific config/assets.
  - Uses `config.example.toml` as a template.
  - GitHub Actions workflow is disabled (manual only, no deploy).
- **trainsh (your site)**: production branch for `train.sh`.
  - Contains site `config.toml` and `static/` assets (e.g., `favicon.ico`).
  - Adds theme as submodule: `themes/hugo-trainsh`.
  - Auto-deploys to Cloudflare Pages project `trainsh`.

Initialize locally for trainsh:
```bash
git checkout trainsh
git submodule update --init --recursive
```

## 🚢 GitHub Actions Auto Deploy (trainsh)

Add GitHub Actions secrets:
- `NOTION_TOKEN`
- `NOTION_DATABASE_ID`
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Deploy workflow: `.github/workflows/deploy-trainsh.yml` (push to `trainsh`, schedule, or manual)

Cloudflare Pages:
- Project name: `trainsh`
- Recommended: set Production branch to `trainsh` in Dashboard

## 📄 License

Apache-2.0. See `LICENSE` or `http://www.apache.org/licenses/LICENSE-2.0`.

## 📮 Support

Issues: `https://github.com/binbinsh/notion-hugo-deploy/issues`
