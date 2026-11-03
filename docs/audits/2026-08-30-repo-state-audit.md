# sdk-python — Repo State & Release Readiness (2026-08-30)

> Portfolio-sweep audit. Scope: tooling integration, test coverage, CI
> gating, docs freshness, and a maturity verdict for alpha/beta.

**Verdict: ALPHA — release-ready but unreleased.** A small, clean library
whose only real gap is that nobody has pushed the tag.

---

## Snapshot

| Signal | Value |
|---|---|
| Last commit | 2026-08-18 (13 days) — `d2b5097` |
| Branch / dirty | `main`, clean, in sync with `origin` and `gitea` |
| Commits (total) | 8 |
| Source files | **6 Python files, 106 LoC** of library code |
| Unit test files | 2 (7 tests, all passing) |
| E2E test files | 0 (correctly — this is a library) |
| Remotes | `gitea` → forge-git (canonical) + `origin` → GitHub mirror |

Note: an automated file count reports ~855 Python files. That is the
committed-out `.review-venv/` and `packages/analytics-os/.venv/`; real
source is 6 files.

## What it is

Monorepo of Python client libraries for BlueForge services. One package today:

- **`blueforge-analytics-os` v0.1.0** — analytics-os event-capture client.
  Stdlib-only by design (`urllib.request`, `threading`, `atexit`), so it adds
  no dependencies to consumers. `client.py` is 89 LoC; buffer with auto-flush,
  bounded overflow, and retry handling.

Created by Phase 3 of
`blueforge/docs/superpowers/plans/2026-08-11-analytics-os-tier4.md`.

## Tests & CI

7 tests across `test_buffer.py` and `test_client.py`, covering the buffer,
auto-flush, ordered overflow, the retry matrix, concurrent capture, and the
"no fetch on empty flush" case. Verified passing at time of audit
(`7 passed in 2.52s`). For 106 LoC that is proportionate, well-targeted
coverage — no placeholder tests, unlike several sibling repos.

CI is dual-hosted and correctly split:
- `.gitea/workflows/ci.yml` — the Python test matrix, run on the act runner
  via `docker://python-slim` images.
- `.github/workflows/publish-analytics-os.yml` — PyPI trusted publishing,
  which must stay on GitHub for the real OIDC issuer.
- `.github/workflows/python-ci.yml` — pre-Gitea-migration leftover;
  now redundant with the Gitea workflow and a candidate for deletion.

## Audit tooling

**Not applicable and correctly absent.** Screen and story audits target
rendered UI; this is a headless client library with no DOM. Its absence is
not a gap.

## Docs

**Weakest dimension.** README is 26 lines and covers dev/publish/release
steps only. There is **no `CLAUDE.md`**, no `docs/` tree, no specs or plans
of its own (the governing plan lives in the `blueforge` repo). No API usage
example is published anywhere in the repo — a consumer has to read
`client.py` to learn the interface.

## Readiness

**Alpha, and the shortest path to beta in the portfolio.** The code and
tests are done; the release pipeline is built and untriggered.

### Release attempt, 2026-08-30 — tagged, but publishing is blocked

`analytics-os-v0.1.0` has now been **created and pushed to both `origin` and
`forge-git`**. Distributions build and validate cleanly
(`blueforge_analytics_os-0.1.0-py3-none-any.whl` + `.tar.gz`, `twine check`
PASSED). Neither registry accepted them, for two separate reasons:

**PyPI — blocked by disabled Actions.** The tag push fired no workflow.
`repos/blueforge-studio/sdk-python/actions/permissions` returns
`{"enabled": false}` — GitHub Actions is off at the repository level, a
side effect of the mirror-sync work that made Gitea Actions canonical. Both
workflows show `state: active`, but Actions itself is disabled, so nothing
runs. PyPI trusted publishing **must** run on GitHub (it needs GitHub's OIDC
issuer), so Gitea cannot substitute. `pypi.org/pypi/blueforge-analytics-os`
still returns 404.

*Fix:* `gh api -X PUT repos/blueforge-studio/sdk-python/actions/permissions
-f enabled=true`, then re-push the tag. Note this also re-enables
`python-ci.yml` on pushes — delete that workflow first (it is already
superseded by `.gitea/workflows/ci.yml`) to avoid duplicate CI.

**packr — blocked by token scope.** `twine upload` to
`https://api.packr.blueforge.studio/pypi/legacy/` returned **403 Forbidden**.
The available `PACKR_TOKEN` carries `admin` permission but is scoped
`["@blueforge-studio"]` — a legacy npm-only scope. Per packr's own README,
"a token scoped to one ecosystem is rejected by every other ecosystem's
publish gate", so an npm scope cannot publish to `/pypi/`.

*Fix:* mint a `pypi:`-scoped admin token via
`POST /api/v1/admin/users/me/tokens` with
`{"role":"admin","scopes":["pypi:"]}` (admin role is required — packr
returns E403 on first-publish of a brand-new package name for `ci-publish`
and `maintainer` tokens). Then re-run the twine upload.

Ordered actions:
1. ~~Tag v0.1.0~~ — **done**, pushed to both remotes. Unblock one of the two
   registries above and the release completes.
2. Add a usage example to the README — the current 26 lines don't show how
   to instantiate the client.
3. Delete the superseded `.github/workflows/python-ci.yml`.
4. Add a `CLAUDE.md`.
5. Consider gitignoring or removing the committed `.review-venv/`.
