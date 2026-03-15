from myos.mode import detect_mode


def test_detects_explore_by_default() -> None:
    mode, source = detect_mode("I keep thinking there is something here but I can't name it yet.")
    assert mode == "explore"
    assert source == "heuristic"


def test_detects_learn_from_learning_language() -> None:
    mode, _ = detect_mode("I read an article today and here is the link: https://example.com/story")
    assert mode == "learn"


def test_detects_create_from_writing_language() -> None:
    mode, _ = detect_mode("I want to write an essay about MyOS and shape this idea.")
    assert mode == "create"


def test_detects_decide_from_decision_language() -> None:
    mode, _ = detect_mode("Should I move out or try to negotiate with my landlord?")
    assert mode == "decide"


def test_explicit_override_wins() -> None:
    mode, source = detect_mode("I want to write an essay about MyOS.", explicit_mode="learn")
    assert mode == "learn"
    assert source == "explicit"
