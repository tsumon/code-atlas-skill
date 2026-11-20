# Code Atlas Skill (`code-atlas`)

> 将任意本地项目或 GitHub 开源仓库，**一键（One-shot）生成单文件、零依赖、可交互的「源码 · 架构图谱」HTML 页面**。

兼容 **Antigravity**、**Claude Code**、**Codex** 以及所有遵循 Agent Skills (`SKILL.md`) 规范的 AI 编程助手。

---

## ✨ 核心特性

- **零依赖单文件输出**：编译后的 `.html` 内联全部样式、脚本与数据，离线双击浏览器即可打开，无需构建工具或 CDN。
- **多专题标签页导航**：默认生成 `0. 项目目录`（完整中文备注目录树 + 6~9 大架构模块全景图）以及 `1..N` 条核心源码执行链路专题。
- **左侧源码 / 目录树 ↔ 右侧架构图双向联动**：
  - 左侧支持按步骤自动高亮并滚动定位行区间、分类快跳标签、实时关键词过滤、一键复制。
  - 右侧支持滚轮缩放、拖拽画布、一键适配、节点霓虹聚焦、连线流动光点动效（`⚡ 动效`）与「全部显示 / 聚焦当前」切换。
- **底部可折叠三栏精讲面板**：每个步骤同步展示：
  1. `⚙ 核心源码机制`（真实文件、函数与调用链）
  2. `⚠ 线上避坑与边界`（生产陷阱、并发/性能边界、阅读抓手）
  3. `🎯 面试高频追问与答法`（紧贴源码设计的深度 Q&A）
- **演练与效率快捷键**：`← / →` 步进切换、`▶ 自动演练`、`Cmd/Ctrl + K` 全局跨专题搜索、`☀️ 浅色 / 🌙 深色` 双主题切换、左右分栏自由拖拽。
- **内置 Schema 强校验器**：通过 `scripts/build_atlas.py` 编译前自动校验行号越界、悬空节点/连线、缺失精讲字段，大幅降低模型幻觉和生成坏页风险。

---

## 📁 仓库结构

```text
code-atlas-skill/
├── README.md
├── LICENSE
└── skills/
    └── code-atlas/
        ├── SKILL.md                   # Skill 主指令与 4 阶段工作流
        ├── assets/
        │   └── template.html          # 单文件交互式图谱渲染引擎（零外部依赖）
        ├── scripts/
        │   └── build_atlas.py         # JSON Schema 校验 + 单文件 HTML 编译器
        ├── references/
        │   ├── data-schema.md         # atlas-data.json 字段与布局规范
        │   └── design-spec.md         # 视觉配色与交互规范
        └── examples/
            └── demo-data.json         # 内置可运行示例数据
```

---

## 🚀 安装方式

### 方式 1：使用 `npx skills` 一键安装（推荐）

```bash
npx skills add tsumon/code-atlas-skill
```

### 方式 2：手动安装到各 Agent 全局目录

```bash
git clone https://github.com/tsumon/code-atlas-skill.git

# Antigravity 全局 Skill
mkdir -p ~/.gemini/config/skills
cp -r code-atlas-skill/skills/code-atlas ~/.gemini/config/skills/

# 通用 .agents 目录（Claude Code / Codex / 多 Agent 共享）
mkdir -p ~/.agents/skills
cp -r code-atlas-skill/skills/code-atlas ~/.agents/skills/
```

---

## 🎯 使用方法

安装后，直接向你的 AI 助手发一句需求即可触发：

> 「用 `code-atlas` 给 `https://github.com/Tencent/WeKnora` 生成一份交互式源码图谱，重点拆解项目目录、RAG 与 HNSW、ReAct Agent、安全与沙箱。」

或者针对当前本地打开的项目：

> 「用 `code-atlas` 给当前仓库做一份交互式架构源码图谱。」

### 快速本地试跑内置 Demo

```bash
python3 skills/code-atlas/scripts/build_atlas.py --demo -o ./demo-atlas.html
open ./demo-atlas.html
```

---

## 📄 License

[MIT](./LICENSE)
