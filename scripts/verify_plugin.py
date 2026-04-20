#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: Path, errors: list[str]) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Invalid JSON in {path}: {exc}")
        return None

    if not isinstance(data, dict):
        errors.append(f"JSON root must be object: {path}")
        return None
    return data


def _check_skill_frontmatter(skill_md: Path, errors: list[str]) -> None:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        errors.append(f"Missing YAML frontmatter in {skill_md}")
        return

    frontmatter = match.group(1)
    if not re.search(r"(?m)^name:\s*.+$", frontmatter):
        errors.append(f"Missing frontmatter 'name' in {skill_md}")
    if not re.search(r"(?m)^description:\s*.+$", frontmatter):
        errors.append(f"Missing frontmatter 'description' in {skill_md}")


def main() -> int:
    errors: list[str] = []

    plugin_json_path = ROOT / ".codex-plugin" / "plugin.json"
    mcp_json_path = ROOT / ".mcp.json"

    for required in [
        plugin_json_path,
        mcp_json_path,
        ROOT / "scripts" / "install_personal.py",
        ROOT / "scripts" / "install_repo.py",
        ROOT / "README.md",
        ROOT / "docs" / "install.md",
    ]:
        if not required.exists():
            errors.append(f"Missing required file: {required}")

    plugin_json = None
    mcp_json = None

    if plugin_json_path.exists():
        plugin_json = _read_json(plugin_json_path, errors)
        if plugin_json is not None:
            if "skills" not in plugin_json:
                errors.append("plugin.json missing required key: skills")
            if "mcpServers" not in plugin_json:
                errors.append("plugin.json missing required key: mcpServers")

    if mcp_json_path.exists():
        mcp_json = _read_json(mcp_json_path, errors)
        if mcp_json is not None and "mcpServers" not in mcp_json:
            errors.append(".mcp.json missing required key: mcpServers")

    skill_dirs = [
        ROOT / "skills" / "yandex-direct-account-audit",
        ROOT / "skills" / "website-404-check",
    ]

    for skill_dir in skill_dirs:
        if not skill_dir.exists() or not skill_dir.is_dir():
            errors.append(f"Missing skill directory: {skill_dir}")
            continue

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"Missing skill file: {skill_md}")
            continue

        _check_skill_frontmatter(skill_md, errors)

    if errors:
        print("Plugin verification failed:\n")
        for idx, err in enumerate(errors, start=1):
            print(f"{idx}. {err}")
        return 1

    print("Plugin verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
