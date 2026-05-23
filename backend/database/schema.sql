-- =============================================================================
-- AlgoMentor AI — Supabase PostgreSQL Schema
-- =============================================================================
-- Run this entire file once in the Supabase SQL Editor (Project → SQL Editor).
-- It is safe to re-run: every statement uses IF NOT EXISTS or CREATE OR REPLACE.
--
-- Tables created:
--   1. public.student_profiles
--   2. public.weekly_schedules
--   3. public.daily_overrides
--   4. public.topic_revision_states
--   5. public.topic_review_history
--
-- Row Level Security is ENABLED on all tables.
-- Auth policies will be added in the auth integration phase.
-- =============================================================================


-- =============================================================================
-- Reusable trigger function: automatically update updated_at on every UPDATE.
-- =============================================================================

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;


-- =============================================================================
-- 1. student_profiles
--
-- One row per student. Stores all long-term profile/onboarding data.
-- Serves as the parent for all other tables via foreign key.
-- =============================================================================

create table if not exists public.student_profiles (
    user_id                 text        primary key,
    name                    text        not null,
    goal                    text        not null,
    current_topic           text        not null,
    completed_topics        text[]      not null default '{}',
    weak_concepts           text[]      not null default '{}',
    preferred_study_time    text        not null,
    minimum_daily_minutes   integer     not null,
    maximum_daily_minutes   integer     not null,
    created_at              timestamptz not null default now(),
    updated_at              timestamptz not null default now(),

    -- Name must be between 2 and 60 characters.
    constraint chk_profiles_name_length
        check (char_length(name) between 2 and 60),

    -- Study time budget bounds.
    constraint chk_profiles_min_minutes
        check (minimum_daily_minutes between 10 and 240),
    constraint chk_profiles_max_minutes
        check (maximum_daily_minutes between 20 and 480),

    -- Maximum must be at least as large as minimum.
    constraint chk_profiles_minutes_order
        check (maximum_daily_minutes >= minimum_daily_minutes),

    -- Allowed goal values (mirrors the Pydantic Literal in models.py).
    constraint chk_profiles_goal
        check (goal in (
            'Beginner DSA',
            'College Practice',
            'Internship Prep',
            'Placement Prep',
            'Competitive Programming'
        )),

    -- Allowed preferred study time slots.
    constraint chk_profiles_study_time
        check (preferred_study_time in ('Morning', 'Afternoon', 'Evening', 'Night'))
);

-- updated_at trigger
create or replace trigger trg_student_profiles_updated_at
    before update on public.student_profiles
    for each row execute function public.set_updated_at();

-- Row Level Security (no policies yet — will be added in auth phase)
alter table public.student_profiles enable row level security;


-- =============================================================================
-- 2. weekly_schedules
--
-- One row per user per weekday (7 rows per student).
-- The `classes` column holds a JSON array of {title, start_time, end_time} objects.
-- Class-slot ordering and overlap validation remain at the FastAPI layer.
-- =============================================================================

create table if not exists public.weekly_schedules (
    id          bigint      generated always as identity primary key,
    user_id     text        not null references public.student_profiles(user_id) on delete cascade,
    day_name    text        not null,
    is_free_day boolean     not null default false,
    classes     jsonb       not null default '[]'::jsonb,
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now(),

    -- Each student can have at most one entry per weekday.
    constraint uq_weekly_schedules_user_day
        unique (user_id, day_name),

    -- Only the seven canonical day names are accepted.
    constraint chk_weekly_schedules_day_name
        check (day_name in ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),

    -- The classes column must always be a JSON array (never an object, scalar, or null).
    constraint chk_weekly_schedules_classes_is_array
        check (jsonb_typeof(classes) = 'array'),

    -- A free day must have an empty classes array.
    -- Application-level validation also enforces this, but the DB adds a safety net.
    constraint chk_weekly_schedules_free_day_no_classes
        check (
            not is_free_day
            or classes = '[]'::jsonb
        )
);


-- updated_at trigger
create or replace trigger trg_weekly_schedules_updated_at
    before update on public.weekly_schedules
    for each row execute function public.set_updated_at();

-- Row Level Security
alter table public.weekly_schedules enable row level security;


-- =============================================================================
-- 3. daily_overrides
--
-- One optional row per student per calendar date.
-- Captures temporary deviations from the regular timetable (exam day, free day, etc.).
-- =============================================================================

create table if not exists public.daily_overrides (
    id                      bigint      generated always as identity primary key,
    user_id                 text        not null references public.student_profiles(user_id) on delete cascade,
    override_date           date        not null,
    situation               text        not null default 'Normal day',
    extra_available_minutes integer     not null default 0,
    energy_level            text        not null default 'Normal',
    note                    text,
    created_at              timestamptz not null default now(),
    updated_at              timestamptz not null default now(),

    -- Each student has at most one override per date.
    constraint uq_daily_overrides_user_date
        unique (user_id, override_date),

    -- Allowed situation types.
    constraint chk_daily_overrides_situation
        check (situation in (
            'Normal day',
            'Assignment',
            'Internal exam / Test',
            'Project work',
            'Event / Hackathon',
            'Free day'
        )),

    -- Extra minutes are clamped to a sensible range.
    constraint chk_daily_overrides_extra_minutes
        check (extra_available_minutes between -240 and 480),

    -- Energy level options.
    constraint chk_daily_overrides_energy_level
        check (energy_level in ('Low', 'Normal', 'High')),

    -- Optional note is capped at 200 characters.
    constraint chk_daily_overrides_note_length
        check (note is null or char_length(note) <= 200)
);

-- updated_at trigger
create or replace trigger trg_daily_overrides_updated_at
    before update on public.daily_overrides
    for each row execute function public.set_updated_at();

-- Row Level Security
alter table public.daily_overrides enable row level security;


-- =============================================================================
-- 4. topic_revision_states
--
-- One row per student per tracked DSA topic.
-- Holds the current SM-2 state (repetitions, interval, easiness factor, etc.).
-- Updated in-place after every successful review submission.
-- =============================================================================

create table if not exists public.topic_revision_states (
    id                  bigint          generated always as identity primary key,
    user_id             text            not null references public.student_profiles(user_id) on delete cascade,
    topic               text            not null,
    repetitions         integer         not null default 0,
    interval_days       integer         not null default 0,
    easiness_factor     numeric(4, 2)   not null default 2.50,
    last_quality        integer         not null,
    last_reviewed_on    date            not null,
    next_review_date    date            not null,
    total_reviews       integer         not null default 1,
    created_at          timestamptz     not null default now(),
    updated_at          timestamptz     not null default now(),

    -- One SM-2 state record per topic per student.
    constraint uq_topic_revision_states_user_topic
        unique (user_id, topic),

    -- SM-2 invariants.
    constraint chk_topic_revision_states_repetitions
        check (repetitions >= 0),
    constraint chk_topic_revision_states_interval_days
        check (interval_days >= 0),
    constraint chk_topic_revision_states_easiness_factor
        check (easiness_factor >= 1.30),
    constraint chk_topic_revision_states_last_quality
        check (last_quality between 0 and 5),
    constraint chk_topic_revision_states_total_reviews
        check (total_reviews >= 1)
);

-- updated_at trigger
create or replace trigger trg_topic_revision_states_updated_at
    before update on public.topic_revision_states
    for each row execute function public.set_updated_at();

-- Index: daily plan service queries by user + next_review_date to find due topics.
create index if not exists idx_topic_revision_states_user_next_review
    on public.topic_revision_states (user_id, next_review_date);

-- Row Level Security
alter table public.topic_revision_states enable row level security;


-- =============================================================================
-- 5. topic_review_history
--
-- Append-only audit trail. One row per review event.
-- Never updated — no updated_at column, no trigger needed.
-- =============================================================================

create table if not exists public.topic_review_history (
    id                          bigint          generated always as identity primary key,
    user_id                     text            not null references public.student_profiles(user_id) on delete cascade,
    topic                       text            not null,
    quality                     integer         not null,
    reviewed_on                 date            not null,
    interval_days_after_review  integer         not null,
    easiness_factor_after_review numeric(4, 2)  not null,
    next_review_date            date            not null,
    created_at                  timestamptz     not null default now(),

    -- Quality must be a valid SM-2 score.
    constraint chk_topic_review_history_quality
        check (quality between 0 and 5),

    -- Interval must be non-negative.
    constraint chk_topic_review_history_interval
        check (interval_days_after_review >= 0),

    -- Easiness factor lower bound.
    constraint chk_topic_review_history_ef
        check (easiness_factor_after_review >= 1.30)
);

-- Index: fetch review history for a specific topic in chronological order.
create index if not exists idx_topic_review_history_user_topic_date
    on public.topic_review_history (user_id, topic, reviewed_on desc);

-- Index: look up all reviews scheduled around a specific date.
create index if not exists idx_topic_review_history_user_next_review
    on public.topic_review_history (user_id, next_review_date);

-- Row Level Security
alter table public.topic_review_history enable row level security;


-- =============================================================================
-- End of schema.sql
--
-- NEXT STEPS (do not run yet):
--   1. Paste this file into Supabase SQL Editor and execute.
--   2. In the auth integration phase, add RLS policies per table.
--   3. Generate the connection URL from Supabase Project Settings → Database.
--   4. Store it as a secret in the FastAPI environment (never commit to git).
--   5. Wire asyncpg / psycopg in the FastAPI services layer.
-- =============================================================================
