from openai import OpenAI
from agents.assessment_agent import run_assessment
from agents.supporting_agents import (
    learning_path_curator,
    study_plan_generator,
    engagement_agent,
    manager_insights,
    SYNTHETIC_TEAM_DATA
)
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"]
)

ORCHESTRATOR_PROMPT = """
You are StochastiQ's Orchestrator — a routing agent that 
coordinates five specialist agents for enterprise stochastic 
reasoning certification.

Given a user message, respond with EXACTLY one of these 
routing decisions (just the keyword, nothing else):

ASSESS — user wants to run a stochastic assessment
CURATOR — user asks what to study or what's next
PLAN — user wants a study schedule or plan
ENGAGE — user wants progress update or reminders
MANAGER — user is a manager asking about team progress
UNKNOWN — cannot determine intent

Examples:
"assess me on Poisson" → ASSESS
"what should I study next" → CURATOR
"make me a study plan" → PLAN
"how am I doing" → ENGAGE
"show me team progress" → MANAGER
"hello" → UNKNOWN
"""

def route_intent(user_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ORCHESTRATOR_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def orchestrate(
    user_message: str,
    role: str = "Quantitative Researcher",
    learner_id: str = "SQ-001",
    current_module: str = "Module 3: Poisson Process",
    completed_modules: list = None,
    last_score: float = 74.0,
    preferred_slot: str = "Morning",
    meeting_hours: int = 18,
    focus_hours: int = 14,
    scenario: str = "poisson"
) -> dict:
    """
    Main orchestration function.
    Routes user message to correct agent.
    Returns dict with intent, agent_used, and response.
    """

    if completed_modules is None:
        completed_modules = ["Module 1", "Module 2"]

    intent = route_intent(user_message)

    if intent == "ASSESS":
        result = run_assessment(scenario)
        return {
            "intent": intent,
            "agent": "Assessment Agent",
            "response": result["reasoning_trace"],
            "metadata": {
                "scenario": result["scenario"],
                "threshold": result["threshold"],
                "extreme_prob": result["extreme_prob"],
                "primary_fit": result["primary_fit"].verdict,
                "secondary_fit": result["secondary_fit"].verdict
            }
        }

    elif intent == "CURATOR":
        response = learning_path_curator(role, completed_modules)
        return {
            "intent": intent,
            "agent": "Learning Path Curator",
            "response": response,
            "metadata": {}
        }

    elif intent == "PLAN":
        response = study_plan_generator(
            role, current_module, meeting_hours, focus_hours
        )
        return {
            "intent": intent,
            "agent": "Study Plan Generator",
            "response": response,
            "metadata": {}
        }

    elif intent == "ENGAGE":
        response = engagement_agent(
            learner_id, current_module,
            last_score, preferred_slot, meeting_hours
        )
        return {
            "intent": intent,
            "agent": "Engagement Agent",
            "response": response,
            "metadata": {}
        }

    elif intent == "MANAGER":
        response = manager_insights()
        return {
            "intent": intent,
            "agent": "Manager Insights Agent",
            "response": response,
            "metadata": {}
        }

    else:
        return {
            "intent": "UNKNOWN",
            "agent": "Orchestrator",
            "response": (
                "I can help you with: assessments, "
                "learning paths, study plans, progress "
                "updates, or team insights. What would "
                "you like?"
            ),
            "metadata": {}
        }