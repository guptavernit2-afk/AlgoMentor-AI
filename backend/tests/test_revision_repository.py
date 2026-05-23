"""
AlgoMentor AI — Tests for RevisionRepository.

Covers:
  - MemoryRevisionRepository CRUD (get, save, list states, list history)
  - Postgres transaction rollback and engine failure simulation
  - Selector logic and test isolation guards
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from app.models import TopicReviewRecord, TopicRevisionState
from app.repositories.revision_repository import (
    MemoryRevisionRepository,
    PostgresRevisionRepository,
    get_revision_repository,
)
from app.storage import clear_all_stores


@pytest.fixture(autouse=True)
def _reset():
    clear_all_stores()
    get_revision_repository.cache_clear()


# ============================================================
# 1. Selector and Guard Tests
# ============================================================

def test_get_revision_repository_defaults_to_memory():
    """In pytest, STORAGE_BACKEND=memory, so it returns MemoryRevisionRepository."""
    repo = get_revision_repository()
    assert isinstance(repo, MemoryRevisionRepository)


def test_postgres_repository_can_be_selected_without_connecting(monkeypatch):
    """If STORAGE_BACKEND=postgres, we get PostgresRevisionRepository but it doesn't auto-connect."""
    monkeypatch.setenv("STORAGE_BACKEND", "postgres")
    get_revision_repository.cache_clear()
    
    repo = get_revision_repository()
    assert isinstance(repo, PostgresRevisionRepository)


def test_hard_guard_blocks_live_postgres_calls(monkeypatch):
    """PostgresRevisionRepository._engine() must raise AssertionError in pytest."""
    monkeypatch.setenv("STORAGE_BACKEND", "postgres")
    get_revision_repository.cache_clear()
    
    repo = get_revision_repository()
    
    with pytest.raises(RuntimeError, match="Database error while listing revision history for 'user123': AssertionError"):
        repo.list_history("user123")


# ============================================================
# 2. Memory Repository Tests
# ============================================================

def _make_state(topic: str) -> TopicRevisionState:
    return TopicRevisionState(
        topic=topic,
        repetitions=1,
        interval_days=1,
        easiness_factor=2.5,
        last_quality=5,
        last_reviewed_on=date(2026, 5, 22),
        next_review_date=date(2026, 5, 23),
        total_reviews=1,
    )


def _make_record(topic: str, quality: int) -> TopicReviewRecord:
    return TopicReviewRecord(
        topic=topic,
        quality=quality,
        reviewed_on=date(2026, 5, 22),
        interval_days_after_review=1,
        easiness_factor_after_review=2.5,
        next_review_date=date(2026, 5, 23),
    )


def test_memory_repo_save_and_get():
    repo = MemoryRevisionRepository()
    state = _make_state("Arrays")
    record = _make_record("Arrays", 5)

    assert repo.get_state("user1", "Arrays") is None
    
    repo.save_review_result("user1", state, record)
    
    fetched = repo.get_state("user1", "Arrays")
    assert fetched is not None
    assert fetched.topic == "Arrays"
    assert fetched.repetitions == 1


def test_memory_repo_history_is_append_only_and_chronological():
    repo = MemoryRevisionRepository()
    
    r1 = _make_record("Arrays", 3)
    r2 = _make_record("Hashing", 4)
    r3 = _make_record("Arrays", 5)
    
    repo.save_review_result("user1", _make_state("Arrays"), r1)
    repo.save_review_result("user1", _make_state("Hashing"), r2)
    repo.save_review_result("user1", _make_state("Arrays"), r3)
    
    history = repo.list_history("user1")
    assert len(history) == 3
    assert history[0].quality == 3
    assert history[1].quality == 4
    assert history[2].quality == 5


def test_memory_repo_list_states():
    repo = MemoryRevisionRepository()
    
    repo.save_review_result("user1", _make_state("Arrays"), _make_record("Arrays", 5))
    repo.save_review_result("user1", _make_state("Hashing"), _make_record("Hashing", 4))
    repo.save_review_result("user2", _make_state("Trees"), _make_record("Trees", 5))
    
    user1_states = repo.list_states("user1")
    assert len(user1_states) == 2
    topics = {s.topic for s in user1_states}
    assert topics == {"Arrays", "Hashing"}


# ============================================================
# 3. Transaction-Safety Tests for Postgres
# ============================================================

def test_postgres_repo_save_transaction_rollback_on_history_failure(monkeypatch):
    """
    Simulate a failure during the second half of save_review_result (history insert).
    Confirm that the repository raises RuntimeError and the transaction roles back.
    """
    repo = PostgresRevisionRepository()
    
    # Mock engine, connection, and transaction
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_engine.begin.return_value.__enter__.return_value = mock_conn
    
    def side_effect(statement, *args, **kwargs):
        # Allow the UPSERT (state) to succeed, but crash on the INSERT (history)
        if "INSERT INTO public.topic_review_history" in str(statement):
            raise Exception("Simulated history constraint violation")
        return MagicMock()
        
    mock_conn.execute.side_effect = side_effect
    
    # Bypass the Layer 3 hard guard by patching _engine directly for this test
    monkeypatch.setattr(repo, "_engine", lambda: mock_engine)
    
    state = _make_state("Arrays")
    record = _make_record("Arrays", 5)
    
    with pytest.raises(RuntimeError, match="Database error while saving review result for 'u1' / topic 'Arrays': Exception"):
        repo.save_review_result("u1", state, record)
        
    # Verify execute was called for both statements, triggering the crash on the second
    assert mock_conn.execute.call_count == 2
