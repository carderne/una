from pathlib import Path
from typing import Annotated

from rich.console import Console
from typer import Argument, Exit, Option, Typer

from una import check, config, defaults, files, package_deps, sync
from una.types import Options

app = Typer(name="una", no_args_is_help=True, add_completion=False)
create = Typer(no_args_is_help=True)
app.add_typer(
    create,
    name="create",
    help="Commands for creating a workspace and libs.",
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
    options = Options(
        quiet=quiet,
        alias=str.split(alias, ",") if alias else [],
    )

    if not check_only:
        projects = package_deps.get_projects_data(root, ns)
        filtered_projects = package_deps.filtered_projects_data(projects)
        enriched_projects = check.enriched_with_lock_files_data(filtered_projects)
        for p in filtered_projects:
            sync.sync_project_int_deps(root, ns, p, options)
            config.clear_conf_cache()

    # reload projects so any changes made by sync are picked up
    projects = package_deps.get_projects_data(root, ns)
    filtered_projects = package_deps.filtered_projects_data(projects)
    enriched_projects = check.enriched_with_lock_files_data(filtered_projects)
    results = {check.check_int_ext_deps(root, ns, p, options) for p in enriched_projects}
    if not all(results):
        raise Exit(code=1)


@create.command("package")
def create_package_command(
    name: Annotated[str, Argument(help="Name of the package.")],
    path: Annotated[str, Argument(help="Where to place the package.")],
):
    """Creates an Una lib."""
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
