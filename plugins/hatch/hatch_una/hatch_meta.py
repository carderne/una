from pathlib import Path
from typing import Any

from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.plugin import hookimpl

from hatch_una import util


class UnaMetaHook(MetadataHookInterface):
    """
    Inject needed third-party dependencies into project.dependencies.
    """

    PLUGIN_NAME = "una-meta"

    def update(self, metadata: dict[str, Any]) -> None:
        print("una: Injecting transitive external dependencies")

        # load the config for this package
        path = Path(self.root)
        ext_deps, int_deps = util.get_dependencies(path)

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
            dep_deps, _ = util.get_dependencies(use_path)
            dep_deps = [d.strip().replace(" ", "") for d in dep_deps]
            add_deps.extend(dep_deps)

        metadata["dependencies"] = list(set(ext_deps + add_deps))


@hookimpl
def hatch_register_metadata_hook() -> type[UnaMetaHook]:
    return UnaMetaHook
