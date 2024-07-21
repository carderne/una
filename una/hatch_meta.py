from typing import Any

from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.plugin import hookimpl

from una import config


class UnaMetaHook(MetadataHookInterface):
    PLUGIN_NAME = "una-meta"

    def update(self, metadata: dict[str, Any]) -> None:
        root = self.root
        conf = config.load_conf(root)
        int_deps = conf.tool.una.libs

        project_deps: list[str] = metadata.get("dependencies", {})
        project_deps = [d.strip().replace(" ", "") for d in project_deps]

        add_deps: list[str] = []
        for dep_path in int_deps:
            dep_conf = config.load_conf(dep_path)
            dep_deps = dep_conf.project.dependencies
            dep_deps = [d.strip().replace(" ", "") for d in dep_deps]
            add_deps.extend(dep_deps)

        all_deps = list(set(project_deps + add_deps))
        metadata["dependencies"] = all_deps


@hookimpl
def hatch_register_metadata_hook():
    return UnaMetaHook
