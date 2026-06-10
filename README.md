Good. The full system is working end to end.



Now do one final integration test before we move to documentation and submission:



\*\*Test the four assessment scenarios through the UI:\*\*



In the sidebar, change the scenario dropdown to each of these and click "Run Assessment" each time:

1\. Poisson Process (Laser Counts)

2\. Lévy Process (Burst Events)

3\. Exponential Inter-arrivals

4\. Unknown Mixed Process ⚠️



Tell me if all four render correctly in the UI — specifically that the metric cards show the right PASS/FAIL and the reasoning trace is visible.



While you test that, here's what we're building next in parallel — the README which is a judging criterion:



Create `README.md`:



```markdown

\# StochastiQ 🎲

\*\*Enterprise Certification for Probabilistic Reasoning Competency\*\*



> AI that reasons through stochastic problems alongside your team — 

> not just at them.



\## What is StochastiQ?



StochastiQ is a multi-agent enterprise certification system that 

verifies data scientists and researchers actually understand the 

probabilistic models they use — not just the tools.



Built for the \*\*Microsoft Agents League Hackathon — Reasoning Agents 

Track\*\*, StochastiQ addresses a real gap: organizations certify teams 

on software tools but rarely on the statistical foundations underneath.



\## The Problem



A data scientist can be certified on Python, SQL, or Azure — but can 

they identify whether a stochastic process is memoryless? Can they 

detect a heavy-tailed distribution, explain why a Poisson model fails, 

and switch to a compound process? These are the skills that determine 

whether probabilistic models are used correctly in production.



StochastiQ certifies exactly this.



\## Multi-Agent Architecture



```

User (Learner / Manager)

&#x20;        ↓

&#x20; Orchestrator Agent

&#x20; (intent routing)

&#x20;   ↙  ↓  ↓  ↘  ↘

\[1]  \[2]  \[3]  \[4]  \[5]

&#x20;LC   SP   AA   EA   MI

```



| Agent | Role | Grounding |

|---|---|---|

| Learning Path Curator (LC) | Recommends next module by role | Knowledge Base (Foundry IQ pattern) |

| Study Plan Generator (SP) | Builds capacity-aware study schedule | Fabric IQ pattern (semantic role-module mapping) |

| Assessment Agent (AA) | Reasons through stochastic problems step by step | Statistical Engine + GPT-4o |

| Engagement Agent (EA) | Personalizes reminders to work context | Work IQ pattern (meeting/focus signals) |

| Manager Insights (MI) | Team readiness and risk summary | Synthetic learner dataset |



\## The Assessment Agent — Core Innovation



The Assessment Agent is what makes StochastiQ different from a 

quiz app. It follows a strict 5-step reasoning protocol:



```

STEP 1 — EXPLORE    → Descriptive statistics, tail behavior, VMR

STEP 2 — HYPOTHESIZE → 2 candidate models with theoretical justification

STEP 3 — TEST       → Goodness-of-fit tests (KS, chi-square)

STEP 4 — REFLECT    → Model rejection with explicit reasoning

STEP 5 — CONCLUDE   → Best-fit model, parameters, extreme event probability

```



Every step is grounded in Ross's \*Introduction to Probability Models\* 

and executed against real statistical tests — not simulated outputs.



\### Example: Ambiguous Mixed Process



When a learner submits burst data that follows no simple distribution:



\- Poisson FAILS (VMR=9.78, equidispersion violated)

\- Negative Binomial FAILS (extreme kurtosis=24.27 exceeds model capacity)

\- Agent correctly identifies compound Poisson-Gamma process

\- Cites Ross Chapter 6 on compound distributions

\- Recommends AIC/BIC model selection as next step



This is the kind of reasoning that cannot be faked with a lookup table.



\## Microsoft IQ Integration



| Layer | Implementation |

|---|---|

| \*\*Foundry IQ\*\* | Knowledge base pattern: Ross module excerpts + certification framework grounding all Curator and Assessment responses |

| \*\*Fabric IQ\*\* | Semantic layer pattern: role → module → prerequisite → threshold mapping drives Study Plan Generator |

| \*\*Work IQ\*\* | Work context pattern: meeting hours + focus hours + preferred slot drives Engagement Agent timing |



\## Tech Stack



| Component | Technology |

|---|---|

| Agent Orchestration | Microsoft Agent Framework (local) |

| LLM | GitHub-hosted GPT-4o via GitHub Models |

| Statistical Engine | Python (scipy, numpy, statsmodels) |

| UI | Streamlit |

| Version Control | GitHub |



> \*\*Deployment note\*\*: Architecture is designed for Foundry Agent 

> Service (Hosted Agents). Local deployment is the hackathon prototype; 

> cloud deployment via Azure Container Registry → Foundry Agent Service 

> is the production path.



\## Certification Modules



| Module | Topic | Ross Chapter | Threshold |

|---|---|---|---|

| 1 | Discrete Random Variables | Ch. 2 | 75% |

| 2 | Conditional Probability \& Bayes | Ch. 3 | 75% |

| 3 | Poisson Process | Ch. 5 | 80% |

| 4 | Markov Chains | Ch. 4 | 80% |

| 5 | Heavy-Tailed Distributions | Ch. 2, 6 | 85% |



\## Assessment Scenarios



| Scenario | Process | Key Test | Expected Outcome |

|---|---|---|---|

| Poisson | Laser photon counts | Chi-square | Confirms VMR≈1, λ estimated |

| Lévy | Burst intensity fluctuations | KS test | Heavy tail confirmed, extreme event risk quantified |

| Exponential | Inter-arrival times | KS test | Memoryless property supported |

| Ambiguous | Mixed burst process | Both | Both models fail → compound process reasoning |



\## Synthetic Data



All data in this project is synthetic and generated programmatically. 

No real employee data, customer data, or PII is used anywhere.



Learner IDs follow the pattern SQ-001 through SQ-004.

All scenarios are generated via `tools/statistical\_engine.py` 

using numpy random seeds for reproducibility.



\## Setup



```bash

git clone https://github.com/rafifernandaa/stochastiQ

cd stochastiQ

python -m venv .venv

.venv\\Scripts\\activate  # Windows

pip install -r requirements.txt

cp .env.example .env

\# Add your GITHUB\_TOKEN to .env

streamlit run app.py

```



\## Environment Variables



```bash

\# .env

GITHUB\_TOKEN=your\_github\_personal\_access\_token

AZURE\_AI\_MODEL\_DEPLOYMENT=gpt-4o

```



\## Project Structure



```

stochastiQ/

├── agents/

│   ├── orchestrator.py          # Intent routing

│   ├── assessment\_agent.py      # Core reasoning agent

│   └── supporting\_agents.py     # LC, SP, EA, MI agents

├── tools/

│   └── statistical\_engine.py    # scipy-based stats engine

├── knowledge\_base/              # Synthetic Ross excerpts

├── synthetic\_data/              # Synthetic learner data

├── app.py                       # Streamlit UI

├── requirements.txt

├── .env.example

└── README.md

```



\## Responsible AI



\- All outputs are clearly labeled as AI-generated

\- Statistical conclusions are grounded in actual test results,

&#x20; never hallucinated

\- Synthetic data only — no PII anywhere in the codebase

\- Agent reasoning is fully transparent and auditable

\- Model failures are reported honestly, not hidden



\## Alignment to Challenge Scenario



StochastiQ implements the full enterprise learning system scenario:



| Official Requirement | StochastiQ Implementation |

|---|---|

| Certification programme management | 5-module stochastic reasoning curriculum |

| Role-based study plans | 4 roles × module prerequisites |

| Grounded practice questions | Statistical scenarios grounded in Ross |

| Progress feedback | Engagement Agent with work context |

| Manager insights | Team readiness dashboard with risk flagging |

| Multi-agent orchestration | 5 agents + orchestrator routing layer |

| Microsoft IQ integration | Foundry IQ + Fabric IQ + Work IQ patterns |



\## License



MIT — see LICENSE file.

```



\---



Now create `requirements.txt`:



```text

openai>=1.0.0

azure-ai-projects

azure-ai-agents

scipy>=1.11.0

numpy>=1.24.0

statsmodels>=0.14.0

matplotlib>=3.7.0

streamlit>=1.28.0

python-dotenv>=1.0.0

```



And `.env.example`:



```bash

GITHUB\_TOKEN=your\_github\_personal\_access\_token\_here

AZURE\_AI\_MODEL\_DEPLOYMENT=gpt-4o

```



\---



\*\*Once UI tests pass, three things left:\*\*



1\. Push everything to GitHub

2\. Record demo video

3\. Submit via GitHub issue



Tell me which UI scenarios passed and we move to the submission checklist.

