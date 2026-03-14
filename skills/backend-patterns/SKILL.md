# Backend Patterns Skill

## When to Use This Skill
Load this skill when writing or reviewing Python backend code, especially:
- Service layer patterns
- FastAPI route structure
- Celery task patterns
- SQLAlchemy async patterns
- Proctoring pipeline code

---

## Service Layer Pattern (FastAPI)

```python
# ✅ CORRECT — Route calls service, service handles logic
# api/v1/endpoints/exams.py
@router.post("/", response_model=ExamSummary, dependencies=[Depends(require_role(UserRole.admin))])
async def create_exam(
    payload: ExamCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Exam:
    return await exam_service.create_exam(db, payload, created_by=current_user)

# services/exam_service.py
async def create_exam(db: AsyncSession, payload: ExamCreate, created_by: User) -> Exam:
    if payload.scheduled_end <= payload.scheduled_start:
        raise ValueError("End must be after start")
    exam = Exam(**payload.model_dump(), created_by_id=created_by.id)
    db.add(exam)
    await db.flush()
    return exam
```

```python
# ❌ WRONG — Business logic in route handler
@router.post("/")
async def create_exam(payload: ExamCreate, db: AsyncSession = Depends(get_db)):
    if payload.scheduled_end <= payload.scheduled_start:  # logic belongs in service
        raise HTTPException(400, "Bad dates")
    exam = Exam(**payload.model_dump())
    db.add(exam)
    await db.commit()
    return exam
```

---

## Admin Guard Pattern

```python
# ✅ CORRECT — guard dep in dependencies=[], not as named param
_admin_only = [Depends(require_role(UserRole.admin, UserRole.superadmin))]

@router.delete("/{exam_id}", status_code=204, dependencies=_admin_only)
async def delete_exam(exam_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    ...

# ❌ WRONG — named _admin param that Pylance flags and pollutes the signature
@router.delete("/{exam_id}", status_code=204)
async def delete_exam(exam_id: UUID, _admin: AdminUser, db: ...) -> None:
    ...
```

---

## Async SQLAlchemy Pattern

```python
# Single row
async def get_session_by_id(db: AsyncSession, session_id: UUID) -> ExamSession | None:
    result = await db.execute(select(ExamSession).where(ExamSession.id == session_id))
    return result.scalar_one_or_none()

# With relationships loaded (avoid N+1 — always load eagerly if you'll access the relation)
async def get_session_with_incidents(db: AsyncSession, session_id: UUID) -> ExamSession | None:
    result = await db.execute(
        select(ExamSession)
        .options(selectinload(ExamSession.incidents))
        .where(ExamSession.id == session_id)
    )
    return result.scalar_one_or_none()
```

---

## Model Convention Pattern

```python
# All model files MUST start with this — required for lazy annotation evaluation
from __future__ import annotations
from typing import TYPE_CHECKING

# Cross-model relationships go under TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from app.models.exam import Exam, ExamSession

class User(Base):
    ...
    # TYPE_CHECKING import lets Pylance resolve this without a runtime circular import
    exam_sessions: Mapped[list[ExamSession]] = relationship(back_populates="student")
```

---

## Celery Task Pattern

```python
# Use bind=True ONLY when the task calls self.retry()
@celery_app.task(name="app.tasks.score_session.compute", max_retries=2)
def compute_risk_score(proctoring_session_id: str) -> dict:
    ...  # no self needed — don't add bind=True
```

---

## Proctoring Ingest Pattern

```python
# ✅ CORRECT — behavior events create Incident rows synchronously (simple DB write)
@router.post("/event", status_code=204)
async def behavior_event(payload: BehaviorEvent, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    session = await get_proctoring_session(db, payload.session_id)
    incident = Incident(
        proctoring_session_id=session.id,
        exam_session_id=payload.session_id,
        incident_type=IncidentType(payload.event_type),
        severity=severity_map[incident_type],
        occurred_at=payload.occurred_at,
    )
    db.add(incident)
    # Done — fast, inline, no queue needed

# ❌ WRONG — queuing simple DB writes is unnecessary overhead
@router.post("/event", status_code=202)
async def behavior_event(payload: BehaviorEvent) -> dict:
    create_incident.delay(payload.model_dump())  # overkill for a DB write
    return {"status": "queued"}
```

---

## Error Handling Pattern

```python
# Custom domain exceptions — don't use raw HTTPException in services
class ExamNotFoundError(Exception):
    pass

# Register handlers in main.py
@app.exception_handler(ExamNotFoundError)
async def exam_not_found(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

# Service raises domain exceptions; routes catch nothing (handled by FastAPI)
async def start_session(db: AsyncSession, exam_id: UUID, student: User) -> ExamSession:
    exam = await get_exam(db, exam_id)
    if not exam:
        raise ExamNotFoundError(f"Exam {exam_id} not found")
```
