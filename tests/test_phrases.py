import pytest

from botislav.intents import IntentMeta, IntentClassifier, get_intent_classifier


@pytest.fixture(scope="module")
def intent_classifier() -> IntentClassifier:
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
        ("!lm", IntentMeta("dota_lastmatch")),
        ("ласт катка в pubg", IntentMeta("pubg_lastmatch")),
        ("lm babagee", IntentMeta("pubg_lastmatch")),
        ("lastmatch", IntentMeta("dota_lastmatch")),
        ("привяжи https://www.opendota.com/players/55136643", IntentMeta("link_account")),
    )
)
def test_intent_classifier(
    intent_classifier: IntentClassifier, phrase: str, expected_meta: IntentMeta
):
    assert intent_classifier.get_intent(phrase) == expected_meta
