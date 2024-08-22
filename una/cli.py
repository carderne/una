from pathlib import Path
from typing import Annotated

from rich.console import Console
from typer import Argument, Exit, Option, Typer

from una import check, config, defaults, external_deps, files, internal_deps, sync
from una.types import Options, Style

app = Typer(name="una", no_args_is_help=True, add_completion=False)
create = Typer(no_args_is_help=True)
app.add_typer(
    create,
    name="create",
    help="Commands for creating a workspace, apps, libs and projects.",
)

option_alias = Option(help="alias for third-party libraries, map install to import name")  # type: ignore[reportAny]
option_verbose = Option(help="More verbose output.")  # type: ignore[reportAny]
option_quiet = Option(help="Do not output any messages.")  # type: ignore[reportAny]


@app.command("info")
def info_command(
    alias: Annotated[str, option_alias] = "",
):
    """Info about the Una workspace."""
    root = config.get_workspace_root()
    ns = config.get_ns(root)
    options = Options(alias=str.split(alias, ",") if alias else [])

    internal_deps.int_deps_from_projects(root, ns)

    internal_deps.int_cross_deps(root, ns)

    # Deps on external libraries
    projects = internal_deps.get_projects_data(root, ns)
    filtered_projects = internal_deps.filtered_projects_data(projects)
    merged_projects_data = check.enriched_with_lock_files_data(filtered_projects, False)
    results = external_deps.external_deps_from_all(root, ns, merged_projects_data, options)
    external_deps.print_libs_in_projects(filtered_projects, options)
    if not all(results):
        raise Exit(code=1)


@app.command("sync")
def sync_command(
    check_only: Annotated[bool, Option(help="Only check, make no changes")] = False,
    quiet: Annotated[bool, option_quiet] = False,
    verbose: Annotated[bool, option_verbose] = False,
    alias: Annotated[str, option_alias] = "",
):
    """Update pyproject.toml with missing int_deps."""
    root = config.get_workspace_root()
    ns = config.get_ns(root)
    options = Options(
        quiet=quiet,
        verbose=verbose,
        alias=str.split(alias, ",") if alias else [],
    )

    if not check_only:
        projects = internal_deps.get_projects_data(root, ns)
        filtered_projects = internal_deps.filtered_projects_data(projects)
        enriched_projects = check.enriched_with_lock_files_data(filtered_projects, verbose)
        for p in filtered_projects:
            sync.sync_project_int_deps(root, ns, p, options)
            config.clear_conf_cache()

    # reload projects so any changes made by sync are picked up
    projects = internal_deps.get_projects_data(root, ns)
    filtered_projects = internal_deps.filtered_projects_data(projects)
    enriched_projects = check.enriched_with_lock_files_data(filtered_projects, verbose)
    results = {check.check_int_ext_deps(root, ns, p, options) for p in enriched_projects}
    if not all(results):
        raise Exit(code=1)


@create.command("lib")
def lib_command(
    name: Annotated[str, Argument(help="Name of the lib.")],
):
    """Creates an Una lib."""
    root = config.get_workspace_root()
    style = config.get_style(root)
    if style == Style.packages:
        files.create_package(root, defaults.example_lib, defaults.libs_dir, "", "")
    else:
        files.create_module(root, defaults.example_lib, defaults.libs_dir, "")
    console = Console(theme=defaults.una_theme)
    console.print("Success!")
    console.print(f"Created lib {name}")


@create.command("app")
def app_command(
    name: Annotated[str, Argument(help="Name of the app.")],
):
    """Creates an Una app."""
    root = config.get_workspace_root()
    style = config.get_style(root)
    if style == Style.packages:
        files.create_package(root, defaults.example_app, defaults.apps_dir, "", "")
    else:
        files.create_module(root, defaults.example_app, defaults.apps_dir, "")
    console = Console(theme=defaults.una_theme)
    console.print("Success!")
    console.print(f"Created app {name}")


@create.command("project")
def project_command(
    name: Annotated[str, Argument(help="Name of the projectlib.")],
    from_app: Annotated[str, Argument(help="Name of the app the project will use.")],
):
    """Creates an Una project."""
    root = config.get_workspace_root()
    style = config.get_style(root)
    console = Console(theme=defaults.una_theme)
    if style == Style.packages:
        console.print("You can't create projects in a Packages style workspace")
        raise Exit(code=1)

    files.create_project(root, name, "", from_app)
    console.print("Success!")
    console.print(f"Created project {name}")


@create.command("workspace")
def workspace_command(
    style: Annotated[Style, Option(help="Workspace style")] = "packages",  # type:ignore[reportArgumentType]
):
    """Creates an Una workspace in the current directory."""
    path = Path.cwd()
    root = config.get_workspace_root()
    ns = config.get_ns(root)
    files.create_workspace(path, ns, style)
    console = Console(theme=defaults.una_theme)
    console.print("Success!")
    console.print("Set up workspace in current directory.")
    console.print("Remember to delete the src/ directory")
