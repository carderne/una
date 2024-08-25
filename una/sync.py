from pathlib import Path

from rich.console import Console

from una import defaults
from una.config import load_conf
from una.types import CheckDiff, Conf, Include, PackageDeps


def sync_package_int_deps(diff: CheckDiff, ns: str, quiet: bool):
    _update_package(ns, diff)
    if not quiet:
        _print_summary(diff)
        _print_int_dep_imports(diff)


def _print_int_dep_imports(diff: CheckDiff) -> None:
    console = Console(theme=defaults.RICH_THEME)
    for key, values in diff.int_dep_imports.items():
        imports_in_int_dep = values.difference({key})
        if not imports_in_int_dep:
            continue
        joined = ", ".join(imports_in_int_dep)
        message = f":information: [dat]{key}[/] is importing [dat]{joined}[/]"
        console.print(message)


def _print_summary(diff: CheckDiff) -> None:
    console = Console(theme=defaults.RICH_THEME)
    name = diff.package.name
    for c in diff.int_dep_diff:
        console.print(f"adding dep [dep]{c}[/] to [pkg]{name}[/]")


def _to_package(orig_pkg: PackageDeps, ns: str, name: str) -> Include:
    int_dep_roots = [f for f in orig_pkg.int_deps if f.name == name]
    if len(int_dep_roots) != 1:
        raise ValueError("WTF?")
    root = int_dep_roots[0].path
    src = root / name / ns / name
    dst = Path(ns) / name
    return Include(src=str(src), dst=str(dst))


def _generate_updated_package(conf: Conf, packages: list[Include]) -> str | None:
    for inc in packages:
        conf.tool.una.deps[inc.src] = inc.dst
    return conf.to_str()


def _to_packages(ns: str, diff: CheckDiff) -> list[Include]:
    return [_to_package(diff.package, ns, c) for c in diff.int_dep_diff]


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
