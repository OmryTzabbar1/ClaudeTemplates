# ContextModuleDocumentation/CONTEXT_config.md

Version: 1.4.0

<!--
This is an EXAMPLE of a populated per-module CONTEXT file, showing what
a real `ContextModuleDocumentation/CONTEXT_<module>.md` looks like once
you've filled in the empty template at the repo root (`CONTEXT_MODULE.md`).

Use this as a reference for tone, depth, and structure — do not copy it
into your project as-is. The fictional "Config" module here is generic
enough to be illustrative; replace it with your real module's contents.
-->

---

## Module Summary

The `Config` module (`src/config/`) provides the central `AppConfig` Pydantic model that holds all tunable runtime values — paths, thresholds, feature flags, and credentials (loaded from env). No other module hardcodes these — they import `get_config()` instead. This module owns configuration loading and validation only; it contains no business logic.

---

## Current Module State

**in-progress** — `AppConfig` model + env loader + caching done; integration into the ingestion module pending.

---

## Recent Changes

- **2026-04-15:** Added `feature_flags` nested model to `AppConfig` (38→47 lines). New tests in `test_app_config.py` (62→78 lines, +2 tests) covering default flags and env overrides.
- **2026-04-12:** Switched env loading from `os.getenv` to `pydantic-settings` `BaseSettings` for type-safety and `.env` file support. `loader.py` 51→34 lines (Pydantic handles parsing). 4 tests retired as dead.
- **2026-04-10:** Added `cache.py` (22 lines) — module-level `lru_cache` wrapping `load_config()` so repeat callers don't re-read `.env`. Tests in `test_cache.py` (41 lines, 3 tests).
- **2026-04-08:** Created module. `app_config.py` (38 lines), `loader.py` (51 lines), `defaults.py` (29 lines, named-constant defaults to satisfy "no hardcoded values" rule). Initial test suite (62 lines, 6 tests).

---

## Pending Tasks

- Wire `get_config()` into `src/ingest/pipeline.py` (currently reads from `os.environ` directly)
- Add `validate-config` CLI subcommand that loads and prints the resolved config (helps debugging deploys)
- Document the `.env` precedence order in module-level docstring

---

## Architecture & File Map

```
src/config/
├── __init__.py     (4 lines)   — Re-exports: AppConfig, get_config, FeatureFlags
├── app_config.py   (47 lines)  — Pydantic models: AppConfig, FeatureFlags
├── defaults.py     (29 lines)  — Named-constant defaults (DEFAULT_BATCH_SIZE, DEFAULT_TIMEOUT, etc.)
├── loader.py       (34 lines)  — pydantic-settings env/.env loader
└── cache.py        (22 lines)  — lru_cache wrapper around load_config()

tests/config/
├── test_app_config.py (78 lines) — 8 tests: defaults, validation errors, env overrides, feature flag toggles
├── test_loader.py     (54 lines) — 5 tests: .env precedence, missing required keys, type coercion
└── test_cache.py      (41 lines) — 3 tests: cache hit, cache miss after clear, thread safety
```

Total: 309 lines across 8 files.

---

## Key Decisions & Notes

- **Pydantic over dataclasses** — Picked `pydantic-settings` for env-var ingestion because dataclasses don't validate types at load time. The cost is the runtime dependency, but every other module already uses Pydantic for API models.
- **lru_cache vs. module global** — Tried a module-level `_config = load_config()` at import; broke tests that needed to override env vars between cases. `lru_cache` lets tests call `get_config.cache_clear()` between cases.
- **No secret values in defaults.py** — Defaults are non-sensitive only (sizes, timeouts, log levels). Anything secret (API keys, DB URLs) has `Field(...)` with no default — Pydantic raises if the env var is missing.
- **`.env` is for local dev only** — Production reads from real environment variables (set by the deploy system). `.env` is in `.gitignore`.

---

## Version Decision Table

<!-- Project-level overrides to this table live in CONTEXT.md § Versioning Rules -->

| Change type | Version bump |
|---|---|
| Line count correction only | patch |
| New file added to module | minor |
| File removed or renamed | minor |
| Module behavior/API changed | minor |
| Module removed or replaced | major |

---

## Module Change Checklist

Run this checklist after every change to this module. Do not skip items.

- [x] **Line counts** — Updated all five source files + three test files in the File Map above
- [x] **New files** — `feature_flags` is a model addition inside `app_config.py`, not a new file; nothing to register
- [ ] **Removed files** — N/A
- [ ] **Split files** — N/A
- [ ] **Interface changes** — N/A (FeatureFlags is consumed only by the toggle decorator inside this module)
- [ ] **README.md** — N/A (module list unchanged, no phase shift, no tech-stack change)
- [x] **Version bump** — 1.3.0 → 1.4.0 (new field on a public model = minor)
- [x] **Recent Changes** — Added 2026-04-15 entry above
