from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeAlias, TypeVar

import tomlkit
from dataclasses_json import dataclass_json

Json: TypeAlias = dict[str, "Json"] | list["Json"] | str | int | float | bool | None
Imports: TypeAlias = dict[str, set[str]]
DepKind: TypeAlias = Literal["app", "lib"]


@dataclass
class OrgImports:
    apps: Imports = field(default_factory=dict)
    libs: Imports = field(default_factory=dict)


@dataclass
class Include:
    src: str
    dst: str
    # path: str
    # include: str
    # root: str


@dataclass(frozen=True)
class CheckReport:
    int_dep_imports: OrgImports
    ext_dep_imports: OrgImports
    int_dep_diff: set[str]
    ext_dep_diff: set[str]


@dataclass(frozen=True)
class Diff:
    name: str
    path: Path
    apps: set[str]
    libs: set[str]
    int_dep_imports: OrgImports


@dataclass
class Options:
    quiet: bool = False
    verbose: bool = False
    alias: list[str] = field(default_factory=list)


def rename_keys(old: str, new: str) -> Callable[[Json], None]:
    def rename_hyphens(d: Json) -> None:
        if isinstance(d, dict):
            for k, v in list(d.items()):
                rename_hyphens(v)
                if old in k:
                    d[k.replace(old, new)] = d.pop(k)

    return rename_hyphens


@dataclass_json
@dataclass(frozen=True)
class Project:
    name: str
    dependencies: list[str]
    version: str | None = None
    optional_dependencies: dict[str, list[str]] | None = None
    requires_python: str = ">= 3.8"


class Style(Enum):
    packages = "packages"
    modules = "modules"


@dataclass_json
@dataclass(frozen=True)
class Una:
    style: Style = Style.packages
    libs: dict[str, str] = field(default_factory=dict)


@dataclass_json
@dataclass(frozen=False)
class Tool:
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

    project: Project
    tool: Tool
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
        rename_keys("-", "_")(tomldoc)
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

        # deal with a a non-existent tool.una.libs
        try:
            tomldoc["tool"]["una"]["libs"].update(self.tool.una.libs)  # type: ignore[reportIndexIssues]
        except KeyError:
            una = tomlkit.table(True)
            libs = tomlkit.table()
            libs.update(self.tool.una.libs)  # type: ignore[reportUnknownMemberType]
            una.append("libs", libs)
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
        - tool.una.libs
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


@dataclass(frozen=True)
class ExtDeps:
    source: str
    items: dict[str, str]


@dataclass(frozen=True)
class IntDeps:
    libs: list[str] = field(default_factory=list)
    apps: list[str] = field(default_factory=list)


@dataclass(frozen=False)
class Proj:
    name: str
    packages: list[Include]
    path: Path
    ext_deps: ExtDeps
    int_deps: IntDeps = field(default_factory=IntDeps)
