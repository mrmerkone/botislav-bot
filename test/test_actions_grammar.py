import pytest
from lark import Tree, Token, Lark

from botislav.commands import ACTIONS_GRAMMAR


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
                [Tree(Token("RULE", "greeting"), [Token("GREETING", "привет")])],
            ),
        ),
        (
            "прив",
            Tree(
                Token("RULE", "action"),
                [Tree(Token("RULE", "greeting"), [Token("GREETING", "прив")])],
            ),
        ),
        (
            "hello",
            Tree(
                Token("RULE", "action"),
                [Tree(Token("RULE", "greeting"), [Token("GREETING", "hello")])],
            ),
        ),
        # lastmatch
        (
            "катка в доту",
            Tree(
                Token("RULE", "action"),
                [
                    Tree(
                        Token("RULE", "lastmatch"),
                        [
                            Token("LASTMATCH", "катка"),
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
                        Token("RULE", "lastmatch"),
                        [
                            Token("LASTMATCH", "ласткатка"),
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
                        Token("RULE", "lastmatch"),
                        [
                            Tree(Token("RULE", "game"), [Token("DOTA", "dota")]),
                            Token("LASTMATCH", "lm"),
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
                        Token("RULE", "lastmatch"),
                        [
                            Tree(Token("RULE", "game"), [Token("PUBG", "pubg")]),
                            Token("LASTMATCH", "lm"),
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
                        Token("RULE", "lastmatch"),
                        [
                            Token("LASTMATCH", "катка"),
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
                        Token("RULE", "lastmatch"),
                        [
                            Token("LASTMATCH", "lastmatch"),
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
