const chatLog = document.getElementById("chatLog");
const taskForm = document.getElementById("taskForm");
const taskInput = document.getElementById("taskInput");
const moduleSelect = document.getElementById("moduleSelect");
const providerSelect = document.getElementById("providerSelect");
const modelInput = document.getElementById("modelInput");
const retrievalToggle = document.getElementById("retrievalToggle");
const retrievalTopK = document.getElementById("retrievalTopK");
const inspectBtn = document.getElementById("inspectBtn");
const runBtn = document.getElementById("runBtn");
const statusBadge = document.getElementById("statusBadge");
const themeToggle = document.getElementById("themeToggle");
const settingsToggle = document.getElementById("settingsToggle");
const copyOutputBtn = document.getElementById("copyOutputBtn");

const routeTrace = document.getElementById("routeTrace");
const planTrace = document.getElementById("planTrace");
const loadedFiles = document.getElementById("loadedFiles");
const resultTrace = document.getElementById("resultTrace");
const suggestionTrace = document.getElementById("suggestionTrace");
const outputPreview = document.getElementById("outputPreview");
const outputTokenMeta = document.getElementById("outputTokenMeta");
const technicalDetails = document.getElementById("technicalDetails");

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

let latestOutputPath = null;
let latestSuggestionId = null;
let settingsCache = null;
let uiLanguage = "zh";

const I18N = {
  zh: {
    doc_title: "Personal Core OS | 工作台",
    app_title: "Personal Core OS",
    app_subtitle: "简化工作台",
    nav_workspace: "工作台",
    nav_audit: "审计中心",
    status_connecting: "连接中...",
    status_connected: "已连接",
    status_offline: "离线",
    hero_title: "你想让我帮你做什么？",
    hero_desc: "输入目标，点击执行。复杂诊断和治理能力在审计中心。",
    label_task: "任务",
    task_placeholder: "例如：帮我生成本周决策复盘",
    btn_run: "开始执行",
    btn_inspect: "预览处理方式",
    btn_go_audit: "打开审计中心",
    advanced_summary: "高级选项（可选）",
    label_module: "模块",
    option_auto_route: "自动路由",
    label_provider: "Provider",
    option_provider_auto: "自动（按设置）",
    label_model: "模型",
    model_placeholder: "gpt-4.1-mini / deepseek-chat",
    label_use_retrieval: "启用检索",
    label_top_k: "Top K",
    task_starters: "快捷开始",
    starter_weekly_review: "每周决策复盘",
    starter_extract_patterns: "提取本周聊天模式",
    starter_write_story: "写一篇饭后BTC故事",
    trace_messages: "系统消息",
    result_title: "执行结果",
    technical_summary: "技术详情（路由/计划/文件）",
    trace_route: "路由",
    trace_plan: "计划",
    trace_loaded_files: "已加载文件",
    trace_result: "结果元信息",
    trace_suggestion_detail: "系统建议",
    settings_title: "设置",
    settings_section_openai: "OpenAI",
    settings_section_deepseek: "DeepSeek",
    settings_section_routing: "路由与默认",
    settings_section_profiles: "任务类型模型覆盖（可选）",
    settings_section_ui: "界面",
    settings_openai_key: "OpenAI API Key",
    settings_openai_base_url: "OpenAI Base URL",
    settings_openai_model: "OpenAI 默认模型",
    settings_deepseek_key: "DeepSeek API Key",
    settings_default_provider: "全局回退 Provider",
    settings_routing_model: "路由模型（轻）",
    settings_deepseek_model: "DeepSeek 默认模型",
    settings_deepseek_base_url: "DeepSeek Base URL",
    settings_profiles_note: "Provider/Model 留空则使用全局默认；在模块路由后生效。",
    settings_decision_provider: "Decision Provider",
    settings_decision_model: "Decision 模型",
    settings_content_provider: "Content Provider",
    settings_content_model: "Content 模型",
    settings_cognition_provider: "Cognition Provider",
    settings_cognition_model: "Cognition 模型",
    settings_ui_language: "界面语言",
    option_use_fallback: "使用全局默认",
    btn_save: "保存",
    settings_key_configured: "已配置（本地存储）",
    msg_settings_saved: "设置已保存。",
    msg_connection_failed: "连接失败：{error}",
    msg_task_required_inspect: "请先输入任务。",
    msg_task_required_run: "请先输入任务。",
    msg_inspect_complete: "预览完成：模块 {module}，技能 {skill}",
    msg_inspect_failed: "预览失败：{error}",
    msg_run_complete: "执行完成：输出文件 {output}",
    msg_run_failed: "执行失败：{error}",
    msg_copy_failed: "复制失败：{error}",
    msg_no_output_yet: "暂无可复制输出，请先执行任务。",
    msg_no_suggestion: "本次执行没有生成系统建议。",
    msg_token_exact: "Tokens：{tokens}（精确）",
    msg_token_estimate: "Tokens：{tokens}（估算）",
    msg_token_unavailable: "Tokens：不可用",
  },
  en: {
    doc_title: "Personal Core OS | Workspace",
    app_title: "Personal Core OS",
    app_subtitle: "Simple Workspace",
    nav_workspace: "Workspace",
    nav_audit: "Audit Center",
    status_connecting: "Connecting...",
    status_connected: "Connected",
    status_offline: "Offline",
    hero_title: "What do you want me to do?",
    hero_desc: "Describe your goal and run it. Advanced diagnostics and governance live in Audit Center.",
    label_task: "Task",
    task_placeholder: "Example: generate this week's decision review",
    btn_run: "Run",
    btn_inspect: "Preview Plan",
    btn_go_audit: "Open Audit Center",
    advanced_summary: "Advanced Options (Optional)",
    label_module: "Module",
    option_auto_route: "Auto route",
    label_provider: "Provider",
    option_provider_auto: "auto (from settings)",
    label_model: "Model",
    model_placeholder: "gpt-4.1-mini / deepseek-chat",
    label_use_retrieval: "Use retrieval",
    label_top_k: "Top K",
    task_starters: "Quick Starters",
    starter_weekly_review: "Weekly Decision Review",
    starter_extract_patterns: "Extract Weekly Chat Patterns",
    starter_write_story: "Write After-Meal BTC Story",
    trace_messages: "System Messages",
    result_title: "Result",
    technical_summary: "Technical Details (Route/Plan/Files)",
    trace_route: "Route",
    trace_plan: "Plan",
    trace_loaded_files: "Loaded Files",
    trace_result: "Result Metadata",
    trace_suggestion_detail: "System Suggestion",
    settings_title: "Settings",
    settings_section_openai: "OpenAI",
    settings_section_deepseek: "DeepSeek",
    settings_section_routing: "Routing & Defaults",
    settings_section_profiles: "Task Profile Overrides (Optional)",
    settings_section_ui: "Interface",
    settings_openai_key: "OpenAI API Key",
    settings_openai_base_url: "OpenAI Base URL",
    settings_openai_model: "OpenAI Default Model",
    settings_deepseek_key: "DeepSeek API Key",
    settings_default_provider: "Fallback Provider",
    settings_routing_model: "Routing Model (lighter)",
    settings_deepseek_model: "DeepSeek Default Model",
    settings_deepseek_base_url: "DeepSeek Base URL",
    settings_profiles_note: "Leave provider/model empty to use fallback defaults. Applies after module routing.",
    settings_decision_provider: "Decision Provider",
    settings_decision_model: "Decision Model",
    settings_content_provider: "Content Provider",
    settings_content_model: "Content Model",
    settings_cognition_provider: "Cognition Provider",
    settings_cognition_model: "Cognition Model",
    settings_ui_language: "UI Language",
    option_use_fallback: "Use fallback",
    btn_save: "Save",
    settings_key_configured: "Configured (stored locally)",
    msg_settings_saved: "Settings saved.",
    msg_connection_failed: "Connection failed: {error}",
    msg_task_required_inspect: "Please enter a task first.",
    msg_task_required_run: "Please enter a task first.",
    msg_inspect_complete: "Preview ready: module {module}, skill {skill}",
    msg_inspect_failed: "Preview failed: {error}",
    msg_run_complete: "Run complete: output file {output}",
    msg_run_failed: "Run failed: {error}",
    msg_copy_failed: "Copy failed: {error}",
    msg_no_output_yet: "No output yet. Run a task first.",
    msg_no_suggestion: "No system suggestion was produced for this run.",
    msg_token_exact: "Tokens: {tokens} (exact)",
    msg_token_estimate: "Tokens: {tokens} (estimate)",
    msg_token_unavailable: "Tokens: unavailable",
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

function setLanguage(lang) {
  uiLanguage = lang === "en" ? "en" : "zh";
  applyI18n();
  const autoOption = moduleSelect.querySelector('option[value=""]');
  if (autoOption) {
    autoOption.textContent = t("option_auto_route");
  }
  const fallbackOptions = document.querySelectorAll('option[data-i18n="option_use_fallback"]');
  for (const option of fallbackOptions) {
    option.textContent = t("option_use_fallback");
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
  planTrace.textContent = planLines.join("\n");

  renderLoadedFiles(data.loaded_files || []);
  latestSuggestionId = null;
  suggestionTrace.textContent = "-";
  if (!data.output_preview) {
    setPreview("-");
    setOutputTokenMeta("-");
  }
}

function renderSuggestionDetail(data) {
  if (!data || typeof data !== "object" || !data.suggestion || typeof data.suggestion !== "object") {
    suggestionTrace.textContent = "-";
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
}

async function loadSuggestionDetail(suggestionId) {
  const sid = String(suggestionId || "").trim();
  if (!sid) {
    suggestionTrace.textContent = "-";
    addBubble("system", t("msg_no_suggestion"));
    return;
  }
  try {
    const data = await getJson(`/api/suggestion?id=${encodeURIComponent(sid)}`);
    renderSuggestionDetail(data);
  } catch (err) {
    suggestionTrace.textContent = `load_failed: ${err.message}`;
  }
}

function renderRunResult(data) {
  renderInspectResult(data);
  latestOutputPath = data.output_path || null;
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
    const key = data.count_method === "tiktoken" ? "msg_token_exact" : "msg_token_estimate";
    setOutputTokenMeta(t(key, { tokens: data.prompt_tokens }));
  } catch {
    setOutputTokenMeta(t("msg_token_unavailable"));
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
    technicalDetails.open = true;
    addBubble("system", t("msg_inspect_complete", { module: data.module, skill: data.plan.skill }));
  } catch (err) {
    addBubble("system", t("msg_inspect_failed", { error: err.message }));
  }
}

async function runTask() {
  const payload = buildPayload();
  if (!payload.task) {
    addBubble("system", t("msg_task_required_run"));
    return;
  }

  addUserTaskOnce(payload.task);

  runBtn.disabled = true;
  inspectBtn.disabled = true;
  try {
    const data = await postJson("/api/run", payload);
    renderRunResult(data);
    addBubble("system", t("msg_run_complete", { output: data.output_path }));
  } catch (err) {
    addBubble("system", t("msg_run_failed", { error: err.message }));
  } finally {
    runBtn.disabled = false;
    inspectBtn.disabled = false;
  }
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

for (const button of document.querySelectorAll(".chip[data-task]")) {
  button.addEventListener("click", () => {
    taskInput.value = button.getAttribute("data-task") || "";
    taskInput.focus();
  });
}

inspectBtn.addEventListener("click", (event) => {
  event.preventDefault();
  inspectTask();
});

taskForm.addEventListener("submit", (event) => {
  event.preventDefault();
  runTask();
});

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
      modelInput.value = (settingsCache && (settingsCache.openai_model || settingsCache.task_model)) || "gpt-4.1-mini";
    }
  }
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

setLanguage("zh");
setStatus(t("status_connecting"), "pending", "status_connecting");
setOutputTokenMeta("-");
initTheme();
loadSettings();
loadStatus();
