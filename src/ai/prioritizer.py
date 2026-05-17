"""Priority scoring engine using Eisenhower matrix principles."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ai.processor import ActionItem


def calculate_priority_score(action: "ActionItem") -> int:
    """
    Calculate priority score for an action item using Eisenhower matrix.

    Scoring rules:
    - urgent: 4 points
    - high: 3 points
    - medium: 2 points
    - low: 1 point
    - deadline within 24h (today, EOD, ASAP): +2 points
    - no deadline: +0 points

    Args:
        action: ActionItem to score

    Returns:
        int: Priority score (1-6 range)
    """
    # Base score from priority level
    priority_scores = {
        "urgent": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    score = priority_scores.get(action.priority, 1)

    # Add deadline urgency bonus
    if action.deadline:
        deadline_lower = action.deadline.lower()
        urgent_keywords = ["today", "eod", "asap"]

        if any(keyword in deadline_lower for keyword in urgent_keywords):
            score += 2

    return score


def sort_actions_by_priority(actions: list[ActionItem]) -> list[ActionItem]:
    """
    Sort action items by priority score in descending order.

    Args:
        actions: List of ActionItem objects

    Returns:
        list[ActionItem]: Sorted list with highest priority first
    """
    return sorted(actions, key=calculate_priority_score, reverse=True)


__all__ = ["calculate_priority_score", "sort_actions_by_priority"]

# Made with Bob
