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

packages_pyproj = """
[project]
name = "{name}"
version = "0.1.0"
description = ""
authors = []
dependencies = []
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

test_template = """\
from {ns} import {name}
def test_import():
    assert {name}
"""
