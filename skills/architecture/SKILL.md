# Architecture Patterns Skill

## When to Use This Skill
Load when designing systems, reviewing architecture decisions, or planning new features.

---

## ExamBrowser Proctoring Pipeline

```
[Windows Exam Client (Tauri + Svelte)]
        │
        ├── POST /ingest/heartbeat  (every 5s) ──────────────────────────────┐
        └── POST /ingest/event      (on behavior change) ────────────────────┤
                                                                              ▼
                                                        [Proctoring Service :8001]
                                                        validate → write Incident → 204
                                                        (on exam submit: enqueue score_session)
                                                                              │
                                                                    .delay() │ (submit only)
                                                                              ▼
                                                                    [Redis Queue]
                                                                              │
                                                                              ▼
                                                              [score_session Celery task]
                                                              compute risk score at submit
                                                                              │
                                                                     write risk_score ──────┐
                                                                                            ▼
                                                                                   [PostgreSQL]
                                                                                            ▲
                                                              [Core API :8000] ─────────────┘
                                                              auth + exam CRUD
                                                                              ▲
                                                        [Admin Dashboard (SvelteKit)]
```

**NO ML SERVICE. NO CAMERA. Proctoring = client-side behavioral events only.**

**Key decisions:**
- Proctoring Service creates Incident rows directly (synchronous) — events are simple writes, no queue overhead
- Celery only used for `score_session` task at submit — it's the only async work
- `risk_score` and `incident_count` denormalized on `exam_sessions` for fast dashboard reads

---

## API Design Pattern

```
POST   /api/v1/exams                    — create exam (admin)
GET    /api/v1/exams                    — list (students see published only)
GET    /api/v1/exams/{id}               — detail with questions
PATCH  /api/v1/exams/{id}               — update (admin)
DELETE /api/v1/exams/{id}               — set status=archived (soft delete)

POST   /api/v1/exams/{id}/sessions      — student starts attempt
GET    /api/v1/exams/{id}/sessions      — admin: all sessions for exam
GET    /api/v1/sessions/{id}/incidents  — admin: incident timeline
PATCH  /api/v1/incidents/{id}/dismiss   — admin: dismiss with reason
```

**Rules:**
- Always version API (`/v1/`)
- Nouns in paths, not verbs
- Pagination on all list endpoints (default 20, max 100)
- Soft delete via status field (exams) or `is_dismissed` (incidents) — never hard delete exam data
- Consistent error envelope: `{ "detail": "message" }` (FastAPI default)

---

## Multi-Incident Risk Scoring

```
Session submit triggered
        │
[score_session Celery task]
        │
SELECT incidents WHERE proctoring_session_id = ? AND is_dismissed = false
        │
        ├── low      × 2
        ├── medium    × 10
        ├── high      × 25
        └── critical  × 50
        │
        = raw_score → min(raw_score, 100) = final_risk_score
        │
UPDATE proctoring_sessions SET final_risk_score = ...
UPDATE exam_sessions SET risk_score = ..., incident_count = ...
        │
        └── if risk_score >= 70 → SET status = 'flagged'
```

---

## Session State Machine

```
scheduled
    │ student opens exam
    ▼
in_progress ──────────────────────────────────────────────────────────┐
    │ student submits / time expires                                   │ client events detected
    ▼                                                                  │ (focus_lost, fullscreen_exit)
submitted                                                              ↓
    │ score_session task runs                               incident rows created (inline)
    ▼
[risk_score < 70] → submitted (awaiting review)
[risk_score >= 70] → flagged   ← admin must review and clear
    │
    ▼
reviewed
```
