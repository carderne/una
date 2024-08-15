# Quickstart
This will give you a quick view of how this all works.
A `packages` style will be used by default, as it is probably more familiar to most.

```bash
rye init my_example
cd my_example
rye add --dev una

# this will create a bunch of folders and files, have a look at them!
rye run una create workspace

# why not have a look
tree
```

The let's create some internal and external dependencies:
```bash
# add an external library to example_lib
cd libs/example_lib
rye add urllib3
cd ../..

# and then depend on example_lib from example_app
echo "import my_example.example_lib" > apps/example_app/my_example/example_app/foo.py
```

But then how do we ensure that builds of example_app will include all of the required code and dependencies?
```bash
# this checks all imports and ensures they are added to
# [tool.una.libs] in the appropriate pyproject.toml
rye run una sync

# have a look at what happened
tail apps/example_app/pyproject.toml
```

Now you can build your app:
```bash
rye build --package example_app

# and see the result
ls dist/
```

And you can do whatever you want with that wheel!
What about stick it in a Dockerfile, have you ever seen such a simple one?
```Dockerfile
FROM python
COPY dist dist
RUN pip install dist/*.whl
```
