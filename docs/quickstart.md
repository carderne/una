# Quickstart
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

## Example
After running through the steps above, the result will be similar to the Projects style example repo:
- [una-example-packages](https://github.com/carderne/una-example-packages)
