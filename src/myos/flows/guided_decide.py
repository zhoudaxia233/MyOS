from __future__ import annotations

from myos.protocol import SessionRequest


def render_decide_response(request: SessionRequest) -> str:
    situation_type, working_frame, prompts = _classify_situation(request.raw_input)
    return "\n".join(
        [
            "[decide]",
            "MyOS reads this as a decision situation.",
            f"Situation type: {situation_type}",
            f"Working frame: {working_frame}",
            "Next step:",
            f"- {prompts[0]}",
            f"- {prompts[1]}",
            f"- {prompts[2]}",
        ]
    )


def _classify_situation(raw_input: str) -> tuple[str, str, tuple[str, str, str]]:
    lowered = raw_input.lower()
    if any(
        phrase in lowered
        for phrase in (
            "landlord",
            "partner",
            "friend",
            "coworker",
            "colleague",
            "manager",
            "family",
            "relationship",
            "message",
            "texted",
            "conversation",
            "conflict",
        )
    ):
        return (
            "Interpersonal.",
            "This looks like a human situation where facts and emotions can get tangled together.",
            (
                "List the concrete facts and what was actually said or done.",
                "Separate your emotions and interpretations from those facts.",
                "Name the options you really have and the missing information that would change the choice.",
            ),
        )
    if any(
        phrase in lowered
        for phrase in (
            "rent",
            "invoice",
            "budget",
            "tax",
            "contract",
            "legal",
            "policy",
            "deadline",
            "fee",
            "price",
            "application",
            "visa",
            "insurance",
            "reimburse",
            "account",
        )
    ):
        return (
            "Financial / procedural.",
            "This looks constrained by rules, money, process, or deadlines, so grounding matters more than speed.",
            (
                "Write down the concrete numbers, rules, dates, or commitments involved.",
                "Name the hard constraints and the downside if you choose wrong or wait.",
                "Identify the one missing document, rule, or fact that would most change the answer.",
            ),
        )
    if any(
        phrase in lowered
        for phrase in (
            "strategy",
            "strategic",
            "roadmap",
            "career",
            "project",
            "direction",
            "positioning",
            "team",
            "company",
            "allocate",
            "priority",
            "prioritize",
            "focus",
        )
    ):
        return (
            "Strategic.",
            "This looks like a directional choice under uncertainty, so compare options by goal, constraints, and reversibility.",
            (
                "State the goal you are optimizing for and the time horizon.",
                "List the real options, including doing nothing, and mark which are reversible.",
                "Name the assumption or missing information that matters most.",
            ),
        )
    return (
        "Ambiguous.",
        "This looks like a mixed decision situation, so structure it before trying to solve it.",
        (
            "Separate facts, feelings, constraints, and options.",
            "Write the decision question in one sentence.",
            "Note the one missing fact that would most change the answer.",
        ),
    )
