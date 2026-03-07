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


def execution_instruction(task: str, module: str) -> str:
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
    return "\n".join(lines)
