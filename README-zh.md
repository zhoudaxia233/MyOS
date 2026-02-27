# Personal Core OS（中文说明）

这是一个给你和 AI agent 协作使用的“个人核心操作系统”。

它不是传统 App（没有必须先跑起来的后端服务），而是一套 **可执行的工作协议 + 记忆结构**：

- 你提任务
- Agent 按路由和模块规则加载最少上下文
- 产出结果并把关键记录追加到日志

## 为什么是文件项目

本仓库用 Markdown/YAML/JSONL 做控制面：

- Markdown：流程、规则、技能说明
- YAML：稳定配置（如 voice、heuristics）
- JSONL：时间序列日志（append-only）

它的目标是：

- 把执行和判断分离
- 让日常动作和长期方向保持一致
- 保留完整可审计历史

## 核心设计思想

1. 内核小而稳定（`core/`）
2. 业务能力插件化（`modules/`）
3. 渐进加载（只读当前任务必需文件）
4. SSOT（单一事实源）
5. 日志只追加，不改历史

## 仓库结构概览

```text
/
  README.md            # 英文主文档
  README-zh.md         # 中文文档
  ROADMAP.md           # 当前讨论总结与演进路线
  CHECKLIST.md         # 验收清单
  core/                # 内核：路由、规则、schema、术语
  modules/             # 插件模块
  scripts/             # 辅助脚本
```

## core 内核怎么用

### `core/ROUTER.md`

永远先读。决定任务属于哪个模块。

### `core/RULES.md`

全局约束：不编造、事实/推断分离、日志 append-only。

### `core/SCHEMAS.md`

统一 ID、时间戳、JSONL schema 规范。

### `core/GLOSSARY.md`

跨模块通用术语定义。

## modules 模块怎么用

### 内容模块 `modules/content/`

用途：从选题到发布记录的内容流水线。

关键文件：

- `MODULE.md`：模块总规则与流程
- `data/voice.yaml`：语气和风格 SSOT
- `data/anti_patterns.md`：禁用表达和结构陷阱
- `data/templates/`：内容模板
- `logs/ideas.jsonl`：创意池
- `logs/posts.jsonl`：发布日志
- `skills/write_fahou_message.md`：写作任务说明

### 决策模块 `modules/decision/`

用途：记录决策、失败复盘、经验信号，并做每周回顾。

关键文件：

- `MODULE.md`：模块总规则与流程
- `data/heuristics.yaml`：启发式规则 SSOT
- `logs/decisions.jsonl`：决策日志
- `logs/failures.jsonl`：失败日志
- `logs/experiences.jsonl`：经验日志
- `skills/log_decision.md`：决策记录技能
- `skills/weekly_review.md`：周回顾技能

### 模板模块 `modules/_template/`

用于新建插件模块时复制。

## 这个系统“怎么执行”

当前是“人触发 + Agent 执行”：

1. 你提出任务
2. Agent 读 `ROUTER.md` 路由
3. 只读对应 `MODULE.md`
4. 再读任务需要的数据文件
5. 生成输出或追加日志

两跳原则：

- `ROUTER -> MODULE -> DATA`

## 你个人特征如何进入系统

v0.1 目前是稳定骨架，个性化还在下一阶段。

现阶段已经可沉淀你的变化：

- 决策过程进 `decisions.jsonl`
- 失败复盘进 `failures.jsonl`
- 关键体验进 `experiences.jsonl`
- 每周复盘将这些变化转为可执行启发式

因此它不是“规则写死”，而是“内核稳定 + 数据进化”。

## 日志安全写入

使用脚本（只追加，不改历史）：

```bash
scripts/append_jsonl.sh <jsonl_file> '<json_object>'
```

示例：

```bash
scripts/append_jsonl.sh modules/decision/logs/decisions.jsonl '{"id":"dc_20260227_003","created_at":"2026-02-27T09:00:00Z","status":"active","domain":"project","decision":"Ship v1","options":["ship","delay"],"reasoning":"Scope complete","risks":["minor bugs"],"expected_outcome":"faster feedback","time_horizon":"1 week","confidence":7}'
```

## 使用建议（你的第一周）

1. 每做一个重要决定就记录到 `decisions.jsonl`
2. 每出现一次明显失误就记录到 `failures.jsonl`
3. 每周固定做一次 `weekly_review`
4. 内容生产统一走 `content` 模块，避免临场风格漂移

## 版本状态

- 当前：v0.1（内核 + content + decision + 日志纪律）
- 下一步：v0.2（个人画像、记忆蒸馏、冲动防护规则）
