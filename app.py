import streamlit as st
from agents.orchestrator import orchestrate

# ── PAGE CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="StochastiQ",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f0f0f; }
    .stApp { background-color: #0f0f0f; color: #f0f0f0; }
    
    .agent-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .badge-assess { background: #1a1a2e; color: #7c3aed; 
                    border: 1px solid #7c3aed; }
    .badge-curator { background: #1a2e1a; color: #16a34a; 
                     border: 1px solid #16a34a; }
    .badge-plan { background: #1a2a2e; color: #0891b2; 
                  border: 1px solid #0891b2; }
    .badge-engage { background: #2e1a1a; color: #dc2626; 
                    border: 1px solid #dc2626; }
    .badge-manager { background: #2e2a1a; color: #d97706; 
                     border: 1px solid #d97706; }

    .metric-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }

    .reasoning-trace {
        background: #111;
        border-left: 3px solid #7c3aed;
        padding: 16px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR: LEARNER PROFILE ─────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/dice.png", 
             width=60)
    st.title("StochastiQ")
    st.caption("Enterprise Stochastic Reasoning Certification")
    st.divider()

    st.subheader("Learner Profile")
    role = st.selectbox("Role", [
        "Quantitative Researcher",
        "Data Scientist",
        "Risk Analyst",
        "Research Engineer"
    ])

    learner_id = st.selectbox("Learner ID", [
        "SQ-001", "SQ-002", "SQ-003", "SQ-004"
    ])

    current_module = st.selectbox("Current Module", [
        "Module 1: Discrete Random Variables",
        "Module 2: Conditional Probability and Bayes",
        "Module 3: Poisson Process",
        "Module 4: Markov Chains",
        "Module 5: Heavy-Tailed Distributions"
    ])

    completed = st.multiselect("Completed Modules", [
        "Module 1", "Module 2",
        "Module 3", "Module 4", "Module 5"
    ], default=["Module 1", "Module 2"])

    st.divider()
    st.subheader("Work Context")
    meeting_hours = st.slider(
        "Meeting Hours/Week", 5, 35, 18
    )
    focus_hours = st.slider(
        "Focus Hours/Week", 5, 30, 14
    )
    last_score = st.slider(
        "Last Assessment Score (%)", 0, 100, 74
    )
    preferred_slot = st.selectbox(
        "Preferred Study Slot",
        ["Morning", "Afternoon", "Evening"]
    )

    st.divider()
    st.subheader("Assessment Scenario")
    scenario = st.selectbox("Data Scenario", [
        "poisson",
        "levy",
        "exponential",
        "ambiguous"
    ], format_func=lambda x: {
        "poisson": "Poisson Process (Laser Counts)",
        "levy": "Lévy Process (Burst Events)",
        "exponential": "Exponential Inter-arrivals",
        "ambiguous": "Unknown Mixed Process ⚠️"
    }[x])

    scenario_descriptions = {
        "poisson": "Clean count data. VMR≈1. Agent should confirm Poisson.",
        "levy": "Extreme bursts. VMR>2000. Agent detects heavy tail.",
        "exponential": "Continuous inter-arrivals. Memoryless property test.",
        "ambiguous": "Mixed process. Both models fail. Agent reasons about compound distributions."
    }
    st.caption(scenario_descriptions[scenario])

# ── MAIN AREA ────────────────────────────────────────────────
st.title("StochastiQ")
st.markdown(
    "**Enterprise Certification for Probabilistic "
    "Reasoning Competency** — AI that reasons through "
    "stochastic problems alongside your team."
)
st.divider()

# Quick action buttons
st.subheader("Quick Actions")
col1, col2, col3, col4, col5 = st.columns(5)

quick_message = None
with col1:
    if st.button("🎲 Run Assessment", use_container_width=True):
        quick_message = f"assess me on {scenario}"
with col2:
    if st.button("📚 Learning Path", use_container_width=True):
        quick_message = "what should I study next"
with col3:
    if st.button("📅 Study Plan", use_container_width=True):
        quick_message = "make me a study plan"
with col4:
    if st.button("📊 My Progress", use_container_width=True):
        quick_message = "how am I doing"
with col5:
    if st.button("👔 Team View", use_container_width=True):
        quick_message = "show me team progress"

st.divider()

# Chat input
user_input = st.chat_input(
    "Ask StochastiQ anything... "
    "(e.g. 'assess me', 'what should I study', "
    "'show team progress')"
)

# Use quick action or typed input
message = quick_message or user_input

# ── RESPONSE AREA ────────────────────────────────────────────
if message:
    with st.spinner("Agents reasoning..."):
        result = orchestrate(
            user_message=message,
            role=role,
            learner_id=learner_id,
            current_module=current_module,
            completed_modules=completed,
            last_score=float(last_score),
            preferred_slot=preferred_slot,
            meeting_hours=meeting_hours,
            focus_hours=focus_hours,
            scenario=scenario
        )

    # Agent badge
    badge_map = {
        "Assessment Agent": "badge-assess",
        "Learning Path Curator": "badge-curator",
        "Study Plan Generator": "badge-plan",
        "Engagement Agent": "badge-engage",
        "Manager Insights Agent": "badge-manager",
        "Orchestrator": "badge-assess"
    }
    badge_class = badge_map.get(result["agent"], "badge-assess")
    st.markdown(
        f'<div class="agent-badge {badge_class}">'
        f'🤖 {result["agent"]}</div>',
        unsafe_allow_html=True
    )

    # Metadata cards for Assessment
    if result["intent"] == "ASSESS" and result["metadata"]:
        m = result["metadata"]
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Scenario",
                      m["scenario"].upper())
        with c2:
            st.metric("Primary Model",
                      "✅ PASS" if "PASSES" in m["primary_fit"]
                      else "❌ FAIL")
        with c3:
            st.metric("Secondary Model",
                      "✅ PASS" if "PASSES" in m["secondary_fit"]
                      else "❌ FAIL")
        with c4:
            st.metric("Extreme Event P",
                      f"{m['extreme_prob']:.1%}")

    # Main response
    st.markdown("### Reasoning Trace" 
                if result["intent"] == "ASSESS" 
                else "### Response")
    st.markdown(result["response"])

    # Raw fit verdicts for Assessment
    if result["intent"] == "ASSESS" and result["metadata"]:
        with st.expander("📊 Raw Statistical Engine Output"):
            st.code(result["metadata"]["primary_fit"])
            st.code(result["metadata"]["secondary_fit"])
            st.code(
                f"Threshold: {result['metadata']['threshold']:.4f}\n"
                f"P(X > threshold): "
                f"{result['metadata']['extreme_prob']:.4f}"
            )