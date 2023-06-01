import pytest

import docopt
from docopt import DocoptExit
from docopt import _Argument
from docopt import _Option
from docopt import _parse_argv
from docopt import _Tokens


def test_version():
    assert isinstance(docopt.__version__, str)


def test_docopt_ng_more_magic_spellcheck_and_expansion():
    def TS(s):
        return _Tokens(s, error=DocoptExit)

    o = [_Option("-h"), _Option("-v", "--verbose"), _Option(None, "--file", 1)]
    assert _parse_argv(TS(""), options=o) == []
    assert _parse_argv(TS("-h"), options=o) == [_Option("-h", None, 0, True)]
    assert _parse_argv(TS("-V"), options=o, more_magic=True) == [
        _Option("-v", "--verbose", 0, True)
    ]
    assert _parse_argv(TS("-h --File f.txt"), options=o, more_magic=True) == [
        _Option("-h", None, 0, True),
        _Option(None, "--file", 1, "f.txt"),
    ]
    assert _parse_argv(TS("-h --fiLe f.txt arg"), options=o, more_magic=True) == [
        _Option("-h", None, 0, True),
        _Option(None, "--file", 1, "f.txt"),
        _Argument(None, "arg"),
    ]
    assert _parse_argv(TS("-h -f f.txt arg arg2"), options=o, more_magic=True) == [
        _Option("-h", None, 0, True),
        _Option(None, "--file", 1, "f.txt"),
        _Argument(None, "arg"),
        _Argument(None, "arg2"),
    ]


def test_docopt_ng_negative_float():
    args = docopt.docopt(
        "usage: prog --negative_pi=NEGPI NEGTAU", "--negative_pi -3.14 -6.28"
    )
    assert args == {"--negative_pi": "-3.14", "NEGTAU": "-6.28"}


def test_docopt_ng_doubledash_version(capsys: pytest.CaptureFixture):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        docopt.docopt("usage: prog", version=1, argv="prog --version")
    assert capsys.readouterr().out == "1\n"
    assert pytest_wrapped_e.type == SystemExit


def test_docopt_ng_dot_access_with_dash():
    doc = """Usage: prog [-vqrd] [FILE]
              prog INPUT OUTPUT
              prog --help

    Options:
      -d --dash-arg  test this argument
      -v             print status messages
      -q             report only file names
      -r             show all occurrences of the same error
      --help

    """
    arguments = docopt.docopt(doc, "-v -d file.py")
    assert arguments == {
        "--dash-arg": True,
        "-v": True,
        "-q": False,
        "-r": False,
        "--help": False,
        "FILE": "file.py",
        "INPUT": None,
        "OUTPUT": None,
    }
    assert arguments.v
    assert arguments.FILE == "file.py"
    assert arguments.dash_arg
