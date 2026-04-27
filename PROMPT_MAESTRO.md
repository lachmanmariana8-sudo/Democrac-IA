# Prompt Maestro — v2 (Mejoras)

> Versión: v2
> Fecha: 2026-04-26
> Origen: aplicación del Prompt Maestro original a los cuatro informes electorales de Perú 2026.
>
> Este documento captura las **tres mejoras al Prompt Maestro original** identificadas a partir del uso del instrumento. Las mejoras son aditivas y deben integrarse sobre el cuerpo del Prompt Maestro base. Cuando se incorpore el texto del prompt original, fusionar siguiendo las instrucciones de ubicación de cada mejora.

---

## Mejora 1 — Instrucción de neutralidad activa (anti-sesgo de preferencia)

**Ubicación:** al inicio del prompt, inmediatamente antes del análisis.

**Texto a insertar:**

> Antes de iniciar el análisis, establece una rúbrica explícita de evaluación y aplícala de manera uniforme a todos los informes. No ajustes los criterios en función de la naturaleza, el mandato ni la calidad de cada documento. Si los informes pertenecen a tipologías distintas (misión presencial, plataforma de datos, misión de expertos), contextualiza esas diferencias pero no las uses para suavizar la aplicación de los criterios. Cuando un informe supere a otro en una dimensión, dilo sin ambigüedad. Cuando un informe sea débil en una dimensión, dilo sin eufemismos. La objetividad es más valiosa que la diplomacia analítica.

---

## Mejora 2 — Indicadores adicionales para contextos electorales con amenazas digitales

**Ubicación:** Sistema de Indicadores (Sección 5), cuando el objeto de análisis sean informes sobre procesos electorales en contextos con amenazas digitales.

**Indicadores a añadir:**

| Indicador adicional | Definición técnica |
|---|---|
| Cobertura del ecosistema digital de campaña | El informe audita el gasto en redes sociales, la distribución de contenidos y la actividad de bots o cuentas inauténticas. |
| Detección de desinformación estructurada | El informe identifica narrativas de desinformación, sus vectores de distribución y sus actores. |
| Análisis de nexos criminales | El informe investiga vínculos entre candidatos, partidos o financiadores con organizaciones criminales. |
| Capacidad anticipatoria | El informe produce hallazgos antes de la jornada electoral que permiten anticipar riesgos o diseñar contramedidas. |
| Integración en arquitectura de monitoreo agéntico | El informe puede ser procesado, actualizado e integrado en una plataforma de monitoreo basada en agentes de IA. |

---

## Mejora 3 — Instrucción sobre distinción de naturaleza de los documentos

**Ubicación:** al inicio de la sección de puntajes.

**Texto a insertar:**

> Al asignar puntajes, distingue explícitamente entre lo que el informe no hace porque está fuera de su mandato institucional y lo que no hace siendo una limitación real de calidad. La primera es una restricción contextual; la segunda es una debilidad técnica. No penalices por restricciones de mandato como si fueran debilidades analíticas, pero sí evalúa si el informe reconoce sus propias restricciones de forma transparente. Un informe que no reconoce sus limitaciones recibe un puntaje más bajo en el indicador "Identificación de riesgos y limitaciones", independientemente de su calidad en otras dimensiones.

---

## Pendiente

- Integrar estas tres mejoras sobre el texto del Prompt Maestro original (cuando se incorpore al repo).
- Validar la v2 reaplicándola a los cuatro informes electorales de Perú 2026 y comparar puntajes con la corrida v1 para confirmar que el sesgo de preferencia se reduce y la cobertura de amenazas digitales mejora.
