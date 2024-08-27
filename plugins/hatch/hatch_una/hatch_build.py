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
        print("una: Injecting internal dependencies")

        # load the config for this package
        path = Path(self.root)
        conf = util.load_conf(path)
        members: list[str] = (
            conf.get("tool", {}).get("uv", {}).get("workspace", {}).get("members", [])  # pyright:ignore[reportAny]
        )
        _, int_deps = util.get_dependencies(path)

        if not int_deps:
            # this is fine, the package doesn't import anything internally
            return

        via_sdist = Path("PKG-INFO").exists()
        if via_sdist:
            # nothing to do as everything should already be included in sdist...
            return

        add_dep_files: dict[str, str] = {}
        for d in int_deps:
            package_dir = util.find_package_dir(d, members)
            finder = SdistBuilder(str(package_dir))
            files = [Path(f.path) for f in finder.recurse_selected_project_files()]
            for f in files:
                add_dep_files[str(f)] = str(f.relative_to(package_dir))

        # make sure all int_deps exist
        found = [Path(k) for k in int_deps if (path / k).exists()]
        missing = set(int_deps) - set(str(p) for p in found)
        if len(missing) > 0:
            missing_str = ", ".join(missing)
            raise ValueError(f"Could not find these paths: {missing_str}")

        add_packages_pyproj = {
            str(f.parents[1] / util.PYPROJ): str(util.EXTRA_PYPROJ / f.name / util.PYPROJ)
            for f in found
        }

        build_data["force_include"] = {
            **build_data["force_include"],
            **add_dep_files,
            **add_packages_pyproj,
        }


@hookimpl
def hatch_register_build_hook() -> type[UnaBuildHook]:
    return UnaBuildHook
