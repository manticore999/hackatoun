"""Interface (French): map, timeline, recommendations, accept / modify / reject, active rules.

Run:  streamlit run app/streamlit_app.py
Skeleton only: shows the sites and one crisis's incidents on the map. The UI never computes; it calls the engine.
"""
import pandas as pd
import streamlit as st

from dispatch.config import load_config
from dispatch.data.loaders import list_crises, load_incidents, load_sites

st.set_page_config(page_title="Pilotage de crise - Enedis", layout="wide")
cfg = load_config()

st.title("Pilotage des équipes en situation de crise")
st.caption("Squelette - l'outil recommande, le responsable décide.")

crisis = st.sidebar.selectbox("Crise à rejouer", list_crises(cfg))
incidents, t0 = load_incidents(cfg, crisis)
sites = load_sites(cfg)

col_map, col_reco = st.columns([2, 1])
with col_map:
    points = pd.DataFrame(
        [{"lat": s.lat, "lon": s.lon, "color": "#1F3A5F", "size": 400} for s in sites]
        + [{"lat": i.lat, "lon": i.lon, "color": "#E76F51", "size": 120} for i in incidents]
    )
    st.map(points, latitude="lat", longitude="lon", color="color", size="size")
    st.caption(f"{len(sites)} sites · {sum(s.n_teams for s in sites)} équipes · "
               f"{len(incidents)} incidents · début {t0:%d/%m/%Y %H:%M}")

with col_reco:
    st.subheader("Recommandations")
    st.info("À brancher sur le moteur (dispatch.engine.planner.plan) et le simulateur.")
    st.subheader("Règles actives")
    st.write("Aucune règle.")
