import pytest

from botislav.actions import Action, ActionManager, get_action_manager


@pytest.fixture(scope="module")
def action_manager() -> ActionManager:
    return get_action_manager()


@pytest.mark.parametrize(
    "phrase, expected_action",
    (
        ("бла бла бла", None),
        ("кто пойдет играть", None),
        ("привет", Action("greeting")),
        ("hello", Action("greeting")),
        ("здарова", Action("greeting")),
        ("ласт катка в доту", Action("lastmatch", {"game": "DOTA"})),
        ("last match dota ", Action("lastmatch", {"game": "DOTA"})),
        ("lm", Action("lastmatch", {"game": "DOTA"})),
        ("ласт катка в pubg", Action("lastmatch", {"game": "PUBG"})),
        ("lm baba gee", Action("lastmatch", {"game": "PUBG"})),
    ),
)
def test_action_manager(
    action_manager: ActionManager, phrase: str, expected_action: Action
):
    assert action_manager.get_action(phrase) == expected_action
