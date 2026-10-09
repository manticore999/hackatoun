"""Tests that must pass from day one (skeleton), plus engine acceptance tests to un-skip as work lands."""
import pytest

from dispatch.config import load_config
from dispatch.data.loaders import list_crises, load_incidents, load_sites, load_teams
from dispatch.data.travel import haversine_km
from dispatch.engine.modifiers import CATALOGUE
from dispatch.engine.types import Incident, Team

cfg = load_config()


def test_config_loads():
    assert cfg.work_rules.shift_h == 12 and cfg.work_rules.rest_h == 11
    assert cfg.work_rules.teams_per_incident == 1


def test_sites_and_teams():
    sites = load_sites(cfg)
    teams = load_teams(cfg, sites)
    assert len(sites) == 18
    assert len(teams) == 63


def test_crises_load():
    crises = list_crises(cfg)
    assert len(crises) == 100
    incidents, _ = load_incidents(cfg, "CRISE_051")
    assert len(incidents) == 248          # 249 in the CSV, INC_007934 has no matching poste
    assert incidents[0].reported_at == 0.0
    assert {i.est_duration for i in incidents} <= {2.0, 4.0, 8.0}


def test_travel_distance():
    assert haversine_km(43.6, 1.44, 43.6, 1.44) == 0
    toulouse_foix = haversine_km(43.6045, 1.4440, 42.9654, 1.6060)
    assert 65 < toulouse_foix < 80


def test_modifier_catalogue():
    assert {"force", "forbid", "zone_inaccessible", "duration_update", "weight"} <= set(CATALOGUE)


# ---------------- engine acceptance tests (docs/RO_ENGINE_BRIEF.md §9) ----------------
def _toy():
    """One team, three incidents at t0, all at the team's position (no travel). Brief §3."""
    team = Team(id="T1", home_site="S1", lat=43.6, lon=1.44, free_at=0.0, shift_end=24.0)
    mk = lambda i, n, p: Incident(id=i, poste_id=i, lat=43.6, lon=1.44, customers=n,  # noqa: E731
                                  sensitive=False, reported_at=0.0, est_duration=p)
    return team, mk("A", 150, 8.0), mk("B", 60, 2.0), mk("C", 100, 4.0)


@pytest.mark.skip(reason="T1: enable once evaluate_route is implemented")
def test_T1_evaluate_route_toy():
    from dispatch.engine.evaluate import evaluate_route
    team, a, b, c = _toy()
    assert evaluate_route(team, [a, c, b], cfg).cost == pytest.approx(3240)
    assert evaluate_route(team, [b, c, a], cfg).cost == pytest.approx(2820)
