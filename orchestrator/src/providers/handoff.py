from __future__ import annotations


def _sanitize_fence(text: str) -> str:
    # Avoid breaking markdown fence when users paste into external chat UIs.
    return text.replace("```", "` ` `")


def run_handoff(task: str, module: str, plan: dict, bundle: dict) -> str:
    lines: list[str] = []
    lines.append("[BEGIN PERSONAL CORE OS HANDOFF]")
    lines.append("")
    lines.append("Role: You are an execution assistant for Personal Core OS.")
    lines.append("Policy: Follow progressive disclosure and use only the provided context.")
    lines.append("")
    lines.append("Task:")
    lines.append(task)
    lines.append("")
    lines.append("Target module:")
    lines.append(module)
    lines.append("")
    lines.append("Skill file:")
    lines.append(plan["skill"])
    lines.append("")
    lines.append("Required output path:")
    lines.append(plan["output_path"])
    lines.append("")
    lines.append("Context files:")

    files = bundle.get("files", [])
    if not files:
        lines.append("- (none)")
    else:
        for item in files:
            lines.append("")
            lines.append(f"## FILE: {item['path']}")
            lines.append(_sanitize_fence(item["content"]))

    lines.append("")
    lines.append("Output requirement:")
    lines.append("Return only the final content for the required output path.")
    lines.append("")
    lines.append("[END PERSONAL CORE OS HANDOFF]")
    return "\n".join(lines)
