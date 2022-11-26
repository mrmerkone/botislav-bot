import pytest

from botislav.intents import IntentMeta, IntentClassifier, get_intent_classifier


@pytest.fixture(scope="module")
def meta_extractor() -> IntentClassifier:
    return get_intent_classifier()


@pytest.mark.parametrize(
    "phrase, expected_meta",
    (
        ("бла бла бла", IntentMeta("silence")),
        ("кто пойдет играть", IntentMeta("silence")),
        ("gish is clueless", IntentMeta("silence")),
        ("привет", IntentMeta("greeting")),
        ("hello", IntentMeta("greeting")),
        ("здарова", IntentMeta("greeting")),
        ("ласт катка в доту", IntentMeta("dota_lastmatch")),
        ("last match dota ", IntentMeta("dota_lastmatch")),
        ("lm", IntentMeta("dota_lastmatch")),
        ("ласт катка в pubg", IntentMeta("pubg_lastmatch")),
        ("lm baba gee", IntentMeta("pubg_lastmatch")),
    ),
)
def test_action_manager(
    meta_extractor: IntentClassifier, phrase: str, expected_meta: IntentMeta
):
    assert meta_extractor.get_intent(phrase) == expected_meta
