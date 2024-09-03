from pathlib import Path
from typing import Annotated

from rich.console import Console
from rich.theme import Theme
from typer import Argument, Exit, Option, Typer

from una import check, config, files, package_deps, sync
from una.types import CheckDiff

app = Typer(name="una", no_args_is_help=True, add_completion=False)
create = Typer(no_args_is_help=True)
app.add_typer(
    create,
    name="create",
    help="Commands for creating workspace and packages.",
)


def rich_console() -> Console:
    theme = Theme({"pkg": "#8A2BE2", "dep": "#32CD32"})
    return Console(theme=theme)


@app.command("sync")
def sync_command(
    check_only: Annotated[bool, Option(help="Only check, make no changes")] = False,
    quiet: Annotated[bool, Option(help="Do not output any messages.")] = False,
    alias: Annotated[
        str, Option(help="alias for third-party libraries, map install to import name")
    ] = "",
):
    """Update packages with missing dependencies."""
    console = rich_console()
    root = config.get_workspace_root()
    ns = config.get_ns(root)
    alias_list = alias.split(",") if alias else []

    packages = package_deps.get_packages(root)
    diffs: list[CheckDiff] = []
    for p in packages:
        d = check.check_package_deps(root, ns, p, alias_list)
        diffs.append(d)

    if check_only:
        for d in diffs:
            if d.ext_dep_diff:
                missing = ", ".join(sorted(d.ext_dep_diff))
                console.print(f"[pkg]{d.package.name}[/] can't find external: [dep]{missing}[/]")
            if d.int_dep_diff:
                missing = ", ".join(sorted(d.int_dep_diff))
                console.print(f"[pkg]{d.package.name}[/] can't find internal: [dep]{missing}[/]")

        if any(d.int_dep_diff or d.ext_dep_diff for d in diffs):
            raise Exit(code=1)
        raise Exit()

    for d in diffs:
        sync.sync_package(d)
        if not quiet:
            for c in d.int_dep_diff:
                console.print(f"[pkg]{d.package.name}[/] adding dep [dep]{c}[/]")

    if not quiet:
        console.print("All good!")


@create.command("package")
def create_package_command(
    name: Annotated[str, Argument(help="Name of the package.")],
    path: Annotated[str, Argument(help="Where to place the package.")],
):
    """Creates an Una package."""
    console = rich_console()
    root = config.get_workspace_root()
    ns = config.get_ns(root)
    files.create_package(root, ns, name, path, "", "", "")
    console.print("Success!")
    console.print(f"Created package {name}")


@create.command("workspace")
def create_workspace_command():
    """Creates an Una workspace in the current directory."""
    console = rich_console()
    path = Path.cwd()
    files.create_workspace(path)
    console.print("Success!")
    console.print("Set up workspace in current directory.")
