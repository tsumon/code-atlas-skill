# Code Atlas Visual & Interaction Design Spec

This reference documents the aesthetic system behind `assets/template.html`, useful when customizing the layout or building bespoke extensions.

## Layout Architecture
1. **Top Navigation Bar (`48px`)**:
   - Left: Brand monogram square (`26x26`, blue-to-cyan gradient), `<Repo> · 源码图谱`, clickable commit SHA pill.
   - Center: Segmented pill tab bar (`0. 项目目录` + `1..N` domain chain tabs).
   - Right: Stepper (`◀ 上一步`, `x/y`, `下一步 ▶`), `▶ 自动演练`, `🔍 搜索` (`Cmd/Ctrl+K`), `☀️ 浅色 / 🌙 深色`.
2. **Main Split Workspace (Flex Row, Resizable Divider)**:
   - **Left Pane (`48%`)**:
     - Horizontal quick-jump pills with category color dots & active bottom indicator bar.
     - Live keyword filter input + one-click Copy button.
     - File metadata & bidirectional sync indicator strip.
     - Scrollable line-numbered monospace viewport with active-step floating banner, blue-cyan line highlight, and dimmed non-active context.
   - **Right Pane (`52%`)**:
     - Header with graph title, subtitle, and toolbar (`−`, `适配`, `+`, `⚡ 动效`, `全部显示`).
     - Dot-grid pan/zoom SVG stage (`wheel` zoom around pointer, drag pan, double-click fit).
     - Rounded node cards (`248x104`) with numbered category badge, monospace path subtitle, dashed internal divider, line-range locator, and category pill tag.
     - Cubic Bezier edges with arrowheads, pill labels, animated dashed flow, and traveling pulse dot when active.
     - Footer legend (`入口` / `核心引擎` / `存储/索引` / `安全/门禁` / `队列/流` / `外部/护栏`) + shortcut hints.
3. **Bottom Collapsible Deep-Dive Drawer**:
   - Header: `Step N · <Title>` + file/line locator pill + `收起精讲 ▾` toggle.
   - 3-column responsive grid (`repeat(3, minmax(0, 1fr))`):
     - `⚙ 核心源码机制` (`#38bdf8` top border)
     - `⚠ 线上避坑与边界` (`#f59e0b` top border)
     - `🎯 面试高频追问与答法` (`#f43f5e` top border)

## Theme Tokens
- **Dark Mode (Default — Obsidian Atlas)**:
  - Canvas `#070c15`, Code `#09101c`, Panels `#0c1422`, Cards `#10192b`
  - Text `#e6edf7` / `#94a3b8`, Comments `#4ade80`, Directories `#38bdf8`, Highlight `#2563eb`
- **Light Mode (Daylight Slate)**:
  - Canvas `#f3f6fb`, Code `#f8fafc`, Panels `#ffffff`, Cards `#ffffff`
  - Text `#0f172a` / `#475569`, Comments `#15803d`, Directories `#0284c7`, Highlight `#2563eb`

## Content Quality Bar
- **Zero Placeholder Text**: Every node, edge, and 3-column insight must reflect actual files, symbols, and architecture discovered in the target codebase.
- **Line Accuracy**: Every `step.lines` interval must strictly match `1 <= start <= end <= codeLines.length`.
- **Readable Tree Alignment**: In `mode: "tree"`, pad paths with spaces so inline `# 中文备注` comments form a crisp vertical column.
- **No Overlapping Cards**: Prefer `col` / `row` grid coordinates (`3x3` for directory overview; `2x3`, `3x2`, or linear pipelines for deep-dive tabs) so cards and edge labels always breathe cleanly.
