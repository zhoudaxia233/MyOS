# Personal Core OS（中文说明）

Personal Core OS 是一个给你和 AI agent 协作使用的“个人核心操作系统”。

它不是传统后端应用，而是一套可执行的协议层：

- 用 `core/` 做路由和全局规则
- 用 `modules/` 做插件化能力
- 用 `JSONL` 做可追溯、可追加的历史记忆

## 北极星

把“执行”与“判断”分离，但长期保持一致。

- 执行：写作、项目推进、记忆摄入
- 判断：决策、取舍、对齐长期目标、迭代启发式

## 这个项目到底怎么运行

当前运行方式是：你触发任务，Agent 按仓库协议执行。

1. 永远先读 `core/ROUTER.md`
2. 路由到一个模块
3. 读该模块 `MODULE.md`
4. 只加载任务所需的数据/日志/模板
5. 产出文件或追加日志

两跳原则：

- `ROUTER -> MODULE -> DATA`

## 仓库结构

```text
/
  README.md
  README-zh.md
  ROADMAP.md
  CHECKLIST.md
  core/
    ROUTER.md
    RULES.md
    SCHEMAS.md
    GLOSSARY.md
  modules/
    content/
    decision/
    profile/
    memory/
    _template/
  scripts/
    append_jsonl.sh
    context_bundle.sh
```

## 各模块作用

### `modules/content`

内容生产模块：选题、草稿、编辑、发布记录。

- SSOT：`voice.yaml`、`anti_patterns.md`、模板
- 日志：`ideas.jsonl`、`posts.jsonl`

### `modules/decision`

决策模块：记录决策、失败和经验，并做周复盘。

- SSOT：`heuristics.yaml`、`impulse_guardrails.yaml`
- 日志：`decisions/failures/experiences/precommit_checks.jsonl`
- 新增：高风险决策前置防冲动检查（precommit）

### `modules/profile`

个人画像与长期方向模块：

- SSOT：`identity.yaml`、`operating_preferences.yaml`
- 日志：`profile_changes.jsonl`、`trigger_events.jsonl`
- 用途：把“你是谁、长期目标、偏好和边界”显式化

### `modules/memory`

进化记忆模块：

- SSOT：`memory_policy.yaml`
- 日志：`memory_events.jsonl`、`memory_insights.jsonl`
- 用途：每天摄入事件，按周蒸馏可复用模式

### `modules/_template`

新模块脚手架模板。

## 你最关心的三个问题

### 1) 这是不是 context engineering？

是。核心就是：

- 路由控制（读哪个模块）
- 上下文最小化（只读必要文件）
- 行为约束（规则、schema、skills）

### 2) 谁来“发上下文”？

当前是你在对话里触发，Agent按仓库协议加载。

现在新增了 `scripts/context_bundle.sh`，可先给出建议路由和最小文件集合。

### 3) 这个系统能体现“我在变化”吗？

能，且这是 v0.2 的重点：

- `profile` 记录长期方向和偏好变化
- `memory` 记录日常事件并蒸馏洞察
- `decision` 通过 precommit guardrail 限制冲动决策

## 快速使用

### 1. 先拿最小上下文建议

```bash
scripts/context_bundle.sh --task "log this high-risk investment decision"
```

### 2. 需要写作

走 `content` 模块，产出写到 `modules/content/outputs/`。

### 3. 需要决策记录

先跑 precommit，再写 `decisions.jsonl`。

### 4. 需要更新你自己的方向

用 `modules/profile/skills/update_profile.md`。

### 5. 需要沉淀日常对话洞察

用 `modules/memory/skills/ingest_memory.md`，每周再 `distill_weekly.md`。

## 脚本

### 安全追加 JSONL

```bash
scripts/append_jsonl.sh <jsonl_file> '<json_object>'
```

### 路由与上下文规划

```bash
scripts/context_bundle.sh --task "<你的任务>"
```

## 版本

- v0.1：内核 + content + decision 基础
- v0.2：新增 profile + memory、decision 防冲动机制、context bundle runner
