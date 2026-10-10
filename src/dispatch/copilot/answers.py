"""Copilot chat answers for the front-end. Every figure comes from the engine (snapshot, what-if, reinforcement).
Known intents get a deterministic answer; other questions go to the LLM with a compact factual context, and the
answer is accepted only if every number it contains is in that context."""
from __future__ import annotations

import json
import re

from dispatch.copilot.client import chat, llm_available
from dispatch.copilot.explain import check_numbers_grounded  # noqa: F401  (kept for symmetry)

SYSTEM = (
    "Tu es le copilote d'un responsable de crise Enedis pendant une tempête. Fonctionnement du système : un moteur "
    "d'optimisation décide quelles équipes envoyer sur quelles pannes ; son objectif est de réduire le total « clients × "
    "heures sans électricité » en commençant par les pannes qui rallument le plus de clients par heure de travail, en "
    "respectant les horaires des équipes (12 h de travail, 12 h de repos). L'objectif de service (90 % des incidents "
    "réparés en 48 h) est vérifié à part ; s'il n'est pas tenu, le système chiffre les renforts nécessaires. Le "
    "responsable valide ou refuse chaque plan ; un refus motivé devient une règle et est enregistré pour le retour "
    "d'expérience. Réponds en français simple, en 4 phrases maximum, uniquement à partir des faits JSON fournis "
    "(situation à l'instant affiché, plan proposé inclus). N'invente aucun chiffre : recopie ceux des faits. Si la "
    "réponse n'est pas dans les faits, dis-le et propose une des questions : « Pourquoi ce plan ? », « Et si je perds "
    "50 % des équipes ? », « Quels clients sensibles attendent ? », « Où est la saturation ? », « Faut-il des renforts ? »."
)


def fmt(n: float) -> str:
    return f"{round(n):,}".replace(",", " ")


def _numbers(s: str) -> set[str]:
    return {x.replace(",", ".").replace(" ", "") for x in re.findall(r"\d[\d\s]*(?:[.,]\d+)?", s)}


def context(snap: dict) -> dict:
    k = snap["kpis"]
    waiting = [i for i in snap["incidents"] if i["status"] == "waiting"]
    by_commune: dict[str, int] = {}
    for i in waiting:
        by_commune[i["commune"]] = by_commune.get(i["commune"], 0) + i["clients"]
    top = sorted(by_commune.items(), key=lambda x: -x[1])[:5]
    return {"heure": snap["time"][11:16], "clients_coupes": k["clientsCut"], "clients_realimentes": k["clientsRestored"],
            "incidents_en_attente": k["incidentsWaiting"], "equipes_disponibles": k["teamsAvailable"],
            "equipes_occupees": k["teamsBusy"], "equipes_au_repos": k["teamsResting"],
            "estimation_90_pourcent_h": k["restore90Hours"], "objectif_h": 48,
            "communes_les_plus_touchees": [{"commune": c, "clients_en_attente": n} for c, n in top],
            "recommandations": [r.get("headline") for r in snap["recommendations"][:5]]}


def sensitive(snap: dict) -> str:
    lst = [i for i in snap["incidents"] if i["sensitive"] and i["status"] != "restored"]
    if not lst:
        return "Aucun poste avec client sensible n'est coupé en ce moment."
    status = {"waiting": "en attente", "enroute": "équipe en route", "repairing": "dépannage en cours"}
    lines = [f"• {i['commune']} ({i['posteId']}) · {fmt(i['clients'])} clients · {status.get(i['status'], i['status'])}"
             for i in lst[:6]]
    return f"{len(lst)} poste(s) avec client sensible encore coupé(s) :\n\n" + "\n".join(lines) + ("\n…" if len(lst) > 6 else "")


def saturation(snap: dict) -> str:
    c = context(snap)
    top = "\n".join(f"• {x['commune']} : {fmt(x['clients_en_attente'])} clients" for x in c["communes_les_plus_touchees"])
    return (f"{c['incidents_en_attente']} incidents attendent une équipe ; {c['equipes_disponibles']} équipe(s) disponible(s), "
            f"{c['equipes_au_repos']} au repos.\n\n" + (f"Plus gros volumes de clients en attente :\n{top}" if top else ""))


def reinforcement_text(r: dict) -> str:
    if r.get("target_met"):
        return (f"Pas besoin de renfort : selon le plan actuel, 90 % des clients coupés sont rétablis avant 48 h "
                f"({round(100 * r['projected_share'])} % à 48 h).")
    rf = r.get("reinforcement") or {}
    sites = ", ".join(f"{n} à {c}" for c, n in rf.get("by_site", {}).items())
    return (f"Objectif 90 % à 48 h hors d'atteinte : {round(100 * r['projected_share'])} % des clients coupés seraient "
            f"rétablis à 48 h. Demander {rf.get('extra_teams', '?')} équipe(s) en renfort ({sites}) permettrait d'atteindre "
            f"{round(100 * (rf.get('projected_share_after') or 0))} %.")


def free_answer(question: str, snap: dict, cfg) -> str | None:
    if not llm_available():
        return None
    ctx = context(snap)
    try:
        text = chat(SYSTEM, json.dumps({"question": question, "faits": ctx}, ensure_ascii=False), cfg, max_tokens=400)
    except Exception:
        return None
    allowed = _numbers(json.dumps(ctx, ensure_ascii=False)) | {"48", "50", "90"}
    allowed |= {str(int(float(n))) for n in allowed if n.replace(".", "", 1).isdigit()}
    return text if text and _numbers(text) <= allowed else None
