from pathlib import Path

import tomlkit

from una import config, consts

_EXAMPLE_APP_NAME = "printer"
_EXAMPLE_LIB_NAME = "greeter"
_EXAMPLE_MEMBERS = ["apps/*", "libs/*"]
_EXAMPLE_IMPORT = "cowsay-python==1.0.2"

_TEMPLATE_PYPROJ = """\
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

[tool.uv]
dev-dependencies = []

[tool.hatch.build.hooks.una-build]
[tool.hatch.metadata.hooks.una-meta]

[tool.una.deps]
{internal_deps}\
"""

_EXAMPLE_INTERNAL_DEPS = """\
"../../libs/{dep_name}/{ns}/{dep_name}" = "{ns}/{dep_name}"
"""

_EXAMPLE_APP_CODE = """\
from {ns} import {lib_name}


def run() -> None:
    print({lib_name}.greet())
"""

_EXAMPLE_LIB_CODE = """\
import cowsay


def greet() -> str:
    return cowsay.say("Hello from una!")
"""

_TEMPLATE_TEST_CODE = """\
from {ns} import {name}


def test_import():
    assert {name}
"""


def create_workspace(path: Path, ns: str) -> None:
    app_content = _EXAMPLE_APP_CODE.format(ns=ns, lib_name=_EXAMPLE_LIB_NAME)
    lib_content = _EXAMPLE_LIB_CODE

    _update_root_pyproj(path, ns, _EXAMPLE_IMPORT)
    create_package(
        path,
        _EXAMPLE_APP_NAME,
        "apps",
        app_content,
        "",
        _EXAMPLE_INTERNAL_DEPS.format(ns=ns, dep_name=_EXAMPLE_LIB_NAME),
    )
    create_package(
        path,
        _EXAMPLE_LIB_NAME,
        "libs",
        lib_content,
        f'"{_EXAMPLE_IMPORT}"',
        "",
    )


def create_package(
    path: Path,
    name: str,
    top_dir: str,
    content: str,
    dependencies: str,
    internal_deps: str,
) -> None:
    conf = config.load_conf(path)
    python_version = conf.project.requires_python
    ns = config.get_ns(path)

    package_dir = _create_dir(path, f"{top_dir}/{name}")
    ns_dir = _create_dir(path, f"{top_dir}/{name}/{ns}")
    code_dir = _create_dir(path, f"{top_dir}/{name}/{ns}/{name}")
    test_dir = _create_dir(path, f"{top_dir}/{name}/tests")

    _create_file(ns_dir, "py.typed")
    _create_file(code_dir, "__init__.py", content)
    _create_file(code_dir, "py.typed")
    _create_file(
        test_dir,
        f"test_{name}_import.py",
        content=_TEMPLATE_TEST_CODE.format(ns=ns, name=name),
    )
    pyproj_content = _TEMPLATE_PYPROJ.format(
        name=name,
        python_version=python_version,
        dependencies=dependencies,
        internal_deps=internal_deps,
    )
    _create_file(
        package_dir,
        consts.PYPROJ_FILE,
        pyproj_content,
    )


def _create_file(path: Path, name: str, content: str | None = None) -> Path:
    fullpath = path / name
    if content:
        with fullpath.open("w", encoding="utf-8") as f:
            f.write(content)
    else:
        fullpath.touch()
    return fullpath


def _create_dir(path: Path, dir_name: str, keep: bool = False) -> Path:
    d = path / dir_name
    d.mkdir(parents=True)
    if keep:
        _create_file(d, consts.KEEP_FILE)
    return d


def _update_root_pyproj(path: Path, ns: str, dependencies: str) -> None:
    pyproj = path / consts.PYPROJ_FILE
    with pyproj.open() as f:
        toml = tomlkit.parse(f.read())

    toml.pop("project")  # pyright:ignore[reportUnknownMemberType]
    toml.pop("build-system")  # pyright:ignore[reportUnknownMemberType]
    toml["tool"]["uv"]["workspace"] = {"members": _EXAMPLE_MEMBERS}  # pyright:ignore[reportIndexIssue]
    with pyproj.open("w") as f:
        f.write(tomlkit.dumps(toml))  # pyright:ignore[reportUnknownMemberType]
