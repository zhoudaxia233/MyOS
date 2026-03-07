# MyOS Next Steps (Cyber-Self Suggestion Mirror)

本文件是当前代码库的执行型下一步清单。目标不是重构系统，而是沿现有架构渐进演化。

## North Goal

先把 MyOS 做成透明、端到端、可审计的建议镜像系统，再逐步进入可治理委托。

## Stage 1 - Transparent Suggestion Pipeline (Current)

### 已完成

- 每次 `run`/Web `api_run` 生成结构化建议对象并写入 `orchestrator/logs/suggestions.jsonl`
- `run` 返回 `suggestion_id`
- 运行日志分类字段一致性修复（`object_type` / `proposal_target`）

### 下一步补齐

- 增加建议详情查询接口（按 `suggestion_id` 读取）
- 前端右侧 trace 区支持切换“本次 suggestion 详情”
- 在 suggestion 中补充更明确的 `invoked_rules`/`invoked_traits` 字段（先最小可用）

### 阶段完成标准

- 可以从任务输入一路追到 suggestion、run 记录、输出文件、上下文来源
- owner 能清楚看到“系统为何给出该建议”

## Stage 2 - Structured Owner Feedback Loop

### 需要新增对象

- `orchestrator/logs/owner_verdicts.jsonl`
- `orchestrator/logs/owner_corrections.jsonl`

### 需要新增能力

- verdict: `accept | modify | reject`
- correction: 记录“不像我”的具体原因、替代判断、目标层（rule/skill/profile/cognition/principle）
- Web UI 增加审核控件与反馈提交

### 阶段完成标准

- 每条 suggestion 都能被结构化裁决和修正
- 修正可追踪、可检索、可复盘

## Stage 3 - Candidate Promotion Workflows

### 需要新增对象

- `modules/decision/logs/rule_candidates.jsonl`
- `modules/decision/logs/skill_candidates.jsonl`
- `modules/profile/logs/profile_trait_candidates.jsonl`
- `modules/cognition/logs/schema_candidates.jsonl`
- `modules/principles/logs/principle_candidates.jsonl`

### 需要新增能力

- `candidate -> reviewed -> promoted|rejected` 状态机
- promotion 必须带 `approval_ref`
- runtime 只调用 promoted 真值，不直接调用 candidate

### 阶段完成标准

- 抽取/蒸馏结果可进入候选池，但不会直接覆盖长期真值
- owner 能显式控制“何时升级为系统真值”

## Stage 4 - Limited Delegation With Explicit Review

### 需要新增对象

- `modules/decision/logs/delegated_action_proposals.jsonl`
- `modules/decision/logs/delegated_action_runs.jsonl`

### 需要新增能力

- 仅低风险白名单动作可委托
- 委托前后都写审计记录（proposal/run/result）
- 默认需要 owner 预批准

### 阶段完成标准

- 系统可执行有限动作，但审计链完整且可回退

## Stage 5 - Governed Higher Autonomy

### 方向

- 在 Stage 1-4 稳定后，扩大低风险自动执行比例
- owner 角色切换为审计、例外处理、策略纠偏
- 持续漂移监控，避免黑箱化

### 阶段完成标准

- 自动执行能力上升，同时可解释性与治理性不下降

## Explicit Non-Goals

- 不做 greenfield 重写
- 不移除 memory/decision/profile/cognition/principles 抽取与蒸馏主链路
- 不把系统降级为通用笔记或纯 RAG 助手
- 不允许 noisy 输入直接覆盖长期真值
- 不跳过 owner 审核直接进入高风险自治

