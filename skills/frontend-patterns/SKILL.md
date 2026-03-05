# Frontend Patterns Skill

## When to Use This Skill
Load when writing React/TypeScript code, API integration, or real-time UI components.

---

## React Component Pattern

```tsx
// ✅ CORRECT — typed props, clear separation
interface SensorCardProps {
  deviceId: string;
  label: string;
  unit: string;
  onRefresh?: () => void;
}

export function SensorCard({ deviceId, label, unit, onRefresh }: SensorCardProps) {
  const { data, isLoading, error } = useSensorReading(deviceId);

  if (isLoading) return <SensorCardSkeleton />;
  if (error) return <SensorCardError message={error.message} onRetry={onRefresh} />;

  return (
    <div className="rounded-lg border p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-2xl font-bold">
        {data.value} <span className="text-sm">{unit}</span>
      </p>
    </div>
  );
}
```

---

## API Client Pattern (with error handling)

```typescript
// lib/api.ts
import axios, { AxiosError } from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
});

// Request interceptor — attach auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor — handle 401 globally
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // clear token, redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

## WebSocket Real-time Pattern

```typescript
// hooks/useDeviceStream.ts
import { useEffect, useRef, useState } from 'react';

interface SensorReading {
  deviceId: string;
  value: number;
  unit: string;
  recordedAt: string;
}

export function useDeviceStream(deviceId: string) {
  const [reading, setReading] = useState<SensorReading | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`${import.meta.env.VITE_WS_URL}/devices/${deviceId}/stream`);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as SensorReading;
        setReading(data);
      } catch {
        console.error('Failed to parse WebSocket message');
      }
    };

    // Reconnection handled by returning cleanup
    return () => {
      ws.close();
    };
  }, [deviceId]);

  return { reading, connected };
}
```

---

## Form Validation Pattern (React Hook Form + Zod)

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  threshold: z.number().min(0).max(9999),
  unit: z.string().min(1).max(20),
});

type FormData = z.infer<typeof schema>;

export function DeviceForm({ onSubmit }: { onSubmit: (data: FormData) => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} />
      {errors.name && <p className="text-red-500">{errors.name.message}</p>}
      {/* ... */}
    </form>
  );
}
```
