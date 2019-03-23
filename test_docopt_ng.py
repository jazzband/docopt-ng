import docopt
from docopt import DocoptExit, DocoptLanguageError, Option, Argument, Command, OptionsShortcut, Required, NotRequired, parse_argv, Tokens
from pytest import raises
from docopt import docopt as magic_docopt


def test_docopt_ng_more_magic_spellcheck_and_expansion():
    o = [Option("-h"), Option("-v", "--verbose"), Option(None, "--file", 1)]
    TS = lambda s: Tokens(s, error=DocoptExit)
    assert parse_argv(TS(""), options=o) == []
    assert parse_argv(TS("-h"), options=o) == [Option("-h", None, 0, True)]
    assert parse_argv(TS("-h --File f.txt"), options=o, more_magic=True) == [Option("-h", None, 0, True), Option(None, "--file", 1, "f.txt")]
    assert parse_argv(TS("-h --fiLe f.txt arg"), options=o, more_magic=True) == [
        Option("-h", None, 0, True),
        Option(None, "--file", 1, "f.txt"),
        Argument(None, "arg"),
    ]
    assert parse_argv(TS("-h -f f.txt arg arg2"), options=o, more_magic=True) == [
        Option("-h", None, 0, True),
        Option(None, "--file", 1, "f.txt"),
        Argument(None, "arg"),
        Argument(None, "arg2"),
    ]

def test_docopt_ng_as_magic_docopt_more_magic_global_arguments_and_dot_access():
    doc = """Usage: prog [-vqr] [FILE]
              prog INPUT OUTPUT
              prog --help

    Options:
      -v  print status messages
      -q  report only file names
      -r  show all occurrences of the same error
      --help

    """
    global arguments
    magic_docopt(doc, "-v file.py")
    assert arguments == {"-v": True, "-q": False, "-r": False, "--help": False, "FILE": "file.py", "INPUT": None, "OUTPUT": None}
    assert arguments.v == True
    assert arguments.FILE == "file.py"

def test_docopt_ng_more_magic_global_arguments_and_dot_access():
    doc = """Usage: prog [-vqr] [FILE]
              prog INPUT OUTPUT
              prog --help

    Options:
      -v  print status messages
      -q  report only file names
      -r  show all occurrences of the same error
      --help

    """
    global arguments
    docopt.docopt(doc, "-v file.py", more_magic=True)
    assert arguments == {"-v": True, "-q": False, "-r": False, "--help": False, "FILE": "file.py", "INPUT": None, "OUTPUT": None}
    assert arguments.v == True
    assert arguments.FILE == "file.py"
    arguments = None
    docopt.docopt(doc.replace("FILE", "<FILE>"), "-v", more_magic=True)
    assert arguments == {"-v": True, "-q": False, "-r": False, "--help": False, "<FILE>": None, "INPUT": None, "OUTPUT": None}
    assert arguments.FILE == None

    with raises(DocoptExit):
        docopt.docopt(doc, "-v input.py output.py")

    with raises(DocoptExit):
        docopt.docopt(doc, "--fake")

def test_docopt_ng__doc__if_no_doc():
    import sys

    __doc__, sys.argv = "usage: prog --long=<a>", [None, "--long="]
    assert docopt.docopt() == {"--long": ""}
    __doc__, sys.argv = "usage:\n\tprog -l <a>\noptions:\n\t-l <a>\n", [None, "-l", ""]
    assert docopt.docopt() == {"-l": ""}
    __doc__, sys.argv = None, [None, "-l", ""]
    with raises(DocoptLanguageError):
        docopt.docopt()

def test_docopt_ng__doc__if_no_doc_indirection():
    import sys
    __doc__, sys.argv = "usage: prog --long=<a>", [None, "--long="]
    def test_indirect():
        return docopt.docopt()
    assert test_indirect() == {"--long": ""}
    def test_even_more_indirect():
        return test_indirect()
    assert test_even_more_indirect() == {"--long": ""}
