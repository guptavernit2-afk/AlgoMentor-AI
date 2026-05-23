# AlgoMentor AI — Database Schema

## Why Supabase?

AlgoMentor AI currently stores all student data in Python dictionaries that are cleared every time the server restarts. Supabase provides a fully managed PostgreSQL database that lets us persist this data permanently while keeping the FastAPI backend as the only layer that talks to the database — the React frontend never connects to Supabase directly.

---

## How to apply the schema

1. Open your [Supabase project dashboard](https://app.supabase.com).
2. Navigate to **SQL Editor** in the left sidebar.
3. Create a new query and paste the entire contents of `schema.sql`.
4. Click **Run**.

The script is safe to execute more than once — every statement uses `IF NOT EXISTS` or `CREATE OR REPLACE`.

> **Never store or commit connection strings, passwords, project URLs, or service-role keys.** These will be loaded from environment variables in the next integration phase.

---

## Tables

| Table | Purpose |
|---|---|
| `public.student_profiles` | One row per student — name, goal, topics, study-time limits |
| `public.weekly_schedules` | One row per student per weekday — regular class timetable |
| `public.daily_overrides` | Optional per-day deviations (exam day, free day, etc.) |
| `public.topic_revision_states` | Current SM-2 state for each tracked DSA topic |
| `public.topic_review_history` | Append-only audit trail of every review submission |

---

## Constraints, indexes and triggers

### Constraints
All columns enforce the same validation rules as the FastAPI Pydantic models:

- `student_profiles`: name 2–60 chars, goal and preferred_study_time allowed values, min/max minutes bounds and ordering.
- `weekly_schedules`: exactly one row per `(user_id, day_name)`, valid day names, free-day ↔ empty classes integrity.
- `daily_overrides`: one per `(user_id, override_date)`, situation and energy_level allowed values, note ≤ 200 chars.
- `topic_revision_states`: `easiness_factor ≥ 1.30`, `last_quality` 0–5, non-negative repetitions and interval.
- `topic_review_history`: same SM-2 validity checks as above.

### Indexes
| Index | Purpose |
|---|---|
| `idx_topic_revision_states_user_next_review` | Fast daily-plan lookups for due topics |
| `idx_topic_review_history_user_topic_date` | Chronological history per topic |
| `idx_topic_review_history_user_next_review` | Look up reviews by scheduled date |

### `updated_at` trigger
A single reusable function `public.set_updated_at()` automatically sets `updated_at = now()` on every `UPDATE`. It is attached to all mutable tables:

- `student_profiles`
- `weekly_schedules`
- `daily_overrides`
- `topic_revision_states`

`topic_review_history` is intentionally append-only and has no `updated_at` column.

---

## Row Level Security (RLS)

RLS is **enabled** on all five tables. No access policies are defined yet.

**Why enable it now without policies?**  
Enabling RLS locks down the table by default — no row is readable or writable through the Supabase client unless a policy explicitly permits it. This is the safe starting point. When authentication is added in a later phase, explicit policies will be written to grant the FastAPI service role the access it needs, and optionally grant students access to their own rows.

> Do not create open `anon` policies. The FastAPI backend will connect using secure server-side credentials and bypass RLS via the service role as needed.

---

## What comes next

| Step | Description |
|---|---|
| Auth integration | Add RLS policies for authenticated FastAPI service role |
| Connection layer | Wire `asyncpg` or `psycopg` in FastAPI, load credentials from env |
| Storage migration | Replace `PROFILE_STORE`, `SCHEDULE_STORE`, etc. with async DB queries |
| Secret management | Store `DATABASE_URL` in `.env` (git-ignored) and production secrets manager |

---

## Student Profile Persistence ✅

`public.student_profiles` is the first table actively used by the FastAPI backend.

### Architecture

The Student Profile API (`PUT /api/users/{user_id}/profile` and `GET /api/users/{user_id}/profile`) now routes through a **repository layer** (`app/repositories/profile_repository.py`) that selects its storage backend at startup:

| `STORAGE_BACKEND` | Implementation | Used by |
|---|---|---|
| `memory` (default) | `MemoryProfileRepository` | All automated tests |
| `postgres` | `PostgresProfileRepository` | Local Supabase / production |

In `postgres` mode, the repository performs an upsert (`INSERT … ON CONFLICT DO UPDATE`) so repeated `PUT` requests update the same row without creating duplicates. The `updated_at` column is refreshed automatically by the `set_updated_at()` database trigger.

### Unit tests

Automated tests always run in `memory` mode. No test connects to the real Supabase project.

### Manual verification

After setting `STORAGE_BACKEND=postgres` in `backend/.env`, run from the `backend/` folder:

```bash
python -m scripts.smoke_test_profile_persistence
```

This writes one test row with `user_id = demo-user-db-test` to `public.student_profiles`. Confirm it visually in **Supabase Table Editor**, then delete it manually.

> The script never prints database credentials, passwords, host names, or connection URLs.

---

## Weekly Schedule Persistence ✅

`public.weekly_schedules` is the second table actively used by the FastAPI backend.

### Architecture

The Weekly Schedule API (`PUT /api/users/{user_id}/weekly-schedule` and `GET /api/users/{user_id}/weekly-schedule`) routes through a **repository layer** (`app/repositories/schedule_repository.py`):

| `STORAGE_BACKEND` | Implementation | Used by |
|---|---|---|
| `memory` (default) | `MemoryScheduleRepository` | All automated tests |
| `postgres` | `PostgresScheduleRepository` | Local Supabase / production |

### Seven rows per user

Each call to `PUT weekly-schedule` writes **seven rows** to `public.weekly_schedules` — one per weekday. All seven rows are upserted inside a **single database transaction** so the schedule is always saved atomically: either all seven days persist or none do (on error the transaction is rolled back automatically).

Each row contains:
- `user_id` — foreign key to `public.student_profiles`
- `day_name` — Monday through Sunday
- `is_free_day` — boolean
- `classes` — JSONB array of `{title, start_time, end_time}` objects

Reads return days in canonical **Monday → Sunday** order (enforced by a `CASE` expression in the SQL, not by application-level sorting).

### Compatibility

`require_schedule(user_id)` (used by daily-override and daily-plan endpoints) is now backed by `PostgresScheduleRepository` in postgres mode, so a persisted schedule is visible across backend restarts and to all downstream features.

### Unit tests

Automated tests always run in `memory` mode. No test connects to the real Supabase project. The `conftest.py` Layer 3 guard additionally blocks `PostgresScheduleRepository._engine()` from being called.

### Manual verification

After setting `STORAGE_BACKEND=postgres` in `backend/.env`, run from the `backend/` folder:

```bash
python -m scripts.smoke_test_weekly_schedule_persistence
```

This writes:
- One test row with `user_id = demo-user-schedule-db-test` to `public.student_profiles`
- Seven schedule rows (one per weekday) to `public.weekly_schedules`

Confirm them visually in **Supabase Table Editor**, then delete them manually.

> The script never prints database credentials, passwords, host names, or connection URLs.

---

## Daily Override Persistence ✅

`public.daily_overrides` is the third table actively used by the FastAPI backend.

### Architecture

The Daily Override API (`PUT`, `GET`, `DELETE /api/users/{user_id}/daily-overrides/{override_date}`) routes through a **repository layer** (`app/repositories/daily_override_repository.py`):

| `STORAGE_BACKEND` | Implementation | Used by |
|---|---|---|
| `memory` (default) | `MemoryDailyOverrideRepository` | All automated tests |
| `postgres` | `PostgresDailyOverrideRepository` | Local Supabase / production |

### One row per user per date

Daily overrides are keyed by `(user_id, override_date)`. They are stored separately from the weekly schedule and **never modify the regular weekly timetable**. The Supabase `UNIQUE (user_id, override_date)` constraint prevents duplicate overrides for the same date.

Each row contains:
- `user_id` — foreign key to `public.student_profiles` (ON DELETE CASCADE)
- `override_date` — the specific date this applies to
- `situation` — e.g. `"Internal exam / Test"`, `"Free day"`, `"Assignment"` etc.
- `extra_available_minutes` — temporary DSA time adjustment (-240 to +480)
- `energy_level` — `"Low"`, `"Normal"`, or `"High"`
- `note` — optional student note (≤ 200 characters)

### Smart Daily Plan integration

`GET /api/users/{user_id}/daily-plan/{plan_date}` now reads daily overrides through `get_optional_daily_override()` (in `app/services/daily_override_service.py`), which delegates to whichever repository is active:

- In **memory mode**: reads from `DAILY_OVERRIDE_STORE` dict (identical to pre-migration behaviour).
- In **postgres mode**: reads from `public.daily_overrides` — a persisted override survives backend restarts and affects the derived workload, available minutes, task list, and recommendations exactly as in memory mode.

### Service layer

`app/services/daily_override_service.py` provides:

| Function | Used by | Behaviour on missing override |
|---|---|---|
| `require_daily_override(user_id, date)` | GET / DELETE endpoints | Raises HTTP 404 |
| `get_optional_daily_override(user_id, date)` | Smart Daily Plan | Returns `None` |

### Unit tests

Automated tests always run in `memory` mode. No test connects to the real Supabase project. The `conftest.py` Layer 3 guard additionally blocks `PostgresDailyOverrideRepository._engine()` from being called.

### Manual verification

After setting `STORAGE_BACKEND=postgres` in `backend/.env`, run from the `backend/` folder:

```bash
python -m scripts.smoke_test_daily_override_persistence
```

This writes:
- One test row to `public.student_profiles` (`demo-user-override-db-test`)
- Seven schedule rows to `public.weekly_schedules`
- One override row to `public.daily_overrides` (date: `2026-05-22`)

And then generates a Smart Daily Plan via the service layer and asserts the persisted Internal exam override is applied correctly.

### Cascade delete

After visual confirmation in Supabase Table Editor, delete only the `student_profiles` row for `demo-user-override-db-test`. The `ON DELETE CASCADE` policy automatically removes the related `weekly_schedules` (7 rows) and `daily_overrides` (1 row) for that user.

> The script never prints database credentials, passwords, host names, or connection URLs.
