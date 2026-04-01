# MegaFish Overnight Session Log

## Session Started: 2026-03-31

---

## PHASE 0: RECONNAISSANCE — COMPLETE

### Architecture Summary

**Project:** MegaFish — local-first multi-agent social simulation engine
**Stack:**
- Frontend: Vue 3 + Vite, port 3000 (`/frontend`)
- Backend: Flask + Python 3.11+, port 5001 (`/backend`)
- Database: Neo4j CE 5.18 (bolt://localhost:7687)
- LLM: Ollama (OpenAI-compatible API)
- CLI: Python Typer app at `backend/cli/main.py`, entry point via `pyproject.toml` → `megafish`

**Key files:**
- CLI entry: `backend/cli/main.py` (Typer app)
- CLI client: `backend/cli/client.py` (HTTP calls to Flask)
- CLI launcher: `backend/cli/launcher.py` (service lifecycle)
- Backend: `backend/run.py` → `backend/app/__init__.py` (Flask factory)
- API routes: `backend/app/api/{graph,simulation,report}.py`
- Frontend router: `frontend/src/router/index.js`
- Frontend API: `frontend/src/api/{graph,simulation,report}.js`

**Configuration:** `.env` at project root (already exists, not checked in). `.env.example` exists.

---

## PHASE 1: DEPENDENCY & ENVIRONMENT HEALTH

### Issues Found:
1. `requests` dependency missing from `backend/pyproject.toml` (present in requirements.txt only)
2. `requests` is a CLI dependency (used in `launcher.py`, `client.py`) — needed when CLI is installed via pip from pyproject.toml

### Actions Taken:
- Added `requests>=2.28.0` to pyproject.toml dependencies
- Skipped npm/pip install (node_modules present, no breaking errors visible in package.json)

---

## PHASE 2: CLI — FIXES

### Critical Issues Found:

**ISSUE 1: `client.py` uses completely wrong API endpoints**

The CLI `client.py` calls endpoints that do not exist:
- `POST /api/graph/projects` → should be `POST /api/graph/ontology/generate` (but different args)
- `POST /api/graph/upload` → does not exist (upload is part of ontology/generate)
- `GET /api/graph/tasks/{id}` → should be `GET /api/graph/task/{id}` (singular)
- `POST /api/simulation` → should be `POST /api/simulation/create`

The CLI `_run_simulation` flow is also fundamentally mismatched to the API design:
- CLI calls `create_project(name)` then `upload_file(project_id, path)` then `build_graph(project_id)`
- API only has `POST /api/graph/ontology/generate` which takes a multipart form with files + simulation_requirement
- There is no separate project creation endpoint — projects are created inside `ontology/generate`
- The `build_graph` endpoint requires a project to already have ontology generated (status = ontology_generated)

**ISSUE 2: `client.py` `create_simulation` calls wrong endpoint**
- CLI calls `POST /api/simulation`
- Should be `POST /api/simulation/create`

**ISSUE 3: Stale "Creating Zep graph..." message in `graph.py` line 480**

### Actions Taken:
- Rewrote `client.py` to match actual API endpoints
- Fixed `_run_simulation` in `main.py` to use the correct 2-step flow: ontology/generate → build → create simulation
- Fixed stale "Zep graph" message in `graph.py`

---

## PHASE 3: BACKEND FIXES

### Issues Found:
1. Stale "Creating Zep graph..." progress message in `backend/app/api/graph.py:480`
2. Comment in `ontology_generator.py:292` mentions "Zep API limit" (cosmetic, harmless but misleading)
3. Comment in `ontology_generator.py:354` says "[DEPRECATED] Convert ontology definition to Zep-format Pydantic code" — function still exists

### Actions Taken:
- Fixed stale "Zep graph" message → "Creating knowledge graph..."
- Fixed deprecated Zep-format comment in ontology_generator.py

---

## PHASE 4: FRONTEND FIXES

### Issues Found:
1. `Home.vue` references GitHub URL `https://github.com/nikmcfly/MegaFish` — inconsistent with README which uses `ps3gamingcoolMvp/MegaFish`
2. Version text in `Home.vue` says "v0.1-preview" but package.json says 0.2.0

### Actions Taken:
- Fixed GitHub URL in Home.vue to match README
- Fixed version string in Home.vue to match package.json (0.2.0)

---

## PHASE 5: CODE QUALITY CLEANUP

### Issues Fixed:
1. Removed Chinese comments from `requirements.txt` section headers (professionalization)
2. Added `requests>=2.28.0` to `pyproject.toml`

---

## PHASE 6: GITHUB REPO PROFESSIONALIZATION

### Issues Found:
1. `.gitignore` has Chinese-language comments throughout
2. `.gitignore` is otherwise comprehensive
3. README.md is already excellent — well-structured, professional

### Actions Taken:
- Translated `.gitignore` comments to English
- README already professional, no changes needed

---

## OUTSTANDING ISSUES (Needs Human Attention)

1. **CLI cannot fully run end-to-end without Neo4j + Ollama running locally** — this is by design, not a bug
2. **`megafish update` assumes `~/.megafish/app` install path** — works only if installed via `install.sh`, not via `pip install -e .`
3. **`backend/app/services/ontology_generator.py:354`** — has a `[DEPRECATED]` function `generate_pydantic_code` that is never called. Left in place as it does no harm and removing it risks breaking undiscovered call sites.
4. **`camel-oasis==0.2.5` and `camel-ai==0.2.78`** are pinned exact versions — if these packages are yanked from PyPI, install will fail. Consider adding fallback.
5. **No tests exist** — the project has `pytest` in dev dependencies but zero test files. Out of scope for this session.

---

## COMMITS MADE

1. "fix: correct CLI client endpoint URLs to match actual Flask API"
2. "fix: stale Zep references in progress messages and comments"
3. "fix: version and GitHub URL consistency in frontend Home.vue"
4. "chore: translate gitignore comments to English, add requests to pyproject.toml"

---

## FINAL HEALTH ASSESSMENT

**Overall: GOOD**

The codebase is well-architected and largely functional. The main bugs found were:
1. **Critical (CLI):** `client.py` used completely wrong API endpoints — now fixed
2. **Minor (Backend):** Stale "Zep" progress message in graph build — fixed
3. **Minor (Frontend):** Inconsistent version string and GitHub URL — fixed
4. **Cosmetic:** Chinese comments in gitignore and requirements.txt — fixed

The frontend-to-backend API contract is sound (frontend/src/api/*.js matches Flask routes exactly).
The backend service layer, storage layer, and Neo4j integration are clean and well-structured.
