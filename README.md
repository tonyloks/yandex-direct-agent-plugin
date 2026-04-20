# yandex-direct-agent-plugin

A minimal Codex plugin for Yandex Direct audits with production MCP access.

## What is included

- `skills/yandex-direct-account-audit` (v1 skeleton)
- `skills/website-404-check` (v1 skeleton)
- `.mcp.json` with production server: `https://direct-alert.ru/mcp`

Production MCP requires login after plugin installation.

## Install (personal)

```bash
python3 scripts/install_personal.py
```

## Install (repo-scoped)

From target repo root:

```bash
python3 /absolute/path/to/yandex-direct-agent-plugin/scripts/install_repo.py
```

## Update

Re-run the same install command you used before (personal or repo-scoped). The scripts are idempotent and update the plugin entry in marketplace.

## Remove

### Personal install

1. Delete `~/.codex/plugins/yandex-direct-agent`
2. Remove `yandex-direct-agent` entry from `~/.agents/plugins/marketplace.json`
3. Restart Codex

### Repo install

1. Delete `./plugins/yandex-direct-agent`
2. Remove `yandex-direct-agent` entry from `./.agents/plugins/marketplace.json`
3. Restart Codex

## Quick verification

```bash
python3 scripts/verify_plugin.py
```

## Development notes

Localhost MCP (for example `http://localhost:8000/mcp`) is intentionally not included in this plugin bundle. Use it only in development docs/workflows.
