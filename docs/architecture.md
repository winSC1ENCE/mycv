# Architecture

`mycv` is a fully-separated frontend/backend application that doubles as a personal CV showcase and as a senior-engineering portfolio.

## Overview

```
                ┌──────────────────────────────────────────────┐
                │                Browser                       │
                └─────────────────────┬────────────────────────┘
                                      │ HTTPS
                                      ▼
                ┌──────────────────────────────────────────────┐
                │   Caddy (host) — TLS + security headers      │
                └─────────────────┬───────────────────┬────────┘
                                  │                   │
                  127.0.0.1:3000  │     /api/* /django-admin/* /static/* /media/*
                                  │                   │
                                  ▼                   ▼
                         ┌─────────────────┐ ┌──────────────────┐
                         │  Vue 3 + nginx  │ │  Django + DRF    │
                         │  (frontend)     │ │  + gunicorn      │
                         └─────────────────┘ └────────┬─────────┘
                                                     │ TCP, internal
                                                     ▼
                                            ┌──────────────────┐
                                            │  PostgreSQL 16   │
                                            │  (no port expose)│
                                            └──────────────────┘
```

All containers join one Docker network. Postgres is **never** bound to a host port. Caddy on the host reaches the app containers via `127.0.0.1` only.

## Stack

| Layer | Choice | Why |
|---|---|---|
| Backend framework | **Django 5.2** | Mature ORM, built-in admin, batteries-included security |
| API | **Django REST Framework + drf-spectacular** | Industry-standard; auto-generated OpenAPI schema |
| Database | **PostgreSQL 16** | Production-grade; SQLite for tests + E2E |
| Auth | DRF SessionAuthentication + CSRF + `django-axes` | Browser-friendly; no JWT token plumbing required |
| PDF | **WeasyPrint** + `segno` (QR) | Browser-quality typography; ATS-friendly real text |
| Frontend framework | **Vue 3** (Composition API + `<script setup>`) | Reactive, ergonomic, strong TS support |
| Build | **Vite 6** | Sub-second HMR; ESM-native |
| State | **Pinia** | Replaces Vuex; first-class TS types |
| Forms | **vee-validate + zod** | Schema-driven validation that mirrors the DRF serializer |
| i18n | **vue-i18n** | DE / EN; locale persisted to localStorage |
| SEO | **`@unhead/vue`** | Reactive `<head>` injection per route |
| Drag-and-drop | **vue-draggable-plus** | Active Vue-3-first port of Sortable.js |
| Animation | **GSAP + ScrollTrigger** | Respect `prefers-reduced-motion` |
| Reverse proxy | **Caddy** (already on host) | Automatic TLS, simple config |
| CI/CD | **GitHub Actions + GHCR** | First-class Docker support, free for public repos |
| Observability | **Sentry** (optional) + JSON logs | No-op when `SENTRY_DSN` unset |

## Request flows

### Public CV (most common)

```
GET /  →  Caddy  →  Vue (nginx serves dist/)
            │
            ├── HTML page boots Vue
            ├── cvStore.load() fetches /api/cv/
            └── /api/cv/  →  Caddy  →  Django  →  Postgres
                                       │
                                       └── PersonDetailSerializer returns
                                           full nested CV payload in one call
```

### Admin write

```
POST /api/experiences/  →  Caddy  →  Django
                                      │
                                      ├── CsrfViewMiddleware validates X-CSRFToken header
                                      ├── SessionAuthentication validates session cookie
                                      ├── IsAdminOrReadOnly permission
                                      ├── ExperienceWriteSerializer validates payload
                                      ├── PersonOwnedCreateMixin auto-fills the FK
                                      └── perform_create → save → 201
```

### PDF export

```
GET /api/cv/pdf/?lang=de&base_url=…  →  Django (CvPdfView, staff-only / IsAdminUser)
                                        │
                                        ├── Load published Person (prefetched)
                                        ├── Generate QR via segno (base_url = visitor origin)
                                        ├── render_to_string("exports/cv.html", ...)
                                        ├── WeasyPrint HTML(...).write_pdf(metadata=...)
                                        └── HttpResponse with Content-Disposition: attachment
```

Exposed only in the admin SPA (Timeline view → `📄 PDF EN` / `📄 PDF DE`); the
public site has no download button. Renders the normal theme in EN or DE.

## Theming

Two independent stylesheets share a single set of CSS custom properties:

- `src/styles/tokens.css` — design tokens (`--space-*`, `--radius-*`, `--font-*`, motion)
- `src/styles/normal.css` — flat corporate palette under `[data-theme="normal"]`
- `src/styles/dog.css` — comic B&W palette under `[data-theme="dog"]`

The active theme is applied to `<html data-theme="...">` by `useThemeStore`, persisted to `localStorage`. **Contrast ratio is ≥ 4.5:1 in both themes** — enforced by `@axe-core/playwright` in the E2E suite.

## i18n

- `vue-i18n` provides translated UI strings via `$t("…")`.
- Domain content (titles, descriptions, role names) is bilingual at the **model level**: every translatable field has a `_de` sibling (e.g. `title` + `title_de`). The `pickLocalized(obj, "title", locale)` composable resolves the right variant client-side, falling back to the canonical EN when DE is empty.

## Authentication

Session-based, browser-native:

1. `POST /api/auth/login/` → Django sets `sessionid` (HttpOnly) and `csrftoken` (readable) cookies.
2. axios request interceptor reads `csrftoken` from `document.cookie` and sets `X-CSRFToken` on all non-GET requests.
3. `django-axes` locks an IP+user pair after 5 failed attempts (1-hour cooldown).
4. `LoginRateThrottle` adds a 5-req/min DRF throttle on the login endpoint.

## PDF generation

WeasyPrint renders a **separate** stylesheet (`backend/templates/exports/cv.css`) rather than reusing the web CSS — the print engine has different layout semantics (page breaks, `@page` rules). The CV uses a **two-column layout**: a `position: fixed` accent sidebar (name, contact, skills, certificates) that WeasyPrint repeats on every page, beside the flowing main column (summary, experience, education). Fonts (Inter + JetBrains Mono) are embedded via `@font-face` with absolute file paths so WeasyPrint can resolve them without a base URL.

## Testing

| Layer | Tool | Purpose | Gate |
|---|---|---|---|
| Backend unit/integration | `pytest` + `pytest-django` + `factory-boy` | Models, serializers, views, management commands | **100% coverage on `apps/`** |
| Frontend unit | `vitest` | Stores, composables, API helpers | No coverage gate |
| End-to-end | `Playwright` + `@axe-core/playwright` | Smoke (home, theme, timeline, 404) + admin write flow + WCAG 2 A/AA accessibility | Serious/critical violations fail the build |

Playwright spawns a dedicated backend on port 8001 with `DATABASE_URL=sqlite:///db.e2e.sqlite3` and a frontend on port 3001. `tests/e2e/helpers/global-setup.ts` resets the DB, seeds it via the existing `load_cv_seed` management command, creates a superuser, and writes credentials to `tests/e2e/.auth.json` for the admin spec to read.

## Security

| Concern | Mitigation |
|---|---|
| XSS | Vue auto-escapes; CSP via `django-csp` (strict in prod) |
| CSRF | Django middleware + DRF SessionAuthentication; `CSRF_TRUSTED_ORIGINS` set per environment |
| Brute-force login | `django-axes` (5 attempts, 1 h cooldown) + `LoginRateThrottle` (5/min) |
| Session theft | HttpOnly session cookie, Secure + SameSite=Lax in prod |
| Clickjacking | `X-Frame-Options: DENY` (Django) + Caddy header |
| Transport | HSTS (1 year, preload, includeSubDomains) at Caddy + Django |
| Secrets in image | `.env` loaded at runtime only; never `COPY`-ed into a Docker layer |
| Postgres exposure | No port mapping in `docker-compose.prod.yml` |

## Deployment

See [deployment.md](deployment.md) for the self-host deployment guide.

## Domain model

See [erd.md](erd.md) for the entity-relationship diagram and conventions.
