#!/usr/bin/env python3
"""Validate an atlas JSON dataset and compile it into a standalone HTML Code Atlas."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

VALID_CATEGORIES = {"entry", "core", "storage", "security", "queue", "external"}
VALID_MODES = {"tree", "code"}


def validate_atlas_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["Top-level JSON must be an object."]

    project = data.get("project")
    if not isinstance(project, dict) or not project.get("name"):
        errors.append("`project.name` is required.")

    tabs = data.get("tabs")
    if not isinstance(tabs, list) or len(tabs) == 0:
        errors.append("`tabs` must be a non-empty array.")
        return errors

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

        code_lines = tab.get("codeLines")
        if not isinstance(code_lines, list) or len(code_lines) == 0:
            errors.append(f"{prefix}.codeLines must be a non-empty list of strings.")
            line_count = 0
        else:
            line_count = len(code_lines)

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

        steps = tab.get("steps")
        if not isinstance(steps, list) or len(steps) == 0:
            errors.append(f"{prefix}.steps must be a non-empty array.")
        else:
            for s_idx, step in enumerate(steps):
                sp = f"{prefix}.steps[{s_idx}]"
                if not isinstance(step, dict):
                    errors.append(f"{sp} must be an object.")
                    continue
                if not step.get("title"):
                    errors.append(f"{sp}.title is required.")

                lines = step.get("lines")
                if (
                    not isinstance(lines, list)
                    or len(lines) != 2
                    or not all(isinstance(x, int) for x in lines)
                ):
                    errors.append(f"{sp}.lines must be a 2-integer array [startLine, endLine].")
                elif line_count > 0:
                    start_l, end_l = lines
                    if start_l < 1 or end_l < start_l or end_l > line_count:
                        errors.append(
                            f"{sp}.lines [{start_l}, {end_l}] is out of bounds for 1..{line_count}."
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

    return errors


def compile_html(data: dict[str, Any], template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    title = f"{data['project']['name']} 源码 · 图谱"
    # Escape closing script tags inside JSON safely
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
    parser.add_argument("-o", "--output", required=True, help="Output standalone HTML path")
    parser.add_argument("--template", default=str(default_template), help="Custom HTML template path")
    parser.add_argument("--demo", action="store_true", help="Build from bundled examples/demo-data.json")
    parser.add_argument("--validate-only", action="store_true", help="Validate JSON without writing HTML")
    args = parser.parse_args()

    input_path = demo_data_path if args.demo else (Path(args.input) if args.input else None)
    if input_path is None:
        parser.error("Provide an input JSON path or pass --demo.")

    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[ERROR] Invalid JSON in {input_path}: {exc}", file=sys.stderr)
        return 1

    errors = validate_atlas_data(data)
    if errors:
        print(f"[ERROR] Validation failed with {len(errors)} issue(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    total_tabs = len(data["tabs"])
    total_steps = sum(len(t["steps"]) for t in data["tabs"])
    total_nodes = sum(len(t["nodes"]) for t in data["tabs"])

    if args.validate_only:
        print(f"[OK] Validated {input_path}: {total_tabs} tabs, {total_steps} steps, {total_nodes} nodes.")
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
        f"[OK] Built {out_path} ({size_kb:.1f} KB) — "
        f"{total_tabs} tabs, {total_steps} steps, {total_nodes} nodes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
