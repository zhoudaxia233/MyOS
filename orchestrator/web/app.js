const chatLog = document.getElementById("chatLog");
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
const learningDirectInput = document.getElementById("learningDirectInput");
const learningTitleInput = document.getElementById("learningTitleInput");
const learningSourceType = document.getElementById("learningSourceType");
const learningConfidence = document.getElementById("learningConfidence");
const learningSourceInput = document.getElementById("learningSourceInput");
const learningResponseInput = document.getElementById("learningResponseInput");
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
const ownerTodos = document.getElementById("ownerTodos");
const learningCandidates = document.getElementById("learningCandidates");
const candidatePipeline = document.getElementById("candidatePipeline");
const suggestionReviewSummary = document.getElementById("suggestionReviewSummary");
const mvpGuide = document.getElementById("mvpGuide");
const settingsModal = document.getElementById("settingsModal");
const settingsClose = document.getElementById("settingsClose");
const settingsSave = document.getElementById("settingsSave");
const settingsApiKey = document.getElementById("settingsApiKey");
const settingsDeepseekApiKey = document.getElementById("settingsDeepseekApiKey");
const settingsDefaultProvider = document.getElementById("settingsDefaultProvider");
const settingsRoutingModel = document.getElementById("settingsRoutingModel");
const settingsTaskModel = document.getElementById("settingsTaskModel");
const settingsDeepseekModel = document.getElementById("settingsDeepseekModel");
const settingsDeepseekBaseUrl = document.getElementById("settingsDeepseekBaseUrl");
const settingsUiLanguage = document.getElementById("settingsUiLanguage");
let latestOutputPath = null;
let latestOutputProvider = null;
let latestSuggestionId = null;
let settingsCache = null;
let uiLanguage = "zh";

const I18N = {
  zh: {
    doc_title: "Personal Core OS | V1 控制台",
    app_title: "Personal Core OS",
    app_subtitle: "V1 控制台",
    status_connecting: "连接中...",
    status_connected: "已连接",
    status_offline: "离线",
    tab_task: "任务台",
    tab_learning: "学习 / 演化",
    tab_audit: "审计台",
    hint_task: "先检查路由和计划，再执行任务。",
    hint_learning: "可直接导入学习内容，或用低成本 handoff，再复核候选。",
    hint_audit: "在这里做漂移检查、报告复核和候选治理。",
    label_task: "任务",
    task_placeholder: "描述你要做的事...",
    label_module: "模块",
    option_auto_route: "自动路由",
    label_provider: "Provider",
    label_model: "模型",
    model_placeholder: "gpt-4.1-mini / deepseek-chat",
    label_use_retrieval: "启用检索",
    label_top_k: "Top K",
    btn_inspect: "检查",
    btn_run: "执行",
    task_starters: "快捷任务",
    starter_weekly_review: "每周决策复盘",
    starter_extract_patterns: "提取本周聊天模式",
    starter_write_story: "写一篇饭后 BTC 市场故事",
    btn_run_mvp: "一键跑通 MVP（检查 -> 执行 -> 复核）",
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
    trace_cognition_signals: "认知信号（7天）",
    trace_owner_todos: "Owner 待办",
    trace_learning_candidates: "学习候选",
    trace_candidate_pipeline: "候选管道（30天 + 趋势）",
    trace_suggestion_reviews: "建议复核（30天 + 趋势）",
    trace_route: "路由",
    trace_plan: "计划",
    trace_loaded_files: "已加载文件",
    trace_result: "结果",
    trace_suggestion_detail: "建议详情",
    trace_output_preview: "输出预览",
    btn_accept: "接受",
    btn_modify: "修改",
    btn_reject: "拒绝",
    btn_resolve: "完成",
    settings_title: "设置",
    settings_openai_key: "OpenAI API Key",
    settings_deepseek_key: "DeepSeek API Key",
    settings_default_provider: "默认 Provider",
    settings_routing_model: "路由模型（轻）",
    settings_task_model: "任务模型（主）",
    settings_deepseek_model: "DeepSeek 模型",
    settings_deepseek_base_url: "DeepSeek Base URL",
    settings_ui_language: "界面语言",
    btn_save: "保存",
    settings_key_configured: "已配置（本地存储）",
    msg_settings_saved: "设置已保存。",
    msg_connection_failed: "连接失败：{error}",
    msg_copy_failed: "复制失败：{error}",
    msg_no_output_yet: "暂无输出，请先执行任务。",
    msg_no_suggestion_selected: "还没有 suggestion，请先执行任务。",
    no_cognition_metrics: "暂无认知指标",
    run_metrics_first: "先运行 Metrics 7D。",
    msg_mvp_started: "MVP 已开始：检查 -> 执行 -> 建议详情。",
    msg_mvp_inspect_ready: "MVP 检查完成：{module} -> {skill}",
    msg_mvp_complete: "MVP 完成。请在 Suggestion Detail 区域做 Accept/Modify/Reject。",
    msg_mvp_failed: "MVP 失败：{error}",
    msg_mvp_mode: "MVP 当前执行模式：{provider}",
    msg_mvp_no_api: "未检测到 DeepSeek/OpenAI key，当前会走非 API 模式。",
    msg_task_required_inspect: "请先填写任务，再检查。",
    msg_task_required_run: "请先填写任务，再执行。",
    msg_no_suggestion_selected: "还没有 suggestion，请先执行任务。",
  },
  en: {
    doc_title: "Personal Core OS | V1 Control Center",
    app_title: "Personal Core OS",
    app_subtitle: "V1 Control Center",
    status_connecting: "Connecting...",
    status_connected: "Connected",
    status_offline: "Offline",
    tab_task: "Task Console",
    tab_learning: "Learning / Evolution",
    tab_audit: "Audit Console",
    hint_task: "Ask the system to do work, inspect route/plan first, then run.",
    hint_learning: "Ingest material directly or run low-cost external handoff, then review candidates.",
    hint_audit: "Review drift, reports, and candidate queues before promoting long-term changes.",
    label_task: "Task",
    task_placeholder: "Describe what you want to do...",
    label_module: "Module",
    option_auto_route: "Auto route",
    label_provider: "Provider",
    label_model: "Model",
    model_placeholder: "gpt-4.1-mini / deepseek-chat",
    label_use_retrieval: "Use retrieval",
    label_top_k: "Top K",
    btn_inspect: "Inspect",
    btn_run: "Run",
    task_starters: "Task Starters",
    starter_weekly_review: "Weekly Decision Review",
    starter_extract_patterns: "Extract Chat Patterns",
    starter_write_story: "Write After-Meal Story",
    btn_run_mvp: "Run MVP Flow (Inspect -> Run -> Review)",
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
    trace_cognition_signals: "Cognition Signals (7D)",
    trace_owner_todos: "Owner Todos",
    trace_learning_candidates: "Learning Candidates",
    trace_candidate_pipeline: "Candidate Pipeline (30D + Trend)",
    trace_suggestion_reviews: "Suggestion Reviews (30D + Trend)",
    trace_route: "Route",
    trace_plan: "Plan",
    trace_loaded_files: "Loaded Files",
    trace_result: "Result",
    trace_suggestion_detail: "Suggestion Detail",
    trace_output_preview: "Output Preview",
    btn_accept: "Accept",
    btn_modify: "Modify",
    btn_reject: "Reject",
    btn_resolve: "Resolve",
    settings_title: "Settings",
    settings_openai_key: "OpenAI API Key",
    settings_deepseek_key: "DeepSeek API Key",
    settings_default_provider: "Default Provider",
    settings_routing_model: "Routing Model (lighter)",
    settings_task_model: "Task Model (main)",
    settings_deepseek_model: "DeepSeek Model",
    settings_deepseek_base_url: "DeepSeek Base URL",
    settings_ui_language: "UI Language",
    btn_save: "Save",
    settings_key_configured: "Configured (stored locally)",
    msg_settings_saved: "Settings saved.",
    msg_connection_failed: "Connection failed: {error}",
    msg_copy_failed: "Copy failed: {error}",
    msg_no_output_yet: "No output yet. Run a task first.",
    msg_no_suggestion_selected: "No suggestion selected. Run a task first.",
    msg_mvp_started: "MVP flow started: Inspect -> Run -> Suggestion detail.",
    msg_mvp_inspect_ready: "MVP inspect ready: {module} -> {skill}",
    msg_mvp_complete: "MVP flow complete. Review Suggestion Detail and click Accept/Modify/Reject.",
    msg_mvp_failed: "MVP flow failed: {error}",
    msg_mvp_mode: "MVP execution mode: {provider}",
    msg_mvp_no_api: "No DeepSeek/OpenAI key found, running without direct API provider.",
    msg_task_required_inspect: "Task is required for inspect.",
    msg_task_required_run: "Task is required for run.",
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

function setLanguage(lang) {
  uiLanguage = lang === "en" ? "en" : "zh";
  applyI18n();
  const autoOption = moduleSelect.querySelector('option[value=""]');
  if (autoOption) {
    autoOption.textContent = t("option_auto_route");
  }
}

function addBubble(role, text) {
  const div = document.createElement("div");
  div.className = `bubble ${role}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
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
    title.textContent = item.label || item.key || "Metric";

    const value = document.createElement("div");
    value.className = "metric-value";
    value.textContent = item.value || "-";

    const meta = document.createElement("div");
    meta.className = "metric-meta";
    const op = item.target_operator || ">=";
    const threshold = item.threshold || "-";
    meta.textContent = `target ${op} ${threshold} | trend: ${trend} (${delta})`;

    card.appendChild(title);
    card.appendChild(value);
    card.appendChild(meta);
    cognitionCards.appendChild(card);
  }
}

function renderOwnerTodos(items) {
  ownerTodos.innerHTML = "";
  if (!Array.isArray(items) || items.length === 0) {
    const empty = document.createElement("div");
    empty.className = "todo-item";
    empty.innerHTML = "<div class=\"todo-head\"><span class=\"todo-metric\">-</span></div><div class=\"todo-action\">-</div>";
    ownerTodos.appendChild(empty);
    return;
  }

  for (const item of items) {
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

function renderLearningCandidates(items) {
  learningCandidates.innerHTML = "";
  if (!Array.isArray(items) || items.length === 0) {
    const empty = document.createElement("div");
    empty.className = "todo-item";
    empty.innerHTML = "<div class=\"todo-head\"><span class=\"todo-metric\">-</span></div><div class=\"todo-action\">-</div>";
    learningCandidates.appendChild(empty);
    return;
  }

  for (const item of items) {
    const wrap = document.createElement("div");
    wrap.className = "todo-item";

    const head = document.createElement("div");
    head.className = "todo-head";
    const metric = document.createElement("span");
    metric.className = "todo-metric";
    metric.textContent = item.candidate_type || "candidate";
    const reason = document.createElement("span");
    reason.className = "todo-reason";
    reason.textContent = item.proposal_target ? `target: ${item.proposal_target}` : "";
    head.appendChild(metric);
    head.appendChild(reason);

    const action = document.createElement("div");
    action.className = "todo-action";
    action.textContent = item.title || item.id || "-";

    const actions = document.createElement("div");
    actions.className = "todo-actions";

    const acceptBtn = document.createElement("button");
    acceptBtn.className = "todo-resolve-btn";
    acceptBtn.type = "button";
    acceptBtn.textContent = t("btn_accept");
    acceptBtn.addEventListener("click", () => {
      reviewLearningCandidate(item.id, "accept");
    });

    const rejectBtn = document.createElement("button");
    rejectBtn.className = "todo-resolve-btn";
    rejectBtn.type = "button";
    rejectBtn.textContent = t("btn_reject");
    rejectBtn.addEventListener("click", () => {
      reviewLearningCandidate(item.id, "reject");
    });

    const modifyBtn = document.createElement("button");
    modifyBtn.className = "todo-resolve-btn";
    modifyBtn.type = "button";
    modifyBtn.textContent = t("btn_modify");
    modifyBtn.addEventListener("click", () => {
      reviewLearningCandidate(item.id, "modify");
    });

    actions.appendChild(acceptBtn);
    actions.appendChild(rejectBtn);
    actions.appendChild(modifyBtn);

    wrap.appendChild(head);
    wrap.appendChild(action);
    wrap.appendChild(actions);
    learningCandidates.appendChild(wrap);
  }
}

function renderCandidatePipelineSummary(summary, trend = null) {
  if (!summary || typeof summary !== "object") {
    candidatePipeline.textContent = "-";
    return;
  }
  const trendSummary = trend && typeof trend === "object" ? trend : null;
  const verdicts = summary.verdicts || {};
  const lines = [
    `window_days: ${summary.window_days || 30}`,
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

  taskConsolePanel.classList.toggle("active", target === "task");
  learningConsolePanel.classList.toggle("active", target === "learning");
  auditConsolePanel.classList.toggle("active", target === "audit");

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
  if (!data.output_preview) {
    setPreview("-");
    setOutputTokenMeta("-");
  }
}

function renderSuggestionDetail(data) {
  if (!data || typeof data !== "object" || !data.suggestion || typeof data.suggestion !== "object") {
    suggestionTrace.textContent = "-";
    setSuggestionReviewEnabled(false);
    return;
  }
  const payload = {
    suggestion: data.suggestion,
    run: data.run || null,
    owner_review: data.owner_review || null,
    output_path: data.output_path || null,
    output_preview: data.output_preview || null,
  };
  suggestionTrace.textContent = JSON.stringify(payload, null, 2);
  setSuggestionReviewEnabled(true);
}

async function loadSuggestionDetail(suggestionId) {
  const sid = String(suggestionId || "").trim();
  if (!sid) {
    suggestionTrace.textContent = "-";
    setSuggestionReviewEnabled(false);
    return;
  }
  try {
    const data = await getJson(`/api/suggestion?id=${encodeURIComponent(sid)}`);
    renderSuggestionDetail(data);
  } catch (err) {
    suggestionTrace.textContent = `load_failed: ${err.message}`;
    setSuggestionReviewEnabled(false);
  }
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
  const out = [];
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
    latestOutputPath = data.output_path || latestOutputPath;
    latestOutputProvider = providerSelect.value || latestOutputProvider;
    setPreview(data.output_preview);
    refreshOutputTokenMeta();
    return;
  }
  if (Array.isArray(data.runs) && data.runs.length > 0) {
    latestOutputPath = data.runs[0].output_path || latestOutputPath;
    latestOutputProvider = providerSelect.value || latestOutputProvider;
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
    setPreview(previewLines.join("\n") || "-");
    setOutputTokenMeta("-");
    return;
  }
  if (data.action === "learning_handoff_packet" && data.packet_text) {
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
    setPreview(previewLines.join("\n") || "-");
    setOutputTokenMeta("-");
    return;
  }
  setPreview("-");
  setOutputTokenMeta("-");
}

function buildPayload() {
  const model = modelInput.value.trim();
  return {
    task: taskInput.value.trim(),
    module: moduleSelect.value || null,
    provider: providerSelect.value,
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
    addBubble("system", `Resolved owner todo: ${data.resolved_todo}`);
  } catch (err) {
    addBubble("system", `Resolve failed: ${err.message}`);
  }
}

async function reviewLearningCandidate(candidateId, verdict) {
  const id = String(candidateId || "").trim();
  if (!id) {
    return;
  }
  const choice = String(verdict || "").trim().toLowerCase();
  if (!["accept", "modify", "reject"].includes(choice)) {
    return;
  }

  let ownerNote = "";
  let modifiedStatement = null;
  if (choice === "accept") {
    ownerNote = window.prompt("Accept note:", "Accepted as aligned with current judgment.") || "";
  } else if (choice === "reject") {
    ownerNote = window.prompt("Reject reason:", "Not aligned with my operating model.") || "";
  } else {
    ownerNote = window.prompt("Modify reason:", "Useful idea but needs stricter wording.") || "";
    modifiedStatement = window.prompt("Modified statement:", "") || "";
  }

  ownerNote = ownerNote.trim();
  if (!ownerNote) {
    addBubble("system", "Review skipped: note is required.");
    return;
  }
  if (choice === "modify" && !String(modifiedStatement || "").trim()) {
    addBubble("system", "Modify skipped: modified statement is required.");
    return;
  }

  try {
    const data = await postJson("/api/action", {
      action: "review_learning_candidate",
      candidate_id: id,
      verdict: choice,
      owner_note: ownerNote,
      modified_statement: modifiedStatement,
    });
    renderActionResult(data);
    addBubble("system", `Candidate reviewed: ${id} -> ${choice}`);
    if (choice === "accept") {
      const doPromote = window.confirm("Promote this accepted candidate now?");
      if (doPromote) {
        await promoteLearningCandidate(id);
      }
    }
  } catch (err) {
    addBubble("system", `Candidate review failed: ${err.message}`);
  }
}

async function promoteLearningCandidate(candidateId) {
  const id = String(candidateId || "").trim();
  if (!id) {
    return;
  }
  const approvalNote = window.prompt("Promotion approval note:", "Approved for promotion after owner review.");
  const note = approvalNote ? approvalNote.trim() : "";
  if (!note) {
    addBubble("system", "Promotion skipped: approval note is required.");
    return;
  }

  try {
    const data = await postJson("/api/action", {
      action: "promote_learning_candidate",
      candidate_id: id,
      approval_note: note,
    });
    renderActionResult(data);
    addBubble("system", `Candidate promoted: ${id} -> ${data.promotion_target}`);
  } catch (err) {
    addBubble("system", `Candidate promotion failed: ${err.message}`);
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

    if (data.default_provider) {
      providerSelect.value = data.default_provider;
    }
    if (data.default_model) {
      modelInput.value = data.default_model;
    }
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

    setStatus(t("status_connected"), "ok", "status_connected");
  } catch (err) {
    setStatus(t("status_offline"), "fail", "status_offline");
    addBubble("system", t("msg_connection_failed", { error: err.message }));
  }
}

function applySettingsToForm(settings) {
  settingsApiKey.value = "";
  settingsApiKey.placeholder = settings.has_openai_api_key ? t("settings_key_configured") : "sk-...";
  settingsDeepseekApiKey.value = "";
  settingsDeepseekApiKey.placeholder = settings.has_deepseek_api_key ? t("settings_key_configured") : "sk-...";
  settingsDefaultProvider.value = settings.default_provider || "handoff";
  settingsRoutingModel.value = settings.routing_model || "gpt-4.1-nano";
  settingsTaskModel.value = settings.task_model || "gpt-4.1-mini";
  settingsDeepseekModel.value = settings.deepseek_model || "deepseek-chat";
  settingsDeepseekBaseUrl.value = settings.deepseek_base_url || "https://api.deepseek.com/v1";
  settingsUiLanguage.value = settings.ui_language || "zh";
}

async function loadSettings() {
  try {
    const data = await getJson("/api/settings");
    settingsCache = data;
    setLanguage(data.ui_language || "zh");
    setMvpGuideText("mvp_guide_idle");
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
    task_model: settingsTaskModel.value.trim() || "gpt-4.1-mini",
    deepseek_model: settingsDeepseekModel.value.trim() || "deepseek-chat",
    deepseek_base_url: settingsDeepseekBaseUrl.value.trim() || "https://api.deepseek.com/v1",
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
    providerSelect.value = data.default_provider || providerSelect.value;
    if ((data.default_provider || "") === "deepseek") {
      modelInput.value = data.deepseek_model || modelInput.value;
    } else {
      modelInput.value = data.task_model || modelInput.value;
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

async function runMvpFlow() {
  if (!settingsCache) {
    await loadSettings();
  }
  const demoTask = "run weekly decision review and output top 3 owner actions with risk notes";
  taskInput.value = demoTask;

  if (settingsCache && settingsCache.has_deepseek_api_key && providerSelect.querySelector('option[value="deepseek"]')) {
    providerSelect.value = "deepseek";
    if (!modelInput.value.trim() || modelInput.value.includes("gpt-")) {
      modelInput.value = settingsCache.deepseek_model || "deepseek-chat";
    }
  } else if (settingsCache && settingsCache.has_openai_api_key && providerSelect.querySelector('option[value="openai"]')) {
    providerSelect.value = "openai";
    if (!modelInput.value.trim()) {
      modelInput.value = settingsCache.task_model || "gpt-4.1-mini";
    }
  }
  retrievalToggle.checked = false;
  moduleSelect.value = "";

  addUserTaskOnce(demoTask);
  setMvpGuideText("mvp_guide_inspecting");
  addBubble("system", t("msg_mvp_started"));
  addBubble("system", t("msg_mvp_mode", { provider: providerSelect.value || "handoff" }));
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

async function reviewSuggestion(verdict) {
  const sid = String(latestSuggestionId || "").trim();
  if (!sid) {
    addBubble("system", t("msg_no_suggestion_selected"));
    return;
  }
  const choice = String(verdict || "").trim().toLowerCase();
  if (!["accept", "modify", "reject"].includes(choice)) {
    return;
  }

  const ownerNote =
    window.prompt("Owner note (required):", "Reviewed with current judgment context.") || "";
  const note = ownerNote.trim();
  if (!note) {
    addBubble("system", "Review skipped: owner note is required.");
    return;
  }

  const payload = {
    action: "review_suggestion",
    suggestion_id: sid,
    verdict: choice,
    owner_note: note,
  };

  if (choice === "modify") {
    const replacement = window.prompt("Replacement judgment (required):", "") || "";
    if (!replacement.trim()) {
      addBubble("system", "Modify skipped: replacement judgment is required.");
      return;
    }
    const unlikeReason = window.prompt("Unlike-me reason (required):", "") || "";
    if (!unlikeReason.trim()) {
      addBubble("system", "Modify skipped: unlike-me reason is required.");
      return;
    }
    const targetLayer = window.prompt("Target layer (optional):", "decision") || "";
    payload.replacement_judgment = replacement.trim();
    payload.unlike_me_reason = unlikeReason.trim();
    if (targetLayer.trim()) {
      payload.correction_target_layer = targetLayer.trim();
    }
  }

  try {
    const data = await postJson("/api/action", payload);
    renderActionResult(data);
    if (data.suggestion_detail) {
      renderSuggestionDetail(data.suggestion_detail);
    } else {
      await loadSuggestionDetail(sid);
    }
    addBubble("system", `Suggestion reviewed: ${sid} -> ${choice}`);
  } catch (err) {
    addBubble("system", `Suggestion review failed: ${err.message}`);
  }
}

async function runAction(action) {
  const taskText = taskInput.value.trim();
  const learningText = learningDirectInput ? learningDirectInput.value.trim() : "";
  const payload = {
    action,
    provider: providerSelect.value,
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
      addBubble("system", "Learning text is required. Paste transcript/article/notes first.");
      return;
    }
    payload.task = learningText;
    payload.title = learningTitleInput.value.trim() || null;
    payload.source_type = learningSourceType.value || "video";
    payload.max_points = 6;
    payload.confidence = Number(learningConfidence.value || 7);
    payload.tags = ["ui_one_click"];
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

  addBubble("system", `Running action: ${payload.action}`);

  try {
    const data = await postJson("/api/action", payload);
    renderActionResult(data);
    addBubble("system", `Action complete: ${data.action}`);
  } catch (err) {
    addBubble("system", `Action failed: ${err.message}`);
  }
}

async function generateLearningHandoffPacket() {
  const sourceRef = learningSourceInput.value.trim();
  if (!sourceRef) {
    addBubble("system", "Source URL/reference is required for learning handoff packet.");
    return;
  }

  const payload = {
    action: "learning_handoff_packet",
    source_ref: sourceRef,
    title: learningTitleInput.value.trim() || null,
    source_type: learningSourceType.value || "video",
    max_candidates_per_type: 3,
  };

  addBubble("system", "Generating learning handoff packet...");
  try {
    const data = await postJson("/api/action", payload);
    renderActionResult(data);
    addBubble("system", "Learning handoff packet ready. Copy Output Preview and send to external model.");
  } catch (err) {
    addBubble("system", `Packet generation failed: ${err.message}`);
  }
}

async function importLearningHandoffResponse() {
  const responseText = learningResponseInput.value.trim();
  if (!responseText) {
    addBubble("system", "Paste external LLM JSON response first.");
    return;
  }

  const payload = {
    action: "learning_handoff_import",
    response_text: responseText,
    source_ref: learningSourceInput.value.trim() || null,
    title: learningTitleInput.value.trim() || null,
    source_type: learningSourceType.value || "video",
    confidence: Number(learningConfidence.value || 7),
    tags: ["ui_learning_handoff"],
  };

  addBubble("system", "Importing handoff response into memory + candidate queue...");
  try {
    const data = await postJson("/api/action", payload);
    renderActionResult(data);
    addBubble("system", `Imported learning handoff. Candidate queue +${data.candidate_total || 0}.`);
  } catch (err) {
    addBubble("system", `Handoff import failed: ${err.message}`);
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
  if (providerSelect.value === "deepseek") {
    const current = modelInput.value.trim();
    if (!current || current.startsWith("gpt-")) {
      modelInput.value = (settingsCache && settingsCache.deepseek_model) || "deepseek-chat";
    }
  } else if (providerSelect.value === "openai") {
    const current = modelInput.value.trim();
    if (!current || current.startsWith("deepseek-")) {
      modelInput.value = (settingsCache && settingsCache.task_model) || "gpt-4.1-mini";
    }
  }
  latestOutputProvider = providerSelect.value || latestOutputProvider;
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
quickIngestBtn.addEventListener("click", () => {
  runAction("ingest_learning");
});
learningPacketBtn.addEventListener("click", () => {
  generateLearningHandoffPacket();
});
learningImportBtn.addEventListener("click", () => {
  importLearningHandoffResponse();
});
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
setMvpGuideText("mvp_guide_idle");
setStatus(t("status_connecting"), "pending", "status_connecting");
initTheme();
switchEntrypoint("task");
setSuggestionReviewEnabled(false);
loadStatus();
loadSettings();
setOutputTokenMeta("-");
