# Entity-Relationship Diagram

The CV domain has one root entity (`Person`) with several owned collections and two pure lookup tables (`Technology`, `SkillCategory`).

```mermaid
erDiagram
    Person ||--o{ Experience      : has
    Person ||--o{ Education       : has
    Person ||--o{ Project         : owns
    Person ||--o{ Certificate     : holds
    Person ||--o{ SocialLink      : has
    Person ||--o{ TimelineEntry   : anchors
    Person  }o--o| MediaAsset     : "photo (FK, nullable)"

    Experience  }o--o{ Technology : "uses (M2M)"
    Project     }o--o{ Technology : "uses (M2M)"
    Project     }o--o{ MediaAsset : "shows (M2M)"

    Skill       }o--|| SkillCategory : "in"
    Skill       }o--o{ Technology    : "implies (M2M)"
    Certificate ||--o| MediaAsset    : "attaches"

    Person {
        string slug PK
        string first_name
        string last_name
        string title
        string title_de
        string email
        string summary
        string summary_de
    }

    Experience {
        int id PK
        string person FK
        string role
        string role_de
        string company
        date start_date
        date end_date
        string description
    }

    Education {
        int id PK
        string person FK
        string degree
        string institution
        date start_date
        date end_date
    }

    Certificate {
        int id PK
        string person FK
        string name
        string issuer
        date issue_date
        int media FK
    }

    Project {
        string slug PK
        string person FK
        string name
        string summary
        string url
        string repo_url
    }

    Technology {
        string slug PK
        string name
        string category
        string icon
    }

    SkillCategory {
        string slug PK
        string name
    }

    Skill {
        int id PK
        string category FK
        string name
        int level
    }

    SocialLink {
        int id PK
        string person FK
        string platform
        string url
    }

    TimelineEntry {
        int id PK
        string person FK
        date date
        string kind
        string title
    }

    MediaAsset {
        int id PK
        string file
        string alt_text
        string kind
    }
```

## Conventions

| Convention | Rule | Reason |
|---|---|---|
| Foreign keys | `on_delete=PROTECT` | Prevent accidental cascading wipes; an admin must explicitly clear children before deleting a parent. |
| Mixin | `Orderable` ABC supplies `order`, `is_published`, `created_at`, `updated_at`; `Meta.ordering = ["order", "id"]` | One place to change publication and ordering semantics. |
| Bilingual fields | `field` (EN, canonical) + `field_de` (DE, optional) | Avoids the migration friction of `django-modeltranslation`; frontend picks via `pickLocalized()`. |
| Indexed lookups | `slug` columns indexed + unique on `Person`, `Project`, `Technology`, `SkillCategory` | URL-friendly identifiers stable across migrations. |
| Date ordering | `Experience.Meta.ordering = ["-start_date", "order"]` (newest first) | Most recent role surfaces top of the CV. |

## Why the `Person` root

This is a single-person CV. The data model is deliberately Person-rooted rather than multi-tenant: every owned collection has a FK to `Person`. The single-row constraint is enforced by convention (the seed command creates exactly one) rather than by schema — leaves the door open for multi-CV instances later.

## Migration churn warning

The `Orderable` mixin + bilingual field pattern means every schema migration touches many rows. Migrations are designed to be additive: prefer adding nullable columns over reshaping existing ones. The current migrations directory contains exactly one initial migration per app (`0001_initial.py`).
