from pathlib import Path

from rich.console import Console

from una import defaults
from una.config import load_conf
from una.types import CheckDiff, Conf, Include


def sync_package_int_deps(diff: CheckDiff, ns: str, quiet: bool):
    _update_package(ns, diff)
    if not quiet:
        _print_summary(diff)
        _print_int_dep_imports(diff)


def _print_int_dep_imports(diff: CheckDiff) -> None:
    int_dep_imports = diff.int_dep_imports
    console = Console(theme=defaults.RICH_THEME)
    libs_imports = int_dep_imports.libs
    for key, values in libs_imports.items():
        imports_in_int_dep = values.difference({key})
        if not imports_in_int_dep:
            continue
        joined = ", ".join(imports_in_int_dep)
        message = f":information: [data]{key}[/] is importing [data]{joined}[/]"
        console.print(message)


def _print_summary(diff: CheckDiff) -> None:
    console = Console(theme=defaults.RICH_THEME)
    name = diff.package.name
    libs_pkgs = diff.int_dep_diff
    for c in libs_pkgs:
        console.print(f"adding [lib]{c}[/] lib to [proj]{name}[/]")


def _to_package(ns: str, name: str, int_dep_root: str) -> Include:
    root = Path(int_dep_root)
    src = root / name / ns / name
    dst = Path(ns) / name
    return Include(src=str(src), dst=str(dst))


def _generate_updated_package(conf: Conf, packages: list[Include]) -> str | None:
    for inc in packages:
        conf.tool.una.deps[inc.src] = inc.dst
    return conf.to_str()


def _to_packages(ns: str, diff: CheckDiff) -> list[Include]:
    libs_path = "../../libs"
    return [_to_package(ns, c, libs_path) for c in diff.int_dep_diff]


def _rewrite_package_pyproj(path: Path, packages: list[Include]):
    conf = load_conf(path)
    generated = _generate_updated_package(conf, packages)
    if not generated:
        return
    fullpath = path / defaults.PYPROJ_FILE
    with fullpath.open("w", encoding="utf-8") as f:
        f.write(generated)


def _update_package(ns: str, diff: CheckDiff):
    packages = _to_packages(ns, diff)
    if packages:
        _rewrite_package_pyproj(diff.package.path, packages)
