# Personal Core OS（中文说明）

这是你的个人 AI 操作系统：

- Agent 负责执行
- 系统负责记忆、约束、复盘
- 你主要负责审计和战略批准

它不是传统后端应用，而是一个文件化控制面（Markdown/YAML/JSONL）。

## 北极星

把执行和判断分离，但长期保持对齐。

- 执行层：内容、项目、日常交互
- 判断层：决策、风控、心理稳定器、偏航纠正

## 架构要点

1. `core/` 是稳定内核（路由 + 全局规则）
2. `modules/` 是插件化能力
3. 渐进加载：`ROUTER -> MODULE -> DATA`
4. SSOT：规范和知识各有唯一来源
5. JSONL 只追加，保留完整历史
6. 路由规则配置化：`orchestrator/config/routes.json`

## 目录

```text
/
  README.md
  README-zh.md
  ROADMAP.md
  CHECKLIST.md
  core/
  modules/
    content/
    decision/
    profile/
    memory/
    _template/
  routines/
    cadence.yaml
    CADENCE.md
  orchestrator/
    README.md
    config/
      routes.json
      runtime.yaml
      providers.yaml
      retrieval.json
    retrieval/
    src/
    logs/
  scripts/
    append_jsonl.sh
    context_bundle.sh
    run_cycle.sh
```

## 模块说明

### `modules/content`

- 内容生产流水线
- 统一 voice、反模式、模板和发布日志

### `modules/decision`

- 决策中枢 + 风控 + 审计视图
- 高风险决策先 precommit，再落决策日志
- 输出 owner 审计报告（你只看异常和偏航）

### `modules/profile`

- 你的身份基线、偏好边界、心理稳定器
- 新增 `psych_profile.yaml` 和 `psych_observations.jsonl`
- 支持月度 profile snapshot

### `modules/memory`

- 每日记忆摄入
- 从 chats 提取范式（paradigm）
- 周度蒸馏可执行洞察

## 这套系统怎么跑

系统不自动“自运行”，而是你触发任务，Agent按协议执行：

1. 先读 `core/ROUTER.md`
2. 路由到模块
3. 读模块 `MODULE.md`
4. 只读当前任务必要文件
5. 生成输出或追加日志

路由是自动且可审计的：

- `inspect` / `run` 会显示路由原因、命中关键词、所选 skill、实际加载文件
- 路由关键词可在 `orchestrator/config/routes.json` 修改，不需要改内核文档

另外你现在有独立执行引擎层：

- `orchestrator/`（可手动模式、可选 API 模式）

## 快速使用

### 1) 先拿最小上下文

```bash
scripts/context_bundle.sh --task "extract chat paradigms from this week"
```

### 2) 按周期跑工作流

```bash
scripts/run_cycle.sh daily
scripts/run_cycle.sh weekly
scripts/run_cycle.sh monthly
```

### 3) 用 orchestrator 作为高层执行器

先做契约校验：

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py validate --strict
```

这一步会检查模块目录结构、skill 引用路径、JSONL schema header、路由配置和 cadence 引用关系。

先检查路由和计划：

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py inspect --task "run weekly decision review"
```

输出里会明确展示：

- 路由到哪个模块
- 为什么路由过去（`keyword_match` / `forced_module` / `fallback_default`）
- 命中了哪些关键词
- 实际加载了哪些文件

无 API 运行（生成 execution packet）：

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run --task "run weekly decision review" --provider manual
```

可选 API 运行：

```bash
OPENAI_API_KEY=... python3 /Users/closears/MyOS/orchestrator/src/main.py run --task "run weekly decision review" --provider openai
```

### 4) 自动调度执行（cadence）

按周期执行 `routines/cadence.yaml`：

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py schedule-run --cycle weekly --provider manual
```

只看 cron 提示（不执行）：

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py schedule-run --cycle weekly --scheduler cron
```

### 5) 偏航仪表盘（量化趋势）

生成 7 天指标：

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py metrics --window 7
```

生成 30 天指标：

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py metrics --window 30
```

### 6) Owner 一页报告（单页审计）

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py owner-report --window 7
```

每周 `schedule-run --cycle weekly` 默认会自动生成 owner 报告（可用 `--no-owner-report` 关闭）。

### 7) Guardrail 硬化（按域策略 + override 审计）

执行域策略检查：

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py guardrail-check --domain invest --decision-ref dc_20260303_001 --guardrail-check-id pc_20260303_001 --downside "Could violate weekly risk budget" --invalidation-condition "Price closes above invalidation level" --max-loss "0.5R" --disconfirming-signal "Falling volume confirmation"
```

如需 override，必须带理由和 owner 确认，并写入 `modules/decision/logs/guardrail_overrides.jsonl`。

### 8) 检索索引（长历史查询）

建立索引：

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py index
```

查询：

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py search --query "momentum" --top-k 5
```

带检索上下文执行：

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run --task "run weekly decision review" --provider manual --with-retrieval --retrieval-top-k 6
```

### 9) 高风险决策流程

1. `precommit_check.md`
2. `log_decision.md`（带 `guardrail_check_id`）
3. 周复盘 + 审计报告

### 10) 你的“第二大脑”流程

1. 每天记录 memory event
2. 每周抽取 chat patterns
3. 每月生成 profile snapshot
4. 你只审计异常并批准调整

## 数据纪律

- JSONL 不覆盖，只追加
- 每个 JSONL 第一行必须是 `_schema`
- 删除用 `status: archived`
- 跨模块只用 ID 引用，不复制内容
- orchestrator 生成输出默认使用 UTC 时间戳后缀（`YYYYMMDD_HHMMSS`），避免同日覆盖

## 当前版本

- v0.1：内核 + content + decision 基础
- v0.2：profile + memory + precommit guardrails
- v0.3-first：心理侧写、chat 范式提取、决策审计视图、周期 runbook
- v0.3-orchestrator：新增独立 `orchestrator/` 执行层抽象（manual + 可选 openai provider）
- v0.4-retrieval：新增可选检索索引、搜索命令、带检索上下文的执行
- v0.4-scheduling：新增 cadence 自动调度执行（`schedule-run`）与调度日志
- v0.5-drift：新增偏航仪表盘（`metrics` 命令）与指标快照日志
- v0.5-guardrails：新增按域 guardrail 硬化与 override 审计链
- v0.6-owner-report：新增 owner 一页报告与每周自动汇总
- v0.6-next：新增配置化路由（`routes.json`）、按 skill 的最小上下文加载、以及 `inspect`/`run` 的路由审计输出
- v0.6-next：新增插件契约校验命令（`validate`）和 CI 校验门禁
