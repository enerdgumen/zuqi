# Requirements

* [pipenv](https://github.com/pypa/pipenv)
* Python 3.8

# Configuration

The service is configured via environment variables, see `.env.example`.

# Development

Run:
```
PYTHONPATH=. pipenv run python conductor/server.py
```

Test:
```
PYTHONPATH=. pipenv run pytest
```
