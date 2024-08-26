from pathlib import Path
from typing import Any

from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
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
        name: str = conf["project"]["name"]

        try:
            int_deps: dict[str, str] = conf["tool"]["una"]["deps"]
        except KeyError as e:
            raise KeyError(
                f"Package '{name}' is missing '[tool.una.deps]' in pyproject.toml"
            ) from e

        if not int_deps:
            # this is fine, the package doesn't import anything internally
            return

        via_sdist = Path("PKG-INFO").exists()
        if via_sdist:
            # nothing to do as everything should already be included in sdist...
            return

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
            **int_deps,
            **add_packages_pyproj,
        }


@hookimpl
def hatch_register_build_hook() -> type[UnaBuildHook]:
    return UnaBuildHook
