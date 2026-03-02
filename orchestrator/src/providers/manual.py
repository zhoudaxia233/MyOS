from __future__ import annotations


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
    lines.append("Execute the skill using the loaded files, then write the final output to the output path above.")
    return "\n".join(lines) + "\n"
