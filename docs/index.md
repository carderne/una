# Una

<div align="center">
  <img src="assets/logo.svg" width="100">
  <p>Easy monorepos with Python</p>
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

Una is a tool to make Python monorepos with Rye easier. It is a CLI tool and a build plugin that does the following things:

1. Enable builds of individual apps or projects within a monorepo.
2. Ensure that internal and external dependencies are correctly specified.

Una is inspired by [python-polylith](https://github.com/DavidVujic/python-polylith) and borrows extensively from that codebase.
But I find the [Polylith](https://polylith.gitbook.io/polylith) architecture to be quite intimidating for many, so wanted to create a lighter touch alternative that doesn't require too much re-thinking.
This project has very limited ambitions and doesn't try to do everything a proper build system such as [Bazel](https://bazel.build/) or [Pants](https://www.pantsbuild.org/) does.
It just tries to make a simple monorepo build just about possible.

Una allows two directory structures or styles:
- `packages`: this is the default style, that is just some extra build help on top of a Rye workspace.
- `modules`: a more novel approach with just a single pyproject.toml, arguably better DevX and doesn't require a Rye workspace.

Within this context, we use the following words frequently:

- `lib`: a module or package that will be imported but not run.
- `app`: a module or package that will be run but never imported.
- `project`: a package with no code but only dependencies (only used in the `modules` style)

Currently it works with the following build backends, but more will follow:

- [Hatch](https://hatch.pypa.io) (used by default and and in all documentation)
- [PDM](https://pdm-project.org/)

## Examples
You can see examples for each of the two styles here:

- [una-example-packages](https://github.com/carderne/una-example-packages)
- [una-example-modules](https://github.com/carderne/una-example-modules)
