"""The only code that knows the CSV format. Everything downstream works on engine types.

Files are in data/raw (semicolon-separated, UTF-8 with BOM). See data/README.md.
"""
from __future__ import annotations

import logging
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import pandas as pd

from dispatch.config import ROOT
from dispatch.engine.types import Incident, Site, Team

log = logging.getLogger(__name__)


def _read(cfg, key: str) -> pd.DataFrame:
    path = ROOT / cfg.data.raw_dir / getattr(cfg.data, key)
    return pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype={"code_insee": str})


@lru_cache(maxsize=1)
def _postes_cached(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype={"code_insee": str}).set_index("id_poste")


def load_postes(cfg) -> pd.DataFrame:
    return _postes_cached(ROOT / cfg.data.raw_dir / cfg.data.postes)


def list_crises(cfg) -> list[str]:
    return sorted(_read(cfg, "incidents")["numero_crise"].unique())


def load_sites(cfg) -> list[Site]:
    df = _read(cfg, "sites")
    return [Site(r.id_site, r.commune, r.departement, r.latitude, r.longitude, int(r.nb_equipes))
            for r in df.itertuples()]


def load_teams(cfg, sites: list[Site] | None = None) -> list[Team]:
    """One Team per unit of nb_equipes, all starting at their site at t0 (MVP: everyone mobilised at 0)."""
    sites = sites or load_sites(cfg)
    teams = []
    for s in sites:
        for k in range(s.n_teams):
            teams.append(Team(id=f"{s.id}_E{k + 1}", home_site=s.id, lat=s.lat, lon=s.lon,
                              free_at=0.0, shift_start=0.0, shift_end=float(cfg.work_rules.shift_h)))
    return teams


def load_incidents(cfg, crisis_id: str) -> tuple[list[Incident], datetime]:
    """Incidents of one crisis, times in hours since the first incident (t0). Returns (incidents, t0)."""
    df = _read(cfg, "incidents")
    df = df[df["numero_crise"] == crisis_id].copy()
    df["ts"] = pd.to_datetime(df["dateHeureIncident"], format="%d/%m/%Y %H:%M")
    t0 = df["ts"].min()
    postes = load_postes(cfg)

    missing = ~df["id_poste"].isin(postes.index)
    if missing.any():
        log.warning("%s: dropping %d incident(s) with unknown poste: %s",
                    crisis_id, missing.sum(), df.loc[missing, "id_incident"].tolist())
        df = df[~missing]

    incidents = []
    for r in df.sort_values("ts").itertuples():
        p = postes.loc[r.id_poste]
        incidents.append(Incident(
            id=r.id_incident, poste_id=r.id_poste, lat=float(p.latitude), lon=float(p.longitude),
            customers=int(p.nb_clients), sensitive=bool(p.poste_avec_client_sensible),
            reported_at=(r.ts - t0).total_seconds() / 3600, est_duration=float(r.dureeDepannage.rstrip("h")),
            cause=r.causeInterruption, commune=str(p.commune), departement=str(p.departement)))
    return incidents, t0.to_pydatetime()
