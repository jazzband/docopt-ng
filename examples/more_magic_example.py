__doc__ = f"""Usage: {__file__} [options] [FILE] ...
       {__file__} (--left | --right) STEP1 STEP2

Process FILE and optionally apply correction to either left-hand side or
right-hand side.

Arguments:
  FILE        optional input file
  STEP1 STEP2 STEP1, STEP2 --left or --right to be present

Options:
  --help
  --verbose      verbose mode
  --quiet        quiet mode
  --report       make report

"""
from docopt import docopt as magic_docopt


if __name__ == "__main__":
    magic_docopt(version=1.9)
    print(arguments)
