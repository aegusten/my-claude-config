# Security Patterns Skill

## When to Use This Skill

Load when writing authentication, building public APIs, or reviewing for security.

---

## FastAPI Auth Pattern (JWT)

```python
# core/deps.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        if payload.get("type") != "access":   # reject refresh tokens used as access tokens
            raise credentials_exception
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = user.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_exception
    return user
```

---

## Authorization Pattern (Resource Ownership)

```python
# Student can only access their OWN sessions - always check ownership
async def get_session_or_403(
    session_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExamSession:
    result = await db.execute(select(ExamSession).where(ExamSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    # Admin can see all; student only their own
    if current_user.role == UserRole.student and session.student_id != current_user.id:
        raise HTTPException(403, "Not your session")
    return session
```

---

## Input Validation Pattern

```python
# Always validate at the boundary with Pydantic
from pydantic import BaseModel, Field, model_validator
from datetime import datetime, timezone

class ExamCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    duration_minutes: int = Field(..., ge=5, le=480)  # 5 min to 8 hours
    scheduled_start: datetime
    scheduled_end: datetime

    @model_validator(mode="after")
    def end_after_start(self) -> "ExamCreate":
        if self.scheduled_end <= self.scheduled_start:
            raise ValueError("scheduled_end must be after scheduled_start")
        now = datetime.now(timezone.utc)
        if self.scheduled_start < now.replace(hour=0, minute=0):
            raise ValueError("Cannot schedule exam in the past")
        return self
```

---

## Rate Limiting Pattern (Redis)

```python
# middleware/rate_limit.py - apply to login endpoint
import redis.asyncio as redis_asyncio
from fastapi import Request, HTTPException

async def rate_limit(
    request: Request,
    limit: int = 10,
    window: int = 60,
    key_prefix: str = "rl",
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    key = f"{key_prefix}:{client_ip}:{request.url.path}"

    async with redis_client.pipeline() as pipe:
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()

    if results[0] > limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={"Retry-After": str(window)},
        )

# Apply to login: 10 requests/minute per IP
```

---

## Environment Variables Pattern

```python
# config.py - NEVER hardcode secrets
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Required - will raise ValidationError on startup if missing
    secret_key: str
    database_url: str
    redis_url: str

    # Optional with safe defaults
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    environment: str = "development"

settings = Settings()  # fails fast if required vars are missing
```

**Never commit `.env` - always commit `.env.example` with placeholder values.**

---

## Proctoring Event Trust Model

```python
# Client-reported events ARE trusted - they come from the locked-down Tauri client.
# Do NOT add server-side verification or second-guess the event type.
# DO reject timestamps too far in the future (clock skew protection):

MAX_FUTURE_SECONDS = 30

async def behavior_event(payload: BehaviorEvent, ...) -> None:
    now = datetime.now(timezone.utc)
    if payload.occurred_at > now + timedelta(seconds=MAX_FUTURE_SECONDS):
        raise HTTPException(422, "Event timestamp is in the future")
    ...
```
