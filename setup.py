from setuptools import setup

from docopt import __version__


setup(
    name="docopt-ng",
    version=__version__,
    maintainer="itdaniher",
    maintainer_email="itdaniher@gmail.com",
    description="Humane command line arguments parser. Now with maintenance, typehints, and complete test coverage.",
    license="MIT",
    keywords="option arguments parsing optparse argparse getopt docopt docopt-ng",
    url="https://github.com/jazzband/docopt-ng",
    package_data={"docopt": ["py.typed"]},
    packages=["docopt"],
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
)
