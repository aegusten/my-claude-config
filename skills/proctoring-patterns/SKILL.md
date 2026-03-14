# Proctoring Patterns Skill

## When to Use This Skill
Load when writing proctoring-service code, designing incident detection rules, or scoring sessions.

**No ML. No camera. Proctoring is behavioral only — client-side events from the locked-down Tauri client.**

---

## Incident Types and Severity

| Incident Type       | Source          | Severity | Points |
|---------------------|-----------------|----------|--------|
| `focus_lost`        | Client-reported | medium   | 10     |
| `fullscreen_exit`   | Client-reported | medium   | 10     |
| `admin_flagged`     | Admin manual    | critical | 50     |

**Scoring:** `min(sum of non-dismissed incident points, 100)`
**Auto-flag threshold:** `risk_score >= 70`

---

## Ingest Endpoint Pattern

```python
# Events are simple DB writes — no Celery needed for ingest
@router.post("/event", status_code=204)
async def behavior_event(payload: BehaviorEvent, db: ...) -> None:
    session = await get_proctoring_session(db, payload.session_id)

    incident = Incident(
        proctoring_session_id=session.id,
        exam_session_id=payload.session_id,
        incident_type=IncidentType(payload.event_type),
        severity=EVENT_SEVERITY_MAP[incident_type],
        occurred_at=payload.occurred_at,
        duration_seconds=payload.duration_seconds,
    )
    db.add(incident)
    await db.flush()
    # Done. Return 204. No queuing.
```

---

## Heartbeat Pattern

```python
@router.post("/heartbeat", status_code=204)
async def heartbeat(payload: HeartbeatEvent, db: ...) -> None:
    session.last_heartbeat_at = payload.timestamp
    if not payload.is_focused:
        session.focus_loss_count += 1
    await db.flush()
    # Fast. No incidents created here.
    # Stale heartbeat detection happens at session review time.
```

---

## Risk Score Computation (score_session task)

```python
SEVERITY_WEIGHTS = {
    IncidentSeverity.low: 2,
    IncidentSeverity.medium: 10,
    IncidentSeverity.high: 25,
    IncidentSeverity.critical: 50,
}

def compute_score(incidents: list[Incident]) -> int:
    raw = sum(SEVERITY_WEIGHTS[inc.severity] for inc in incidents if not inc.is_dismissed)
    return min(raw, 100)  # always cap at 100
```

---

## Session State Machine

```
scheduled
    │ student opens client, starts exam
    ▼
in_progress ──── focus_lost / fullscreen_exit ──► Incident rows created inline
    │ student submits / time expires
    ▼
submitted
    │ score_session Celery task runs
    ▼
[risk_score < 70] → submitted (awaiting admin review)
[risk_score >= 70] → flagged   ← admin must review and clear
    │
    ▼
reviewed
```

---

## Behavior Event Severity Map

```python
EVENT_SEVERITY_MAP: dict[IncidentType, IncidentSeverity] = {
    IncidentType.focus_lost: IncidentSeverity.medium,
    IncidentType.fullscreen_exit: IncidentSeverity.medium,
}
```
