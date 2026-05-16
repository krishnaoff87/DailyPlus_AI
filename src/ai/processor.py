"""AI processor with LangChain + Claude and strict Pydantic schemas."""

import json
from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from config.settings import settings
from src.ingest.loader import MockContextItem


class ActionItem(BaseModel):
    """Pydantic model for action items extracted from daily context."""

    task: str
    assignee: str
    deadline: str | None
    priority: Literal["urgent", "high", "medium", "low"]


class DailyBriefing(BaseModel):
    """Pydantic model for daily briefing with summary, actions, and stakeholders."""

    summary: str
    actions: list[ActionItem]
    stakeholders: list[str]


def process_daily_context(items: list[MockContextItem]) -> DailyBriefing:
    """
    Process daily context items using Claude AI to extract briefing information.

    Args:
        items: List of validated MockContextItem objects

    Returns:
        DailyBriefing: Validated briefing with summary, actions, and stakeholders

    Raises:
        ValueError: If API key is missing or AI response is invalid after retries
    """
    # Initialize Claude with exact model name
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=settings.ANTHROPIC_API_KEY,
        temperature=0.2,
    )

    # Format items for the prompt
    items_text = "\n\n".join(
        [
            f"Item {idx + 1}:\n"
            f"Source: {item.source}\n"
            f"Timestamp: {item.timestamp}\n"
            f"Subject: {item.subject}\n"
            f"Body: {item.body}\n"
            f"Sender: {item.sender}\n"
            f"Participants: {', '.join(item.participants)}\n"
            f"Urgency: {item.urgency_hint}\n"
            f"Has Action: {item.has_action}"
            for idx, item in enumerate(items)
        ]
    )

    # Create prompt with strict JSON schema instructions
    prompt = f"""Analyze these work items and extract:
1. A 3-bullet summary of the day
2. All actionable items with task, assignee, deadline, priority
3. List of all stakeholders mentioned

Return ONLY valid JSON matching this schema:
{{
  "summary": "• Bullet 1\\n• Bullet 2\\n• Bullet 3",
  "actions": [{{"task": "...", "assignee": "...", "deadline": "...", "priority": "urgent|high|medium|low"}}],
  "stakeholders": ["name1", "name2"]
}}

Work Items:
{items_text}

Remember: Return ONLY the JSON object, no additional text or explanation."""

    # Retry logic: max 2 attempts
    max_attempts = 2
    last_error = None

    for attempt in range(max_attempts):
        try:
            # Invoke Claude
            message = HumanMessage(content=prompt)
            response = llm.invoke([message])

            # Extract content from response
            response_text = response.content.strip()

            # Parse JSON response
            parsed_data = json.loads(response_text)

            # Validate with Pydantic
            briefing = DailyBriefing.model_validate(parsed_data)

            return briefing

        except json.JSONDecodeError as e:
            last_error = f"JSON parsing error on attempt {attempt + 1}: {e}"
        except Exception as e:
            last_error = f"Validation error on attempt {attempt + 1}: {e}"

    # If all attempts failed, raise clear error
    raise ValueError(
        f"Failed to process daily context after {max_attempts} attempts.\n"
        f"Last error: {last_error}\n"
        f"Please check that the AI response matches the expected JSON schema."
    )


__all__ = ["ActionItem", "DailyBriefing", "process_daily_context"]

# Made with Bob
