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
| `commit` | string | No | Short commit SHA from `git rev-parse --short=9 HEAD` (shown in topbar pill) |
| `repoUrl` | string | No | Clickable URL attached to the commit pill |

---

## `tabs[]`

Plan **4 to 6 tabs** per repository:
- **Tab 0 (`mode: "tree"`)**: Complete annotated directory tree + 6–9 architecture module overview graph.
- **Tabs 1..N (`mode: "code"`)**: Deep-dive execution chains (e.g., `1. RAG 与检索`, `2. ReAct Agent 循环`, `3. 文档解析流水线`, `4. 安全与沙箱`).

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | No | Unique tab slug |
| `label` | string | Yes | Topbar tab text, prefixed with index (e.g. `0. 项目目录`, `1. RAG 与 HNSW`) |
| `mode` | `"tree"` \| `"code"` | Yes | `"tree"` enables directory + `# 中文备注` highlighting; `"code"` enables source syntax highlighting |
| `filePath` | string | Yes | File path or repo root label displayed in left meta bar & bottom drawer |
| `fileSubtitle` | string | No | Short summary of the file or tree scope |
| `graphTitle` | string | Yes | Right pane canvas header title |
| `graphSubtitle` | string | No | Right pane canvas subtitle |
| `codeLines` | string[] | Yes | Array of lines (1-indexed in UI). For `"tree"` mode, align `# 中文备注` cleanly around column 34–42. For `"code"` mode, paste real curated source excerpts with brief Chinese inline comments |
| `nodes` | Node[] | Yes | Architecture cards rendered on the right SVG canvas |
| `edges` | Edge[] | Yes | Directed relationships between nodes |
| `steps` | Step[] | Yes | Ordered walkthrough steps binding left lines, right nodes/edges, and bottom 3-column insights |

---

## `nodes[]`

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | Yes | Unique node ID within the tab |
| `badge` | string | No | Short step/module number shown in top-left circle (e.g. `"1"`..`"9"`) |
| `title` | string | Yes | Module / stage name (keep ≤ 14 CJK chars so it never clips) |
| `subtitle` | string | No | Monospace path or symbol summary (e.g. `cmd/ · config/ · container`) |
| `loc` | string | No | Line range hint shown bottom-left (e.g. `目录 L1-L25` or `agent.go L42-L88`) |
| `tag` | string | No | Compact bottom-right pill tag (2–5 chars, e.g. `启动装配`, `多租户`, `核心编排`) |
| `category` | enum | Yes | One of: `"entry"`, `"core"`, `"storage"`, `"security"`, `"queue"`, `"external"` |
| `col` | number | Recommended | Grid column index (`0`, `1`, `2`, ...). Automatically spaced cleanly |
| `row` | number | Recommended | Grid row index (`0`, `1`, `2`, ...) |
| `x`, `y` | number | Optional | Explicit pixel coordinates (overrides `col`/`row` when custom topology is needed) |

### Semantic Category Palette
- `entry` (天蓝): CLI / HTTP / Server Entrypoints, Config & Bootstrap
- `core` (深蓝): Core Domain Logic, Orchestrators, Agents, Schedulers
- `storage` (翠绿): Databases, Vector Stores, Indexes, Caches, File Parsers
- `security` (玫红): Auth, RBAC, Guardrails, Sandboxes, Credential Vaults
- `queue` (紫罗兰): Async Queues, Event Streams, SSE, Pipelines, MCP / Model Routers
- `external` (琥珀金): Frontend, Migrations, Docker/Deploy, External APIs, Testing

---

## `edges[]`

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | No | Optional explicit ID; defaults to `"<from>-><to>"` |
| `from` | string | Yes | Source node `id` |
| `to` | string | Yes | Target node `id` |
| `label` | string | No | Compact verb/protocol label (2–6 chars, e.g. `DI装配`, `鉴权拦截`, `检索召回`) |
| `dashed` | boolean | No | `true` for async, optional, or cross-boundary calls |

---

## `steps[]`

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `title` | string | Yes | Full step title (shown in banner & bottom drawer) |
| `shortTitle` | string | No | Compact label for left-pane quick-jump pill (4–7 chars) |
| `lines` | `[number, number]` | Yes | Inclusive 1-based line range `[startLine, endLine]` in `codeLines` |
| `nodeIds` | string[] | Yes | One or more node IDs illuminated during this step |
| `edgeIds` | string[] | No | Specific edge IDs (`"<from>-><to>"` or custom `edge.id`) to illuminate; if omitted, edges connected to active nodes illuminate automatically |
| `insights` | object | Yes | Three mandatory structured fields (supports inline `` `code` `` and `**bold**`) |
| `insights.mechanism` | string | Yes | **核心源码机制**: Concrete files, symbols, data structures, and control flow |
| `insights.pitfalls` | string | Yes | **线上避坑与边界**: Production edge cases, failure modes, config traps, reading tips |
| `insights.interview` | string | Yes | **面试高频追问与答法**: Format as `问：...\n答：...` grounded in actual repo design |
