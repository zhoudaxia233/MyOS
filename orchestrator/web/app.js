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
const settingsModal = document.getElementById("settingsModal");
const settingsClose = document.getElementById("settingsClose");
const settingsSave = document.getElementById("settingsSave");
const settingsApiKey = document.getElementById("settingsApiKey");
const settingsDefaultProvider = document.getElementById("settingsDefaultProvider");
const settingsRoutingModel = document.getElementById("settingsRoutingModel");
const settingsTaskModel = document.getElementById("settingsTaskModel");
let latestOutputPath = null;
let latestOutputProvider = null;
let latestSuggestionId = null;
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

function renderCognitionCards(cards) {
  cognitionCards.innerHTML = "";
  if (!Array.isArray(cards) || cards.length === 0) {
    const empty = document.createElement("div");
    empty.className = "metric-card status-warn";
    empty.innerHTML = "<div class=\"metric-title\">No cognition metrics</div><div class=\"metric-value\">-</div><div class=\"metric-meta\">Run metrics first.</div>";
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
    empty.innerHTML = "<div class=\"todo-head\"><span class=\"todo-metric\">No open todos</span></div><div class=\"todo-action\">No unresolved escalation items.</div>";
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
    btn.textContent = "Resolve";
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
    empty.innerHTML = "<div class=\"todo-head\"><span class=\"todo-metric\">No pending candidates</span></div><div class=\"todo-action\">Use Learning Handoff import to populate queue.</div>";
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
    acceptBtn.textContent = "Accept";
    acceptBtn.addEventListener("click", () => {
      reviewLearningCandidate(item.id, "accept");
    });

    const rejectBtn = document.createElement("button");
    rejectBtn.className = "todo-resolve-btn";
    rejectBtn.type = "button";
    rejectBtn.textContent = "Reject";
    rejectBtn.addEventListener("click", () => {
      reviewLearningCandidate(item.id, "reject");
    });

    const modifyBtn = document.createElement("button");
    modifyBtn.className = "todo-resolve-btn";
    modifyBtn.type = "button";
    modifyBtn.textContent = "Modify";
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
    entrypointHint.textContent = "Ingest material directly or run low-cost external handoff, then review candidates.";
    return;
  }
  if (target === "audit") {
    entrypointHint.textContent = "Review drift, reports, and candidate queues before promoting long-term changes.";
    return;
  }
  entrypointHint.textContent = "Ask the system to do work, inspect route/plan first, then run.";
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
    renderCognitionCards(data.cognition_cards || []);
    renderOwnerTodos(data.owner_todos || []);
    renderLearningCandidates(data.learning_candidates || []);
    renderCandidatePipelineSummary(data.candidate_pipeline_summary || {}, data.candidate_pipeline_trend || null);
    renderSuggestionReviewSummary(data.suggestion_review_summary || {}, data.suggestion_review_trend || null);

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

async function runMvpFlow() {
  const demoTask = "run weekly decision review and output top 3 owner actions with risk notes";
  taskInput.value = demoTask;

  if (providerSelect.querySelector('option[value="dry-run"]')) {
    providerSelect.value = "dry-run";
  }
  retrievalToggle.checked = false;
  moduleSelect.value = "";

  addUserTaskOnce(demoTask);
  addBubble("system", "MVP flow started: Inspect -> Run -> Suggestion detail.");

  try {
    const payload = buildPayload();
    const inspectData = await postJson("/api/inspect", payload);
    renderInspectResult(inspectData);
    addBubble("system", `MVP inspect ready: ${inspectData.module} -> ${inspectData.plan.skill}`);

    const runData = await postJson("/api/run", payload);
    renderRunResult(runData);
    if (runData.suggestion_id) {
      await loadSuggestionDetail(runData.suggestion_id);
    }

    switchEntrypoint("audit");
    addBubble("system", "MVP flow complete. Review Suggestion Detail and click Accept/Modify/Reject.");
  } catch (err) {
    addBubble("system", `MVP flow failed: ${err.message}`);
  }
}

async function reviewSuggestion(verdict) {
  const sid = String(latestSuggestionId || "").trim();
  if (!sid) {
    addBubble("system", "No suggestion selected. Run a task first.");
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

initTheme();
switchEntrypoint("task");
loadStatus();
loadSettings();
setOutputTokenMeta("-");
