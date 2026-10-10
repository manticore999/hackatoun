"""Interface (French): replay a crisis with a dispatch strategy, see the result, the 48 h check and explanations.

Run:  streamlit run app/streamlit_app.py
The UI never computes decisions: it calls the engine (dispatch.engine) and the simulator (dispatch.sim).
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dispatch.config import load_config  # noqa: E402
from dispatch.data.loaders import list_crises, load_incidents, load_sites, load_teams  # noqa: E402
from dispatch.engine.baselines import BASELINES  # noqa: E402
from dispatch.engine.explain import explain  # noqa: E402
from dispatch.engine.planner import OptimisedPolicy, plan  # noqa: E402
from dispatch.engine.types import State  # noqa: E402
from dispatch.sim.simulator import Simulator  # noqa: E402
from dispatch.sim.whatif import teams_needed  # noqa: E402

st.set_page_config(page_title="Pilotage de crise - Enedis", layout="wide")
cfg = load_config()
sites = load_sites(cfg)
teams = load_teams(cfg, sites)

st.title("Pilotage des équipes en situation de crise")
st.caption("L'outil recommande, le responsable décide. Indicateur officiel : Σ clients × heures de coupure.")

POLICIES = {"Moteur optimisé (RSLS)": "optimised", "Règle de Smith seule": "smith", "Premier arrivé": "fifo",
            "Équipe la plus proche": "nearest", "Plus de clients d'abord": "max_customers"}
crisis = st.sidebar.selectbox("Crise à rejouer", list_crises(cfg), index=49)
policy_label = st.sidebar.selectbox("Stratégie", list(POLICIES))
budget = st.sidebar.slider("Budget de recherche par décision (ms)", 10, 300, 50, 10)
incidents, t0 = load_incidents(cfg, crisis)


def make_policy():
    name = POLICIES[policy_label]
    return OptimisedPolicy(budget) if name == "optimised" else BASELINES[name]()


col_map, col_side = st.columns([2, 1])
with col_map:
    pts = pd.DataFrame([{"lat": s.lat, "lon": s.lon, "color": "#1F3A5F", "size": 400} for s in sites]
                       + [{"lat": i.lat, "lon": i.lon, "color": "#E76F51", "size": 120} for i in incidents])
    st.map(pts, latitude="lat", longitude="lon", color="color", size="size")
    st.caption(f"{len(sites)} sites · {len(teams)} équipes · {len(incidents)} incidents · début {t0:%d/%m/%Y %H:%M}")

with col_side:
    st.subheader("Planning des équipes (fixé à l'initialisation)")
    n_b = sum(t.shift_start > 0 for t in teams)
    st.write(f"Rotation {cfg.roster.work_h:g} h de travail / {cfg.roster.rest_h:g} h de repos. "
             f"Groupe A : {len(teams) - n_b} équipes à H0 · Groupe B : {n_b} équipes à H0 + {cfg.roster.b_offset_h:g} h.")
    now = st.slider("Instant de décision (h après H0)", 0.0, 8.0, 2.0, 0.5)
    known = [i for i in incidents if i.reported_at <= now]
    if known:
        state = State(now=now, teams=teams, pending=known)
        p = plan(state, cfg, budget_ms=budget)
        st.subheader(f"Recommandations à H0 + {now:g} h ({len(known)} incidents connus)")
        for f in sorted(explain(p, state, cfg), key=lambda f: f.rank_in_plan)[:8]:
            alt = f.best_alternative_team
            st.markdown(f"**{f.team} → {f.incident}** · {f.factors['customers']} clients · "
                        f"{f.factors['travel_min']} min de route · {f.factors['repair_h']:g} h de dépannage · "
                        f"indice {f.factors['priority_index']}"
                        + (f" · alternative {alt['team']} : +{alt['delta']:,.0f} clients·h" if alt else ""))

st.divider()
if st.button("Rejouer toute la crise avec cette stratégie"):
    with st.spinner("Simulation en cours…"):
        res = Simulator(cfg, incidents, teams, make_policy()).run()
    k = res.kpis
    target = cfg.service_target
    share = k[f"share_by_deadline_{target.basis}"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clients × heures de coupure", f"{k['customer_hours']:,.0f}")
    c2.metric(f"Incidents résolus à H+{target.deadline_h}", f"{100 * share:.1f} %",
              "objectif atteint" if share >= target.share else "objectif manqué")
    c3.metric("Attente moyenne par client", f"{k['mean_wait_per_customer_h']:.1f} h")
    c4.metric("Fin de crise", f"H0 + {k['end_h']:.1f} h")
    if share < target.share:
        with st.spinner("Calcul des renforts nécessaires…"):
            r = teams_needed(cfg, incidents, teams, sites)
        st.warning(f"Objectif {100 * target.share:.0f} % à H+{target.deadline_h} hors d'atteinte : demander "
                   f"**{r['extra_teams']} équipes** en renfort à d'autres régions ({r['by_site']}).")
    df = pd.DataFrame([{"incident": i, "équipe": res.team_of[i], "début dépannage (h)": round(res.started_at[i], 2),
                        "rétabli à (h)": round(res.restored_at[i], 2)} for i in res.restored_at])
    st.dataframe(df.sort_values("rétabli à (h)"), use_container_width=True)
