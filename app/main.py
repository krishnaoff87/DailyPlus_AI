"""
DailyPlus AI - Grey & White Elegant Theme
Minimal, professional interface with no icons - typography and spacing only
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from datetime import datetime
import time

from src.ingest.loader import load_mock_data
from src.ai.processor import process_daily_context
from src.ai.llm_factory import get_llm
from src.ai.prioritizer import sort_actions_by_priority, calculate_priority_score

# ============================================
# Page Configuration
# ============================================
st.set_page_config(
    page_title="DailyPlus AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================
# Load CSS
# ============================================
def _read_css() -> str:
    """Read CSS file from disk"""
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            return f.read()
    return ""


def load_css():
    """Load custom CSS styling"""
    css_content = _read_css()
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


load_css()


# ============================================
# Custom Rendering Functions
# ============================================
def render_header():
    """Render elegant header with logo"""
    st.markdown(
        """
        <div class="logo">DailyPlus AI</div>
    """,
        unsafe_allow_html=True,
    )


def render_card(title, description):
    """Render a card component with hover effect"""
    st.markdown(
        f"""
        <div class="card">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_section(heading, content=""):
    """Render a content section with fade-in animation"""
    st.markdown(
        f"""
        <div class="content-section">
            <h1>{heading}</h1>
            {f'<p>{content}</p>' if content else ''}
        </div>
    """,
        unsafe_allow_html=True,
    )


# ============================================
# Session State Initialization
# ============================================
if "briefing" not in st.session_state:
    st.session_state.briefing = None
if "mock_items" not in st.session_state:
    st.session_state.mock_items = None
if "draft_context" not in st.session_state:
    st.session_state.draft_context = ""
if "last_load_time" not in st.session_state:
    st.session_state.last_load_time = None
if "tokens_saved" not in st.session_state:
    st.session_state.tokens_saved = 0
if "selected_priority" not in st.session_state:
    st.session_state.selected_priority = None
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# ============================================
# Dynamic Theme Injection
# ============================================
if st.session_state.theme == "dark":
    st.markdown(
        """
    <style>
        :root {
            --bg-main: #0B0F19;
            --bg-card: #161C2D;
            --bg-card-hover: #1E263C;
            
            --text-primary: #F1F5F9; /* Off-white to reduce glare */
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            
            --accent-primary: #3B82F6;
            --accent-hover: #60A5FA;
            
            --border-light: rgba(255, 255, 255, 0.1);
            --border-focus: rgba(59, 130, 246, 0.5);
            
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        }
        
        /* Dark mode specific button adjustments */
        .stButton button[kind="primary"] {
            background-color: var(--accent-primary) !important;
            border-color: var(--accent-primary) !important;
        }
        .stButton button[kind="primary"]:hover {
            background-color: var(--accent-hover) !important;
            border-color: var(--accent-hover) !important;
        }
        .stButton button[kind="secondary"] {
            background-color: transparent !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


# ============================================
# Header & Theme Toggle
# ============================================
# Float the theme button to the top right next to Deploy
st.markdown(
    """
    <style>
    #theme-button-marker {
        display: none;
    }
    /* Streamlit wraps elements in divs. Target the container of the button immediately following our marker */
    div[data-testid="stVerticalBlock"] > div:has(#theme-button-marker) + div {
        position: fixed !important;
        top: 0.5rem !important;
        right: 8rem !important;
        z-index: 9999999 !important;
        width: auto !important;
    }
    div[data-testid="stVerticalBlock"] > div:has(#theme-button-marker) + div button {
        padding: 0.25rem 0.75rem !important;
        border-radius: 20px !important;
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-light) !important;
        color: var(--text-primary) !important;
        cursor: pointer !important;
    }
    </style>
    <div id="theme-button-marker"></div>
""",
    unsafe_allow_html=True,
)

theme_label = "☀️ Light" if st.session_state.theme == "dark" else "🌙 Dark"
if st.button(theme_label, key="theme_toggle"):
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()

render_header()
st.markdown(
    "<p style='text-align: left; color: var(--text-secondary); font-size: 1.2rem; margin-top: -2.5rem; margin-bottom: 2rem;'>Intelligent Workflows. Powerful Insights. Beautifully Simple.</p>",
    unsafe_allow_html=True,
)

st.divider()

# ============================================
# Tabs Section
# ============================================
if not st.session_state.get("briefing"):
    st.markdown('<div id="data-not-loaded-marker"></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab_draft, tab4 = st.tabs(
    ["Overview", "Action Board", "Metrics", "AI Assistance", "Connect"]
)

# ============================================
# Tab 1: Overview
# ============================================
with tab1:
    st.markdown("### Load Your Daily Context")
    st.markdown(
        "<p style='color: var(--text-secondary); margin-bottom: 1.5rem;'>Sync your latest communications, calendar events, and tasks into the AI engine for instant triage and summarization.</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 3, 2])

    with col1:
        btn_text = "Refresh" if st.session_state.briefing else "Load Daily Context"
        load_button = st.button(btn_text, type="primary", use_container_width=True)
        if st.session_state.mock_items and st.session_state.last_load_time:
            st.markdown(
                f"""
                <div style='margin-left: 0.5cm; margin-top: 0.5rem;'>
                    <p style='font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5cm; font-weight: 500;'>Loaded {len(st.session_state.mock_items)} items successfully</p>
                    <p style='font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0;'>Last updated: {st.session_state.last_load_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

    with col2:
        pass  # Empty column to maintain layout spacing

    with col3:
        if st.session_state.briefing:
            st.metric("Items Loaded", len(st.session_state.mock_items or []))

    # Load Data Logic
    if load_button:
        max_retries = 2
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                with st.spinner("Loading and processing daily context..."):
                    if retry_count > 0:
                        st.info(f"Retry attempt {retry_count}/{max_retries - 1}...")
                        time.sleep(1)

                    # Load mock data
                    mock_items = load_mock_data()
                    st.session_state.mock_items = mock_items

                    # Process with AI
                    briefing = process_daily_context(mock_items)
                    st.session_state.briefing = briefing
                    st.session_state.last_load_time = datetime.now()

                success = True

            except ValueError as e:
                error_msg = str(e)

                if "api_key" in error_msg.lower() or "gemini" in error_msg.lower():
                    st.error("❌ API Key Error")
                    st.warning(
                        "Check that config/.env file exists and GEMINI_API_KEY is set correctly"
                    )
                    break
                elif "mock data file not found" in error_msg.lower():
                    st.error("❌ Data File Missing")
                    st.warning("Ensure data/mock_daily_context.json exists")
                    break
                else:
                    retry_count += 1
                    if retry_count >= max_retries:
                        st.error(f"❌ Error after {max_retries} attempts: {error_msg}")

            except Exception as e:
                retry_count += 1

                if retry_count >= max_retries:
                    st.error(f"❌ Unexpected error after {max_retries} attempts")
                    st.code(str(e), language=None)

    if st.session_state.briefing:
        st.divider()
        briefing = st.session_state.briefing

        st.markdown("### Daily Summary Insights")
        st.markdown(
            "<p style='color: var(--text-secondary); margin-bottom: 2rem;'>Here is the comprehensive breakdown of your context, automatically generated by Gemini AI.</p>",
            unsafe_allow_html=True,
        )

        # Define category configurations
        categories = [
            ("Executive Overview", briefing.executive_overview),
            ("Project Progress & Milestones", briefing.project_progress),
            ("Productivity Metrics", briefing.productivity_metrics),
            ("Critical Actions & Deadlines", briefing.critical_actions),
            ("Risks, Blockers & Challenges", briefing.risks_and_blockers),
            ("Team & Stakeholder Activity", briefing.team_activity),
            ("Departmental Breakdown", briefing.departmental_breakdown),
            ("Notable Events & Decisions", briefing.notable_events),
            ("Trends Analysis", briefing.trends_analysis),
            ("Forecasts & Predictions", briefing.forecasts),
            ("AI Recommendations", briefing.ai_recommendations),
        ]

        # Display categories in interactive tabs (auto-closes others)
        active_cats = [(header, items) for header, items in categories if items]
        if active_cats:
            # Create tabs
            insight_tabs = st.tabs([header for header, _ in active_cats])
            for tab, (header, items) in zip(insight_tabs, active_cats):
                with tab:
                    # Make it explicitly bold as requested
                    st.markdown(f"**{header}**")
                    for item in items:
                        st.write(f"• {item}")

# ============================================
# Tab 2: Action Board
# ============================================
with tab2:
    # Action Board (if data loaded)
    if st.session_state.briefing:
        col_head1, col_head2 = st.columns([3, 1])
        with col_head1:
            st.markdown("### Action Board")

        with col_head2:
            if st.session_state.selected_priority:
                if st.button(
                    "Reset Filter", use_container_width=True, type="secondary"
                ):
                    st.session_state.selected_priority = None
                    st.rerun()

        briefing = st.session_state.briefing
        sorted_actions = sort_actions_by_priority(briefing.actions)

        # Priority Distribution
        priority_counts = {"urgent": 0, "high": 0, "medium": 0, "low": 0}
        for action in sorted_actions:
            priority_counts[action.priority] = (
                priority_counts.get(action.priority, 0) + 1
            )

        # Priority Metrics
        col1, col2, col3, col4 = st.columns(4)

        priorities = [
            ("urgent", "Urgent", priority_counts["urgent"]),
            ("high", "High", priority_counts["high"]),
            ("medium", "Medium", priority_counts["medium"]),
            ("low", "Low", priority_counts["low"]),
        ]

        for col, (priority_key, priority_label, count) in zip(
            [col1, col2, col3, col4], priorities
        ):
            with col:
                st.metric(priority_label, count)
                # Dynamic glow/active state for selected filter
                btn_type = (
                    "primary"
                    if st.session_state.selected_priority == priority_key
                    else "secondary"
                )
                if st.button(
                    f"Filter {priority_label}",
                    key=f"filter_{priority_key}",
                    use_container_width=True,
                    type=btn_type,
                ):
                    if st.session_state.selected_priority == priority_key:
                        st.session_state.selected_priority = None
                    else:
                        st.session_state.selected_priority = priority_key
                    st.rerun()

        # Actions Table
        if sorted_actions:
            # Filter actions
            if st.session_state.selected_priority:
                filtered_actions = [
                    a
                    for a in sorted_actions
                    if a.priority == st.session_state.selected_priority
                ]
                filter_text = (
                    f" - {st.session_state.selected_priority.upper()} Priority"
                )
            else:
                filtered_actions = sorted_actions
                filter_text = ""

            st.markdown(f"#### All Actions{filter_text}")

            if not filtered_actions:
                st.info(
                    f"No {st.session_state.selected_priority} priority actions found"
                )
            else:
                action_data = []
                for action in filtered_actions:
                    score = calculate_priority_score(action)
                    action_data.append(
                        {
                            "Task": action.task,
                            "Priority": action.priority.upper(),
                            "Score": f"{score}/6",
                            "Assignee": action.assignee,
                            "Deadline": action.deadline
                            if action.deadline
                            else "No deadline",
                        }
                    )

                import pandas as pd

                df = pd.DataFrame(action_data)

                # Apply priority colors
                def color_priority(val):
                    if val == "LOW":
                        return "color: #10B981; font-weight: bold;"
                    elif val == "MEDIUM":
                        return "color: #F59E0B; font-weight: bold;"
                    elif val in ["HIGH", "URGENT"]:
                        return "color: #EF4444; font-weight: bold;"
                    return ""

                # Use applymap for older pandas, map for newer. applymap is safer.
                styled_df = (
                    df.style.map(color_priority, subset=["Priority"])
                    if hasattr(df.style, "map")
                    else df.style.applymap(color_priority, subset=["Priority"])
                )
                st.table(styled_df)

            # Expandable Action Details
            st.markdown("#### Action Details")

            for idx, action in enumerate(sorted_actions):
                score = calculate_priority_score(action)
                priority_display = f"{action.priority.upper()}"

                with st.expander(
                    f"{action.task} - {priority_display} (Score: {score}/6)",
                    expanded=(idx < 3),
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("• Assignee")
                        st.write(action.assignee)

                    with col2:
                        st.markdown("• Deadline")
                        deadline_text = (
                            action.deadline if action.deadline else "No deadline"
                        )
                        st.write(deadline_text)

                    with col3:
                        st.markdown("• Priority Score")
                        st.write(f"{score}/6")

                    st.checkbox("Mark as complete", key=f"action_{idx}", disabled=True)

# ============================================
# Tab 3: Metrics
# ============================================
with tab3:
    # Key Metrics
    if st.session_state.briefing:
        st.markdown("### System Metrics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Actions", len(st.session_state.briefing.actions))

        with col2:
            st.metric("Stakeholders", len(st.session_state.briefing.stakeholders))

        with col3:
            urgent_count = sum(
                1
                for action in st.session_state.briefing.actions
                if action.priority == "urgent"
            )
            st.metric("Urgent Items", urgent_count)

        st.divider()

        st.markdown("### Workload Analytics")
        st.caption("Visualizing task distribution and team capacity")

        import pandas as pd

        # Prepare graph data
        priority_counts = {}
        assignee_counts = {}

        for action in st.session_state.briefing.actions:
            # Format priority for display
            p_key = action.priority.title()
            priority_counts[p_key] = priority_counts.get(p_key, 0) + 1

            # Format assignee
            assignee_counts[action.assignee] = (
                assignee_counts.get(action.assignee, 0) + 1
            )

        import altair as alt

        # Pick a beautiful accent color based on theme
        chart_color = "#3B82F6" if st.session_state.theme == "dark" else "#2563EB"

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("#### Priority Distribution")
            if priority_counts:
                df_priority = pd.DataFrame(
                    list(priority_counts.items()), columns=["Priority", "Count"]
                )
                # Using Altair without .interactive() perfectly disables scroll-zooming!
                chart1 = (
                    alt.Chart(df_priority)
                    .mark_bar(
                        color=chart_color, cornerRadiusTopLeft=4, cornerRadiusTopRight=4
                    )
                    .encode(
                        x=alt.X(
                            "Priority",
                            sort=None,
                            axis=alt.Axis(labelAngle=0, title=None),
                        ),
                        y=alt.Y("Count", axis=alt.Axis(title=None)),
                        tooltip=["Priority", "Count"],
                    )
                    .properties(height=300)
                )
                st.altair_chart(chart1, use_container_width=True)
            else:
                st.info("No priority data available.")

        with col_chart2:
            st.markdown("#### Task Load by Assignee")
            if assignee_counts:
                df_assignee = pd.DataFrame(
                    list(assignee_counts.items()), columns=["Assignee", "Tasks"]
                )
                chart2 = (
                    alt.Chart(df_assignee)
                    .mark_bar(
                        color=chart_color, cornerRadiusTopLeft=4, cornerRadiusTopRight=4
                    )
                    .encode(
                        x=alt.X(
                            "Assignee",
                            sort="-y",
                            axis=alt.Axis(labelAngle=-45, title=None),
                        ),
                        y=alt.Y("Tasks", axis=alt.Axis(title=None)),
                        tooltip=["Assignee", "Tasks"],
                    )
                    .properties(height=300)
                )
                st.altair_chart(chart2, use_container_width=True)
            else:
                st.info("No assignee data available.")

# ============================================
# Tab: AI Assistance
# ============================================
with tab_draft:
    # AI Assistance
    st.markdown("### AI Assistance")
    st.caption("Generate professional drafts using AI")

    draft_context = st.text_area(
        "Enter context for draft generation:",
        value=st.session_state.draft_context or "Reply to client proposal request",
        height=120,
        key="draft_input",
        placeholder="Describe what you need to draft...",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        generate_button = st.button(
            "Generate Draft", type="primary", use_container_width=True
        )

    # Generate Draft Logic
    if generate_button:
        if not draft_context.strip():
            st.warning("Please enter some context for the draft")
        else:
            max_retries = 2
            retry_count = 0
            success = False

            while retry_count < max_retries and not success:
                try:
                    with st.spinner("Generating professional draft..."):
                        if retry_count > 0:
                            st.info(f"Retry attempt {retry_count}/{max_retries - 1}...")
                            time.sleep(1)

                        # Use the shared LLM helper (NVIDIA NIM preferred, Gemini fallback)
                        from langchain_core.messages import HumanMessage

                        llm = get_llm(temperature=0.7)

                        # Create prompt
                        prompt = f"""Generate a professional, concise reply (under 50 words) for the following context:

{draft_context}

Keep it professional, clear, and actionable. Return only the draft text, no explanations."""

                        # Generate draft
                        message = HumanMessage(content=prompt)
                        response = llm.invoke([message])
                        draft_text = response.content.strip()

                    st.success("Draft generated successfully")

                    st.markdown("#### Generated Draft:")
                    st.code(draft_text, language=None)
                    st.info("Use the copy button above to copy the draft")
                    success = True

                except ValueError as e:
                    error_msg = str(e)

                    if "api_key" in error_msg.lower() or "gemini" in error_msg.lower():
                        st.error("API Key Error")
                        st.warning(
                            "Check that config/.env file exists and GEMINI_API_KEY is set correctly"
                        )
                        break
                    else:
                        retry_count += 1
                        if retry_count >= max_retries:
                            st.error(f"Error after {max_retries} attempts: {error_msg}")

                except Exception as e:
                    error_msg = str(e)

                    # Handle rate limits gracefully
                    if (
                        "429" in error_msg
                        or "RESOURCE_EXHAUSTED" in error_msg
                        or "Quota" in error_msg
                    ):
                        st.warning("⏳ Google Gemini API Rate Limit Exceeded.")
                        st.info(
                            "You are using a free-tier API key which has strict limits (e.g., requests per minute). Please wait about 60 seconds and try again."
                        )
                        break

                    retry_count += 1

                    if retry_count >= max_retries:
                        st.error(f"Error generating draft after {max_retries} attempts")
                        st.code(error_msg, language=None)

    st.divider()

    # Example Contexts
    st.markdown("#### Example Contexts")
    st.caption("Click any example to use it as your draft context")

    examples = [
        "Reply to client proposal request",
        "Follow-up email after meeting",
        "Status update for project stakeholders",
        "Request for deadline extension",
    ]

    cols = st.columns(2)
    for idx, example in enumerate(examples):
        with cols[idx % 2]:
            if st.button(example, key=f"example_{idx}", use_container_width=True):
                st.session_state.draft_context = example
                st.rerun()


# ============================================
# Tab 4: Connect
# ============================================
with tab4:
    render_section("Connect with Us", "")

    st.markdown("### Send Us Your Inquiry")

    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email Address")
        message = st.text_area("Project Details", height=150)

        submitted = st.form_submit_button("Submit", use_container_width=True)
        if submitted:
            if name and email and message:
                st.success("Inquiry submitted successfully")
            else:
                st.warning("Please fill in all fields")

# ============================================
# Footer
# ============================================
st.markdown(
    """
    <div style="text-align: center; padding: 3rem 0; color: var(--text-muted); border-top: 1px solid var(--border-light); margin-top: 4rem; font-size: 0.9rem;">
        <p>&copy; 2026 DailyPlus AI. All rights reserved.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Made with Bob
