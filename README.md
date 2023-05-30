# **docopt-ng** creates *beautiful* command-line interfaces

[![Test](https://github.com/jazzband/docopt-ng/actions/workflows/test.yml/badge.svg?event=push)](https://github.com/jazzband/docopt-ng/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/jazzband/docopt-ng/branch/master/graph/badge.svg)](https://codecov.io/gh/jazzband/docopt-ng)
[![image](https://img.shields.io/pypi/v/docopt-ng.svg)](https://pypi.python.org/pypi/docopt-ng)
[![Jazzband](https://jazzband.co/static/img/badge.svg)](https://jazzband.co/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**docopt-ng** is a fork of the [original docopt](https://github.com/docopt/docopt), now maintained by the
[jazzband](https://jazzband.co/) project. Now with maintenance, typehints, and complete test coverage!

**docopt-ng** helps you create beautiful command-line interfaces:

```python
"""Naval Fate.

Usage:
  naval_fate.py ship new <name>...
  naval_fate.py ship <name> move <x> <y> [--speed=<kn>]
  naval_fate.py ship shoot <x> <y>
  naval_fate.py mine (set|remove) <x> <y> [--moored | --drifting]
  naval_fate.py (-h | --help)
  naval_fate.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Moored (anchored) mine.
  --drifting    Drifting mine.

"""
from docopt import docopt

if __name__ == "__main__":
    argv = ["ship", "Guardian", "move", "100", "150", "--speed=15"]
    arguments = docopt(__doc__, argv)
    print(arguments)
```

results in:

```python
{'--drifting': False,
 '--help': False,
 '--moored': False,
 '--speed': '15',
 '--version': False,
 '<name>': ['Guardian'],
 '<x>': '100',
 '<y>': '150',
 'mine': False,
 'move': True,
 'new': False,
 'remove': False,
 'set': False,
 'ship': True,
 'shoot': False}
```

Beat that! The option parser is generated based on the docstring above
that is passed to `docopt` function. `docopt` parses the usage pattern
(`"Usage: ..."`) and option descriptions (lines starting with dash
"`-`") and ensures that the program invocation matches the usage
pattern; it parses options, arguments and commands based on that. The
basic idea is that *a good help message has all necessary information in
it to make a parser*.

Also, [PEP 257](http://www.python.org/dev/peps/pep-0257/) recommends
putting help message in the module docstrings.

# Installation

Use [pip](http://pip-installer.org):

    python -m pip install docopt-ng

**docopt-ng** is tested with Python 3.7+.

# API

```python
def docopt(
    docstring: str,
    argv: list[str] | str | None = None,
    default_help: bool = True,
    version: Any = None,
    options_first: bool = False,
) -> ParsedOptions:
```

`docopt` takes a docstring, and 4 optional arguments:

-   `docstring` is a string that contains a **help message** that will be
    used to create the option parser.
    The simple rules of how to write such a help message
    are given in next sections. Typically you would just use `__doc__`.

-   `argv` is an optional argument vector; by default `docopt` uses the
    argument vector passed to your program (`sys.argv[1:]`).
    Alternatively you can supply a list of strings like
    `["--verbose", "-o", "hai.txt"]`, or a single string that will be split
    on spaces like `"--verbose -o hai.txt"`.

-   `default_help`, by default `True`, specifies whether the parser should
    automatically print the help message (supplied as `doc`) and
    terminate, in case `-h` or `--help` option is encountered (options
    should exist in usage pattern, more on that below). If you want to
    handle `-h` or `--help` options manually (as other options), set
    `help=False`.

-   `version`, by default `None`, is an optional argument that specifies
    the version of your program. If supplied, then, (assuming
    `--version` option is mentioned in usage pattern) when parser
    encounters the `--version` option, it will print the supplied
    version and terminate. `version` could be any printable object, but
    most likely a string, e.g. `"2.1.0rc1"`.

    > Note, when `docopt` is set to automatically handle `-h`, `--help`
    > and `--version` options, you still need to mention them in usage
    > pattern for this to work. Also, for your users to know about them.

-   `options_first`, by default `False`. If set to `True` will disallow
    mixing options and positional argument. I.e. after first positional
    argument, all arguments will be interpreted as positional even if
    the look like options. This can be used for strict compatibility
    with POSIX, or if you want to dispatch your arguments to other
    programs.

The **return** value is a simple dictionary with options, arguments and
commands as keys, spelled exactly like in your help message. Long
versions of options are given priority. Furthermore, dot notation is
supported, with preceeding dashes (`-`) and surrounding brackets (`<>`)
ignored, for example `arguments.drifting` or `arguments.x`.

# Help message format

Help message consists of 2 parts:

-   Usage pattern, e.g.:

        Usage: my_program.py [-hso FILE] [--quiet | --verbose] [INPUT ...]

-   Option descriptions, e.g.:

        -h --help    show this
        -s --sorted  sorted output
        -o FILE      specify output file [default: ./test.txt]
        --quiet      print less text
        --verbose    print more text

Their format is described below; other text is ignored.

## Usage pattern format

**Usage pattern** is a substring of `doc` that starts with `usage:`
(case *insensitive*) and ends with a *visibly* empty line. Minimum
example:

```python
"""Usage: my_program.py

"""
```

The first word after `usage:` is interpreted as your program's name. You
can specify your program's name several times to signify several
exclusive patterns:

```python
"""Usage: my_program.py FILE
          my_program.py COUNT FILE

"""
```

Each pattern can consist of the following elements:

-   **&lt;arguments&gt;**, **ARGUMENTS**. Arguments are specified as
    either upper-case words, e.g. `my_program.py CONTENT-PATH` or words
    surrounded by angular brackets: `my_program.py <content-path>`.
-   **--options**. Options are words started with dash (`-`), e.g.
    `--output`, `-o`. You can "stack" several of one-letter options,
    e.g. `-oiv` which will be the same as `-o -i -v`. The options can
    have arguments, e.g. `--input=FILE` or `-i FILE` or even `-iFILE`.
    However it is important that you specify option descriptions if you
    want your option to have an argument, a default value, or specify
    synonymous short/long versions of the option (see next section on
    option descriptions).
-   **commands** are words that do *not* follow the described above
    conventions of `--options` or `<arguments>` or `ARGUMENTS`, plus two
    special commands: dash "`-`" and double dash "`--`" (see below).

Use the following constructs to specify patterns:

-   **\[ \]** (brackets) **optional** elements. e.g.:
    `my_program.py [-hvqo FILE]`
-   **( )** (parens) **required** elements. All elements that are *not*
    put in **\[ \]** are also required, e.g.:
    `my_program.py --path=<path> <file>...` is the same as
    `my_program.py (--path=<path> <file>...)`. (Note, "required options"
    might be not a good idea for your users).
-   **|** (pipe) **mutually exclusive** elements. Group them using **(
    )** if one of the mutually exclusive elements is required:
    `my_program.py (--clockwise | --counter-clockwise) TIME`. Group them
    using **\[ \]** if none of the mutually-exclusive elements are
    required: `my_program.py [--left | --right]`.
-   **...** (ellipsis) **one or more** elements. To specify that
    arbitrary number of repeating elements could be accepted, use
    ellipsis (`...`), e.g. `my_program.py FILE ...` means one or more
    `FILE`-s are accepted. If you want to accept zero or more elements,
    use brackets, e.g.: `my_program.py [FILE ...]`. Ellipsis works as a
    unary operator on the expression to the left.
-   **\[options\]** (case sensitive) shortcut for any options. You can
    use it if you want to specify that the usage pattern could be
    provided with any options defined below in the option-descriptions
    and do not want to enumerate them all in usage-pattern.
-   "`[--]`". Double dash "`--`" is used by convention to separate
    positional arguments that can be mistaken for options. In order to
    support this convention add "`[--]`" to your usage patterns.
-   "`[-]`". Single dash "`-`" is used by convention to signify that
    `stdin` is used instead of a file. To support this add "`[-]`" to
    your usage patterns. "`-`" acts as a normal command.

If your pattern allows to match argument-less option (a flag) several
times:

    Usage: my_program.py [-v | -vv | -vvv]

then number of occurrences of the option will be counted. I.e.
`args["-v"]` will be `2` if program was invoked as `my_program -vv`.
Same works for commands.

If your usage patterns allows to match same-named option with argument
or positional argument several times, the matched arguments will be
collected into a list:

    Usage: my_program.py <file> <file> --path=<path>...

I.e. invoked with
`my_program.py file1 file2 --path=./here --path=./there` the returned
dict will contain `args["<file>"] == ["file1", "file2"]` and
`args["--path"] == ["./here", "./there"]`.

## Option descriptions format

**Option descriptions** consist of a list of options that you put below
your usage patterns.

It is necessary to list option descriptions in order to specify:

-   synonymous short and long options,
-   if an option has an argument,
-   if option's argument has a default value.

The rules are as follows:

-   Every line in `doc` that starts with `-` or `--` (not counting
    spaces) is treated as an option description, e.g.:

        Options:
          --verbose   # GOOD
          -o FILE     # GOOD
        Other: --bad  # BAD, line does not start with dash "-"

-   To specify that option has an argument, put a word describing that
    argument after space (or equals "`=`" sign) as shown below. Follow
    either &lt;angular-brackets&gt; or UPPER-CASE convention for
    options' arguments. You can use comma if you want to separate
    options. In the example below, both lines are valid, however you are
    recommended to stick to a single style.:

        -o FILE --output=FILE       # without comma, with "=" sign
        -i <file>, --input <file>   # with comma, without "=" sign

-   Use two spaces to separate options with their informal description:

        --verbose More text.   # BAD, will be treated as if verbose option had
                               # an argument "More", so use 2 spaces instead
        -q        Quit.        # GOOD
        -o FILE   Output file. # GOOD
        --stdout  Use stdout.  # GOOD, 2 spaces

-   If you want to set a default value for an option with an argument,
    put it into the option-description, in form
    `[default: <my-default-value>]`:

        --coefficient=K  The K coefficient [default: 2.95]
        --output=FILE    Output file [default: test.txt]
        --directory=DIR  Some directory [default: ./]

-   If the option is not repeatable, the value inside `[default: ...]`
    will be interpreted as string. If it *is* repeatable, it will be
    splited into a list on whitespace:

        Usage: my_program.py [--repeatable=<arg> --repeatable=<arg>]
                             [--another-repeatable=<arg>]...
                             [--not-repeatable=<arg>]

        # will be ["./here", "./there"]
        --repeatable=<arg>          [default: ./here ./there]

        # will be ["./here"]
        --another-repeatable=<arg>  [default: ./here]

        # will be "./here ./there", because it is not repeatable
        --not-repeatable=<arg>      [default: ./here ./there]

# Examples

We have an extensive list of
[examples](https://github.com/jazzband/docopt-ng/tree/master/examples)
which cover every aspect of functionality of **docopt-ng**. Try them
out, read the source if in doubt.

# Development

We would *love* to hear what you think about **docopt-ng** on our
[issues page](https://github.com/jazzband/docopt-ng/issues). Make pull requests, report bugs, and suggest ideas.

To setup your dev environment, fork this repo and clone it locally.
We use [pdm](https://pdm.fming.dev/latest/#installation) to
manage the project, so install that first.

Then install dev requirements and the package itself as editable, then
install the pre-commit hooks:

    pdm sync -d -G dev
    pdm run pre-commit install

Useful testing, linting, and formatting commands:

    pdm run pytest
    pdm run black .
    pdm run ruff .
