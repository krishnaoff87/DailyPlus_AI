"""
DailyPlus_AI PoC - Complete Streamlit Application
Full dashboard with Morning Briefing, Action Board, and Draft Generator.
"""

import streamlit as st
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
import time

from config.settings import settings
from src.ingest.loader import load_mock_data
from src.ai.processor import process_daily_context
from src.ai.prioritizer import sort_actions_by_priority, calculate_priority_score

# Set page configuration
st.set_page_config(page_title="DailyPlus_AI PoC", page_icon="🚀", layout="wide")

# Initialize session state
if "briefing" not in st.session_state:
    st.session_state.briefing = None
if "mock_items" not in st.session_state:
    st.session_state.mock_items = None
if "draft_context" not in st.session_state:
    st.session_state.draft_context = ""
if "last_load_time" not in st.session_state:
    st.session_state.last_load_time = None

# Display header
st.header("🚀 DailyPlus_AI - Executive Dashboard")

# Load Data Button
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔄 Load Daily Context", type="primary"):
        max_retries = 2
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                if retry_count > 0:
                    st.info(f"🔄 Retry attempt {retry_count}/{max_retries - 1}...")
                    time.sleep(1)  # Brief delay before retry

                with st.spinner(
                    f"Loading and processing daily context... {'(Retry)' if retry_count > 0 else ''}"
                ):
                    # Load mock data
                    mock_items = load_mock_data()
                    st.session_state.mock_items = mock_items

                    # Process with AI
                    briefing = process_daily_context(mock_items)
                    st.session_state.briefing = briefing
                    st.session_state.last_load_time = datetime.now()

                st.success(f"✅ Loaded {len(mock_items)} items successfully!")
                st.toast("✅ Daily context loaded!", icon="✅")
                success = True

            except ValueError as e:
                error_msg = str(e)
                if "api_key" in error_msg.lower() or "anthropic" in error_msg.lower():
                    st.error("❌ API Key Error")
                    st.warning(
                        "**Troubleshooting:**\n"
                        "1. Check that `config/.env` file exists\n"
                        "2. Verify `ANTHROPIC_API_KEY` is set correctly\n"
                        "3. Ensure API key is valid and has credits\n"
                        "4. Restart the application after updating .env"
                    )
                    break  # Don't retry for API key errors
                elif "mock data file not found" in error_msg.lower():
                    st.error("❌ Data File Missing")
                    st.warning(
                        "**Troubleshooting:**\n"
                        "1. Ensure `data/mock_daily_context.json` exists\n"
                        "2. Check file permissions\n"
                        "3. Verify you're in the correct directory"
                    )
                    break  # Don't retry for missing files
                else:
                    retry_count += 1
                    if retry_count >= max_retries:
                        st.error(f"❌ Error after {max_retries} attempts: {error_msg}")
                        st.warning(
                            "**Troubleshooting:**\n"
                            "1. Check your internet connection\n"
                            "2. Verify API key has sufficient credits\n"
                            "3. Try again in a few moments\n"
                            "4. Check logs for detailed error information"
                        )

            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    st.error(f"❌ Unexpected error after {max_retries} attempts")
                    st.code(str(e), language=None)
                    st.warning(
                        "**Troubleshooting:**\n"
                        "1. Check application logs for details\n"
                        "2. Verify all dependencies are installed: `uv sync`\n"
                        "3. Restart the application\n"
                        "4. Report this issue if it persists"
                    )

with col2:
    if st.session_state.last_load_time:
        st.info(
            f"Last updated: {st.session_state.last_load_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

st.divider()

# Create tabs
tab1, tab2, tab3 = st.tabs(
    ["📅 Morning Briefing", "✅ Action Board", "📝 Draft Generator"]
)

# Tab 1: Morning Briefing
with tab1:
    st.subheader("📅 Morning Briefing")

    if st.session_state.briefing:
        briefing = st.session_state.briefing

        # Display summary
        st.markdown("### Daily Summary")
        st.markdown(briefing.summary)

        st.divider()

        # Display stakeholders as badges
        st.markdown("### Key Stakeholders")
        if briefing.stakeholders:
            # Create columns for stakeholder badges
            cols = st.columns(min(len(briefing.stakeholders), 5))
            for idx, stakeholder in enumerate(briefing.stakeholders):
                with cols[idx % 5]:
                    st.markdown(f"👤 **{stakeholder}**")
        else:
            st.info("No stakeholders identified")

        st.divider()

        # Display action count
        st.metric("Total Actions", len(briefing.actions))

    else:
        st.info("👆 Click 'Load Daily Context' to generate your morning briefing")

# Tab 2: Action Board
with tab2:
    st.subheader("✅ Action Board")

    if st.session_state.briefing:
        briefing = st.session_state.briefing

        # Sort actions by priority
        sorted_actions = sort_actions_by_priority(briefing.actions)

        # Display total count
        st.metric("Total Actions", len(sorted_actions))

        st.divider()

        # Priority color mapping
        priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

        # Display actions in a table format
        if sorted_actions:
            for idx, action in enumerate(sorted_actions):
                score = calculate_priority_score(action)
                priority_display = f"{priority_emoji.get(action.priority, '⚪')} {action.priority.upper()}"

                # Create expandable section for each action
                with st.expander(
                    f"**{action.task}** - {priority_display} (Score: {score})",
                    expanded=(idx < 3),
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Assignee:** {action.assignee}")

                    with col2:
                        deadline_text = (
                            action.deadline if action.deadline else "No deadline"
                        )
                        st.markdown(f"**Deadline:** {deadline_text}")

                    with col3:
                        st.markdown(f"**Priority Score:** {score}/6")

                    # Non-functional checkbox for PoC
                    st.checkbox("Mark as complete", key=f"action_{idx}", disabled=True)
        else:
            st.info("No actions found")
    else:
        st.info("👆 Click 'Load Daily Context' to view your action items")

# Tab 3: Draft Generator
with tab3:
    st.subheader("📝 Draft Generator")

    st.markdown("Generate professional drafts using AI")

    # Context input
    draft_context = st.text_area(
        "Enter context for draft generation:",
        value="Reply to client proposal request",
        height=100,
        key="draft_input",
    )

    # Generate button
    if st.button("✨ Generate Draft", type="primary"):
        if not draft_context.strip():
            st.warning("⚠️ Please enter some context for the draft")
        else:
            max_retries = 2
            retry_count = 0
            success = False

            while retry_count < max_retries and not success:
                try:
                    if retry_count > 0:
                        st.info(f"🔄 Retry attempt {retry_count}/{max_retries - 1}...")
                        time.sleep(1)  # Brief delay before retry

                    with st.spinner(
                        f"Generating professional draft... {'(Retry)' if retry_count > 0 else ''}"
                    ):
                        # Initialize Claude
                        llm = ChatAnthropic(
                            model="claude-3-5-sonnet-20241022",
                            api_key=settings.ANTHROPIC_API_KEY,
                            temperature=0.7,
                        )

                        # Create prompt
                        prompt = f"""Generate a professional, concise reply (under 50 words) for the following context:

{draft_context}

Keep it professional, clear, and actionable. Return only the draft text, no explanations."""

                        # Generate draft
                        message = HumanMessage(content=prompt)
                        response = llm.invoke([message])
                        draft_text = response.content.strip()

                        # Display generated draft
                        st.success("✅ Draft generated successfully!")
                        st.toast("✅ Draft ready!", icon="✅")
                        st.markdown("### Generated Draft:")
                        st.code(draft_text, language=None)

                        # Copy button hint
                        st.info(
                            "💡 Use the copy button in the top-right corner of the code block above"
                        )
                        success = True

                except ValueError as e:
                    error_msg = str(e)
                    if (
                        "api_key" in error_msg.lower()
                        or "anthropic" in error_msg.lower()
                    ):
                        st.error("❌ API Key Error")
                        st.warning(
                            "**Troubleshooting:**\n"
                            "1. Check that `config/.env` file exists\n"
                            "2. Verify `ANTHROPIC_API_KEY` is set correctly\n"
                            "3. Ensure API key is valid and has credits\n"
                            "4. Restart the application after updating .env"
                        )
                        break  # Don't retry for API key errors
                    else:
                        retry_count += 1
                        if retry_count >= max_retries:
                            st.error(
                                f"❌ Error after {max_retries} attempts: {error_msg}"
                            )
                            st.warning(
                                "**Troubleshooting:**\n"
                                "1. Check your internet connection\n"
                                "2. Verify API key has sufficient credits\n"
                                "3. Try again in a few moments"
                            )

                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        st.error(
                            f"❌ Error generating draft after {max_retries} attempts"
                        )
                        st.code(str(e), language=None)
                        st.warning(
                            "**Troubleshooting:**\n"
                            "1. Check your internet connection\n"
                            "2. Verify API key is valid\n"
                            "3. Try with simpler context\n"
                            "4. Restart the application if issue persists"
                        )

    st.divider()

    # Example contexts
    st.markdown("### Example Contexts:")
    examples = [
        "Reply to client proposal request",
        "Follow-up email after meeting",
        "Status update for project stakeholders",
        "Request for deadline extension",
    ]

    for example in examples:
        if st.button(f"📋 {example}", key=f"example_{example}"):
            st.session_state.draft_context = example
            st.rerun()

# Made with Bob
