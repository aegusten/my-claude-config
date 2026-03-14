# Frontend Patterns Skill

## When to Use This Skill
Load when writing SvelteKit (admin dashboard), Svelte-in-Tauri (exam client), or Tailwind v4 styling.

---

## SvelteKit Load Function Pattern

```typescript
// routes/exams/+page.server.ts
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { apiGet } from '$lib/api/client';
import type { ExamSummary } from '$lib/types/exam';

export const load: PageServerLoad = async ({ locals }) => {
  // Guard: redirect to login if not authenticated
  if (!locals.user) redirect(302, '/login');

  const exams = await apiGet<ExamSummary[]>('/exams');
  return { exams };
};
```

```svelte
<!-- routes/exams/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';
  let { data }: { data: PageData } = $props();
</script>

{#each data.exams as exam}
  <ExamCard {exam} />
{/each}
```

---

## Typed API Client Pattern

```typescript
// lib/api/client.ts — single place for all API calls
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  constructor(public status: number, public body: unknown) {
    super(`API error ${status}`);
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const token = localStorage.getItem('access_token');
  const res = await fetch(`${BASE_URL}/api/v1${path}`, {
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });
  if (!res.ok) throw new ApiError(res.status, await res.json());
  return res.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const token = localStorage.getItem('access_token');
  const res = await fetch(`${BASE_URL}/api/v1${path}`, {
    method: 'POST',
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new ApiError(res.status, await res.json());
  return res.json() as Promise<T>;
}

// Never do raw fetch in a component or page — always use this client
```

---

## Svelte Component Pattern

```svelte
<!-- components/SessionCard.svelte -->
<script lang="ts">
  import type { SessionSummary } from '$lib/types/session';

  interface Props {
    session: SessionSummary;
    onDismiss?: (id: string) => void;
  }

  let { session, onDismiss }: Props = $props();

  // Derived state — no logic in template
  const riskClass = $derived(
    session.risk_score >= 70 ? 'text-red-600' :
    session.risk_score >= 40 ? 'text-yellow-600' : 'text-green-600'
  );
</script>

<div class="rounded-lg border p-4">
  <p class="font-medium">{session.student_id}</p>
  <p class={riskClass}>Risk: {session.risk_score}/100</p>
  {#if session.status === 'flagged'}
    <button onclick={() => onDismiss?.(session.id)}>Review</button>
  {/if}
</div>
```

---

## Real-Time Polling Store Pattern

```typescript
// lib/stores/session-monitor.ts
import { writable } from 'svelte/store';
import { apiGet } from '$lib/api/client';
import type { SessionDetail } from '$lib/types/session';

export function createSessionMonitor(sessionId: string) {
  const { subscribe, set } = writable<SessionDetail | null>(null);
  let interval: ReturnType<typeof setInterval>;

  async function refresh() {
    try {
      const data = await apiGet<SessionDetail>(`/sessions/${sessionId}`);
      set(data);
    } catch {
      // Don't crash the monitor on a transient error
    }
  }

  refresh(); // immediate first load
  interval = setInterval(refresh, 5000);

  return {
    subscribe,
    destroy: () => clearInterval(interval),
  };
}
```

```svelte
<script lang="ts">
  import { onDestroy } from 'svelte';
  import { createSessionMonitor } from '$lib/stores/session-monitor';

  const monitor = createSessionMonitor(sessionId);
  onDestroy(monitor.destroy);
</script>

{#if $monitor}
  <p>Risk score: {$monitor.risk_score}</p>
{/if}
```

---

## Tailwind v4 Theme Pattern

```css
/* app.css — v4 uses CSS-first config, no tailwind.config.js */
@import "tailwindcss";

@theme {
  --color-primary: #2563eb;
  --color-danger: #dc2626;
  --color-warning: #d97706;
  --color-success: #16a34a;

  --font-sans: 'Inter', system-ui, sans-serif;
}
```

```svelte
<!-- Use tokens in classes — no hardcoded hex values in markup -->
<span class="text-[--color-danger]">Flagged</span>

<!-- Or define semantic utility classes in app.css -->
```

---

## SvelteKit Layout Guard Pattern

```typescript
// routes/admin/+layout.server.ts — protects all admin routes
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  if (!locals.user) redirect(302, '/login');
  if (locals.user.role !== 'admin' && locals.user.role !== 'superadmin') {
    redirect(302, '/unauthorized');
  }
  return { user: locals.user };
};
```
