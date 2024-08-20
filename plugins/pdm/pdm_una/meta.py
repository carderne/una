from pathlib import Path

from pdm.backend.hooks import Context

from pdm_una import util


def add_dependencies(context: Context):
    """
    Inject needed third-party dependencies into project.dependencies.

    This hook is only needed for Packages style una workspaces.
    Modules style should have all dependencies specified in pyproject.toml.
    """
    print("una: Injecting transitive external dependencies")
    metadata = context.config.metadata
    path = context.root

    conf = util.load_conf(path)
    name: str = conf["project"]["name"]

    root_path = path.parents[1]
    style = util.get_workspace_style(root_path)
    if style == "modules":
        # in Hatch, we raise here (should we?)
        # but in PDM the hooks are not configured separately
        # so just return
        return

    try:
        int_deps: dict[str, str] = conf["tool"]["una"]["libs"]
    except KeyError as e:
        raise KeyError(
            f"App/project '{name}' is missing '[tool.una.libs]' in pyproject.toml"
        ) from e

    project_deps: list[str] = metadata.get("dependencies", [])
    project_deps = [d.strip().replace(" ", "") for d in project_deps]

    add_deps: list[str] = []
    for dep_path in int_deps:
        # In builds that do src -> sdist -> wheel, the needed pyproject.toml files
        # will have been copied into the sdist so they're available for the wheel build.
        # Here we check for both in order.
        dep_project_path = Path(dep_path).parents[1]
        extra_path = util.EXTRA_PYPROJ / Path(dep_path).name
        if dep_project_path.exists():
            use_path = dep_project_path
        elif extra_path.exists():
            use_path = extra_path
        else:
            raise ValueError(f"Could not find internal dependency at '{dep_path}'")

        # load all third-party dependencies from this internal dependency into the
        # project.dependencies table
        dep_conf = util.load_conf(use_path)
        try:
            dep_deps: list[str] = dep_conf["project"]["dependencies"]
        except KeyError as e:
            raise KeyError(f"No project.dependcies table for '{use_path}'")
        dep_deps = [d.strip().replace(" ", "") for d in dep_deps]
        add_deps.extend(dep_deps)

    metadata["dependencies"] = list(set(project_deps + add_deps))
