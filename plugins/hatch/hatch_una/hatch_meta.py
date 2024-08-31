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
        print("una-meta: Injecting transitive external dependencies")

        path = Path(self.root)
        ext_deps, int_deps = util.get_dependencies(path)

        via_sdist = Path("PKG-INFO").exists()
        if via_sdist:
            raise ValueError("Una doesn't work for wheels built from sdist")

        members: list[str] = util.get_members()

        add_deps: list[str] = []
        for dep_name in int_deps:
            dep_path = util.find_package_dir(dep_name, members)

            # load all third-party dependencies from this internal dependency into the
            # project.dependencies table
            dep_deps, _ = util.get_dependencies(dep_path)
            dep_deps = [d.strip().replace(" ", "") for d in dep_deps]
            add_deps.extend(dep_deps)

        metadata["dependencies"] = list(set(ext_deps + add_deps))


@hookimpl
def hatch_register_metadata_hook() -> type[UnaMetaHook]:
    return UnaMetaHook
