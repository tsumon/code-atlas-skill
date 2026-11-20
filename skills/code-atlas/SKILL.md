---
name: code-atlas
description: >-
  Generate a zero-dependency, single-file interactive source-code architecture atlas
  (源码图谱 HTML) for any local repository or GitHub project. Features multi-tab navigation
  (annotated directory tree + deep-dive execution chains), bidirectional code-to-graph
  highlighting, zoomable animated SVG architecture diagrams, cross-tab search, auto-play
  walkthrough, dark/light themes, and a 3-column collapsible deep-dive drawer
  (核心源码机制 / 线上避坑与边界 / 面试高频追问与答法). Use whenever the user asks to
  visualize, map, explain, or create an interactive source-code atlas / architecture guide
  for a codebase.
---

# Code Atlas (`code-atlas`)

Build a polished, standalone single-file HTML **Interactive Source-Code Atlas** for any repository, backed by **verified real source code**.

## Non-Negotiable Grounding Rules

1. **Never fabricate file paths, symbols, or line numbers.** Every directory entry, code excerpt, function name, and architectural claim must come from reading the actual repository.
2. **Capture real metadata.** Read the exact commit SHA (`git rev-parse --short=9 HEAD`) and version/tag if available.
3. **Validate before delivering.** Always compile through [`scripts/build_atlas.py`](./scripts/build_atlas.py) so schema, line bounds, node IDs, and edge links are verified with zero errors.

---

## Step-by-Step Workflow

### Phase 1: Inspect the Target Repository

1. Locate the codebase:
   - If given a local path, inspect it directly.
   - If given a GitHub URL, shallow-clone it (`git clone --depth 1 <url>`) into a clean temporary or workspace directory (or inspect via `gh`/API for small repos).
2. Gather ground-truth structure:
   - Run `git rev-parse --short=9 HEAD` and check version files (`VERSION`, `package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`).
   - Map top-level directories, entry points (`main.*`, `cmd/`, `src/index.*`, `app/`), routers/handlers, core domain engines, storage/index layers, security/middleware, queues/workers, and deployment configs.
3. Plan **4 to 6 tabs** (unless the user specifies custom topics):
   - **Tab 0 (`0. 项目目录`, `mode: "tree"`)**: Complete annotated directory tree (60–200 lines) paired with a **6 to 9 module architecture overview** (`3x2` or `3x3` grid).
   - **Tabs 1..N (`mode: "code"`)**: The 3–5 highest-leverage core execution chains of the project (e.g., request lifecycle, RAG/indexing pipeline, Agent loop, auth/sandbox, async worker). For each tab, read the real source files and curate a tight, faithful code walkthrough (`codeLines`) with concise Chinese inline comments.

### Phase 2: Author `atlas-data.json`

Read [`references/data-schema.md`](./references/data-schema.md) for the exact JSON specification (and [`references/design-spec.md`](./references/design-spec.md) if customizing layout/styles).

Quality checklist while authoring `atlas-data.json`:
- **Aligned tree annotations**: In Tab 0 (`mode: "tree"`), pad file/dir paths with spaces so inline `# 中文备注` comments line up cleanly.
- **Complete step coverage**: Every node on the right canvas should be reachable via at least one step (so clicking any node smoothly jumps to its exact line range on the left).
- **Rich 3-column insights for EVERY step**:
  - `insights.mechanism` (**核心源码机制**): Cite exact files, structs/classes, functions, and data flow using inline `` `code` ``.
  - `insights.pitfalls` (**线上避坑与边界**): Real production edge cases, performance/concurrency traps, config gotchas, or reading-order tips.
  - `insights.interview` (**面试高频追问与答法**): Concrete `问：...\n答：...` pair grounded in the repository's actual design trade-offs.
- **Clean topology**: Assign `col` and `row` grid coordinates thoughtfully so edges flow left-to-right / top-to-bottom without clutter. Use semantic categories (`entry`, `core`, `storage`, `security`, `queue`, `external`).

### Phase 3: Build & Validate the Standalone HTML

Run the zero-dependency builder script:

```bash
python3 <skill_dir>/scripts/build_atlas.py <path/to/atlas-data.json> -o <output-repo-atlas.html>
```

- If validation reports any errors (out-of-bounds `lines`, dangling `edge.from`/`edge.to`, missing `insights`), fix `atlas-data.json` and re-run until `[OK]` is printed.
- To test the pipeline quickly at any time, run:
  ```bash
  python3 <skill_dir>/scripts/build_atlas.py --demo -o /tmp/demo-atlas.html
  ```

### Phase 4: Deliver & Verify

1. Confirm the output `.html` exists and is self-contained (zero external CSS/JS CDN links — opens cleanly offline by double-clicking).
2. Provide the user with:
   - Clickable file link to the generated `.html` file.
   - Summary of the tabs, step count, and commit SHA covered.
   - Tip on key interactive shortcuts (`←/→` step navigation, `Cmd/Ctrl + K` global search, scroll/drag zoom, bidirectional node/code click).
