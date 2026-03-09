const chatLog = document.getElementById("chatLog");
const taskForm = document.getElementById("taskForm");
const taskInput = document.getElementById("taskInput");
const moduleSelect = document.getElementById("moduleSelect");
const providerSelect = document.getElementById("providerSelect");
const modelInput = document.getElementById("modelInput");
const retrievalToggle = document.getElementById("retrievalToggle");
const retrievalTopK = document.getElementById("retrievalTopK");
const providerHelp = document.getElementById("providerHelp");
const retrievalHelp = document.getElementById("retrievalHelp");
const inspectBtn = document.getElementById("inspectBtn");
const runBtn = document.getElementById("runBtn");
const statusBadge = document.getElementById("statusBadge");
const themeToggle = document.getElementById("themeToggle");
const settingsToggle = document.getElementById("settingsToggle");
const copyOutputBtn = document.getElementById("copyOutputBtn");

const quickIngestBtn = document.getElementById("quickIngestBtn");
const learningPacketBtn = document.getElementById("learningPacketBtn");
const learningImportBtn = document.getElementById("learningImportBtn");
const learningDirectInput = document.getElementById("learningDirectInput");
const learningTitleInput = document.getElementById("learningTitleInput");
const learningCertainty = document.getElementById("learningCertainty");
const learningSourceInput = document.getElementById("learningSourceInput");
const learningResponseInput = document.getElementById("learningResponseInput");

const routeTrace = document.getElementById("routeTrace");
const planTrace = document.getElementById("planTrace");
const loadedFiles = document.getElementById("loadedFiles");
const resultTrace = document.getElementById("resultTrace");
const suggestionTrace = document.getElementById("suggestionTrace");
const outputPreview = document.getElementById("outputPreview");
const outputTokenMeta = document.getElementById("outputTokenMeta");
const technicalDetails = document.getElementById("technicalDetails");
const outputDetails = document.getElementById("outputDetails");
const outputPathText = document.getElementById("outputPathText");
const resultSummary = document.getElementById("resultSummary");
const modeGuide = document.getElementById("modeGuide");
const nextStepsList = document.getElementById("nextStepsList");
const quickSettingsBtn = document.getElementById("quickSettingsBtn");
const quickCopyBtn = document.getElementById("quickCopyBtn");
const quickFollowupBtn = document.getElementById("quickFollowupBtn");
const workspaceTabs = document.querySelectorAll(".workspace-tab");
const workspaceTaskPanel = document.getElementById("workspaceTaskPanel");
const workspaceLearningPanel = document.getElementById("workspaceLearningPanel");

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
let latestRunProvider = null;
let settingsCache = null;
let statusCache = null;
let uiLanguage = "zh";
let latestGuidanceMode = "pre_run_no_api";
let isRunningTask = false;
let activeWorkspaceTab = "task";

const LEARNING_SOURCE_DEFAULT = "notes";

const I18N = {
  zh: {
    doc_title: "Personal Core OS | 工作台",
    app_title: "Personal Core OS",
    app_subtitle: "工作台（任务 + 学习）",
    nav_workspace: "工作台",
    nav_audit: "审计中心",
    status_connecting: "连接中...",
    status_connected: "已连接",
    status_offline: "离线",
    hero_title: "你想让我帮你做什么？",
    hero_desc: "你说目标，我给结果、关键结论和下一步动作。任务输入和学习更新都在这里。",
    quick_use_title: "30 秒上手",
    quick_use_step_1: "输入你希望得到的结果（例如“给我下周3件最重要的事”）。",
    quick_use_step_2: "点击“开始执行”。",
    quick_use_step_3: "先看右侧“执行结果”摘要，再决定是否看完整 Markdown。",
    quick_use_step_4: "如果你有新经验/资料，切到上方“学习更新”标签补充到系统里。",
    workspace_tab_task: "任务执行",
    workspace_tab_learning: "学习更新",
    section_task: "任务输入",
    task_intro: "在这里输入你要的结果，执行后在右侧查看结果。",
    section_learning: "学习更新",
    label_task: "任务",
    task_placeholder: "例如：总结我本周做了什么、哪里做得好/不好、下周3件重点事",
    btn_run: "开始执行",
    btn_inspect: "查看处理步骤",
    btn_go_audit: "打开审计中心",
    advanced_summary: "执行方式与高级控制（可选）",
    label_module: "任务类型（可选）",
    option_auto_route: "自动路由",
    module_help: "不确定就保持“自动路由”。",
    label_provider: "执行方式",
    option_provider_auto: "系统自动（推荐）",
    label_model: "模型（高级）",
    model_placeholder: "gpt-4.1-mini / deepseek-chat",
    model_help: "一般保持空，让系统自动匹配。",
    label_use_retrieval: "参考历史记录",
    label_top_k: "参考条数",
    top_k_help: "每次最多带入多少条历史记录。越大越全，但更慢；默认 6。",
    provider_help_auto: "推荐：系统自动按你的设置选择执行方式。",
    provider_help_dry_run: "离线演练：不调用外部 API，主要用于测试流程。",
    provider_help_handoff: "外部协作：生成请求包，你复制到外部模型执行。",
    provider_help_openai: "OpenAI 直连：由系统直接生成结果。",
    provider_help_deepseek: "DeepSeek 直连：由系统直接生成结果。",
    retrieval_help_off: "当前未开启历史参考：仅基于你这次输入生成结果。",
    retrieval_help_on: "已开启历史参考：会结合过去记录辅助生成。",
    option_provider_dry_run: "离线演练（dry-run）",
    option_provider_handoff: "外部协作（handoff）",
    option_provider_openai: "OpenAI（直连）",
    option_provider_deepseek: "DeepSeek（直连）",
    task_starters: "示例任务",
    starter_hint: "点击任一项会自动执行并生成结果。",
    review_definition: "复盘 = 回顾本周关键决策、结果原因、改进动作，并给下周执行清单。",
    starter_weekly_review: "本周总结+下周3件事",
    starter_extract_patterns: "目标拆解行动清单",
    starter_write_story: "风险检查+应对动作",
    learning_intro: "把你新的经验、资料、文章要点放进系统，帮助后续任务更贴合你。",
    learning_direct_title: "直接学习输入",
    label_learning_text: "学习文本",
    learning_text_placeholder: "粘贴你的复盘、文章摘要、会议纪要...",
    label_title_optional: "标题（可选）",
    title_placeholder: "这段内容叫什么",
    label_learning_certainty: "把握程度",
    certainty_auto: "自动（系统判断）",
    certainty_low: "低（先记为待验证）",
    certainty_medium: "中（大体可靠）",
    certainty_high: "高（高度确定）",
    btn_ingest_memory: "保存到学习记录",
    learning_handoff_title: "外部模型辅助学习",
    learning_handoff_help: "适合没有 API 时：先生成“学习请求包”给外部模型，再把 JSON 回复粘贴回来。",
    label_source_url: "来源链接 / 引用",
    source_url_placeholder: "YouTube / 播客 / 文章链接",
    btn_generate_packet: "生成学习请求包",
    label_external_response: "外部模型 JSON 回复",
    external_response_placeholder: "把外部模型 JSON 粘贴到这里",
    btn_parse_queue: "导入学习候选",
    trace_messages: "系统消息",
    result_title: "执行结果",
    result_summary_empty: "执行后，这里会先给你可读摘要。",
    result_file_label: "结果文件",
    next_steps_title: "下一步怎么做",
    next_steps_idle: "先执行一次任务，系统会告诉你下一步。",
    btn_open_settings: "去配置 API",
    btn_copy_report: "复制完整报告",
    btn_prepare_followup: "生成回填任务模板",
    output_details_summary: "完整报告（Markdown）",
    technical_summary: "技术详情（路由/计划/文件）",
    trace_route: "路由",
    trace_plan: "计划",
    trace_loaded_files: "已加载文件",
    trace_result: "结果元信息",
    trace_suggestion_detail: "系统建议",
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
    settings_routing_model: "自动分配模型（高级）",
    settings_deepseek_model: "DeepSeek 默认模型",
    settings_deepseek_base_url: "DeepSeek Base URL",
    settings_profiles_note: "大多数用户不需要改这里。留空即可沿用默认执行方式。",
    settings_decision_provider: "决策类任务执行方式",
    settings_decision_model: "决策类任务模型",
    settings_content_provider: "内容类任务执行方式",
    settings_content_model: "内容类任务模型",
    settings_cognition_provider: "学习类任务执行方式",
    settings_cognition_model: "学习类任务模型",
    settings_ui_language: "界面语言",
    option_use_fallback: "使用全局默认",
    option_mode_dry_run: "离线演练（不调用 API）",
    option_mode_handoff: "外部协作（复制请求包）",
    option_mode_openai: "OpenAI（直连）",
    option_mode_deepseek: "DeepSeek（直连）",
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
    msg_report_copied: "完整报告已复制。",
    msg_followup_prepared: "回填任务模板已放入任务框。请粘贴外部模型结果后执行。",
    msg_followup_truncated: "外部结果太长，已自动截断到可编辑范围。",
    followup_template_intro:
      "请基于下面的外部模型输出，整理成最终版复盘。要求：1) 先给3条优先行动；2) 给每条行动的风险提示；3) 最后给本周执行清单。",
    msg_no_output_yet: "暂无可复制输出，请先执行任务。",
    msg_no_suggestion: "本次执行没有生成系统建议。",
    msg_token_exact: "Tokens：{tokens}（精确）",
    msg_token_estimate: "Tokens：{tokens}（估算）",
    msg_token_unavailable: "Tokens：不可用",
    mode_with_api: "已检测到 API 配置，直接点击“开始执行”即可得到结果。",
    mode_no_api: "你还没有配置 API Key。当前会走离线模式，输出可能是请求包或草稿。",
    mode_no_api_steps: "建议步骤：1) 打开设置填写 API Key；或 2) 使用 handoff，把“完整报告（Markdown）”复制到外部模型，再将返回内容贴回这里继续处理。",
    next_pre_run_api_1: "输入任务后点击“开始执行”。",
    next_pre_run_api_2: "先看“执行结果”摘要，再决定是否展开完整 Markdown。",
    next_pre_run_no_api_1: "先去“设置”配置 API，可直接得到最终结果。",
    next_pre_run_no_api_2: "若暂不配 API：使用 handoff，把完整报告发到外部模型。",
    next_handoff_1: "点击“复制完整报告”，把请求包发给外部模型。",
    next_handoff_2: "拿到外部模型结果后，点击“生成回填任务模板”。",
    next_handoff_3: "把外部结果粘贴到模板中，再点“开始执行”。",
    next_dry_run_1: "当前是演练结果，仅用于流程验证。",
    next_dry_run_2: "建议先配置 API，再重跑得到可用复盘。",
    next_final_1: "先阅读摘要中的关键结论和行动点。",
    next_final_2: "需要细节时展开完整 Markdown。",
    next_final_3: "可复制完整报告用于归档或分享。",
    next_learning_packet_1: "复制完整报告中的学习请求包。",
    next_learning_packet_2: "发送到外部模型执行。",
    next_learning_packet_3: "把 JSON 结果粘贴到“外部模型 JSON 回复”，点击“导入学习候选”。",
    next_learning_import_1: "学习候选已入队，可继续在审计中心做治理。",
    next_learning_import_2: "后续任务会逐步利用这些学习内容。",
    next_learning_saved_1: "学习记录已保存，后续任务会参考这些内容。",
    next_learning_saved_2: "如需结构化提炼，可使用“外部模型辅助学习”。",
    summary_run_generic: "结果已生成。你可以先看下方摘要，再按需展开完整 Markdown。",
    summary_handoff: "当前是 handoff 模式：这是一份“给外部模型的请求包”，不是最终复盘。请复制完整报告到外部模型执行。",
    summary_dry_run: "当前是 dry-run 演练模式：输出是系统草稿，不是最终高质量结果。建议配置 API 后再执行。",
    summary_review_title: "本周复盘已生成（包含：发生了什么 / 为什么 / 下一步）：",
    summary_structure_title: "这份结果包含：",
    summary_actions_title: "建议你先看这几条可执行点：",
    summary_no_bullets: "完整报告已经生成，请展开“完整报告（Markdown）”查看详细内容。",
    msg_learning_text_required: "请先粘贴学习文本。",
    msg_learning_source_required: "请先填写来源链接 / 引用。",
    msg_learning_response_required: "请先粘贴外部模型 JSON 回复。",
    msg_learning_packet_generating: "正在生成学习请求包...",
    msg_learning_packet_ready: "学习请求包已生成。请复制“完整报告（Markdown）”里的内容发给外部模型。",
    msg_learning_packet_failed: "学习请求包生成失败：{error}",
    msg_learning_importing: "正在导入外部学习结果...",
    msg_learning_import_done: "学习候选已导入：+{count}",
    msg_learning_import_failed: "学习候选导入失败：{error}",
    msg_learning_confidence_auto: "把握程度自动判断：{confidence}/10",
    msg_learning_confidence_manual: "把握程度：{level}（{confidence}/10）",
    msg_learning_ingest_done: "学习记录已保存：新增 event={events}，insight={insights}",
    msg_learning_ingest_failed: "学习保存失败：{error}",
  },
  en: {
    doc_title: "Personal Core OS | Workspace",
    app_title: "Personal Core OS",
    app_subtitle: "Workspace (Task + Learning)",
    nav_workspace: "Workspace",
    nav_audit: "Audit Center",
    status_connecting: "Connecting...",
    status_connected: "Connected",
    status_offline: "Offline",
    hero_title: "What do you want me to do?",
    hero_desc: "Tell me the goal. I return outcomes, key conclusions, and next actions.",
    quick_use_title: "30-Second Guide",
    quick_use_step_1: "Describe the outcome you want (for example: top 3 priorities for next week).",
    quick_use_step_2: "Click Run.",
    quick_use_step_3: "Read the result summary first, then open markdown only if needed.",
    quick_use_step_4: "If you have new notes or experience, switch to the Learning tab and add them.",
    workspace_tab_task: "Task",
    workspace_tab_learning: "Learning",
    section_task: "Task Input",
    task_intro: "Describe the output you want here. Results will appear on the right.",
    section_learning: "Learning",
    label_task: "Task",
    task_placeholder: "Example: summarize my week, what worked/failed, and top 3 priorities for next week",
    btn_run: "Run",
    btn_inspect: "View Processing Steps",
    btn_go_audit: "Open Audit Center",
    advanced_summary: "Execution Mode & Advanced Controls (Optional)",
    label_module: "Task Type (Optional)",
    option_auto_route: "Auto route",
    module_help: "If unsure, keep Auto route.",
    label_provider: "Execution Mode",
    option_provider_auto: "System Auto (Recommended)",
    label_model: "Model (Advanced)",
    model_placeholder: "gpt-4.1-mini / deepseek-chat",
    model_help: "Usually leave empty and let the system choose.",
    label_use_retrieval: "Use Historical Context",
    label_top_k: "Context Count",
    top_k_help: "Maximum historical records to include during retrieval. Higher means broader but slower. Default 6.",
    provider_help_auto: "Recommended: system chooses the best mode from your settings.",
    provider_help_dry_run: "Offline simulation: no external API call, useful for flow checks.",
    provider_help_handoff: "External handoff: generate a packet and run it in external model.",
    provider_help_openai: "OpenAI direct mode: system generates final output directly.",
    provider_help_deepseek: "DeepSeek direct mode: system generates final output directly.",
    retrieval_help_off: "Historical context is off: output is based only on current input.",
    retrieval_help_on: "Historical context is on: output also uses past records.",
    option_provider_dry_run: "Offline Dry Run",
    option_provider_handoff: "External Handoff",
    option_provider_openai: "OpenAI (Direct)",
    option_provider_deepseek: "DeepSeek (Direct)",
    task_starters: "Example Tasks",
    starter_hint: "Clicking any item runs it immediately and generates output.",
    review_definition: "Review means: what happened, why it happened, what to improve, and next-week checklist.",
    starter_weekly_review: "Weekly Summary + Top 3 Next Actions",
    starter_extract_patterns: "Break Goals Into Action List",
    starter_write_story: "Risk Check + Response Actions",
    learning_intro: "Feed your new experiences and notes into the system so future tasks fit you better.",
    learning_direct_title: "Direct Learning Input",
    label_learning_text: "Learning Text",
    learning_text_placeholder: "Paste your review notes, summaries, or memo...",
    label_title_optional: "Title (optional)",
    title_placeholder: "Name this learning note",
    label_learning_certainty: "Certainty",
    certainty_auto: "Auto (system inferred)",
    certainty_low: "Low (needs verification)",
    certainty_medium: "Medium (mostly reliable)",
    certainty_high: "High (high confidence)",
    btn_ingest_memory: "Save Learning Note",
    learning_handoff_title: "External Model Assisted Learning",
    learning_handoff_help: "Good when API is unavailable: generate a packet, run it in external model, then paste JSON back.",
    label_source_url: "Source URL / Reference",
    source_url_placeholder: "YouTube / podcast / article URL",
    btn_generate_packet: "Generate Learning Packet",
    label_external_response: "External Model JSON Response",
    external_response_placeholder: "Paste external model JSON here",
    btn_parse_queue: "Import Learning Candidates",
    trace_messages: "System Messages",
    result_title: "Result",
    result_summary_empty: "After running, this area will show a readable summary first.",
    result_file_label: "Result File",
    next_steps_title: "What To Do Next",
    next_steps_idle: "Run a task once and the system will show the next steps.",
    btn_open_settings: "Configure API",
    btn_copy_report: "Copy Full Report",
    btn_prepare_followup: "Prepare Follow-up Template",
    output_details_summary: "Full Report (Markdown)",
    technical_summary: "Technical Details (Route/Plan/Files)",
    trace_route: "Route",
    trace_plan: "Plan",
    trace_loaded_files: "Loaded Files",
    trace_result: "Result Metadata",
    trace_suggestion_detail: "System Suggestion",
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
    settings_routing_model: "Auto-Routing Model (Advanced)",
    settings_deepseek_model: "DeepSeek Default Model",
    settings_deepseek_base_url: "DeepSeek Base URL",
    settings_profiles_note: "Most users do not need this. Leave empty to use default execution mode.",
    settings_decision_provider: "Decision Task Mode",
    settings_decision_model: "Decision Task Model",
    settings_content_provider: "Content Task Mode",
    settings_content_model: "Content Task Model",
    settings_cognition_provider: "Learning Task Mode",
    settings_cognition_model: "Learning Task Model",
    settings_ui_language: "UI Language",
    option_use_fallback: "Use fallback",
    option_mode_dry_run: "Offline Dry Run (No API)",
    option_mode_handoff: "External Handoff (Copy Packet)",
    option_mode_openai: "OpenAI (Direct)",
    option_mode_deepseek: "DeepSeek (Direct)",
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
    msg_report_copied: "Full report copied.",
    msg_followup_prepared: "Follow-up template is ready in the task box. Paste external result and run.",
    msg_followup_truncated: "External content was too long and has been truncated for editing.",
    followup_template_intro:
      "Based on the external model output below, produce a final review: 1) top 3 prioritized actions, 2) risk note for each action, 3) this-week execution checklist.",
    msg_no_output_yet: "No output yet. Run a task first.",
    msg_no_suggestion: "No system suggestion was produced for this run.",
    msg_token_exact: "Tokens: {tokens} (exact)",
    msg_token_estimate: "Tokens: {tokens} (estimate)",
    msg_token_unavailable: "Tokens: unavailable",
    mode_with_api: "API key detected. Click Run to get direct outputs.",
    mode_no_api: "No API key configured. The system is in offline mode, so output may be a packet or draft.",
    mode_no_api_steps: "Recommended: 1) add API key in Settings; or 2) use handoff, copy Full Report to external model, then paste response back for further processing.",
    next_pre_run_api_1: "Enter your task and click Run.",
    next_pre_run_api_2: "Read the result summary first, then open markdown only if needed.",
    next_pre_run_no_api_1: "Configure API in Settings to get final direct outputs.",
    next_pre_run_no_api_2: "If not, use handoff and send Full Report to an external model.",
    next_handoff_1: "Click Copy Full Report and send the packet to an external model.",
    next_handoff_2: "After you get the external result, click Prepare Follow-up Template.",
    next_handoff_3: "Paste external result into the template and click Run.",
    next_dry_run_1: "This is a simulation draft for flow validation.",
    next_dry_run_2: "Configure API and rerun for production-grade review.",
    next_final_1: "Read the key conclusions and action points in the summary.",
    next_final_2: "Open markdown only when you need full detail.",
    next_final_3: "Copy full report for archive or sharing.",
    next_learning_packet_1: "Copy the learning packet from Full Report.",
    next_learning_packet_2: "Send it to an external model.",
    next_learning_packet_3: "Paste JSON back to External Model Response and import candidates.",
    next_learning_import_1: "Learning candidates are imported and ready for governance in Audit Center.",
    next_learning_import_2: "Future tasks will gradually use these learning inputs.",
    next_learning_saved_1: "Learning note is saved and will be used by future tasks.",
    next_learning_saved_2: "Use External Assisted Learning for structured extraction if needed.",
    summary_run_generic: "Output generated. Read the summary first, then expand the full markdown if needed.",
    summary_handoff: "Current mode is handoff: this is a request packet for external model, not the final review.",
    summary_dry_run: "Current mode is dry-run: this is a system draft, not final quality output. Configure API for direct generation.",
    summary_review_title: "Weekly review is ready (what / why / next):",
    summary_structure_title: "This output includes:",
    summary_actions_title: "Suggested actionable points:",
    summary_no_bullets: "Full report is generated. Expand Full Report (Markdown) for details.",
    msg_learning_text_required: "Learning text is required.",
    msg_learning_source_required: "Source URL/reference is required.",
    msg_learning_response_required: "Paste external model JSON response first.",
    msg_learning_packet_generating: "Generating learning packet...",
    msg_learning_packet_ready: "Learning packet is ready. Copy content from Full Report (Markdown) and send to external model.",
    msg_learning_packet_failed: "Learning packet generation failed: {error}",
    msg_learning_importing: "Importing external learning response...",
    msg_learning_import_done: "Learning candidates imported: +{count}",
    msg_learning_import_failed: "Learning import failed: {error}",
    msg_learning_confidence_auto: "Certainty auto-inferred: {confidence}/10",
    msg_learning_confidence_manual: "Certainty: {level} ({confidence}/10)",
    msg_learning_ingest_done: "Learning saved: new event={events}, insight={insights}",
    msg_learning_ingest_failed: "Learning save failed: {error}",
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

function switchWorkspaceTab(tab) {
  const target = tab === "learning" ? "learning" : "task";
  activeWorkspaceTab = target;
  for (const item of workspaceTabs) {
    const key = item.getAttribute("data-workspace-tab") || "task";
    const isActive = key === target;
    item.classList.toggle("active", isActive);
    item.setAttribute("aria-pressed", isActive ? "true" : "false");
  }
  if (workspaceTaskPanel) {
    workspaceTaskPanel.classList.toggle("active", target === "task");
  }
  if (workspaceLearningPanel) {
    workspaceLearningPanel.classList.toggle("active", target === "learning");
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
  updateProviderHelp();
  updateRetrievalHelp();
  setNextStepsByMode(latestGuidanceMode);
  renderModeGuide();
}

function setResultSummary(text) {
  resultSummary.removeAttribute("data-i18n");
  resultSummary.textContent = String(text || t("result_summary_empty"));
}

function setNextSteps(lines) {
  if (!nextStepsList) {
    return;
  }
  nextStepsList.innerHTML = "";
  const items = Array.isArray(lines) && lines.length > 0 ? lines : [t("next_steps_idle")];
  for (const line of items) {
    const li = document.createElement("li");
    li.textContent = line;
    nextStepsList.appendChild(li);
  }
}

function setNextStepsByMode(mode) {
  latestGuidanceMode = mode;
  const mapping = {
    pre_run_api: ["next_pre_run_api_1", "next_pre_run_api_2"],
    pre_run_no_api: ["next_pre_run_no_api_1", "next_pre_run_no_api_2"],
    handoff: ["next_handoff_1", "next_handoff_2", "next_handoff_3"],
    dry_run: ["next_dry_run_1", "next_dry_run_2"],
    final: ["next_final_1", "next_final_2", "next_final_3"],
    learning_packet: ["next_learning_packet_1", "next_learning_packet_2", "next_learning_packet_3"],
    learning_import: ["next_learning_import_1", "next_learning_import_2"],
    learning_saved: ["next_learning_saved_1", "next_learning_saved_2"],
    idle: ["next_steps_idle"],
  };
  const keys = mapping[mode] || mapping.idle;
  setNextSteps(keys.map((key) => t(key)));
}

function hasUserVisibleResult() {
  const preview = String(outputPreview.textContent || "").trim();
  return preview !== "-" || Boolean(latestOutputPath);
}

function updateProviderHelp() {
  if (!providerHelp) {
    return;
  }
  const value = String(providerSelect.value || "auto").toLowerCase();
  const map = {
    auto: "provider_help_auto",
    "dry-run": "provider_help_dry_run",
    handoff: "provider_help_handoff",
    openai: "provider_help_openai",
    deepseek: "provider_help_deepseek",
  };
  const key = map[value] || "provider_help_auto";
  providerHelp.setAttribute("data-i18n", key);
  providerHelp.textContent = t(key);
}

function updateRetrievalHelp() {
  if (!retrievalHelp) {
    return;
  }
  const key = retrievalToggle.checked ? "retrieval_help_on" : "retrieval_help_off";
  retrievalHelp.setAttribute("data-i18n", key);
  retrievalHelp.textContent = t(key);
}

function renderModeGuide() {
  if (!modeGuide) {
    return;
  }
  const hasApi = Boolean(statusCache && (statusCache.has_openai_api_key || statusCache.has_deepseek_api_key));
  const lines = [];
  if (hasApi) {
    lines.push(t("mode_with_api"));
  } else {
    lines.push(t("mode_no_api"));
    lines.push(t("mode_no_api_steps"));
  }
  modeGuide.textContent = lines.join("\n");
  if (!hasUserVisibleResult()) {
    setNextStepsByMode(hasApi ? "pre_run_api" : "pre_run_no_api");
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
  const text = String(task || "").trim();
  if (!text) {
    return;
  }
  const lastUserText = getLastUserBubbleText();
  if (lastUserText === text) {
    return;
  }
  addBubble("user", text);
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

function setOutputPath(path) {
  outputPathText.textContent = String(path || "-");
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
}

function extractTopBullets(markdown, limit = 3) {
  const lines = String(markdown || "").split("\n");
  const bullets = [];
  let inCodeBlock = false;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (line.startsWith("```")) {
      inCodeBlock = !inCodeBlock;
      continue;
    }
    if (inCodeBlock || !line) {
      continue;
    }
    const match = line.match(/^[-*]\s+(.+)$/) || line.match(/^\d+\.\s+(.+)$/);
    if (match && match[1]) {
      bullets.push(match[1].trim());
      if (bullets.length >= limit) {
        break;
      }
    }
  }
  return bullets;
}

function extractTopHeadings(markdown, limit = 4) {
  const lines = String(markdown || "").split("\n");
  const headings = [];
  let inCodeBlock = false;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (line.startsWith("```")) {
      inCodeBlock = !inCodeBlock;
      continue;
    }
    if (inCodeBlock || !line) {
      continue;
    }
    const match = line.match(/^#{1,3}\s+(.+)$/);
    if (match && match[1]) {
      headings.push(match[1].trim());
      if (headings.length >= limit) {
        break;
      }
    }
  }
  return headings;
}

function renderReadableSummary(task, provider, outputText) {
  if (provider === "handoff") {
    setResultSummary(t("summary_handoff"));
    return;
  }
  if (provider === "dry-run") {
    setResultSummary(t("summary_dry_run"));
    return;
  }

  const taskText = String(task || "").toLowerCase();
  const bullets = extractTopBullets(outputText, 3);
  const headings = extractTopHeadings(outputText, 4);
  const lines = [];

  if (taskText.includes("复盘") || taskText.includes("review")) {
    lines.push(t("summary_review_title"));
  } else {
    lines.push(t("summary_run_generic"));
  }

  if (headings.length > 0) {
    lines.push(t("summary_structure_title"));
    for (const item of headings.slice(0, 3)) {
      lines.push(`- ${item}`);
    }
  }

  if (bullets.length > 0) {
    lines.push(t("summary_actions_title"));
    for (const item of bullets) {
      lines.push(`- ${item}`);
    }
  } else {
    lines.push(t("summary_no_bullets"));
  }

  setResultSummary(lines.join("\n"));
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

function renderRunResult(data, userTask) {
  renderInspectResult(data);
  latestOutputPath = data.output_path || null;
  latestSuggestionId = data.suggestion_id || null;
  latestRunProvider = data.provider || providerSelect.value || null;

  const lines = [
    `output_path: ${data.output_path}`,
    `output_hash: ${data.output_hash}`,
    `module: ${data.module}`,
    `provider: ${data.provider || "-"}`,
  ];
  if (data.suggestion_id) {
    lines.push(`suggestion_id: ${data.suggestion_id}`);
  }
  resultTrace.textContent = lines.join("\n");

  setOutputPath(data.output_path || "-");
  setPreview(data.output_preview || "-");
  renderReadableSummary(userTask, latestRunProvider, data.output_preview || "");
  if (latestRunProvider === "handoff") {
    setNextStepsByMode("handoff");
  } else if (latestRunProvider === "dry-run") {
    setNextStepsByMode("dry_run");
  } else {
    setNextStepsByMode("final");
  }
  outputDetails.open = true;
  refreshOutputTokenMeta();
  loadSuggestionDetail(latestSuggestionId);
}

function renderActionPreview(data) {
  if (data.output_path) {
    latestOutputPath = data.output_path;
    setOutputPath(data.output_path);
  }

  if (data.output_preview) {
    setPreview(data.output_preview);
    outputDetails.open = true;
    setOutputTokenMeta("-");
    if (data.action === "learning_handoff_packet") {
      setNextStepsByMode("learning_packet");
    } else if (data.action === "learning_handoff_import") {
      setNextStepsByMode("learning_import");
    } else if (data.action === "ingest_learning") {
      setNextStepsByMode("learning_saved");
    }
    return;
  }

  if (data.action === "learning_handoff_packet" && data.packet_text) {
    setPreview(data.packet_text);
    outputDetails.open = true;
    setOutputTokenMeta("-");
    setNextStepsByMode("learning_packet");
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
    outputDetails.open = true;
    setOutputTokenMeta("-");
    setNextStepsByMode("learning_saved");
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
    setPreview(previewLines.join("\n") || "-");
    outputDetails.open = true;
    setOutputTokenMeta("-");
    setNextStepsByMode("learning_import");
    return;
  }
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

async function copyLatestOutput(withSuccessHint = false) {
  if (!latestOutputPath) {
    addBubble("system", t("msg_no_output_yet"));
    return false;
  }
  const originalIcon = copyOutputBtn.textContent;
  try {
    const data = await getJson(`/api/output?path=${encodeURIComponent(latestOutputPath)}`);
    await copyText(data.content);
    copyOutputBtn.textContent = "✓";
    setTimeout(() => {
      copyOutputBtn.textContent = originalIcon;
    }, 1200);
    if (withSuccessHint) {
      addBubble("system", t("msg_report_copied"));
    }
    return true;
  } catch (err) {
    addBubble("system", t("msg_copy_failed", { error: err.message }));
    return false;
  }
}

async function prepareFollowupTaskTemplate() {
  if (!latestOutputPath) {
    addBubble("system", t("msg_no_output_yet"));
    return;
  }

  try {
    const data = await getJson(`/api/output?path=${encodeURIComponent(latestOutputPath)}`);
    const maxChars = 15000;
    let content = String(data.content || "");
    if (content.length > maxChars) {
      content = `${content.slice(0, maxChars)}\n\n...[truncated]`;
      addBubble("system", t("msg_followup_truncated"));
    }
    const template = `${t("followup_template_intro")}\n\n${content}`;
    taskInput.value = template;
    switchWorkspaceTab("task");
    taskInput.focus();
    taskInput.selectionStart = 0;
    taskInput.selectionEnd = 0;
    setNextStepsByMode("final");
    addBubble("system", t("msg_followup_prepared"));
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

    statusCache = data;

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

    updateProviderHelp();
    updateRetrievalHelp();
    renderModeGuide();
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
    statusCache = data;
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
  switchWorkspaceTab("task");
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
  if (isRunningTask) {
    return;
  }
  switchWorkspaceTab("task");
  const payload = buildPayload();
  if (!payload.task) {
    addBubble("system", t("msg_task_required_run"));
    return;
  }

  addUserTaskOnce(payload.task);

  isRunningTask = true;
  runBtn.disabled = true;
  inspectBtn.disabled = true;
  try {
    const data = await postJson("/api/run", payload);
    renderRunResult(data, payload.task);
    addBubble("system", t("msg_run_complete", { output: data.output_path }));
  } catch (err) {
    addBubble("system", t("msg_run_failed", { error: err.message }));
  } finally {
    isRunningTask = false;
    runBtn.disabled = false;
    inspectBtn.disabled = false;
  }
}

async function runLearningIngest() {
  switchWorkspaceTab("learning");
  const learningText = learningDirectInput.value.trim();
  if (!learningText) {
    addBubble("system", t("msg_learning_text_required"));
    return;
  }

  const sourceRef = learningSourceInput.value.trim();
  const confidenceProfile = resolveLearningConfidence(learningText, sourceRef);
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

  addUserTaskOnce(learningTitleInput.value.trim() || learningText.slice(0, 120));

  const payload = {
    action: "ingest_learning",
    task: learningText,
    title: learningTitleInput.value.trim() || null,
    source_type: LEARNING_SOURCE_DEFAULT,
    max_points: 6,
    confidence: confidenceProfile.confidence,
    tags: ["ui_workspace_learning"],
  };

  try {
    const data = await postJson("/api/action", payload);
    renderActionPreview(data);
    setResultSummary(
      t("msg_learning_ingest_done", {
        events: data.appended_events || 0,
        insights: data.appended_insights || 0,
      })
    );
    addBubble(
      "system",
      t("msg_learning_ingest_done", {
        events: data.appended_events || 0,
        insights: data.appended_insights || 0,
      })
    );
  } catch (err) {
    addBubble("system", t("msg_learning_ingest_failed", { error: err.message }));
  }
}

async function generateLearningHandoffPacket() {
  switchWorkspaceTab("learning");
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
    renderActionPreview(data);
    setResultSummary(t("msg_learning_packet_ready"));
    addBubble("system", t("msg_learning_packet_ready"));
  } catch (err) {
    addBubble("system", t("msg_learning_packet_failed", { error: err.message }));
  }
}

async function importLearningHandoffResponse() {
  switchWorkspaceTab("learning");
  const responseText = learningResponseInput.value.trim();
  if (!responseText) {
    addBubble("system", t("msg_learning_response_required"));
    return;
  }

  const sourceRef = learningSourceInput.value.trim();
  const confidenceProfile = resolveLearningConfidence(responseText, sourceRef);

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

  const payload = {
    action: "learning_handoff_import",
    response_text: responseText,
    source_ref: sourceRef || null,
    title: learningTitleInput.value.trim() || null,
    source_type: LEARNING_SOURCE_DEFAULT,
    confidence: confidenceProfile.confidence,
    tags: ["ui_workspace_learning_handoff"],
  };

  addBubble("system", t("msg_learning_importing"));
  try {
    const data = await postJson("/api/action", payload);
    renderActionPreview(data);
    setResultSummary(t("msg_learning_import_done", { count: data.candidate_total || 0 }));
    addBubble("system", t("msg_learning_import_done", { count: data.candidate_total || 0 }));
  } catch (err) {
    addBubble("system", t("msg_learning_import_failed", { error: err.message }));
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

for (const tab of workspaceTabs) {
  tab.addEventListener("click", () => {
    const target = tab.getAttribute("data-workspace-tab") || "task";
    if (target === activeWorkspaceTab) {
      return;
    }
    switchWorkspaceTab(target);
  });
}

for (const button of document.querySelectorAll(".chip[data-task]")) {
  button.addEventListener("click", () => {
    taskInput.value = button.getAttribute("data-task") || "";
    taskInput.focus();
    runTask();
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

if (quickSettingsBtn) {
  quickSettingsBtn.addEventListener("click", () => {
    openSettingsModal();
  });
}

if (quickCopyBtn) {
  quickCopyBtn.addEventListener("click", () => {
    copyLatestOutput(true);
  });
}

if (quickFollowupBtn) {
  quickFollowupBtn.addEventListener("click", () => {
    prepareFollowupTaskTemplate();
  });
}

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
  updateProviderHelp();
  renderModeGuide();
  refreshOutputTokenMeta();
});

retrievalToggle.addEventListener("change", () => {
  updateRetrievalHelp();
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

if (quickIngestBtn) {
  quickIngestBtn.addEventListener("click", () => {
    runLearningIngest();
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

switchWorkspaceTab("task");
setLanguage("zh");
setStatus(t("status_connecting"), "pending", "status_connecting");
setResultSummary(t("result_summary_empty"));
setOutputPath("-");
setPreview("-");
setOutputTokenMeta("-");
initTheme();
loadSettings();
loadStatus();
