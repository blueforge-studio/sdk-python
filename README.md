# BlueForge Python SDKs

Monorepo of Python client libraries for BlueForge services.

## Packages

| Package | Description |
|---|---|
| [`blueforge-analytics-os`](./packages/analytics-os) | Analytics-os event capture client (stdlib-only, threading + atexit flush). |

## Development

```
pytest                 # run all package tests
cd packages/analytics-os && python -m build
```

## Publishing

PyPI trusted publishing on tag push (`v*.*.*`). Each package has its own
publish workflow under `.github/workflows/`.
```
