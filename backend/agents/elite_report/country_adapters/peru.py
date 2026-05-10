"""PeruAdapter — datos electorales especificos de Peru 2026.

Concentra TODA la informacion PER-especifica que antes estaba
distribuida en elite_report.py:_attach_visualizations + organizers/
phase_organizer.py + integraciones varias.

Calendario: cubre 1ra y 2da vuelta (LOE 26859 Art. 380, ~60 dias post
primera vuelta). Marco legal: Constitucion 1993 + LOE 26859 + LOP
28094 + Resoluciones JNE 2020-2025.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Tuple


# Diccionarios i18n para los strings locales del adapter.
# Las palabras descriptivas (actor types, recomendaciones, etc.) varian
# por idioma; los nombres propios y acronimos (JNE, ONPE, RENIEC, STAE)
# se mantienen.

_ACTOR_LABELS = {
    "es": {
        "inst": "institución", "fis": "fiscal", "jud": "judicial", "med": "media",
        "investiga": "investiga", "audita": "audita", "padron": "padrón",
        "supervisa": "supervisa", "reporta": "reporta",
        "fiscalia": "Fiscalía", "pj": "Poder Judicial", "prensa": "Prensa indep.",
    },
    "en": {
        "inst": "institution", "fis": "prosecutor", "jud": "judicial", "med": "media",
        "investiga": "investigates", "audita": "audits", "padron": "electoral roll",
        "supervisa": "supervises", "reporta": "reports",
        "fiscalia": "Prosecutor's Office", "pj": "Judiciary",
        "prensa": "Independent press",
    },
    "pt": {
        "inst": "instituição", "fis": "fiscal", "jud": "judicial", "med": "media",
        "investiga": "investiga", "audita": "audita", "padron": "cadastro",
        "supervisa": "supervisiona", "reporta": "reporta",
        "fiscalia": "Ministério Público", "pj": "Judiciário",
        "prensa": "Imprensa indep.",
    },
}

_DATA_LABELS = {
    "es": {
        "ew_levels": {"green": "Estable", "amber": "Vigilancia",
                      "orange": "Riesgo elevado", "red": "Crisis"},
        "horizon_short": "corto", "horizon_medium": "medio", "horizon_long": "largo",
        "rec_rows": [
            "Auditar STAE/SCE con tercero independiente",
            "Marco legal IA en procesos electorales",
            "Reforzar cadena de custodia de actas",
            "Capacitación obligatoria miembros de mesa",
            "Marco regulatorio publicidad digital",
            "Protocolo de respuesta a desinformación",
        ],
        "addressee_congress": "Congreso", "addressee_jne_cong": "JNE/Congreso",
        "addressee_onpe_jne": "ONPE/JNE",
        "stae_subtitle": "Mesa — laptops/imp.",
        "sce_subtitle": "Cómputo + IA dual",
        "spr_subtitle": "resultadoelectoral",
        "flow_label_actas": "actas + foto",
        "flow_label_aggr": "agregados",
        "role_arbiter": "árbitro", "role_org": "organización", "role_roll": "padrón",
        "edge_label_roll": "padrón", "edge_label_tally": "actas",
        "edge_label_oversight": "fiscaliza",
        "stage_roll": "Padrón", "stage_table": "Mesa",
        "stage_tally": "Acta", "stage_count": "Cómputo",
        "stage_proclaim": "Proclamación",
        "actor_table_members": "Miembros mesa",
    },
    "en": {
        "ew_levels": {"green": "Stable", "amber": "Watch",
                      "orange": "Elevated risk", "red": "Crisis"},
        "horizon_short": "short", "horizon_medium": "medium", "horizon_long": "long",
        "rec_rows": [
            "Audit STAE/SCE with an independent third party",
            "Legal framework for AI in electoral processes",
            "Strengthen chain of custody of tally sheets",
            "Mandatory training for polling station members",
            "Regulatory framework for digital advertising",
            "Disinformation response protocol",
        ],
        "addressee_congress": "Congress", "addressee_jne_cong": "JNE/Congress",
        "addressee_onpe_jne": "ONPE/JNE",
        "stae_subtitle": "Polling — laptops/printers",
        "sce_subtitle": "Tabulation + dual AI",
        "spr_subtitle": "results portal",
        "flow_label_actas": "tally sheets + photo",
        "flow_label_aggr": "aggregates",
        "role_arbiter": "arbiter", "role_org": "organization",
        "role_roll": "electoral roll",
        "edge_label_roll": "electoral roll", "edge_label_tally": "tally sheets",
        "edge_label_oversight": "oversight",
        "stage_roll": "Electoral roll", "stage_table": "Polling station",
        "stage_tally": "Tally sheet", "stage_count": "Tabulation",
        "stage_proclaim": "Proclamation",
        "actor_table_members": "Polling members",
    },
    "pt": {
        "ew_levels": {"green": "Estável", "amber": "Vigilância",
                      "orange": "Risco elevado", "red": "Crise"},
        "horizon_short": "curto", "horizon_medium": "médio", "horizon_long": "longo",
        "rec_rows": [
            "Auditar STAE/SCE com terceiro independente",
            "Marco legal de IA em processos eleitorais",
            "Reforçar cadeia de custódia das atas",
            "Capacitação obrigatória dos membros de mesa",
            "Marco regulatório de publicidade digital",
            "Protocolo de resposta a desinformação",
        ],
        "addressee_congress": "Congresso", "addressee_jne_cong": "JNE/Congresso",
        "addressee_onpe_jne": "ONPE/JNE",
        "stae_subtitle": "Mesa — laptops/imp.",
        "sce_subtitle": "Apuração + IA dual",
        "spr_subtitle": "portal de resultados",
        "flow_label_actas": "atas + foto",
        "flow_label_aggr": "agregados",
        "role_arbiter": "árbitro", "role_org": "organização", "role_roll": "cadastro",
        "edge_label_roll": "cadastro", "edge_label_tally": "atas",
        "edge_label_oversight": "fiscaliza",
        "stage_roll": "Cadastro", "stage_table": "Mesa",
        "stage_tally": "Ata", "stage_count": "Apuração",
        "stage_proclaim": "Proclamação",
        "actor_table_members": "Membros mesa",
    },
}


def _actors_for(lang: str) -> Dict[str, str]:
    return _ACTOR_LABELS.get(lang) or _ACTOR_LABELS["es"]


def _data_for(lang: str) -> Dict[str, Any]:
    return _DATA_LABELS.get(lang) or _DATA_LABELS["es"]


class PeruAdapter:
    """Adapter para Peru 2026."""

    country_code: str = "PER"
    country_name: str = "Perú"

    # ── Marco legal ────────────────────────────────────────────────────

    def legal_framework_rows(self) -> List[Dict[str, str]]:
        return [
            {"instrument": "Constitución Art. 176",
             "topic": "Finalidad del sistema electoral",
             "hierarchy": "constitucional"},
            {"instrument": "Constitución Art. 178",
             "topic": "Atribuciones del JNE",
             "hierarchy": "constitucional"},
            {"instrument": "Constitución Art. 183",
             "topic": "Funciones de ONPE",
             "hierarchy": "constitucional"},
            {"instrument": "LOE Art. 190", "topic": "Silencio electoral",
             "hierarchy": "legal"},
            {"instrument": "LOE Art. 343", "topic": "Actas observadas",
             "hierarchy": "legal"},
            {"instrument": "LOE Art. 380", "topic": "Segunda vuelta",
             "hierarchy": "legal"},
            {"instrument": "LOP Art. 34", "topic": "Transparencia financiera",
             "hierarchy": "legal"},
            {"instrument": "Ley 31030 (2020)", "topic": "Paridad y alternancia",
             "hierarchy": "legal"},
            {"instrument": "Ley 31170 (2021)", "topic": "Acoso político",
             "hierarchy": "legal"},
            {"instrument": "Res. JNE 0891-2025",
             "topic": "Rechazo del voto electrónico",
             "hierarchy": "jurisprudencial"},
            {"instrument": "ICCPR Art. 25", "topic": "Derechos políticos",
             "hierarchy": "internacional"},
            {"instrument": "CADH Art. 23",
             "topic": "Derechos políticos interamericanos",
             "hierarchy": "internacional"},
        ]

    # ── Estructura institucional ───────────────────────────────────────

    def actor_network(self, language: str) -> Dict[str, Any]:
        a = _actors_for(language)
        return {
            "actors": [
                {"id": "JNE", "label": "JNE", "type": a["inst"]},
                {"id": "ONPE", "label": "ONPE", "type": a["inst"]},
                {"id": "RENIEC", "label": "RENIEC", "type": a["inst"]},
                {"id": "FIS", "label": a["fiscalia"], "type": a["fis"]},
                {"id": "PJ", "label": a["pj"], "type": a["jud"]},
                {"id": "PRENSA", "label": a["prensa"], "type": a["med"]},
            ],
            "edges": [
                {"from": "FIS", "to": "ONPE", "action": a["investiga"], "severity": "high"},
                {"from": "JNE", "to": "ONPE", "action": a["audita"], "severity": "medium"},
                {"from": "RENIEC", "to": "ONPE", "action": a["padron"], "severity": "info"},
                {"from": "PJ", "to": "FIS", "action": a["supervisa"], "severity": "info"},
                {"from": "PRENSA", "to": "ONPE", "action": a["reporta"], "severity": "medium"},
            ],
        }

    def network_institutions(self, language: str) -> Dict[str, Any]:
        d = _data_for(language)
        return {
            "nodes": [
                {"id": "JNE", "label": "JNE", "role": d["role_arbiter"], "status": "amber"},
                {"id": "ONPE", "label": "ONPE", "role": d["role_org"], "status": "red"},
                {"id": "RENIEC", "label": "RENIEC", "role": d["role_roll"], "status": "ok"},
            ],
            "edges": [
                {"from": "RENIEC", "to": "ONPE", "label": d["edge_label_roll"]},
                {"from": "ONPE", "to": "JNE", "label": d["edge_label_tally"]},
                {"from": "JNE", "to": "ONPE", "label": d["edge_label_oversight"]},
            ],
        }

    def flow_voting_stages(self, language: str) -> Dict[str, Any]:
        d = _data_for(language)
        return {
            "stages": [
                {"name": d["stage_roll"], "actor": "RENIEC", "status": "ok"},
                {"name": d["stage_table"], "actor": "ONPE+ODPE", "status": "ok"},
                {"name": d["stage_tally"], "actor": d["actor_table_members"], "status": "warn"},
                {"name": "STAE/SCE", "actor": "ONPE", "status": "warn"},
                {"name": d["stage_count"], "actor": "JEE", "status": "ok"},
                {"name": d["stage_proclaim"], "actor": "JNE", "status": "pending"},
            ],
        }

    def architecture(self, language: str) -> Dict[str, Any]:
        d = _data_for(language)
        return {
            "components": [
                {"id": "STAE", "label": "STAE",
                 "subtitle": d["stae_subtitle"], "layer": "edge", "audited": False},
                {"id": "SCE", "label": "SCE",
                 "subtitle": d["sce_subtitle"], "layer": "core", "audited": False},
                {"id": "SPR", "label": "SPR",
                 "subtitle": d["spr_subtitle"], "layer": "publish", "audited": True},
            ],
            "flows": [
                {"from": "STAE", "to": "SCE", "label": d["flow_label_actas"]},
                {"from": "SCE", "to": "SPR", "label": d["flow_label_aggr"]},
            ],
        }

    # ── Producto del informe ───────────────────────────────────────────

    def recommendations(self, language: str) -> Dict[str, Any]:
        d = _data_for(language)
        rec = d["rec_rows"]
        hs, hm = d["horizon_short"], d["horizon_medium"]
        return {
            "rows": [
                {"recommendation": rec[0], "addressee": "ONPE",
                 "priority": "critical", "horizon": hs},
                {"recommendation": rec[1], "addressee": d["addressee_congress"],
                 "priority": "high", "horizon": hm},
                {"recommendation": rec[2], "addressee": d["addressee_onpe_jne"],
                 "priority": "high", "horizon": hs},
                {"recommendation": rec[3], "addressee": "ONPE",
                 "priority": "medium", "horizon": hs},
                {"recommendation": rec[4], "addressee": d["addressee_jne_cong"],
                 "priority": "medium", "horizon": hm},
                {"recommendation": rec[5], "addressee": "JNE",
                 "priority": "high", "horizon": hs},
            ]
        }

    def early_warning_label(self, level: str, language: str) -> str:
        d = _data_for(language)
        return d["ew_levels"].get(level, "")

    # ── Inteligencia institucional ─────────────────────────────────────

    def organ_keywords(self) -> Dict[str, List[str]]:
        return {
            "JNE":    ["jne", "jurado nacional", "jurado electoral"],
            "ONPE":   ["onpe", "oficina nacional"],
            "RENIEC": ["reniec", "registro nacional"],
        }

    # ── Calendario electoral ───────────────────────────────────────────

    def electoral_calendar(self) -> Dict[str, Tuple[date, date]]:
        return {
            "preparatory":         (date(2025, 10, 12), date(2026,  1, 11)),
            "pre_campaign":        (date(2026,  1, 12), date(2026,  2, 11)),
            "campaign":            (date(2026,  2, 12), date(2026,  4,  9)),
            "electoral_silence":   (date(2026,  4, 10), date(2026,  4, 11)),
            "election_day":        (date(2026,  4, 12), date(2026,  4, 12)),
            "counting_tabulation": (date(2026,  4, 13), date(2026,  4, 20)),
            "post_election":       (date(2026,  4, 21), date(2026,  5, 15)),
            "dispute_resolution":  (date(2026,  5, 16), date(2026,  6, 10)),
            "completed":           (date(2026,  6, 11), date(2027,  1,  1)),
        }

    # ── Datos opcionales ───────────────────────────────────────────────

    def parliament_scenarios(self) -> Optional[Dict[str, Any]]:
        try:
            from modules.peru_data import PERU_PARL_DATA
        except ImportError:
            return None
        if not PERU_PARL_DATA.get("scenarios"):
            return None
        return {
            "scenarios": PERU_PARL_DATA["scenarios"],
            "total_seats": PERU_PARL_DATA.get("total_seats", 130),
        }

    def regions_data(self) -> Optional[List[Dict[str, Any]]]:
        try:
            from modules.peru_data import PERU_REGIONS_DATA
        except ImportError:
            return None
        return PERU_REGIONS_DATA
