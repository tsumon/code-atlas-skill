---
name: code-atlas
description: >-
  Generate a zero-dependency, single-file interactive source-code architecture atlas
  (源码图谱 HTML) for any local repository or GitHub project. Features multi-tab navigation
  (annotated directory tree + multi-file deep-dive execution chains), bidirectional
  code-to-graph highlighting, zoomable animated SVG architecture diagrams with smart port
  spreading, GitHub source deep-links, URL hash sharing, SVG/Markdown export, cross-tab
  search, auto-play walkthrough, dark/light themes, and a 3-column collapsible deep-dive
  drawer (核心源码机制 / 线上避坑与边界 / 面试高频追问与答法). Use whenever the user asks
  to visualize, map, explain, or create an interactive source-code atlas / architecture guide
  for a codebase.
---

# Code Atlas (`code-atlas`)

Build a polished, standalone single-file HTML **Interactive Source-Code Atlas** for any repository, backed by **verified real source code**.

## Non-Negotiable Grounding Rules

1. **Never fabricate file paths, symbols, or line numbers.** Every directory entry, code excerpt, function name, and architectural claim must come from reading the actual repository.
2. **Pre-scan first.** Always run [`scripts/scan_repo.py`](./scripts/scan_repo.py) before authoring Tab 0 so commit SHA, version, remote URL, and directory layout are 100% grounded while saving context tokens.
3. **Ground-truth verify at build time.** Compile via [`scripts/build_atlas.py`](./scripts/build_atlas.py) **with `--repo-root <repo_path>`** so every file path and optional `realLines` range is verified directly against disk.

---

## Step-by-Step Workflow

### Phase 1: Pre-Scan & Inspect the Target Repository

1. Locate the codebase:
   - If given a local path, inspect it directly.
   - If given a GitHub URL, shallow-clone it (`git clone --depth 1 <url>`) into a clean temporary or scratch directory.
2. Run the zero-dependency pre-scanner:
   ```bash
   python3 <skill_dir>/scripts/scan_repo.py <repo_path> --max-depth 3
   ```
   Capture the exact `commit`, `version`, `repoUrl`, top-level directories, language breakdown, and entrypoint candidates.
3. Plan **4 to 6 tabs** (unless the user specifies custom topics):
   - **Tab 0 (`0. 项目目录`, `mode: "tree"`)**: Complete annotated directory tree paired with a **6 to 9 module architecture overview** (`3x2` or `3x3` grid).
   - **Tabs 1..N (`mode: "code"`)**: The 3–5 highest-leverage core execution chains of the project. Prefer **multi-file tabs (`files[]`)** whenever a real execution chain spans 2–4 source files (e.g., `handler → service → retriever → store`), and record `startLine` or `realLines` so the `↗ GitHub 原文` button jumps to the exact source lines.

### Phase 2: Author `atlas-data.json`

Read [`references/data-schema.md`](./references/data-schema.md) for the complete schema (and [`references/design-spec.md`](./references/design-spec.md) if customizing layout/styles).

Quality checklist while authoring `atlas-data.json`:
- **Aligned tree annotations**: In Tab 0 (`mode: "tree"`), pad file/dir paths with spaces so inline `# 中文备注` comments line up cleanly.
- **Multi-file cross-module walkthroughs**: Use `tab.files[]` + `step.fileId` + `step.realLines` for real multi-file call chains.
- **Complete step coverage**: Every node on the right canvas should be reachable via at least one step.
- **Rich 3-column insights for EVERY step**:
  - `insights.mechanism` (**核心源码机制**): Cite exact files, structs/classes, functions, and data flow using inline `` `code` ``.
  - `insights.pitfalls` (**线上避坑与边界**): Real production edge cases, performance/concurrency traps, config gotchas, or reading-order tips.
  - `insights.interview` (**面试高频追问与答法**): Concrete `问：...\n答：...` pair grounded in the repository's actual design trade-offs.
- **Clean topology**: Assign `col` and `row` grid coordinates cleanly; use optional `fromSide`/`toSide`/`labelOffset` if fine-tuning complex topologies.

### Phase 3: Build & Ground-Truth Verify

Run the zero-dependency builder with `--repo-root` enabled:

```bash
python3 <skill_dir>/scripts/build_atlas.py <path/to/atlas-data.json> --repo-root <repo_path> -o <output-repo-atlas.html>
```

- If validation reports any schema or `[GROUNDING]` errors (missing files, out-of-bounds `lines`/`realLines`, dangling edges, missing insights), fix `atlas-data.json` and re-run until `[OK]` is printed.

### Phase 4: Deliver & Verify

1. Confirm the output `.html` exists and is self-contained (zero external CDN links — opens cleanly offline).
2. Present the user with:
   - Clickable file link to the generated `.html` file.
   - Summary of tabs, multi-file chains, step count, and verified commit SHA.
   - Quick feature tips (`←/→` step, `⌘K` global search, `↗ GitHub 原文`, `🔗` deep-link share, `⬇ SVG` diagram export, `📝 导出笔记` Markdown notes export).
