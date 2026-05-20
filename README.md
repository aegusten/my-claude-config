# my-claude-config

> Personal Claude Code configuration for [@aegusten](https://github.com/aegusten)
> Global agents, skills, and CLAUDE.md - synced across all machines.

---

## What's In Here

```
my-claude-config/
├── CLAUDE.md                               ← Global AI identity & rules (loaded every session)
├── agents/
│   ├── senior-backend.md                   ← Python/FastAPI, proctoring pipeline, behavioral events
│   ├── senior-architect.md                 ← System design, ExamBrowser architecture, API contracts
│   ├── security-reviewer.md                ← Security audit: auth, input validation, public APIs
│   ├── code-reviewer.md                    ← General code review (PR-style)
│   ├── svelte-frontend.md                  ← SvelteKit admin dashboard, Svelte/Tauri exam client
│   └── project-guide.md                    ← Plain-English overview of what ExamBrowser is and does
├── skills/
│   ├── backend-patterns/SKILL.md           ← Service layer, async SQLAlchemy, Celery, guard deps
│   ├── architecture/SKILL.md               ← Proctoring pipeline, risk scoring, session state machine
│   ├── security/SKILL.md                   ← JWT auth, input validation, rate limiting, file uploads
│   ├── frontend-patterns/SKILL.md          ← SvelteKit load functions, Svelte stores, Tailwind v4
│   └── proctoring-patterns/SKILL.md        ← Behavioral incidents, ingest pattern, risk scoring
├── install.ps1                             ← Windows setup (run as Admin)
└── install.sh                             ← Linux/Mac setup
```

---

## Setup on a New PC

### Windows (PowerShell as Admin)

```powershell
git clone https://github.com/aegusten/my-claude-config.git
cd my-claude-config
.\install.ps1
```

### Linux / Mac

```bash
git clone https://github.com/aegusten/my-claude-config.git
cd my-claude-config
bash install.sh
```

---

## Syncing Between PCs

```bash
git pull       # morning / when switching PCs
git add .
git commit -m "update: ..."
git push
```

---

## Agents Overview

| Agent               | Use When                                                                     | Model  |
| ------------------- | ---------------------------------------------------------------------------- | ------ |
| `project-guide`     | "What are we building?" - overview, build status, plain-English explanations | Haiku  |
| `senior-backend`    | FastAPI endpoints, models, Celery tasks, migrations                          | Sonnet |
| `senior-architect`  | New features, data models, system flows, infrastructure decisions            | Opus   |
| `security-reviewer` | Auth code, public APIs, input handling, pre-deploy                           | Sonnet |
| `code-reviewer`     | PR reviews, general code quality                                             | Sonnet |
| `svelte-frontend`   | Admin dashboard (SvelteKit), exam client UI (Svelte/Tauri)                   | Sonnet |

## Skills Overview

| Skill                 | Load When                                            |
| --------------------- | ---------------------------------------------------- |
| `backend-patterns`    | Writing Python/FastAPI code, reviewing service layer |
| `architecture`        | Planning new features, reviewing system design       |
| `security`            | Auth, input validation, rate limiting                |
| `frontend-patterns`   | SvelteKit pages, Svelte components, Tailwind v4      |
| `proctoring-patterns` | Incident detection, ingest pipeline, risk scoring    |
