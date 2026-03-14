from __future__ import annotations

import re

TOKEN_RE = re.compile(r"[a-z0-9]+")

SCHEMA_DEBUGGER_MODULES = {"decision", "profile", "memory", "cognition", "principles"}
SCHEMA_DEBUGGER_KEYWORDS = {
    "schema",
    "mental model",
    "cognition",
    "assimilation",
    "accommodation",
    "disequilibrium",
    "equilibration",
    "contradiction",
    "mismatch",
    "invalidation",
}

BASE_EXECUTION_INSTRUCTION = (
    "Follow progressive disclosure and use only the provided context. "
    "Separate observations from inferences, and mark uncertainty when evidence is thin."
)


def _norm(text: str) -> str:
    return " ".join(TOKEN_RE.findall(str(text).lower()))


def _skill_norm(skill: str | None) -> str:
    return str(skill or "").strip().replace("\\", "/").lower()


def schema_debugger_enabled(module: str, task: str) -> bool:
    mod = str(module).strip().lower()
    if mod in SCHEMA_DEBUGGER_MODULES:
        return True

    norm = _norm(task)
    if not norm:
        return False
    return any(keyword in norm for keyword in SCHEMA_DEBUGGER_KEYWORDS)


def schema_debugger_questions(module: str, task: str) -> list[str]:
    if not schema_debugger_enabled(module, task):
        return []

    questions = [
        "What schema is being used to interpret this input right now?",
        "Which assumption is doing hidden work in that interpretation?",
        "What evidence does not fit and why?",
        "What would need to be true for the current model to be wrong?",
        "Is this confusion a lack of information or a structural mismatch?",
        "What new distinction or higher-order synthesis may be emerging?",
    ]

    mod = str(module).strip().lower()
    if mod == "decision":
        questions.append("Which decision rule should be revised if this conflict repeats?")
    if mod == "profile":
        questions.append("Which trigger-response pattern indicates schema drift in self-model?")
    if mod == "memory":
        questions.append("Which repeated note pattern indicates unresolved disequilibrium?")
    if mod == "cognition":
        questions.append("Which accommodation operator best fits this mismatch (weaken/replace/split/merge/refine)?")
    if mod == "principles":
        questions.append("Which constitutional clause constrains this action, and does any time-bounded exception apply?")
    return questions


def schema_debugger_output_sections(module: str, task: str) -> list[str]:
    if not schema_debugger_enabled(module, task):
        return []

    sections = [
        "Facts I Read",
        "Current Schema",
        "Assumptions Under Load",
        "Contradictions / Mismatch",
        "Accommodation Options",
        "Best Revision Hypothesis",
        "Falsification Test",
        "Next Logging Action",
    ]

    mod = str(module).strip().lower()
    if mod == "decision":
        sections.append("Decision Rule Patch")
    if mod == "profile":
        sections.append("Trigger-Response Update")
    if mod == "memory":
        sections.append("Pattern Signal to Track")
    if mod == "cognition":
        sections.append("Equilibration Criteria")
    if mod == "principles":
        sections.append("Constitutional Constraint Check")
    return sections


def review_object_instruction(task: str, module: str, skill: str | None = None) -> str:
    mod = str(module).strip().lower()
    skill_norm = _skill_norm(skill)
    lines: list[str] = []

    if mod == "decision" and skill_norm.endswith("weekly_review.md"):
        lines.extend(
            [
                "Owner-review object contract:",
                "- This weekly review only becomes an owner-review object when it contains a distilled proposal.",
                "- Never use the task title, output path, file list, or run metadata as the proposal itself.",
                "- Keep the review body as the main artifact and, only when the evidence supports a real recommendation, end with exactly one explicit section heading:",
                "  `## Owner Action Proposal`",
                "- Put 1-3 concrete bullets under that heading, each with a short risk note in the same bullet.",
                "- If sample size is too thin or no stable recommendation exists, do not emit the proposal block.",
            ]
        )
        return "\n".join(lines)

    if mod == "content" and skill_norm.endswith("write_after_meal_story.md"):
        lines.extend(
            [
                "Review-object boundary:",
                "- This skill normally produces a draft artifact, not an owner-review object.",
                "- Do not append any `## Content Direction Proposal`, `## Judgment Proposal`, or other owner-review block to the story draft.",
                "- If context includes an accepted content-direction proposal, use it as framing guidance only; do not copy its heading or proposal bullets verbatim into the draft.",
                "- If owner direction or framing judgment is needed, that should be handled as a separate proposal-producing task, not embedded into this draft artifact.",
            ]
        )
        return "\n".join(lines)

    if mod == "content" and skill_norm.endswith("propose_content_direction.md"):
        lines.extend(
            [
                "Owner-review object contract:",
                "- This skill is intended to produce a reviewable content-direction proposal.",
                "- Keep supporting analysis above, and only when you reached a real direction recommendation, end with exactly one explicit section heading:",
                "  `## Content Direction Proposal`",
                "- Put 1-3 distilled bullets under that heading.",
                "- Never use the task title, output path, file list, or run metadata as the proposal itself.",
                "- If context is too thin for a stable direction, say what is missing and do not emit the proposal block.",
            ]
        )
        return "\n".join(lines)

    return ""


def execution_instruction(task: str, module: str, skill: str | None = None) -> str:
    lines = [BASE_EXECUTION_INSTRUCTION]
    prompts = schema_debugger_questions(module, task)
    if prompts:
        lines.append("")
        lines.append("Schema debugger prompts (answer explicitly when relevant):")
        for i, prompt in enumerate(prompts, start=1):
            lines.append(f"{i}. {prompt}")
        lines.append("")
        lines.append("Output structure guideline (unless task requires a strict template):")
        for i, section in enumerate(schema_debugger_output_sections(module, task), start=1):
            lines.append(f"{i}. {section}")
    review_contract = review_object_instruction(task, module, skill)
    if review_contract:
        lines.append("")
        lines.append(review_contract)
    return "\n".join(lines)
