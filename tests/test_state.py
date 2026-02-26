from functions.core.state import AppState, add_selected, remove_selected, selected_list


def test_dedupe_by_skill_id():
    s = AppState()
    add_selected(s, {"skill_id": "A", "skill_name": "x"})
    add_selected(s, {"skill_id": "A", "skill_name": "x2"})
    assert len(s.selected) == 1
    assert s.selected["A"]["skill_name"] == "x2"


def test_remove():
    s = AppState()
    add_selected(s, {"skill_id": "A", "skill_name": "x"})
    remove_selected(s, "A")
    assert len(s.selected) == 0


def test_selected_list_sorted():
    s = AppState()
    add_selected(s, {"skill_id": "1", "skill_name": "b", "relevance_score": 0.2})
    add_selected(s, {"skill_id": "2", "skill_name": "a", "relevance_score": 0.9})
    out = selected_list(s)
    assert out[0]["skill_id"] == "2"