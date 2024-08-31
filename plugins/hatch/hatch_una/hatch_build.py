from pathlib import Path
from typing import Any

from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.builders.sdist import SdistBuilder
from hatchling.plugin import hookimpl

from hatch_una import util


class UnaBuildHook(BuildHookInterface[BuilderConfig]):
    """
    Force-include all needed internal monorepo dependencies.
    """

    PLUGIN_NAME = "una-build"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        via_sdist = Path("PKG-INFO").exists()
        if via_sdist:
            raise ValueError("Una doesn't work for wheels built from sdist")

        print("una-build: Injecting internal dependencies")

        # load the config for this package
        path = Path(self.root)
        root = util.get_workspace_root()
        root_conf = util.load_conf(root)
        members: list[str] = (
            root_conf.get("tool", {}).get("uv", {}).get("workspace", {}).get("members", [])  # pyright:ignore[reportAny]
        )
        _, int_deps = util.get_dependencies(path)

        if not int_deps:
            # this is fine, the package doesn't import anything internally
            return

        add_dep_files: dict[str, str] = {}
        package_dirs = [util.find_package_dir(d, members) for d in int_deps]
        for package_dir in package_dirs:
            finder = SdistBuilder(str(package_dir))
            files = [Path(f.path) for f in finder.recurse_selected_project_files()]
            for f in files:
                add_dep_files[str(f)] = str(f.relative_to(package_dir))

        build_data["force_include"] = {
            **build_data["force_include"],
            **add_dep_files,
        }


@hookimpl
def hatch_register_build_hook() -> type[UnaBuildHook]:
    return UnaBuildHook
