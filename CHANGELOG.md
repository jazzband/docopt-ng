# CHANGELOG

## Version 0.7.2:

-   Complete MyPy typehints - ZERO errors.
    Required refactoring class implementations, adding typing stubs, but not changing tests. :)
-   100% code coverage. Required the addition of a few tests.
    Removed unused codepaths. Tagged typing stubs `pragma: no cover` as they are definitionally exercised.

## Version 0.7.1:

-   Add `magic()` and `magic_docopt()` aliases for `docopt()` allowing easier use of new features.

## Version 0.7.0:

-   "MORE MAGIC"
-   First argument is now optional - `docopt()` will look for `__doc__` defined in parent scopes.
-   Dot access is supported on resulting `arguments` object,
    ignoring angle brackets and leading dashes.
-   `more_magic` parameter added to `docopt()` defaults False.
-   If `more_magic` enabled, `arguments` variable created and populated
    in calling scope with results.
-   If `more_magic` enabled, fuzzy (levenshtein) autocorrect enabled for long-args.
-   Lots of typehints.
-   README moved to Markdown.

## Version 0.6.3:

-   Catch up on \~two years of pull requests.
-   Fork [docopt](https://github.com/docopt/docopt) to
    [docopt-ng](https://github.com/bazaar-projects/docopt-ng).
-   Add levenshtein based autocorrect from
    [string-dist](https://github.com/obulkin/string-dist).
-   Add better debug / error messages.
-   Linting (via [black](https://github.com/ambv/black) and
    [flake8](https://gitlab.com/pycqa/flake8)).

## Version 0.6.2:

-   Bugfixes

## Version 0.6.1:

-   Fix issue [\#85](https://github.com/docopt/docopt/issues/85) which
    caused improper handling of `[options]` shortcut if it was present
    several times.

## Version 0.6.0:

-   New argument `options_first`, disallows interspersing options and
    arguments. If you supply `options_first=True` to `docopt`, it will
    interpret all arguments as positional arguments after first
    positional argument.
-   If option with argument could be repeated, its default value will
    be interpreted as space-separated list. E.g. with
    `[default: ./here ./there]` will be interpreted as
    `['./here', './there']`.