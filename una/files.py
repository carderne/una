from pathlib import Path

import tomlkit

from una import config, defaults


def create_workspace(path: Path, ns: str) -> None:
    app_content = defaults.EXAMPLE_APP_CODE.format(ns=ns, lib_name=defaults.EXAMPLE_LIB_NAME)
    lib_content = defaults.EXAMPLE_LIB_CODE

    _update_root_pyproj(path, ns, defaults.EXAMPLE_IMPORT)
    create_package(
        path,
        defaults.EXAMPLE_APP_NAME,
        "apps",
        app_content,
        "",
        defaults.EXAMPLE_INTERNAL_DEPS,
    )
    create_package(
        path,
        defaults.EXAMPLE_LIB_NAME,
        "libs",
        lib_content,
        f'"{defaults.EXAMPLE_IMPORT}"',
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
        content=defaults.TEMPLATE_TEST_CODE.format(ns=ns, name=name),
    )
    pyproj_content = defaults.TEMPLATE_PYPROJ.format(
        name=name,
        python_version=python_version,
        dependencies=dependencies,
        internal_deps=internal_deps,
    )
    _create_file(
        package_dir,
        defaults.PYPROJ_FILE,
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
        _create_file(d, defaults.KEEP_FILE)
    return d


def _update_root_pyproj(path: Path, ns: str, dependencies: str) -> None:
    pyproj = path / defaults.PYPROJ_FILE
    with pyproj.open() as f:
        toml = tomlkit.parse(f.read())

    toml["tool"]["rye"]["virtual"] = True  # type:ignore[reportIndexIssues]
    toml["tool"]["rye"]["workspace"] = {"member": defaults.EXAMPLE_MEMBERS}  # type:ignore[reportIndexIssues]
    toml["tool"]["una"] = {"members": defaults.EXAMPLE_MEMBERS}  # type:ignore[reportIndexIssues]
    with pyproj.open("w") as f:
        f.write(tomlkit.dumps(toml))  # type:ignore[reportUnknownMemberType]
