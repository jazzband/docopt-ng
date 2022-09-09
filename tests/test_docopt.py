from __future__ import annotations

import re
from textwrap import dedent
from typing import Sequence

import pytest
from pytest import raises

from docopt import Argument
from docopt import Command
from docopt import DocoptExit
from docopt import DocoptLanguageError
from docopt import Either
from docopt import NotRequired
from docopt import OneOrMore
from docopt import Option
from docopt import OptionsShortcut
from docopt import ParsedOptions
from docopt import Required
from docopt import Tokens
from docopt import docopt
from docopt import formal_usage
from docopt import lint_docstring
from docopt import parse_argv
from docopt import parse_docstring_sections
from docopt import parse_longer
from docopt import parse_options
from docopt import parse_pattern
from docopt import parse_shorts
from docopt import transform


def test_pattern_flat():
    assert Required(OneOrMore(Argument("N")), Option("-a"), Argument("M")).flat() == [
        Argument("N"),
        Option("-a"),
        Argument("M"),
    ]
    assert Required(
        NotRequired(OptionsShortcut()), NotRequired(Option("-a", None))
    ).flat(OptionsShortcut) == [OptionsShortcut()]


def test_option():
    assert Option.parse("-h") == Option("-h", None)
    assert Option.parse("--help") == Option(None, "--help")
    assert Option.parse("-h --help") == Option("-h", "--help")
    assert Option.parse("-h, --help") == Option("-h", "--help")

    assert Option.parse("-h TOPIC") == Option("-h", None, 1)
    assert Option.parse("--help TOPIC") == Option(None, "--help", 1)
    assert Option.parse("-h TOPIC --help TOPIC") == Option("-h", "--help", 1)
    assert Option.parse("-h TOPIC, --help TOPIC") == Option("-h", "--help", 1)
    assert Option.parse("-h TOPIC, --help=TOPIC") == Option("-h", "--help", 1)

    assert Option.parse("-h  Description...") == Option("-h", None)
    assert Option.parse("-h --help  Description...") == Option("-h", "--help")
    assert Option.parse("-h TOPIC  Description...") == Option("-h", None, 1)

    assert Option.parse("    -h") == Option("-h", None)

    assert Option.parse("-h TOPIC  Descripton... [default: 2]") == Option(
        "-h", None, 1, "2"
    )
    assert Option.parse("-h TOPIC  Descripton... [default: topic-1]") == Option(
        "-h", None, 1, "topic-1"
    )
    assert Option.parse("--help=TOPIC  ... [default: 3.14]") == Option(
        None, "--help", 1, "3.14"
    )
    assert Option.parse("-h, --help=DIR  ... [default: ./]") == Option(
        "-h", "--help", 1, "./"
    )
    assert Option.parse("-h TOPIC  Descripton... [dEfAuLt: 2]") == Option(
        "-h", None, 1, "2"
    )


def test_option_name():
    assert Option("-h", None).name == "-h"
    assert Option("-h", "--help").name == "--help"
    assert Option(None, "--help").name == "--help"


def test_commands():
    assert docopt("Usage: prog add", "add") == {"add": True}
    assert docopt("Usage: prog [add]", "") == {"add": False}
    assert docopt("Usage: prog [add]", "add") == {"add": True}
    assert docopt("Usage: prog (add|rm)", "add") == {"add": True, "rm": False}
    assert docopt("Usage: prog (add|rm)", "rm") == {"add": False, "rm": True}
    assert docopt("Usage: prog a b", "a b") == {"a": True, "b": True}
    with raises(
        DocoptExit,
        match=r"Warning: found unmatched \(duplicate\?\) arguments.*'b'.*'a'",
    ):
        docopt("Usage: prog a b", "b a")


def test_formal_usage():
    doc = """
    Usage: prog [-hv] ARG
           prog N M

    prog is a program."""
    _, _, usage_body, _ = parse_docstring_sections(doc)
    assert usage_body == " prog [-hv] ARG\n           prog N M\n"
    assert formal_usage(usage_body) == "( [-hv] ARG ) | ( N M )"


def test_parse_argv():
    def TS(s):
        return Tokens(s, error=DocoptExit)

    o = [Option("-h"), Option("-v", "--verbose"), Option("-f", "--file", 1)]
    assert parse_argv(TS(""), options=o) == []
    assert parse_argv(TS("-h"), options=o) == [Option("-h", None, 0, True)]
    assert parse_argv(TS("-h --verbose"), options=o) == [
        Option("-h", None, 0, True),
        Option("-v", "--verbose", 0, True),
    ]
    assert parse_argv(TS("-h --file f.txt"), options=o) == [
        Option("-h", None, 0, True),
        Option("-f", "--file", 1, "f.txt"),
    ]
    assert parse_argv(TS("-h --file f.txt arg"), options=o) == [
        Option("-h", None, 0, True),
        Option("-f", "--file", 1, "f.txt"),
        Argument(None, "arg"),
    ]
    assert parse_argv(TS("-h --file f.txt arg arg2"), options=o) == [
        Option("-h", None, 0, True),
        Option("-f", "--file", 1, "f.txt"),
        Argument(None, "arg"),
        Argument(None, "arg2"),
    ]
    assert parse_argv(TS("-h arg -- -v"), options=o) == [
        Option("-h", None, 0, True),
        Argument(None, "arg"),
        Argument(None, "--"),
        Argument(None, "-v"),
    ]


def test_parse_pattern():
    o = [Option("-h"), Option("-v", "--verbose"), Option("-f", "--file", 1)]
    assert parse_pattern("[ -h ]", options=o) == Required(NotRequired(Option("-h")))
    assert parse_pattern("[ ARG ... ]", options=o) == Required(
        NotRequired(OneOrMore(Argument("ARG")))
    )
    assert parse_pattern("[ -h | -v ]", options=o) == Required(
        NotRequired(Either(Option("-h"), Option("-v", "--verbose")))
    )
    assert parse_pattern("( -h | -v [ --file <f> ] )", options=o) == Required(
        Required(
            Either(
                Option("-h"),
                Required(
                    Option("-v", "--verbose"),
                    NotRequired(Option("-f", "--file", 1, None)),
                ),
            )
        )
    )
    assert parse_pattern("(-h|-v[--file=<f>]N...)", options=o) == Required(
        Required(
            Either(
                Option("-h"),
                Required(
                    Option("-v", "--verbose"),
                    NotRequired(Option("-f", "--file", 1, None)),
                    OneOrMore(Argument("N")),
                ),
            )
        )
    )
    assert parse_pattern("(N [M | (K | L)] | O P)", options=[]) == Required(
        Required(
            Either(
                Required(
                    Argument("N"),
                    NotRequired(
                        Either(
                            Argument("M"),
                            Required(Either(Argument("K"), Argument("L"))),
                        )
                    ),
                ),
                Required(Argument("O"), Argument("P")),
            )
        )
    )
    assert parse_pattern("[ -h ] [N]", options=o) == Required(
        NotRequired(Option("-h")), NotRequired(Argument("N"))
    )
    assert parse_pattern("[options]", options=o) == Required(
        NotRequired(OptionsShortcut())
    )
    assert parse_pattern("[options] A", options=o) == Required(
        NotRequired(OptionsShortcut()), Argument("A")
    )
    assert parse_pattern("-v [options]", options=o) == Required(
        Option("-v", "--verbose"), NotRequired(OptionsShortcut())
    )
    assert parse_pattern("ADD", options=o) == Required(Argument("ADD"))
    assert parse_pattern("<add>", options=o) == Required(Argument("<add>"))
    assert parse_pattern("add", options=o) == Required(Command("add"))


def test_option_match():
    assert Option("-a").match([Option("-a", value=True)]) == (
        True,
        [],
        [Option("-a", value=True)],
    )
    assert Option("-a").match([Option("-x")]) == (False, [Option("-x")], [])
    assert Option("-a").match([Argument("N")]) == (False, [Argument("N")], [])
    assert Option("-a").match([Option("-x"), Option("-a"), Argument("N")]) == (
        True,
        [Option("-x"), Argument("N")],
        [Option("-a")],
    )
    assert Option("-a").match([Option("-a", value=True), Option("-a")]) == (
        True,
        [Option("-a")],
        [Option("-a", value=True)],
    )


def test_argument_match():
    assert Argument("N").match([Argument(None, 9)]) == (True, [], [Argument("N", 9)])
    assert Argument("N").match([Option("-x")]) == (False, [Option("-x")], [])
    assert Argument("N").match([Option("-x"), Option("-a"), Argument(None, 5)]) == (
        True,
        [Option("-x"), Option("-a")],
        [Argument("N", 5)],
    )
    assert Argument("N").match([Argument(None, 9), Argument(None, 0)]) == (
        True,
        [Argument(None, 0)],
        [Argument("N", 9)],
    )


def test_command_match():
    assert Command("c").match([Argument(None, "c")]) == (True, [], [Command("c", True)])
    assert Command("c").match([Option("-x")]) == (False, [Option("-x")], [])
    assert Command("c").match([Option("-x"), Option("-a"), Argument(None, "c")]) == (
        True,
        [Option("-x"), Option("-a")],
        [Command("c", True)],
    )
    assert Either(Command("add", False), Command("rm", False)).match(
        [Argument(None, "rm")]
    ) == (True, [], [Command("rm", True)])


def test_optional_match():
    assert NotRequired(Option("-a")).match([Option("-a")]) == (True, [], [Option("-a")])
    assert NotRequired(Option("-a")).match([]) == (True, [], [])
    assert NotRequired(Option("-a")).match([Option("-x")]) == (True, [Option("-x")], [])
    assert NotRequired(Option("-a"), Option("-b")).match([Option("-a")]) == (
        True,
        [],
        [Option("-a")],
    )
    assert NotRequired(Option("-a"), Option("-b")).match([Option("-b")]) == (
        True,
        [],
        [Option("-b")],
    )
    assert NotRequired(Option("-a"), Option("-b")).match([Option("-x")]) == (
        True,
        [Option("-x")],
        [],
    )
    assert NotRequired(Argument("N")).match([Argument(None, 9)]) == (
        True,
        [],
        [Argument("N", 9)],
    )
    assert NotRequired(Option("-a"), Option("-b")).match(
        [Option("-b"), Option("-x"), Option("-a")]
    ) == (True, [Option("-x")], [Option("-a"), Option("-b")])


def test_required_match():
    assert Required(Option("-a")).match([Option("-a")]) == (True, [], [Option("-a")])
    assert Required(Option("-a")).match([]) == (False, [], [])
    assert Required(Option("-a")).match([Option("-x")]) == (False, [Option("-x")], [])
    assert Required(Option("-a"), Option("-b")).match([Option("-a")]) == (
        False,
        [Option("-a")],
        [],
    )


def test_either_match():
    assert Either(Option("-a"), Option("-b")).match([Option("-a")]) == (
        True,
        [],
        [Option("-a")],
    )
    assert Either(Option("-a"), Option("-b")).match([Option("-a"), Option("-b")]) == (
        True,
        [Option("-b")],
        [Option("-a")],
    )
    assert Either(Option("-a"), Option("-b")).match([Option("-x")]) == (
        False,
        [Option("-x")],
        [],
    )
    assert Either(Option("-a"), Option("-b"), Option("-c")).match(
        [Option("-x"), Option("-b")]
    ) == (True, [Option("-x")], [Option("-b")])
    assert Either(Argument("M"), Required(Argument("N"), Argument("M"))).match(
        [Argument(None, 1), Argument(None, 2)]
    ) == (
        True,
        [],
        [Argument("N", 1), Argument("M", 2)],
    )


def test_one_or_more_match():
    assert OneOrMore(Argument("N")).match([Argument(None, 9)]) == (
        True,
        [],
        [Argument("N", 9)],
    )
    assert OneOrMore(Argument("N")).match([]) == (False, [], [])
    assert OneOrMore(Argument("N")).match([Option("-x")]) == (False, [Option("-x")], [])
    assert OneOrMore(Argument("N")).match([Argument(None, 9), Argument(None, 8)]) == (
        True,
        [],
        [Argument("N", 9), Argument("N", 8)],
    )
    assert OneOrMore(Argument("N")).match(
        [Argument(None, 9), Option("-x"), Argument(None, 8)]
    ) == (True, [Option("-x")], [Argument("N", 9), Argument("N", 8)])
    assert OneOrMore(Option("-a")).match(
        [Option("-a"), Argument(None, 8), Option("-a")]
    ) == (True, [Argument(None, 8)], [Option("-a"), Option("-a")])
    assert OneOrMore(Option("-a")).match([Argument(None, 8), Option("-x")]) == (
        False,
        [Argument(None, 8), Option("-x")],
        [],
    )
    assert OneOrMore(Required(Option("-a"), Argument("N"))).match(
        [Option("-a"), Argument(None, 1), Option("-x"), Option("-a"), Argument(None, 2)]
    ) == (
        True,
        [Option("-x")],
        [Option("-a"), Argument("N", 1), Option("-a"), Argument("N", 2)],
    )
    assert OneOrMore(NotRequired(Argument("N"))).match([Argument(None, 9)]) == (
        True,
        [],
        [Argument("N", 9)],
    )


def test_list_argument_match():
    assert Required(Argument("N"), Argument("N")).fix().match(
        [Argument(None, "1"), Argument(None, "2")]
    ) == (True, [], [Argument("N", ["1", "2"])])
    assert OneOrMore(Argument("N")).fix().match(
        [Argument(None, "1"), Argument(None, "2"), Argument(None, "3")]
    ) == (True, [], [Argument("N", ["1", "2", "3"])])
    assert Required(Argument("N"), OneOrMore(Argument("N"))).fix().match(
        [Argument(None, "1"), Argument(None, "2"), Argument(None, "3")]
    ) == (
        True,
        [],
        [Argument("N", ["1", "2", "3"])],
    )
    assert Required(Argument("N"), Required(Argument("N"))).fix().match(
        [Argument(None, "1"), Argument(None, "2")]
    ) == (True, [], [Argument("N", ["1", "2"])])


def test_basic_pattern_matching():
    # ( -a N [ -x Z ] )
    pattern = Required(
        Option("-a"), Argument("N"), NotRequired(Option("-x"), Argument("Z"))
    )
    # -a N
    assert pattern.match([Option("-a"), Argument(None, 9)]) == (
        True,
        [],
        [Option("-a"), Argument("N", 9)],
    )
    # -a -x N Z
    assert pattern.match(
        [Option("-a"), Option("-x"), Argument(None, 9), Argument(None, 5)]
    ) == (
        True,
        [],
        [Option("-a"), Argument("N", 9), Option("-x"), Argument("Z", 5)],
    )
    # -x N Z  # BZZ!
    assert pattern.match([Option("-x"), Argument(None, 9), Argument(None, 5)]) == (
        False,
        [Option("-x"), Argument(None, 9), Argument(None, 5)],
        [],
    )


def test_pattern_either():
    assert transform(Option("-a")) == Either(Required(Option("-a")))
    assert transform(Argument("A")) == Either(Required(Argument("A")))
    assert transform(
        Required(Either(Option("-a"), Option("-b")), Option("-c"))
    ) == Either(
        Required(Option("-a"), Option("-c")), Required(Option("-b"), Option("-c"))
    )
    assert transform(
        NotRequired(Option("-a"), Either(Option("-b"), Option("-c")))
    ) == Either(
        Required(Option("-b"), Option("-a")), Required(Option("-c"), Option("-a"))
    )
    assert transform(
        Either(Option("-x"), Either(Option("-y"), Option("-z")))
    ) == Either(Required(Option("-x")), Required(Option("-y")), Required(Option("-z")))
    assert transform(OneOrMore(Argument("N"), Argument("M"))) == Either(
        Required(Argument("N"), Argument("M"), Argument("N"), Argument("M"))
    )


def test_pattern_fix_repeating_arguments():
    assert Required(Option("-a")).fix_repeating_arguments() == Required(Option("-a"))
    assert Required(Argument("N", None)).fix_repeating_arguments() == Required(
        Argument("N", None)
    )
    assert Required(Argument("N"), Argument("N")).fix_repeating_arguments() == Required(
        Argument("N", []), Argument("N", [])
    )
    assert Either(Argument("N"), OneOrMore(Argument("N"))).fix() == Either(
        Argument("N", []), OneOrMore(Argument("N", []))
    )


def test_set():
    assert Argument("N") == Argument("N")
    assert set([Argument("N"), Argument("N")]) == set([Argument("N")])


def test_pattern_fix_identities_1():
    pattern = Required(Argument("N"), Argument("N"))
    assert pattern.children[0] == pattern.children[1]
    assert pattern.children[0] is not pattern.children[1]
    pattern.fix_identities()
    assert pattern.children[0] is pattern.children[1]


def test_pattern_fix_identities_2():
    pattern = Required(NotRequired(Argument("X"), Argument("N")), Argument("N"))
    assert pattern.children[0].children[1] == pattern.children[1]
    assert pattern.children[0].children[1] is not pattern.children[1]
    pattern.fix_identities()
    assert pattern.children[0].children[1] is pattern.children[1]


@pytest.mark.parametrize("tokens", [[], ["not_a_long_option"]])
def test_parse_longer__rejects_inappropriate_token(tokens: list[str]):
    with raises(
        ValueError, match=r"parse_longer got what appears to be an invalid token"
    ):
        parse_longer(Tokens(tokens), [])


def test_parse_longer__rejects_duplicate_long_options():
    options = [Option(None, "--foo"), Option(None, "--foo")]
    with raises(DocoptLanguageError, match=r"foo is not a unique prefix"):
        parse_longer(Tokens("--foo"), options)


@pytest.mark.parametrize("tokens", [[], ["not_a_short_option"]])
def test_parse_shorts__rejects_inappropriate_token(tokens: list[str]):
    with raises(
        ValueError, match=r"parse_shorts got what appears to be an invalid token"
    ):
        parse_shorts(Tokens(tokens), [])


def test_parse_shorts__rejects_duplicate_short_options():
    options = [Option("-f"), Option("-f")]
    with raises(DocoptLanguageError, match=r"-f is specified ambiguously 2 times"):
        parse_shorts(Tokens("-f"), options)


def test_long_options_error_handling():
    #    with raises(DocoptLanguageError):
    #        docopt('Usage: prog --non-existent', '--non-existent')
    #    with raises(DocoptLanguageError):
    #        docopt('Usage: prog --non-existent')
    with raises(
        DocoptExit,
        match=r"Warning: found unmatched \(duplicate\?\) arguments.*--non-existent",
    ):
        docopt("Usage: prog", "--non-existent")
    with raises(
        DocoptExit, match=r"Warning: found unmatched \(duplicate\?\) arguments.*--ver\b"
    ):
        docopt(
            "Usage: prog [--version --verbose]\n" "Options: --version\n --verbose",
            "--ver",
        )
    # --long is missing ARG in usage
    with raises(DocoptLanguageError, match=r"unmatched '\('"):
        docopt("Usage: prog --long\nOptions: --long ARG")
    with raises(DocoptExit, match=r"--long requires argument"):
        docopt("Usage: prog --long ARG\nOptions: --long ARG", "--long")
    with raises(DocoptLanguageError, match=r"--long must not have an argument"):
        docopt("Usage: prog --long=ARG\nOptions: --long")
    with raises(DocoptExit, match=r"--long must not have an argument"):
        docopt("Usage: prog --long\nOptions: --long", "--long=ARG")


def test_short_options_error_handling():
    with raises(DocoptLanguageError, match=r"-x is specified ambiguously 2 times"):
        docopt("Usage: prog -x\nOptions: -x  this\n -x  that")

    with raises(
        DocoptExit, match=r"Warning: found unmatched \(duplicate\?\) arguments.*-x"
    ):
        docopt("Usage: prog", "-x")

    with raises(DocoptLanguageError):
        docopt("Usage: prog -o\nOptions: -o ARG")
    with raises(DocoptExit, match=r"-o requires argument"):
        docopt("Usage: prog -o ARG\nOptions: -o ARG", "-o")


def test_matching_paren():
    with raises(DocoptLanguageError, match=r"unmatched '\['"):
        docopt("Usage: prog [a [b]")
    with raises(DocoptLanguageError, match=r"unexpected ending: '\)'"):
        docopt("Usage: prog [a [b] ] c )")


def test_allow_double_dash():
    assert docopt("usage: prog [-o] [--] <arg>\nkptions: -o", "-- -o") == {
        "-o": False,
        "<arg>": "-o",
        "--": True,
    }
    assert docopt("usage: prog [-o] [--] <arg>\nkptions: -o", "-o 1") == {
        "-o": True,
        "<arg>": "1",
        "--": False,
    }
    with raises(
        DocoptExit, match=r"Warning: found unmatched \(duplicate\?\) arguments.*-o\b"
    ):  # "--" is not allowed; FIXME?
        docopt("usage: prog [-o] <arg>\noptions:-o", "-- -o")


def test_docopt(capsys: pytest.CaptureFixture):
    doc = """Usage: prog [-v] A

             Options: -v  Be verbose."""
    assert docopt(doc, "arg") == {"-v": False, "A": "arg"}
    assert docopt(doc, "-v arg") == {"-v": True, "A": "arg"}

    doc = """Usage: prog [-vqr] [FILE]
              prog INPUT OUTPUT
              prog --help

    Options:
      -v  print status messages
      -q  report only file names
      -r  show all occurrences of the same error
      --help

    """
    a = docopt(doc, "-v file.py")
    assert a == {
        "-v": True,
        "-q": False,
        "-r": False,
        "--help": False,
        "FILE": "file.py",
        "INPUT": None,
        "OUTPUT": None,
    }

    a = docopt(doc, "-v")
    assert a == {
        "-v": True,
        "-q": False,
        "-r": False,
        "--help": False,
        "FILE": None,
        "INPUT": None,
        "OUTPUT": None,
    }

    with raises(
        DocoptExit,
        match=r"Warning: found unmatched \(duplicate\?\) arguments.*output\.py",
    ):
        docopt(doc, "-v input.py output.py")

    with raises(
        DocoptExit,
        match=r"Warning: found unmatched \(duplicate\?\) arguments.*--fake",
    ):
        docopt(doc, "--fake")

    capsys.readouterr()  # clear any captured output

    with raises(SystemExit):
        docopt(doc, "--hel")
    assert capsys.readouterr().out.startswith("Usage: prog")


@pytest.mark.parametrize(
    "items, expected",
    [
        ({}, "{}"),
        (
            {"<z>": None, "<a>": None, "--foo": "abc", "--bar": True},
            ("{'--bar': True,\n '--foo': 'abc',\n '<a>': None,\n '<z>': None}"),
        ),
    ],
)
def test_docopt_result_dict_repr(items: dict[str, object], expected: str):
    assert repr(ParsedOptions(items)) == expected


@pytest.mark.parametrize(
    "args, before_usage_val", [("", None), ("--before-usage=2", "2")]
)
def test_docopt__usage_descriptions_cant_bridge_usage_section(
    args: str, before_usage_val: str | None
):
    # For compatibility with docopt 0.6.2 we support option descriptions
    # before the usage and after (but not inside usage). However, a
    # description cannot start in one part and continue in the next.
    # i.e. the default value after Usage does not apply to
    # --before-usage
    usage = """\
My prog

--before-usage VAL

Usage:
    prog [options]

[default: 42]
Options:
    --after-usage
"""
    assert docopt(usage, args) == {
        "--before-usage": before_usage_val,
        "--after-usage": False,
    }


def test_language_errors():
    with raises(
        DocoptLanguageError,
        match=r'Failed to parse doc: "usage:" section \(case-insensitive\) not '
        r"found\. Check http://docopt\.org/ for examples of how your doc "
        r"should look\.",
    ):
        docopt("no usage with colon here")
    with raises(
        DocoptLanguageError, match=r'More than one "usage:" \(case-insensitive\)'
    ):
        docopt("usage: here \n\n and again usage: here")


def test_issue_40(capsys: pytest.CaptureFixture):
    with raises(SystemExit):  # i.e. shows help
        docopt("usage: prog --help-commands | --help", "--help")
    assert capsys.readouterr().out.startswith("usage: prog --help-commands | --help")

    assert docopt("usage: prog --aabb | --aa", "--aa") == {
        "--aabb": False,
        "--aa": True,
    }


def test_count_multiple_flags():
    assert docopt("usage: prog [-v]", "-v") == {"-v": True}
    assert docopt("usage: prog [-vv]", "") == {"-v": 0}
    assert docopt("usage: prog [-vv]", "-v") == {"-v": 1}
    assert docopt("usage: prog [-vv]", "-vv") == {"-v": 2}
    with raises(
        DocoptExit, match=r"Warning: found unmatched \(duplicate\?\) arguments.*'-v'"
    ):
        docopt("usage: prog [-vv]", "-vvv")
    assert docopt("usage: prog [-v | -vv | -vvv]", "-vvv") == {"-v": 3}
    assert docopt("usage: prog -v...", "-vvvvvv") == {"-v": 6}
    assert docopt("usage: prog [--ver --ver]", "--ver --ver") == {"--ver": 2}


def test_any_options_parameter():
    with raises(
        DocoptExit,
        match=r"Warning: found unmatched \(duplicate\?\) arguments"
        r".*-f.*-o.*-o.*--bar.*--spam.*eggs",
    ):
        docopt("usage: prog [options]", "-foo --bar --spam=eggs")
    #    assert docopt('usage: prog [options]', '-foo --bar --spam=eggs',
    #                  any_options=True) == {'-f': True, '-o': 2,
    #                                         '--bar': True, '--spam': 'eggs'}
    with raises(
        DocoptExit,
        match=r"Warning: found unmatched \(duplicate\?\) arguments"
        r".*--foo.*--bar.*--bar",
    ):
        docopt("usage: prog [options]", "--foo --bar --bar")
    #    assert docopt('usage: prog [options]', '--foo --bar --bar',
    #                  any_options=True) == {'--foo': True, '--bar': 2}
    with raises(
        DocoptExit,
        match=r"Warning: found unmatched \(duplicate\?\) arguments"
        r".*--bar.*--bar.*--bar.*-f.*-f.*-f.*-f",
    ):
        docopt("usage: prog [options]", "--bar --bar --bar -ffff")
    #    assert docopt('usage: prog [options]', '--bar --bar --bar -ffff',
    #                  any_options=True) == {'--bar': 3, '-f': 4}
    with raises(
        DocoptExit,
        match=r"Warning: found unmatched \(duplicate\?\) arguments"
        r".*--long.*arg.*--long.*another",
    ):
        docopt("usage: prog [options]", "--long=arg --long=another")


#    assert docopt('usage: prog [options]', '--long=arg --long=another',
#                  any_options=True) == {'--long': ['arg', 'another']}


# def test_options_shortcut_multiple_commands():
#    # any_options is disabled
#    assert docopt('usage: prog c1 [options] prog c2 [options]',
#        'c2 -o', any_options=True) == {'-o': True, 'c1': False, 'c2': True}
#    assert docopt('usage: prog c1 [options] prog c2 [options]',
#        'c1 -o', any_options=True) == {'-o': True, 'c1': True, 'c2': False}


def test_default_value_for_positional_arguments():
    doc = """Usage: prog [--data=<data>...]\n
             Options:\n\t-d --data=<arg>    Input data [default: x]
          """
    a = docopt(doc, "")
    assert a == {"--data": ["x"]}
    doc = """Usage: prog [--data=<data>...]\n
             Options:\n\t-d --data=<arg>    Input data [default: x y]
          """
    a = docopt(doc, "")
    assert a == {"--data": ["x", "y"]}
    doc = """Usage: prog [--data=<data>...]\n
             Options:\n\t-d --data=<arg>    Input data [default: x y]
          """
    a = docopt(doc, "--data=this")
    assert a == {"--data": ["this"]}


def test_issue_59():
    assert docopt("usage: prog --long=<a>", "--long=") == {"--long": ""}
    assert docopt("usage: prog -l <a>\n" "options: -l <a>", ["-l", ""]) == {"-l": ""}


def test_options_first():
    assert docopt("usage: prog [--opt] [<args>...]", "--opt this that") == {
        "--opt": True,
        "<args>": ["this", "that"],
    }
    assert docopt("usage: prog [--opt] [<args>...]", "this that --opt") == {
        "--opt": True,
        "<args>": ["this", "that"],
    }
    assert docopt(
        "usage: prog [--opt] [<args>...]", "this that --opt", options_first=True
    ) == {"--opt": False, "<args>": ["this", "that", "--opt"]}


def test_issue_68_options_shortcut_does_not_include_options_in_usage_pattern():
    args = docopt("usage: prog [-ab] [options]\n" "options: -x\n -y", "-ax")
    # Need to use `is` (not `==`) since we want to make sure
    # that they are not 1/0, but strictly True/False:
    assert args["-a"] is True
    assert args["-b"] is False
    assert args["-x"] is True
    assert args["-y"] is False


def test_issue_65_evaluate_argv_when_called_not_when_imported():
    import sys

    sys.argv = "prog -a".split()
    assert docopt("usage: prog [-ab]") == {"-a": True, "-b": False}
    sys.argv = "prog -b".split()
    assert docopt("usage: prog [-ab]") == {"-a": False, "-b": True}


def test_issue_71_double_dash_is_not_a_valid_option_argument():
    with raises(DocoptExit, match=r"--log requires argument"):
        docopt("usage: prog [--log=LEVEL] [--] <args>...", "--log -- 1 2")
    with raises(DocoptExit, match=r"-l requires argument"):
        docopt("usage: prog [-l LEVEL] [--] <args>...\noptions: -l LEVEL", "-l -- 1 2")


option_examples: Sequence[tuple[str, Sequence[Option]]] = [
    ("", []),
    ("Some content\nbefore the first option.", []),
    ("-f", [Option("-f", None, 0, False)]),
    ("-f  Description.", [Option("-f", None, 0, False)]),
    ("-f ARG  Description.", [Option("-f", None, 1, None)]),
    ("-f ARG  Description. [default: 42]", [Option("-f", None, 1, "42")]),
    ("--foo", [Option(None, "--foo", 0, False)]),
    ("--foo  Description.", [Option(None, "--foo", 0, False)]),
    ("--foo ARG  Description.", [Option(None, "--foo", 1, None)]),
    ("--foo ARG  Description. [default: 42]", [Option(None, "--foo", 1, "42")]),
    # Options can wrap over multiple lines
    (
        """\
         \t --foo ARG, -f ARG  With a long

         wrapped description
           \t [default: 42]
         """,
        [Option("-f", "--foo", 1, "42")],
    ),
    # Options can start after whitespace
    (
        "\t--foo=<arg>  [default: bar]",
        [Option(None, "--foo", 1, "bar")],
    ),
    (
        " \t -f ARG, --foo ARG  Description. [default: 42]",
        [Option("-f", "--foo", 1, "42")],
    ),
    # Options can start on the same line as an "options:" heading
    (
        "options:-f ARG, --foo ARG  Description. [default: 42]",
        [Option("-f", "--foo", 1, "42")],
    ),
    (
        "  Special oPtioNs:  --foo ARG  Description. [default: 42]",
        [Option(None, "--foo", 1, "42")],
    ),
    (
        "  other options: --foo ARG  Description. [default: 42]",
        [Option(None, "--foo", 1, "42")],
    ),
    (
        """\
        -a  This is the first option

            -b=<x>  Options don't have to be in an options section

        Options:
            -c, --charlie  This describes the option.
            --delta, -d
                This option has the desc on another line.

        --echo   This option starts after a blank line.

            -f --foxtrot   This option has no comma

        Other Options:
            -g VAL     This option is after another section heading.
                       [default: gval]
        options:-h  This option is on the same line as a heading
        oPtioNs:--india
              oPtIons:  -j X

                        [default: jval]
            and more Options:  --k X  [default: kval]
        """,
        [
            Option("-a", None, 0, False),
            Option("-b", None, 1, None),
            Option("-c", "--charlie", 0, False),
            Option("-d", "--delta", 0, False),
            Option(None, "--echo", 0, False),
            Option("-f", "--foxtrot", 0, False),
            Option("-g", None, 1, "gval"),
            Option("-h", None, 0, False),
            Option(None, "--india", 0, False),
            Option("-j", None, 1, "jval"),
            Option(None, "--k", 1, "kval"),
        ],
    ),
    # Option with description (or other content) on following line.
    (
        """
        Options:
            -a
            -b
         description of b
            -c
        Other Options:
            -d
        Other Options:-e
        """,
        [
            Option("-a", None, 0, False),
            Option("-b", None, 0, False),
            Option("-c", None, 0, False),
            Option("-d", None, 0, False),
            Option("-e", None, 0, False),
        ],
    ),
    # Option-like things which aren't actually options
    (
        """
        --option1 <x>  This really is an option.
                       And it has a default [default: 42]

        Talking about options:
            Here we're talking about options and defaults, like [default: 3] and
            options such as --foo, but we're not intending to define them. And
            although the default of 3 I just mentioned does not get picked up as
            the default of --option1, defined above.

            But if we happen to start a line of our prose with an option, like
            -b then we are unfortunately defining an option. And "then" acts as
            an argument for -b, so it accepts an argument.

            Options are also allowed to start on the same line as an option
            heading, so this is an option:
            options: --option2

            And this also works after several words, so options: --option3  is
            also an option. But options after other heading-like things aren't
            picked up, so this isn't an option:
            things: --not-an-option

        -o, --option4 <x>  This is also a real option
        """,
        [
            Option(None, "--option1", 1, "42"),
            Option("-b", None, 1, None),
            Option(None, "--option2", 0, False),
            Option(None, "--option3", 0, False),
            Option("-o", "--option4", 1, None),
        ],
    ),
]
option_examples = [(dedent(doc), options) for (doc, options) in option_examples]


@pytest.mark.parametrize("descriptions, options", option_examples)
def test_parse_options(descriptions, options):
    assert parse_options(descriptions) == options


@pytest.mark.parametrize(
    "before",
    [
        pytest.param("", id="empty"),
        pytest.param("This is a prog\n", id="1line"),
        pytest.param(
            "This is a prog\n\nInfo:\n Blah blah\n\n"
            # contains usage: but not a usage section
            "Ingredients in pork sausage:\nBlah blah\n",
            id="preceding_sections",
        ),
    ],
)
@pytest.mark.parametrize(
    "header",
    [
        pytest.param("usage:", id="simple"),
        pytest.param("uSaGe:", id="odd_case"),
        pytest.param("My Program's Usage:", id="long"),
        pytest.param("  Indented Usage:", id="indented"),
    ],
)
@pytest.mark.parametrize(
    "body",
    [
        pytest.param("prog [options]", id="simple"),
        pytest.param(" prog [options]", id="space_simple"),
        pytest.param("\tprog [options]", id="tab_simple"),
        pytest.param(" \t prog [options]", id="WS_simple"),
        pytest.param("\n prog [options]", id="LF_simple"),
        pytest.param("\n prog [options]\n", id="LF_simple_LF"),
        pytest.param("prog [options] cmd1\n prog [options] cmd2\n", id="multiple_LF"),
        pytest.param("\n prog [options] cmd1\n prog [options] cmd2", id="LF_multiple"),
        pytest.param(
            "\n prog [options] cmd1\n prog [options] cmd2\n", id="LF_multiple_LF"
        ),
        pytest.param(
            """\
 prog [options] cmd1
   [--foo --bar]
   [--baz --boz]
 prog [options] cmd2
""",
            id="wrapped_arguments",
        ),
    ],
)
@pytest.mark.parametrize(
    "after",
    [
        pytest.param("", id="empty"),
        pytest.param("This can be\nany content.\n", id="text"),
        pytest.param("Options: -a  All", id="single_line"),
    ],
)
def test_parse_docstring_sections(before: str, header: str, body: str, after: str):
    if after and not body.endswith("\n"):
        body = body + "\n"
    assert parse_docstring_sections(before + header + body + after) == (
        (before, header, body, after)
    )


@pytest.mark.parametrize(
    "invalid_docstring",
    [
        pytest.param("", id="empty"),
        pytest.param(
            """\
            This doc has no usage heading

                myprog [options]

            Options:
                --foo
                --bar
            """,
            id="no_usage_heading",
        ),
    ],
)
def test_parse_docstring_sections__reports_invalid_docstrings(invalid_docstring: str):
    with pytest.raises(
        DocoptLanguageError,
        match=re.escape(
            'Failed to parse doc: "usage:" section (case-insensitive) not found'
        ),
    ):
        parse_docstring_sections(dedent(invalid_docstring))


@pytest.mark.parametrize(
    "doc, error_message",
    [
        pytest.param(
            """\
            My prog.

            Usage:
                myprog [options]
                Options:
                    --foo
                    --bar
            """,
            'Failed to parse docstring: "options:" (case-insensitive) was '
            'found in "usage:" section.',
            id="options_in_usage",
        ),
        pytest.param(
            """\
            My prog.

            Usage:
                myprog [options]

            More Usage:
                Blah blah.
            """,
            'Failed to parse docstring: More than one "usage:" '
            "(case-insensitive) section found.",
            id="multiple_usage_sections",
        ),
        pytest.param(
            """\
            This docstring has nothing in its usage.

            Usage:""",
            'Failed to parse docstring: "usage:" section is empty.',
            id="empty_usage_section",
        ),
        pytest.param(
            """\
            This docstring has only whitespace in its usage.

            Usage:

            Options:""",
            'Failed to parse docstring: "usage:" section is empty.',
            id="whitespace_usage_section",
        ),
    ],
)
def test_lint_docstring(doc: str, error_message: str):
    doc_sections = parse_docstring_sections(dedent(doc))
    with pytest.raises(DocoptLanguageError, match=re.escape(error_message)):
        lint_docstring(doc_sections)
