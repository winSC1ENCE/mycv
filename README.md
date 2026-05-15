# mycv — Interactive CV

Full-stack interactive CV for Nicolas Mischler at **cv.chlous.top**, designed
as both a personal portfolio and a senior-level engineering showcase.

Stack: **Django + DRF · Vue 3 + Vite + TypeScript · PostgreSQL · Docker · Caddy**.

## Quickstart

```bash
cp .env.example .env
make up                  # docker compose up --build
# →  http://localhost:3000   (Vue frontend)
# →  http://localhost:8000   (Django API + admin)
```

## Common commands

| Command | What it does |
|---|---|
| `make up` / `make down` | Start / stop the dev stack |
| `make migrate` | Run Django migrations in the running container |
| `make seed` | Reload the curated CV seed JSON |
| `make shell` | Open a Django shell |
| `make test` | Run backend (pytest, 100% coverage) + frontend (vitest) |
| `make lint` | ruff + black + mypy + bandit + eslint + prettier + vue-tsc |

## Repository layout

See `.rag/project/implementation_plan.md` for the full plan. Phase 1 (MVP)
delivers a read-only public CV with theme + locale toggles, served via the
docker-compose stack.

## Phase status

- ✅ Phase 1 — MVP (read-only public CV, Docker stack, CI, 100% backend tests)
- ⏳ Phase 2 — Admin & Auth
- ⏳ Phase 3 — PDF export + Dog Mode polish + i18n complete
- ⏳ Phase 4 — Production hardening + Hetzner deploy
