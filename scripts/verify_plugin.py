#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_AUTHOR = "Антон Перепечаев"
EXPECTED_WEBSITE = "https://direct-alert.ru"
EXPECTED_MCP_URL = "https://direct-alert.ru/mcp"
PLACEHOLDER_MARKERS = (
    "[" + "Your",
    "example" + "." + "com",
    "team@" + "example" + "." + "com",
)


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


def _iter_repo_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        files.append(path)
    return files


def _check_appledouble_files(repo_files: list[Path], errors: list[str]) -> None:
    dot_underscore_files = [path for path in repo_files if path.name.startswith("._")]
    if dot_underscore_files:
        for path in dot_underscore_files:
            errors.append(f"Forbidden AppleDouble file found: {path}")


def _check_placeholders(repo_files: list[Path], errors: list[str]) -> None:
    for path in repo_files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_bytes().decode("utf-8", errors="ignore")
        except Exception as exc:
            errors.append(f"Cannot read {path} for placeholder checks: {exc}")
            continue

        for marker in PLACEHOLDER_MARKERS:
            if marker in text:
                errors.append(f"Placeholder marker found in {path}: {marker!r}")


def _check_plugin_json(plugin_json: dict, errors: list[str]) -> None:
    if "skills" not in plugin_json:
        errors.append("plugin.json missing required key: skills")
    if "mcpServers" not in plugin_json:
        errors.append("plugin.json missing required key: mcpServers")

    skills_path = plugin_json.get("skills")
    if not isinstance(skills_path, str) or not skills_path.startswith("./"):
        errors.append("plugin.json 'skills' must be a string that starts with './'")

    mcp_servers_path = plugin_json.get("mcpServers")
    if not isinstance(mcp_servers_path, str) or not mcp_servers_path.startswith("./"):
        errors.append("plugin.json 'mcpServers' must be a string that starts with './'")

    author = plugin_json.get("author")
    if not isinstance(author, dict):
        errors.append("plugin.json 'author' must be an object")
    else:
        if author.get("name") != EXPECTED_AUTHOR:
            errors.append("plugin.json 'author.name' must match expected author")

        email = author.get("email")
        placeholder_domain = ("example" + "." + "com").lower()
        if isinstance(email, str) and placeholder_domain in email.lower():
            errors.append("plugin.json 'author.email' contains a placeholder domain")

    interface = plugin_json.get("interface")
    if not isinstance(interface, dict):
        errors.append("plugin.json 'interface' must be an object")
    else:
        if interface.get("developerName") != EXPECTED_AUTHOR:
            errors.append(
                "plugin.json 'interface.developerName' must match expected author"
            )
        if interface.get("websiteURL") != EXPECTED_WEBSITE:
            errors.append(
                "plugin.json 'interface.websiteURL' must be "
                f"{EXPECTED_WEBSITE!r}"
            )


def _check_mcp_json(mcp_json: dict, errors: list[str]) -> None:
    mcp_servers = mcp_json.get("mcpServers")
    if not isinstance(mcp_servers, dict):
        errors.append(".mcp.json missing required object key: mcpServers")
        return

    server = mcp_servers.get("yandex-direct-agent")
    if not isinstance(server, dict):
        errors.append(".mcp.json missing mcpServers.yandex-direct-agent object")
        return

    if server.get("url") != EXPECTED_MCP_URL:
        errors.append(
            ".mcp.json mcpServers.yandex-direct-agent.url must be "
            f"{EXPECTED_MCP_URL!r}"
        )


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

    repo_files = _iter_repo_files(ROOT)
    _check_appledouble_files(repo_files, errors)
    _check_placeholders(repo_files, errors)

    if plugin_json_path.exists():
        plugin_json = _read_json(plugin_json_path, errors)
        if plugin_json is not None:
            _check_plugin_json(plugin_json, errors)

    if mcp_json_path.exists():
        mcp_json = _read_json(mcp_json_path, errors)
        if mcp_json is not None:
            _check_mcp_json(mcp_json, errors)

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
