"""
CitationBuilder — extrae citas in-line de los capítulos y arma bibliografía APA 7.

Después del ChapterComposer, cada capítulo tiene su narrativa en markdown con
citas en formato:
- `(Medio, Año, Fecha)` — periodístico
- `(Autor/Institución, Año)` — dataset / reporte
- `(Art. N de [Ley])` — normativa
- `(Res. JNE XXXX-YYYY-JNE)` — jurisprudencia
- `[frase](url)` — markdown link con URL

CitationBuilder:
1. Recorre las narrativas con regex y extrae patrones.
2. Matchea cada cita contra las fuentes conocidas (FindingRef, rag_docs, datasets).
3. Genera CitationEntry con APA 7 completa.
4. Asigna citation_id único.
5. Retorna bibliografía ordenada alfabéticamente.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from agents.elite_report.models import (
    CitationEntry,
    EliteChapter,
    FindingRef,
    HistoricalSeries,
)


# ── Plantillas APA 7 por tipo de fuente ──────────────────────────────────
MEDIA_FULL_NAMES = {
    "andina": "Andina (Agencia Peruana de Noticias)",
    "elcomercio": "El Comercio",
    "gestion": "Gestión",
    "idl": "IDL-Reporteros",
    "rpp": "RPP Noticias",
    "wayka": "Wayka",
    "jne": "Jurado Nacional de Elecciones",
    "onpe": "Oficina Nacional de Procesos Electorales",
    # Fuentes internacionales (Sprint Hunter-International)
    "bbc_la": "BBC News Latin America",
    "bbc_mundo": "BBC Mundo",
    "dw_es": "Deutsche Welle (en español)",
    "elpais_intl": "El País Internacional",
    "guardian_world": "The Guardian (World)",
    "nyt_americas": "The New York Times — Americas",
}

# Mapeo de instrumentos normativos a su cita APA 7 completa
NORMATIVE_APA = {
    "constitucion_peru_1993": (
        "Congreso Constituyente Democrático del Perú. (1993). "
        "*Constitución Política del Perú*. Publicada el 30 de diciembre de 1993. "
        "https://www.congreso.gob.pe/constitucion/"
    ),
    "loe_26859": (
        "Congreso de la República del Perú. (1997). "
        "*Ley N° 26859 — Ley Orgánica de Elecciones*. Diario Oficial El Peruano, "
        "30 de septiembre de 1997."
    ),
    "lop_28094": (
        "Congreso de la República del Perú. (2003). "
        "*Ley N° 28094 — Ley de Organizaciones Políticas*. Diario Oficial El Peruano, "
        "1 de noviembre de 2003."
    ),
    "ley_31030": (
        "Congreso de la República del Perú. (2020). "
        "*Ley N° 31030 — Ley que modifica normas de la Ley Orgánica de Elecciones "
        "respecto al ejercicio de los derechos políticos, paridad y alternancia*."
    ),
    "ley_31170": (
        "Congreso de la República del Perú. (2021). "
        "*Ley N° 31170 — Ley que incorpora el acoso político contra las mujeres "
        "en la vida política como tipo penal en el Código Penal*."
    ),
    "res_jne_0891_2025": (
        "Jurado Nacional de Elecciones. (2025, 15 de agosto). "
        "*Resolución N° 0891-2025-JNE: Rechazo de propuesta de Voto Electrónico "
        "No Presencial (VENP) para Elecciones Generales 2026* "
        "(Expediente N° JNE-2025-001)."
    ),
    "iccpr": (
        "Organización de las Naciones Unidas. (1966). "
        "*Pacto Internacional de Derechos Civiles y Políticos*. Resolución 2200A (XXI) "
        "de la Asamblea General, 16 de diciembre de 1966. Ratificado por el Perú en 1978."
    ),
    "cadh": (
        "Organización de Estados Americanos. (1969). "
        "*Convención Americana sobre Derechos Humanos — Pacto de San José*. "
        "Suscrita el 22 de noviembre de 1969, en vigor desde el 18 de julio de 1978. "
        "Ratificada por el Perú el 28 de julio de 1978."
    ),
    "cdi": (
        "Organización de Estados Americanos. (2001, 11 de septiembre). "
        "*Carta Democrática Interamericana*. Adoptada en la Primera Sesión Plenaria "
        "celebrada en Lima, Perú."
    ),
    "vdem": (
        "V-Dem Institute. (2025). *Varieties of Democracy (V-Dem) Dataset v15*. "
        "University of Gothenburg. https://v-dem.net/data/dataset-archive/"
    ),
    "freedom_house": (
        "Freedom House. (2025). *Freedom in the World 2025*. Freedom House. "
        "https://freedomhouse.org/report/freedom-world"
    ),
    "pei": (
        "Norris, P., & Grömping, M. (2024). *Perceptions of Electoral Integrity "
        "(PEI-10.0) Dataset*. Electoral Integrity Project, University of Sydney & "
        "Harvard Kennedy School. https://www.electoralintegrityproject.com"
    ),
    "rsf": (
        "Reporteros Sin Fronteras. (2025). *Índice Mundial de la Libertad de Prensa 2025*. "
        "Reporteros Sin Fronteras. https://rsf.org/es/clasificacion"
    ),
    "un_2005": (
        "Organización de las Naciones Unidas. (2005, 27 de octubre). "
        "*Declaración de Principios para la Observación Internacional de Elecciones "
        "y Código de Conducta para Observadores Internacionales*. Adoptada en conmemoración "
        "del 60° aniversario de la ONU."
    ),
}


class CitationBuilder:
    """Extrae citas y construye bibliografía APA 7."""

    def __init__(self):
        self._id_counter = 0
        self._by_key: Dict[str, CitationEntry] = {}

    def _next_id(self) -> str:
        self._id_counter += 1
        return f"C-{self._id_counter:03d}"

    def build_bibliography(
        self,
        chapters: List[EliteChapter],
        hunter_entries: List[FindingRef],
        historical_series: List[HistoricalSeries],
    ) -> List[CitationEntry]:
        """Procesa todos los capítulos, extrae citas y arma bibliografía.

        Retorna lista ordenada alfabéticamente (por APA formatted).
        """
        self._id_counter = 0
        self._by_key = {}

        # 1. Recolectar todas las citas desde las narrativas
        for ch in chapters:
            if not ch.narrative:
                continue
            self._extract_from_narrative(ch, hunter_entries)

        # 2. Agregar referencias a datasets que aparezcan en el contexto
        for s in historical_series:
            self._add_dataset_citation(s)

        # 3. Agregar instrumentos universales que siempre se citan en Elite Reports
        for key in ("iccpr", "cadh", "cdi", "un_2005"):
            self._ensure_citation(key, "treaty")

        # 4. Ordenar alfabéticamente
        entries = list(self._by_key.values())
        entries.sort(key=lambda e: e.apa_formatted.lower())

        # 5. Re-asignar citation_ids en orden alfabético
        for i, e in enumerate(entries):
            e.citation_id = f"C-{i+1:03d}"

        return entries

    # ── Extracción de narrativas ────────────────────────────────────────
    def _extract_from_narrative(self, ch: EliteChapter, hunter_entries: List[FindingRef]):
        text = ch.narrative

        # Patrón 1: [texto](url) — markdown links
        for match in re.finditer(r'\[([^\]]+)\]\((https?://[^)]+)\)', text):
            url = match.group(2)
            # Buscar si el URL matchea un finding conocido
            finding = next((f for f in hunter_entries if f.source_url == url), None)
            if finding:
                self._add_journalistic_citation(finding)
            else:
                # URL suelto sin finding: crear entrada web genérica
                label = match.group(1)[:80]
                self._add_web_citation(url, label)
            ch.citations_used.append(self._by_key.get(url, CitationEntry(
                citation_id="", type="web", apa_formatted="", short_form="")).citation_id or "")

        # Patrón 2: (Medio, Año, Fecha) o (Medio, Año)
        for match in re.finditer(
            r'\(([A-Z][a-záéíóúñ\- ]+?),\s*(\d{4})(?:,\s*([0-9]{1,2}\s+de\s+[a-záéíóú]+))?\)',
            text,
            flags=re.IGNORECASE,
        ):
            medio = match.group(1).strip()
            year = match.group(2)
            date = match.group(3)
            # Heurística: si medio matchea un MEDIA_FULL_NAMES, procesar
            slug = medio.lower().replace(" ", "")
            full_name = None
            for slug_key, name in MEDIA_FULL_NAMES.items():
                if slug_key in slug or slug in slug_key:
                    full_name = name
                    break
            if full_name:
                self._add_media_generic_citation(full_name, year, date)

        # Patrón 3: (Art. N de [Ley]) o (Art. N Const.)
        for match in re.finditer(
            r'\(Art\.\s*(\d+[a-záéíóú]?(?:\([a-z\d]+\))?)\s+(?:de\s+)?(la\s+)?([A-ZÁÉÍÓÚ][a-zA-ZÁÉÍÓÚáéíóúñ\d°\s]{3,80})\)',
            text,
        ):
            article = match.group(1)
            ley_raw = match.group(3).strip()
            self._add_legal_citation_by_name(ley_raw, article)

        # Patrón 4: (Res. JNE XXXX-YYYY-JNE)
        for match in re.finditer(r'\(Res\.\s*JNE\s*(\d{4}-\d{4}-JNE)\)', text):
            key = f"res_jne_{match.group(1).lower().replace('-', '_')}"
            if match.group(1).startswith("0891-2025"):
                self._ensure_citation("res_jne_0891_2025", "case_law")

        # Patrón 5: (ICCPR, Art. X), (CADH, Art. Y), (CDI, Art. Z)
        if re.search(r'\(ICCPR[,\s]', text) or "ICCPR Art." in text:
            self._ensure_citation("iccpr", "treaty")
        if re.search(r'\(CADH[,\s]', text) or "CADH Art." in text:
            self._ensure_citation("cadh", "treaty")
        if re.search(r'\(CDI[,\s]', text) or "CDI Art." in text:
            self._ensure_citation("cdi", "treaty")

        # Patrón 6: menciones a datasets conocidos sin paréntesis explícitos
        if re.search(r'V[- ]?Dem', text):
            self._ensure_citation("vdem", "dataset")
        if "Freedom House" in text:
            self._ensure_citation("freedom_house", "dataset")
        if re.search(r'PEI|Electoral Integrity Project', text):
            self._ensure_citation("pei", "dataset")
        if re.search(r'\bRSF\b|Reporteros Sin Fronteras|Reporters Without Borders', text):
            self._ensure_citation("rsf", "dataset")

    # ── Adición de citas específicas ────────────────────────────────────
    def _add_journalistic_citation(self, f: FindingRef):
        if not f.source_url or f.source_url in self._by_key:
            return
        medium_full = MEDIA_FULL_NAMES.get((f.source_name or "").lower(),
                                            (f.source_name or "medio").title())
        date_str = (f.recorded_at or "")[:10]
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            year = dt.year
            date_human = f"{dt.day} de {self._month_es(dt.month)}"
        except Exception:
            year = 2026
            date_human = date_str or "s.f."

        title = f.source_title or (f.finding or "")[:120]
        apa = (
            f"{medium_full}. ({year}, {date_human}). "
            f"{title}. *{medium_full}*. {f.source_url}"
        )
        short = f"({medium_full}, {year}, {date_human})"
        entry = CitationEntry(
            citation_id=self._next_id(),
            type="journalistic",
            apa_formatted=apa,
            short_form=short,
            url=f.source_url,
            accessed_date=datetime.utcnow().strftime("%Y-%m-%d"),
        )
        self._by_key[f.source_url] = entry

    def _add_web_citation(self, url: str, label: str):
        if url in self._by_key:
            return
        apa = f"{label}. (s.f.). Recuperado de {url}"
        entry = CitationEntry(
            citation_id=self._next_id(),
            type="web",
            apa_formatted=apa,
            short_form=f"(web, s.f.)",
            url=url,
            accessed_date=datetime.utcnow().strftime("%Y-%m-%d"),
        )
        self._by_key[url] = entry

    def _add_media_generic_citation(self, medium_full: str, year: str, date: Optional[str]):
        key = f"media_{medium_full.lower().replace(' ', '_')}_{year}_{date or 'none'}"
        if key in self._by_key:
            return
        if date:
            apa = f"{medium_full}. ({year}, {date}). *{medium_full}*."
            short = f"({medium_full}, {year}, {date})"
        else:
            apa = f"{medium_full}. ({year}). *{medium_full}*."
            short = f"({medium_full}, {year})"
        entry = CitationEntry(
            citation_id=self._next_id(),
            type="journalistic",
            apa_formatted=apa,
            short_form=short,
        )
        self._by_key[key] = entry

    def _add_legal_citation_by_name(self, ley_raw: str, article: str):
        low = ley_raw.lower()
        if "constituci" in low:
            self._ensure_citation("constitucion_peru_1993", "legal")
        elif "loe" in low or "26859" in low or "orgánica de elecciones" in low or "organica de elecciones" in low:
            self._ensure_citation("loe_26859", "legal")
        elif "28094" in low or "organizaciones pol" in low:
            self._ensure_citation("lop_28094", "legal")
        elif "31030" in low:
            self._ensure_citation("ley_31030", "legal")
        elif "31170" in low:
            self._ensure_citation("ley_31170", "legal")

    def _add_dataset_citation(self, s: HistoricalSeries):
        indicator = s.indicator.lower()
        if "vdem" in indicator:
            self._ensure_citation("vdem", "dataset")
        elif "fh" in indicator:
            self._ensure_citation("freedom_house", "dataset")
        elif "pei" in indicator:
            self._ensure_citation("pei", "dataset")
        elif "rsf" in indicator:
            self._ensure_citation("rsf", "dataset")

    def _ensure_citation(self, key: str, type_: str):
        """Agrega una cita desde NORMATIVE_APA si no está aún."""
        if key in self._by_key:
            return
        apa = NORMATIVE_APA.get(key)
        if not apa:
            return
        # Short form: extraer autor + año
        short = self._short_form_from_apa(apa)
        entry = CitationEntry(
            citation_id=self._next_id(),
            type=type_,  # type: ignore
            apa_formatted=apa,
            short_form=short,
        )
        self._by_key[key] = entry

    @staticmethod
    def _short_form_from_apa(apa: str) -> str:
        """Extrae '(Autor, Año)' de una cita APA completa."""
        m = re.match(r'^([^.(]+)\.\s*\((\d{4})', apa)
        if not m:
            return "(Fuente, s.f.)"
        author = m.group(1).strip()
        year = m.group(2)
        # Tomar primeras 2-3 palabras del autor si es muy largo
        if len(author) > 40:
            words = author.split()
            author = " ".join(words[:3])
        return f"({author}, {year})"

    @staticmethod
    def _month_es(m: int) -> str:
        months = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                   "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        return months[m - 1] if 1 <= m <= 12 else ""
