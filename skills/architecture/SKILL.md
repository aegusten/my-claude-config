# Architecture Patterns Skill

## When to Use This Skill
Load when designing systems, reviewing architecture decisions, or planning new features.

---

## IoT Data Pipeline Architecture

```
[IoT Devices]
     │ MQTT publish
     ▼
[Mosquitto Broker] ──auth──► reject unauthenticated
     │
     ▼
[MQTT Consumer Service]  ← subscribes to device/+/sensors/+
     │ validate payload
     │ decode
     ▼
[Celery Queue (Redis)]
     │
     ▼
[Celery Worker: process_reading]
     ├──► [PostgreSQL] — persist raw reading
     ├──► [Redis Cache] — update latest value per device
     └──► [WebSocket Hub] — push to connected dashboards
```

**Key decisions in this pattern:**
- MQTT consumer is lightweight — validate + enqueue only, never block
- All heavy processing is async via Celery
- Redis holds "current state" for fast dashboard reads
- PostgreSQL holds historical data

---

## Multi-Tenant Data Isolation Pattern

```
Tenant A ──► DB Router ──► tenant_a database
Tenant B ──► DB Router ──► tenant_b database
              │
              └──► Global DB (user auth, tenant registry)
```

**When to use:** SaaS with strict data isolation requirements
**Trade-off:** More complex migrations, but no risk of data leakage

---

## API Design Pattern

```
POST   /api/v1/devices          — create device
GET    /api/v1/devices          — list devices (paginated)
GET    /api/v1/devices/{id}     — get device
PATCH  /api/v1/devices/{id}     — partial update
DELETE /api/v1/devices/{id}     — soft delete (never hard delete)

GET    /api/v1/devices/{id}/readings          — paginated readings
POST   /api/v1/devices/{id}/readings/batch    — bulk ingest
GET    /api/v1/devices/{id}/readings/latest   — most recent reading
```

**Rules:**
- Always version your API (`/v1/`)
- Use nouns not verbs in paths
- Pagination on all list endpoints (default 20, max 100)
- Soft delete — add `deleted_at` timestamp, never remove rows
- Consistent response envelope: `{ data, meta, errors }`

---

## Real-Time Alert Architecture

```
[New Reading] → [Celery Worker]
                     │
                     ├── check: value > threshold?
                     │         YES → [Alert Service]
                     │                    │
                     │                    ├── [DB: log alert]
                     │                    ├── [Redis: set alert state] ← prevents re-alerting
                     │                    └── [Notification Queue] → email/SMS/webhook
                     │
                     └── NO → [Redis: clear alert state if was alerting]
```

**Key:** Use Redis to track alert state so you don't spam notifications.
Only trigger notification on state CHANGE (normal→alert, alert→normal).
