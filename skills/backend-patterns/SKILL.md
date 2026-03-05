# Backend Patterns Skill

## When to Use This Skill
Load this skill when writing or reviewing Python backend code, especially:
- Service layer patterns
- Repository / data access patterns
- FastAPI route structure
- Django view/serializer patterns
- Celery task patterns

---

## Service Layer Pattern (FastAPI)

```python
# ✅ CORRECT — Route calls service, service handles logic
# routes/sensor.py
@router.post("/sensors/readings", response_model=ReadingResponse)
async def create_reading(
    payload: ReadingCreate,
    db: AsyncSession = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    return await sensor_service.create_reading(db, payload, device=current_device)

# services/sensor_service.py
async def create_reading(
    db: AsyncSession,
    payload: ReadingCreate,
    device: Device,
) -> SensorReading:
    if payload.value < device.min_threshold or payload.value > device.max_threshold:
        raise ValueError(f"Value {payload.value} out of range for device {device.id}")
    
    reading = SensorReading(
        device_id=device.id,
        value=payload.value,
        unit=payload.unit,
        recorded_at=payload.recorded_at or datetime.utcnow(),
    )
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return reading
```

```python
# ❌ WRONG — Business logic in route handler
@router.post("/sensors/readings")
async def create_reading(payload: ReadingCreate, db: AsyncSession = Depends(get_db)):
    # Don't do this — logic belongs in service
    if payload.value < 0:
        raise HTTPException(400, "Bad value")
    reading = SensorReading(**payload.dict())
    db.add(reading)
    await db.commit()
    return reading
```

---

## Async SQLAlchemy Pattern

```python
# Correct async session usage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_device_by_id(db: AsyncSession, device_id: UUID) -> Device | None:
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    return result.scalar_one_or_none()

# With relationships loaded (avoid N+1)
async def get_device_with_readings(db: AsyncSession, device_id: UUID) -> Device | None:
    result = await db.execute(
        select(Device)
        .options(selectinload(Device.readings))
        .where(Device.id == device_id)
    )
    return result.scalar_one_or_none()
```

---

## Celery Task Pattern

```python
# tasks/sensor_tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    time_limit=300,  # 5 min hard limit
    soft_time_limit=240,  # 4 min soft limit
)
def process_sensor_batch(self, device_id: str, readings: list[dict]) -> dict:
    try:
        # heavy processing here
        result = _do_processing(device_id, readings)
        return {"status": "success", "processed": len(readings)}
    except SoftTimeLimitExceeded:
        logger.error(f"Task timed out for device {device_id}")
        raise
    except Exception as exc:
        logger.error(f"Task failed for device {device_id}: {exc}")
        raise self.retry(exc=exc)
```

---

## Error Handling Pattern

```python
# Custom exceptions — define these, don't use raw HTTPException everywhere
# exceptions.py
class DeviceNotFoundError(Exception):
    pass

class SensorValueOutOfRangeError(Exception):
    pass

# Exception handlers in main.py
@app.exception_handler(DeviceNotFoundError)
async def device_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

# In service — raise domain exceptions, not HTTP exceptions
async def get_device(db: AsyncSession, device_id: UUID) -> Device:
    device = await device_repo.get_by_id(db, device_id)
    if not device:
        raise DeviceNotFoundError(f"Device {device_id} not found")
    return device
```
