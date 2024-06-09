# Hooks

The idea is to setup a pre-compmit hook that will run Python's tools flake8 and black against the source code.

The pre-commit is available in the file `pre-commit.hook`.

You'll first need to setup a Python virtual environment:

```bash
> python3 -m venv venv
```

To test the hook, make some changes to a Python file in the `src/` dir and try to commit them.

https://git-scm.com/docs/githooks
