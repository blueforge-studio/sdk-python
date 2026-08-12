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

PyPI trusted publishing on tag push matching the package's release pattern (e.g. `analytics-os-v*.*.*`). Each package has its own publish workflow under `.github/workflows/`.

## Releasing a package

1. Bump version in `packages/<pkg>/pyproject.toml`.
2. Tag: `git tag analytics-os-v0.1.0 && git push --tags`.
3. The publish workflow builds and uploads to PyPI via trusted publishing.
