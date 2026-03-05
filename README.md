# my-claude-config

> Personal Claude Code configuration for [@aegusten](https://github.com/aegusten)
> Global agents, skills, and CLAUDE.md — synced across all machines.

---

## What's In Here

```
my-claude-config/
├── CLAUDE.md                          ← Global AI identity & rules (loaded every session)
├── agents/
│   ├── senior-backend.md              ← Python/FastAPI/Django senior engineer
│   ├── senior-architect.md            ← System design & architecture review
│   ├── security-reviewer.md           ← Security audit with severity ratings
│   └── code-reviewer.md              ← General code review (PR-style)
├── skills/
│   ├── backend-patterns/SKILL.md     ← Service layer, async SQLAlchemy, Celery patterns
│   ├── architecture/SKILL.md         ← IoT pipeline, API design, alert architecture
│   ├── security/SKILL.md             ← JWT auth, input validation, rate limiting
│   └── frontend-patterns/SKILL.md   ← React, TypeScript, WebSocket patterns
├── install.ps1                        ← Windows setup (run as Admin)
└── install.sh                         ← Linux/Mac setup
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
# Pull latest (morning / when switching PCs)
git pull

# Push updates (after editing agents or CLAUDE.md)
git add .
git commit -m "update: improved backend agent"
git push
```

---

## How to Use the Agents

In any project terminal with Claude Code running:

```bash
# Invoke a specific agent
> Use the senior-backend agent. Write a FastAPI endpoint for sensor ingestion.

> Use the senior-architect agent. I want to add real-time alerts — how should I design this?

> Use the security-reviewer agent. Review my auth module.

> Use the code-reviewer agent. Review the decoder module before I merge.

# Or let Claude auto-pick based on CLAUDE.md context
> Review this file and tell me what's wrong
```

---

## Per-Project Setup

Each project should have its own `CLAUDE.md` at the root with project-specific context:

```markdown
# ProjectName — Claude Context

## Stack
...

## Project Structure
...

## Specific Rules
...

## Run Commands
- Start: `docker-compose up`
- Test: `pytest`
```

---

## Agents Overview

| Agent | Use When | Model |
|---|---|---|
| `senior-backend` | Writing Python/FastAPI/Django code | Sonnet |
| `senior-architect` | Designing systems, planning features | Opus |
| `security-reviewer` | Auth code, public APIs, pre-deploy | Sonnet |
| `code-reviewer` | PR reviews, general code quality | Sonnet |
