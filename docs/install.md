# Installation
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
