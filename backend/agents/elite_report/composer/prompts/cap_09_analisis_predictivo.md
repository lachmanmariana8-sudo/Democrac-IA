# Capítulo 9 — Análisis predictivo

**Objetivo:** proyectar escenarios probabilísticos para las próximas 2-6 semanas. Este es un capítulo distintivo del Elite Report.

**IMPORTANTE — Alcance del capítulo:**
- NO es pronóstico político (quién gana). Eso lo hacen encuestadoras.
- SÍ es estimación de dinámica institucional: disputas, nulidad, segunda vuelta, crisis, reforma legislativa.
- Las probabilidades NO son mutuamente excluyentes.

**Estructura esperada (## subsecciones):**

## 9.1 Metodología del análisis predictivo

- Pipeline híbrido: reglas deterministas sobre patrones del Hunter + análisis cualitativo con Claude
- Fuentes de evidencia usadas: señales agregadas, trayectoria histórica (datasets), marco normativo (umbrales legales)
- Limitaciones reconocidas: horizonte corto, no predice comportamiento político partidario

## 9.2 Patrón dominante identificado

- Describir el `dominant_pattern` provisto en el contexto del forecast
- Fundamentar con 2-3 señales concretas de la evidencia (cifras + fuentes)

## 9.3 Escenarios probabilísticos

Para cada uno de los 3-5 escenarios del `ForecastPayload`:

- **Nombre y probabilidad** (con intervalo de confianza si disponible)
- **Indicadores que lo sustentan** (citar hallazgos específicos)
- **Marco normativo aplicable** (artículo/resolución)
- **Implicaciones** si ocurre
- **Watch signals** — qué monitorear para confirmar/desconfirmar

Formato sugerido para cada escenario:

```
### Escenario A: {label}

**Probabilidad estimada:** {prob}% (IC 95%: {low}–{high}%)
**Base normativa:** {legal_basis}

**Indicadores:**
- {indicator_1}
- {indicator_2}
- {indicator_3}

**Implicaciones:** {implications}

**Señales a monitorear:**
- {watch_1}
- {watch_2}
```

## 9.4 Nivel de alerta temprana

- Nivel actual (green/amber/orange/red) con justificación
- Criterios que moverían el nivel en las próximas 2 semanas
- Recomendación de período de actualización del informe

**Requisitos:**

- Longitud: **800-1000 palabras**.
- Usar EXACTAMENTE los escenarios provistos en el contexto `forecast_formatted`. No inventar escenarios nuevos.
- Cada escenario debe tener probabilidad numérica exacta.
- NO hacer juicios de valor sobre qué escenario es "bueno" o "malo". Solo describir implicaciones objetivas.
- Subsección 9.4 debe cerrar con una **frase operativa**: si `early_warning=orange`, por ejemplo: "Se recomienda la actualización de este informe en un plazo no mayor a 7 días dada la dinámica en curso".

**Tono:** analítico-prospectivo. Cauteloso. Lenguaje de análisis de riesgo institucional.

Redactá ahora el **Capítulo 9 — Análisis predictivo** en markdown. Empezá con `## 9.1`.
