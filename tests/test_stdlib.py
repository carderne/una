from una import stdlib


def test_stdlib_3_11():
    assert stdlib.py310.difference(stdlib.py311) == {"binhex"}
    assert stdlib.py311.difference(stdlib.py310) == {
        "tomllib",
        "_tkinter",
        "sitecustomize",
        "usercustomize",
    }


def test_stdlib_3_12():
    assert stdlib.py311.difference(stdlib.py312) == {
        "asynchat",
        "asyncore",
        "distutils",
        "imp",
        "smtpd",
    }
    assert stdlib.py312.difference(stdlib.py311) == set()
