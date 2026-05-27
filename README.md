# mycv — Interactive CV

Full-stack interactive CV built as a senior-engineering reference build:
Vue 3 + Django REST + PostgreSQL behind Docker and a reverse proxy.

> **Stack** — Django 5 + DRF · Vue 3 + Vite + TypeScript · PostgreSQL 16 · Docker · WeasyPrint
> **Quality** — 100% backend coverage · mypy strict · ESLint + Prettier · Playwright + axe-core

> _Self-host on any Docker-capable VPS behind a reverse proxy. Configure `your-domain.tld` in `.env` and `Caddyfile.example`, then push the deploy workflow._

---

## Features

- **Bilingual content** (EN / DE) at the data-model level
- **Two themes**: clean corporate (`normal`) and comic B&W (`dog`)
- **Sensitive-data redaction** — 5 person fields (email, phone, address, marital status, DOB) and certificate file URLs are placeholders until a valid `AccessKey` token is supplied via `?key=…`
- **Admin CV endpoint** `/api/admin/cv/` returns unredacted data for authenticated staff
- **Custom Vue admin panel** (no Django admin UI for content edits)
- **Media attachments** — certificates and experiences accept image or PDF; projects accept up to 6 images with reorder controls
- **Image lightbox** + **PDF card** previews (shared `ImageLightbox` + `MediaPreview` components)
- Drag-and-drop reordering, image upload with crop, file validation, Esc-to-close admin modals
- Server-rendered **PDF export** via WeasyPrint (four lang/theme combos)
- **SEO**: JSON-LD Person schema, OG + Twitter tags, sitemap.xml, robots.txt
- **WCAG 2 AA** accessibility (enforced in CI via axe-playwright)
- Optional **Sentry** integration (DSN-gated; no-op without)
- `/api/health/` + `/api/ready/` probes; JSON-structured logs in prod

---

## Architecture

```
Internet → Reverse proxy (host) → Vue SPA (Docker) → Django REST API (Docker) → PostgreSQL (Docker)
```

Three Docker containers (`db`, `backend`, `frontend`) sit behind a host-level reverse proxy
(Caddy is the assumed default, Nginx/Traefik work the same way). The frontend is a Vite-built
SPA served by nginx-alpine; the backend is Django + DRF served by `gunicorn` in prod, the
Vite dev server in dev. Sensitive endpoints (`/api/admin/cv/`) require an authenticated
staff session; public endpoints redact sensitive fields unless a valid `AccessKey` is passed.

See [`docs/architecture.md`](docs/architecture.md) for the full request-flow diagrams, theming,
auth, and security details.

---

## Quickstart — Docker

```bash
cp .env.example .env             # fill in SECRET_KEY, POSTGRES_PASSWORD
make up                          # starts db + backend + frontend
# →  http://localhost:3000        (Vue frontend)
# →  http://localhost:8000/api/   (Django API)
# →  http://localhost:8000/django-admin/ (Django admin)
```

The backend container auto-runs `migrate` and `load_cv_seed` on first boot, so the site is populated immediately.

## Quickstart — without Docker

Two terminals.

**Terminal 1 — Backend** (uses SQLite by default):
```bash
cd backend
uv run python manage.py migrate
uv run python manage.py load_cv_seed
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

**Terminal 2 — Frontend**:
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000.

---

## Common commands

| Command | What it does |
|---|---|
| `make up` / `make down` | Start / stop the dev stack |
| `make migrate` | Run Django migrations in the running container |
| `make seed` | Reload the curated CV seed JSON |
| `make shell` | Open a Django shell |
| `make test` | Backend (pytest, 100% coverage) + frontend (vitest) |
| `make test-e2e` | Playwright E2E + accessibility tests |
| `make lint` | ruff + black + mypy + bandit + eslint + prettier + vue-tsc |
| `make build-backend` / `make build-frontend` | Production Docker images |

---

## Testing

```bash
make test               # backend (pytest --cov, 100%) + frontend (vitest)
make test-e2e           # Playwright E2E + axe-core a11y
make lint               # ruff + black + mypy + bandit + eslint + prettier + vue-tsc
```

Backend coverage is gated at 100%; frontend type-check via `vue-tsc --noEmit`.
Individual suites:

```bash
docker compose exec backend uv run pytest --cov --cov-report=term-missing
cd frontend && npm run test -- --run
```

---

## Repository layout

```
mycv/
├── backend/                      # Django + DRF + uv
│   ├── apps/
│   │   ├── cv/                   # Person, Experience, Education, …
│   │   ├── accounts/             # Custom User + session auth
│   │   └── exports/              # WeasyPrint PDF + sitemaps
│   ├── config/settings/          # base / dev / prod / test
│   ├── templates/exports/        # cv.html + cv.css for the PDF
│   ├── static/fonts/             # Inter + JetBrains Mono
│   ├── pyproject.toml
│   └── Dockerfile                # multi-stage; non-root in runtime
├── frontend/                     # Vue 3 + Vite + TS
│   ├── src/
│   │   ├── api/                  # Typed wrappers (exports, admin, auth)
│   │   ├── components/{base,sections,admin,timeline}/
│   │   ├── composables/          # usePageMeta, useLocalized, useEscClose, useAccessKey
│   │   ├── stores/               # Pinia: cv, theme, locale, auth
│   │   ├── views/{HomeView,LoginView,admin/*}
│   │   ├── locales/{en,de}.json
│   │   └── styles/{tokens,normal,dog,app}.css
│   ├── tests/{unit,e2e}/
│   └── Dockerfile                # multi-stage; nginx-alpine runtime
├── docs/
│   ├── architecture.md
│   ├── erd.md
│   └── deployment.md
├── scripts/                      # backup.sh + systemd units
├── .github/workflows/{ci,deploy}.yml
├── docker-compose.yml            # dev
├── docker-compose.prod.yml       # prod (no exposed ports except via reverse proxy)
├── Caddyfile.example
└── Makefile
```

---

## Documentation

| Doc | Purpose |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Stack overview, request flows, theming, auth, security |
| [`docs/erd.md`](docs/erd.md) | Mermaid ERD + schema conventions |
| [`docs/deployment.md`](docs/deployment.md) | Self-host on any Docker-capable VPS behind a reverse proxy |

---

## License

[MIT](LICENSE) © Nicolas Mischler.

---

## Status

All planned iterations are complete (Phases 1–5) plus a series of follow-up refactorings:

- **Phase 1** — Public read-only CV; Vue + Django + DRF; 100% coverage; CI
- **Phase 2** — Custom Vue admin panel, session auth, `django-axes`, file upload + crop
- **Phase 3** — PDF export (WeasyPrint + QR), SEO (JSON-LD, sitemap), Dog Mode polish
- **Phase 4** — Prod stack (`docker-compose.prod.yml`, CSP, Sentry, JSON logging, deploy workflow, nightly backups)
- **Phase 5** — Playwright E2E + axe-playwright; full docs; expanded README
- **Sensitive data + AccessKey flow** — 5 person fields and certificate URLs gated by `?key=` token
- **Admin endpoint** — `/api/admin/cv/` returns unredacted data for staff users
- **Media everywhere** — Certificate/Experience FK to `MediaAsset`; Project M2M (cap 6) with reorder; shared `ImageLightbox` + `MediaPreview` (PDF card) primitives
- **UX polish** — flat SVG icons (`Icon.vue`), Esc-to-close admin modals (`useEscClose`), modernised `Sensitive` blur + lock chip

Test
