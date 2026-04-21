"""
Templates de escenarios probabilísticos.

Cada escenario tiene:
- trigger_rules: condiciones sobre la evidencia que lo activan como candidato
- base_probability: probabilidad inicial antes de ajuste Claude
- indicators_template: lista de patrones típicos que lo sustentan
- implications_template: qué implica si ocurre
- watch_signals_template: qué monitorear a futuro
- legal_basis: artículo o norma relevante

Orden de ejecución:
1. Reglas deterministas sobre EvidenceBundle → lista de escenarios candidatos
2. Claude refina probabilidades finales + escribe narrativa específica

Alcance Perú 2026: plantillas específicas del contexto peruano
(LOE Art. 184, Art. 380 segunda vuelta, etc.). Arquitectura lista para
extender a otros países.
"""
from __future__ import annotations

from typing import Any, Dict, List


# Cada template es un dict con los campos del ForecastScenario + metadatos
# para las reglas de activación.
SCENARIO_TEMPLATES: List[Dict[str, Any]] = [
    {
        "scenario_id": "s_dispute_prolongada",
        "label": "Disputa post-electoral prolongada",
        "base_probability": 0.30,
        "legal_basis": "LOE N° 26859 Art. 343 y 363 (impugnaciones y actas observadas)",
        "indicators_template": [
            "Alta densidad de fraud_allegation en las últimas 72h",
            "Presencia de denuncias penales contra autoridades electorales",
            "Narrativa pública de nulidad promovida por partidos perdedores",
        ],
        "implications_template": (
            "Alto riesgo de impugnaciones masivas ante los Jurados Electorales "
            "Especiales. Posible retraso en la proclamación. Tensión "
            "institucional sostenida entre JNE, ONPE y el Ejecutivo durante "
            "semanas. Potencial activación de mecanismos interamericanos "
            "(Carta Democrática, CIDH)."
        ),
        "watch_signals_template": [
            "Número total de impugnaciones ante JEE dentro de las 72h post-jornada",
            "Resoluciones del JNE sobre pedidos de nulidad parcial o total",
            "Posicionamiento de observadores internacionales (OEA, EU EOM)",
            "Declaraciones de gremios empresariales sobre legitimidad del proceso",
        ],
        "triggers": {
            "fraud_allegation_count_ge": 10,
            "or_penal_complaints_against_emb_ge": 1,
        },
    },
    {
        "scenario_id": "s_nulidad_parcial",
        "label": "Nulidad parcial por el JNE (art. 184 Constitución / LOE)",
        "base_probability": 0.10,
        "legal_basis": "Constitución Perú Art. 184; doctrina JNE sobre nulidad parcial",
        "indicators_template": [
            "Votos nulos + blancos cercanos o superiores a 2/3 en mesas/regiones específicas",
            "Irregularidades graves y sistemáticas en un grupo identificable de mesas",
            "Denuncias penales corroboradas contra funcionarios de mesa o ONPE",
        ],
        "implications_template": (
            "El JNE declara nulidad parcial de mesas o circunscripciones "
            "determinadas. Debe convocarse a elecciones complementarias en esas "
            "mesas/regiones. Impacto en la composición del Congreso o en el "
            "resultado presidencial dependiendo del número de votos afectados."
        ),
        "watch_signals_template": [
            "Porcentaje de actas observadas por circunscripción",
            "Recursos de nulidad presentados por partidos con fundamento técnico",
            "Posicionamiento del Pleno del JNE",
        ],
        "triggers": {
            "ballot_tampering_count_ge": 1,
            "or_critical_logistics_regions_ge": 2,
        },
    },
    {
        "scenario_id": "s_segunda_vuelta",
        "label": "Segunda vuelta electoral con alta complejidad operativa",
        "base_probability": 0.55,
        "legal_basis": "LOE N° 26859 Art. 380 (segunda vuelta presidencial)",
        "indicators_template": [
            "Ningún candidato supera el 50%+1 de votos válidos en primera vuelta",
            "Crisis operativa de ONPE sin resolver previo a segunda vuelta",
            "Titular de ONPE bajo investigación penal durante el proceso",
        ],
        "implications_template": (
            "Segunda vuelta electoral dentro de los 30 días siguientes a la "
            "proclamación oficial. Desafío operativo adicional para una ONPE "
            "con credibilidad cuestionada. Probable reconfiguración de alianzas "
            "políticas entre vueltas."
        ),
        "watch_signals_template": [
            "Fecha de convocatoria oficial a segunda vuelta por el JNE",
            "Resolución sobre continuidad del jefe de ONPE",
            "Alianzas declaradas entre partidos perdedores y finalistas",
        ],
        "triggers": {
            "country": "PER",  # Específico Perú con LOE Art. 380
        },
    },
    {
        "scenario_id": "s_crisis_institucional",
        "label": "Crisis institucional post-escrutinio aguda",
        "base_probability": 0.25,
        "legal_basis": "CDI Art. 20 (alteración del orden constitucional); "
                        "Constitución Perú Art. 113",
        "indicators_template": [
            "Inestabilidad histórica (6 presidentes en 4 años, trayectoria V-Dem "
            "de deterioro)",
            "Tensión entre poderes del Estado durante el escrutinio",
            "Protestas sociales documentadas con víctimas",
        ],
        "implications_template": (
            "Escalada de tensión institucional con potencial de afectar la "
            "estabilidad del proceso de transferencia democrática de poder. "
            "Posible activación de la Carta Democrática Interamericana. "
            "Riesgo de represión de protestas con violaciones a DDHH."
        ),
        "watch_signals_template": [
            "Medidas cautelares de la CIDH",
            "Pronunciamientos de la Secretaría General de OEA",
            "Movilizaciones sociales con magnitud regional",
            "Uso de fuerzas armadas en contextos civiles",
        ],
        "triggers": {
            "country": "PER",
            "security_violence_count_ge": 2,
        },
    },
    {
        "scenario_id": "s_reforma_legislativa",
        "label": "Reforma legislativa post-proceso sobre IA electoral",
        "base_probability": 0.35,
        "legal_basis": "Iniciativa del JNE (Art. 178 Const.) + potestad del Congreso",
        "indicators_template": [
            "Ausencia de auditoría pública certificada del sistema STAE",
            "Debate público sobre el rol de la IA en el escrutinio",
            "Recomendaciones de la misión de observación sobre regulación de IA",
        ],
        "implications_template": (
            "Probable iniciativa legislativa para regular sistemas de IA en "
            "procesos electorales: auditoría obligatoria, publicación de código "
            "fuente, estándares de explicabilidad, derecho de impugnación sobre "
            "decisiones automatizadas. Precedente para la región."
        ),
        "watch_signals_template": [
            "Proyectos de ley ingresados al Congreso sobre IA electoral",
            "Auditorías encargadas por el JNE sobre STAE/SCE/SPR",
            "Dictámenes académicos sobre el sistema",
        ],
        "triggers": {
            "digital_count_ge": 1,
            "or_stae_incidents": True,
        },
    },
    {
        "scenario_id": "s_proclamacion_sin_disputa",
        "label": "Proclamación sin disputa mayor",
        "base_probability": 0.15,
        "legal_basis": "LOE N° 26859 Art. 178(5) (competencia del JNE para proclamar)",
        "indicators_template": [
            "Volumen de impugnaciones dentro de umbrales históricos",
            "Conteo rápido consistente con resultados oficiales",
            "Reconocimiento público del resultado por parte de los principales "
            "candidatos",
        ],
        "implications_template": (
            "Proclamación oficial dentro del plazo legal sin impugnaciones "
            "significativas. Transferencia ordenada de poder. Oportunidad para "
            "la agenda de reformas pendientes."
        ),
        "watch_signals_template": [
            "Ritmo del escrutinio en línea con cronograma ONPE",
            "Declaraciones de reconocimiento del resultado",
        ],
        "triggers": {
            "low_disruption": True,  # complemento de los escenarios anteriores
        },
    },
]
