import tomllib
from pathlib import Path
from typing import Any

from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.plugin import hookimpl


def load_conf(path: Path) -> dict[str, Any]:
    with (path / "pyproject.toml").open("rb") as fp:
        return tomllib.load(fp)


class UnaMetaHook(MetadataHookInterface):
    PLUGIN_NAME = "una-meta"

    def update(self, metadata: dict[str, Any]) -> None:
        root = Path(self.root)
        conf = load_conf(root)
        int_deps: dict[str, str] = conf["tool"]["una"]["libs"]

        project_deps: list[str] = metadata.get("dependencies", {})
        project_deps = [d.strip().replace(" ", "") for d in project_deps]

        add_deps: list[str] = []
        for dep_path in int_deps:
            dep_project_path = Path(dep_path).parents[1]
            try:
                dep_conf = load_conf(dep_project_path)
            except FileNotFoundError:
                continue
            dep_deps: list[str] = dep_conf["project"]["dependencies"]
            dep_deps = [d.strip().replace(" ", "") for d in dep_deps]
            add_deps.extend(dep_deps)

        all_deps = list(set(project_deps + add_deps))
        print(all_deps)
        metadata["dependencies"] = all_deps


@hookimpl
def hatch_register_metadata_hook():
    return UnaMetaHook
