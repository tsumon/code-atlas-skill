#!/usr/bin/env python3
"""Zero-dependency repository pre-scanner for the code-atlas skill.

Extracts real git metadata, language breakdown, entrypoint candidates, and a pruned
directory tree so the agent can ground atlas-data.json without wasting context tokens.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "dist",
    "build",
    "out",
    "target",
    ".next",
    ".nuxt",
    ".output",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "vendor",
    ".idea",
    ".vscode",
    "coverage",
    ".turbo",
    ".cache",
}

ENTRYPOINT_NAMES = {
    "main.go",
    "main.py",
    "app.py",
    "server.py",
    "manage.py",
    "main.rs",
    "lib.rs",
    "index.ts",
    "index.js",
    "server.ts",
    "server.js",
    "app.ts",
    "app.js",
    "Makefile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Dockerfile",
    "go.mod",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "VERSION",
}

EXT_LANG = {
    ".go": "Go",
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".sql": "SQL",
    ".sh": "Shell",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".proto": "Protobuf",
    ".vue": "Vue",
    ".svelte": "Svelte",
}


def run_git(repo: Path, args: list[str]) -> str:
    try:
        res = subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return res.stdout.strip() if res.returncode == 0 else ""
    except Exception:
        return ""


def normalize_repo_url(remote_url: str) -> str:
    if not remote_url:
        return ""
    url = remote_url.strip()
    if url.startswith("git@github.com:"):
        url = "https://github.com/" + url[len("git@github.com:") :]
    if url.endswith(".git"):
        url = url[:-4]
    return url


def detect_version(repo: Path) -> str:
    version_file = repo / "VERSION"
    if version_file.is_file():
        txt = version_file.read_text(encoding="utf-8", errors="ignore").strip().splitlines()
        if txt:
            v = txt[0].strip()
            return v if v.startswith("v") else f"v{v}"

    pkg = repo / "package.json"
    if pkg.is_file():
        try:
            v = json.loads(pkg.read_text(encoding="utf-8")).get("version")
            if v:
                return f"v{v}" if not str(v).startswith("v") else str(v)
        except Exception:
            pass

    pyproj = repo / "pyproject.toml"
    if pyproj.is_file():
        m = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', pyproj.read_text(encoding="utf-8", errors="ignore"), re.M)
        if m:
            v = m.group(1)
            return f"v{v}" if not v.startswith("v") else v

    cargo = repo / "Cargo.toml"
    if cargo.is_file():
        m = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', cargo.read_text(encoding="utf-8", errors="ignore"), re.M)
        if m:
            v = m.group(1)
            return f"v{v}" if not v.startswith("v") else v

    tag = run_git(repo, ["describe", "--tags", "--abbrev=0"])
    if tag:
        return tag
    return ""


def build_tree_lines(
    root: Path,
    max_depth: int,
    max_entries: int,
) -> tuple[list[str], Counter[str], list[str], int]:
    lang_counts: Counter[str] = Counter()
    entrypoints: list[str] = []
    total_files = 0

    # First walk for stats and entrypoints
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORE_DIRS)
        rel_dir = Path(dirpath).relative_to(root)
        depth = 0 if str(rel_dir) == "." else len(rel_dir.parts)
        for fname in sorted(filenames):
            total_files += 1
            ext = Path(fname).suffix.lower()
            if ext in EXT_LANG:
                lang_counts[EXT_LANG[ext]] += 1
            if fname in ENTRYPOINT_NAMES and depth <= 3:
                rel_file = fname if str(rel_dir) == "." else str(rel_dir / fname)
                entrypoints.append(rel_file)

    # Build pruned visual directory tree
    lines: list[str] = [f"{root.name}/"]
    count = 0
    truncated = False

    def walk_tree(current: Path, prefix: str, depth: int) -> None:
        nonlocal count, truncated
        if depth > max_depth or count >= max_entries:
            return
        try:
            entries = sorted(
                current.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
        except PermissionError:
            return

        entries = [e for e in entries if e.name not in IGNORE_DIRS]
        visible = entries[:40]
        omitted = len(entries) - len(visible)

        for idx, entry in enumerate(visible):
            if count >= max_entries:
                truncated = True
                return
            is_last = (idx == len(visible) - 1) and omitted == 0
            branch = "└── " if is_last else "├── "
            label = f"{entry.name}/" if entry.is_dir() else entry.name
            lines.append(f"{prefix}{branch}{label}")
            count += 1
            if entry.is_dir() and depth < max_depth:
                ext_prefix = prefix + ("    " if is_last else "│   ")
                walk_tree(entry, ext_prefix, depth + 1)

        if omitted > 0 and count < max_entries:
            lines.append(f"{prefix}└── ... (+{omitted} more)")
            count += 1

    walk_tree(root, "", 1)
    if truncated:
        lines.append(f"# ... truncated at {max_entries} entries; inspect subdirs selectively")

    return lines, lang_counts, entrypoints[:40], total_files


def scan_repository(repo: Path, max_depth: int = 3, max_entries: int = 180) -> dict[str, Any]:
    commit = run_git(repo, ["rev-parse", "--short=9", "HEAD"])
    branch = run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    remote_url = normalize_repo_url(run_git(repo, ["remote", "get-url", "origin"]))
    version = detect_version(repo)
    tree_lines, lang_counts, entrypoints, total_files = build_tree_lines(repo, max_depth, max_entries)

    top_dirs = sorted(
        p.name for p in repo.iterdir() if p.is_dir() and p.name not in IGNORE_DIRS and not p.name.startswith(".")
    )

    return {
        "name": repo.name,
        "version": version,
        "commit": commit or branch or "main",
        "branch": branch,
        "repoUrl": remote_url,
        "totalFiles": total_files,
        "topLevelDirs": top_dirs,
        "languages": dict(lang_counts.most_common(8)),
        "entrypoints": entrypoints,
        "treeLines": tree_lines,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-scan a local repository for code-atlas.")
    parser.add_argument("repo", help="Path to local repository root")
    parser.add_argument("--max-depth", type=int, default=3, help="Directory tree max depth (default: 3)")
    parser.add_argument("--max-entries", type=int, default=180, help="Max tree entries (default: 180)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"[ERROR] Repository directory not found: {repo}", file=sys.stderr)
        return 1

    report = scan_repository(repo, max_depth=args.max_depth, max_entries=args.max_entries)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print(f"# Repo Scan: {report['name']}")
    print(f"- Version: {report['version'] or 'N/A'}")
    print(f"- Commit:  {report['commit']} (branch: {report['branch'] or 'N/A'})")
    print(f"- Remote:  {report['repoUrl'] or 'N/A'}")
    print(f"- Files:   {report['totalFiles']}")
    print(f"- TopDirs: {', '.join(report['topLevelDirs'])}")
    print(f"- Langs:   {', '.join(f'{k}({v})' for k, v in report['languages'].items())}")
    print("\n## Entrypoint Candidates")
    for ep in report["entrypoints"]:
        print(f"- {ep}")
    print("\n## Pruned Directory Tree")
    print("\n".join(report["treeLines"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
