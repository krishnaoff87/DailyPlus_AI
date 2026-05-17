"""Basic pytest scaffolds for DailyPlus_AI PoC."""

import pytest
from src.ingest.loader import load_mock_data, MockContextItem
from src.ai.processor import ActionItem
from src.ai.prioritizer import calculate_priority_score, sort_actions_by_priority


def test_load_mock_data_returns_9_items():
    """Test that load_mock_data() returns exactly 9 items from mock data."""
    items = load_mock_data()
    assert len(items) == 9, f"Expected 9 items, got {len(items)}"
    assert all(isinstance(item, MockContextItem) for item in items)


def test_mock_context_item_validation():
    """Test MockContextItem Pydantic validation with valid data."""
    valid_item = MockContextItem(
        id="test_001",
        source="email",
        timestamp="2026-05-16T08:30:00Z",
        subject="Test Subject",
        body="Test body content",
        sender="test@example.com",
        participants=["test@example.com", "user@example.com"],
        urgency_hint="high",
        has_action=True,
    )

    assert valid_item.id == "test_001"
    assert valid_item.source == "email"
    assert valid_item.urgency_hint == "high"
    assert valid_item.has_action is True


def test_mock_context_item_validation_invalid_source():
    """Test MockContextItem validation fails with invalid source."""
    with pytest.raises(Exception):  # Pydantic ValidationError
        MockContextItem(
            id="test_002",
            source="invalid_source",  # Not in Literal["email", "calendar", "chat"]
            timestamp="2026-05-16T08:30:00Z",
            subject="Test",
            body="Test",
            sender="test@example.com",
            participants=["test@example.com"],
            urgency_hint="high",
            has_action=False,
        )


def test_calculate_priority_score_urgent():
    """Test priority score calculation for urgent action."""
    action = ActionItem(
        task="Urgent task", assignee="John", deadline="today", priority="urgent"
    )

    score = calculate_priority_score(action)
    assert score == 6, f"Expected score 6 (urgent=4 + today=2), got {score}"


def test_calculate_priority_score_high_with_eod():
    """Test priority score calculation for high priority with EOD deadline."""
    action = ActionItem(
        task="High priority task", assignee="Sarah", deadline="EOD", priority="high"
    )

    score = calculate_priority_score(action)
    assert score == 5, f"Expected score 5 (high=3 + EOD=2), got {score}"


def test_calculate_priority_score_medium_no_deadline():
    """Test priority score calculation for medium priority without deadline."""
    action = ActionItem(
        task="Medium task", assignee="Mike", deadline=None, priority="medium"
    )

    score = calculate_priority_score(action)
    assert score == 2, f"Expected score 2 (medium=2 + no deadline=0), got {score}"


def test_calculate_priority_score_low():
    """Test priority score calculation for low priority."""
    action = ActionItem(
        task="Low priority task", assignee="Emily", deadline="next week", priority="low"
    )

    score = calculate_priority_score(action)
    assert score == 1, f"Expected score 1 (low=1 + no urgent keyword=0), got {score}"


def test_sort_actions_by_priority():
    """Test that actions are sorted correctly by priority score."""
    actions = [
        ActionItem(task="Low task", assignee="A", deadline=None, priority="low"),
        ActionItem(
            task="Urgent task", assignee="B", deadline="today", priority="urgent"
        ),
        ActionItem(task="Medium task", assignee="C", deadline=None, priority="medium"),
        ActionItem(task="High task", assignee="D", deadline="ASAP", priority="high"),
    ]

    sorted_actions = sort_actions_by_priority(actions)

    # Verify order: urgent+today (6) > high+ASAP (5) > medium (2) > low (1)
    assert sorted_actions[0].task == "Urgent task"
    assert sorted_actions[1].task == "High task"
    assert sorted_actions[2].task == "Medium task"
    assert sorted_actions[3].task == "Low task"

    # Verify scores are in descending order
    scores = [calculate_priority_score(action) for action in sorted_actions]
    assert scores == sorted(
        scores, reverse=True
    ), "Actions not sorted by priority score"


def test_sort_actions_by_priority_empty_list():
    """Test sorting empty action list."""
    sorted_actions = sort_actions_by_priority([])
    assert sorted_actions == []


def test_action_item_validation():
    """Test ActionItem Pydantic validation."""
    action = ActionItem(
        task="Test task", assignee="John Doe", deadline="2026-05-20", priority="high"
    )

    assert action.task == "Test task"
    assert action.assignee == "John Doe"
    assert action.deadline == "2026-05-20"
    assert action.priority == "high"


def test_action_item_validation_invalid_priority():
    """Test ActionItem validation fails with invalid priority."""
    with pytest.raises(Exception):  # Pydantic ValidationError
        ActionItem(
            task="Test",
            assignee="John",
            deadline=None,
            priority="invalid_priority",  # Not in Literal
        )


# Made with Bob
