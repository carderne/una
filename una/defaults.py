from rich.theme import Theme

RICH_THEME = Theme(
    {
        "data": "#999966",
        "proj": "#8A2BE2",
        "lib": "#32CD32",
        "app": "#6495ED",
    }
)

KEEP_FILE = ".keep"
ROOT_FILE = ".git"
PYPROJ_FILE = "pyproject.toml"

libs_dir = "libs"

EXAMPLE_APP_NAME = "printer"
EXAMPLE_LIB_NAME = "greeter"

EXAMPLE_IMPORT = "cowsay-python==1.0.2"

TEMPLATE_PYPROJ = """\
[project]
name = "{name}"
version = "0.1.0"
description = ""
authors = []
dependencies = [{dependencies}]
requires-python = "{python_version}"
dynamic = ["una"]  # needed for hatch-una metadata hook to work

[build-system]
requires = ["hatchling", "hatch-una"]
build-backend = "hatchling.build"

[tool.hatch.metadata]
allow-direct-references = true

[tool.rye]
managed = true
dev-dependencies = []

[tool.hatch.build.hooks.una-build]
[tool.hatch.metadata.hooks.una-meta]

[tool.una.deps]
{internal_deps}
"""

EXAMPLE_INTERNAL_DEPS = """\
"../../libs/{lib_name}/{ns}/{lib_name}" = "{ns}/{lib_name}"
"""

EXAMPLE_APP_CODE = """\
import {ns}.{lib_name} as {lib_name}


def run() -> None:
    print({lib_name}.greet())
"""

EXAMPLE_LIB_CODE = """\
import cowsay


def greet() -> str:
    return cowsay.say("Hello from una!")
"""

TEMPLATE_TEST_CODE = """\
from {ns} import {name}


def test_import():
    assert {name}
"""
