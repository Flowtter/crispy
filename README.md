# Setup pre-commit
First install `pre-commit` by running:
```sh
pip install pre-commit
```

Then to install the git hook run:
```sh
pre-commit install -t pre-commit -t commit-msg
```

Now `pre-commit` will run on every `git commit`.
