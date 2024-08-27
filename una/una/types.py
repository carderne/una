from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, TypeAlias, TypeVar

import tomlkit
from dataclasses_json import dataclass_json

Json: TypeAlias = dict[str, "Json"] | list["Json"] | str | int | float | bool | None
Imports: TypeAlias = dict[str, set[str]]


@dataclass(frozen=True)
class ExtDep:
    name: str
    version: str


@dataclass(frozen=True)
class IntDep:
    name: str
    version: str = ""


@dataclass(frozen=False)
class PackageDeps:
    name: str
    path: Path
    ext_deps: list[ExtDep]
    int_deps: list[IntDep]


@dataclass(frozen=True)
class CheckDiff:
    package: PackageDeps
    int_dep_imports: Imports
    ext_dep_imports: Imports
    int_dep_diff: set[str]
    ext_dep_diff: set[str]


def _rename_keys(old: str, new: str) -> Callable[[Json], None]:
    def rename(d: Json) -> None:
        if isinstance(d, dict):
            for k, v in list(d.items()):
                rename(v)
                if old in k:
                    d[k.replace(old, new)] = d.pop(k)

    return rename


@dataclass_json
@dataclass(frozen=True)
class Project:
    name: str = ""
    dependencies: list[str] = field(default_factory=list)
    version: str | None = None
    requires_python: str = ">= 3.8"


def _default_members() -> list[str]:
    return ["libs/*", "apps/*"]


@dataclass_json
@dataclass(frozen=True)
class UvWorkspace:
    members: list[str] = field(default_factory=_default_members)


@dataclass_json
@dataclass(frozen=True)
class UvSourceIsWorkspace:
    workspace: bool = False


@dataclass_json
@dataclass(frozen=True)
class Uv:
    workspace: UvWorkspace = field(default_factory=UvWorkspace)
    sources: dict[str, UvSourceIsWorkspace] = field(default_factory=dict)


@dataclass_json
@dataclass(frozen=True)
class Una:
    namespace: str | None = None
    requires_python: str | None = None


@dataclass_json
@dataclass(frozen=False)
class Tool:
    uv: Uv = field(default_factory=Uv)
    una: Una = field(default_factory=Una)


Self = TypeVar("Self", bound="Conf")


@dataclass_json
@dataclass()
class Conf:
    """
    Conf object.

    Should never be created manually, only loaded from a toml file.
    See the caveats on `to_str()`.
    """

    tool: Tool
    project: Project = field(default_factory=Project)
    _tomldoc: tomlkit.TOMLDocument | None = field(default=None)

    if TYPE_CHECKING:
        # these are just here becaue dataclass_json doesn't
        # seem to play well with pyright?
        @classmethod
        def from_dict(cls: type[Self], _: Json) -> Self:
            raise

    @classmethod
    def from_tomldoc(cls: type[Self], tomldoc: tomlkit.TOMLDocument) -> Self:
        orig = deepcopy(tomldoc)
        _rename_keys("-", "_")(tomldoc)
        res = cls.from_dict(tomldoc)
        res._tomldoc = orig
        return res

    def to_tomldoc(self) -> tomlkit.TOMLDocument:
        tomldoc = self._tomldoc
        if not tomldoc:
            raise ValueError("This Conf has no _tomldoc member. This should not happen")

        # impossible for project.dependencies to be unset as validated on load
        orig_deps: list[str] = tomldoc["project"]["dependencies"]  # type: ignore[reportIndexIssues]
        new_deps = set(self.project.dependencies) - set(orig_deps)
        for dep in new_deps:
            tomldoc["project"]["dependencies"].add_line(dep)  # type: ignore[reportIndexIssues]

        # deal with a a non-existent tool.una.deps
        try:
            tomldoc["tool"]["uv"]["sources"].update(self.tool.uv.sources)  # type: ignore[reportIndexIssues]
        except KeyError:
            una = tomlkit.table(True)
            deps = tomlkit.table()
            deps.update(self.tool.una.deps)  # type: ignore[reportUnknownMemberType]
            una.append("deps", deps)
            tomldoc["tool"].append("una", una)  # type: ignore[reportIndexIssues]
        return tomldoc

    @classmethod
    def from_str(cls: type[Self], s: str) -> Self:
        tomldoc = tomlkit.loads(s)
        return cls.from_tomldoc(tomldoc)

    def to_str(self) -> str:
        """
        Dump the config to a string.

        To preserve the original formatting and make my life easy, this function
        will currently only modify the following fields:
        - project.dependencies
        - tool.uv.sources
        - tool.hatch.build.hooks.una-build
        - tool.hatch.meta.hooks.una-meta

        All others will be written from the original toml file.
        """
        tomldoc = self.to_tomldoc()
        return tomlkit.dumps(tomldoc)  # type: ignore[reportUnknownMemberType]


@dataclass(frozen=True)
class ConfWrapper:
    conf: Conf
    path: Path
