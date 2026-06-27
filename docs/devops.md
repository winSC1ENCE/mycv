# DevOps Guide — develop, test, merge, release

End-to-end workflow for contributing to `mycv`: how to branch a feature, run and
test the stack locally, merge via pull request, and push the release tag that
triggers a production deploy.

- **Local dev** → [`Makefile`](../Makefile) targets over Docker Compose.
- **Quality gates** → [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).
- **Release/deploy** → [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml).
- **Host & server ops** → private [`docs/deployment.md`](./deployment.md) (gitignored).
- **System layout** → [`docs/architecture.md`](./architecture.md).

---

## 1. Overview

We follow **GitFlow**. Feature work merges into `develop`; releases promote
`develop` → `main`; a version tag on `main` deploys to production.

```
feature/<desc> ──PR──▶ develop ──release PR──▶ main ──tag vX.Y.Z──▶ deploy
   (or fix/<desc>)        │                       │                    │
                          └── CI gate ────────────┴── CI gate          └── build → GHCR → SSH deploy
```

| Stage     | Action                            | What fires                                    |
| --------- | --------------------------------- | --------------------------------------------- |
| Develop   | commit on `feature/*` or `fix/*`  | nothing (local)                               |
| Integrate | open PR → `develop`               | `ci.yml` — lint, test, build, e2e             |
| Release   | open PR `develop` → `main`, merge | `ci.yml`                                      |
| Deploy    | push tag `vX.Y.Z` on `main`       | `deploy.yml` — build → push GHCR → SSH deploy |

> **Branching rules (non-negotiable).** Never commit or push directly to `main`
> or `develop`. `feature/*` and `fix/*` branch **from** `develop` and merge **back
> into** `develop` via PR. `main` only ever changes via a PR from `develop`.
> Delete the branch after merge.

---

## 2. Prerequisites

| Tool                    | Version | Notes                                                               |
| ----------------------- | ------- | ------------------------------------------------------------------- |
| Docker + Compose plugin | recent  | runs the whole stack                                                |
| `uv`                    | latest  | Python deps/runner (backend runs `uv run` **inside** the container) |
| Node                    | 20      | only needed for editor tooling; tests/build also run in CI          |
| `pre-commit`            | latest  | install the hooks once: `pre-commit install`                        |

```bash
git clone https://github.com/winSC1ENCE/mycv.git
cd mycv
cp .env.example .env      # dev defaults are fine; never commit .env
pre-commit install
```

---

## 3. Start a feature

Always branch from an up-to-date `develop`:

```bash
git switch develop
git pull
git switch -c feature/<short-description>     # bugfixes: fix/<short-description>
```

Commit with **Conventional Commits** — `type(scope): subject`, subject ≤ 50 chars,
imperative mood. Allowed types: `feat, fix, perf, refactor, docs, test, chore, ci`.
Claude-authored commits carry the trailer:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 4. Run & test locally

Start the full dev stack (Postgres + Django + Vue, hot reload). On first boot the
backend auto-runs migrations and seeds the CV data:

```bash
make up          # docker compose up --build
```

| URL                                 | Service                            |
| ----------------------------------- | ---------------------------------- |
| <
>             | Vue frontend (Vite HMR)            |
| <http://localhost:8000/api/health/> | backend health (`{"status":"ok"}`) |
| <http://localhost:8000/admin/>      | Django admin                       |

Postgres is **not** exposed to the host — the backend reaches it over the Docker
network. Common day-to-day targets:

| Command        | Does                                                                |
| -------------- | ------------------------------------------------------------------- |
| `make logs`    | tail backend logs                                                   |
| `make migrate` | run Django migrations in the running container                      |
| `make seed`    | reload curated CV seed (`load_cv_seed --flush`) — wipes admin edits |
| `make shell`   | Django shell in the container                                       |
| `make down`    | stop the stack                                                      |

Run any backend management command via `uv run` inside the container:

```bash
docker compose exec backend uv run python manage.py <command>
```

### Test & lint before pushing

These mirror the CI gates — run them locally so the PR is green first time:

```bash
make test        # backend pytest (100% coverage gate) + frontend vitest
make test-e2e    # Playwright E2E (boots backend + frontend)
make lint        # ruff + black --check + mypy + bandit  |  eslint + prettier --check + vue-tsc
pre-commit run --all-files
```

> The backend `pytest` gate requires **100% coverage** — a drop fails CI.

---

## 5. Open a PR into `develop`

```bash
git push -u origin feature/<short-description>
gh pr create --base develop --fill        # or open the PR in the GitHub UI
```

`ci.yml` runs on the PR and must be **fully green** before merge:

- **Backend** — `ruff`, `black --check`, `mypy`, `bandit`, `pytest` (100% coverage), Python 3.14.
- **Frontend** — `eslint`, `prettier --check`, `vue-tsc` typecheck, `vitest`, `vite build`, Node 20.
- **Playwright E2E + a11y** and a **Docker build smoke** (both gated on backend + frontend passing).

Merge after review, then delete the branch.

> ⚠️ **CI trigger gap.** `ci.yml` currently triggers only on `push`/`pull_request`
> to **`main`**, so PRs targeting `develop` are **not yet gated automatically**.
> Until this is fixed, run `make lint && make test && make test-e2e` locally before
> merging into `develop`. **Required follow-up:** add `develop` to both
> `on.push.branches` and `on.pull_request.branches` in
> [`.github/workflows/ci.yml`](../.github/workflows/ci.yml). (Out of scope for this
> guide — tracked as a separate change.)

---

## 6. Release: `develop` → `main`

When `develop` holds a releasable set of changes:

```bash
gh pr create --base main --head develop --title "release: vX.Y.Z" --fill
```

Merge once CI is green. `main` is always deployable and only ever advances via this
release PR — never a direct commit.

---

## 7. Tag & deploy

**A tag push is the only thing that deploys to production.** After the release PR is
merged, tag the up-to-date `main`:

```bash
git switch main
git pull
git tag vX.Y.Z            # semantic versioning; tag ONLY on main
git push origin vX.Y.Z    # this fires deploy.yml
```

The tag **must match `v*.*.*`** (e.g. `v0.2.0`). Pushing it triggers
[`deploy.yml`](../.github/workflows/deploy.yml), which runs three jobs in order:

1. **`test`** — re-runs the lint/test/build gate on the exact tagged commit.
2. **`build_push`** — builds `mycv-backend` and `mycv-frontend` images and pushes
   them to **GHCR** tagged `:<sha>` and `:latest`.
3. **`deploy`** — SSHes to the host, checks out the tag, `docker compose pull`,
   `up -d`, waits for `/api/health/`, applies `migrate --noinput`, prunes old images.
   This job is **gated on the `DEPLOY_HOST` repository variable** — if it is unset,
   `build_push` still runs but the SSH deploy is **skipped**.

Watch the run and verify:

```bash
gh run watch                                   # or the Actions tab on GitHub
curl https://<your-domain>/api/health/         # {"status":"ok"}
curl https://<your-domain>/api/ready/          # {"status":"ready","db":"ok"}
```

**Manual re-run:** `deploy.yml` also supports `workflow_dispatch` — trigger it from
the Actions tab to re-deploy without cutting a new tag.

Host setup, SSH/secrets configuration, backups, and manual-deploy fallback live in
the private [`docs/deployment.md`](./deployment.md) — not duplicated here.

---

## 8. Reference & troubleshooting

### Make targets

| Target                                       | Purpose                            |
| -------------------------------------------- | ---------------------------------- |
| `make up` / `make down`                      | start / stop the dev stack         |
| `make logs`                                  | tail backend logs                  |
| `make migrate` / `make seed` / `make shell`  | DB migrate / reseed / Django shell |
| `make test` / `make test-e2e`                | unit+coverage / Playwright E2E     |
| `make lint`                                  | all backend + frontend linters     |
| `make build-backend` / `make build-frontend` | build production images locally    |

### Common issues

| Symptom                       | Cause / fix                                                                                                                                          |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tag pushed but no deploy      | Tag must match `v*.*.*` **and** be pushed (`git push origin vX.Y.Z`). Lightweight tag on the wrong branch won't deploy production code — tag `main`. |
| Deploy job skipped            | `DEPLOY_HOST` repo variable not set — `build_push` runs, SSH deploy is skipped by design. Set it under repo **Settings → Variables**.                |
| PR into `develop` shows no CI | The trigger gap in §5 — `ci.yml` is wired for `main` only. Run gates locally until `develop` is added to the triggers.                               |
| `make seed` wiped admin edits | `load_cv_seed --flush` is destructive — only run on a fresh/dev DB, never after curating content via the admin UI.                                   |
| Coverage gate fails           | Backend `pytest` requires 100%; add tests for new lines.                                                                                             |

> **Security reminders.** Never commit `.env` or any secret. Never push directly to
> `main`/`develop`. Never bypass the gates (`--no-verify`, disabling analysers).
