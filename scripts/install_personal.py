#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

PLUGIN_NAME = "yandex-direct-agent"
IGNORE_PATTERNS = (
    ".git",
    "__pycache__",
    ".DS_Store",
    "._*",
    ".AppleDouble",
    ".repo-archive",
    "*.tar.gz",
)
ENTRY = {
    "name": PLUGIN_NAME,
    "source": {
        "source": "local",
        "path": "./.codex/plugins/yandex-direct-agent",
    },
    "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    },
    "category": "Productivity",
}


def _is_subpath(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _validate_copy_paths(source_root: Path, target_root: Path) -> None:
    if source_root == target_root:
        raise ValueError(
            "Refusing unsafe copy: source and target plugin directories are identical."
        )

    if _is_subpath(source_root, target_root):
        raise ValueError(
            "Refusing unsafe copy: source directory is inside target plugin directory."
        )

    if _is_subpath(target_root, source_root):
        raise ValueError(
            "Refusing unsafe copy: target plugin directory is inside source directory."
        )


def _load_marketplace(path: Path) -> dict:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("marketplace.json root must be an object")
    else:
        data = {}

    if not isinstance(data.get("interface"), dict):
        data["interface"] = {"displayName": "Local Plugins"}

    if not data.get("name"):
        data["name"] = "local-marketplace"

    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        data["plugins"] = []

    return data


def _upsert_plugin(data: dict, entry: dict) -> None:
    plugins = data["plugins"]
    for idx, existing in enumerate(plugins):
        if isinstance(existing, dict) and existing.get("name") == entry["name"]:
            plugins[idx] = entry
            break
    else:
        plugins.append(entry)


def _copy_plugin(source_root: Path, target_root: Path) -> None:
    _validate_copy_paths(source_root, target_root)
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source_root,
        target_root,
        ignore=shutil.ignore_patterns(*IGNORE_PATTERNS),
    )


def main() -> int:
    source_root = Path(__file__).resolve().parents[1]
    target_plugin_dir = Path.home() / ".codex" / "plugins" / PLUGIN_NAME
    marketplace_path = Path.home() / ".agents" / "plugins" / "marketplace.json"

    try:
        _copy_plugin(source_root, target_plugin_dir)

        marketplace_path.parent.mkdir(parents=True, exist_ok=True)
        data = _load_marketplace(marketplace_path)
        _upsert_plugin(data, ENTRY)
        marketplace_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] Installation failed: {exc}", file=sys.stderr)
        return 1

    print("[OK] Personal plugin files copied to ~/.codex/plugins/yandex-direct-agent")
    print("[OK] Marketplace entry upserted in ~/.agents/plugins/marketplace.json")
    print("Next steps:")
    print("1) Restart Codex")
    print("2) Install 'Yandex.Direct Agent' from marketplace")
    print("3) Complete MCP login flow if production MCP uses OAuth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
