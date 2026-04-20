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

Restart Codex, open `/plugins`, install **Yandex.Direct Agent**, then open `/mcp` and verify that `yandex-direct-agent` is visible.

## 4) Smoke-check

```bash
python3 scripts/verify_plugin.py
codex mcp list
codex mcp login yandex-direct-agent
```

Use `codex mcp login yandex-direct-agent` only when production MCP uses an OAuth login flow.

After that, run a simple prompt in Codex such as:

- `Run a quick Yandex Direct account audit and list top 3 issues.`
- `Check these landing pages for 404/soft-404 behavior.`

If MCP auth is complete, tools should return production-backed data.
