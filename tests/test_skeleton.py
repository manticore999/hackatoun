"""Tests that must pass from day one (skeleton), plus engine acceptance tests to un-skip as work lands."""

from dispatch.config import load_config
from dispatch.data.loaders import list_crises, load_incidents, load_sites, load_teams
from dispatch.data.travel import haversine_km
from dispatch.engine.modifiers import CATALOGUE


cfg = load_config()


def test_config_loads():
    assert cfg.roster.work_h == 12 and cfg.roster.rest_h >= 11
    assert cfg.work_rules.teams_per_incident == 1
    assert cfg.objective.beta_sensitive == 0          # official N x T mode by default


def test_sites_and_teams():
    sites = load_sites(cfg)
    teams = load_teams(cfg, sites)
    assert len(sites) == 18
    assert len(teams) == 63
    r = cfg.roster
    assert sum(t.shift_start == r.b_offset_h for t in teams) == sum(vars(r.b_per_site).values())      # group B
    assert sum(t.shift_start == r.c_offset_h for t in teams) == sum(vars(r.c_per_site).values())      # relief C


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

