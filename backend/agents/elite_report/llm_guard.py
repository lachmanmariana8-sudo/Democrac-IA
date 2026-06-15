"""Validador anti-alucinación para los capítulos redactados por el LLM.

Pilar de auditabilidad del Marco de Calidad PEIRS: ningún número del texto debe
afirmarse sin respaldo. Extrae los tokens numéricos "estadísticos" (decimales,
porcentajes, años 19xx/20xx, cifras con separador de miles) de un capítulo y
marca los que NO aparecen en el contexto provisto al modelo. Conservador: no
toca enteros chicos (números de artículo como "178", incisos, etc.).

Es NO bloqueante: alimenta `warnings` para revisión. Atrapa el tipo de error
"V-Dem 1.31 en 2025" (año/valor inexistente en los datos).
"""
from __future__ import annotations

import re
from typing import Iterable, List, Optional

# Decimales (1.31 / 0,96), miles (1.303 / 9.036.046) y años 19xx-20xx.
_NUM_RE = re.compile(
    r"\b\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?\b"   # con separador de miles
    r"|\b\d+[.,]\d+\b"                          # decimal simple
    r"|\b(?:19|20)\d{2}\b"                      # año
)


def _norm(s: str) -> str:
    """Quita separadores de miles/decimales para comparar por dígitos."""
    return re.sub(r"[.,\s]", "", s or "")


def find_unsupported_numbers(
    text: str, context: str, *, whitelist: Optional[Iterable[str]] = None
) -> List[str]:
    """Tokens numéricos 'estadísticos' de `text` ausentes de `context`.

    Compara el token tal cual y su forma normalizada (solo dígitos), para
    tolerar diferencias de separador (1.303 vs 1,303 vs 1303)."""
    if not text:
        return []
    ctx = context or ""
    ctx_norm = _norm(ctx)
    wl = set(whitelist or ())
    flagged: List[str] = []
    for m in _NUM_RE.finditer(text):
        tok = m.group(0)
        if tok in wl or tok in ctx:
            continue
        if _norm(tok) and _norm(tok) in ctx_norm:
            continue
        flagged.append(tok)
    # Únicos, preservando orden.
    seen = set()
    out = []
    for t in flagged:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def guard_chapter(chapter_id: str, narrative: str, context: str,
                  *, whitelist: Optional[Iterable[str]] = None) -> List[str]:
    """Devuelve warnings (strings) por cifras sin respaldo en `context`."""
    unsupported = find_unsupported_numbers(narrative, context, whitelist=whitelist)
    if not unsupported:
        return []
    sample = ", ".join(unsupported[:8])
    return [f"[llm_guard] Cap '{chapter_id}': {len(unsupported)} cifra(s) sin "
            f"respaldo en el corpus/contexto: {sample}"]
