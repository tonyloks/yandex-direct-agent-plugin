# Installation Guide

## 1) Personal install (home-level)

1. Clone this repository locally.
2. Run:

```bash
python3 scripts/install_personal.py
```

This copies the plugin into `~/.codex/plugins/yandex-direct-agent` and upserts an entry in `~/.agents/plugins/marketplace.json`.

## 2) Repo install (project-level)

From your target repository root, run:

```bash
python3 /absolute/path/to/yandex-direct-agent-plugin/scripts/install_repo.py
```

This copies the plugin into `./plugins/yandex-direct-agent` and upserts `./.agents/plugins/marketplace.json`.

## 3) Restart and connect

1. Restart Codex.
2. Install **Yandex.Direct Agent** from the plugin marketplace.
3. Complete MCP login flow for production access.

## 4) Smoke-check

In Codex, run a simple prompt such as:

- `Run a quick Yandex Direct account audit and list top 3 issues.`
- `Check these landing pages for 404/soft-404 behavior.`

If MCP auth is complete, tools should return production-backed data.
