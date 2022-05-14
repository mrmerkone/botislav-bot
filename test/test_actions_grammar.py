import pytest
from lark import Tree, Token, Lark

from botislav.parsing import ACTIONS_GRAMMAR


@pytest.fixture
def parser():
    return Lark(grammar=ACTIONS_GRAMMAR, start="action")


@pytest.mark.parametrize(
    "phrase, expected",
    (
        # hello
        (
            "привет",
            Tree(
                Token("RULE", "action"),
                [Tree(Token("RULE", "hello"), [Token("GREETING", "привет")])],
            ),
        ),
        (
            "прив",
            Tree(
                Token("RULE", "action"),
                [Tree(Token("RULE", "hello"), [Token("GREETING", "прив")])],
            ),
        ),
        (
            "hello",
            Tree(
                Token("RULE", "action"),
                [Tree(Token("RULE", "hello"), [Token("GREETING", "hello")])],
            ),
        ),
        # last_match
        (
            "катка в доту",
            Tree(
                Token("RULE", "action"),
                [
                    Tree(
                        Token("RULE", "last_match"),
                        [
                            Token("LAST_MATCH", "катка"),
                            Tree(Token("RULE", "game"), [Token("DOTA", "доту")]),
                        ],
                    )
                ],
            ),
        ),
        (
            "ласткатка в доту",
            Tree(
                Token("RULE", "action"),
                [
                    Tree(
                        Token("RULE", "last_match"),
                        [
                            Token("LAST_MATCH", "ласткатка"),
                            Tree(Token("RULE", "game"), [Token("DOTA", "доту")]),
                        ],
                    )
                ],
            ),
        ),
        (
            "dota lm",
            Tree(
                Token("RULE", "action"),
                [
                    Tree(
                        Token("RULE", "last_match"),
                        [
                            Tree(Token("RULE", "game"), [Token("DOTA", "dota")]),
                            Token("LAST_MATCH", "lm"),
                        ],
                    )
                ],
            ),
        ),
        (
            "pubg lm",
            Tree(
                Token("RULE", "action"),
                [
                    Tree(
                        Token("RULE", "last_match"),
                        [
                            Tree(Token("RULE", "game"), [Token("PUBG", "pubg")]),
                            Token("LAST_MATCH", "lm"),
                        ],
                    )
                ],
            ),
        ),
        (
            "катка пубг",
            Tree(
                Token("RULE", "action"),
                [
                    Tree(
                        Token("RULE", "last_match"),
                        [
                            Token("LAST_MATCH", "катка"),
                            Tree(Token("RULE", "game"), [Token("PUBG", "пубг")]),
                        ],
                    )
                ],
            ),
        ),
        (
            "lastmatch pubg",
            Tree(
                Token("RULE", "action"),
                [
                    Tree(
                        Token("RULE", "last_match"),
                        [
                            Token("LAST_MATCH", "lastmatch"),
                            Tree(Token("RULE", "game"), [Token("PUBG", "pubg")]),
                        ],
                    )
                ],
            ),
        ),
    ),
)
def test_ast_parsing(phrase, expected, parser):
    assert parser.parse(phrase) == expected
