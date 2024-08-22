# Una

<div align="center">
  <img src="https://raw.githubusercontent.com/carderne/una/main/docs/assets/logo.svg" alt="Una logo" width="100" role="img">
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

Una is a tool to make Python monorepos easier. It is a CLI tool and a build plugin that does the following things:

1. Enable builds of individual apps or projects within a monorepo.
2. Ensure that internal and external dependencies are correctly specified.

Una doesn't try to replicate a full build system such as [Bazel](https://bazel.build/) or [Pants](https://www.pantsbuild.org/). It just makes it possible to have a simple monorepo with interdependencies.

Una allows two directory structures or styles:

- **Packages:** The default style, where each lib or app is a package with its own pyproject.toml (much like Rust's workspaces).
- **Modules**: A more novel approach with just a single pyproject.toml, inspired by [python-polylith](https://github.com/DavidVujic/python-polylith).

Within this context, we use the following words frequently:

- `lib`: a module or package that will be imported but not run.
- `app`: a module or package that will be run but never imported.
- `project`: a package with no code but only dependencies (only used in the Modules style).

Currently it works with the following build backends, but more will follow:

- [Hatch](https://hatch.pypa.io) (used by default and and in all documentation)
- [PDM](https://pdm-project.org/)

All instructions and examples use Rye for local development, but there is nothing inherently Rye-specific about the tool.

## Examples
You can see examples for each of the two styles here:

- [una-example-packages](https://github.com/carderne/una-example-packages)
- [una-example-modules](https://github.com/carderne/una-example-modules)

## Quickstart
This will give you a quick view of how this all works.
A `packages` style will be used by default, as it is probably more familiar to most.

```bash
rye init unarepo   # choose another name if you prefer
cd unarepo
rye add --dev una
```

Then setup the Una workspace. This will generate a structure and an example lib and app.
```
rye run una create workspace
rye sync
```

Have a look at what's been generated:
```
tree
```

Have a look at the generated `__init__.py` files in the `apps/printer` and `libs/greeter` packages.
An external dependency ([cowsay-python](https://pypi.org/project/cowsay-python/)) has also been added to the latter's `pyproject.toml`.

The magic of Una then comes in to resolve the graph of direct and transitive dependencies, which looks like this:
```elm
printer --> greeter --> cowsay-python
```

You can do this by running the following:
```bash
# this checks all imports and ensures they are added to
# [tool.una.libs] in the appropriate pyproject.toml
rye run una sync
```

Have a look at what happened:
```bash
tail apps/printer/pyproject.toml
```

It added `greeter` as an internal dependency to `printer`.
It didn't add `cowsay-python`, as external dependencies are only resolved at build-time (keep reading).

Now you can build your app:
```bash
rye build --package printer
# this will inject the cowsay-python externel dependency
```

And see the result:
```bash
ls dist/
```

And you can do whatever you want with that wheel!
What about stick it in a Dockerfile, have you ever seen such a simple one?
```Dockerfile
FROM python
COPY dist dist
RUN pip install dist/*.whl
```

And run it:
```bash
docker build --tag unarepo-printer .
docker run --rm -it unarepo-printer python -c 'from unarepo.printer import run; run()'
```

## Installation
The CLI tool isn't strictly necessary, as all the stuff that lets the monorepo builds work is in the separate (and tiny) [hatch-una](plugins/hatch) package.
But you will likely struggle to manage your monorepo without the tool!

So you may as well install it:
```bash
rye add --dev una
```

As for the build-time `hatch-una`, it will automatically be installed by build tools when it spots this in your `pyproject.toml` (this will be configured automatically by the CLI):
```toml
[build-system]
requires = ["hatchling", "hatch-una"]
build-backend = "hatchling.build"
```

## Usage
The CLI has a few commands and options, have a look:
```bash
rye run una --help

 Usage: una [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                             │
╰─────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────╮
│ create   Commands for creating a workspace, apps, libs and projects.    │
│ diff     Shows changed int_deps compared to the latest git tag.         │
│ info     Info about the Una workspace.                                  │
│ sync     Update pyproject.toml with missing int_deps.                   │
╰─────────────────────────────────────────────────────────────────────────╯
```

## Documentation

Read more at [the official documentation](https://una.rdrn.me/).

It covers additional things like:
- [type-checking](https://una.rdrn.me/types-tests/), testing, editor integration
- more detail on the [packages](https://una.rdrn.me/style-packages/) vs [modules](https://una.rdrn.me/style-modules/) styles
- and more!

## Contributing
See the instructions at the [official documentation](https://una.rdrn.me/contributing/).

Very briefly, local development is with Rye:
```bash
rye sync
rye run all  # will fmt, lint, typecheck and test
```

Then open a PR.

## License
Una is distributed under the terms of the MIT license.
Significant parts of the code are from the [python-polylith](https://github.com/DavidVujic/python-polylith) project (c) 2022 David Vujic
