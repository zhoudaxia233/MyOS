from planner import plan_task


def test_plan_task_with_skill_hint():
    plan = plan_task(
        task="[daily] capture memory",
        module="memory",
        skill_hint="ingest_memory",
        routine_id="rt_daily_memory_ingest",
    )
    assert plan["skill"] == "modules/memory/skills/ingest_memory.md"
    assert "ingest_memory_" in plan["output_path"]
    assert "rt_daily_memory_ingest" in plan["output_path"]
