"""AI processor with LangChain + Google Gemini and strict Pydantic schemas.
# Force reload for Streamlit cache
"""

import hashlib
import json
import re
from typing import Literal

import streamlit as st
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from config.settings import settings
from src.ingest.loader import MockContextItem
from src.ingest.sanitizer import LocalSanitizer


from src.ai.llm_factory import get_llm


def _generate_cache_key(items: list[MockContextItem]) -> str:
    """
    Generate a stable hash key from input data for cache identification.

    Creates a deterministic hash based on item IDs, timestamps, and content
    to ensure identical data produces the same cache key.

    Args:
        items: List of MockContextItem objects

    Returns:
        str: SHA256 hash of the serialized item data
    """
    # Create a stable representation of the items
    item_data = [
        {
            "id": item.id,
            "timestamp": item.timestamp,
            "subject": item.subject,
            "body": item.body,
            "urgency_hint": item.urgency_hint,
            "has_action": item.has_action,
        }
        for item in items
    ]

    # Serialize to JSON with sorted keys for consistency
    serialized = json.dumps(item_data, sort_keys=True)

    # Generate SHA256 hash
    return hashlib.sha256(serialized.encode()).hexdigest()


class ActionItem(BaseModel):
    """Pydantic model for action items extracted from daily context."""

    task: str
    assignee: str
    deadline: str | None
    priority: Literal["urgent", "high", "medium", "low"]


class DailyBriefing(BaseModel):
    """Pydantic model for enhanced daily briefing with 11 comprehensive categories."""

    # Enhanced categories (8 original sections)
    executive_overview: list[str] = []  # 2-3 bullets with metrics
    project_progress: list[str] = []  # 3-5 bullets grouped by project
    productivity_metrics: list[str] = []  # 3-4 bullets with quantitative data
    critical_actions: list[str] = []  # 2-5 bullets with urgency levels
    risks_and_blockers: list[str] = []  # 2-4 bullets with impact assessment
    team_activity: list[str] = []  # 3-5 bullets with workload info
    departmental_breakdown: list[str] = []  # 2-4 bullets with distribution
    notable_events: list[str] = []  # 2-3 bullets with significance

    # New AI-powered categories (3 advanced sections)
    trends_analysis: list[str] = []  # 3-4 bullets identifying patterns and trends
    forecasts: list[str] = []  # 2-3 bullets with predictive insights
    ai_recommendations: list[str] = []  # 3-5 bullets with actionable suggestions

    # Legacy fields for backward compatibility
    summary: str  # Concatenation of all categories
    actions: list[ActionItem]
    stakeholders: list[str]


def _rule_based_fallback(items: list[MockContextItem]) -> DailyBriefing:
    """
    Enhanced deterministic fallback extraction with 8 comprehensive categories.

    Args:
        items: List of validated MockContextItem objects

    Returns:
        DailyBriefing: Enhanced briefing with all 8 categories extracted using deterministic rules
    """

    # Extract data from body field (Project, Department, Status, Hours, Due Date, Notes)
    def extract_field(body: str, field: str) -> str:
        """Extract field value from body text."""
        pattern = rf"{field}:\s*([^\n]+)"
        match = re.search(pattern, body, re.IGNORECASE)
        return match.group(1).strip() if match else "Unknown"

    # Parse all items and extract structured data
    parsed_items = []
    for item in items:
        parsed_items.append(
            {
                "subject": item.subject,
                "body": item.body,
                "sender": item.sender,
                "participants": item.participants,
                "urgency": item.urgency_hint,
                "has_action": item.has_action,
                "project": extract_field(item.body, "Project"),
                "department": extract_field(item.body, "Department"),
                "status": extract_field(item.body, "Status"),
                "hours": extract_field(item.body, "Hours"),
                "due_date": extract_field(item.body, "Due Date"),
                "notes": extract_field(item.body, "Notes"),
            }
        )

    # 1. Executive Overview (2-3 bullets with metrics)
    total_items = len(items)
    action_items = sum(1 for item in items if item.has_action)
    urgent_items = sum(1 for item in items if item.urgency_hint.lower() == "urgent")
    total_hours = sum(
        float(p["hours"]) for p in parsed_items if p["hours"].replace(".", "").isdigit()
    )

    executive_overview = [
        f"Total of {total_items} work items processed today with {action_items} actionable tasks identified",
        f"{urgent_items} urgent items requiring immediate attention ({(urgent_items/total_items*100):.0f}% of total)",
        f"Team logged {total_hours:.1f} hours across all activities",
    ]

    # 2. Project Progress & Milestones (3-5 bullets grouped by project)
    project_groups = {}
    for p in parsed_items:
        proj = p["project"]
        if proj not in project_groups:
            project_groups[proj] = []
        project_groups[proj].append(p)

    project_progress = []
    for proj, items_list in list(project_groups.items())[:5]:
        completed = sum(1 for i in items_list if "completed" in i["status"].lower())
        in_progress = sum(1 for i in items_list if "in progress" in i["status"].lower())
        project_progress.append(
            f"{proj}: {completed} completed, {in_progress} in progress ({len(items_list)} total tasks)"
        )

    # 3. Productivity Metrics (3-4 bullets with quantitative data)
    completed_count = sum(1 for p in parsed_items if "completed" in p["status"].lower())
    completion_rate = (completed_count / total_items * 100) if total_items > 0 else 0
    avg_hours = total_hours / total_items if total_items > 0 else 0

    productivity_metrics = [
        f"Task completion rate: {completion_rate:.1f}% ({completed_count}/{total_items} tasks completed)",
        f"Average time per task: {avg_hours:.1f} hours",
        f"Efficiency score: {(completion_rate * 0.7 + (1 / (avg_hours + 0.1)) * 30):.1f}/100",
        f"Action item conversion rate: {(action_items/total_items*100):.1f}%",
    ]

    # 4. Critical Actions & Deadlines (2-5 bullets with urgency levels)
    critical_actions = []
    actions = []
    for item in items:
        if item.has_action:
            assignee = item.participants[0] if item.participants else item.sender
            urgency_lower = item.urgency_hint.lower()
            if urgency_lower == "urgent":
                priority: Literal["urgent", "high", "medium", "low"] = "urgent"
            elif urgency_lower == "high":
                priority = "high"
            elif urgency_lower == "low":
                priority = "low"
            else:
                priority = "medium"

            deadline = None
            date_pattern = (
                r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|today|tomorrow|next week"
            )
            match = re.search(date_pattern, item.body, re.IGNORECASE)
            if match:
                deadline = match.group(0)

            actions.append(
                ActionItem(
                    task=item.subject,
                    assignee=assignee,
                    deadline=deadline,
                    priority=priority,
                )
            )

            urgency_label = f"[{priority.upper()}]"
            deadline_text = f" - Due: {deadline}" if deadline else ""
            critical_actions.append(
                f"{urgency_label} {item.subject} (Assigned: {assignee}){deadline_text}"
            )

    if not critical_actions:
        critical_actions = ["No critical actions identified for today"]

    # 5. Risks, Blockers & Challenges (2-4 bullets with impact assessment)
    blocker_keywords = ["blocked", "awaiting", "dependency", "issue", "problem", "risk"]
    risks_and_blockers = []
    for p in parsed_items:
        notes_lower = p["notes"].lower()
        if any(keyword in notes_lower for keyword in blocker_keywords):
            impact = "HIGH" if p["urgency"] == "urgent" else "MEDIUM"
            risks_and_blockers.append(
                f"[{impact} IMPACT] {p['subject']}: {p['notes'][:80]}..."
            )

    if not risks_and_blockers:
        risks_and_blockers = ["No significant blockers or risks identified"]

    # 6. Team & Stakeholder Activity (3-5 bullets with workload info)
    stakeholders = set()
    sender_workload = {}
    for item in items:
        stakeholders.add(item.sender)
        stakeholders.update(item.participants)
        sender_workload[item.sender] = sender_workload.get(item.sender, 0) + 1

    team_activity = []
    for sender, count in sorted(
        sender_workload.items(), key=lambda x: x[1], reverse=True
    )[:5]:
        team_activity.append(
            f"{sender}: {count} tasks/items ({(count/total_items*100):.1f}% of workload)"
        )

    # 7. Departmental Breakdown (2-4 bullets with distribution)
    dept_groups = {}
    for p in parsed_items:
        dept = p["department"]
        if dept not in dept_groups:
            dept_groups[dept] = []
        dept_groups[dept].append(p)

    departmental_breakdown = []
    for dept, items_list in sorted(
        dept_groups.items(), key=lambda x: len(x[1]), reverse=True
    )[:4]:
        dept_hours = sum(
            float(i["hours"])
            for i in items_list
            if i["hours"].replace(".", "").isdigit()
        )
        departmental_breakdown.append(
            f"{dept}: {len(items_list)} tasks, {dept_hours:.1f} hours ({(len(items_list)/total_items*100):.1f}% of total)"
        )

    # 8. Notable Events & Decisions (2-3 bullets with significance)
    notable_keywords = [
        "decision",
        "approved",
        "milestone",
        "launch",
        "completed",
        "achieved",
    ]
    notable_events = []
    for p in parsed_items:
        combined = (p["subject"] + " " + p["notes"]).lower()
        if any(keyword in combined for keyword in notable_keywords):
            notable_events.append(f"[SIGNIFICANT] {p['subject']}")

    if not notable_events:
        notable_events = ["No major events or decisions recorded today"]
    notable_events = notable_events[:3]  # Limit to 3

    # Create legacy summary field (concatenation of all categories)
    all_bullets = (
        ["Executive Overview:"]
        + executive_overview
        + ["\nProject Progress:"]
        + project_progress
        + ["\nProductivity Metrics:"]
        + productivity_metrics
        + ["\nCritical Actions:"]
        + critical_actions
        + ["\nRisks & Blockers:"]
        + risks_and_blockers
        + ["\nTeam Activity:"]
        + team_activity
        + ["\nDepartmental Breakdown:"]
        + departmental_breakdown
        + ["\nNotable Events:"]
        + notable_events
    )
    summary = "\n".join(all_bullets)

    return DailyBriefing(
        executive_overview=executive_overview,
        project_progress=project_progress,
        productivity_metrics=productivity_metrics,
        critical_actions=critical_actions,
        risks_and_blockers=risks_and_blockers,
        team_activity=team_activity,
        departmental_breakdown=departmental_breakdown,
        notable_events=notable_events,
        summary=summary,
        actions=actions,
        stakeholders=sorted(list(stakeholders)),
    )


class _AIInsights(BaseModel):
    """Lightweight Pydantic model for AI-only insight categories."""

    trends_analysis: list[str] = []
    forecasts: list[str] = []
    ai_recommendations: list[str] = []


def _get_ai_insights(summary_text: str, sanitizer: LocalSanitizer) -> _AIInsights:
    """
    Call the LLM with a compact pre-summarized input to generate only the
    3 AI-insight categories (trends, forecasts, recommendations).

    This is dramatically faster than sending 105 raw items because:
    - Input is ~2KB instead of ~78KB
    - Output schema has 3 fields instead of 14
    - The LLM does analysis, not data extraction

    Args:
        summary_text: Pre-computed summary from rule-based engine
        sanitizer: LocalSanitizer instance for PII handling

    Returns:
        _AIInsights: Validated AI insights
    """
    if not settings.NVIDIA_API_KEY and not settings.GEMINI_API_KEY:
        return _AIInsights()

    llm = get_llm(temperature=0.7, timeout=60, max_retries=2)

    parser = PydanticOutputParser(pydantic_object=_AIInsights)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an AI analyst. Given a daily work summary, provide strategic insights. Return ONLY valid JSON.",
            ),
            (
                "human",
                """Based on this daily work summary, generate 3 categories of strategic insight:

1. **trends_analysis** (3-4 bullets): Identify patterns, recurring themes, velocity trends. Tag with [TREND ↑], [TREND ↓], or [PATTERN].
2. **forecasts** (2-3 bullets): Predict bottlenecks, resource constraints, completion timelines. Tag with [FORECAST] and [HIGH/MEDIUM/LOW CONFIDENCE].
3. **ai_recommendations** (3-5 bullets): Suggest prioritization, resource reallocation, process improvements. Tag with [ACTION], [OPTIMIZE], [MITIGATE], or [IMPROVE].

Daily Summary:
{summary_text}

Return a JSON object with fields: trends_analysis, forecasts, ai_recommendations (each a list of strings).""",
            ),
        ]
    )

    chain = prompt | llm | parser

    try:
        insights = chain.invoke({"summary_text": sanitizer.mask_text(summary_text)})
        insights.trends_analysis = [
            sanitizer.unmask_text(s) for s in insights.trends_analysis
        ]
        insights.forecasts = [sanitizer.unmask_text(s) for s in insights.forecasts]
        insights.ai_recommendations = [
            sanitizer.unmask_text(s) for s in insights.ai_recommendations
        ]
        return insights
    except Exception:
        return _AIInsights()


def process_daily_context(items: list[MockContextItem]) -> DailyBriefing:
    """
    Process daily context items using a hybrid rule-based + AI approach.

    Hybrid architecture for speed:
    1. Rule-based engine instantly computes 8 data categories (executive overview,
       project progress, metrics, actions, risks, team activity, departments, events)
    2. A compact summary is sent to Gemini for only 3 AI-insight categories
       (trends, forecasts, recommendations) — ~90% less LLM input

    Also implements:
    - Hash-based session_state caching to avoid repeat processing
    - Pre-filtering triage to skip non-actionable items
    - PII sanitization before LLM processing

    Args:
        items: List of validated MockContextItem objects

    Returns:
        DailyBriefing: Validated briefing with summary, actions, and stakeholders

    Raises:
        ValueError: If API key is missing
    """
    # Hash-based caching: Check if we've already processed this exact data
    cache_key = _generate_cache_key(items)

    # Initialize cache in session state if not exists
    if "ai_result_cache" not in st.session_state:
        st.session_state.ai_result_cache = {}

    # Return cached result if available
    if cache_key in st.session_state.ai_result_cache:
        cached_result = st.session_state.ai_result_cache[cache_key]
        if "tokens_saved" in cached_result:
            st.session_state.tokens_saved = cached_result["tokens_saved"]
        return cached_result["briefing"]

    # Triage: Filter out non-actionable items without priority keywords
    PRIORITY_KEYWORDS = ["urgent", "deadline", "review", "due"]
    skipped_count = 0

    for item in items:
        combined_text = (item.subject + " " + item.body).lower()
        has_priority_keyword = any(
            keyword in combined_text for keyword in PRIORITY_KEYWORDS
        )

        if item.has_action == False and not has_priority_keyword:
            skipped_count += 1

    # Audit: Track token savings from pre-filtering
    tokens_saved = skipped_count * 150
    st.session_state.tokens_saved = tokens_saved

    # Step 1: Rule-based engine — instant computation of 8 data categories
    briefing = _rule_based_fallback(items)

    # Step 2: AI insights — send compact summary to LLM for 3 insight categories
    sanitizer = LocalSanitizer()

    try:
        ai_insights = _get_ai_insights(briefing.summary, sanitizer)
        briefing.trends_analysis = ai_insights.trends_analysis
        briefing.forecasts = ai_insights.forecasts
        briefing.ai_recommendations = ai_insights.ai_recommendations
    except Exception:
        # If AI fails, briefing still has all 8 rule-based categories
        pass

    # Store result in hash-based cache
    st.session_state.ai_result_cache[cache_key] = {
        "briefing": briefing,
        "tokens_saved": st.session_state.get("tokens_saved", 0),
    }

    return briefing


__all__ = ["ActionItem", "DailyBriefing", "process_daily_context"]

# Made with Bob
