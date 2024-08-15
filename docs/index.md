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
