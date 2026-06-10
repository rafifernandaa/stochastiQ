from openai import OpenAI
from tools.statistical_engine import (
    explore,
    test_poisson,
    test_exponential,
    test_levy,
    test_negative_binomial,
    generate_scenario,
    extreme_event_probability,
)
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Retrieve API key safely
api_key = os.getenv("GITHUB_TOKEN")
if api_key is None:
    raise ValueError(
        "GITHUB_TOKEN not found in .env file."
    )

# Initialize GitHub Models client
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=api_key
)

SYSTEM_PROMPT = """
You are StochastiQ's Assessment Agent — an expert
in stochastic processes grounded in Ross's Introduction
to Probability Models.

You receive structured statistical results from a Python
engine and produce a transparent, step-by-step reasoning
trace.

You MUST follow exactly this structure in your response:

STEP 1 — EXPLORE
Interpret the descriptive statistics. Comment on VMR,
skewness, kurtosis, tail behavior. What does this suggest
about the underlying process? Reference Ross Chapter 2
where relevant.

STEP 2 — HYPOTHESIZE
Based on Step 1, propose exactly 2 candidate models.
Justify each with probability theory. Reference Ross
chapters.

STEP 3 — TEST
Report the goodness-of-fit results provided. State
clearly: PASS or FAIL for each model. Explain what the
p-value means in plain language.

STEP 4 — REFLECT
If primary model fails: explain exactly why, what the
failure reveals about the data, and why you switch to the
alternative. If it passes: confirm why the model is
appropriate and what assumptions are satisfied.

STEP 5 — CONCLUDE
State:
- best-fit model,
- key parameters,
- probability of extreme events,
- one Ross concept that explains the behavior,
- two actionable next steps for the learner.

RULES:
- Never invent statistical numbers.
- Only interpret what is given.
- Always cite Ross by chapter when invoking theory.
- Write for a data scientist learner — technical but clear.
- Keep each step to 3–5 sentences maximum.
"""


def run_assessment(scenario: str) -> dict:
    """
    Full assessment pipeline:
    1. Generate data
    2. Run statistical engine
    3. LLM reasons over results

    Parameters
    ----------
    scenario : str
        One of:
        - "poisson"
        - "exponential"
        - "levy"
        - "ambiguous"

    Returns
    -------
    dict
        Structured assessment output.
    """

    # Generate synthetic data
    data = generate_scenario(scenario)

    # Exploratory statistics
    exploration = explore(data)

    primary_fit = None
    secondary_fit = None

    # Fit candidate models
    if scenario == "exponential":

        primary_fit = test_exponential(data)

        secondary_fit = test_poisson(
            np.round(data).astype(int)
        )

    elif scenario == "levy":

        primary_fit = test_levy(data)

        secondary_fit = test_exponential(data)

    elif scenario == "ambiguous":

        counts = np.round(data).astype(int)

        primary_fit = test_poisson(counts)

        secondary_fit = test_negative_binomial(
            counts
        )

    else:  # Default: poisson

        primary_fit = test_poisson(
            np.round(data).astype(int)
        )

        secondary_fit = test_exponential(data)

    # Probability of extreme events
    threshold = float(
        np.percentile(data, 95)
    )

    extreme_prob = extreme_event_probability(
        data,
        threshold
    )

    # Check if both models fail
    all_failed = (
        not primary_fit.good_fit
        and not secondary_fit.good_fit
    )

    engine_results = f"""
STATISTICAL ENGINE RESULTS
==========================

SCENARIO:
{scenario.upper()}

SAMPLE SIZE:
{len(data)}

EXPLORATION:
{exploration.summary}

PRIMARY MODEL TEST:
{primary_fit.verdict}

SECONDARY MODEL TEST:
{secondary_fit.verdict}

MODEL SELECTION STATUS:
{
'⚠️ BOTH MODELS FAILED — data may represent a mixed or compound process. Explain transparently what this implies.'
if all_failed
else
'✅ At least one model passed — proceed to final interpretation.'
}

EXTREME EVENT ANALYSIS:
95th percentile threshold:
{threshold:.4f}

P(X > threshold):
{extreme_prob:.4f}
"""

    # LLM reasoning
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": engine_results
            }
        ],
        temperature=0.3
    )

    reasoning_trace = (
        response.choices[0]
        .message
        .content
    )

    return {
        "scenario": scenario,
        "exploration": exploration,
        "primary_fit": primary_fit,
        "secondary_fit": secondary_fit,
        "threshold": threshold,
        "extreme_prob": extreme_prob,
        "reasoning_trace": reasoning_trace,
        "raw_data": data
    }
