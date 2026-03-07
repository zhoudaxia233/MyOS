from __future__ import annotations

from prompting import execution_instruction


def run_manual(task: str, module: str, plan: dict, bundle: dict) -> str:
    lines = []
    lines.append("# Execution Packet")
    lines.append("")
    lines.append(f"- Task: {task}")
    lines.append(f"- Module: {module}")
    lines.append(f"- Skill: {plan['skill']}")
    lines.append(f"- Output path: {plan['output_path']}")
    lines.append("")
    lines.append("## Files Loaded")
    for f in bundle.get("files", []):
        lines.append(f"- {f['path']}")
    lines.append("")
    lines.append("## Instruction")
    lines.append(execution_instruction(task, module))
    lines.append("")
    lines.append("Return only the final content for the required output path.")
    return "\n".join(lines) + "\n"
