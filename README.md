# ignore-peek

Check whether repository-relative paths match Git ignore rules. The command is read only: it does not stage, unstage, or modify files.

## Use

Requires Python 3.10+ and Git on `PATH`.

```sh
python ignore_peek.py build/output.log .env --repo .
```

Tracked paths are checked against ignore rules too, which can help explain why a path would be ignored if it were untracked. Pathnames are JSON-quoted in the output so control characters cannot create extra terminal lines. At most 100 paths of 4,096 characters each are accepted.

Exit status is `0` when all paths are ignored, `1` when at least one is not ignored, and `2` when the repository or Git command cannot be used.

## License

MIT
