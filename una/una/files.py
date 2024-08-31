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
requires-python = "{requires_python}"
dynamic = ["una"]  # needed for hatch-una metadata hook to work

[build-system]
requires = ["hatchling", "hatch-una"]
build-backend = "hatchling.build"

[tool.hatch.metadata]
allow-direct-references = true

[tool.uv]
dev-dependencies = []

[tool.uv.sources]
{sources}

[tool.hatch.build.hooks.una-build]
[tool.hatch.metadata.hooks.una-meta]\
"""

_EXAMPLE_INTERNAL_DEPS = """{dep_name} = {{ workspace = true }}"""

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


def create_workspace(path: Path) -> None:
    ns = _update_root_pyproj(path, _EXAMPLE_IMPORT)

    app_content = _EXAMPLE_APP_CODE.format(ns=ns, lib_name=_EXAMPLE_LIB_NAME)
    app_deps = _EXAMPLE_INTERNAL_DEPS.format(dep_name=_EXAMPLE_LIB_NAME)
    lib_content = _EXAMPLE_LIB_CODE
    create_package(
        path,
        ns,
        _EXAMPLE_APP_NAME,
        "apps",
        app_content,
        f'"{_EXAMPLE_LIB_NAME}"',
        app_deps,
    )
    create_package(
        path,
        ns,
        _EXAMPLE_LIB_NAME,
        "libs",
        lib_content,
        f'"{_EXAMPLE_IMPORT}"',
        "",
    )


def create_package(
    path: Path,
    ns: str,
    name: str,
    top_dir: str,
    content: str,
    dependencies: str,
    internal_deps: str,
) -> None:
    conf = config.load_conf(path)
    requires_python = conf.tool.una.requires_python or ">= 3.11"

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
        requires_python=requires_python,
        dependencies=dependencies,
        sources=internal_deps,
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


def _update_root_pyproj(path: Path, dependencies: str) -> str:
    pyproj = path / consts.PYPROJ_FILE
    with pyproj.open() as f:
        toml = tomlkit.parse(f.read())

    ns: str = toml["project"]["name"]  # pyright:ignore[reportIndexIssue,reportAssignmentType]
    requires_python: str = toml["project"]["requires-python"]  # pyright:ignore[reportIndexIssue,reportAssignmentType]
    toml["tool"]["uv"].add("package", False)  # pyright:ignore[reportUnknownMemberType]
    toml["tool"]["uv"]["workspace"] = {"members": _EXAMPLE_MEMBERS}  # pyright:ignore[reportIndexIssue]
    toml["tool"]["una"] = {"namespace": ns, "requires-python": requires_python}  # pyright:ignore[reportIndexIssue]
    with pyproj.open("w") as f:
        f.write(tomlkit.dumps(toml))  # pyright:ignore[reportUnknownMemberType]
    return ns
