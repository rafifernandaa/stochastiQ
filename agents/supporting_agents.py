from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"]
)

# ── KNOWLEDGE BASE (inline synthetic docs) ──────────────────

KNOWLEDGE_BASE = """
# StochastiQ Certification Framework (Synthetic)

## Competency Modules
- Module 1: Discrete Random Variables (Ross Ch. 2)
  Prerequisites: None
  Threshold: Score >= 75%
  Topics: PMF, CDF, expectation, variance, Bernoulli, Binomial, Poisson

- Module 2: Conditional Probability and Bayes (Ross Ch. 3)
  Prerequisites: Module 1
  Threshold: Score >= 75%
  Topics: Conditioning, Bayes theorem, independence, total probability

- Module 3: Poisson Process (Ross Ch. 5)
  Prerequisites: Module 2
  Threshold: Score >= 80%
  Topics: Memoryless property, inter-arrival times, exponential distribution, MLE for lambda

- Module 4: Markov Chains (Ross Ch. 4)
  Prerequisites: Module 3
  Threshold: Score >= 80%
  Topics: Transition matrices, steady state, state classification

- Module 5: Heavy-Tailed Distributions (Ross Ch. 2, 6)
  Prerequisites: Module 3
  Threshold: Score >= 85%
  Topics: Lévy distribution, extreme events, tail index, compound processes

## Role-Based Learning Paths
- Quantitative Researcher: Module 1 → 2 → 3 → 5
- Data Scientist: Module 1 → 2 → 3 → 4
- Risk Analyst: Module 1 → 2 → 3 → 5
- Research Engineer: Module 1 → 2 → 3 → 4 → 5

## Certification Levels
- Foundation: Complete Modules 1-2
- Practitioner: Complete Modules 1-3
- Advanced: Complete Modules 1-4
- Expert: Complete all 5 modules
"""

SYNTHETIC_TEAM_DATA = [
    {
        "learner_id": "SQ-001",
        "role": "Quantitative Researcher",
        "modules_completed": ["Module 1", "Module 2"],
        "current_module": "Module 3",
        "scores": {"Module 1": 88, "Module 2": 74},
        "certification": "Foundation",
        "meeting_hours_per_week": 18,
        "focus_hours_per_week": 14,
        "preferred_slot": "Morning"
    },
    {
        "learner_id": "SQ-002",
        "role": "Data Scientist",
        "modules_completed": ["Module 1"],
        "current_module": "Module 2",
        "scores": {"Module 1": 61},
        "certification": "In Progress",
        "meeting_hours_per_week": 24,
        "focus_hours_per_week": 8,
        "preferred_slot": "Afternoon"
    },
    {
        "learner_id": "SQ-003",
        "role": "Risk Analyst",
        "modules_completed": ["Module 1", "Module 2", "Module 3"],
        "current_module": "Module 5",
        "scores": {"Module 1": 92, "Module 2": 85, "Module 3": 81},
        "certification": "Practitioner",
        "meeting_hours_per_week": 12,
        "focus_hours_per_week": 20,
        "preferred_slot": "Morning"
    },
    {
        "learner_id": "SQ-004",
        "role": "Research Engineer",
        "modules_completed": ["Module 1", "Module 2", "Module 3", "Module 4"],
        "current_module": "Module 5",
        "scores": {
            "Module 1": 95, "Module 2": 90,
            "Module 3": 88, "Module 4": 79
        },
        "certification": "Advanced",
        "meeting_hours_per_week": 10,
        "focus_hours_per_week": 22,
        "preferred_slot": "Evening"
    }
]

# ── AGENT 1: LEARNING PATH CURATOR ──────────────────────────

def learning_path_curator(role: str,
                           completed_modules: list[str]) -> str:
    prompt = f"""
You are StochastiQ's Learning Path Curator.
Ground all recommendations in this knowledge base:

{KNOWLEDGE_BASE}

Learner role: {role}
Completed modules: {', '.join(completed_modules) if completed_modules else 'None'}

Tasks:
1. Identify the recommended learning path for this role
2. State which module to study next and why
3. List 2-3 key concepts the learner must master in that module
4. Cite the Ross chapter for each concept
5. State the certification level they are working toward

Be specific. Do not recommend modules already completed.
Format as: Next Module → Key Concepts → Certification Target
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content


# ── AGENT 2: STUDY PLAN GENERATOR ───────────────────────────

def study_plan_generator(role: str,
                          current_module: str,
                          meeting_hours: int,
                          focus_hours: int) -> str:
    available_hours = max(0, focus_hours - 5)  # buffer
    prompt = f"""
You are StochastiQ's Study Plan Generator.
Use this knowledge base for module requirements:

{KNOWLEDGE_BASE}

Learner profile:
- Role: {role}
- Current module: {current_module}
- Meeting hours per week: {meeting_hours}
- Focus hours per week: {focus_hours}
- Available study hours per week (estimated): {available_hours}

Generate a practical 2-week study plan that:
1. Fits within available focus time (not meeting time)
2. Breaks the module into daily 30-60 minute sessions
3. Includes checkpoint days for self-assessment
4. Accounts for high meeting load (if > 20hrs/week, reduce daily targets)
5. States realistic completion date

Format as a day-by-day schedule. Be concise.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content


# ── AGENT 3: ENGAGEMENT AGENT ───────────────────────────────

def engagement_agent(learner_id: str,
                     current_module: str,
                     last_score: float,
                     preferred_slot: str,
                     meeting_hours: int) -> str:
    load = "high" if meeting_hours > 20 else \
           "moderate" if meeting_hours > 14 else "low"
    prompt = f"""
You are StochastiQ's Engagement Agent.
Your job is to keep learners progressing without disrupting their work.

Learner: {learner_id}
Current module: {current_module}
Last assessment score: {last_score}%
Preferred study slot: {preferred_slot}
Meeting load: {load} ({meeting_hours} hrs/week)

Generate:
1. One personalized progress message (encouraging but honest —
   if score < 75 say so directly)
2. Three study reminder suggestions timed to their preferred slot
   and avoiding peak meeting periods
3. One specific action for today based on their score and module

Keep tone professional and direct. No empty praise.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content


# ── AGENT 4: MANAGER INSIGHTS ───────────────────────────────

def manager_insights() -> str:
    team_json = json.dumps(SYNTHETIC_TEAM_DATA, indent=2)
    prompt = f"""
You are StochastiQ's Manager Insights Agent.
Analyze this synthetic team data and produce an executive summary:

{team_json}

Your report must include:
1. Team certification status overview (counts by level)
2. Top performer and most at-risk learner (by score trend)
3. Capacity analysis: which learners have high meeting load
   that may slow progress?
4. Two recommended manager actions this week
5. Predicted team readiness for next certification tier
   in 30 days (honest estimate)

Use only data provided. Do not invent metrics.
Flag SQ-002 explicitly if their score (61%) is below threshold.
Format as an executive briefing. Concise, no fluff.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content