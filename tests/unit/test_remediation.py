from backend.app.services.remediation import build_actions


def test_build_actions_returns_relevant_action():
    actions = build_actions("Memory leak suspected", "critical")
    assert "Page incident response" in actions
    assert any("Restart" in action for action in actions)
