import json
import re
from pathlib import Path
from typing import Generator
from typing import Sequence
from unittest import mock

import pytest

import docopt


def pytest_collect_file(file_path: Path, path, parent):
    if file_path.suffix == ".docopt" and file_path.stem.startswith("test"):
        return DocoptTestFile.from_parent(path=file_path, parent=parent)


def parse_test(raw: str):
    raw = re.compile("#.*$", re.M).sub("", raw).strip()
    if raw.startswith('"""'):
        raw = raw[3:]

    for i, fixture in enumerate(raw.split('r"""')):
        if i == 0:
            if not fixture.strip() == "":
                raise DocoptTestException(
                    f"Unexpected content before first testcase: {fixture}"
                )
            continue

        try:
            doc, _, body = fixture.partition('"""')
            cases = []
            for case in body.split("$")[1:]:
                argv, _, expect = case.strip().partition("\n")
                try:
                    expect = json.loads(expect)
                except json.JSONDecodeError as e:
                    raise DocoptTestException(
                        f"The test case JSON is invalid: {expect!r} - {e}."
                    )
                prog, _, argv = argv.strip().partition(" ")
                cases.append((prog, argv, expect))
            if len(cases) == 0:
                raise DocoptTestException(
                    "No test cases follow the doc. Each example must have at "
                    "least one test case starting with '$'"
                )
        except Exception as e:
            raise DocoptTestException(
                f"Failed to parse test case {i}. {e}\n"
                f'The test\'s definition is:\nr"""{fixture}'
            ) from None
        yield doc, cases


class DocoptTestFile(pytest.File):
    def collect(self):
        raw = self.path.open().read()
        for i, (doc, cases) in enumerate(parse_test(raw), 1):
            name = f"{self.path.stem}({i})"
            for case in cases:
                yield DocoptTestItem.from_parent(
                    name=name, parent=self, doc=doc, case=case
                )


class DocoptTestItem(pytest.Item):
    def __init__(self, name, parent, doc, case):
        super(DocoptTestItem, self).__init__(name, parent)
        self.doc = doc
        self.prog, self.argv, self.expect = case

    def runtest(self):
        try:
            result = docopt.docopt(self.doc, argv=self.argv)
        except docopt.DocoptExit:
            result = "user-error"

        if self.expect != result:
            raise DocoptTestException(self, result)

    def repr_failure(self, excinfo):
        """Called when self.runtest() raises an exception."""
        if isinstance(excinfo.value, DocoptTestException):
            return "\n".join(
                (
                    "usecase execution failed:",
                    self.doc.rstrip(),
                    f"$ {self.prog} {self.argv}",
                    f"result> {json.dumps(excinfo.value.args[1])}",
                    f"expect> {json.dumps(self.expect)}",
                )
            )
        return super().repr_failure(excinfo)

    def reportinfo(self):
        return self.path, 0, f"usecase: {self.name}"


class DocoptTestException(Exception):
    pass


@pytest.fixture(autouse=True)
def override_sys_argv(argv: Sequence[str]) -> Generator[None, None, None]:
    """Patch `sys.argv` with a fixed value during tests.

    A lot of docopt tests call docopt() without specifying argv, which uses
    `sys.argv` by default, so a predictable value for it is necessary.
    """
    with mock.patch("sys.argv", new=argv):
        yield


@pytest.fixture
def argv() -> Sequence[str]:
    """The `sys.argv` value seen inside tests."""
    return ["exampleprogram"]
