# Code Atlas Data Schema (`atlas-data.json`)

Use this schema when preparing the JSON input for `scripts/build_atlas.py`.

## Top-Level Structure

```json
{
  "project": {
    "name": "WeKnora",
    "monogram": "WK",
    "version": "v0.9.0",
    "commit": "53ce747b5",
    "repoUrl": "https://github.com/Tencent/WeKnora"
  },
  "tabs": [ ... ]
}
```

### `project`
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | Yes | Repository / project display name |
| `monogram` | string | No | 2-character badge text (defaults to first 2 chars of `name`) |
| `version` | string | No | Tag/version string (e.g. `v0.9.0`) |
| `commit` | string | No | Short commit SHA from `scan_repo.py` / `git rev-parse --short=9 HEAD` |
| `repoUrl` | string | No | GitHub repo URL; enables clickable `↗ GitHub 原文` line links automatically |

---

## `tabs[]`

Plan **4 to 6 tabs** per repository:
- **Tab 0 (`mode: "tree"`)**: Complete annotated directory tree + 6–9 architecture module overview graph.
- **Tabs 1..N (`mode: "code"`)**: Deep-dive execution chains supporting **single-file OR multi-file walkthroughs**.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | No | Unique tab slug |
| `label` | string | Yes | Topbar tab text, prefixed with index (e.g. `0. 项目目录`, `1. RAG 与 HNSW`) |
| `mode` | `"tree"` \| `"code"` | Yes | `"tree"` enables directory + `# 中文备注` highlighting; `"code"` enables syntax highlighting |
| `filePath` | string | Single-file | File path (used when `files` is omitted) |
| `fileSubtitle` | string | Single-file | Short summary of the file or tree scope |
| `startLine` | number | Optional | Real starting line number in the source file (default `1`) |
| `codeLines` | string[] | Single-file | Lines of code or tree (used when `files` is omitted) |
| `files` | FileObj[] | Multi-file | Array of source files inside this tab! Auto-switches file when stepping |
| `graphTitle` | string | Yes | Right pane canvas header title |
| `graphSubtitle` | string | No | Right pane canvas subtitle |
| `nodes` | Node[] | Yes | Architecture cards rendered on the right SVG canvas |
| `edges` | Edge[] | Yes | Directed relationships between nodes |
| `steps` | Step[] | Yes | Ordered walkthrough steps binding left lines, right nodes/edges, and bottom 3-column insights |

### Multi-File `files[]` Entry (Recommended for Cross-File Chains)
```json
{
  "id": "retriever",
  "label": "hybrid_retriever.go",
  "path": "internal/rag/hybrid_retriever.go",
  "subtitle": "双路召回与 RRF 融合",
  "startLine": 45,
  "codeLines": [ "..." ]
}
```
- When `files` is provided, each step specifies `"fileId": "retriever"`.
- Clicking a step or graph node automatically switches the left file tab and scrolls to the exact highlighted block.
- When `project.repoUrl` is a GitHub URL, the `↗ GitHub 原文` link automatically resolves to `blob/<commit>/<path>#L<realStart>-L<realEnd>`.

---

## `nodes[]`

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | Yes | Unique node ID within the tab |
| `badge` | string | No | Short step/module number shown in top-left circle (e.g. `"1"`..`"9"`) |
| `title` | string | Yes | Module / stage name (keep ≤ 14 CJK chars) |
| `subtitle` | string | No | Monospace path or symbol summary (e.g. `cmd/ · config/ · container`) |
| `loc` | string | No | Line range hint shown bottom-left (e.g. `目录 L1-L25` or `agent.go L42-L88`) |
| `tag` | string | No | Compact bottom-right pill tag (2–5 chars) |
| `category` | enum | Yes | One of: `"entry"`, `"core"`, `"storage"`, `"security"`, `"queue"`, `"external"` |
| `col`, `row` | number | Recommended | Grid coordinates (`0`, `1`, `2`, ...) |
| `x`, `y` | number | Optional | Explicit pixel coordinates (overrides `col`/`row`) |

---

## `edges[]`

The renderer automatically applies **Port Spreading** (distributing anchor points when multiple edges touch the same side of a node) and **Skip-Arching** (arching cleanly over intermediate cards).

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | No | Optional explicit ID; defaults to `"<from>-><to>"` |
| `from` | string | Yes | Source node `id` |
| `to` | string | Yes | Target node `id` |
| `label` | string | No | Compact verb/protocol label (2–6 chars) |
| `dashed` | boolean | No | `true` for async, optional, or cross-boundary calls |
| `fromSide` | `"top"\|"bottom"\|"left"\|"right"` | No | Explicit exit anchor side |
| `toSide` | `"top"\|"bottom"\|"left"\|"right"` | No | Explicit entry anchor side |
| `curveOffset` | number | No | Custom Bezier bend strength in pixels |
| `labelOffset` | `[number, number]` | No | Fine `[dx, dy]` nudge for edge label placement |

---

## `steps[]`

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `title` | string | Yes | Full step title |
| `shortTitle` | string | No | Compact quick-jump pill label (4–7 chars) |
| `fileId` | string | Multi-file | ID of the file inside `tab.files[]` |
| `lines` | `[number, number]` | Yes | Inclusive 1-based line range within `codeLines` |
| `realLines` | `[number, number]` | Optional | Exact line range in the real repo file (validated by `--repo-root` and used for GitHub links) |
| `nodeIds` | string[] | Yes | Active node ID(s) illuminated during this step |
| `edgeIds` | string[] | No | Explicit edge IDs to illuminate; defaults to incident edges |
| `insights.mechanism` | string | Yes | **核心源码机制** (supports `` `code` `` & `**bold**`) |
| `insights.pitfalls` | string | Yes | **线上避坑与边界** |
| `insights.interview` | string | Yes | **面试高频追问与答法** (`问：...\n答：...`) |
