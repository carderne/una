from rich.theme import Theme

una_theme = Theme(
    {
        "data": "#999966",
        "proj": "#8A2BE2",
        "lib": "#32CD32",
        "app": "#6495ED",
    }
)

keep_file_name = ".keep"
lock_file = "requirements.lock"
root_file = ".git"
pyproj = "pyproject.toml"

libs_dir = "libs"
apps_dir = "apps"
proj_dir = "projects"

example_app = "printer"
example_lib = "greeter"

example_import = "cowsay-python==1.0.2"

packages_pyproj = """\
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

[tool.una.libs]
"""

projects_pyproj = """\
[project]
name = "{name}"
version = "0.1.0"
description = ""
authors = []
dependencies = [{dependencies}]
requires-python = "{python_version}"

[build-system]
requires = ["hatchling", "hatch-una"]
build-backend = "hatchling.build"

[tool.hatch.metadata]
allow-direct-references = true

[tool.hatch.build]
packages = ["{ns}"]

[tool.hatch.build.hooks.una-build]

[tool.una.libs]
"""

example_packages_style_app_deps = """\
"../../libs/{lib_name}/{ns}/{lib_name}" = "{ns}/{lib_name}"
"""

example_modules_style_project_deps = """\
"../../apps/{ns}/{app_name}" = "{ns}/{app_name}"
"../../libs/{ns}/{lib_name}" = "{ns}/{lib_name}"
"""

app_template = """\
import {ns}.{lib_name} as {lib_name}


def run() -> None:
    print({lib_name}.greet())
"""

lib_template = """\
import cowsay


def greet() -> str:
    return cowsay.say("Hello from una!")
"""

test_template = """\
from {ns} import {name}


def test_import():
    assert {name}
"""
