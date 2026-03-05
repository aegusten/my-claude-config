# Security Patterns Skill

## When to Use This Skill
Load when writing authentication, handling user data, building public APIs, or reviewing for security.

---

## FastAPI Auth Pattern (JWT)

```python
# auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],  # NEVER allow "none" algorithm
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await user_repo.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

# Authorization check — not just authentication
async def get_device_or_403(
    device_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Device:
    device = await device_repo.get_by_id(db, device_id)
    if not device:
        raise HTTPException(404, "Device not found")
    if device.owner_id != current_user.id:  # ownership check
        raise HTTPException(403, "Not your device")
    return device
```

---

## Input Validation Pattern

```python
# Always validate at the boundary with Pydantic
from pydantic import BaseModel, validator, Field
from decimal import Decimal

class SensorReadingCreate(BaseModel):
    device_id: UUID
    value: Decimal = Field(..., ge=-999.99, le=9999.99)  # bounded range
    unit: str = Field(..., max_length=20, regex=r'^[a-zA-Z°/]+$')  # allowlist pattern
    recorded_at: datetime | None = None

    @validator('recorded_at')
    def recorded_at_not_in_future(cls, v):
        if v and v > datetime.utcnow() + timedelta(minutes=5):
            raise ValueError('recorded_at cannot be in the future')
        return v
```

---

## Rate Limiting Pattern (FastAPI + Redis)

```python
# middleware/rate_limit.py
import redis.asyncio as redis
from fastapi import Request, HTTPException

async def rate_limit(request: Request, limit: int = 100, window: int = 60):
    """limit requests per window (seconds) per IP"""
    client_ip = request.client.host
    key = f"ratelimit:{client_ip}:{request.url.path}"
    
    async with redis_client.pipeline() as pipe:
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()
    
    count = results[0]
    if count > limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={"Retry-After": str(window)},
        )
```

---

## Environment Variables Pattern

```python
# config.py — NEVER hardcode secrets
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    MQTT_USERNAME: str
    MQTT_PASSWORD: str
    
    # with defaults for non-sensitive config only
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()  # fails fast if required env vars are missing
```

**Never commit `.env` — always commit `.env.example` with placeholder values.**
