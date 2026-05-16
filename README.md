# mycv — Interactive CV

Full-stack interactive CV for Nicolas Mischler at **[cv.chlous.top](https://cv.chlous.top)**, built as both a personal portfolio and a senior-engineering showcase.

> Stack: **Django 5 + DRF · Vue 3 + Vite + TypeScript · PostgreSQL 16 · Docker · Caddy**
> Quality: **100% backend coverage · mypy strict · ESLint + Prettier · Playwright + axe-core**

---

## Features

- 🌐 Bilingual content (EN / DE) at the data-model level
- 🎨 Two themes: clean corporate (`normal`) and comic B&W (`dog`)
- 📄 Server-rendered PDF export via WeasyPrint, four lang/theme combos
- 🔐 Custom Vue admin panel (no Django admin UI for content edits)
- 📊 Drag-and-drop reordering, image upload with crop, file validation
- 🔍 SEO-ready: JSON-LD Person schema, OG + Twitter tags, sitemap.xml, robots.txt
- ♿ WCAG 2 AA accessibility (enforced in CI via axe-playwright)
- 🛰️ Optional Sentry integration (DSN-gated; no-op without)
- 📈 `/api/health/` + `/api/ready/` probes; JSON-structured logs in prod

---

## Quickstart — Docker

```bash
cp .env.example .env             # fill in SECRET_KEY, POSTGRES_PASSWORD
make up                          # starts db + backend + frontend
# →  http://localhost:3000        (Vue frontend)
# →  http://localhost:8000/api/   (Django API)
# →  http://localhost:8000/admin/ (Django admin)
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
│   │   ├── composables/          # usePageMeta, useLocalized
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
├── docker-compose.prod.yml       # prod (no exposed ports except via Caddy)
├── Caddyfile.example
└── Makefile
```

---

## Documentation

| Doc | Purpose |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Stack overview, request flows, theming, auth, security |
| [`docs/erd.md`](docs/erd.md) | Mermaid ERD + schema conventions |
| [`docs/deployment.md`](docs/deployment.md) | Hetzner deploy, Caddy merge, backup setup, secrets |
| [`.rag/project/implementation_plan.md`](.rag/project/implementation_plan.md) | Source plan that drove the build |

---

## Status

All five planned iterations are complete:

- ✅ **Phase 1** — Public read-only CV; Vue + Django + DRF; 100% coverage; CI
- ✅ **Phase 2** — Custom Vue admin panel, session auth, `django-axes`, file upload + crop
- ✅ **Phase 3** — PDF export (WeasyPrint + QR), SEO (`@unhead/vue`, JSON-LD, sitemap), Dog Mode polish
- ✅ **Phase 4** — Prod stack (`docker-compose.prod.yml`, Caddy, CSP, Sentry, JSON logging, deploy workflow, nightly backups)
- ✅ **Phase 5** — Playwright E2E + axe-playwright; full docs; expanded README

---

## License

MIT.
