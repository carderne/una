# una
**Warning: this is pre-alpha and probably doesn't work at all. You'll probably just get frustrated if you even try to use it.**

una is a tool to make Python monorepos with Rye easier. It is a CLI tool and a Hatch plugin that does the following things:
1. Enable builds of individual apps or projects within a monorepo.
2. Ensure that internal and external dependencies are correctly specified.

una is inspired by [python-polylith](https://github.com/DavidVujic/python-polylith) and is based on that codebase.
But I find the [Polylith](https://polylith.gitbook.io/polylith) architecture to be quite intimidating for many, so wanted to create a lighter touch alternative that doesn't require too much re-thinking. This project has very limited ambitions and doesn't try to do everything a proper build system such as [Bazel](https://bazel.build/) or [Pants](https://www.pantsbuild.org/) does.
It just tries to make a simple monorepo build just about possible.

una allows two directory structures or styles:
- `packages`: this is the lightest-touch approach, that is just some extra build help on top of a Rye workspace.
- `modules`: a more novel approach with just a single pyproject.toml, arguably better DevX and doesn't require a Rye workspace.

Within this context, we use the following words frequently:
- `lib`: a module or package that will be imported but not run.
- `app`: a module or package that will be run but never imported.
- `project`: a package with no code but only dependencies (only used in the `modules` style)

## Quickstart
This will give you a quick view of how this all works.
A `packages` style will be used by default, as it is probably more familiar to most.

```bash
rye init unarepo   # choose another name if you prefer
cd unarepo
rye add --dev una
```

Then setup the una workspace. This will generate a structure and an example lib and app.
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

The magic of `una` then comes in to resolve the graph of direct and transitive dependencies, which looks like this:
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
pip install una
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

## License
una is distributed under the terms of the MIT license.
