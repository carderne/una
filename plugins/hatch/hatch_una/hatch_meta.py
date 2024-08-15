from pathlib import Path
from typing import Any

from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.plugin import hookimpl

from hatch_una import util


class UnaMetaHook(MetadataHookInterface):
    PLUGIN_NAME = "una-meta"

    def update(self, metadata: dict[str, Any]) -> None:
        print("una: Injecting transitive external dependencies")
        root = Path(self.root)
        conf = util.load_conf(root)
        int_deps: dict[str, str] = conf["tool"]["una"]["libs"]

        project_deps: list[str] = metadata.get("dependencies", {})
        project_deps = [d.strip().replace(" ", "") for d in project_deps]

        add_deps: list[str] = []
        for dep_path in int_deps:
            dep_project_path = Path(dep_path).parents[1]
            extra_path = util.EXTRA_PYPROJ / Path(dep_path).name
            if dep_project_path.exists():
                use_path = dep_project_path
            elif extra_path.exists():
                use_path = extra_path
            else:
                # should I raise here?
                continue
            dep_conf = util.load_conf(use_path)
            dep_deps: list[str] = dep_conf["project"]["dependencies"]
            dep_deps = [d.strip().replace(" ", "") for d in dep_deps]
            add_deps.extend(dep_deps)

        metadata["dependencies"] = list(set(project_deps + add_deps))


@hookimpl
def hatch_register_metadata_hook() -> type[UnaMetaHook]:
    return UnaMetaHook
