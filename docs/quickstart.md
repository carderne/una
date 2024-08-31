# Quickstart
This will give you a quick view of how this all works.

First install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

And start your workspace:
```bash
uv init unarepo   # choose another name if you prefer
cd unarepo
git init
uv add --dev una
```

Then setup the Una workspace. This will generate a structure and an example lib and app.
```bash
uv run una create workspace
rm -rf src
uv sync
```

Have a look at what's been generated:
```bash
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
# project.dependencies and tool.uv.sources in the each pyproject.toml
uv run una sync
```

Have a look at what happened:
```bash
tail apps/printer/pyproject.toml
```

It added `greeter` as an internal dependency to `printer`.
It didn't add `cowsay-python`, as transitive external dependencies are only resolved at build-time.

Now you can build your app. Note that you **must** specify the `--wheel` parameter. Una doesn't currently work for builds that do source -> sdist -> wheel, as these break some things with uv virtual envs.
```bash
uvx --from build pyproject-build --installer=uv \
    --outdir=dist --wheel apps/printer
# this will inject the cowsay-python external dependency
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
