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

const routeTrace = document.getElementById("routeTrace");
const planTrace = document.getElementById("planTrace");
const loadedFiles = document.getElementById("loadedFiles");
const resultTrace = document.getElementById("resultTrace");
const outputPreview = document.getElementById("outputPreview");
const outputTokenMeta = document.getElementById("outputTokenMeta");
const settingsModal = document.getElementById("settingsModal");
const settingsClose = document.getElementById("settingsClose");
const settingsSave = document.getElementById("settingsSave");
const settingsApiKey = document.getElementById("settingsApiKey");
const settingsDefaultProvider = document.getElementById("settingsDefaultProvider");
const settingsRoutingModel = document.getElementById("settingsRoutingModel");
const settingsTaskModel = document.getElementById("settingsTaskModel");
let latestOutputPath = null;
let latestOutputProvider = null;
let settingsCache = null;

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

function setStatus(label, kind) {
  statusBadge.textContent = label;
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

  planTrace.textContent = [
    `skill: ${data.plan.skill}`,
    `output_path: ${data.plan.output_path}`,
    `retrieval_hits: ${data.retrieval_hits}`,
  ].join("\n");

  renderLoadedFiles(data.loaded_files || []);
  if (!data.output_preview) {
    setPreview("-");
    setOutputTokenMeta("-");
  }
}

function renderRunResult(data) {
  renderInspectResult(data);
  latestOutputPath = data.output_path || null;
  latestOutputProvider = data.provider || providerSelect.value || null;
  resultTrace.textContent = [
    `output_path: ${data.output_path}`,
    `output_hash: ${data.output_hash}`,
    `module: ${data.module}`,
  ].join("\n");
  setPreview(data.output_preview || "-");
  refreshOutputTokenMeta();
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
    addBubble("system", "No output yet. Run a task first.");
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
    addBubble("system", `Copy failed: ${err.message}`);
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

    moduleSelect.innerHTML = "<option value=\"\">Auto route</option>";
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

    setStatus("Connected", "ok");
    addBubble("system", `Connected to ${data.repo_root}`);
  } catch (err) {
    setStatus("Offline", "fail");
    addBubble("system", `Connection failed: ${err.message}`);
  }
}

function applySettingsToForm(settings) {
  settingsApiKey.value = "";
  settingsApiKey.placeholder = settings.has_openai_api_key ? "Configured (stored locally)" : "sk-...";
  settingsDefaultProvider.value = settings.default_provider || "handoff";
  settingsRoutingModel.value = settings.routing_model || "gpt-4.1-nano";
  settingsTaskModel.value = settings.task_model || "gpt-4.1-mini";
}

async function loadSettings() {
  try {
    const data = await getJson("/api/settings");
    settingsCache = data;
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
  const payload = {
    default_provider: settingsDefaultProvider.value,
    routing_model: settingsRoutingModel.value.trim() || "gpt-4.1-nano",
    task_model: settingsTaskModel.value.trim() || "gpt-4.1-mini",
  };
  if (apiKey) {
    payload.openai_api_key = apiKey;
  }

  try {
    const data = await postJson("/api/settings", payload);
    settingsCache = data;
    providerSelect.value = data.default_provider || providerSelect.value;
    modelInput.value = data.task_model || modelInput.value;
    settingsApiKey.value = "";
    closeSettingsModal();
    addBubble("system", "Settings saved.");
  } catch (err) {
    addBubble("system", `Settings save failed: ${err.message}`);
  }
}

async function inspectTask() {
  const payload = buildPayload();
  if (!payload.task) {
    addBubble("system", "Task is required for inspect.");
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
    addBubble("system", "Task is required for run.");
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

async function runAction(action) {
  const taskText = taskInput.value.trim();
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

  if (action === "ingest_learning") {
    if (!taskText) {
      addBubble("system", "Task text is required. Paste your learning summary first.");
      return;
    }
    payload.task = taskText;
    payload.source_type = "video";
    payload.max_points = 6;
    payload.confidence = 7;
    payload.tags = ["ui_one_click"];
    addUserTaskOnce(taskText);
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

inspectBtn.addEventListener("click", (event) => {
  event.preventDefault();
  inspectTask();
});

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

addBubble("system", "Type a task, click Inspect, then Run.");

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

initTheme();
loadStatus();
loadSettings();
setOutputTokenMeta("-");
