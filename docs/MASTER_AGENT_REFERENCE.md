# Hunter Agent Operations Manual

This master reference is written for autonomous and semi-autonomous teammates working against the Hunter job-application workspace. It condenses runtime operations, module wiring, data layout, and failure playbooks so new agents can ramp without additional briefing.

---

## Table of Contents

1. [Operational Quick Start](#operational-quick-start)
   - [Start the App](#start-the-app)
   - [Restart & Recover](#restart--recover)
   - [Shut Down](#shut-down)
2. [Runtime Environment & External Dependencies](#runtime-environment--external-dependencies)
3. [System Architecture Overview](#system-architecture-overview)
   - [Execution Flow](#execution-flow)
   - [Core Dependency Map](#core-dependency-map)
4. [Module Reference](#module-reference)
   - [Web Layer](#web-layer)
   - [Models](#models)
   - [Services](#services)
   - [Utilities](#utilities)
   - [Frontend Templates & Static Assets](#frontend-templates--static-assets)
5. [Data & Configuration Layout](#data--configuration-layout)
6. [Root Scripts & Operational Utilities](#root-scripts--operational-utilities)
7. [Operational Playbooks](#operational-playbooks)
   - [Matching Hallucinations & Skewed Scores](#matching-hallucinations--skewed-scores)
   - [Document Generation Failures](#document-generation-failures)
   - [Dashboard Drift or Stale Data](#dashboard-drift-or-stale-data)
   - [Ollama or Model Connectivity](#ollama-or-model-connectivity)
8. [Testing & Verification Checklist](#testing--verification-checklist)
9. [Retired Documentation (November 2025)](#retired-documentation-november-2025)
10. [Fast Reference Links](#fast-reference-links)

---

## Operational Quick Start

### Start the App

1. **Ensure prerequisites**  
   - Ollama is running locally (`ollama serve`) with the `llama3` model available.  
   - Virtual environment activated (run `source venv/bin/activate` if not already).

2. **Preferred start command**  
   ```bash
   ./run.sh [PORT]
   ```  
   - Defaults to port `51003`.  
   - Wrapper checks the virtual environment and pings Ollama before launching `python -m app.web`.

3. **Alternative manual start** (used in some automation contexts)  
   ```bash
   python -m app.web
   ```  
   or  
   ```bash
   python3 app/web.py
   ```  
   The latter path is hard-coded inside `@start_app.sh` and assumes the project root is `/Users/kervinleacock/Documents/Development/hunter`.

4. **Access points**  
   - Dashboard: `http://localhost:51003/dashboard`  
   - API root: `http://localhost:51003/api/...`  
   - Landing UI: `http://localhost:51003/new-application`

### Restart & Recover

- **Soft restart (Flask reloader)**: stop the process with `Ctrl+C` and re-run the start command.  
- **Hard restart when dependencies changed**:  
  1. Stop the app.  
  2. Activate virtual environment (`source venv/bin/activate`).  
  3. `pip install -r requirements.txt` if packages changed.  
  4. Verify Ollama is still serving (`curl http://localhost:11434/api/tags`).  
  5. Start the app with `./run.sh`.
- **When configuration (`@config/config.yaml`) changes**: restart ensures new paths/models load into service singletons constructed in `@app/web.py`.

### Shut Down

- Use `Ctrl+C` in the terminal running Flask.  
- No background daemons are spawned by default. If `run.sh` was launched in the background, terminate the relevant process (`pkill -f "python -m app.web"` as last resort).

---

## Runtime Environment & External Dependencies

- **Python**: 3.11 (per virtual environment under `venv/`).  
- **Primary dependencies**: codified in `@requirements.txt`. Key libraries used in production code include `flask`, `flask-cors`, `requests`, `pyyaml`, and `jinja2`.  
- **Local AI runtime**: Ollama at `http://localhost:11434`, default model `llama3`. Both `@app/services/ai_analyzer.py` and `@app/services/enhanced_qualifications_analyzer.py` depend on this endpoint.  
- **Data storage**: filesystem under `data/` (YAML, Markdown, HTML, PDF). No external database.  
- **Browser UI**: served statically from `app/templates/web` and `static/`. No build tooling required.

---

## System Architecture Overview

### Execution Flow

1. **HTTP entry point** – `@app/web.py` creates the Flask app, registers UI routes, and exposes REST endpoints.  
2. **Request handling** – Endpoints delegate to service singletons instantiated at module import time (e.g., `JobProcessor`, `ResumeManager`, `DocumentGenerator`).  
3. **Services** – Orchestrate AI calls, file I/O, and domain logic (e.g., generate documents, manage resumes, build dashboards).  
4. **Models** – Lightweight dataclasses (`@app/models/application.py`, `@app/models/resume.py`, `@app/models/qualification.py`) represent persistent entities.  
5. **Utilities** – Provide cross-cutting helpers for file paths, YAML IO, prompts, datetime formatting, skill normalization.  
6. **Templates/static** – Rendered HTML pages in `data/output/index.html` or Jinja templates in `app/templates/web` for interactive pages.  
7. **Data persistence** – YAML and Markdown written under `data/applications/<Company-Role>/...`, enabling offline review and regeneration.

### Core Dependency Map

- `@app/web.py` ← depends on → `@app/services/*`, `@app/utils/datetime_utils.py`, `@app/utils/file_utils.py`
- `@app/services/document_generator.py` ← depends on → `@app/services.resume_manager`, `@app/services.ai_analyzer`, `@app/models/*`, `@app/utils/*`
- `@app/services.job_processor.py` ← depends on → `@app/models/application`, `@app/services.ai_analyzer`, `@app/utils/*`
- `@app/services.enhanced_qualifications_analyzer.py` ← wraps → `@app/services.preliminary_matcher`, `@app/services.ai_analyzer`
- `@app/services.dashboard_generator.py` ← depends on → `@app/services.job_processor`, `@app/models/application`
- `@app/services.template_manager.py` ← depends on → file utilities, datetime utilities
- `@app/services.skill_extractor.py` ← depends on → `AIAnalyzer`, `SimpleTechExtractor`, YAML utilities
- Utilities (`file_utils`, `datetime_utils`, `prompts`, `skill_normalizer`, `simple_tech_extractor`, `tech_matcher`) provide the shared toolkit used across services.

---

## Module Reference

### Web Layer

- `@app/web.py`  
  - Boots Flask with template root `app/templates/web` and static assets mapped from `static/`.  
  - Registers dashboard, resume management, application lifecycle, template CRUD, and reporting endpoints.  
  - Instantiates singleton services at import time; consider process restarts after altering service constructors.  
  - Generates dashboard before serving `/` and `/dashboard`.  
  - Provides health check `/api/check-ollama` and numerous JSON APIs consumed by the UI.

### Models

- `@app/models/application.py` – Dataclass mirroring application metadata persisted in `application.yaml`. Handles string→`Path` / `datetime` conversion and contact-count calculation.  
- `@app/models/qualification.py` – Dataclass representing AI-driven qualification analysis payloads.  
- `@app/models/resume.py` – Dataclass for base/custom resumes plus metadata stored in `base_resume.yaml`.

### Services

- `@app/services/ai_analyzer.py`  
  - Low-level Ollama client: qualification analysis, cover letter generation, company research, intro messages, resume rewrites, job detail extraction.  
  - Uses `EnhancedQualificationsAnalyzer` if available for hybrid preliminary+AI scoring.  
  - Exposes fallback parsing for match scores and skill extraction.

- `@app/services/document_generator.py`  
  - Orchestrates full document generation pipeline (qualifications, research, cover letter, summary HTML, optional intros/resumes).  
  - Persists outputs alongside application metadata and updates `Application` instance fields.  
  - Adds tailored compatibility paragraphs to cover letters and prunes undesirable content (e.g., “Scala” references).

- `@app/services/job_processor.py`  
  - Cleans raw job descriptions, creates folder structure, saves raw/structured descriptions, fetches job metadata (posted date, salary, etc.).  
  - Maintains application status history, handles rejection cleanup, and writes HTML updates per status change.  
  - Persists state as YAML inside each application folder.  
  - Supplies listing/search APIs for dashboard and reports.

- `@app/services/resume_manager.py`  
  - Manages base resume file, metadata YAML, technology extraction cache (`tech.yaml`), and AI-driven skill extraction (`skills.yaml`).  
  - Supports custom resume overrides per application, fallback templates, and technology categorization logic.

- `@app/services/dashboard_generator.py`  
  - Builds tabbed HTML dashboard summarizing application states and metrics.  
  - Invoked automatically after create/update operations or via `/api/dashboard/update`.

- `@app/services/template_manager.py`  
  - CRUD on outreach templates stored under `data/templates`.  
  - Maintains `templates_meta.yaml` index with formatted timestamps.

- `@app/services/preliminary_matcher.py` & `@app/services/enhanced_qualifications_analyzer.py`  
  - Provide lightweight, deterministic skill matching using `@app/utils/skill_normalizer.py` and `Jobdescr-General Skils.md`.  
  - Feed match context into the AI analyzer to reduce hallucinations and smooth scoring.

- `@app/services/skill_extractor.py`  
  - Performs comprehensive resume skill extraction (AI + fallback).  
  - Writes merged result to `data/resumes/skills.yaml` and ensures categories align with downstream matchers.

- `@app/services/skill_extractor.py`, `@app/services/skill_extractor.SkillExtractor.extract_and_save_skills` are invoked lazily by `ResumeManager.save_base_resume`.

- `@app/services/document_generator.generate_intro_messages` (within the service) – generates recruiter and hiring manager intros, reused by `/api/applications/<id>/generate-intros`.

### Utilities

- `@app/utils/file_utils.py` – Project root detection, data path helpers, YAML/text IO, filename sanitization.  
- `@app/utils/datetime_utils.py` – EST-aware timestamps, display formatting, filename-safe datetime strings.  
- `@app/utils/prompts.py` – Centralized prompt templates consumed by `AIAnalyzer` and related services.  
- `@app/utils/simple_tech_extractor.py` – Regex/keyword-based technology extraction for resumes/job descriptions.  
- `@app/utils/skill_normalizer.py` – Canonicalizes skills using taxonomy from `data/config/skill_normalization.yaml`.  
- `@app/utils/tech_matcher.py` – Additional matching helpers for technology crosswalks (used by analyzers).  
- `@app/utils/file_utils.get_project_root()` is foundational for path calculations; avoid changing directory structure without updating this utility.

### Frontend Templates & Static Assets

- **Reusable assets** (`static/`)  
  - `static/css/*.css` – Shared styles for dashboard, cover letters, forms, navigation.  
  - `static/js/*.js` – Vanilla JS modules powering dashboard interactions (tabs, filters) and template management.  
  - `static/favicon.svg` – Global favicon.

- **Custom page templates** (`@app/templates/web`)  
  - `base.html` – Shared layout skeleton (nav/sidebar).  
  - `landing.html` – High-level marketing/landing experience (rarely served).  
  - `ui.html` – Application creation UI (used by `/new-application`).  
  - `reports.html`, `daily_activities.html`, `templates.html` – Specialized dashboards consuming REST APIs.  
  - `reports.html` and `daily_activities.html` rely on JSON from `/api/reports` and `/api/daily-activities`; update endpoints and front-end logic together.

---

## Data & Configuration Layout

- `data/applications/<Company-Role>/`  
  - Contains `application.yaml`, raw and structured job descriptions, qualifications markdown, cover letters, summary HTML, intro messages, updates timeline HTML, optional custom resumes.  
  - Folder names derived from `Application.get_folder_name()`.
- `data/resumes/`  
  - `base_resume.md`, `base_resume.yaml`, `tech.yaml`, `skills.yaml`, supporting caches for resume analysis.  
  - `tech.yaml.backup` retains previous technology extraction snapshots.
- `data/templates/`  
  - HTML snippets per outreach template plus `templates_meta.yaml`.
- `data/output/index.html`  
  - Generated dashboard served by `/` and `/dashboard`.
- `data/config/skill_normalization.yaml`  
  - Taxonomy and canonical mappings used by `SkillNormalizer`.
- `config/config.yaml`  
  - Global settings: paths, AI defaults, dashboard preferences.  
  - Not read dynamically everywhere; some services hard-code defaults, so restart the app after editing.

---

## Root Scripts & Operational Utilities

| Script | Purpose | Key Dependencies |
| --- | --- | --- |
| `process_next_application.py` | Regenerate structured research, intros, and documents for a specific application using the enhanced research format. | `AIAnalyzer`, `JobProcessor`, `DocumentGenerator` |
| `regenerate_all_summaries.py`, `reprocess_application.py`, `regenerate_bestbuy.py`, `regenerate_insight.py` | Batch regeneration helpers tailored to named employers or latest schema updates. Review script before use; most call into `DocumentGenerator`. | Services bundle (`JobProcessor`, `DocumentGenerator`) |
| `resume_research_fix.py`, `interactive_research_fix.py`, `fix_research_and_intros.py` | Correct research or intro artifacts after prompt updates; typically re-run AI flows for existing folders. | `AIAnalyzer`, file utilities |
| `debug_extraction.py` | Inspect and debug technology extraction segments in stored qualification files. | `re`, application artifact paths |
| `delete_cover_applications.py`, `delete_test_applications.py` | Purge generated test data matching certain heuristics; regenerate dashboard afterward. | `JobProcessor`, `DashboardGenerator`, filesystem |
| `migrate_existing_applications.py`, `simple_migration.py` | Move older application directories into current schema. | File utilities, YAML |
| `update_bestbuy_html.py`, `process_insight_global.py` | Legacy migration scripts for specific employers; reference before reuse. | Mixed services |
| `test_extraction.py`, `test_job_extraction.py`, `test_amerisave.py` | Ad-hoc manual tests for parsing and extraction flows. | AI analyzer, skill matchers |
| `import_skills_to_taxonomy.py`, `compare_normalizers.py`, `extract_resume_skills.py` (under `scripts/`) | CLI utilities for maintaining skill normalization data and verifying extractor outputs. | `SkillNormalizer`, `SkillExtractor` |

Most scripts assume execution from the project root with the virtual environment active. Because many import service singletons, stop any running Flask instance to avoid race conditions on shared artifacts.

---

## Operational Playbooks

### Matching Hallucinations & Skewed Scores

Symptoms: match scores wildly low/high versus expectation, missing obvious skills, or Orwellian “wackets” noted in summaries.

1. **Validate cached skills**  
   - Open `data/resumes/skills.yaml`; ensure expected skills exist.  
   - If stale, re-run `ResumeManager.extract_and_save_skills()` by saving the base resume via `/api/resume` or running `python -m app.services.resume_manager` manually with a small script.
2. **Check preliminary matcher sources**  
   - Ensure `data/resumes/skills.yaml` and `Jobdescr-General Skils.md` contain coverage.  
   - For new skill categories, update `@app/utils/skill_normalizer.py` and `data/config/skill_normalization.yaml`.
3. **Re-run enhanced analysis**  
   - Use `/api/applications/<id>/regenerate` or `DocumentGenerator.generate_all_documents(application)` from a shell.  
   - Confirm Ollama logs for tokens/timeouts.
4. **Mitigate hallucinations**  
   - If AI over-penalizes, tweak prompt weights in `@app/utils/prompts.py` (qualification template) focusing on generosity guidance.  
   - For persistent anomalies, temporarily disable enhanced analyzer by catching exceptions in `AIAnalyzer` (forces fallback).
5. **Document incident**  
   - Add notes under the application’s `updates/` folder summarizing remediation steps for future agents.

### Document Generation Failures

1. Review traceback in console (Flask logs). Common triggers: missing base resume, Ollama offline, malformed JSON from UI.  
2. Confirm file paths exist using `@app/utils/file_utils.get_data_path`. Regenerate directories via `JobProcessor.create_job_application`.  
3. If AI timeout occurs, adjust `timeout` in `AIAnalyzer` temporarily or retry after verifying Ollama load.  
4. When HTML generation fails due to malformed data, open the specific writer in `DocumentGenerator` and re-run with sanitized inputs.  
5. After remediation, call `/api/dashboard/update` or rerun `DashboardGenerator.generate_index_page()` to refresh aggregated views.

### Dashboard Drift or Stale Data

1. Ensure `data/output/index.html` timestamp updates after operations. If not, invoke `/api/dashboard/update` or run `DashboardGenerator.generate_index_page()`.  
2. Verify JSON APIs (`/api/dashboard-stats`, `/api/recent-applications`) return expected counts; if they fail, inspect `JobProcessor.list_all_applications()` for YAML parsing errors.  
3. If certain applications lack updates, confirm their folders still exist (scripts like `delete_*` may have removed them).  
4. Restore from backups in `backup_qualifications_engine_*` if YAML corruption occurs.

### Ollama or Model Connectivity

1. Hit `/api/check-ollama`; it surfaces connectivity, base URL, current model list.  
2. If unreachable:  
   - Start service (`ollama serve`).  
   - Pull required model (`ollama pull llama3`).  
   - Restart Flask to refresh service singletons that cache `base_url` or `model`.  
3. For long-running jobs requiring higher token limits, tweak `num_predict` / `num_ctx` inside `AIAnalyzer._call_ollama`.  
4. When switching to paid APIs (OpenAI/Anthropic), adjust `@config/config.yaml` and extend `AIAnalyzer` accordingly.

---

## Testing & Verification Checklist

- Endpoint smoke test:  
  - `GET /api/check-ollama` → `connected: true`.  
  - `GET /api/applications` → returns array with `success: true`.  
  - `GET /api/reports?period=today` → success payload.
- UI sanity: load `/dashboard`, `/reports`, `/daily-activities` to confirm static assets load without console errors.  
- Resume cycle:  
  - `PUT /api/resume` with sample content regenerates `data/resumes/tech.yaml` and `skills.yaml`.  
  - `POST /api/applications` with sample job description creates folder and summary.  
  - `POST /api/applications/<id>/regenerate` completes without error.
- Regression scripts: run `python test_extraction.py` or targeted scripts under `scripts/` to validate matchers after taxonomy updates.

---

## Retired Documentation (November 2025)

| Removed File | Reason for Removal |
| --- | --- |
| `@docs/DOCUMENTATION_OVERVIEW.md` | Superseded by this manual; contained stale status claims and duplicated navigation. |
| `@docs/INDEX.md` | Redundant with `docs/README.md` and new master manual; referenced non-existent FAQ. |
| `@docs/TECHNICAL_SPECIFICATION.md` | Outdated architecture (mixed Node/Python references) incompatible with current codebase. |

Archived copies remain in version control history if needed for historical context.

---

## Fast Reference Links

- Project README: `@README.md`  
- Documentation entry point: `@docs/README.md`  
- API reference: `@docs/API_REFERENCE.md`  
- Enhanced matching deep dive: `@docs/ENHANCED_MATCHING_SYSTEM.md`  
- Skill matching plan: `@docs/NORMALIZATION_SYSTEM_PLAN.md`  
- Change history: `@CHANGES_SUMMARY.md` & `@docs/CHANGELOG.md`

For any missing context, search code with the file path prefix (e.g., `@app/services/document_generator.py:DocumentGenerator`) when prompting agents.


