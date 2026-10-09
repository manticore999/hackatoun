# Pilotage de crise: real-time dispatch of field teams

**Défi Enedis · Hackathon La Mêlée · 9–10 October 2026**

During a climate crisis, many outages hit at once. This project is a **real-time decision-support system** that
recommends which field team should go to which incident, in what order, to restore power as fast as possible for
as many customers as possible (sensitive customers first), under work/rest rules. It explains every recommendation,
and lets the crisis manager accept, modify or reject it.

> **The engine decides and computes · the LLM translates and explains · the manager validates.**

![Architecture](docs/architecture.png)

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -e ".[all]"
pytest                                # skeleton tests must pass
streamlit run app/streamlit_app.py    # map of sites + one crisis
```

For the LLM copilot: copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY`.

## How it works

1. **Events** (new incident, team on site, repair done, team unavailable, shift end) arrive from interchangeable
   sources: CSV crisis replay (×1 / ×60), operator input, a storm generator.
2. The **optimisation engine** re-plans at every event. It builds a plan with a greedy pass (*list scheduling*,
   priority = weighted customers / (travel + repair)), improves it with local search / ALNS within a few hundred
   milliseconds, and computes counterfactuals (cost of each alternative).
3. The **LLM** explains the plan in French, using only numbers produced by the engine.
4. The **manager** accepts, or rejects with a reason. The LLM turns the reason into a structured rule from a fixed
   catalogue. A validator checks it. The engine re-solves and shows what the rule costs.
5. **Learning loops** (all proposals, never silent): duration calibration within the crisis, recurring rejections
   turned into rule proposals, and objective weights learned from the manager's choices.

One full cycle is drawn in [docs/decision_loop.png](docs/decision_loop.png).

**Objective:** minimise `Σ w_i · (C_i − r_i)` with `w_i = customers × (1 + β · sensitive)`, plus stability, travel
and fairness penalties. All weights and rules (12 h work / 11 h rest, one team per incident, …) are in
[`config/default.yaml`](config/default.yaml), never hard-coded.

## Repository layout

```
config/default.yaml         every rule and weight (β, λ, shifts, speeds, solver budget, LLM model)
data/raw/                   organisers' files (never edited), see data/README.md
docs/                       team brief (PDF), engine brief, architecture diagrams (.puml / .png / .svg)
src/dispatch/
  config.py                 load_config()
  data/                     loaders (only code that knows the CSV format), travel times
  engine/                   types (shared contract), modifiers catalogue, evaluate, baselines,
                            construct, local_search, planner, counterfactual, explain, reference_ortools
  sim/                      events, sources (CSV replay, manual, generator), simulator
  copilot/                  Claude client, explanations, reason -> modifiers, validator
  learning/                 calibration, decision memory, preference learning
app/streamlit_app.py        French UI (map, recommendations, active rules)
bench/run_benchmark.py      all policies x all crises, same simulator, same score
tests/                      skeleton tests + engine acceptance tests (skipped until implemented)
```

## Workstreams

| Workstream | Folder | Owner | Reference |
|---|---|---|---|
| Data & travel | `src/dispatch/data/` | | `data/README.md` |
| Optimisation engine | `src/dispatch/engine/` | | [`docs/RO_ENGINE_BRIEF.md`](docs/RO_ENGINE_BRIEF.md) |
| Simulator & event sources | `src/dispatch/sim/` | | brief §5 (contract) |
| LLM copilot & validator | `src/dispatch/copilot/` | | brief §7–§8 |
| Learning loops | `src/dispatch/learning/` | | team brief, section "Self-improvement" |
| Interface | `app/` | | team brief §8 (demo script) |
| Benchmark | `bench/` | | brief §9 (T9–T10) |

## Team conventions

- **Shared contract:** `src/dispatch/engine/types.py` and `engine/modifiers.py`. Change them together, in a dedicated PR.
- **Branches:** `feat/<workstream>-<topic>`, small PRs to `main`, and `pytest` green before merging.
- **No CSV access outside `data/loaders.py`.** No magic numbers outside `config/default.yaml`.
- **Only the engine produces decisions and numbers.** The UI and the LLM display and translate.
- **Python ≥ 3.11**, formatted with `ruff`.

## Documentation

- [Team brief (PDF)](docs/Enedis_Hackathon_Team_Brief.pdf): problem, data, objective, constraints, algorithm, roadmap
- [Optimisation engine brief](docs/RO_ENGINE_BRIEF.md): spec, contract, acceptance tests
- [Architecture](docs/architecture.png) · [Decision loop](docs/decision_loop.png): editable sources in `docs/*.puml`

## Assumptions and limits (to keep in the final README)

Synthetic customer counts and relocated incidents; repair durations known as estimates (the simulator can add noise);
no road blockages unless set by the operator; no network topology (one repair restores one substation); teams are
interchangeable (no skills data).
