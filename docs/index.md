# Una

<div align="center">
  <img src="assets/logo.svg" width="100">
  <p>Easy monorepos with Python and uv</p>
</div>

----
<div align="center">

<a href="https://pypi.org/project/una/">
<img alt="pypi" src="https://img.shields.io/pypi/v/una.svg?logo=pypi&label=PyPI&logoColor=gold">
</a>
<a href="https://una.rdrn.me/">
<img alt="docs" src="https://img.shields.io/badge/Docs-gray?logo=materialformkdocs&logoColor=white">
</a>
<a href="https://github.com/carderne/una">
<img alt="GitHub" src="https://img.shields.io/badge/GitHub-una-blue?logo=github">
</a>

</div>

**Una is currently a bit broken since uv v0.4.0. Figuring out what to do next.**

Una is a tool to build and productionise Python monorepos with [uv](https://docs.astral.sh/uv/).

uv has [Workspaces](https://docs.astral.sh/uv/concepts/workspaces/), but no ability to _build_ them.
This means if you have dependencies between packages in your workspace, there's no good way to distribute or productionise the end result.

Una solves this.
No additional configuration is needed: if you have a functional uv Workspace, just add Una.
It consists of the following two things:

1. A CLI to ensure that all imports are correctly specified as dependencies.
2. A build plugin that enables production builds of individual apps within a monorepo by injecting local dependencies and transitive third-party dependencies.

Una doesn't try to replicate a full build system such as [Bazel](https://bazel.build/) or
[Pants](https://www.pantsbuild.org/).
It just makes it possible to have a simple monorepo with interdependencies.

Una works much like a Rust workspace, with each package having its own pyproject.toml.
In general, packages should either be libraries (imported but not run) or apps (run but never imported), but Una will not enforce this.

It only works with the [Hatch](https://hatch.pypa.io) build backend.

## Examples
You can see an example repo here:

- [una-example](https://github.com/carderne/una-example)
