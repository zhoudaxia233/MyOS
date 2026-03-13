const chatLog = document.getElementById("chatLog");
const latestMessage = document.getElementById("latestMessage");
const chatLogWrap = document.getElementById("chatLogWrap");
const toggleMessagesBtn = document.getElementById("toggleMessagesBtn");
const taskForm = document.getElementById("taskForm");
const taskInput = document.getElementById("taskInput");
const moduleSelect = document.getElementById("moduleSelect");
const providerSelect = document.getElementById("providerSelect");
const modelInput = document.getElementById("modelInput");
const retrievalToggle = document.getElementById("retrievalToggle");
const retrievalTopK = document.getElementById("retrievalTopK");
const inspectBtn = document.getElementById("inspectBtn");
const statusBadge = document.getElementById("statusBadge");
const themeToggle = document.getElementById("themeToggle");
const settingsToggle = document.getElementById("settingsToggle");
const copyOutputBtn = document.getElementById("copyOutputBtn");
const quickIngestBtn = document.getElementById("quickIngestBtn");
const learningPacketBtn = document.getElementById("learningPacketBtn");
const learningImportBtn = document.getElementById("learningImportBtn");
const mvpFlowBtn = document.getElementById("mvpFlowBtn");
const demoModeBtn = document.getElementById("demoModeBtn");
const learningDirectInput = document.getElementById("learningDirectInput");
const learningTitleInput = document.getElementById("learningTitleInput");
const learningCertainty = document.getElementById("learningCertainty");
const learningSourceInput = document.getElementById("learningSourceInput");
const learningResponseInput = document.getElementById("learningResponseInput");
const auditQuickRunBtn = document.getElementById("auditQuickRunBtn");
const auditGuide = document.getElementById("auditGuide");
const auditZeroState = document.getElementById("auditZeroState");
const auditManualActions = document.getElementById("auditManualActions");
const auditShowManualBtn = document.getElementById("auditShowManualBtn");
const auditAdvancedActions = document.getElementById("auditAdvancedActions");
const entrypointTabs = document.querySelectorAll(".entrypoint-tab");
const entrypointHint = document.getElementById("entrypointHint");
const taskConsolePanel = document.getElementById("taskConsolePanel");
const learningConsolePanel = document.getElementById("learningConsolePanel");
const auditConsolePanel = document.getElementById("auditConsolePanel");

const routeTrace = document.getElementById("routeTrace");
const planTrace = document.getElementById("planTrace");
const loadedFiles = document.getElementById("loadedFiles");
const resultTrace = document.getElementById("resultTrace");
const suggestionTrace = document.getElementById("suggestionTrace");
const outputPreview = document.getElementById("outputPreview");
const outputTokenMeta = document.getElementById("outputTokenMeta");
const suggestionAcceptBtn = document.getElementById("suggestionAcceptBtn");
const suggestionModifyBtn = document.getElementById("suggestionModifyBtn");
const suggestionRejectBtn = document.getElementById("suggestionRejectBtn");
const cognitionCards = document.getElementById("cognitionCards");
const reviewInboxLead = document.getElementById("reviewInboxLead");
const reviewCountSuggestion = document.getElementById("reviewCountSuggestion");
const reviewCountReview = document.getElementById("reviewCountReview");
const reviewCountPromote = document.getElementById("reviewCountPromote");
const reviewCountTodo = document.getElementById("reviewCountTodo");
const suggestionReviewCount = document.getElementById("suggestionReviewCount");
const reviewQueueCount = document.getElementById("reviewQueueCount");
const promoteQueueCount = document.getElementById("promoteQueueCount");
const ownerTodoCount = document.getElementById("ownerTodoCount");
const reviewStageFilter = document.getElementById("reviewStageFilter");
const reviewTypeFilter = document.getElementById("reviewTypeFilter");
const reviewSourceFilter = document.getElementById("reviewSourceFilter");
const reviewAgeFilter = document.getElementById("reviewAgeFilter");
const reviewFilterResetBtn = document.getElementById("reviewFilterResetBtn");
const reviewFilterMeta = document.getElementById("reviewFilterMeta");
const reviewPresetButtons = Array.from(document.querySelectorAll("[data-review-preset]"));
const suggestionReviewList = document.getElementById("suggestionReviewList");
const auditTimelineKindFilter = document.getElementById("auditTimelineKindFilter");
const auditTimelineStatusFilter = document.getElementById("auditTimelineStatusFilter");
const auditTimelineAgeFilter = document.getElementById("auditTimelineAgeFilter");
const auditTimelineResetBtn = document.getElementById("auditTimelineResetBtn");
const auditTimelineMeta = document.getElementById("auditTimelineMeta");
const auditTimelineCount = document.getElementById("auditTimelineCount");
const auditTimelineList = document.getElementById("auditTimelineList");
const reviewCandidates = document.getElementById("reviewCandidates");
const promoteCandidates = document.getElementById("promoteCandidates");
const ownerTodos = document.getElementById("ownerTodos");
const learningLifecycle = document.getElementById("learningLifecycle");
const candidatePipeline = document.getElementById("candidatePipeline");
const suggestionReviewSummary = document.getElementById("suggestionReviewSummary");
const auditSupportSubject = document.getElementById("auditSupportSubject");
const auditJudgmentDetailBlock = document.getElementById("auditJudgmentDetailBlock");
const suggestionDetailCard = document.getElementById("suggestionDetailCard");
const auditDetailRawFold = document.getElementById("auditDetailRawFold");
const suggestionDetailActions = document.getElementById("suggestionDetailActions");
const mvpGuide = document.getElementById("mvpGuide");
const demoSummary = document.getElementById("demoSummary");
const settingsModal = document.getElementById("settingsModal");
const settingsClose = document.getElementById("settingsClose");
const settingsSave = document.getElementById("settingsSave");
const settingsApiKey = document.getElementById("settingsApiKey");
const settingsDeepseekApiKey = document.getElementById("settingsDeepseekApiKey");
const settingsOpenaiBaseUrl = document.getElementById("settingsOpenaiBaseUrl");
const settingsOpenaiModel = document.getElementById("settingsOpenaiModel");
const settingsDefaultProvider = document.getElementById("settingsDefaultProvider");
const settingsRoutingModel = document.getElementById("settingsRoutingModel");
const settingsDeepseekModel = document.getElementById("settingsDeepseekModel");
const settingsDeepseekBaseUrl = document.getElementById("settingsDeepseekBaseUrl");
const settingsDecisionProvider = document.getElementById("settingsDecisionProvider");
const settingsDecisionModel = document.getElementById("settingsDecisionModel");
const settingsContentProvider = document.getElementById("settingsContentProvider");
const settingsContentModel = document.getElementById("settingsContentModel");
const settingsCognitionProvider = document.getElementById("settingsCognitionProvider");
const settingsCognitionModel = document.getElementById("settingsCognitionModel");
const settingsUiLanguage = document.getElementById("settingsUiLanguage");
const auditMachineFold = document.getElementById("auditMachineFold");
const learningReviewModal = document.getElementById("learningReviewModal");
const learningReviewTitle = document.getElementById("learningReviewTitle");
const learningReviewMeta = document.getElementById("learningReviewMeta");
const learningReviewNote = document.getElementById("learningReviewNote");
const learningReviewStatementWrap = document.getElementById("learningReviewStatementWrap");
const learningReviewStatement = document.getElementById("learningReviewStatement");
const learningReviewSubmit = document.getElementById("learningReviewSubmit");
const learningReviewCancel = document.getElementById("learningReviewCancel");
const learningReviewClose = document.getElementById("learningReviewClose");
const suggestionReviewModal = document.getElementById("suggestionReviewModal");
const suggestionReviewTitle = document.getElementById("suggestionReviewTitle");
const suggestionReviewMeta = document.getElementById("suggestionReviewMeta");
const suggestionReviewNote = document.getElementById("suggestionReviewNote");
const suggestionReviewReplacementWrap = document.getElementById("suggestionReviewReplacementWrap");
const suggestionReviewReplacement = document.getElementById("suggestionReviewReplacement");
const suggestionReviewReasonWrap = document.getElementById("suggestionReviewReasonWrap");
const suggestionReviewReason = document.getElementById("suggestionReviewReason");
const suggestionReviewTargetWrap = document.getElementById("suggestionReviewTargetWrap");
const suggestionReviewTarget = document.getElementById("suggestionReviewTarget");
const suggestionReviewSubmit = document.getElementById("suggestionReviewSubmit");
const suggestionReviewCancel = document.getElementById("suggestionReviewCancel");
const suggestionReviewClose = document.getElementById("suggestionReviewClose");
let latestOutputPath = null;
let latestOutputProvider = null;
let latestSuggestionId = null;
let auditSupportTarget = { kind: null, id: null };
let auditSupportRevealTimer = null;
let settingsCache = null;
let uiLanguage = "zh";
let learningReviewDraft = null;
let suggestionReviewDraft = null;
let auditManualForcedVisible = false;
let messagesExpanded = false;
let latestMessagePayload = { role: null, text: "" };
let auditUiSnapshot = {
  owner_todos: [],
  learning_candidates: [],
  candidate_pipeline_summary: {},
  suggestion_review_queue: {
    pending_total: 0,
    reviewed_total: 0,
    pending: [],
    recently_reviewed: [],
  },
};
let reviewFilterState = {
  stage: "all",
  type: "all",
  source: "",
  age: "all",
};
let auditTimelineFilterState = {
  kind: "all",
  status: "all",
  age: "all",
};
const LEARNING_SOURCE_DEFAULT = "notes";
const REVIEW_PRESET_STORAGE_KEY = "pcos_audit_review_preset_v1";
const REVIEW_FILTER_PRESETS = Object.freeze({
  all: { stage: "all", type: "all", source: "", age: "all" },
  review: { stage: "review", type: "all", source: "", age: "all" },
  promote: { stage: "promote", type: "all", source: "", age: "all" },
  recent: { stage: "all", type: "all", source: "", age: "7d" },
});

const I18N = {
  zh: {
    doc_title: "Personal Core OS | 审计中心",
    app_title: "Personal Core OS",
    app_subtitle: "审计中心",
    nav_workspace: "工作台",
    nav_audit: "审计中心",
    status_connecting: "连接中...",
    status_connected: "已连接",
    status_offline: "离线",
    tab_task: "任务执行",
    tab_learning: "学习与进化",
    tab_audit: "审计台",
    hint_task: "这是任务执行入口（可选）。常规治理请切换到审计台。",
    hint_learning: "学习与进化已迁移到工作台。这里主要做审计与候选治理。",
    hint_audit: "在这里做漂移检查、报告复核和学习与进化候选治理。",
    audit_kicker: "Owner Review",
    review_inbox_title: "待判断事项",
    review_inbox_desc: "先处理任务建议、学习候选与 Owner 待办，再按需查看生命周期、报告和机器轨迹。",
    review_inbox_lead_suggestion: "当前有任务建议等待判断。先做 Accept / Modify / Reject，再处理学习候选或其他治理事项。",
    review_inbox_lead_review: "当前有待复核候选。先做 Accept / Modify / Reject，再决定哪些值得进入下一阶段。",
    review_inbox_lead_promote: "当前有候选已经通过复核。Accept 不等于 Promote，请单独判断是否值得晋升。",
    review_inbox_lead_todo: "当前主要是 Owner 待办。先处理这些异常与判断事项，再回看支持上下文。",
    review_inbox_lead_empty: "当前收件箱为空。你可以回到工作台补充学习素材，或按需运行一次 quick audit。",
    review_inbox_lead_filtered_empty: "当前筛选条件下没有匹配候选。你可以放宽筛选范围，或回到全部视图。",
    review_inbox_lead_mixed: "先处理真正需要你判断的对象；生命周期和机器轨迹只作为辅助上下文。",
    review_count_suggestion: "建议复核",
    review_count_review: "待复核",
    review_count_promote: "可晋升",
    review_count_todo: "Owner 待办",
    review_presets_title: "常用分诊视图",
    review_presets_desc: "一键回到常见 Owner 队列；手动微调筛选时会自动进入自定义视图。",
    review_preset_all: "全部",
    review_preset_review: "待复核优先",
    review_preset_promote: "可晋升",
    review_preset_recent: "近 7 天新增",
    review_filters_title: "收件箱筛选",
    review_filters_desc: "按阶段、类型、来源和时效收窄候选范围。",
    review_filter_stage: "阶段",
    review_filter_stage_all: "全部",
    review_filter_stage_review: "待复核",
    review_filter_stage_promote: "可晋升",
    review_filter_stage_reviewed: "近期已处理",
    review_filter_type: "类型",
    review_filter_type_all: "全部类型",
    review_filter_source: "来源",
    review_filter_source_placeholder: "来源引用 / import id / 关键词",
    review_filter_age: "时间",
    review_filter_age_all: "全部时间",
    review_filter_age_24h: "近 24 小时",
    review_filter_age_7d: "近 7 天",
    review_filter_age_30d: "近 30 天",
    btn_reset_filters: "清空筛选",
    review_filter_meta_idle: "当前显示全部候选。",
    review_filter_meta_active: "当前显示 {shown} / {total} 条候选。",
    suggestion_queue_title: "任务建议复核",
    suggestion_queue_desc: "这里处理最近执行产出的建议判断，不和学习候选治理混在一起。",
    suggestion_queue_next: "下一步：判断这条建议是保留、改写还是拒绝。",
    suggestion_queue_empty: "当前没有待复核的任务建议。",
    suggestion_queue_open_detail: "查看细节",
    suggestion_meta_created: "进入队列 {created}",
    suggestion_history_summary: "最近执行判断",
    suggestion_history_desc: "这里回看最近已经完成的 execution judgment，不重新打开操作动作。",
    suggestion_history_empty: "当前没有最近已复核的执行建议。",
    suggestion_history_reviewed: "已判断 {created}",
    audit_timeline_summary: "近期判断时间线",
    audit_timeline_desc: "按时间回看最近完成的 execution judgment 与 learning judgment，主队列仍只保留待处理对象。",
    audit_timeline_empty: "当前没有可回看的近期判断。",
    audit_timeline_kind_suggestion: "执行建议",
    audit_timeline_kind_learning: "学习候选",
    audit_timeline_time_decided: "判断于 {created}",
    audit_timeline_time_reviewed: "复核于 {created}",
    audit_timeline_time_promoted: "晋升于 {created}",
    audit_timeline_time_created: "进入队列 {created}",
    audit_timeline_open_detail: "打开支撑详情",
    audit_timeline_filter_kind: "对象",
    audit_timeline_filter_kind_all: "全部对象",
    audit_timeline_filter_kind_suggestion: "执行建议",
    audit_timeline_filter_kind_learning: "学习候选",
    audit_timeline_filter_status: "判断",
    audit_timeline_filter_status_all: "全部判断",
    audit_timeline_filter_status_accept: "Accept",
    audit_timeline_filter_status_modify: "Modify",
    audit_timeline_filter_status_reject: "Reject",
    audit_timeline_filter_status_promote: "Promote / Runtime",
    audit_timeline_filter_age: "时间",
    audit_timeline_filter_age_all: "全部时间",
    audit_timeline_filter_age_7d: "近 7 天",
    audit_timeline_filter_age_30d: "近 30 天",
    audit_timeline_meta_idle: "当前显示全部近期判断。",
    audit_timeline_meta_active: "当前显示 {shown} / {total} 条近期判断。",
    audit_timeline_empty_filtered: "当前没有符合时间线筛选的判断。",
    suggestion_detail_empty: "选择一条建议或已处理学习项以查看复核支撑。",
    suggestion_detail_raw: "原始快照（按需展开）",
    suggestion_detail_task: "任务",
    suggestion_detail_status: "当前状态",
    suggestion_detail_status_pending: "待复核",
    suggestion_detail_status_accept: "已接受",
    suggestion_detail_status_modify: "已修改",
    suggestion_detail_status_reject: "已拒绝",
    suggestion_detail_created: "进入队列时间",
    suggestion_detail_module: "模块",
    suggestion_detail_run: "运行记录",
    suggestion_detail_output: "输出文件",
    suggestion_detail_focus: "复核焦点",
    suggestion_detail_focus_none: "暂无显式复核焦点。",
    suggestion_detail_owner_note: "Owner 备注",
    suggestion_detail_correction: "修正记录",
    suggestion_detail_replacement: "替代判断",
    suggestion_detail_reason: "不像我的原因",
    suggestion_detail_target: "目标层",
    suggestion_detail_next: "下一步",
    judgment_detail_next: "下一步",
    judgment_detail_subject_empty: "选择一条建议或已处理学习项以查看复核支撑。",
    judgment_detail_subject_suggestion: "执行建议复核",
    judgment_detail_subject_learning: "学习判断回看",
    detail_compact_showing: "显示 {shown} / {total} 条",
    detail_compact_full: "展开完整内容",
    detail_snapshot_summary: "快照摘要",
    detail_snapshot_fields: "字段",
    detail_snapshot_size: "估计体积",
    detail_snapshot_lists: "列表项",
    suggestion_detail_next_pending: "提交 Accept / Modify / Reject，让这条执行建议完成 judgment。",
    suggestion_detail_next_accept: "已接受：如需沉淀，再单独判断是否值得进入学习流程。",
    suggestion_detail_next_modify: "已修改：修正记录已经写入，可继续对照输出与更正后的判断。",
    suggestion_detail_next_reject: "已拒绝：这条执行建议不会作为你的判断被保留。",
    review_queue_title: "学习候选待复核",
    review_queue_desc: "这里处理学习候选的 Accept / Modify / Reject，不把判断淹没在日志里。",
    promote_queue_title: "学习候选可晋升",
    promote_queue_desc: "Accept 不等于 Promote。这里只处理已经通过复核的学习项。",
    owner_todo_title: "Owner 待办",
    owner_todo_desc: "这是系统已经升级成 owner judgment 的异常与待确认事项。",
    review_history_summary: "近期已处理 / 冷却中",
    queue_empty_review: "当前没有待复核候选。",
    queue_empty_promote: "当前没有可晋升候选。",
    queue_empty_reviewed: "当前没有近期已处理或冷却中的候选。",
    queue_empty_todo: "当前没有 Owner 待办。",
    audit_support_kicker: "支持上下文",
    audit_support_title: "复核支撑",
    audit_support_desc: "生命周期、报告和机器轨迹在这里辅助判断，但不占据主舞台。",
    audit_fold_pipeline: "候选与复核汇总",
    audit_fold_machine: "机器轨迹（按需展开）",
    label_task: "任务",
    task_placeholder: "描述你要做的事...",
    label_module: "模块",
    option_auto_route: "自动路由",
    option_provider_auto: "自动（按设置）",
    option_use_fallback: "使用全局默认",
    label_provider: "Provider",
    label_model: "模型",
    model_placeholder: "gpt-4.1-mini / deepseek-chat",
    label_use_retrieval: "启用检索",
    label_top_k: "参考条数",
    btn_inspect: "检查",
    btn_run: "执行",
    task_starters: "快捷任务",
    starter_weekly_review: "每周决策复盘",
    starter_extract_patterns: "提取本周聊天模式",
    starter_write_story: "写一篇饭后 BTC 市场故事",
    btn_run_mvp: "一键跑通 MVP（检查 -> 执行 -> 复核）",
    btn_run_demo: "运行演示模式（决策 + 学习 + 审计）",
    mvp_guide_idle: "新手提示：点击一键按钮后，依次看 Route / Plan / Result / Suggestion Detail。",
    mvp_guide_inspecting: "MVP 进行中：正在检查路由与计划...",
    mvp_guide_running: "MVP 进行中：正在执行任务并生成建议...",
    mvp_guide_done: "MVP 已完成：请到 Suggestion Detail 点击 Accept / Modify / Reject。",
    learning_direct_ingest_title: "直接导入",
    learning_direct_ingest_desc: "粘贴文本，直接写入记忆日志。",
    label_learning_text: "学习文本",
    learning_text_placeholder: "粘贴 transcript、文章或你的总结...",
    label_title_optional: "标题（可选）",
    title_placeholder: "来源标题",
    label_learning_certainty: "把握程度",
    certainty_auto: "自动（系统判断）",
    certainty_low: "低（先记为待验证）",
    certainty_medium: "中（大体可靠）",
    certainty_high: "高（高度确定）",
    learning_quick_defaults: "快捷模式默认：来源类型=notes，把握程度=自动。",
    label_source_type: "来源类型",
    label_confidence: "置信度",
    btn_ingest_memory: "导入到记忆",
    learning_handoff_title: "学习 Handoff",
    learning_handoff_desc: "先生成低成本外部包，再把结构化结果贴回。",
    label_source_url: "来源链接 / 引用",
    source_url_placeholder: "YouTube / 播客 / 其他来源",
    btn_generate_packet: "生成 Handoff 包",
    label_external_response: "外部 LLM JSON 返回",
    external_response_placeholder: "把外部模型 JSON 粘贴到这里...",
    btn_parse_queue: "解析到候选队列",
    audit_actions: "审计动作",
    audit_start_title: "先跑一遍（推荐）",
    audit_start_desc: "先点击一键审计，再按结果做手动动作。",
    btn_audit_quick_run: "一键审计（校验 -> 7天指标 -> Owner报告）",
    audit_guide_idle: "审计指引：先跑一键审计，再看右侧认知信号和待办。",
    audit_zero_state_desc: "当前没有待复核建议、学习候选或 Owner 待办。建议先去工作台输入学习素材，或先跑一次一键审计。",
    btn_go_workspace_learning: "去工作台学习与进化",
    btn_show_manual_actions: "仍然显示全部手动动作",
    audit_guide_title: "一键审计执行摘要",
    audit_guide_running: "进行中：正在依次执行校验、7天指标、Owner报告...",
    audit_guide_done: "完成：先看右侧指标卡，再处理 Owner 待办（如果有）。",
    audit_guide_failed: "一键审计失败：{error}",
    audit_step_validate: "1) 校验：状态={status}",
    audit_step_metrics: "2) 7天指标：输出={output_path}",
    audit_step_owner: "3) Owner报告：输出={output_path}，待办={todo_count}",
    audit_actions_primary: "手动动作（常用）",
    audit_actions_secondary_fold: "诊断 / 维护与复核筛选（按需展开）",
    audit_actions_secondary: "诊断 / 维护（按需）",
    audit_validate: "校验",
    audit_metrics: "7天指标",
    audit_owner_report: "7天 Owner 报告",
    audit_detect_diseq: "检测失衡",
    audit_cognition_timeline: "认知时间线",
    audit_schedule_weekly: "执行周循环",
    audit_build_index: "构建检索索引",
    suggestion_review_filters: "建议复核筛选",
    filter_review_all: "全部",
    filter_accept: "接受",
    filter_modify: "修改",
    filter_reject: "拒绝",
    execution_trace: "执行轨迹",
    trace_messages: "系统消息",
    messages_idle: "暂无系统消息。",
    messages_prefix_system: "系统：",
    messages_prefix_user: "你：",
    btn_expand_messages: "展开历史",
    btn_collapse_messages: "收起历史",
    trace_cognition_signals: "认知信号（7天）",
    trace_owner_todos: "待办",
    trace_learning_lifecycle: "学习生命周期",
    trace_learning_lifecycle_note: "任何内容都不会直接进入运行时上下文。必须先复核，再晋升；晋升后仍需成熟期。",
    trace_learning_candidates: "学习候选与状态队列",
    trace_candidate_pipeline: "候选管道（30天 + 趋势）",
    trace_suggestion_reviews: "建议复核（30天 + 趋势）",
    trace_route: "路由",
    trace_plan: "计划",
    trace_loaded_files: "已加载文件",
    trace_result: "结果",
    trace_judgment_detail: "判断详情",
    trace_suggestion_detail: "建议详情",
    trace_output_preview: "输出预览",
    btn_accept: "接受",
    btn_modify: "修改",
    btn_reject: "拒绝",
    btn_promote: "晋升",
    btn_resolve: "完成",
    lifecycle_step_imported: "已导入",
    lifecycle_step_candidate: "候选中",
    lifecycle_step_reviewed: "已复核",
    lifecycle_step_promoted: "已晋升",
    lifecycle_step_active_runtime: "运行中",
    lifecycle_stage_candidate: "候选中",
    lifecycle_stage_reviewed_accept: "已复核：接受",
    lifecycle_stage_reviewed_modify: "已复核：修改",
    lifecycle_stage_reviewed_reject: "已复核：拒绝",
    lifecycle_stage_promoted: "已晋升（冷却中）",
    lifecycle_stage_active_runtime: "运行中",
    candidate_label_statement: "陈述",
    candidate_label_type: "类型",
    candidate_label_target: "目标层",
    candidate_label_source: "来源",
    candidate_label_rationale: "提取理由",
    candidate_label_evidence: "证据",
    candidate_label_confidence: "置信度",
    candidate_label_status: "当前状态",
    candidate_source_unknown: "未提供来源",
    candidate_evidence_none: "无证据片段",
    candidate_detail_summary: "查看判断依据",
    candidate_detail_evidence: "证据片段",
    candidate_detail_sources: "来源引用",
    candidate_detail_created: "进入队列时间",
    candidate_detail_owner_note: "Owner 备注",
    candidate_detail_modified: "修改后陈述",
    candidate_detail_promotion_target: "晋升目标",
    candidate_detail_runtime: "运行时状态",
    candidate_detail_none: "暂无更细证据。",
    candidate_detail_runtime_pending: "尚未进入运行时上下文。",
    candidate_detail_runtime_cooling: "仍在成熟期，约剩余 {hours} 小时。",
    candidate_detail_runtime_active: "已进入运行时上下文。",
    candidate_next_review: "下一步：执行复核（接受 / 修改 / 拒绝）。",
    candidate_next_promote: "下一步：可晋升进入治理成熟期。",
    candidate_next_rework: "下一步：修改后会生成新的候选条目等待复核。",
    candidate_next_reject: "已拒绝：不会进入判断核心。",
    candidate_next_cooling: "已晋升，成熟期剩余约 {hours} 小时，之后才可进入运行时上下文。",
    candidate_next_runtime: "已进入运行时上下文（成熟完成）。",
    learning_review_modal_title_accept: "接受候选",
    learning_review_modal_title_modify: "修改候选",
    learning_review_modal_title_reject: "拒绝候选",
    learning_review_modal_title_promote: "晋升候选",
    learning_review_modal_title: "复核候选",
    learning_review_owner_note: "复核备注",
    learning_review_note_placeholder: "写下你的判断依据...",
    learning_review_modified_statement: "修改后的陈述",
    learning_review_statement_placeholder: "输入修改后的候选陈述...",
    learning_review_cancel: "取消",
    learning_review_submit: "提交",
    suggestion_review_modal_title_accept: "接受建议",
    suggestion_review_modal_title_modify: "修改建议",
    suggestion_review_modal_title_reject: "拒绝建议",
    suggestion_review_modal_title: "复核建议",
    suggestion_review_owner_note: "Owner 备注",
    suggestion_review_note_placeholder: "写下你的判断依据...",
    suggestion_review_replacement: "替代判断",
    suggestion_review_replacement_placeholder: "输入修改后的判断...",
    suggestion_review_reason: "不像我的原因",
    suggestion_review_reason_placeholder: "说明原建议为什么不像你...",
    suggestion_review_target: "目标层",
    suggestion_review_target_placeholder: "decision",
    suggestion_review_cancel: "取消",
    suggestion_review_submit: "提交",
    settings_title: "连接与偏好设置",
    settings_intro: "只需配置一个 API Key 并保存即可。其余选项建议先保持默认。",
    settings_section_openai: "OpenAI（可选）",
    settings_section_deepseek: "DeepSeek（可选）",
    settings_provider_tip: "配置任意一个直连模型即可直接生成结果。",
    settings_section_routing: "默认执行方式",
    settings_routing_note: "不确定就保持系统自动；只有当你想固定模式时再修改。",
    settings_section_profiles: "高级：按任务类型覆盖（可选）",
    settings_section_ui: "界面",
    settings_openai_key: "OpenAI API Key",
    settings_openai_base_url: "OpenAI Base URL",
    settings_openai_model: "OpenAI 默认模型",
    settings_deepseek_key: "DeepSeek API Key",
    settings_default_provider: "默认执行方式",
    settings_routing_model: "路由模型（轻）",
    settings_deepseek_model: "DeepSeek 默认模型",
    settings_deepseek_base_url: "DeepSeek Base URL",
    settings_profiles_note: "留空即跟随默认执行方式。仅在你想区分任务类型时再设置。",
    settings_decision_provider: "决策类任务执行方式",
    settings_decision_model: "决策类任务模型",
    settings_content_provider: "内容类任务执行方式",
    settings_content_model: "内容类任务模型",
    settings_cognition_provider: "学习类任务执行方式",
    settings_cognition_model: "学习类任务模型",
    option_mode_dry_run: "离线演练（不调用 API）",
    option_mode_handoff: "外部协作（复制请求包）",
    option_mode_openai: "OpenAI（直连）",
    option_mode_deepseek: "DeepSeek（直连）",
    settings_ui_language: "界面语言",
    btn_save: "保存",
    settings_key_configured: "已配置（本地存储）",
    msg_settings_saved: "设置已保存。",
    msg_connection_failed: "连接失败：{error}",
    msg_copy_failed: "复制失败：{error}",
    msg_no_output_yet: "暂无输出，请先执行任务。",
    msg_no_suggestion_selected: "还没有选中建议，请先选择一条建议或先执行任务。",
    demo_summary_idle: "演示摘要会显示在这里。",
    demo_summary_title: "演示模式执行摘要",
    demo_started: "演示模式开始：将自动执行 决策 -> 学习 -> 审计 三步。",
    demo_done: "演示模式完成：你现在可以在审计台查看完整轨迹与报告。",
    demo_failed: "演示模式失败：{error}",
    demo_mode_provider: "执行 provider：{provider}",
    demo_step_decision: "1) 决策：模块={module}，输出={output_path}，suggestion={suggestion_id}",
    demo_step_learning: "2) 学习：新增 event={events}，insight={insights}",
    demo_step_audit: "3) 审计：owner_report={output_path}，fail 指标={fails}",
    demo_none: "无",
    no_cognition_metrics: "暂无认知指标",
    run_metrics_first: "请先运行 7天指标。",
    msg_mvp_started: "MVP 已开始：检查 -> 执行 -> 建议详情。",
    msg_mvp_inspect_ready: "MVP 检查完成：{module} -> {skill}",
    msg_mvp_complete: "MVP 完成。请在 Suggestion Detail 区域做 Accept/Modify/Reject。",
    msg_mvp_failed: "MVP 失败：{error}",
    msg_mvp_mode: "MVP 当前执行模式：{provider}",
    msg_mvp_no_api: "未检测到 DeepSeek/OpenAI key，当前会走非 API 模式。",
    msg_task_required_inspect: "请先填写任务，再检查。",
    msg_task_required_run: "请先填写任务，再执行。",
    msg_action_running: "正在执行动作：{action}",
    msg_action_complete: "动作完成：{action}",
    msg_action_failed: "动作失败：{error}",
    msg_owner_todo_resolved: "已完成 Owner Todo：{id}",
    msg_owner_todo_resolve_failed: "完成 Owner Todo 失败：{error}",
    msg_review_note_required: "复核需要填写备注。",
    msg_modify_statement_required: "选择“修改”时必须填写修改后的陈述。",
    msg_suggestion_note_required: "请输入对这条建议的 Owner 备注。",
    msg_suggestion_replacement_required: "请输入替代判断。",
    msg_suggestion_reason_required: "请输入不像我的原因。",
    msg_suggestion_review_done: "建议已复核：{id} -> {verdict}",
    msg_suggestion_review_failed: "建议复核失败：{error}",
    msg_candidate_review_done: "候选已复核：{id} -> {verdict}",
    msg_candidate_review_failed: "候选复核失败：{error}",
    msg_promotion_note_required: "晋升需要填写审批备注。",
    msg_candidate_promoted_done: "候选已晋升：{id} -> {target}",
    msg_candidate_promote_failed: "候选晋升失败：{error}",
    msg_learning_text_required: "请先粘贴学习文本。",
    msg_learning_source_required: "学习 Handoff 需要先填写来源链接 / 引用。",
    msg_learning_packet_generating: "正在生成学习 Handoff 包...",
    msg_learning_packet_ready: "Handoff 包已生成。复制 Output Preview 发给外部模型。",
    msg_learning_packet_failed: "Handoff 包生成失败：{error}",
    msg_learning_response_required: "请先粘贴外部模型 JSON 返回。",
    msg_learning_importing: "正在导入 Handoff 响应到记忆与候选队列...",
    msg_learning_import_done: "导入完成。候选队列 +{count}。",
    msg_learning_import_failed: "Handoff 导入失败：{error}",
    msg_learning_confidence_auto: "把握程度自动判断：{confidence}/10",
    msg_learning_confidence_manual: "把握程度：{level}（{confidence}/10）",
    msg_no_suggestion_selected: "还没有 suggestion，请先执行任务。",
  },
  en: {
    doc_title: "Personal Core OS | Audit Center",
    app_title: "Personal Core OS",
    app_subtitle: "Audit Center",
    nav_workspace: "Workspace",
    nav_audit: "Audit Center",
    status_connecting: "Connecting...",
    status_connected: "Connected",
    status_offline: "Offline",
    tab_task: "Task",
    tab_learning: "Learning & Evolution",
    tab_audit: "Audit Console",
    hint_task: "Task execution entry (optional). For governance, switch to Audit Console.",
    hint_learning: "Learning & Evolution has moved to Workspace. This page is for audit and candidate governance.",
    hint_audit: "Review drift, reports, and Learning & Evolution candidates before promoting into judgment core.",
    audit_kicker: "Owner Review",
    review_inbox_title: "Items Requiring Judgment",
    review_inbox_desc: "Handle task suggestions, learning candidates, and owner todos first, then open lifecycle, reports, or machine traces only when needed.",
    review_inbox_lead_suggestion: "Task suggestions are waiting for judgment. Decide Accept / Modify / Reject before switching to learning governance or support context.",
    review_inbox_lead_review: "Pending candidates need review now. Decide Accept / Modify / Reject before thinking about promotion.",
    review_inbox_lead_promote: "Some candidates already passed review. Accept is not Promote, so judge promotion separately.",
    review_inbox_lead_todo: "Owner todos are the main work right now. Clear these judgment items first, then use support context if needed.",
    review_inbox_lead_empty: "The inbox is empty for now. Add new learning material from Workspace or run quick audit if you want fresh context.",
    review_inbox_lead_filtered_empty: "No candidates match the current filters. Relax the filters or return to the full inbox view.",
    review_inbox_lead_mixed: "Focus on the objects that need owner judgment first; lifecycle and machine traces stay in a support role.",
    review_count_suggestion: "Suggestion Review",
    review_count_review: "Needs Review",
    review_count_promote: "Ready To Promote",
    review_count_todo: "Owner Todos",
    review_presets_title: "Common Triage Views",
    review_presets_desc: "Jump back to common owner queues in one click. Manual filter tweaks automatically become a custom view.",
    review_preset_all: "All",
    review_preset_review: "Needs Review",
    review_preset_promote: "Ready To Promote",
    review_preset_recent: "Last 7d",
    review_filters_title: "Inbox Filters",
    review_filters_desc: "Narrow candidates by stage, type, source, and recency.",
    review_filter_stage: "Stage",
    review_filter_stage_all: "All",
    review_filter_stage_review: "Needs Review",
    review_filter_stage_promote: "Ready To Promote",
    review_filter_stage_reviewed: "Recently Processed",
    review_filter_type: "Type",
    review_filter_type_all: "All Types",
    review_filter_source: "Source",
    review_filter_source_placeholder: "Source ref / import id / keyword",
    review_filter_age: "Age",
    review_filter_age_all: "Any Time",
    review_filter_age_24h: "Last 24h",
    review_filter_age_7d: "Last 7d",
    review_filter_age_30d: "Last 30d",
    btn_reset_filters: "Reset Filters",
    review_filter_meta_idle: "Showing all candidates.",
    review_filter_meta_active: "Showing {shown} / {total} candidates.",
    suggestion_queue_title: "Task Suggestion Inbox",
    suggestion_queue_desc: "Review execution suggestions here without mixing them into learning candidate governance.",
    suggestion_queue_next: "Next action: decide whether this suggestion should be kept, rewritten, or rejected.",
    suggestion_queue_empty: "No task suggestions currently need review.",
    suggestion_queue_open_detail: "Open Detail",
    suggestion_meta_created: "Queued {created}",
    suggestion_history_summary: "Recent Execution Judgments",
    suggestion_history_desc: "Review the latest completed execution judgments here without reopening decision actions.",
    suggestion_history_empty: "No recently reviewed execution suggestions yet.",
    suggestion_history_reviewed: "Reviewed {created}",
    audit_timeline_summary: "Recent Judgment Timeline",
    audit_timeline_desc: "Review recent execution and learning judgments in time order. The main queues still keep only pending items.",
    audit_timeline_empty: "No recent judgments to review yet.",
    audit_timeline_kind_suggestion: "Execution Suggestion",
    audit_timeline_kind_learning: "Learning Candidate",
    audit_timeline_time_decided: "Decided {created}",
    audit_timeline_time_reviewed: "Reviewed {created}",
    audit_timeline_time_promoted: "Promoted {created}",
    audit_timeline_time_created: "Queued {created}",
    audit_timeline_open_detail: "Open Support Detail",
    audit_timeline_filter_kind: "Object",
    audit_timeline_filter_kind_all: "All Objects",
    audit_timeline_filter_kind_suggestion: "Execution Suggestions",
    audit_timeline_filter_kind_learning: "Learning Candidates",
    audit_timeline_filter_status: "Judgment",
    audit_timeline_filter_status_all: "All Judgments",
    audit_timeline_filter_status_accept: "Accept",
    audit_timeline_filter_status_modify: "Modify",
    audit_timeline_filter_status_reject: "Reject",
    audit_timeline_filter_status_promote: "Promote / Runtime",
    audit_timeline_filter_age: "Time",
    audit_timeline_filter_age_all: "Any Time",
    audit_timeline_filter_age_7d: "Last 7d",
    audit_timeline_filter_age_30d: "Last 30d",
    audit_timeline_meta_idle: "Showing all recent judgments.",
    audit_timeline_meta_active: "Showing {shown} / {total} recent judgments.",
    audit_timeline_empty_filtered: "No recent judgments match the current timeline filters.",
    suggestion_detail_empty: "Select a suggestion or reviewed learning item to open review support.",
    suggestion_detail_raw: "Raw Snapshot (Open On Demand)",
    suggestion_detail_task: "Task",
    suggestion_detail_status: "Current Status",
    suggestion_detail_status_pending: "Needs Review",
    suggestion_detail_status_accept: "Accepted",
    suggestion_detail_status_modify: "Modified",
    suggestion_detail_status_reject: "Rejected",
    suggestion_detail_created: "Queued At",
    suggestion_detail_module: "Module",
    suggestion_detail_run: "Run Ref",
    suggestion_detail_output: "Output File",
    suggestion_detail_focus: "Review Focus",
    suggestion_detail_focus_none: "No explicit review focus points were recorded.",
    suggestion_detail_owner_note: "Owner Note",
    suggestion_detail_correction: "Correction Record",
    suggestion_detail_replacement: "Replacement Judgment",
    suggestion_detail_reason: "Unlike-Me Reason",
    suggestion_detail_target: "Target Layer",
    suggestion_detail_next: "Next Action",
    judgment_detail_next: "Next Action",
    judgment_detail_subject_empty: "Select a suggestion or reviewed learning item to open review support.",
    judgment_detail_subject_suggestion: "Execution Suggestion Review",
    judgment_detail_subject_learning: "Learning Judgment Replay",
    detail_compact_showing: "Showing {shown} / {total}",
    detail_compact_full: "Open Full Content",
    detail_snapshot_summary: "Snapshot Summary",
    detail_snapshot_fields: "Fields",
    detail_snapshot_size: "Approx Size",
    detail_snapshot_lists: "List Entries",
    suggestion_detail_next_pending: "Submit Accept / Modify / Reject so this execution suggestion completes judgment.",
    suggestion_detail_next_accept: "Accepted. If it should become durable learning, judge that separately in the learning flow.",
    suggestion_detail_next_modify: "Modified. The correction record is written; compare the output against the corrected judgment if needed.",
    suggestion_detail_next_reject: "Rejected. This execution suggestion will not be retained as your judgment.",
    review_queue_title: "Learning Candidates Needing Review",
    review_queue_desc: "This queue is for learning candidate Accept / Modify / Reject without burying judgment under logs.",
    promote_queue_title: "Learning Candidates Ready To Promote",
    promote_queue_desc: "Accept is not Promote. This queue is only for learning items that already passed review.",
    owner_todo_title: "Owner Todos",
    owner_todo_desc: "These are exceptions and decisions that have already escalated into owner judgment work.",
    review_history_summary: "Recently Reviewed / Cooling",
    queue_empty_review: "No candidates currently need review.",
    queue_empty_promote: "No candidates are ready to promote right now.",
    queue_empty_reviewed: "No recently reviewed or cooling candidates yet.",
    queue_empty_todo: "No owner todos right now.",
    audit_support_kicker: "Support Context",
    audit_support_title: "Review Support",
    audit_support_desc: "Lifecycle, reports, and machine traces support judgment here, but they should not dominate the page.",
    audit_fold_pipeline: "Candidate And Review Summaries",
    audit_fold_machine: "Machine Trace (Open On Demand)",
    label_task: "Task",
    task_placeholder: "Describe what you want to do...",
    label_module: "Module",
    option_auto_route: "Auto route",
    option_provider_auto: "auto (from settings)",
    option_use_fallback: "Use fallback",
    label_provider: "Provider",
    label_model: "Model",
    model_placeholder: "gpt-4.1-mini / deepseek-chat",
    label_use_retrieval: "Use retrieval",
    label_top_k: "Context Count",
    btn_inspect: "Inspect",
    btn_run: "Run",
    task_starters: "Task Starters",
    starter_weekly_review: "Weekly Decision Review",
    starter_extract_patterns: "Extract Chat Patterns",
    starter_write_story: "Write After-Meal Story",
    btn_run_mvp: "Run MVP Flow (Inspect -> Run -> Review)",
    btn_run_demo: "Run Demo Mode (Decision + Learning + Audit)",
    mvp_guide_idle: "Quick start: click the MVP button, then check Route / Plan / Result / Suggestion Detail in order.",
    mvp_guide_inspecting: "MVP in progress: inspecting route and plan...",
    mvp_guide_running: "MVP in progress: running task and generating suggestion...",
    mvp_guide_done: "MVP complete: use Accept / Modify / Reject in Suggestion Detail.",
    learning_direct_ingest_title: "Direct Ingest",
    learning_direct_ingest_desc: "Paste transcript/article/notes and append memory records directly.",
    label_learning_text: "Learning Text",
    learning_text_placeholder: "Paste transcript, article body, or your summary...",
    label_title_optional: "Title (optional)",
    title_placeholder: "Source title",
    label_learning_certainty: "Certainty",
    certainty_auto: "Auto (system inferred)",
    certainty_low: "Low (needs verification)",
    certainty_medium: "Medium (mostly reliable)",
    certainty_high: "High (high confidence)",
    learning_quick_defaults: "Quick mode defaults: source type = notes, certainty = auto.",
    label_source_type: "Source Type",
    label_confidence: "Confidence",
    btn_ingest_memory: "Ingest To Memory",
    learning_handoff_title: "Learning Handoff",
    learning_handoff_desc: "Generate a low-cost packet for external LLM, then paste structured response back.",
    label_source_url: "Source URL / Reference",
    source_url_placeholder: "YouTube URL, podcast URL, or source ref",
    btn_generate_packet: "Generate Handoff Packet",
    label_external_response: "External LLM JSON Response",
    external_response_placeholder: "Paste external model JSON here...",
    btn_parse_queue: "Parse To Candidate Queue",
    audit_actions: "Audit Actions",
    audit_start_title: "Start Here",
    audit_start_desc: "Run quick audit first, then use manual actions based on results.",
    btn_audit_quick_run: "Run Quick Audit (Validate -> Metrics -> Owner Report)",
    audit_guide_idle: "Audit guide: run quick audit first, then check Cognition Signals and Owner Todos on the right.",
    audit_zero_state_desc: "No task suggestions, learning candidates, or owner todos need attention right now. Start from Workspace learning input or run quick audit first.",
    btn_go_workspace_learning: "Go To Workspace Learning",
    btn_show_manual_actions: "Show Manual Actions Anyway",
    audit_guide_title: "Quick Audit Summary",
    audit_guide_running: "Running: Validate -> Metrics 7D -> Owner Report...",
    audit_guide_done: "Done: check metric cards first, then process Owner Todos if any.",
    audit_guide_failed: "Quick audit failed: {error}",
    audit_step_validate: "1) Validate: status={status}",
    audit_step_metrics: "2) Metrics 7D: output={output_path}",
    audit_step_owner: "3) Owner report: output={output_path}, todos={todo_count}",
    audit_actions_primary: "Manual Actions (Common)",
    audit_actions_secondary_fold: "Diagnostics / Maintenance + Review Filters (Expand When Needed)",
    audit_actions_secondary: "Diagnostics / Maintenance",
    audit_validate: "Validate",
    audit_metrics: "Metrics 7D",
    audit_owner_report: "Owner Report 7D",
    audit_detect_diseq: "Detect Disequilibrium",
    audit_cognition_timeline: "Cognition Timeline",
    audit_schedule_weekly: "Run Weekly Cycle",
    audit_build_index: "Build Retrieval Index",
    suggestion_review_filters: "Suggestion Review Filters",
    filter_review_all: "Review All",
    filter_accept: "Accept",
    filter_modify: "Modify",
    filter_reject: "Reject",
    execution_trace: "Execution Trace",
    trace_messages: "System Messages",
    messages_idle: "No system messages yet.",
    messages_prefix_system: "System: ",
    messages_prefix_user: "You: ",
    btn_expand_messages: "Show History",
    btn_collapse_messages: "Hide History",
    trace_cognition_signals: "Cognition Signals (7D)",
    trace_owner_todos: "Owner Todos",
    trace_learning_lifecycle: "Learning Lifecycle",
    trace_learning_lifecycle_note: "Nothing enters runtime context until reviewed and promoted; promoted items still require maturity time.",
    trace_learning_candidates: "Learning Candidate Lifecycle Queue",
    trace_candidate_pipeline: "Candidate Pipeline (30D + Trend)",
    trace_suggestion_reviews: "Suggestion Reviews (30D + Trend)",
    trace_route: "Route",
    trace_plan: "Plan",
    trace_loaded_files: "Loaded Files",
    trace_result: "Result",
    trace_judgment_detail: "Judgment Detail",
    trace_suggestion_detail: "Suggestion Detail",
    trace_output_preview: "Output Preview",
    btn_accept: "Accept",
    btn_modify: "Modify",
    btn_reject: "Reject",
    btn_promote: "Promote",
    btn_resolve: "Resolve",
    lifecycle_step_imported: "Imported",
    lifecycle_step_candidate: "Candidate",
    lifecycle_step_reviewed: "Reviewed",
    lifecycle_step_promoted: "Promoted",
    lifecycle_step_active_runtime: "Active Runtime",
    lifecycle_stage_candidate: "Candidate",
    lifecycle_stage_reviewed_accept: "Reviewed: Accept",
    lifecycle_stage_reviewed_modify: "Reviewed: Modify",
    lifecycle_stage_reviewed_reject: "Reviewed: Reject",
    lifecycle_stage_promoted: "Promoted (Cooling)",
    lifecycle_stage_active_runtime: "Active Runtime",
    candidate_label_statement: "Statement",
    candidate_label_type: "Type",
    candidate_label_target: "Target Layer",
    candidate_label_source: "Source",
    candidate_label_rationale: "Why Extracted",
    candidate_label_evidence: "Evidence",
    candidate_label_confidence: "Confidence",
    candidate_label_status: "Status",
    candidate_source_unknown: "No source reference",
    candidate_evidence_none: "No evidence snippet",
    candidate_detail_summary: "Review Context",
    candidate_detail_evidence: "Evidence Snippets",
    candidate_detail_sources: "Source References",
    candidate_detail_created: "Queued At",
    candidate_detail_owner_note: "Owner Note",
    candidate_detail_modified: "Modified Statement",
    candidate_detail_promotion_target: "Promotion Target",
    candidate_detail_runtime: "Runtime Status",
    candidate_detail_none: "No deeper evidence available.",
    candidate_detail_runtime_pending: "Not in runtime context yet.",
    candidate_detail_runtime_cooling: "Still cooling, about {hours} hours remaining.",
    candidate_detail_runtime_active: "Already active in runtime context.",
    candidate_next_review: "Next: review this candidate (Accept / Modify / Reject).",
    candidate_next_promote: "Next: promote this accepted candidate.",
    candidate_next_rework: "Next: modified statement creates a new review candidate.",
    candidate_next_reject: "Rejected: does not enter judgment core.",
    candidate_next_cooling: "Promoted and cooling. About {hours}h remaining before runtime context.",
    candidate_next_runtime: "Active in runtime context (maturity complete).",
    learning_review_modal_title_accept: "Accept Candidate",
    learning_review_modal_title_modify: "Modify Candidate",
    learning_review_modal_title_reject: "Reject Candidate",
    learning_review_modal_title_promote: "Promote Candidate",
    learning_review_modal_title: "Review Candidate",
    learning_review_owner_note: "Owner Note",
    learning_review_note_placeholder: "Write your owner rationale...",
    learning_review_modified_statement: "Modified Statement",
    learning_review_statement_placeholder: "Refine the candidate statement...",
    learning_review_cancel: "Cancel",
    learning_review_submit: "Submit",
    suggestion_review_modal_title_accept: "Accept Suggestion",
    suggestion_review_modal_title_modify: "Modify Suggestion",
    suggestion_review_modal_title_reject: "Reject Suggestion",
    suggestion_review_modal_title: "Review Suggestion",
    suggestion_review_owner_note: "Owner Note",
    suggestion_review_note_placeholder: "Write your owner rationale...",
    suggestion_review_replacement: "Replacement Judgment",
    suggestion_review_replacement_placeholder: "Write the corrected judgment...",
    suggestion_review_reason: "Unlike-Me Reason",
    suggestion_review_reason_placeholder: "Explain why the current suggestion is unlike you...",
    suggestion_review_target: "Target Layer",
    suggestion_review_target_placeholder: "decision",
    suggestion_review_cancel: "Cancel",
    suggestion_review_submit: "Submit",
    settings_title: "Connection & Preferences",
    settings_intro: "You only need one API key and Save. Keep everything else as default first.",
    settings_section_openai: "OpenAI (Optional)",
    settings_section_deepseek: "DeepSeek (Optional)",
    settings_provider_tip: "Configuring either direct model is enough to generate outputs directly.",
    settings_section_routing: "Default Execution Mode",
    settings_routing_note: "If unsure, keep system auto. Change this only when you need a fixed mode.",
    settings_section_profiles: "Advanced: Task-Type Overrides (Optional)",
    settings_section_ui: "Interface",
    settings_openai_key: "OpenAI API Key",
    settings_openai_base_url: "OpenAI Base URL",
    settings_openai_model: "OpenAI Default Model",
    settings_deepseek_key: "DeepSeek API Key",
    settings_default_provider: "Default Execution Mode",
    settings_routing_model: "Routing Model (lighter)",
    settings_deepseek_model: "DeepSeek Default Model",
    settings_deepseek_base_url: "DeepSeek Base URL",
    settings_profiles_note: "Leave empty to follow default execution mode. Set only when you need per-task behavior.",
    settings_decision_provider: "Decision Task Mode",
    settings_decision_model: "Decision Task Model",
    settings_content_provider: "Content Task Mode",
    settings_content_model: "Content Task Model",
    settings_cognition_provider: "Learning Task Mode",
    settings_cognition_model: "Learning Task Model",
    option_mode_dry_run: "Offline Dry Run (No API)",
    option_mode_handoff: "External Handoff (Copy Packet)",
    option_mode_openai: "OpenAI (Direct)",
    option_mode_deepseek: "DeepSeek (Direct)",
    settings_ui_language: "UI Language",
    btn_save: "Save",
    settings_key_configured: "Configured (stored locally)",
    msg_settings_saved: "Settings saved.",
    msg_connection_failed: "Connection failed: {error}",
    msg_copy_failed: "Copy failed: {error}",
    msg_no_output_yet: "No output yet. Run a task first.",
    msg_no_suggestion_selected: "No suggestion selected. Pick one from the inbox or run a task first.",
    demo_summary_idle: "Demo summary will appear here.",
    demo_summary_title: "Demo Mode Summary",
    demo_started: "Demo mode started: Decision -> Learning -> Audit will run automatically.",
    demo_done: "Demo mode completed. Check Audit Console for full traces and report.",
    demo_failed: "Demo mode failed: {error}",
    demo_mode_provider: "Execution provider: {provider}",
    demo_step_decision: "1) Decision: module={module}, output={output_path}, suggestion={suggestion_id}",
    demo_step_learning: "2) Learning: appended event={events}, insight={insights}",
    demo_step_audit: "3) Audit: owner_report={output_path}, fail metrics={fails}",
    demo_none: "none",
    msg_mvp_started: "MVP flow started: Inspect -> Run -> Suggestion detail.",
    msg_mvp_inspect_ready: "MVP inspect ready: {module} -> {skill}",
    msg_mvp_complete: "MVP flow complete. Review Suggestion Detail and click Accept/Modify/Reject.",
    msg_mvp_failed: "MVP flow failed: {error}",
    msg_mvp_mode: "MVP execution mode: {provider}",
    msg_mvp_no_api: "No DeepSeek/OpenAI key found, running without direct API provider.",
    msg_task_required_inspect: "Task is required for inspect.",
    msg_task_required_run: "Task is required for run.",
    msg_action_running: "Running action: {action}",
    msg_action_complete: "Action complete: {action}",
    msg_action_failed: "Action failed: {error}",
    msg_owner_todo_resolved: "Owner todo resolved: {id}",
    msg_owner_todo_resolve_failed: "Resolve owner todo failed: {error}",
    msg_review_note_required: "Owner note is required for review.",
    msg_modify_statement_required: "Modified statement is required for modify verdict.",
    msg_suggestion_note_required: "Owner note is required for suggestion review.",
    msg_suggestion_replacement_required: "Replacement judgment is required for modify verdict.",
    msg_suggestion_reason_required: "Unlike-me reason is required for modify verdict.",
    msg_suggestion_review_done: "Suggestion reviewed: {id} -> {verdict}",
    msg_suggestion_review_failed: "Suggestion review failed: {error}",
    msg_candidate_review_done: "Candidate reviewed: {id} -> {verdict}",
    msg_candidate_review_failed: "Candidate review failed: {error}",
    msg_promotion_note_required: "Approval note is required for promotion.",
    msg_candidate_promoted_done: "Candidate promoted: {id} -> {target}",
    msg_candidate_promote_failed: "Candidate promotion failed: {error}",
    msg_learning_text_required: "Learning text is required. Paste transcript/article/notes first.",
    msg_learning_source_required: "Source URL/reference is required for learning handoff packet.",
    msg_learning_packet_generating: "Generating learning handoff packet...",
    msg_learning_packet_ready: "Learning handoff packet ready. Copy Output Preview and send to external model.",
    msg_learning_packet_failed: "Packet generation failed: {error}",
    msg_learning_response_required: "Paste external LLM JSON response first.",
    msg_learning_importing: "Importing handoff response into memory + candidate queue...",
    msg_learning_import_done: "Imported learning handoff. Candidate queue +{count}.",
    msg_learning_import_failed: "Handoff import failed: {error}",
    msg_learning_confidence_auto: "Certainty auto-inferred: {confidence}/10",
    msg_learning_confidence_manual: "Certainty: {level} ({confidence}/10)",
    msg_no_suggestion_selected: "No suggestion selected. Run a task first.",
    no_cognition_metrics: "No cognition metrics",
    run_metrics_first: "Run metrics first.",
  },
};

function t(key, vars = {}) {
  const table = I18N[uiLanguage] || I18N.en;
  const fallback = I18N.en;
  let text = table[key] || fallback[key] || key;
  for (const [name, value] of Object.entries(vars || {})) {
    text = text.replaceAll(`{${name}}`, String(value));
  }
  return text;
}

function applyI18n() {
  const lang = uiLanguage === "en" ? "en" : "zh";
  document.documentElement.lang = lang;
  for (const node of document.querySelectorAll("[data-i18n]")) {
    const key = node.getAttribute("data-i18n");
    if (!key) {
      continue;
    }
    node.textContent = t(key);
  }
  for (const node of document.querySelectorAll("[data-i18n-placeholder]")) {
    const key = node.getAttribute("data-i18n-placeholder");
    if (!key) {
      continue;
    }
    node.setAttribute("placeholder", t(key));
  }
  const titleNode = document.querySelector("title[data-i18n]");
  if (titleNode) {
    document.title = t(titleNode.getAttribute("data-i18n") || "");
  }
}

function setMvpGuideText(key) {
  if (!mvpGuide) {
    return;
  }
  mvpGuide.setAttribute("data-i18n", key);
  mvpGuide.textContent = t(key);
}

function setDemoSummaryKey(key) {
  if (!demoSummary) {
    return;
  }
  demoSummary.setAttribute("data-i18n", key);
  demoSummary.textContent = t(key);
}

function setDemoSummaryLines(lines) {
  if (!demoSummary) {
    return;
  }
  demoSummary.removeAttribute("data-i18n");
  demoSummary.textContent = lines.join("\n");
}

function setAuditGuideKey(key) {
  if (!auditGuide) {
    return;
  }
  auditGuide.setAttribute("data-i18n", key);
  auditGuide.textContent = t(key);
}

function setAuditGuideLines(lines) {
  if (!auditGuide) {
    return;
  }
  auditGuide.removeAttribute("data-i18n");
  auditGuide.textContent = lines.join("\n");
}

function refreshAuditUiSnapshot(data) {
  if (!data || typeof data !== "object") {
    return;
  }
  if (Array.isArray(data.owner_todos)) {
    auditUiSnapshot.owner_todos = data.owner_todos;
  }
  if (Array.isArray(data.learning_candidates)) {
    auditUiSnapshot.learning_candidates = data.learning_candidates;
  }
  if (data.candidate_pipeline_summary && typeof data.candidate_pipeline_summary === "object") {
    auditUiSnapshot.candidate_pipeline_summary = data.candidate_pipeline_summary;
  }
  if (data.suggestion_review_queue && typeof data.suggestion_review_queue === "object") {
    auditUiSnapshot.suggestion_review_queue = data.suggestion_review_queue;
  }
  refreshReviewTypeOptions();
  renderSuggestionReviewQueue(auditUiSnapshot.suggestion_review_queue);
  renderAuditTimeline();
  renderReviewInboxSummary();
  if (auditSupportTarget.kind === "learning" && auditSupportTarget.id) {
    const item = findLearningCandidateItem(auditSupportTarget.id);
    if (item) {
      renderLearningSupportDetail(item);
    } else {
      syncAuditSupportSelection(null, null);
      renderSuggestionDetailEmpty();
      latestOutputPath = null;
      latestOutputProvider = null;
      setPreview("-");
      setOutputTokenMeta("-");
    }
  }
  updateAuditConsoleDensity();
}

function hasRealOwnerTodos(items) {
  if (!Array.isArray(items)) {
    return false;
  }
  return items.some((item) => item && typeof item === "object" && String(item.id || "").trim());
}

function hasRealLearningCandidates(items) {
  if (!Array.isArray(items)) {
    return false;
  }
  return items.some((item) => item && typeof item === "object" && String(item.id || "").trim());
}

function isSuggestionReviewItem(item) {
  return item && typeof item === "object" && String(item.id || "").trim();
}

function suggestionPendingItems(queue) {
  if (!queue || typeof queue !== "object" || !Array.isArray(queue.pending)) {
    return [];
  }
  return queue.pending.filter(isSuggestionReviewItem);
}

function suggestionReviewedItems(queue) {
  if (!queue || typeof queue !== "object" || !Array.isArray(queue.recently_reviewed)) {
    return [];
  }
  return queue.recently_reviewed.filter(isSuggestionReviewItem);
}

function suggestionPendingTotal(queue) {
  if (!queue || typeof queue !== "object") {
    return 0;
  }
  const total = Number(queue.pending_total);
  if (Number.isFinite(total) && total >= 0) {
    return total;
  }
  return suggestionPendingItems(queue).length;
}

function suggestionReviewedTotal(queue) {
  if (!queue || typeof queue !== "object") {
    return 0;
  }
  const total = Number(queue.reviewed_total);
  if (Number.isFinite(total) && total >= 0) {
    return total;
  }
  return suggestionReviewedItems(queue).length;
}

function findSuggestionReviewItem(suggestionId) {
  const sid = String(suggestionId || "").trim();
  if (!sid) {
    return null;
  }
  const queue = auditUiSnapshot.suggestion_review_queue || {};
  const rows = [
    ...(Array.isArray(queue.pending) ? queue.pending : []),
    ...(Array.isArray(queue.recently_reviewed) ? queue.recently_reviewed : []),
  ];
  return rows.find((item) => String(item && item.id ? item.id : "").trim() === sid) || null;
}

function findLearningCandidateItem(candidateId) {
  const cid = String(candidateId || "").trim();
  if (!cid) {
    return null;
  }
  const rows = Array.isArray(auditUiSnapshot.learning_candidates) ? auditUiSnapshot.learning_candidates : [];
  return rows.find((item) => String(item && item.id ? item.id : "").trim() === cid) || null;
}

function hasLifecycleSignals(summary) {
  if (!summary || typeof summary !== "object") {
    return false;
  }
  const lifecycle = summary.lifecycle && typeof summary.lifecycle === "object" ? summary.lifecycle : {};
  const keys = ["imported", "candidate", "reviewed", "promoted", "active_runtime"];
  return keys.some((key) => Number(lifecycle[key] || 0) > 0);
}

function splitLearningCandidates(items) {
  const buckets = {
    review: [],
    promote: [],
    reviewed: [],
  };
  if (!Array.isArray(items)) {
    return buckets;
  }
  for (const item of items) {
    if (!item || typeof item !== "object") {
      continue;
    }
    if (item.can_review) {
      buckets.review.push(item);
      continue;
    }
    if (item.can_promote) {
      buckets.promote.push(item);
      continue;
    }
    buckets.reviewed.push(item);
  }
  return buckets;
}

function candidateStageBucket(item) {
  if (!item || typeof item !== "object") {
    return "reviewed";
  }
  if (item.can_review) {
    return "review";
  }
  if (item.can_promote) {
    return "promote";
  }
  return "reviewed";
}

function candidateAgeHours(item) {
  if (!item || typeof item !== "object") {
    return null;
  }
  const createdAt = String(item.created_at || "").trim();
  if (!createdAt) {
    return null;
  }
  const created = new Date(createdAt);
  const ts = created.getTime();
  if (Number.isNaN(ts)) {
    return null;
  }
  return Math.max(0, (Date.now() - ts) / 3600000);
}

function candidateSourceText(item) {
  if (!item || typeof item !== "object") {
    return "";
  }
  return [
    item.title,
    item.source_material_ref,
    item.source_import_ref,
    ...(Array.isArray(item.source_refs) ? item.source_refs : []),
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function normalizeReviewFilterState(nextState = {}) {
  const stage = String(nextState.stage || "all").trim();
  const age = String(nextState.age || "all").trim();
  return {
    stage: ["all", "review", "promote", "reviewed"].includes(stage) ? stage : "all",
    type: String(nextState.type || "all").trim() || "all",
    source: String(nextState.source || ""),
    age: ["all", "24h", "7d", "30d"].includes(age) ? age : "all",
  };
}

function sameReviewFilterState(left, right) {
  const normalizedLeft = normalizeReviewFilterState(left);
  const normalizedRight = normalizeReviewFilterState(right);
  return (
    normalizedLeft.stage === normalizedRight.stage &&
    normalizedLeft.type === normalizedRight.type &&
    normalizedLeft.age === normalizedRight.age &&
    normalizedLeft.source === normalizedRight.source
  );
}

function getActiveReviewPresetKey() {
  for (const [key, preset] of Object.entries(REVIEW_FILTER_PRESETS)) {
    if (sameReviewFilterState(reviewFilterState, preset)) {
      return key;
    }
  }
  return "";
}

function updateReviewPresetButtons() {
  const activePreset = getActiveReviewPresetKey();
  for (const button of reviewPresetButtons) {
    const isActive = String(button.dataset.reviewPreset || "") === activePreset;
    button.dataset.active = isActive ? "true" : "false";
    button.setAttribute("aria-pressed", isActive ? "true" : "false");
  }
}

function persistReviewPresetSelection() {
  try {
    const activePreset = getActiveReviewPresetKey();
    if (activePreset) {
      localStorage.setItem(REVIEW_PRESET_STORAGE_KEY, activePreset);
    } else {
      localStorage.removeItem(REVIEW_PRESET_STORAGE_KEY);
    }
  } catch (error) {
    console.debug("review preset persistence unavailable", error);
  }
}

function syncReviewFilterControls() {
  if (reviewStageFilter) {
    reviewStageFilter.value = reviewFilterState.stage;
  }
  refreshReviewTypeOptions();
  if (reviewSourceFilter) {
    reviewSourceFilter.value = reviewFilterState.source;
  }
  if (reviewAgeFilter) {
    reviewAgeFilter.value = reviewFilterState.age;
  }
}

function applyReviewPreset(presetKey) {
  const preset = REVIEW_FILTER_PRESETS[presetKey] || REVIEW_FILTER_PRESETS.all;
  reviewFilterState = normalizeReviewFilterState(preset);
  syncReviewFilterControls();
  rerenderReviewInbox();
}

function initReviewPresetSelection() {
  updateReviewPresetButtons();
  try {
    const savedPreset = String(localStorage.getItem(REVIEW_PRESET_STORAGE_KEY) || "").trim();
    if (savedPreset && REVIEW_FILTER_PRESETS[savedPreset]) {
      applyReviewPreset(savedPreset);
      return;
    }
  } catch (error) {
    console.debug("review preset restore unavailable", error);
  }
  persistReviewPresetSelection();
}

function hasActiveReviewFilters() {
  return (
    reviewFilterState.stage !== "all" ||
    reviewFilterState.type !== "all" ||
    reviewFilterState.age !== "all" ||
    Boolean(String(reviewFilterState.source || "").trim())
  );
}

function filterLearningCandidates(items) {
  if (!Array.isArray(items)) {
    return [];
  }
  return items.filter((item) => {
    if (!item || typeof item !== "object") {
      return false;
    }
    if (reviewFilterState.stage !== "all" && candidateStageBucket(item) !== reviewFilterState.stage) {
      return false;
    }
    if (reviewFilterState.type !== "all" && String(item.candidate_type || "").trim() !== reviewFilterState.type) {
      return false;
    }

    const sourceTerm = String(reviewFilterState.source || "").trim().toLowerCase();
    if (sourceTerm && !candidateSourceText(item).includes(sourceTerm)) {
      return false;
    }

    const ageHours = candidateAgeHours(item);
    if (reviewFilterState.age === "24h" && (ageHours === null || ageHours > 24)) {
      return false;
    }
    if (reviewFilterState.age === "7d" && (ageHours === null || ageHours > 24 * 7)) {
      return false;
    }
    if (reviewFilterState.age === "30d" && (ageHours === null || ageHours > 24 * 30)) {
      return false;
    }
    return true;
  });
}

function refreshReviewTypeOptions() {
  if (!reviewTypeFilter) {
    updateReviewPresetButtons();
    return;
  }
  const current = String(reviewFilterState.type || "all");
  const types = Array.from(
    new Set(
      (Array.isArray(auditUiSnapshot.learning_candidates) ? auditUiSnapshot.learning_candidates : [])
        .map((item) => String(item && item.candidate_type ? item.candidate_type : "").trim())
        .filter(Boolean)
    )
  ).sort((left, right) => left.localeCompare(right));

  reviewTypeFilter.innerHTML = "";
  const allOption = document.createElement("option");
  allOption.value = "all";
  allOption.setAttribute("data-i18n", "review_filter_type_all");
  allOption.textContent = t("review_filter_type_all");
  reviewTypeFilter.appendChild(allOption);

  for (const type of types) {
    const option = document.createElement("option");
    option.value = type;
    option.textContent = type;
    reviewTypeFilter.appendChild(option);
  }

  reviewFilterState.type = types.includes(current) ? current : "all";
  reviewTypeFilter.value = reviewFilterState.type;
  updateReviewPresetButtons();
}

function updateReviewFilterMeta(filteredItems, totalItems) {
  if (!reviewFilterMeta) {
    return;
  }
  if (!hasActiveReviewFilters()) {
    reviewFilterMeta.setAttribute("data-i18n", "review_filter_meta_idle");
    reviewFilterMeta.textContent = t("review_filter_meta_idle");
    return;
  }
  reviewFilterMeta.removeAttribute("data-i18n");
  reviewFilterMeta.textContent = t("review_filter_meta_active", {
    shown: Number(filteredItems || 0),
    total: Number(totalItems || 0),
  });
}

function normalizeAuditTimelineFilterState(nextState = {}) {
  const kind = String(nextState.kind || "all").trim();
  const status = String(nextState.status || "all").trim();
  const age = String(nextState.age || "all").trim();
  return {
    kind: ["all", "suggestion", "learning"].includes(kind) ? kind : "all",
    status: ["all", "accept", "modify", "reject", "promote"].includes(status) ? status : "all",
    age: ["all", "7d", "30d"].includes(age) ? age : "all",
  };
}

function syncAuditTimelineFilterControls() {
  if (auditTimelineKindFilter) {
    auditTimelineKindFilter.value = auditTimelineFilterState.kind;
  }
  if (auditTimelineStatusFilter) {
    auditTimelineStatusFilter.value = auditTimelineFilterState.status;
  }
  if (auditTimelineAgeFilter) {
    auditTimelineAgeFilter.value = auditTimelineFilterState.age;
  }
}

function hasActiveAuditTimelineFilters() {
  return (
    auditTimelineFilterState.kind !== "all" ||
    auditTimelineFilterState.status !== "all" ||
    auditTimelineFilterState.age !== "all"
  );
}

function updateAuditTimelineMeta(filteredItems, totalItems) {
  if (!auditTimelineMeta) {
    return;
  }
  if (!hasActiveAuditTimelineFilters()) {
    auditTimelineMeta.setAttribute("data-i18n", "audit_timeline_meta_idle");
    auditTimelineMeta.textContent = t("audit_timeline_meta_idle");
    return;
  }
  auditTimelineMeta.removeAttribute("data-i18n");
  auditTimelineMeta.textContent = t("audit_timeline_meta_active", {
    shown: Number(filteredItems || 0),
    total: Number(totalItems || 0),
  });
}

function formatCandidateCreatedAt(item) {
  if (!item || typeof item !== "object") {
    return "-";
  }
  const raw = String(item.created_at || "").trim();
  if (!raw) {
    return "-";
  }
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) {
    return raw;
  }
  return date.toLocaleString(uiLanguage === "zh" ? "zh-CN" : "en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function summarizeSuggestionTask(item) {
  const raw = String((item && item.task_raw) || (item && item.id) || "").trim();
  if (!raw) {
    return "-";
  }
  return raw.length > 160 ? `${raw.slice(0, 157)}...` : raw;
}

function clipText(value, maxLength = 240) {
  const raw = String(value || "").trim();
  if (!raw) {
    return "";
  }
  return raw.length > maxLength ? `${raw.slice(0, maxLength - 3)}...` : raw;
}

function normalizeTextItems(items) {
  if (!Array.isArray(items)) {
    return [];
  }
  return items.map((item) => String(item || "").trim()).filter(Boolean);
}

function suggestionReviewBadgeKey(item) {
  const verdict = String((((item || {}).owner_review || {}).verdict) || "").trim().toLowerCase();
  if (verdict === "accept") {
    return "accept";
  }
  if (verdict === "modify") {
    return "modify";
  }
  if (verdict === "reject") {
    return "reject";
  }
  return "pending";
}

function timelineDateValue(raw) {
  const text = String(raw || "").trim();
  if (!text) {
    return 0;
  }
  const ts = Date.parse(text);
  return Number.isNaN(ts) ? 0 : ts;
}

function learningTimelineTimestamp(item) {
  return String((item && (item.promoted_at || item.reviewed_at || item.created_at)) || "").trim();
}

function learningTimelineTimeKey(item) {
  const stage = String((item && item.lifecycle_stage) || "").trim();
  if ((stage === "promoted" || stage === "active_runtime") && String((item && item.promoted_at) || "").trim()) {
    return "audit_timeline_time_promoted";
  }
  if (stage === "reviewed" && String((item && item.reviewed_at) || "").trim()) {
    return "audit_timeline_time_reviewed";
  }
  return "audit_timeline_time_created";
}

function learningTimelineStageClass(item) {
  const stage = String((item && item.lifecycle_stage) || "reviewed").trim();
  if (stage === "active_runtime") {
    return "stage-active_runtime";
  }
  if (stage === "promoted") {
    return "stage-promoted";
  }
  if (stage === "reviewed") {
    return "stage-reviewed";
  }
  return "stage-candidate";
}

function learningTimelineJudgmentKey(item) {
  const stage = String((item && item.lifecycle_stage) || "").trim();
  if (stage === "promoted" || stage === "active_runtime") {
    return "promote";
  }
  const verdict = String((item && item.verdict) || "").trim().toLowerCase();
  if (["accept", "modify", "reject"].includes(verdict)) {
    return verdict;
  }
  return "all";
}

function timelineAgeHours(timestamp) {
  const ts = timelineDateValue(timestamp);
  if (!ts) {
    return null;
  }
  return Math.max(0, (Date.now() - ts) / 3600000);
}

function buildAuditTimelineItems() {
  const items = [];
  for (const item of suggestionReviewedItems(auditUiSnapshot.suggestion_review_queue)) {
    const suggestionId = String(item && item.id ? item.id : "").trim();
    if (!suggestionId) {
      continue;
    }
    const ownerReview = item && item.owner_review && typeof item.owner_review === "object" ? item.owner_review : {};
    const timestamp = String(ownerReview.reviewed_at || item.created_at || "").trim();
    const detailLines = [
      String(ownerReview.owner_note || "").trim(),
      String(ownerReview.replacement_judgment || "").trim(),
      String(ownerReview.unlike_me_reason || "").trim(),
    ].filter(Boolean);
    items.push({
      kind: "suggestion",
      id: suggestionId,
      title: summarizeSuggestionTask(item),
      badgeText: t(`suggestion_detail_status_${suggestionReviewBadgeKey(item)}`),
      badgeClassName: `suggestion-detail-chip status-${suggestionReviewBadgeKey(item)}`,
      metaChips: [
        t("audit_timeline_kind_suggestion"),
        item.module ? String(item.module) : "",
        t("audit_timeline_time_decided", {
          created: formatCandidateCreatedAt({ created_at: timestamp || item.created_at || "" }),
        }),
        ownerReview.target_layer ? `${t("suggestion_detail_target")}: ${String(ownerReview.target_layer)}` : "",
      ].filter(Boolean),
      statusKey: suggestionReviewBadgeKey(item),
      summaryText: detailLines[0] || "",
      noteText: detailLines.length > 1 ? detailLines.slice(1).join("\n") : "",
      timestamp,
      active:
        auditSupportTarget.kind === "suggestion" &&
        suggestionId === String(auditSupportTarget.id || "").trim(),
      openLabel: t("audit_timeline_open_detail"),
      openAction() {
        void focusSuggestionReview(suggestionId);
      },
    });
  }

  for (const item of splitLearningCandidates(auditUiSnapshot.learning_candidates).reviewed) {
    const candidateId = String(item && item.id ? item.id : "").trim();
    if (!candidateId) {
      continue;
    }
    const timestamp = learningTimelineTimestamp(item);
    items.push({
      kind: "learning",
      id: candidateId,
      title: String(item.title || item.candidate_type || item.id || "-").trim(),
      badgeText: lifecycleStageLabel(item),
      badgeClassName: `lifecycle-badge ${learningTimelineStageClass(item)}`,
      metaChips: [
        t("audit_timeline_kind_learning"),
        item.candidate_type ? String(item.candidate_type) : "",
        t(learningTimelineTimeKey(item), {
          created: formatCandidateCreatedAt({ created_at: timestamp || item.created_at || "" }),
        }),
        item.promotion_target || item.proposal_target
          ? `${t("candidate_label_target")}: ${String(item.promotion_target || item.proposal_target)}`
          : "",
      ].filter(Boolean),
      statusKey: learningTimelineJudgmentKey(item),
      summaryText: clipText(item.statement, 260),
      noteText: clipText(item.owner_note || item.modified_statement || lifecycleNextAction(item), 240),
      timestamp,
      active:
        auditSupportTarget.kind === "learning" &&
        candidateId === String(auditSupportTarget.id || "").trim(),
      sourceItem: item,
      openLabel: t("audit_timeline_open_detail"),
      openAction() {
        void focusLearningTimelineReview(candidateId);
      },
    });
  }

  items.sort((left, right) => {
    const rightValue = timelineDateValue(right.timestamp);
    const leftValue = timelineDateValue(left.timestamp);
    if (rightValue !== leftValue) {
      return rightValue - leftValue;
    }
    return String(right.timestamp || "").localeCompare(String(left.timestamp || ""));
  });
  return items;
}

function filterAuditTimelineItems(items) {
  if (!Array.isArray(items)) {
    return [];
  }
  return items.filter((item) => {
    if (!item || typeof item !== "object") {
      return false;
    }
    if (auditTimelineFilterState.kind !== "all" && item.kind !== auditTimelineFilterState.kind) {
      return false;
    }
    if (auditTimelineFilterState.status !== "all" && item.statusKey !== auditTimelineFilterState.status) {
      return false;
    }
    const ageHours = timelineAgeHours(item.timestamp);
    if (auditTimelineFilterState.age === "7d" && (ageHours === null || ageHours > 24 * 7)) {
      return false;
    }
    if (auditTimelineFilterState.age === "30d" && (ageHours === null || ageHours > 24 * 30)) {
      return false;
    }
    return true;
  });
}

function renderAuditTimeline() {
  if (!auditTimelineList) {
    return;
  }
  const allItems = buildAuditTimelineItems();
  const items = filterAuditTimelineItems(allItems);
  if (auditTimelineCount) {
    auditTimelineCount.textContent = String(items.length);
  }
  updateAuditTimelineMeta(items.length, allItems.length);

  auditTimelineList.innerHTML = "";
  if (items.length === 0) {
    const empty = document.createElement("div");
    empty.className = "todo-item todo-item-empty";
    empty.textContent = t(hasActiveAuditTimelineFilters() ? "audit_timeline_empty_filtered" : "audit_timeline_empty");
    auditTimelineList.appendChild(empty);
    return;
  }

  for (const item of items) {
    const wrap = document.createElement("div");
    wrap.className = "todo-item suggestion-review-card reviewed-card";
    wrap.dataset.active = item.active ? "true" : "false";

    const head = document.createElement("div");
    head.className = "todo-head";
    const metric = document.createElement("span");
    metric.className = "todo-metric";
    metric.textContent = item.title || "-";
    const badge = document.createElement("span");
    badge.className = item.badgeClassName;
    badge.textContent = item.badgeText;
    head.appendChild(metric);
    head.appendChild(badge);
    wrap.appendChild(head);

    const meta = document.createElement("div");
    meta.className = "suggestion-meta";
    for (const chipText of item.metaChips) {
      const chip = document.createElement("span");
      chip.className = "suggestion-meta-chip";
      chip.textContent = chipText;
      meta.appendChild(chip);
    }
    wrap.appendChild(meta);

    if (item.summaryText) {
      const summary = document.createElement("div");
      summary.className = "suggestion-review-note timeline-summary";
      summary.textContent = item.summaryText;
      wrap.appendChild(summary);
    }

    if (item.noteText) {
      const note = document.createElement("div");
      note.className = "suggestion-review-note";
      note.textContent = item.noteText;
      wrap.appendChild(note);
    }

    if (item.kind === "learning" && item.sourceItem) {
      wrap.appendChild(buildCandidateContext(item.sourceItem));
    }

    if (typeof item.openAction === "function") {
      const actions = document.createElement("div");
      actions.className = "todo-actions";
      const detailBtn = document.createElement("button");
      detailBtn.className = "todo-resolve-btn";
      detailBtn.type = "button";
      detailBtn.textContent = item.openLabel;
      detailBtn.addEventListener("click", item.openAction);
      actions.appendChild(detailBtn);
      wrap.appendChild(actions);
    }

    auditTimelineList.appendChild(wrap);
  }
}

function renderSuggestionReviewQueue(queue) {
  if (!suggestionReviewList) {
    return;
  }
  const items = suggestionPendingItems(queue);
  const total = suggestionPendingTotal(queue);
  const selectedId =
    auditSupportTarget.kind === "suggestion" ? String(auditSupportTarget.id || "").trim() : "";

  if (suggestionReviewCount) {
    suggestionReviewCount.textContent = String(total);
  }

  suggestionReviewList.innerHTML = "";
  if (items.length === 0) {
    const empty = document.createElement("div");
    empty.className = "todo-item todo-item-empty";
    empty.textContent = t("suggestion_queue_empty");
    suggestionReviewList.appendChild(empty);
    return;
  }

  for (const item of items) {
    const suggestionId = String(item.id || "").trim();
    const wrap = document.createElement("div");
    wrap.className = "todo-item suggestion-review-card";
    wrap.dataset.active = suggestionId && suggestionId === selectedId ? "true" : "false";

    const head = document.createElement("div");
    head.className = "todo-head";
    const metric = document.createElement("span");
    metric.className = "todo-metric";
    metric.textContent = summarizeSuggestionTask(item);
    head.appendChild(metric);

    const meta = document.createElement("div");
    meta.className = "suggestion-meta";
    if (item.module) {
      const moduleChip = document.createElement("span");
      moduleChip.className = "suggestion-meta-chip";
      moduleChip.textContent = String(item.module);
      meta.appendChild(moduleChip);
    }
    const createdChip = document.createElement("span");
    createdChip.className = "suggestion-meta-chip";
    createdChip.textContent = t("suggestion_meta_created", { created: formatCandidateCreatedAt(item) });
    meta.appendChild(createdChip);

    const nextAction = document.createElement("div");
    nextAction.className = "todo-action suggestion-next";
    nextAction.textContent = t("suggestion_queue_next");

    const actions = document.createElement("div");
    actions.className = "todo-actions";

    const detailBtn = document.createElement("button");
    detailBtn.className = "todo-resolve-btn";
    detailBtn.type = "button";
    detailBtn.textContent = t("suggestion_queue_open_detail");
    detailBtn.addEventListener("click", () => {
      void focusSuggestionReview(suggestionId);
    });
    actions.appendChild(detailBtn);

    for (const verdict of ["accept", "modify", "reject"]) {
      const button = document.createElement("button");
      button.className = "todo-resolve-btn";
      button.type = "button";
      button.textContent = t(`btn_${verdict}`);
      button.addEventListener("click", () => {
        reviewSuggestion(verdict, suggestionId);
      });
      actions.appendChild(button);
    }

    wrap.appendChild(head);
    wrap.appendChild(meta);
    wrap.appendChild(nextAction);
    wrap.appendChild(actions);
    suggestionReviewList.appendChild(wrap);
  }
}

function candidateRuntimeDetail(item) {
  if (!item || typeof item !== "object") {
    return t("candidate_detail_runtime_pending");
  }
  if (item.lifecycle_stage === "active_runtime" || item.runtime_active) {
    return t("candidate_detail_runtime_active");
  }
  if (item.lifecycle_stage === "promoted") {
    return t("candidate_detail_runtime_cooling", {
      hours: Number(item.runtime_hours_remaining || 0),
    });
  }
  return t("candidate_detail_runtime_pending");
}

function renderReviewInboxSummary() {
  const filtered = filterLearningCandidates(auditUiSnapshot.learning_candidates);
  const buckets = splitLearningCandidates(filtered);
  const suggestionTotal = suggestionPendingTotal(auditUiSnapshot.suggestion_review_queue);
  const todoTotal = Array.isArray(auditUiSnapshot.owner_todos)
    ? auditUiSnapshot.owner_todos.filter((item) => item && typeof item === "object" && String(item.id || "").trim()).length
    : 0;

  if (reviewCountSuggestion) {
    reviewCountSuggestion.textContent = String(suggestionTotal);
  }
  if (reviewCountReview) {
    reviewCountReview.textContent = String(buckets.review.length);
  }
  if (reviewCountPromote) {
    reviewCountPromote.textContent = String(buckets.promote.length);
  }
  if (reviewCountTodo) {
    reviewCountTodo.textContent = String(todoTotal);
  }
  if (reviewQueueCount) {
    reviewQueueCount.textContent = String(buckets.review.length);
  }
  if (promoteQueueCount) {
    promoteQueueCount.textContent = String(buckets.promote.length);
  }
  if (ownerTodoCount) {
    ownerTodoCount.textContent = String(todoTotal);
  }

  if (!reviewInboxLead) {
    return;
  }

  let leadKey = "review_inbox_lead_mixed";
  if (suggestionTotal > 0) {
    leadKey = "review_inbox_lead_suggestion";
  } else if (hasActiveReviewFilters() && filtered.length === 0) {
    leadKey = "review_inbox_lead_filtered_empty";
  } else if (buckets.review.length > 0) {
    leadKey = "review_inbox_lead_review";
  } else if (buckets.promote.length > 0) {
    leadKey = "review_inbox_lead_promote";
  } else if (todoTotal > 0) {
    leadKey = "review_inbox_lead_todo";
  } else if (!hasLifecycleSignals(auditUiSnapshot.candidate_pipeline_summary)) {
    leadKey = "review_inbox_lead_empty";
  }

  reviewInboxLead.setAttribute("data-i18n", leadKey);
  reviewInboxLead.textContent = t(leadKey);
}

function updateAuditConsoleDensity() {
  if (!auditZeroState) {
    return;
  }
  const buckets = splitLearningCandidates(auditUiSnapshot.learning_candidates);
  const empty =
    !hasRealOwnerTodos(auditUiSnapshot.owner_todos) &&
    suggestionPendingTotal(auditUiSnapshot.suggestion_review_queue) === 0 &&
    buckets.review.length === 0 &&
    buckets.promote.length === 0;
  const showZero = empty && !auditManualForcedVisible;
  auditZeroState.hidden = !showZero;
  if (auditManualActions) {
    auditManualActions.hidden = showZero;
  }
  if (auditAdvancedActions && showZero) {
    auditAdvancedActions.open = false;
  }
}

function clampInt(value, minimum, maximum) {
  return Math.max(minimum, Math.min(maximum, Math.round(value)));
}

function inferLearningConfidence(text, sourceRef = "") {
  const body = String(text || "");
  const content = body.toLowerCase();
  let score = 6;

  if (sourceRef && /^https?:\/\//i.test(sourceRef)) {
    score += 1;
  }
  if (body.length >= 1200) {
    score += 2;
  } else if (body.length >= 500) {
    score += 1;
  } else if (body.length <= 120) {
    score -= 1;
  }

  const numberMatches = body.match(/\d+/g) || [];
  if (numberMatches.length >= 3) {
    score += 1;
  }

  const highCues = ["evidence", "metric", "experiment", "validated", "复盘", "数据", "验证", "实验", "证据", "步骤"];
  const lowCues = ["maybe", "guess", "probably", "uncertain", "可能", "也许", "大概", "猜", "不确定", "感觉"];
  const highHits = highCues.reduce((count, cue) => (content.includes(cue) ? count + 1 : count), 0);
  const lowHits = lowCues.reduce((count, cue) => (content.includes(cue) ? count + 1 : count), 0);
  if (highHits >= 2) {
    score += 1;
  }
  if (lowHits >= 2) {
    score -= 2;
  }

  return clampInt(score, 3, 9);
}

function resolveLearningConfidence(text, sourceRef = "") {
  const mode = (learningCertainty && learningCertainty.value) || "auto";
  if (mode === "low") {
    return { mode, confidence: 4 };
  }
  if (mode === "medium") {
    return { mode, confidence: 7 };
  }
  if (mode === "high") {
    return { mode, confidence: 9 };
  }
  return { mode: "auto", confidence: inferLearningConfidence(text, sourceRef) };
}

function setMessagePanelExpanded(expanded) {
  if (!chatLogWrap || !toggleMessagesBtn) {
    return;
  }
  messagesExpanded = Boolean(expanded);
  chatLogWrap.classList.toggle("expanded", messagesExpanded);
  const key = messagesExpanded ? "btn_collapse_messages" : "btn_expand_messages";
  toggleMessagesBtn.setAttribute("data-i18n", key);
  toggleMessagesBtn.textContent = t(key);
  toggleMessagesBtn.setAttribute("aria-expanded", messagesExpanded ? "true" : "false");
}

function renderLatestMessage() {
  if (!latestMessage) {
    return;
  }
  const raw = String(latestMessagePayload.text || "").trim();
  if (!raw) {
    latestMessage.setAttribute("data-i18n", "messages_idle");
    latestMessage.textContent = t("messages_idle");
    return;
  }
  const compact = raw.replace(/\s+/g, " ");
  const clipped = compact.length > 180 ? `${compact.slice(0, 177)}...` : compact;
  const prefix = latestMessagePayload.role === "user" ? t("messages_prefix_user") : t("messages_prefix_system");
  latestMessage.removeAttribute("data-i18n");
  latestMessage.textContent = `${prefix}${clipped}`;
}

function setLanguage(lang) {
  uiLanguage = lang === "en" ? "en" : "zh";
  applyI18n();
  syncAuditTimelineFilterControls();
  const autoOption = moduleSelect.querySelector('option[value=""]');
  if (autoOption) {
    autoOption.textContent = t("option_auto_route");
  }
  refreshReviewTypeOptions();
  renderSuggestionReviewQueue(auditUiSnapshot.suggestion_review_queue);
  renderAuditTimeline();
  renderReviewInboxSummary();
  renderLearningCandidates(auditUiSnapshot.learning_candidates);
  renderOwnerTodos(auditUiSnapshot.owner_todos);
  if (auditSupportTarget.kind === "suggestion" && auditSupportTarget.id) {
    void loadSuggestionDetail(auditSupportTarget.id);
  } else if (auditSupportTarget.kind === "learning" && auditSupportTarget.id) {
    const item = findLearningCandidateItem(auditSupportTarget.id);
    if (item) {
      renderLearningSupportDetail(item);
    } else {
      syncAuditSupportSelection(null, null);
      renderSuggestionDetailEmpty();
      latestOutputPath = null;
      latestOutputProvider = null;
      setPreview("-");
      setOutputTokenMeta("-");
    }
  } else {
    renderSuggestionDetailEmpty();
  }
  renderLatestMessage();
  setMessagePanelExpanded(messagesExpanded);
}

function addBubble(role, text) {
  const div = document.createElement("div");
  div.className = `bubble ${role}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
  latestMessagePayload = {
    role: role === "user" ? "user" : "system",
    text: String(text || ""),
  };
  renderLatestMessage();
}

function getLastUserBubbleText() {
  const userBubbles = chatLog.querySelectorAll(".bubble.user");
  if (userBubbles.length === 0) {
    return null;
  }
  return userBubbles[userBubbles.length - 1].textContent;
}

function addUserTaskOnce(task) {
  const lastUserText = getLastUserBubbleText();
  if (lastUserText === task) {
    return;
  }
  addBubble("user", task);
}

function setStatus(label, kind, key = null) {
  statusBadge.textContent = label;
  if (key) {
    statusBadge.setAttribute("data-i18n", key);
  } else {
    statusBadge.removeAttribute("data-i18n");
  }
  statusBadge.classList.remove("pending", "ok", "fail");
  statusBadge.classList.add(kind);
}

function setPreview(text) {
  const value = String(text || "").trim();
  outputPreview.textContent = value || "-";
}

function setOutputTokenMeta(text) {
  outputTokenMeta.textContent = String(text || "-");
}

function renderLoadedFiles(files) {
  loadedFiles.innerHTML = "";
  if (!Array.isArray(files) || files.length === 0) {
    const li = document.createElement("li");
    li.textContent = "-";
    loadedFiles.appendChild(li);
    return;
  }

  for (const file of files) {
    const li = document.createElement("li");
    li.textContent = file;
    loadedFiles.appendChild(li);
  }
}

function localizeCognitionMetricLabel(item) {
  const keyRaw = String(item && item.key ? item.key : "").trim().toLowerCase();
  const labelRaw = String(item && item.label ? item.label : "").trim().toLowerCase();
  const byKey = {
    unresolved_disequilibrium: { zh: "未解决失衡率", en: "Unresolved Disequilibrium" },
    equilibration_quality: { zh: "平衡质量", en: "Equilibration Quality" },
    schema_explicitness: { zh: "结构显性度", en: "Schema Explicitness" },
  };
  const alias = {
    "unresolved disequilibrium": "unresolved_disequilibrium",
    "equilibration quality": "equilibration_quality",
    "schema explicitness": "schema_explicitness",
  };
  const canonical = byKey[keyRaw] ? keyRaw : alias[labelRaw] || "";
  if (canonical && byKey[canonical]) {
    return uiLanguage === "zh" ? byKey[canonical].zh : byKey[canonical].en;
  }
  if (item && item.label) {
    return String(item.label);
  }
  if (item && item.key) {
    return String(item.key);
  }
  return uiLanguage === "zh" ? "指标" : "Metric";
}

function localizeTrendLabel(trend) {
  const value = String(trend || "stable").trim().toLowerCase();
  if (uiLanguage !== "zh") {
    return value || "stable";
  }
  const map = {
    stable: "稳定",
    improving: "改善",
    worsening: "恶化",
  };
  return map[value] || value || "稳定";
}

function renderCognitionCards(cards) {
  cognitionCards.innerHTML = "";
  if (!Array.isArray(cards) || cards.length === 0) {
    const empty = document.createElement("div");
    empty.className = "metric-card status-warn";
    empty.innerHTML = `<div class="metric-title">${t("no_cognition_metrics")}</div><div class="metric-value">-</div><div class="metric-meta">${t("run_metrics_first")}</div>`;
    cognitionCards.appendChild(empty);
    return;
  }

  for (const item of cards) {
    const status = item.status || "warn";
    const card = document.createElement("div");
    card.className = `metric-card status-${status}`;

    const trend = item.trend || "stable";
    const delta = typeof item.delta_pp === "number" ? `${item.delta_pp >= 0 ? "+" : ""}${item.delta_pp.toFixed(1)}pp` : "-";

    const title = document.createElement("div");
    title.className = "metric-title";
    title.textContent = localizeCognitionMetricLabel(item);

    const value = document.createElement("div");
    value.className = "metric-value";
    value.textContent = item.value || "-";

    const meta = document.createElement("div");
    meta.className = "metric-meta";
    const op = item.target_operator || ">=";
    const threshold = item.threshold || "-";
    if (uiLanguage === "zh") {
      meta.textContent = `目标 ${op} ${threshold} | 趋势：${localizeTrendLabel(trend)}（${delta}）`;
    } else {
      meta.textContent = `target ${op} ${threshold} | trend: ${localizeTrendLabel(trend)} (${delta})`;
    }

    card.appendChild(title);
    card.appendChild(value);
    card.appendChild(meta);
    cognitionCards.appendChild(card);
  }
}

function renderQueueEmpty(container, message) {
  if (!container) {
    return;
  }
  container.innerHTML = "";
  const empty = document.createElement("div");
  empty.className = "todo-item todo-item-empty";
  empty.innerHTML = `<div class="todo-head"><span class="todo-metric">${message}</span></div><div class="todo-action">-</div>`;
  container.appendChild(empty);
}

function renderOwnerTodos(items) {
  if (!ownerTodos) {
    return;
  }
  ownerTodos.innerHTML = "";
  const priorityRank = {
    red: 0,
    amber: 1,
    yellow: 1,
    green: 2,
  };
  const rows = Array.isArray(items)
    ? items
        .filter((item) => item && typeof item === "object" && String(item.id || "").trim())
        .sort((a, b) => {
          const left = priorityRank[String(a.priority || "").toLowerCase()] ?? 3;
          const right = priorityRank[String(b.priority || "").toLowerCase()] ?? 3;
          return left - right;
        })
    : [];
  if (rows.length === 0) {
    renderQueueEmpty(ownerTodos, t("queue_empty_todo"));
    return;
  }

  for (const item of rows) {
    const wrap = document.createElement("div");
    const priority = (item.priority || "red").toLowerCase();
    wrap.className = `todo-item priority-${priority}`;

    const head = document.createElement("div");
    head.className = "todo-head";
    const metric = document.createElement("span");
    metric.className = "todo-metric";
    metric.textContent = item.metric || "unknown_metric";
    const reason = document.createElement("span");
    reason.className = "todo-reason";
    reason.textContent = item.reason || "";
    head.appendChild(metric);
    head.appendChild(reason);

    const action = document.createElement("div");
    action.className = "todo-action";
    action.textContent = item.action || "-";

    const actions = document.createElement("div");
    actions.className = "todo-actions";
    const btn = document.createElement("button");
    btn.className = "todo-resolve-btn";
    btn.type = "button";
    btn.textContent = t("btn_resolve");
    btn.addEventListener("click", () => {
      resolveOwnerTodo(item.id);
    });
    actions.appendChild(btn);

    wrap.appendChild(head);
    wrap.appendChild(action);
    wrap.appendChild(actions);
    ownerTodos.appendChild(wrap);
  }
}

function lifecycleStageLabel(item) {
  const stage = String(item.lifecycle_stage || "candidate");
  const verdict = String(item.verdict || "").toLowerCase();
  if (stage === "candidate") {
    return t("lifecycle_stage_candidate");
  }
  if (stage === "reviewed" && verdict === "accept") {
    return t("lifecycle_stage_reviewed_accept");
  }
  if (stage === "reviewed" && verdict === "modify") {
    return t("lifecycle_stage_reviewed_modify");
  }
  if (stage === "reviewed" && verdict === "reject") {
    return t("lifecycle_stage_reviewed_reject");
  }
  if (stage === "promoted") {
    return t("lifecycle_stage_promoted");
  }
  return t("lifecycle_stage_active_runtime");
}

function lifecycleNextAction(item) {
  const stage = String(item.lifecycle_stage || "candidate");
  const verdict = String(item.verdict || "").toLowerCase();
  if (stage === "candidate") {
    return t("candidate_next_review");
  }
  if (stage === "reviewed" && verdict === "accept") {
    return t("candidate_next_promote");
  }
  if (stage === "reviewed" && verdict === "modify") {
    return t("candidate_next_rework");
  }
  if (stage === "reviewed" && verdict === "reject") {
    return t("candidate_next_reject");
  }
  if (stage === "promoted") {
    return t("candidate_next_cooling", { hours: Number(item.runtime_hours_remaining || 0) });
  }
  return t("candidate_next_runtime");
}

function renderLearningLifecycle(summary) {
  if (!learningLifecycle) {
    return;
  }
  const lifecycle = summary && typeof summary === "object" ? summary.lifecycle || {} : {};
  const rows = [
    { key: "imported", label: t("lifecycle_step_imported") },
    { key: "candidate", label: t("lifecycle_step_candidate") },
    { key: "reviewed", label: t("lifecycle_step_reviewed") },
    { key: "promoted", label: t("lifecycle_step_promoted") },
    { key: "active_runtime", label: t("lifecycle_step_active_runtime") },
  ];
  learningLifecycle.innerHTML = "";
  for (const row of rows) {
    const card = document.createElement("div");
    card.className = "learning-stage-card";
    const name = document.createElement("div");
    name.className = "learning-stage-name";
    name.textContent = row.label;
    const value = document.createElement("div");
    value.className = "learning-stage-value";
    value.textContent = String(Number(lifecycle[row.key] || 0));
    card.appendChild(name);
    card.appendChild(value);
    learningLifecycle.appendChild(card);
  }
}

function buildCandidateContext(item) {
  const sourceRef =
    (item && (item.source_material_ref || item.source_import_ref)) || t("candidate_source_unknown");
  const evidenceItems = normalizeTextItems(item && item.evidence);
  const sourceItems = normalizeTextItems(item && item.source_refs);

  const context = document.createElement("details");
  context.className = "candidate-context";
  const contextSummary = document.createElement("summary");
  contextSummary.textContent = t("candidate_detail_summary");
  context.appendChild(contextSummary);

  const contextGrid = document.createElement("div");
  contextGrid.className = "candidate-context-grid";

  const makeBlock = (labelText, bodyNode) => {
    const block = document.createElement("div");
    block.className = "candidate-context-block";
    const label = document.createElement("div");
    label.className = "candidate-context-label";
    label.textContent = labelText;
    block.appendChild(label);
    block.appendChild(bodyNode);
    contextGrid.appendChild(block);
  };

  const evidenceBody = buildCompactListBody(evidenceItems, t("candidate_detail_none"), {
    maxVisible: 2,
    maxChars: 170,
    fullJoin: "\n\n",
  });
  makeBlock(t("candidate_detail_evidence"), evidenceBody);

  const sourceBody = buildCompactListBody(sourceItems, sourceRef || t("candidate_source_unknown"), {
    maxVisible: 3,
    maxChars: 150,
    fullJoin: "\n",
  });
  makeBlock(t("candidate_detail_sources"), sourceBody);

  const sections = [
    [t("candidate_detail_created"), formatCandidateCreatedAt(item)],
    [t("candidate_detail_owner_note"), (item && item.owner_note) || "-"],
    [t("candidate_detail_modified"), (item && item.modified_statement) || "-"],
    [t("candidate_detail_promotion_target"), (item && (item.promotion_target || item.proposal_target)) || "-"],
    [t("candidate_detail_runtime"), candidateRuntimeDetail(item)],
  ];

  for (const [labelText, valueText] of sections) {
    const value = document.createElement("div");
    value.className = "candidate-context-value";
    value.textContent = String(valueText || "-");
    makeBlock(labelText, value);
  }

  context.appendChild(contextGrid);
  return context;
}

function renderCandidateCards(container, items, emptyKey) {
  if (!container) {
    return;
  }
  container.innerHTML = "";
  if (!Array.isArray(items) || items.length === 0) {
    renderQueueEmpty(container, t(emptyKey));
    return;
  }

  for (const item of items) {
    const wrap = document.createElement("div");
    wrap.className = `todo-item learning-candidate-card stage-${String(item.lifecycle_stage || "candidate")}`;

    const head = document.createElement("div");
    head.className = "todo-head";
    const metric = document.createElement("span");
    metric.className = "todo-metric";
    metric.textContent = item.candidate_type || "candidate";
    const status = document.createElement("span");
    status.className = "todo-reason lifecycle-badge";
    status.textContent = lifecycleStageLabel(item);
    head.appendChild(metric);
    head.appendChild(status);

    const title = document.createElement("div");
    title.className = "todo-action";
    title.textContent = item.title || item.id || "-";

    const statement = document.createElement("div");
    statement.className = "candidate-statement";
    statement.textContent = `${t("candidate_label_statement")}: ${item.statement || "-"}`;

    const meta = document.createElement("div");
    meta.className = "candidate-meta";
    const sourceRef = item.source_material_ref || item.source_import_ref || t("candidate_source_unknown");
    const confidence = typeof item.confidence === "number" ? `${item.confidence}/10` : "-";
    const rationale = item.rationale || "-";
    const evidence = item.evidence_preview || t("candidate_evidence_none");
    const target = item.proposal_target ? `${item.proposal_target}` : "-";
    const rows = [
      [t("candidate_label_type"), item.candidate_type || "-"],
      [t("candidate_label_target"), target],
      [t("candidate_label_source"), sourceRef],
      [t("candidate_label_confidence"), confidence],
      [t("candidate_label_rationale"), rationale],
      [t("candidate_label_evidence"), evidence],
      [t("candidate_label_status"), lifecycleNextAction(item)],
    ];
    for (const row of rows) {
      const line = document.createElement("div");
      const label = document.createElement("strong");
      label.textContent = `${row[0]}: `;
      const value = document.createElement("span");
      value.textContent = String(row[1]);
      line.appendChild(label);
      line.appendChild(value);
      meta.appendChild(line);
    }

    const context = buildCandidateContext(item);

    const actions = document.createElement("div");
    actions.className = "todo-actions";

    if (item.can_review) {
      const acceptBtn = document.createElement("button");
      acceptBtn.className = "todo-resolve-btn";
      acceptBtn.type = "button";
      acceptBtn.textContent = t("btn_accept");
      acceptBtn.addEventListener("click", () => {
        openLearningReviewModal(item, "accept");
      });
      const rejectBtn = document.createElement("button");
      rejectBtn.className = "todo-resolve-btn";
      rejectBtn.type = "button";
      rejectBtn.textContent = t("btn_reject");
      rejectBtn.addEventListener("click", () => {
        openLearningReviewModal(item, "reject");
      });
      const modifyBtn = document.createElement("button");
      modifyBtn.className = "todo-resolve-btn";
      modifyBtn.type = "button";
      modifyBtn.textContent = t("btn_modify");
      modifyBtn.addEventListener("click", () => {
        openLearningReviewModal(item, "modify");
      });
      actions.appendChild(acceptBtn);
      actions.appendChild(rejectBtn);
      actions.appendChild(modifyBtn);
    } else if (item.can_promote) {
      const promoteBtn = document.createElement("button");
      promoteBtn.className = "todo-resolve-btn";
      promoteBtn.type = "button";
      promoteBtn.textContent = t("btn_promote");
      promoteBtn.addEventListener("click", () => {
        openLearningReviewModal(item, "promote");
      });
      actions.appendChild(promoteBtn);
    } else if (item.lifecycle_stage === "promoted") {
      const coolingBtn = document.createElement("button");
      coolingBtn.className = "todo-resolve-btn";
      coolingBtn.type = "button";
      coolingBtn.disabled = true;
      coolingBtn.textContent = t("lifecycle_stage_promoted");
      actions.appendChild(coolingBtn);
    }

    wrap.appendChild(head);
    wrap.appendChild(title);
    wrap.appendChild(statement);
    wrap.appendChild(meta);
    wrap.appendChild(context);
    wrap.appendChild(actions);
    container.appendChild(wrap);
  }
}

function renderLearningCandidates(items) {
  const total = Array.isArray(items) ? items.length : 0;
  const filtered = filterLearningCandidates(items);
  const buckets = splitLearningCandidates(filtered);
  renderCandidateCards(reviewCandidates, buckets.review, "queue_empty_review");
  renderCandidateCards(promoteCandidates, buckets.promote, "queue_empty_promote");
  updateReviewFilterMeta(filtered.length, total);
}

function renderCandidatePipelineSummary(summary, trend = null) {
  if (!summary || typeof summary !== "object") {
    candidatePipeline.textContent = "-";
    renderLearningLifecycle(null);
    return;
  }
  renderLearningLifecycle(summary);
  const trendSummary = trend && typeof trend === "object" ? trend : null;
  const verdicts = summary.verdicts || {};
  const lifecycle = summary.lifecycle || {};
  const lines = [
    `window_days: ${summary.window_days || 30}`,
    `lifecycle: imported=${Number(lifecycle.imported || 0)} candidate=${Number(lifecycle.candidate || 0)} reviewed=${Number(lifecycle.reviewed || 0)} promoted=${Number(lifecycle.promoted || 0)} active_runtime=${Number(lifecycle.active_runtime || 0)}`,
    `pending_total: ${summary.pending_total || 0}`,
    `reviewed_total: ${summary.reviewed_total || 0}`,
    `verdicts: accept=${verdicts.accept || 0} modify=${verdicts.modify || 0} reject=${verdicts.reject || 0}`,
    `promoted_total: ${summary.promoted_total || 0}`,
    `promotion_conversion_rate: ${(Number(summary.promotion_conversion_rate || 0)).toFixed(3)}`,
  ];
  const readiness = summary.promotion_readiness || {};
  if (readiness && typeof readiness === "object") {
    lines.push(
      `promotion_readiness: ready=${Number(readiness.ready_total || 0)} ` +
        `cooling=${Number(readiness.cooling_total || 0)} ` +
        `maturity_hours=${Number(readiness.maturity_hours || 0)}`
    );
  }
  const pendingByType = summary.pending_by_type || {};
  const pendingKeys = Object.keys(pendingByType);
  if (pendingKeys.length > 0) {
    lines.push("pending_by_type:");
    for (const key of pendingKeys.sort()) {
      lines.push(`  ${key}: ${pendingByType[key]}`);
    }
  }
  const promotedByTarget = summary.promoted_by_target || {};
  const promotedKeys = Object.keys(promotedByTarget);
  if (promotedKeys.length > 0) {
    lines.push("promoted_by_target:");
    for (const key of promotedKeys.sort()) {
      lines.push(`  ${key}: ${promotedByTarget[key]}`);
    }
  }
  const readyByTarget = readiness.ready_by_target || {};
  const readyKeys = Object.keys(readyByTarget);
  if (readyKeys.length > 0) {
    lines.push("ready_by_target:");
    for (const key of readyKeys.sort()) {
      lines.push(`  ${key}: ${readyByTarget[key]}`);
    }
  }
  const coolingByTarget = readiness.cooling_by_target || {};
  const coolingKeys = Object.keys(coolingByTarget);
  if (coolingKeys.length > 0) {
    lines.push("cooling_by_target:");
    for (const key of coolingKeys.sort()) {
      lines.push(`  ${key}: ${coolingByTarget[key]}`);
    }
  }
  if (trendSummary && Array.isArray(trendSummary.comparisons)) {
    lines.push("");
    lines.push("trend_7d_vs_30d:");
    const inflow = trendSummary.inflow || {};
    lines.push(`  inflow: 7d=${Number(inflow["7d"] || 0)} 30d=${Number(inflow["30d"] || 0)}`);
    for (const item of trendSummary.comparisons) {
      if (!item || typeof item !== "object") {
        continue;
      }
      const key = item.key || "unknown";
      const value7 = Number(item.value_7d || 0).toFixed(3);
      const value30 = Number(item.value_30d || 0).toFixed(3);
      const delta = Number(item.delta || 0).toFixed(3);
      const trendTag = String(item.trend || "stable");
      lines.push(`  ${key}: 7d=${value7} 30d=${value30} delta=${delta} trend=${trendTag}`);
    }
  }
  candidatePipeline.textContent = lines.join("\n");
}

function renderSuggestionReviewSummary(summary, trend = null) {
  if (!summary || typeof summary !== "object") {
    suggestionReviewSummary.textContent = "-";
    return;
  }
  const trendSummary = trend && typeof trend === "object" ? trend : null;
  const verdicts = summary.verdicts || {};
  const lines = [
    `window_days: ${summary.window_days || 30}`,
    `verdict_filter: ${summary.verdict_filter || "all"}`,
    `suggestions_total: ${summary.suggestions_total || 0}`,
    `reviewed_total: ${summary.reviewed_total || 0}`,
    `pending_total: ${summary.pending_total || 0}`,
    `review_coverage_rate: ${(Number(summary.review_coverage_rate || 0)).toFixed(3)}`,
    `verdicts: accept=${verdicts.accept || 0} modify=${verdicts.modify || 0} reject=${verdicts.reject || 0}`,
    `corrections_total: ${summary.corrections_total || 0}`,
    `correction_ratio: ${(Number(summary.correction_ratio || 0)).toFixed(3)}`,
  ];

  const recentReviews = Array.isArray(summary.recent_reviews) ? summary.recent_reviews : [];
  if (recentReviews.length > 0) {
    lines.push("recent_reviews:");
    for (const row of recentReviews.slice(0, 5)) {
      if (!row || typeof row !== "object") {
        continue;
      }
      const verdict = row.verdict || "-";
      const suggestionRef = row.suggestion_ref || "-";
      const module = row.module || "-";
      const correction = row.correction_ref ? ` correction=${row.correction_ref}` : "";
      lines.push(`  ${suggestionRef}: ${verdict} module=${module}${correction}`);
    }
  }

  if (trendSummary && Array.isArray(trendSummary.comparisons)) {
    lines.push("");
    lines.push("trend_7d_vs_30d:");
    const windows = trendSummary.windows || {};
    const w7 = windows["7d"] || {};
    const w30 = windows["30d"] || {};
    lines.push(
      `  reviewed_total: 7d=${Number(w7.reviewed_total || 0)} 30d=${Number(w30.reviewed_total || 0)}`
    );
    for (const item of trendSummary.comparisons) {
      if (!item || typeof item !== "object") {
        continue;
      }
      const key = item.key || "unknown";
      const value7 = Number(item.value_7d || 0).toFixed(3);
      const value30 = Number(item.value_30d || 0).toFixed(3);
      const delta = Number(item.delta || 0).toFixed(3);
      const trendTag = String(item.trend || "stable");
      lines.push(`  ${key}: 7d=${value7} 30d=${value30} delta=${delta} trend=${trendTag}`);
    }
  }

  suggestionReviewSummary.textContent = lines.join("\n");
}

function switchEntrypoint(entrypoint) {
  const target = String(entrypoint || "task").trim().toLowerCase();
  for (const tab of entrypointTabs) {
    tab.classList.toggle("active", tab.getAttribute("data-entrypoint") === target);
  }

  if (taskConsolePanel) {
    taskConsolePanel.classList.toggle("active", target === "task");
  }
  if (learningConsolePanel) {
    learningConsolePanel.classList.toggle("active", target === "learning");
  }
  if (auditConsolePanel) {
    auditConsolePanel.classList.toggle("active", target === "audit");
  }

  if (target === "learning") {
    entrypointHint.setAttribute("data-i18n", "hint_learning");
    entrypointHint.textContent = t("hint_learning");
    return;
  }
  if (target === "audit") {
    entrypointHint.setAttribute("data-i18n", "hint_audit");
    entrypointHint.textContent = t("hint_audit");
    return;
  }
  entrypointHint.setAttribute("data-i18n", "hint_task");
  entrypointHint.textContent = t("hint_task");
}

function formatRouteScoring(route) {
  if (!route || typeof route !== "object") {
    return [];
  }
  const scoring = route.scoring;
  if (!scoring || typeof scoring !== "object") {
    return [];
  }

  const asLine = (candidate) => {
    const module = candidate.module || "?";
    const score = typeof candidate.score === "number" ? candidate.score : 0;
    const positive = typeof candidate.positive_hits === "number" ? candidate.positive_hits : 0;
    const negative = typeof candidate.negative_hits === "number" ? candidate.negative_hits : 0;
    const matched = Array.isArray(candidate.matched_keywords) ? candidate.matched_keywords.join(", ") : "-";
    return `  ${module}: s=${score} (+${positive}/-${negative}) [${matched || "-"}]`;
  };

  if (Array.isArray(scoring.manifest_candidates) && scoring.manifest_candidates.length > 0) {
    const lines = ["manifest_candidates:"];
    for (const candidate of scoring.manifest_candidates.slice(0, 3)) {
      lines.push(asLine(candidate));
    }
    return lines;
  }

  if (Array.isArray(scoring.routes_candidates) && scoring.routes_candidates.length > 0) {
    const lines = ["routes_candidates:"];
    for (const candidate of scoring.routes_candidates.slice(0, 3)) {
      lines.push(asLine(candidate));
    }
    return lines;
  }

  return [];
}

function renderInspectResult(data) {
  const routeLines = [
    `module: ${data.module}`,
    `reason: ${data.route.reason}`,
    `keywords: ${(data.route.matched_keywords || []).join(", ") || "-"}`,
  ];
  routeLines.push(...formatRouteScoring(data.route));
  routeTrace.textContent = routeLines.join("\n");

  const planLines = [
    `skill: ${data.plan.skill}`,
    `output_path: ${data.plan.output_path}`,
    `retrieval_hits: ${data.retrieval_hits}`,
  ];
  if (Array.isArray(data.debug_prompts) && data.debug_prompts.length > 0) {
    planLines.push("schema_debugger_prompts:");
    data.debug_prompts.forEach((prompt, idx) => {
      planLines.push(`  ${idx + 1}. ${prompt}`);
    });
  }
  if (Array.isArray(data.debug_sections) && data.debug_sections.length > 0) {
    planLines.push("schema_debugger_output_sections:");
    data.debug_sections.forEach((section, idx) => {
      planLines.push(`  ${idx + 1}. ${section}`);
    });
  }
  planTrace.textContent = planLines.join("\n");

  renderLoadedFiles(data.loaded_files || []);
  latestSuggestionId = null;
  suggestionTrace.textContent = "-";
  setSuggestionReviewEnabled(false);
  renderSuggestionReviewQueue(auditUiSnapshot.suggestion_review_queue);
  renderAuditTimeline();
  if (!data.output_preview) {
    setPreview("-");
    setOutputTokenMeta("-");
  }
}

function suggestionReviewStatusKey(ownerReview) {
  const verdict = String((((ownerReview || {}).verdict || {}).verdict) || "").trim().toLowerCase();
  if (verdict === "accept") {
    return "accept";
  }
  if (verdict === "modify") {
    return "modify";
  }
  if (verdict === "reject") {
    return "reject";
  }
  return "pending";
}

function setAuditSupportSubject(messageKey = "judgment_detail_subject_empty", messageText = "") {
  if (!auditSupportSubject) {
    return;
  }
  if (messageText) {
    auditSupportSubject.removeAttribute("data-i18n");
    auditSupportSubject.textContent = messageText;
    return;
  }
  auditSupportSubject.setAttribute("data-i18n", messageKey);
  auditSupportSubject.textContent = t(messageKey);
}

function setAuditSupportRawVisible(visible) {
  if (auditDetailRawFold) {
    auditDetailRawFold.hidden = !visible;
  }
}

function setAuditSupportActionsVisible(visible) {
  if (suggestionDetailActions) {
    suggestionDetailActions.hidden = !visible;
  }
}

function revealAuditJudgmentDetail() {
  if (!auditJudgmentDetailBlock) {
    return;
  }
  if (auditMachineFold) {
    auditMachineFold.open = true;
  }
  auditJudgmentDetailBlock.dataset.supportReveal = "true";
  if (auditSupportRevealTimer !== null) {
    window.clearTimeout(auditSupportRevealTimer);
  }
  window.requestAnimationFrame(() => {
    auditJudgmentDetailBlock.scrollIntoView({
      behavior: "smooth",
      block: "start",
      inline: "nearest",
    });
  });
  auditSupportRevealTimer = window.setTimeout(() => {
    if (auditJudgmentDetailBlock) {
      delete auditJudgmentDetailBlock.dataset.supportReveal;
    }
    auditSupportRevealTimer = null;
  }, 1600);
}

function syncAuditSupportSelection(kind = null, id = null) {
  auditSupportTarget = {
    kind: kind ? String(kind).trim() : null,
    id: id ? String(id).trim() : null,
  };
  renderSuggestionReviewQueue(auditUiSnapshot.suggestion_review_queue);
  renderAuditTimeline();
}

function renderSuggestionDetailEmpty(messageKey = "suggestion_detail_empty", messageText = "") {
  setAuditSupportSubject("judgment_detail_subject_empty");
  setAuditSupportRawVisible(false);
  setAuditSupportActionsVisible(false);
  suggestionTrace.textContent = "-";
  setSuggestionReviewEnabled(false);
  if (suggestionDetailCard) {
    suggestionDetailCard.innerHTML = "";
    const empty = document.createElement("div");
    empty.className = "suggestion-detail-empty";
    if (messageText) {
      empty.removeAttribute("data-i18n");
      empty.textContent = messageText;
    } else {
      empty.setAttribute("data-i18n", messageKey);
      empty.textContent = t(messageKey);
    }
    suggestionDetailCard.appendChild(empty);
  }
}

function appendSuggestionDetailSection(container, labelKey, value) {
  if (!container || value === null || value === undefined || value === "") {
    return;
  }
  const section = document.createElement("div");
  section.className = "suggestion-detail-section";

  const label = document.createElement("div");
  label.className = "suggestion-detail-label";
  label.textContent = t(labelKey);

  const body = document.createElement("div");
  body.className = "suggestion-detail-value";
  body.textContent = String(value);

  section.appendChild(label);
  section.appendChild(body);
  container.appendChild(section);
}

function appendSuggestionDetailNodeSection(container, labelKey, bodyNode) {
  if (!container || !bodyNode) {
    return;
  }
  const section = document.createElement("div");
  section.className = "suggestion-detail-section";

  const label = document.createElement("div");
  label.className = "suggestion-detail-label";
  label.textContent = t(labelKey);

  section.appendChild(label);
  section.appendChild(bodyNode);
  container.appendChild(section);
}

function formatApproxByteSize(bytes) {
  const size = Number(bytes || 0);
  if (!Number.isFinite(size) || size <= 0) {
    return "0 B";
  }
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(size < 10 * 1024 ? 1 : 0)} KB`;
  }
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function buildCompactListBody(items, emptyText, options = {}) {
  const rows = normalizeTextItems(items);
  const maxVisible = Math.max(1, Number(options.maxVisible || 2));
  const maxChars = Math.max(40, Number(options.maxChars || 180));
  const fullJoin = String(options.fullJoin || "\n");

  const body = document.createElement("div");
  body.className = "compact-detail-body";

  if (rows.length === 0) {
    const empty = document.createElement("div");
    empty.className = "suggestion-detail-value";
    empty.textContent = emptyText;
    body.appendChild(empty);
    return body;
  }

  const shownRows = rows.slice(0, maxVisible);
  let truncated = rows.length > shownRows.length;

  const list = document.createElement("ul");
  list.className = "compact-detail-list";
  for (const row of shownRows) {
    const item = document.createElement("li");
    const clipped = clipText(row, maxChars);
    if (clipped !== row) {
      truncated = true;
    }
    item.textContent = clipped;
    list.appendChild(item);
  }
  body.appendChild(list);

  if (rows.length > 1 || truncated) {
    const meta = document.createElement("div");
    meta.className = "compact-detail-meta";
    meta.textContent = t("detail_compact_showing", {
      shown: shownRows.length,
      total: rows.length,
    });
    body.appendChild(meta);
  }

  if (truncated) {
    const fold = document.createElement("details");
    fold.className = "compact-detail-fold";
    const summary = document.createElement("summary");
    summary.textContent = t("detail_compact_full");
    const full = document.createElement("div");
    full.className = "compact-detail-full";
    full.textContent = rows.join(fullJoin);
    fold.appendChild(summary);
    fold.appendChild(full);
    body.appendChild(fold);
  }

  return body;
}

function buildSnapshotSummaryText(payload) {
  if (!payload || typeof payload !== "object") {
    return "-";
  }
  const keys = Object.keys(payload).filter((key) => payload[key] !== null && payload[key] !== undefined && payload[key] !== "");
  const serialized = JSON.stringify(payload);
  const byteSize = serialized ? serialized.length : 0;
  const listCount = Object.values(payload).reduce((count, value) => {
    if (Array.isArray(value)) {
      return count + value.length;
    }
    return count;
  }, 0);

  const fieldLabel =
    keys.length > 6 ? `${keys.slice(0, 6).join(", ")} +${keys.length - 6}` : keys.join(", ") || "-";
  const lines = [
    `${t("detail_snapshot_fields")}: ${fieldLabel}`,
    `${t("detail_snapshot_size")}: ${formatApproxByteSize(byteSize)}`,
  ];
  if (listCount > 0) {
    lines.push(`${t("detail_snapshot_lists")}: ${listCount}`);
  }
  return lines.join("\n");
}

function renderLearningSupportDetail(item, options = {}) {
  if (!item || typeof item !== "object") {
    renderSuggestionDetailEmpty();
    latestOutputPath = null;
    latestOutputProvider = null;
    setPreview("-");
    setOutputTokenMeta("-");
    return;
  }

  const candidateId = String(item.id || "").trim();
  if (!candidateId) {
    renderSuggestionDetailEmpty();
    latestOutputPath = null;
    latestOutputProvider = null;
    setPreview("-");
    setOutputTokenMeta("-");
    return;
  }

  syncAuditSupportSelection("learning", candidateId);
  setAuditSupportSubject(
    "",
    `${t("judgment_detail_subject_learning")}: ${String(item.title || item.candidate_type || candidateId)}`
  );
  setAuditSupportRawVisible(true);
  setAuditSupportActionsVisible(false);
  suggestionTrace.textContent = JSON.stringify(item, null, 2);

  if (suggestionDetailCard) {
    suggestionDetailCard.innerHTML = "";

    const meta = document.createElement("div");
    meta.className = "suggestion-detail-meta";

    const typeChip = document.createElement("span");
    typeChip.className = "suggestion-detail-chip";
    typeChip.textContent = `${t("candidate_label_type")}: ${String(item.candidate_type || "-")}`;
    meta.appendChild(typeChip);

    const stageChip = document.createElement("span");
    stageChip.className = `suggestion-detail-chip ${learningTimelineStageClass(item)}`;
    stageChip.textContent = `${t("candidate_label_status")}: ${lifecycleStageLabel(item)}`;
    meta.appendChild(stageChip);

    const timeChip = document.createElement("span");
    timeChip.className = "suggestion-detail-chip";
    timeChip.textContent = t(learningTimelineTimeKey(item), {
      created: formatCandidateCreatedAt({ created_at: learningTimelineTimestamp(item) || item.created_at || "" }),
    });
    meta.appendChild(timeChip);

    suggestionDetailCard.appendChild(meta);
    appendSuggestionDetailSection(suggestionDetailCard, "candidate_label_statement", item.statement || "-");
    appendSuggestionDetailSection(
      suggestionDetailCard,
      "candidate_label_source",
      item.source_material_ref || item.source_import_ref || t("candidate_source_unknown")
    );
    appendSuggestionDetailSection(suggestionDetailCard, "candidate_label_rationale", item.rationale || "-");
    appendSuggestionDetailNodeSection(
      suggestionDetailCard,
      "candidate_detail_evidence",
      buildCompactListBody(item.evidence, t("candidate_detail_none"), {
        maxVisible: 2,
        maxChars: 180,
        fullJoin: "\n\n",
      })
    );
    appendSuggestionDetailNodeSection(
      suggestionDetailCard,
      "candidate_detail_sources",
      buildCompactListBody(
        Array.isArray(item.source_refs) && item.source_refs.length > 0
          ? item.source_refs
          : [item.source_material_ref || item.source_import_ref || t("candidate_source_unknown")],
        item.source_material_ref || item.source_import_ref || t("candidate_source_unknown"),
        {
          maxVisible: 3,
          maxChars: 160,
          fullJoin: "\n",
        }
      )
    );
    appendSuggestionDetailSection(suggestionDetailCard, "candidate_detail_owner_note", item.owner_note || "-");
    appendSuggestionDetailSection(suggestionDetailCard, "candidate_detail_modified", item.modified_statement || "-");
    appendSuggestionDetailSection(
      suggestionDetailCard,
      "candidate_detail_promotion_target",
      item.promotion_target || item.proposal_target || "-"
    );
    appendSuggestionDetailSection(suggestionDetailCard, "candidate_detail_runtime", candidateRuntimeDetail(item));
    appendSuggestionDetailSection(suggestionDetailCard, "detail_snapshot_summary", buildSnapshotSummaryText(item));
    appendSuggestionDetailSection(suggestionDetailCard, "judgment_detail_next", lifecycleNextAction(item));
  }

  latestOutputPath = null;
  latestOutputProvider = null;
  setPreview("-");
  setOutputTokenMeta("-");
  setSuggestionReviewEnabled(false);
  if (options && options.openSupport && auditMachineFold) {
    revealAuditJudgmentDetail();
  }
}

function renderSuggestionDetail(data) {
  if (!data || typeof data !== "object" || !data.suggestion || typeof data.suggestion !== "object") {
    renderSuggestionDetailEmpty();
    latestOutputPath = null;
    latestOutputProvider = null;
    setPreview("-");
    setOutputTokenMeta("-");
    return;
  }
  const suggestion = data.suggestion;
  const ownerReview = data.owner_review && typeof data.owner_review === "object" ? data.owner_review : {};
  const verdictRow = ownerReview.verdict && typeof ownerReview.verdict === "object" ? ownerReview.verdict : null;
  const correctionRow = ownerReview.correction && typeof ownerReview.correction === "object" ? ownerReview.correction : null;
  const statusKey = suggestionReviewStatusKey(ownerReview);
  const payload = {
    suggestion,
    run: data.run || null,
    owner_review: ownerReview,
    output_path: data.output_path || null,
    output_preview: data.output_preview || null,
  };
  suggestionTrace.textContent = JSON.stringify(payload, null, 2);
  syncAuditSupportSelection("suggestion", String(suggestion.id || "").trim());
  setAuditSupportSubject("", `${t("judgment_detail_subject_suggestion")}: ${summarizeSuggestionTask(suggestion)}`);
  setAuditSupportRawVisible(true);
  setAuditSupportActionsVisible(statusKey === "pending");

  if (suggestionDetailCard) {
    suggestionDetailCard.innerHTML = "";

    const meta = document.createElement("div");
    meta.className = "suggestion-detail-meta";

    const moduleChip = document.createElement("span");
    moduleChip.className = "suggestion-detail-chip";
    moduleChip.textContent = `${t("suggestion_detail_module")}: ${String(suggestion.module || "-")}`;
    meta.appendChild(moduleChip);

    const createdChip = document.createElement("span");
    createdChip.className = "suggestion-detail-chip";
    createdChip.textContent = `${t("suggestion_detail_created")}: ${formatCandidateCreatedAt(suggestion)}`;
    meta.appendChild(createdChip);

    const statusChip = document.createElement("span");
    statusChip.className = `suggestion-detail-chip status-${statusKey}`;
    statusChip.textContent = `${t("suggestion_detail_status")}: ${t(`suggestion_detail_status_${statusKey}`)}`;
    meta.appendChild(statusChip);

    suggestionDetailCard.appendChild(meta);
    appendSuggestionDetailSection(suggestionDetailCard, "suggestion_detail_task", summarizeSuggestionTask(suggestion));
    appendSuggestionDetailSection(suggestionDetailCard, "suggestion_detail_output", String(data.output_path || "").trim() || "-");
    appendSuggestionDetailSection(suggestionDetailCard, "suggestion_detail_run", String(suggestion.run_ref || "").trim() || "-");

    const focusPoints = Array.isArray(suggestion.audit_focus_points) ? suggestion.audit_focus_points.filter(Boolean) : [];
    appendSuggestionDetailNodeSection(
      suggestionDetailCard,
      "suggestion_detail_focus",
      buildCompactListBody(focusPoints, t("suggestion_detail_focus_none"), {
        maxVisible: 3,
        maxChars: 170,
        fullJoin: "\n",
      })
    );

    if (verdictRow && String(verdictRow.owner_note || "").trim()) {
      appendSuggestionDetailSection(
        suggestionDetailCard,
        "suggestion_detail_owner_note",
        String(verdictRow.owner_note || "").trim()
      );
    }

    if (correctionRow) {
      const correctionSection = document.createElement("div");
      correctionSection.className = "suggestion-detail-section";
      const correctionLabel = document.createElement("div");
      correctionLabel.className = "suggestion-detail-label";
      correctionLabel.textContent = t("suggestion_detail_correction");
      correctionSection.appendChild(correctionLabel);

      const correctionParts = [];
      if (String(correctionRow.replacement_judgment || "").trim()) {
        correctionParts.push(
          `${t("suggestion_detail_replacement")}: ${String(correctionRow.replacement_judgment || "").trim()}`
        );
      }
      if (String(correctionRow.unlike_me_reason || "").trim()) {
        correctionParts.push(`${t("suggestion_detail_reason")}: ${String(correctionRow.unlike_me_reason || "").trim()}`);
      }
      if (String(correctionRow.target_layer || "").trim()) {
        correctionParts.push(`${t("suggestion_detail_target")}: ${String(correctionRow.target_layer || "").trim()}`);
      }

      const correctionBody = document.createElement("div");
      correctionBody.className = "suggestion-detail-value";
      correctionBody.textContent = correctionParts.join("\n");
      correctionSection.appendChild(correctionBody);
      suggestionDetailCard.appendChild(correctionSection);
    }

    appendSuggestionDetailSection(suggestionDetailCard, "detail_snapshot_summary", buildSnapshotSummaryText(payload));
    appendSuggestionDetailSection(
      suggestionDetailCard,
      "suggestion_detail_next",
      t(`suggestion_detail_next_${statusKey}`)
    );
  }

  latestOutputPath = data.output_path || null;
  if (data.run && typeof data.run === "object") {
    latestOutputProvider = data.run.provider || latestOutputProvider;
  }
  setPreview(data.output_preview || "-");
  refreshOutputTokenMeta();
  setSuggestionReviewEnabled(statusKey === "pending");
}

async function loadSuggestionDetail(suggestionId, options = {}) {
  const sid = String(suggestionId || "").trim();
  if (!sid) {
    latestSuggestionId = null;
    if (auditSupportTarget.kind === "suggestion") {
      syncAuditSupportSelection(null, null);
    } else {
      renderSuggestionReviewQueue(auditUiSnapshot.suggestion_review_queue);
      renderAuditTimeline();
    }
    renderSuggestionDetailEmpty();
    latestOutputPath = null;
    latestOutputProvider = null;
    setPreview("-");
    setOutputTokenMeta("-");
    return;
  }
  latestSuggestionId = sid;
  syncAuditSupportSelection("suggestion", sid);
  if (options && options.openSupport && auditMachineFold) {
    auditMachineFold.open = true;
  }
  try {
    const data = await getJson(`/api/suggestion?id=${encodeURIComponent(sid)}`);
    renderSuggestionDetail(data);
    if (options && options.openSupport) {
      revealAuditJudgmentDetail();
    }
  } catch (err) {
    renderSuggestionDetailEmpty("", `load_failed: ${err.message}`);
    suggestionTrace.textContent = `load_failed: ${err.message}`;
    setAuditSupportRawVisible(true);
    setAuditSupportActionsVisible(false);
    latestOutputPath = null;
    latestOutputProvider = null;
    setPreview("-");
    setOutputTokenMeta("-");
    if (options && options.openSupport) {
      revealAuditJudgmentDetail();
    }
  }
}

function focusSuggestionReview(suggestionId) {
  return loadSuggestionDetail(suggestionId, { openSupport: true });
}

function focusLearningTimelineReview(candidateId) {
  const item = findLearningCandidateItem(candidateId);
  if (!item) {
    syncAuditSupportSelection(null, null);
    renderSuggestionDetailEmpty();
    latestOutputPath = null;
    latestOutputProvider = null;
    setPreview("-");
    setOutputTokenMeta("-");
    return;
  }
  renderLearningSupportDetail(item, { openSupport: true });
}

function setSuggestionReviewEnabled(enabled) {
  const active = Boolean(enabled);
  suggestionAcceptBtn.disabled = !active;
  suggestionModifyBtn.disabled = !active;
  suggestionRejectBtn.disabled = !active;
}

function renderRunResult(data) {
  renderInspectResult(data);
  latestOutputPath = data.output_path || null;
  latestOutputProvider = data.provider || providerSelect.value || null;
  latestSuggestionId = data.suggestion_id || null;
  const lines = [
    `output_path: ${data.output_path}`,
    `output_hash: ${data.output_hash}`,
    `module: ${data.module}`,
  ];
  if (data.suggestion_id) {
    lines.push(`suggestion_id: ${data.suggestion_id}`);
  }
  resultTrace.textContent = lines.join("\n");
  setPreview(data.output_preview || "-");
  refreshOutputTokenMeta();
  loadSuggestionDetail(latestSuggestionId);
}

function renderActionResult(data) {
  refreshAuditUiSnapshot(data);
  const out = [];
  const shouldHoldLearningSupport = auditSupportTarget.kind === "learning" && Boolean(auditSupportTarget.id);
  const refreshLearningSupport = () => {
    if (!shouldHoldLearningSupport) {
      return false;
    }
    const selected = findLearningCandidateItem(auditSupportTarget.id);
    if (selected) {
      renderLearningSupportDetail(selected);
    } else {
      syncAuditSupportSelection(null, null);
      renderSuggestionDetailEmpty();
      latestOutputPath = null;
      latestOutputProvider = null;
      setPreview("-");
      setOutputTokenMeta("-");
    }
    return true;
  };
  out.push(`action: ${data.action}`);

  if (data.status) {
    out.push(`status: ${data.status}`);
  }
  if (data.output_path) {
    out.push(`output_path: ${data.output_path}`);
  }
  if (typeof data.routine_count === "number") {
    out.push(`routine_count: ${data.routine_count}`);
  }
  if (data.summary) {
    out.push(`summary: ${JSON.stringify(data.summary)}`);
  }
  if (typeof data.appended_events === "number") {
    out.push(`appended_events: ${data.appended_events}`);
  }
  if (typeof data.appended_insights === "number") {
    out.push(`appended_insights: ${data.appended_insights}`);
  }
  if (typeof data.candidate_total === "number") {
    out.push(`candidate_total: ${data.candidate_total}`);
  }
  if (data.candidate_counts) {
    out.push(`candidate_counts: ${JSON.stringify(data.candidate_counts)}`);
  }
  if (data.import_record_id) {
    out.push(`import_record_id: ${data.import_record_id}`);
  }
  if (data.verdict_record_id) {
    out.push(`verdict_record_id: ${data.verdict_record_id}`);
  }
  if (data.correction_record_id) {
    out.push(`correction_record_id: ${data.correction_record_id}`);
  }
  if (data.candidate_ref) {
    out.push(`candidate_ref: ${data.candidate_ref}`);
  }
  if (data.verdict) {
    out.push(`verdict: ${data.verdict}`);
  }
  if (data.replacement_candidate_ref) {
    out.push(`replacement_candidate_ref: ${data.replacement_candidate_ref}`);
  }
  if (data.approval_record_id) {
    out.push(`approval_record_id: ${data.approval_record_id}`);
  }
  if (data.promotion_record_id) {
    out.push(`promotion_record_id: ${data.promotion_record_id}`);
  }
  if (data.promotion_target) {
    out.push(`promotion_target: ${data.promotion_target}`);
  }
  if (data.module_candidate_ref) {
    out.push(`module_candidate_ref: ${data.module_candidate_ref}`);
  }
  if (data.module_candidate_path) {
    out.push(`module_candidate_path: ${data.module_candidate_path}`);
  }
  if (typeof data.tension_score === "number") {
    out.push(`tension_score: ${data.tension_score}`);
  }
  if (typeof data.signal_count === "number") {
    out.push(`signal_count: ${data.signal_count}`);
  }
  if (typeof data.event_count === "number") {
    out.push(`event_count: ${data.event_count}`);
  }
  if (data.event_id) {
    out.push(`event_id: ${data.event_id}`);
  }
  if (data.cognitive_trend && data.cognitive_trend.windows) {
    out.push("cognitive_trend: 7d_vs_30d");
  }
  if (Array.isArray(data.record_ids) && data.record_ids.length > 0) {
    out.push(`record_ids: ${data.record_ids.join(", ")}`);
  }
  if (Array.isArray(data.errors) && data.errors.length > 0) {
    out.push(`errors: ${data.errors.length}`);
  }
  if (Array.isArray(data.warnings) && data.warnings.length > 0) {
    out.push(`warnings: ${data.warnings.length}`);
  }

  resultTrace.textContent = out.join("\n");

  if (Array.isArray(data.cognition_cards)) {
    renderCognitionCards(data.cognition_cards);
  }
  if (Array.isArray(data.owner_todos)) {
    renderOwnerTodos(data.owner_todos);
  }
  if (Array.isArray(data.learning_candidates)) {
    renderLearningCandidates(data.learning_candidates);
  }
  if (data.candidate_pipeline_summary && typeof data.candidate_pipeline_summary === "object") {
    renderCandidatePipelineSummary(data.candidate_pipeline_summary, data.candidate_pipeline_trend || null);
  }
  if (data.suggestion_review_summary && typeof data.suggestion_review_summary === "object") {
    renderSuggestionReviewSummary(data.suggestion_review_summary, data.suggestion_review_trend || null);
  }

  if (data.output_preview) {
    if (refreshLearningSupport()) {
      return;
    }
    latestOutputPath = data.output_path || latestOutputPath;
    if (providerSelect.value !== "auto") {
      latestOutputProvider = providerSelect.value || latestOutputProvider;
    }
    setPreview(data.output_preview);
    refreshOutputTokenMeta();
    return;
  }
  if (Array.isArray(data.runs) && data.runs.length > 0) {
    if (refreshLearningSupport()) {
      return;
    }
    latestOutputPath = data.runs[0].output_path || latestOutputPath;
    if (providerSelect.value !== "auto") {
      latestOutputProvider = providerSelect.value || latestOutputProvider;
    }
    setPreview(data.runs[0].output_preview || "-");
    refreshOutputTokenMeta();
    return;
  }
  if (data.action === "ingest_learning" && data.preview) {
    const eventPreview = data.preview.event && data.preview.event.event ? data.preview.event.event : "";
    const insightPreview = data.preview.insight && data.preview.insight.insight ? data.preview.insight.insight : "";
    const previewLines = [];
    if (eventPreview) {
      previewLines.push(`event: ${eventPreview}`);
    }
    if (insightPreview) {
      previewLines.push(`insight: ${insightPreview}`);
    }
    if (refreshLearningSupport()) {
      return;
    }
    setPreview(previewLines.join("\n") || "-");
    setOutputTokenMeta("-");
    return;
  }
  if (data.action === "learning_handoff_packet" && data.packet_text) {
    if (refreshLearningSupport()) {
      return;
    }
    setPreview(data.packet_text);
    setOutputTokenMeta("-");
    return;
  }
  if (data.action === "learning_handoff_import" && data.preview) {
    const previewLines = [];
    if (data.preview.import) {
      previewLines.push(`import: ${data.preview.import.id} (${data.preview.import.candidate_count} candidates)`);
    }
    if (Array.isArray(data.preview.candidates) && data.preview.candidates.length > 0) {
      for (const item of data.preview.candidates.slice(0, 5)) {
        previewLines.push(`- [${item.candidate_type}] ${item.title}`);
      }
    }
    if (Array.isArray(data.learning_candidates)) {
      renderLearningCandidates(data.learning_candidates);
    }
    if (refreshLearningSupport()) {
      return;
    }
    setPreview(previewLines.join("\n") || "-");
    setOutputTokenMeta("-");
    return;
  }
  if (refreshLearningSupport()) {
    return;
  }
  setPreview("-");
  setOutputTokenMeta("-");
}

function buildPayload() {
  const model = modelInput.value.trim();
  const providerValue = providerSelect.value;
  return {
    task: taskInput.value.trim(),
    module: moduleSelect.value || null,
    provider: providerValue === "auto" ? null : providerValue,
    model: model || null,
    with_retrieval: retrievalToggle.checked,
    retrieval_top_k: Number(retrievalTopK.value || 6),
  };
}

async function postJson(path, payload) {
  const resp = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });

  let data;
  try {
    data = await resp.json();
  } catch {
    throw new Error(`Request failed (${resp.status})`);
  }

  if (!resp.ok || data.ok === false) {
    const msg = data.error || `Request failed (${resp.status})`;
    throw new Error(msg);
  }

  return data;
}

async function getJson(path) {
  const resp = await fetch(path);
  let data;
  try {
    data = await resp.json();
  } catch {
    throw new Error(`Request failed (${resp.status})`);
  }
  if (!resp.ok || data.ok === false) {
    const msg = data.error || `Request failed (${resp.status})`;
    throw new Error(msg);
  }
  return data;
}

async function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const temp = document.createElement("textarea");
  temp.value = text;
  temp.setAttribute("readonly", "true");
  temp.style.position = "absolute";
  temp.style.left = "-9999px";
  document.body.appendChild(temp);
  temp.select();
  document.execCommand("copy");
  document.body.removeChild(temp);
}

async function copyLatestOutput() {
  if (!latestOutputPath) {
    addBubble("system", t("msg_no_output_yet"));
    return;
  }

  const originalIcon = copyOutputBtn.textContent;
  try {
    const data = await getJson(`/api/output?path=${encodeURIComponent(latestOutputPath)}`);
    await copyText(data.content);
    copyOutputBtn.textContent = "✓";
    setTimeout(() => {
      copyOutputBtn.textContent = originalIcon;
    }, 1200);
  } catch (err) {
    addBubble("system", t("msg_copy_failed", { error: err.message }));
  }
}

async function resolveOwnerTodo(todoId) {
  const id = String(todoId || "").trim();
  if (!id) {
    return;
  }
  const note = window.prompt("Resolution note (required):", "Completed and verified with log evidence.");
  if (note === null) {
    return;
  }
  const noteText = String(note).trim();
  if (!noteText) {
    addBubble("system", "Resolve skipped: note is required.");
    return;
  }
  try {
    const data = await postJson("/api/action", {
      action: "resolve_owner_todo",
      todo_id: id,
      note: noteText,
    });
    if (Array.isArray(data.owner_todos)) {
      renderOwnerTodos(data.owner_todos);
    }
    addBubble("system", t("msg_owner_todo_resolved", { id: data.resolved_todo || id }));
  } catch (err) {
    addBubble("system", t("msg_owner_todo_resolve_failed", { error: err.message }));
  }
}

function openLearningReviewModal(item, mode) {
  if (
    !learningReviewModal ||
    !learningReviewTitle ||
    !learningReviewMeta ||
    !learningReviewNote ||
    !learningReviewStatementWrap ||
    !learningReviewStatement
  ) {
    return;
  }
  const verdict = String(mode || "").trim().toLowerCase();
  if (!["accept", "modify", "reject", "promote"].includes(verdict)) {
    return;
  }
  learningReviewDraft = {
    id: String(item.id || "").trim(),
    verdict,
    statement: String(item.statement || "").trim(),
    title: String(item.title || item.id || "").trim(),
    target: String(item.proposal_target || "").trim(),
    candidate_type: String(item.candidate_type || "").trim(),
  };
  const titleMap = {
    accept: "learning_review_modal_title_accept",
    modify: "learning_review_modal_title_modify",
    reject: "learning_review_modal_title_reject",
    promote: "learning_review_modal_title_promote",
  };
  learningReviewTitle.textContent = t(titleMap[verdict] || "learning_review_modal_title");
  learningReviewMeta.textContent =
    `${learningReviewDraft.title} | ${learningReviewDraft.candidate_type || "candidate"} | ` +
    `target=${learningReviewDraft.target || "-"}`;
  const defaultNotes = {
    accept: uiLanguage === "zh" ? "与当前判断核心一致，建议保留。" : "Aligned with current judgment core.",
    modify: uiLanguage === "zh" ? "方向可用，但表达需收紧。" : "Useful direction but wording needs tightening.",
    reject: uiLanguage === "zh" ? "与当前判断核心不一致，拒绝晋升。" : "Not aligned with current judgment core.",
    promote: uiLanguage === "zh" ? "已完成复核，批准 Promote。" : "Reviewed and approved for promotion.",
  };
  learningReviewNote.value = defaultNotes[verdict] || "";
  const needsStatement = verdict === "modify";
  learningReviewStatementWrap.hidden = !needsStatement;
  learningReviewStatement.value = needsStatement ? learningReviewDraft.statement : "";
  learningReviewModal.classList.remove("hidden");
  learningReviewNote.focus();
}

function closeLearningReviewModal() {
  if (!learningReviewModal) {
    return;
  }
  learningReviewDraft = null;
  learningReviewModal.classList.add("hidden");
}

async function submitLearningReviewModal() {
  if (!learningReviewDraft || !learningReviewNote || !learningReviewStatement) {
    return;
  }
  const id = String(learningReviewDraft.id || "").trim();
  const verdict = String(learningReviewDraft.verdict || "").trim().toLowerCase();
  const ownerNote = String(learningReviewNote.value || "").trim();
  const modifiedStatement = String(learningReviewStatement.value || "").trim();

  if (!id) {
    closeLearningReviewModal();
    return;
  }
  if (!ownerNote) {
    addBubble("system", t("msg_review_note_required"));
    return;
  }
  if (verdict === "modify" && !modifiedStatement) {
    addBubble("system", t("msg_modify_statement_required"));
    return;
  }

  if (verdict === "promote") {
    await promoteLearningCandidate(id, ownerNote);
    closeLearningReviewModal();
    return;
  }
  await reviewLearningCandidate(id, verdict, ownerNote, verdict === "modify" ? modifiedStatement : null);
  closeLearningReviewModal();
}

async function reviewLearningCandidate(candidateId, verdict, ownerNote, modifiedStatement = null) {
  const id = String(candidateId || "").trim();
  if (!id) {
    return;
  }
  const choice = String(verdict || "").trim().toLowerCase();
  if (!["accept", "modify", "reject"].includes(choice)) {
    return;
  }
  const note = String(ownerNote || "").trim();
  if (!note) {
    addBubble("system", t("msg_review_note_required"));
    return;
  }
  const revised = modifiedStatement !== null ? String(modifiedStatement || "").trim() : null;
  if (choice === "modify" && !revised) {
    addBubble("system", t("msg_modify_statement_required"));
    return;
  }

  try {
    const data = await postJson("/api/action", {
      action: "review_learning_candidate",
      candidate_id: id,
      verdict: choice,
      owner_note: note,
      modified_statement: revised,
    });
    renderActionResult(data);
    addBubble("system", t("msg_candidate_review_done", { id, verdict: choice }));
  } catch (err) {
    addBubble("system", t("msg_candidate_review_failed", { error: err.message }));
  }
}

async function promoteLearningCandidate(candidateId, approvalNote) {
  const id = String(candidateId || "").trim();
  if (!id) {
    return;
  }
  const note = String(approvalNote || "").trim();
  if (!note) {
    addBubble("system", t("msg_promotion_note_required"));
    return;
  }

  try {
    const data = await postJson("/api/action", {
      action: "promote_learning_candidate",
      candidate_id: id,
      approval_note: note,
    });
    renderActionResult(data);
    addBubble("system", t("msg_candidate_promoted_done", { id, target: data.promotion_target || "-" }));
  } catch (err) {
    addBubble("system", t("msg_candidate_promote_failed", { error: err.message }));
  }
}

async function refreshOutputTokenMeta() {
  if (!latestOutputPath) {
    setOutputTokenMeta("-");
    return;
  }

  const model = modelInput.value.trim();
  const params = new URLSearchParams({ path: latestOutputPath });
  if (model) {
    params.set("model", model);
  }

  try {
    const data = await getJson(`/api/output-meta?${params.toString()}`);
    const method = data.count_method === "tiktoken" ? "exact" : "estimate";
    setOutputTokenMeta(`Tokens: ${data.prompt_tokens} (${method})`);
  } catch {
    setOutputTokenMeta("Tokens: unavailable");
  }
}

async function loadStatus() {
  try {
    const resp = await fetch("/api/status");
    const data = await resp.json();

    if (!resp.ok || data.ok === false) {
      throw new Error(data.error || "Failed to load status");
    }

    moduleSelect.innerHTML = `<option value="">${t("option_auto_route")}</option>`;
    for (const moduleName of data.modules || []) {
      const option = document.createElement("option");
      option.value = moduleName;
      option.textContent = moduleName;
      moduleSelect.appendChild(option);
    }

    providerSelect.value = "auto";
    modelInput.value = "";
    if (data.ui_language) {
      setLanguage(data.ui_language);
      moduleSelect.innerHTML = `<option value="">${t("option_auto_route")}</option>`;
      for (const moduleName of data.modules || []) {
        const option = document.createElement("option");
        option.value = moduleName;
        option.textContent = moduleName;
        moduleSelect.appendChild(option);
      }
    }
    renderCognitionCards(data.cognition_cards || []);
    renderOwnerTodos(data.owner_todos || []);
    renderLearningCandidates(data.learning_candidates || []);
    renderCandidatePipelineSummary(data.candidate_pipeline_summary || {}, data.candidate_pipeline_trend || null);
    renderSuggestionReviewSummary(data.suggestion_review_summary || {}, data.suggestion_review_trend || null);
    refreshAuditUiSnapshot(data);

    setStatus(t("status_connected"), "ok", "status_connected");
  } catch (err) {
    setStatus(t("status_offline"), "fail", "status_offline");
    addBubble("system", t("msg_connection_failed", { error: err.message }));
  }
}

function applySettingsToForm(settings) {
  const openaiModel = settings.openai_model || settings.task_model || "gpt-4.1-mini";
  settingsApiKey.value = "";
  settingsApiKey.placeholder = settings.has_openai_api_key ? t("settings_key_configured") : "sk-...";
  settingsDeepseekApiKey.value = "";
  settingsDeepseekApiKey.placeholder = settings.has_deepseek_api_key ? t("settings_key_configured") : "sk-...";
  settingsOpenaiBaseUrl.value = settings.openai_base_url || "https://api.openai.com/v1";
  settingsOpenaiModel.value = openaiModel;
  settingsDefaultProvider.value = settings.default_provider || "handoff";
  settingsRoutingModel.value = settings.routing_model || "gpt-4.1-nano";
  settingsDeepseekModel.value = settings.deepseek_model || "deepseek-chat";
  settingsDeepseekBaseUrl.value = settings.deepseek_base_url || "https://api.deepseek.com/v1";
  settingsDecisionProvider.value = settings.decision_provider || "";
  settingsDecisionModel.value = settings.decision_model || "";
  settingsContentProvider.value = settings.content_provider || "";
  settingsContentModel.value = settings.content_model || "";
  settingsCognitionProvider.value = settings.cognition_provider || "";
  settingsCognitionModel.value = settings.cognition_model || "";
  settingsUiLanguage.value = settings.ui_language || "zh";
}

async function loadSettings() {
  try {
    const data = await getJson("/api/settings");
    settingsCache = data;
    setLanguage(data.ui_language || "zh");
    setMvpGuideText("mvp_guide_idle");
    setDemoSummaryKey("demo_summary_idle");
    setAuditGuideKey("audit_guide_idle");
    applySettingsToForm(data);
  } catch (err) {
    addBubble("system", `Settings load failed: ${err.message}`);
  }
}

function openSettingsModal() {
  if (settingsCache) {
    applySettingsToForm(settingsCache);
  }
  settingsModal.classList.remove("hidden");
}

function closeSettingsModal() {
  settingsModal.classList.add("hidden");
}

async function saveSettings() {
  const apiKey = settingsApiKey.value.trim();
  const deepseekApiKey = settingsDeepseekApiKey.value.trim();
  const payload = {
    default_provider: settingsDefaultProvider.value,
    routing_model: settingsRoutingModel.value.trim() || "gpt-4.1-nano",
    openai_model: settingsOpenaiModel.value.trim() || "gpt-4.1-mini",
    openai_base_url: settingsOpenaiBaseUrl.value.trim() || "https://api.openai.com/v1",
    deepseek_model: settingsDeepseekModel.value.trim() || "deepseek-chat",
    deepseek_base_url: settingsDeepseekBaseUrl.value.trim() || "https://api.deepseek.com/v1",
    decision_provider: settingsDecisionProvider.value.trim(),
    decision_model: settingsDecisionModel.value.trim(),
    content_provider: settingsContentProvider.value.trim(),
    content_model: settingsContentModel.value.trim(),
    cognition_provider: settingsCognitionProvider.value.trim(),
    cognition_model: settingsCognitionModel.value.trim(),
    ui_language: settingsUiLanguage.value || "zh",
  };
  if (apiKey) {
    payload.openai_api_key = apiKey;
  }
  if (deepseekApiKey) {
    payload.deepseek_api_key = deepseekApiKey;
  }

  try {
    const data = await postJson("/api/settings", payload);
    settingsCache = data;
    setLanguage(data.ui_language || settingsUiLanguage.value || "zh");
    if (providerSelect.value === "deepseek") {
      modelInput.value = data.deepseek_model || modelInput.value;
    } else if (providerSelect.value === "openai") {
      modelInput.value = data.openai_model || data.task_model || modelInput.value;
    } else if (providerSelect.value === "auto") {
      modelInput.value = "";
    }
    settingsApiKey.value = "";
    settingsDeepseekApiKey.value = "";
    closeSettingsModal();
    addBubble("system", t("msg_settings_saved"));
    loadStatus();
  } catch (err) {
    addBubble("system", `Settings save failed: ${err.message}`);
  }
}

async function inspectTask() {
  const payload = buildPayload();
  if (!payload.task) {
    addBubble("system", t("msg_task_required_inspect"));
    return;
  }

  addUserTaskOnce(payload.task);

  try {
    const data = await postJson("/api/inspect", payload);
    renderInspectResult(data);
    addBubble("system", `Inspect complete: ${data.module} -> ${data.plan.skill}`);
  } catch (err) {
    addBubble("system", `Inspect failed: ${err.message}`);
  }
}

async function runTask() {
  const payload = buildPayload();
  if (!payload.task) {
    addBubble("system", t("msg_task_required_run"));
    return;
  }

  addUserTaskOnce(payload.task);

  try {
    const data = await postJson("/api/run", payload);
    renderRunResult(data);
    addBubble("system", `Run complete. Output: ${data.output_path}`);
  } catch (err) {
    addBubble("system", `Run failed: ${err.message}`);
  }
}

function selectPreferredApiProvider() {
  if (settingsCache && settingsCache.has_deepseek_api_key && providerSelect.querySelector('option[value="deepseek"]')) {
    providerSelect.value = "deepseek";
    if (!modelInput.value.trim() || modelInput.value.includes("gpt-")) {
      modelInput.value = settingsCache.deepseek_model || "deepseek-chat";
    }
    return "deepseek";
  }
  if (settingsCache && settingsCache.has_openai_api_key && providerSelect.querySelector('option[value="openai"]')) {
    providerSelect.value = "openai";
    if (!modelInput.value.trim() || modelInput.value.startsWith("deepseek-")) {
      modelInput.value = settingsCache.openai_model || settingsCache.task_model || "gpt-4.1-mini";
    }
    return "openai";
  }
  return providerSelect.value || "handoff";
}

async function runMvpFlow() {
  if (!settingsCache) {
    await loadSettings();
  }
  const demoTask = "run weekly decision review and output top 3 owner actions with risk notes";
  taskInput.value = demoTask;

  const preferredProvider = selectPreferredApiProvider();
  retrievalToggle.checked = false;
  moduleSelect.value = "";

  addUserTaskOnce(demoTask);
  setMvpGuideText("mvp_guide_inspecting");
  addBubble("system", t("msg_mvp_started"));
  addBubble("system", t("msg_mvp_mode", { provider: preferredProvider }));
  if (!settingsCache || (!settingsCache.has_deepseek_api_key && !settingsCache.has_openai_api_key)) {
    addBubble("system", t("msg_mvp_no_api"));
  }

  try {
    const payload = buildPayload();
    const inspectData = await postJson("/api/inspect", payload);
    renderInspectResult(inspectData);
    addBubble("system", t("msg_mvp_inspect_ready", { module: inspectData.module, skill: inspectData.plan.skill }));

    setMvpGuideText("mvp_guide_running");
    const runData = await postJson("/api/run", payload);
    renderRunResult(runData);
    if (runData.suggestion_id) {
      await loadSuggestionDetail(runData.suggestion_id);
    }

    switchEntrypoint("audit");
    setMvpGuideText("mvp_guide_done");
    addBubble("system", t("msg_mvp_complete"));
  } catch (err) {
    setMvpGuideText("mvp_guide_idle");
    addBubble("system", t("msg_mvp_failed", { error: err.message }));
  }
}

async function runDemoMode() {
  if (!settingsCache) {
    await loadSettings();
  }

  const preferredProvider = selectPreferredApiProvider();
  retrievalToggle.checked = false;
  moduleSelect.value = "";

  const summaryLines = [t("demo_summary_title"), t("demo_mode_provider", { provider: preferredProvider })];
  setDemoSummaryLines(summaryLines);
  addBubble("system", t("demo_started"));
  if (!settingsCache || (!settingsCache.has_deepseek_api_key && !settingsCache.has_openai_api_key)) {
    addBubble("system", t("msg_mvp_no_api"));
  }

  try {
    const decisionTask = "请输出本周决策复盘，并给出3条按优先级排序的风险控制动作。";
    taskInput.value = decisionTask;
    addUserTaskOnce(decisionTask);

    const inspectPayload = buildPayload();
    const inspectData = await postJson("/api/inspect", inspectPayload);
    renderInspectResult(inspectData);

    const runData = await postJson("/api/run", inspectPayload);
    renderRunResult(runData);
    if (runData.suggestion_id) {
      await loadSuggestionDetail(runData.suggestion_id);
    }
    summaryLines.push(
      t("demo_step_decision", {
        module: runData.module || "-",
        output_path: runData.output_path || "-",
        suggestion_id: runData.suggestion_id || "-",
      })
    );
    setDemoSummaryLines(summaryLines);

    const learningPayload = {
      action: "ingest_learning",
      task: "学习样本：高风险决策先写反证条件；情绪波动时先做低负荷执行任务；每周复盘记录触发点与修正动作。",
      title: "Demo 学习样本",
      source_type: "notes",
      max_points: 6,
      confidence: 8,
      tags: ["demo_mode"],
    };
    const learningData = await postJson("/api/action", learningPayload);
    renderActionResult(learningData);
    summaryLines.push(
      t("demo_step_learning", {
        events: learningData.appended_events || 0,
        insights: learningData.appended_insights || 0,
      })
    );
    setDemoSummaryLines(summaryLines);

    const auditData = await postJson("/api/action", { action: "owner_report", window_days: 7 });
    renderActionResult(auditData);
    const failMetrics = Object.entries(auditData.summary || {})
      .filter((entry) => entry[1] === "fail")
      .map((entry) => entry[0]);
    summaryLines.push(
      t("demo_step_audit", {
        output_path: auditData.output_path || "-",
        fails: failMetrics.length > 0 ? failMetrics.join(", ") : t("demo_none"),
      })
    );
    setDemoSummaryLines(summaryLines);
    switchEntrypoint("audit");
    addBubble("system", t("demo_done"));
  } catch (err) {
    summaryLines.push(t("demo_failed", { error: err.message }));
    setDemoSummaryLines(summaryLines);
    addBubble("system", t("demo_failed", { error: err.message }));
  }
}

async function runAuditQuickRun() {
  const lines = [t("audit_guide_title"), t("audit_guide_running")];
  setAuditGuideLines(lines);
  switchEntrypoint("audit");
  addBubble("system", t("audit_guide_running"));

  try {
    const validateData = await postJson("/api/action", { action: "validate", strict: true });
    renderActionResult(validateData);
    lines.push(t("audit_step_validate", { status: validateData.status || "-" }));
    setAuditGuideLines(lines);

    const metricsData = await postJson("/api/action", { action: "metrics", window_days: 7 });
    renderActionResult(metricsData);
    lines.push(
      t("audit_step_metrics", {
        output_path: metricsData.output_path || "-",
      })
    );
    setAuditGuideLines(lines);

    const ownerData = await postJson("/api/action", { action: "owner_report", window_days: 7 });
    renderActionResult(ownerData);
    lines.push(
      t("audit_step_owner", {
        output_path: ownerData.output_path || "-",
        todo_count: Array.isArray(ownerData.owner_todos) ? ownerData.owner_todos.length : 0,
      })
    );
    lines.push(t("audit_guide_done"));
    setAuditGuideLines(lines);
    addBubble("system", t("audit_guide_done"));
  } catch (err) {
    lines.push(t("audit_guide_failed", { error: err.message }));
    setAuditGuideLines(lines);
    addBubble("system", t("audit_guide_failed", { error: err.message }));
  }
}

function openSuggestionReviewModal(suggestionId, mode) {
  if (
    !suggestionReviewModal ||
    !suggestionReviewTitle ||
    !suggestionReviewMeta ||
    !suggestionReviewNote ||
    !suggestionReviewReplacementWrap ||
    !suggestionReviewReplacement ||
    !suggestionReviewReasonWrap ||
    !suggestionReviewReason ||
    !suggestionReviewTargetWrap ||
    !suggestionReviewTarget
  ) {
    return;
  }
  const sid = String(suggestionId || "").trim();
  if (!sid) {
    addBubble("system", t("msg_no_suggestion_selected"));
    return;
  }
  const verdict = String(mode || "").trim().toLowerCase();
  if (!["accept", "modify", "reject"].includes(verdict)) {
    return;
  }
  const item = findSuggestionReviewItem(sid);
  suggestionReviewDraft = {
    id: sid,
    verdict,
    module: String((item && item.module) || "").trim(),
    task: String((item && item.task_raw) || "").trim(),
  };
  const titleMap = {
    accept: "suggestion_review_modal_title_accept",
    modify: "suggestion_review_modal_title_modify",
    reject: "suggestion_review_modal_title_reject",
  };
  suggestionReviewTitle.textContent = t(titleMap[verdict] || "suggestion_review_modal_title");
  const metaParts = [summarizeSuggestionTask(item || { id: sid })];
  if (suggestionReviewDraft.module) {
    metaParts.push(suggestionReviewDraft.module);
  }
  if (item && item.created_at) {
    metaParts.push(formatCandidateCreatedAt(item));
  }
  suggestionReviewMeta.textContent = metaParts.filter(Boolean).join(" | ");

  const defaultNotes = {
    accept: uiLanguage === "zh" ? "与当前判断核心一致，建议保留。" : "Aligned with current judgment core.",
    modify: uiLanguage === "zh" ? "方向可用，但表达和判断边界需要收紧。" : "Direction is usable, but the framing and judgment boundary need tightening.",
    reject: uiLanguage === "zh" ? "与当前判断核心不一致，不建议保留。" : "Not aligned with current judgment core and should not be kept.",
  };
  suggestionReviewNote.value = defaultNotes[verdict] || "";

  const needsCorrection = verdict === "modify";
  suggestionReviewReplacementWrap.hidden = !needsCorrection;
  suggestionReviewReasonWrap.hidden = !needsCorrection;
  suggestionReviewTargetWrap.hidden = !needsCorrection;
  suggestionReviewReplacement.value = "";
  suggestionReviewReason.value = "";
  suggestionReviewTarget.value = suggestionReviewDraft.module || "decision";

  suggestionReviewModal.classList.remove("hidden");
  suggestionReviewNote.focus();
}

function closeSuggestionReviewModal() {
  if (!suggestionReviewModal) {
    return;
  }
  suggestionReviewDraft = null;
  suggestionReviewModal.classList.add("hidden");
}

async function submitSuggestionReviewModal() {
  if (
    !suggestionReviewDraft ||
    !suggestionReviewNote ||
    !suggestionReviewReplacement ||
    !suggestionReviewReason ||
    !suggestionReviewTarget
  ) {
    return;
  }
  const sid = String(suggestionReviewDraft.id || "").trim();
  const verdict = String(suggestionReviewDraft.verdict || "").trim().toLowerCase();
  const ownerNote = String(suggestionReviewNote.value || "").trim();

  if (!sid) {
    closeSuggestionReviewModal();
    return;
  }
  if (!ownerNote) {
    addBubble("system", t("msg_suggestion_note_required"));
    return;
  }

  const payload = {
    action: "review_suggestion",
    suggestion_id: sid,
    verdict,
    owner_note: ownerNote,
  };

  if (verdict === "modify") {
    const replacement = String(suggestionReviewReplacement.value || "").trim();
    const unlikeReason = String(suggestionReviewReason.value || "").trim();
    const targetLayer = String(suggestionReviewTarget.value || "").trim();
    if (!replacement) {
      addBubble("system", t("msg_suggestion_replacement_required"));
      return;
    }
    if (!unlikeReason) {
      addBubble("system", t("msg_suggestion_reason_required"));
      return;
    }
    payload.replacement_judgment = replacement;
    payload.unlike_me_reason = unlikeReason;
    if (targetLayer) {
      payload.correction_target_layer = targetLayer;
    }
  }

  try {
    const data = await postJson("/api/action", payload);
    renderActionResult(data);
    latestSuggestionId = sid;
    if (data.suggestion_detail) {
      renderSuggestionDetail(data.suggestion_detail);
    } else {
      await loadSuggestionDetail(sid);
    }
    await loadStatus();
    addBubble("system", t("msg_suggestion_review_done", { id: sid, verdict }));
    closeSuggestionReviewModal();
  } catch (err) {
    addBubble("system", t("msg_suggestion_review_failed", { error: err.message }));
  }
}

function reviewSuggestion(verdict, suggestionId = null) {
  const sid = String(suggestionId || latestSuggestionId || "").trim();
  if (!sid) {
    addBubble("system", t("msg_no_suggestion_selected"));
    return;
  }
  void focusSuggestionReview(sid);
  openSuggestionReviewModal(sid, verdict);
}

async function runAction(action) {
  const taskText = taskInput.value.trim();
  const learningText = learningDirectInput ? learningDirectInput.value.trim() : "";
  const payload = {
    action,
    provider: providerSelect.value === "auto" ? null : providerSelect.value,
    model: modelInput.value.trim() || null,
    with_retrieval: retrievalToggle.checked,
    retrieval_top_k: Number(retrievalTopK.value || 6),
  };

  if (action === "metrics" || action === "owner_report") {
    payload.window_days = 7;
  }

  if (action === "schedule_weekly") {
    payload.action = "schedule_cycle";
    payload.cycle = "weekly";
    payload.no_owner_report = false;
  }

  if (action === "suggestion_review_summary_all") {
    payload.action = "suggestion_review_summary";
    payload.window_days = 30;
  }
  if (action === "suggestion_review_summary_accept") {
    payload.action = "suggestion_review_summary";
    payload.window_days = 30;
    payload.verdict_filter = "accept";
  }
  if (action === "suggestion_review_summary_modify") {
    payload.action = "suggestion_review_summary";
    payload.window_days = 30;
    payload.verdict_filter = "modify";
  }
  if (action === "suggestion_review_summary_reject") {
    payload.action = "suggestion_review_summary";
    payload.window_days = 30;
    payload.verdict_filter = "reject";
  }

  if (action === "ingest_learning") {
    if (!learningText) {
      addBubble("system", t("msg_learning_text_required"));
      return;
    }
    const confidenceProfile = resolveLearningConfidence(learningText, learningSourceInput.value.trim());
    payload.task = learningText;
    payload.title = learningTitleInput.value.trim() || null;
    payload.source_type = LEARNING_SOURCE_DEFAULT;
    payload.max_points = 6;
    payload.confidence = confidenceProfile.confidence;
    payload.tags = ["ui_one_click"];
    if (confidenceProfile.mode === "auto") {
      addBubble("system", t("msg_learning_confidence_auto", { confidence: confidenceProfile.confidence }));
    } else {
      addBubble(
        "system",
        t("msg_learning_confidence_manual", {
          level: t(`certainty_${confidenceProfile.mode}`),
          confidence: confidenceProfile.confidence,
        })
      );
    }
    addUserTaskOnce(payload.title || learningText.slice(0, 120));
  }

  if (action === "detect_disequilibrium") {
    let topic = taskText;
    if (!topic) {
      const prompted = window.prompt("Topic for disequilibrium scan:", "decision quality");
      topic = prompted ? prompted.trim() : "";
    }
    if (!topic) {
      addBubble("system", "Topic is required for disequilibrium scan.");
      return;
    }
    payload.task = topic;
    payload.window_days = 30;
    payload.tags = ["ui_quick_action"];
    addUserTaskOnce(topic);
  }

  if (action === "cognition_timeline") {
    payload.task = taskText || null;
    payload.window_days = 90;
    payload.tags = ["ui_quick_action"];
    if (taskText) {
      addUserTaskOnce(taskText);
    }
  }

  addBubble("system", t("msg_action_running", { action: payload.action }));

  try {
    const data = await postJson("/api/action", payload);
    renderActionResult(data);
    addBubble("system", t("msg_action_complete", { action: data.action }));
  } catch (err) {
    addBubble("system", t("msg_action_failed", { error: err.message }));
  }
}

async function generateLearningHandoffPacket() {
  const sourceRef = learningSourceInput.value.trim();
  if (!sourceRef) {
    addBubble("system", t("msg_learning_source_required"));
    return;
  }

  const payload = {
    action: "learning_handoff_packet",
    source_ref: sourceRef,
    title: learningTitleInput.value.trim() || null,
    source_type: LEARNING_SOURCE_DEFAULT,
    max_candidates_per_type: 3,
  };

  addBubble("system", t("msg_learning_packet_generating"));
  try {
    const data = await postJson("/api/action", payload);
    renderActionResult(data);
    addBubble("system", t("msg_learning_packet_ready"));
  } catch (err) {
    addBubble("system", t("msg_learning_packet_failed", { error: err.message }));
  }
}

async function importLearningHandoffResponse() {
  const responseText = learningResponseInput.value.trim();
  if (!responseText) {
    addBubble("system", t("msg_learning_response_required"));
    return;
  }
  const sourceRef = learningSourceInput.value.trim();
  const confidenceProfile = resolveLearningConfidence(responseText, sourceRef);

  const payload = {
    action: "learning_handoff_import",
    response_text: responseText,
    source_ref: sourceRef || null,
    title: learningTitleInput.value.trim() || null,
    source_type: LEARNING_SOURCE_DEFAULT,
    confidence: confidenceProfile.confidence,
    tags: ["ui_learning_handoff"],
  };

  if (confidenceProfile.mode === "auto") {
    addBubble("system", t("msg_learning_confidence_auto", { confidence: confidenceProfile.confidence }));
  } else {
    addBubble(
      "system",
      t("msg_learning_confidence_manual", {
        level: t(`certainty_${confidenceProfile.mode}`),
        confidence: confidenceProfile.confidence,
      })
    );
  }
  addBubble("system", t("msg_learning_importing"));
  try {
    const data = await postJson("/api/action", payload);
    renderActionResult(data);
    addBubble("system", t("msg_learning_import_done", { count: data.candidate_total || 0 }));
  } catch (err) {
    addBubble("system", t("msg_learning_import_failed", { error: err.message }));
  }
}

inspectBtn.addEventListener("click", (event) => {
  event.preventDefault();
  inspectTask();
});

if (mvpFlowBtn) {
  mvpFlowBtn.addEventListener("click", (event) => {
    event.preventDefault();
    runMvpFlow();
  });
}

if (demoModeBtn) {
  demoModeBtn.addEventListener("click", (event) => {
    event.preventDefault();
    runDemoMode();
  });
}

if (auditQuickRunBtn) {
  auditQuickRunBtn.addEventListener("click", (event) => {
    event.preventDefault();
    runAuditQuickRun();
  });
}
if (auditShowManualBtn) {
  auditShowManualBtn.addEventListener("click", () => {
    auditManualForcedVisible = true;
    updateAuditConsoleDensity();
  });
}

function rerenderReviewInbox() {
  updateReviewPresetButtons();
  persistReviewPresetSelection();
  renderReviewInboxSummary();
  renderLearningCandidates(auditUiSnapshot.learning_candidates);
}

function rerenderAuditTimeline() {
  auditTimelineFilterState = normalizeAuditTimelineFilterState(auditTimelineFilterState);
  syncAuditTimelineFilterControls();
  renderAuditTimeline();
}

for (const button of reviewPresetButtons) {
  button.addEventListener("click", () => {
    applyReviewPreset(String(button.dataset.reviewPreset || "all"));
  });
}

if (reviewStageFilter) {
  reviewStageFilter.addEventListener("change", () => {
    reviewFilterState.stage = reviewStageFilter.value || "all";
    rerenderReviewInbox();
  });
}

if (reviewTypeFilter) {
  reviewTypeFilter.addEventListener("change", () => {
    reviewFilterState.type = reviewTypeFilter.value || "all";
    rerenderReviewInbox();
  });
}

if (reviewSourceFilter) {
  reviewSourceFilter.addEventListener("input", () => {
    reviewFilterState.source = reviewSourceFilter.value || "";
    rerenderReviewInbox();
  });
}

if (reviewAgeFilter) {
  reviewAgeFilter.addEventListener("change", () => {
    reviewFilterState.age = reviewAgeFilter.value || "all";
    rerenderReviewInbox();
  });
}

if (reviewFilterResetBtn) {
  reviewFilterResetBtn.addEventListener("click", () => {
    applyReviewPreset("all");
  });
}

if (auditTimelineKindFilter) {
  auditTimelineKindFilter.addEventListener("change", () => {
    auditTimelineFilterState.kind = auditTimelineKindFilter.value || "all";
    rerenderAuditTimeline();
  });
}

if (auditTimelineStatusFilter) {
  auditTimelineStatusFilter.addEventListener("change", () => {
    auditTimelineFilterState.status = auditTimelineStatusFilter.value || "all";
    rerenderAuditTimeline();
  });
}

if (auditTimelineAgeFilter) {
  auditTimelineAgeFilter.addEventListener("change", () => {
    auditTimelineFilterState.age = auditTimelineAgeFilter.value || "all";
    rerenderAuditTimeline();
  });
}

if (auditTimelineResetBtn) {
  auditTimelineResetBtn.addEventListener("click", () => {
    auditTimelineFilterState = normalizeAuditTimelineFilterState();
    rerenderAuditTimeline();
  });
}

taskForm.addEventListener("submit", (event) => {
  event.preventDefault();
  runTask();
});

for (const button of document.querySelectorAll(".chip[data-task]")) {
  button.addEventListener("click", () => {
    taskInput.value = button.getAttribute("data-task") || "";
    taskInput.focus();
  });
}

for (const button of document.querySelectorAll(".chip.action")) {
  button.addEventListener("click", () => {
    const action = button.getAttribute("data-action");
    if (!action) {
      return;
    }
    runAction(action);
  });
}

for (const tab of entrypointTabs) {
  tab.addEventListener("click", () => {
    const target = tab.getAttribute("data-entrypoint") || "task";
    switchEntrypoint(target);
  });
}

const THEME_KEY = "pcos_theme";

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  document.body.setAttribute("data-theme", theme);
  themeToggle.textContent = theme === "dark" ? "☾" : "☀";
}

function initTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = saved || (prefersDark ? "dark" : "light");
  applyTheme(theme);
}

themeToggle.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const next = current === "dark" ? "light" : "dark";
  applyTheme(next);
  localStorage.setItem(THEME_KEY, next);
});

copyOutputBtn.addEventListener("click", () => {
  copyLatestOutput();
});
providerSelect.addEventListener("change", () => {
  if (providerSelect.value === "auto") {
    modelInput.value = "";
  } else if (providerSelect.value === "deepseek") {
    const current = modelInput.value.trim();
    if (!current || current.startsWith("gpt-")) {
      modelInput.value = (settingsCache && settingsCache.deepseek_model) || "deepseek-chat";
    }
  } else if (providerSelect.value === "openai") {
    const current = modelInput.value.trim();
    if (!current || current.startsWith("deepseek-")) {
      modelInput.value =
        (settingsCache && (settingsCache.openai_model || settingsCache.task_model)) || "gpt-4.1-mini";
    }
  }
  latestOutputProvider = providerSelect.value === "auto" ? latestOutputProvider : providerSelect.value || latestOutputProvider;
  refreshOutputTokenMeta();
});
modelInput.addEventListener("change", () => {
  refreshOutputTokenMeta();
});
settingsToggle.addEventListener("click", () => {
  openSettingsModal();
});
settingsClose.addEventListener("click", () => {
  closeSettingsModal();
});
settingsSave.addEventListener("click", () => {
  saveSettings();
});
settingsModal.addEventListener("click", (event) => {
  if (event.target === settingsModal) {
    closeSettingsModal();
  }
});
if (learningReviewClose) {
  learningReviewClose.addEventListener("click", () => {
    closeLearningReviewModal();
  });
}
if (learningReviewCancel) {
  learningReviewCancel.addEventListener("click", () => {
    closeLearningReviewModal();
  });
}
if (learningReviewSubmit) {
  learningReviewSubmit.addEventListener("click", () => {
    submitLearningReviewModal();
  });
}
if (learningReviewModal) {
  learningReviewModal.addEventListener("click", (event) => {
    if (event.target === learningReviewModal) {
      closeLearningReviewModal();
    }
  });
}
if (suggestionReviewClose) {
  suggestionReviewClose.addEventListener("click", () => {
    closeSuggestionReviewModal();
  });
}
if (suggestionReviewCancel) {
  suggestionReviewCancel.addEventListener("click", () => {
    closeSuggestionReviewModal();
  });
}
if (suggestionReviewSubmit) {
  suggestionReviewSubmit.addEventListener("click", () => {
    submitSuggestionReviewModal();
  });
}
if (suggestionReviewModal) {
  suggestionReviewModal.addEventListener("click", (event) => {
    if (event.target === suggestionReviewModal) {
      closeSuggestionReviewModal();
    }
  });
}
if (quickIngestBtn) {
  quickIngestBtn.addEventListener("click", () => {
    runAction("ingest_learning");
  });
}
if (learningPacketBtn) {
  learningPacketBtn.addEventListener("click", () => {
    generateLearningHandoffPacket();
  });
}
if (learningImportBtn) {
  learningImportBtn.addEventListener("click", () => {
    importLearningHandoffResponse();
  });
}
if (toggleMessagesBtn) {
  toggleMessagesBtn.addEventListener("click", () => {
    setMessagePanelExpanded(!messagesExpanded);
  });
}
suggestionAcceptBtn.addEventListener("click", () => {
  reviewSuggestion("accept");
});
suggestionModifyBtn.addEventListener("click", () => {
  reviewSuggestion("modify");
});
suggestionRejectBtn.addEventListener("click", () => {
  reviewSuggestion("reject");
});

setLanguage("zh");
setMessagePanelExpanded(false);
renderLatestMessage();
setMvpGuideText("mvp_guide_idle");
setDemoSummaryKey("demo_summary_idle");
setAuditGuideKey("audit_guide_idle");
setStatus(t("status_connecting"), "pending", "status_connecting");
initTheme();
initReviewPresetSelection();
rerenderAuditTimeline();
switchEntrypoint("audit");
setSuggestionReviewEnabled(false);
updateAuditConsoleDensity();
loadStatus();
loadSettings();
setOutputTokenMeta("-");
