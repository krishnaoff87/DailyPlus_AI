"""Data loader with Pydantic validation for mock daily context items."""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class MockContextItem(BaseModel):
    """Pydantic model for validating mock context items."""

    id: str = Field(..., description="Unique identifier for the item")
    source: Literal["email", "calendar", "chat"] = Field(
        ..., description="Source type of the context item"
    )
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    subject: str = Field(..., description="Subject or title of the item")
    body: str = Field(..., description="Main content of the item")
    sender: str = Field(..., description="Sender name or email")
    participants: list[str] = Field(..., description="List of participants involved")
    urgency_hint: Literal["urgent", "high", "medium", "low"] = Field(
        ..., description="Urgency level hint"
    )
    has_action: bool = Field(..., description="Whether the item contains action items")


def load_mock_data() -> list[MockContextItem]:
    """
    Load and validate mock daily context data from JSON file.

    Cached for 1 hour to avoid repeated file I/O operations.

    Returns:
        list[MockContextItem]: List of validated context items

    Raises:
        ValueError: If file is missing, invalid JSON, or validation fails
    """
    # Construct path relative to project root
    data_file = (
        Path(__file__).resolve().parent.parent.parent
        / "data"
        / "mock_daily_context.json"
    )

    # Check if file exists
    if not data_file.exists():
        raise ValueError(
            f"Mock data file not found at: {data_file}\n"
            f"Please ensure data/mock_daily_context.json exists in the project root."
        )

    # Load and parse JSON
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in mock data file: {data_file}\nError: {e}")
    except Exception as e:
        raise ValueError(f"Failed to read mock data file: {data_file}\nError: {e}")

    # Validate each item with Pydantic
    validated_items = []
    for idx, item_data in enumerate(raw_data):
        try:
            validated_item = MockContextItem(**item_data)
            validated_items.append(validated_item)
        except Exception as e:
            raise ValueError(
                f"Validation failed for item at index {idx} (id: {item_data.get('id', 'unknown')})\n"
                f"Error: {e}"
            )

    return validated_items


__all__ = ["MockContextItem", "load_mock_data"]

# Made with Bob
