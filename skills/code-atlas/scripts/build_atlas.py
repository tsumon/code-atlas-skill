#!/usr/bin/env python3
"""Validate an atlas JSON dataset (optionally against a real repo) and compile to standalone HTML."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

VALID_CATEGORIES = {"entry", "core", "storage", "security", "queue", "external"}
VALID_MODES = {"tree", "code"}
VALID_SIDES = {"top", "bottom", "left", "right"}


def _get_tab_files(tab: dict[str, Any]) -> list[dict[str, Any]]:
    files = tab.get("files")
    if isinstance(files, list) and len(files) > 0:
        return files
    return [
        {
            "id": "__default__",
            "path": tab.get("filePath", ""),
            "codeLines": tab.get("codeLines", []),
            "startLine": tab.get("startLine", 1),
        }
    ]


def validate_atlas_data(
    data: dict[str, Any],
    repo_root: Path | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return ["Top-level JSON must be an object."], warnings

    project = data.get("project")
    if not isinstance(project, dict) or not project.get("name"):
        errors.append("`project.name` is required.")

    tabs = data.get("tabs")
    if not isinstance(tabs, list) or len(tabs) == 0:
        errors.append("`tabs` must be a non-empty array.")
        return errors, warnings

    for t_idx, tab in enumerate(tabs):
        prefix = f"tabs[{t_idx}]"
        if not isinstance(tab, dict):
            errors.append(f"{prefix} must be an object.")
            continue

        if not tab.get("label"):
            errors.append(f"{prefix}.label is required.")

        mode = tab.get("mode", "code")
        if mode not in VALID_MODES:
            errors.append(f"{prefix}.mode must be one of {sorted(VALID_MODES)}, got {mode!r}.")

        # Validate files (supports both single-file codeLines and multi-file files[])
        file_map: dict[str, dict[str, Any]] = {}
        tab_files = _get_tab_files(tab)
        is_multi = isinstance(tab.get("files"), list) and len(tab.get("files", [])) > 0

        for f_idx, fobj in enumerate(tab_files):
            fp = f"{prefix}.files[{f_idx}]" if is_multi else prefix
            if not isinstance(fobj, dict):
                errors.append(f"{fp} must be an object.")
                continue
            fid = fobj.get("id")
            if not fid:
                errors.append(f"{fp}.id is required.")
                continue
            if fid in file_map:
                errors.append(f"{fp}.id {fid!r} is duplicated.")
            code_lines = fobj.get("codeLines")
            if not isinstance(code_lines, list) or len(code_lines) == 0:
                errors.append(f"{fp}.codeLines must be a non-empty list of strings.")
                line_count = 0
            else:
                line_count = len(code_lines)

            rel_path = fobj.get("path", "")
            real_disk_lines: int | None = None
            if repo_root is not None and mode == "code":
                if not rel_path:
                    errors.append(f"{fp}.path is required when --repo-root is enabled.")
                else:
                    disk_file = repo_root / rel_path
                    if not disk_file.is_file():
                        errors.append(
                            f"[GROUNDING] {fp}.path {rel_path!r} does not exist in repo {repo_root}."
                        )
                    else:
                        real_disk_lines = len(
                            disk_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                        )

            file_map[fid] = {
                "path": rel_path,
                "line_count": line_count,
                "real_disk_lines": real_disk_lines,
                "startLine": fobj.get("startLine", 1),
            }

        nodes = tab.get("nodes")
        node_ids: set[str] = set()
        if not isinstance(nodes, list) or len(nodes) == 0:
            errors.append(f"{prefix}.nodes must be a non-empty array.")
        else:
            for n_idx, node in enumerate(nodes):
                nid = node.get("id") if isinstance(node, dict) else None
                if not nid:
                    errors.append(f"{prefix}.nodes[{n_idx}].id is required.")
                    continue
                if nid in node_ids:
                    errors.append(f"{prefix}.nodes[{n_idx}].id {nid!r} is duplicated.")
                node_ids.add(nid)
                if not node.get("title"):
                    errors.append(f"{prefix}.nodes[{n_idx}].title is required.")
                cat = node.get("category", "core")
                if cat not in VALID_CATEGORIES:
                    errors.append(
                        f"{prefix}.nodes[{n_idx}].category {cat!r} not in {sorted(VALID_CATEGORIES)}."
                    )

        edges = tab.get("edges", [])
        if not isinstance(edges, list):
            errors.append(f"{prefix}.edges must be an array.")
        else:
            for e_idx, edge in enumerate(edges):
                if not isinstance(edge, dict):
                    errors.append(f"{prefix}.edges[{e_idx}] must be an object.")
                    continue
                if edge.get("from") not in node_ids:
                    errors.append(f"{prefix}.edges[{e_idx}].from {edge.get('from')!r} does not match any node id.")
                if edge.get("to") not in node_ids:
                    errors.append(f"{prefix}.edges[{e_idx}].to {edge.get('to')!r} does not match any node id.")
                for side_key in ("fromSide", "toSide"):
                    if side_key in edge and edge[side_key] not in VALID_SIDES:
                        errors.append(
                            f"{prefix}.edges[{e_idx}].{side_key} {edge[side_key]!r} not in {sorted(VALID_SIDES)}."
                        )

        steps = tab.get("steps")
        if not isinstance(steps, list) or len(steps) == 0:
            errors.append(f"{prefix}.steps must be a non-empty array.")
        else:
            default_fid = next(iter(file_map), "__default__")
            for s_idx, step in enumerate(steps):
                sp = f"{prefix}.steps[{s_idx}]"
                if not isinstance(step, dict):
                    errors.append(f"{sp} must be an object.")
                    continue
                if not step.get("title"):
                    errors.append(f"{sp}.title is required.")

                fid = step.get("fileId", default_fid)
                if fid not in file_map:
                    errors.append(f"{sp}.fileId {fid!r} does not match any file id in tab.")
                    f_meta = None
                else:
                    f_meta = file_map[fid]

                lines = step.get("lines")
                if (
                    not isinstance(lines, list)
                    or len(lines) != 2
                    or not all(isinstance(x, int) for x in lines)
                ):
                    errors.append(f"{sp}.lines must be a 2-integer array [startLine, endLine].")
                elif f_meta and f_meta["line_count"] > 0:
                    start_l, end_l = lines
                    if start_l < 1 or end_l < start_l or end_l > f_meta["line_count"]:
                        errors.append(
                            f"{sp}.lines [{start_l}, {end_l}] is out of bounds for 1..{f_meta['line_count']}."
                        )

                real_lines = step.get("realLines")
                if real_lines is not None:
                    if (
                        not isinstance(real_lines, list)
                        or len(real_lines) != 2
                        or not all(isinstance(x, int) for x in real_lines)
                        or real_lines[0] < 1
                        or real_lines[1] < real_lines[0]
                    ):
                        errors.append(f"{sp}.realLines must be a valid [start, end] integer range.")
                    elif f_meta and f_meta["real_disk_lines"] is not None:
                        if real_lines[1] > f_meta["real_disk_lines"]:
                            errors.append(
                                f"[GROUNDING] {sp}.realLines {real_lines} exceeds actual file line count "
                                f"({f_meta['real_disk_lines']}) of {f_meta['path']}."
                            )

                s_nodes = step.get("nodeIds", [])
                if not isinstance(s_nodes, list) or len(s_nodes) == 0:
                    errors.append(f"{sp}.nodeIds must reference at least one node id.")
                else:
                    for nid in s_nodes:
                        if nid not in node_ids:
                            errors.append(f"{sp}.nodeIds contains unknown node id {nid!r}.")

                insights = step.get("insights")
                if not isinstance(insights, dict):
                    errors.append(f"{sp}.insights object is required.")
                else:
                    for req_key in ("mechanism", "pitfalls", "interview"):
                        if not insights.get(req_key):
                            errors.append(f"{sp}.insights.{req_key} is required.")

    return errors, warnings


def compile_html(data: dict[str, Any], template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    title = f"{data['project']['name']} 源码 · 图谱"
    json_payload = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")

    if "__ATLAS_DATA__" not in template:
        raise ValueError("Template is missing __ATLAS_DATA__ placeholder.")

    rendered = template.replace("__ATLAS_TITLE__", html.escape(title))
    rendered = rendered.replace("__ATLAS_DATA__", json_payload)
    return rendered


def main() -> int:
    skill_root = Path(__file__).resolve().parent.parent
    default_template = skill_root / "assets" / "template.html"
    demo_data_path = skill_root / "examples" / "demo-data.json"

    parser = argparse.ArgumentParser(
        description="Validate atlas-data.json and build a standalone interactive Code Atlas HTML."
    )
    parser.add_argument("input", nargs="?", help="Path to atlas-data.json")
    parser.add_argument("-o", "--output", help="Output standalone HTML path (required unless --validate-only)")
    parser.add_argument("--template", default=str(default_template), help="Custom HTML template path")
    parser.add_argument("--repo-root", help="Optional local repo root to verify every filePath and realLines exists on disk")
    parser.add_argument("--demo", action="store_true", help="Build from bundled examples/demo-data.json")
    parser.add_argument("--validate-only", action="store_true", help="Validate JSON without writing HTML")
    args = parser.parse_args()

    input_path = demo_data_path if args.demo else (Path(args.input) if args.input else None)
    if input_path is None:
        parser.error("Provide an input JSON path or pass --demo.")
    if not args.validate_only and not args.output:
        parser.error("-o/--output is required unless --validate-only is set.")

    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        return 1

    repo_root: Path | None = None
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
        if not repo_root.is_dir():
            print(f"[ERROR] --repo-root directory not found: {repo_root}", file=sys.stderr)
            return 1

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[ERROR] Invalid JSON in {input_path}: {exc}", file=sys.stderr)
        return 1

    errors, warnings = validate_atlas_data(data, repo_root=repo_root)
    for w in warnings:
        print(f"[WARN] {w}", file=sys.stderr)
    if errors:
        print(f"[ERROR] Validation failed with {len(errors)} issue(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    total_tabs = len(data["tabs"])
    total_steps = sum(len(t["steps"]) for t in data["tabs"])
    total_nodes = sum(len(t["nodes"]) for t in data["tabs"])
    verified_tag = f" (grounded against {repo_root.name})" if repo_root else ""

    if args.validate_only:
        print(f"[OK] Validated {input_path}{verified_tag}: {total_tabs} tabs, {total_steps} steps, {total_nodes} nodes.")
        return 0

    template_path = Path(args.template)
    if not template_path.exists():
        print(f"[ERROR] Template file not found: {template_path}", file=sys.stderr)
        return 1

    html_output = compile_html(data, template_path)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_output, encoding="utf-8")

    size_kb = out_path.stat().st_size / 1024
    print(
        f"[OK] Built {out_path} ({size_kb:.1f} KB){verified_tag} — "
        f"{total_tabs} tabs, {total_steps} steps, {total_nodes} nodes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
