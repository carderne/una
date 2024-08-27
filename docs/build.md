# Build

At build-time, Una itself does nothing.
This is when `hatch-una`, the plugin for [Hatch](https://hatch.pypa.io/) steps in and resolves the graph of dependencies.

Assuming your `pyproject.toml` is correctly configured, and your `[tool.una.deps]` section includes all necessary dependencies (_and_ transitive dependencies!),
then `hatch-una` will inject all the needed internal dependencies (other stuff in your monorepo) and external dependencies (stuff from PyPI) into your build.

So all you need to do is run something like:
```bash
uvx --from build pyproject-build --installer uv apps/printer
```

You'll get some `*.whl` files, which you can then deploy with Docker or whatever you prefer.
They are fully self-contained, so you don't need uv/Hatch or Una or anything else wherever you want to install them.
