__doc__ = f"""
Usage: {__file__} [options] [FILE] ...
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

from docopt import magic

magic()

"""
prints:
{'--help': False,
 '--left': False,
 '--quiet': False,
 '--report': False,
 '--right': False,
 '--verbose': False,
 'FILE': [],
 'STEP1': None,
 'STEP2': None}
"""

print(arguments)

"""
prints:
False
"""
print(arguments.left)
