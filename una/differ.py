import re
import subprocess
from pathlib import Path

from rich.console import Console
from rich.padding import Padding

from una import config, defaults, internal_deps
from una.types import Proj


def calc_diff(tag_name: str | None, only_int_deps: bool):
    root = config.get_workspace_root()
    tag = get_latest_tag(tag_name)
    if not tag:
        print("No tags found in repository.")
        return

    ns = config.get_ns(root)
    files = get_files(tag)
    apps_paths = get_changed_apps(root, files, ns)
    libs_paths = get_changed_libs(root, files, ns)
    projects = get_changed_projects(files)
    all_projects_data = internal_deps.get_int_deps_in_projects(root, libs_paths, apps_paths, ns)
    projects_data = [p for p in all_projects_data]
    if only_int_deps:
        print_detected_changes_in_int_deps(apps_paths, libs_paths)
        return
    print_diff_summary(tag, apps_paths, libs_paths)
    print_detected_changes(projects, "proj")
    print_diff_details(projects_data, apps_paths, libs_paths)


def parse_folder_parts(pattern: str, changed_file: Path) -> str:
    parts = re.split(pattern, changed_file.as_posix())
    remainder = parts[-1]
    file_path = Path(remainder)
    return next(p for p in file_path.parts if p != file_path.root)


def get_changed(pattern: str, changed_files: list[Path]) -> set[str]:
    return {parse_folder_parts(pattern, f) for f in changed_files if re.match(pattern, f.as_posix())}


def parse_path_pattern(_: Path, top_dir: str, namespace: str) -> str:
    return f"{top_dir}/{namespace}/"


def get_changed_int_deps(root: Path, top_dir: str, changed_files: list[Path], namespace: str) -> list[str]:
    pattern = parse_path_pattern(root, top_dir, namespace)
    return sorted(get_changed(pattern, changed_files))


def get_changed_libs(root: Path, changed_files: list[Path], namespace: str) -> list[str]:
    return get_changed_int_deps(root, defaults.libs_dir, changed_files, namespace)


def get_changed_apps(root: Path, changed_files: list[Path], namespace: str) -> list[str]:
    return get_changed_int_deps(root, defaults.apps_dir, changed_files, namespace)


def get_changed_projects(changed_files: list[Path]) -> list[str]:
    res = get_changed(defaults.apps_dir, changed_files)
    filtered = {p for p in res if p != defaults.apps_dir}
    return sorted(filtered)


def get_latest_tag(key: str | None) -> str | None:
    tag_pattern = config.get_tag_pattern(key)
    sorting_options = [f"--sort={option}" for option in config.get_tag_sort_options()]
    res = subprocess.run(
        ["git", "tag", "-l"] + sorting_options + [f"{tag_pattern}"],
        capture_output=True,
    )
    return next((tag for tag in res.stdout.decode("utf-8").split()), None)


def get_files(tag: str) -> list[Path]:
    res = subprocess.run(
        ["git", "diff", tag, "--stat", "--name-only"],
        capture_output=True,
    )
    return [Path(p) for p in res.stdout.decode("utf-8").split()]


def print_diff_details(projects_data: list[Proj], apps: list[str], libs: list[str]) -> None:
    if not apps and not libs:
        return
    console = Console(theme=defaults.una_theme)
    table = internal_deps.build_int_deps_in_projects_table(projects_data, apps, libs, for_info=False)
    console.print(table, overflow="ellipsis")


def print_detected_changes(changes: list[str], markup: str) -> None:
    if not changes:
        return
    console = Console(theme=defaults.una_theme)
    for int_dep in changes:
        console.print(f"[data]:gear: Changes found in [/][{markup}]{int_dep}[/]")


def print_detected_changes_in_int_deps(apps: list[str], libs: list[str]) -> None:
    sorted_apps = sorted(apps)
    sorted_libs = sorted(libs)
    print_detected_changes(sorted_libs, "lib")
    print_detected_changes(sorted_apps, "app")


def print_diff_summary(tag: str, apps: list[str], libs: list[str]) -> None:
    console = Console(theme=defaults.una_theme)
    console.print(Padding(f"[data]Diff: based on the {tag} tag[/]", (1, 0, 1, 0)))
    if not apps and not libs:
        console.print("[data]No int_dep changes found.[/]")
        return
    if libs:
        console.print(f"[lib]Changed libs[/]: [data]{len(libs)}[/]")
    if apps:
        console.print(f"[app]Changed apps[/]: [data]{len(apps)}[/]")
