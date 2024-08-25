from pathlib import Path
from typing import Annotated

from rich.console import Console
from typer import Argument, Exit, Option, Typer

from una import check, config, defaults, files, package_deps, sync
from una.types import CheckDiff

app = Typer(name="una", no_args_is_help=True, add_completion=False)
create = Typer(no_args_is_help=True)
app.add_typer(
    create,
    name="create",
    help="Commands for creating workspace and packages.",
)


@app.command("sync")
def sync_command(
    check_only: Annotated[bool, Option(help="Only check, make no changes")] = False,
    quiet: Annotated[bool, Option(help="Do not output any messages.")] = False,
    alias: Annotated[
        str, Option(help="alias for third-party libraries, map install to import name")
    ] = "",
):
    """Update pyproject.toml with missing int_deps."""
    root = config.get_workspace_root()
    ns = config.get_ns(root)
    alias_list = alias.split(",") if alias else []

    packages = package_deps.get_packages(root, ns)
    diffs: list[CheckDiff] = []
    for p in packages:
        diff = check.check_package_deps(root, ns, p, alias_list)
        diffs.append(diff)

    if check_only:
        failed = any(d.int_dep_diff or d.ext_dep_diff for d in diffs)
        if failed:
            for d in diffs:
                check.print_check_results(d)
            raise Exit(code=1)

    else:
        for d in diffs:
            sync.sync_package_int_deps(d, ns, quiet)


@create.command("package")
def create_package_command(
    name: Annotated[str, Argument(help="Name of the package.")],
    path: Annotated[str, Argument(help="Where to place the package.")],
):
    """Creates an Una package."""
    root = config.get_workspace_root()
    files.create_package(root, name, path, "", "", "")
    console = Console(theme=defaults.RICH_THEME)
    console.print("Success!")
    console.print(f"Created package {name}")


@create.command("workspace")
def create_workspace_command():
    """Creates an Una workspace in the current directory."""
    path = Path.cwd()
    root = config.get_workspace_root()
    ns = config.get_ns(root)
    files.create_workspace(path, ns)
    console = Console(theme=defaults.RICH_THEME)
    console.print("Success!")
    console.print("Set up workspace in current directory.")
    console.print("Remember to delete the src/ directory")
