"""DEMOCRAC.IA — Peru Electoral Sources
Fetchers RSS para fuentes públicas peruanas.
Usa httpx (ya en requirements) + xml stdlib. Sin dependencias extra.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

import httpx

# ── RSS feeds por fuente ──────────────────────────────────────────────────────
# Todas las URLs son públicas, sin autenticación.
# El Hunter elige las fuentes relevantes según la fase activa.

RSS_FEEDS: Dict[str, List[str]] = {
    # Agencia Andina — agencia oficial del Estado peruano. Política y elecciones.
    "andina": [
        "https://andina.pe/rss/politica.xml",
    ],
    # RPP Noticias — radio/digital de mayor audiencia política en Perú.
    "rpp": [
        "https://rpp.pe/feed/",
    ],
    # El Comercio — diario de referencia, sección política. RSS 2.0 verificado.
    "elcomercio": [
        "https://elcomercio.pe/arcio/rss/category/politica/",
    ],
    # Gestión — prensa económica/política. RSS 2.0 verificado.
    "gestion": [
        "https://gestion.pe/arcio/rss/category/peru/",
    ],
    # IDL-Reporteros — periodismo de investigación (corrupción, crimen organizado).
    "idl": [
        "https://www.idl-reporteros.pe/feed/",
    ],
    # Wayka — medio digital independiente, cobertura de movimientos sociales.
    "wayka": [
        "https://wayka.pe/feed/",
    ],
    # JNE — feed pendiente de verificación (403/404 en pruebas directas).
    "jne": [
        "https://www.jne.gob.pe/feed/",
    ],
    # ONPE — devuelve 403, puede requerir sesión o user-agent específico.
    "onpe": [
        "https://www.onpe.gob.pe/feed/",
    ],

    # ── Fuentes internacionales (Sprint Hunter-International, 7-may-2026) ──
    # Estas cubren Peru solo cuando hay noticia con relevancia internacional.
    # Se filtran por keyword "Peru/Perú" en _filter_intl_relevant antes de
    # entrar al pipeline. Cobertura proxy de la observacion externa.

    # BBC News Latin America — feed regional EN, alta credibilidad institucional.
    "bbc_la": [
        "http://feeds.bbci.co.uk/news/world/latin_america/rss.xml",
    ],
    # BBC Mundo — feed general ES. Cubre eventos electorales latam con foco en
    # contexto internacional. Filtra a Peru por keyword.
    "bbc_mundo": [
        "https://feeds.bbci.co.uk/mundo/rss.xml",
    ],
    # Deutsche Welle en español — cobertura LatAm con perspectiva europea.
    "dw_es": [
        "https://rss.dw.com/xml/rss-sp-all",
    ],
    # El País Internacional — diario referencia ES con cobertura LatAm extensa.
    "elpais_intl": [
        "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/internacional/portada",
    ],
    # The Guardian World — cobertura global, alta credibilidad para EOM context.
    "guardian_world": [
        "https://www.theguardian.com/world/rss",
    ],
    # NYT Americas — cobertura US/LatAm con perspectiva editorial-analitica.
    "nyt_americas": [
        "https://rss.nytimes.com/services/xml/rss/nyt/Americas.xml",
    ],
}

# Fuentes que requieren filtro por keyword "Peru/Perú" antes de ingestar.
# Las peruanas estan en Peru por default, no necesitan filtro.
INTL_SOURCES = {"bbc_la", "bbc_mundo", "dw_es", "elpais_intl", "guardian_world", "nyt_americas"}

# ── Fuentes activas por fase electoral ───────────────────────────────────────
PHASE_SOURCES: Dict[str, List[str]] = {
    "preparatory":         ["andina", "elcomercio", "gestion", "idl", "jne"],
    "pre_campaign":        ["andina", "elcomercio", "gestion", "idl", "wayka", "jne", "onpe", "rpp",
                            "bbc_mundo", "dw_es"],
    "campaign":            ["andina", "elcomercio", "gestion", "idl", "wayka", "rpp", "jne", "onpe",
                            "bbc_mundo", "dw_es", "elpais_intl"],
    "electoral_silence":   ["andina", "elcomercio", "rpp",
                            "bbc_mundo", "elpais_intl"],
    "election_day":        ["andina", "elcomercio", "rpp", "onpe",
                            "bbc_la", "bbc_mundo", "dw_es", "elpais_intl",
                            "guardian_world", "nyt_americas"],
    "counting_tabulation": ["andina", "elcomercio", "gestion", "rpp", "onpe", "jne",
                            "bbc_mundo", "elpais_intl", "nyt_americas"],
    "post_election":       ["andina", "elcomercio", "gestion", "idl", "rpp", "jne", "onpe",
                            "bbc_la", "bbc_mundo", "dw_es", "elpais_intl",
                            "guardian_world", "nyt_americas"],
    "dispute_resolution":  ["andina", "elcomercio", "idl", "jne", "rpp",
                            "bbc_mundo", "elpais_intl"],
    "completed":           ["andina", "jne"],
}


def _filter_intl_relevant(items: List[Dict], country_keywords: Optional[List[str]] = None) -> List[Dict]:
    """Filtra items de fuentes internacionales que mencionen el pais.

    Para fuentes intl (BBC, DW, El Pais, Guardian, NYT) la mayoria de items son
    sobre otros temas. Conservamos solo los que mencionan Peru/Perú/Lima en
    title o description (case-insensitive). Las fuentes peruanas pasan sin
    filtrar (todas son sobre Peru por default).
    """
    if country_keywords is None:
        country_keywords = ["peru", "perú", "lima"]
    needles = [k.lower() for k in country_keywords]
    out = []
    for item in items:
        src = item.get("source", "")
        if src not in INTL_SOURCES:
            out.append(item)
            continue
        haystack = f"{item.get('title', '')} {item.get('description', '')}".lower()
        if any(n in haystack for n in needles):
            item["international"] = True
            out.append(item)
    return out

_HEADERS = {
    "User-Agent": "DEMOCRAC.IA-Hunter/1.0 (+https://github.com/democracia-ia)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
}


def _parse_rss(xml_text: str, source_key: str, feed_url: str) -> List[Dict]:
    """Parsea RSS 2.0 o Atom. Retorna lista de ítems normalizados."""
    items: List[Dict] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items

    tag = root.tag.lower()
    ns_atom = "http://www.w3.org/2005/Atom"

    # ── RSS 2.0 ──
    if "rss" in tag or root.find("channel") is not None:
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link  = (item.findtext("link")  or "").strip()
            desc  = (item.findtext("description") or "").strip()
            pub   = (item.findtext("pubDate") or "").strip()
            if title:
                items.append({
                    "title":       title,
                    "url":         link,
                    "description": desc[:500],
                    "published":   pub,
                    "source":      source_key,
                    "feed_url":    feed_url,
                })

    # ── Atom ──
    elif "feed" in tag or f"{{{ns_atom}}}feed" in tag:
        ns = {"a": ns_atom}
        for entry in root.findall(f".//{{{ns_atom}}}entry"):
            title   = (entry.findtext(f"{{{ns_atom}}}title")   or "").strip()
            summary = (entry.findtext(f"{{{ns_atom}}}summary") or "").strip()
            pub     = (entry.findtext(f"{{{ns_atom}}}published") or "").strip()
            link_el = entry.find(f"{{{ns_atom}}}link")
            link    = link_el.get("href", "") if link_el is not None else ""
            if title:
                items.append({
                    "title":       title,
                    "url":         link,
                    "description": summary[:500],
                    "published":   pub,
                    "source":      source_key,
                    "feed_url":    feed_url,
                })

    # ── Sitemap (fallback para RPP y similares) ──
    elif "urlset" in tag or "sitemapindex" in tag:
        ns_sitemap = "http://www.sitemaps.org/schemas/sitemap/0.9"
        ns_news    = "http://www.google.com/schemas/sitemap-news/0.9"
        for url_el in root.findall(f".//{{{ns_sitemap}}}url"):
            loc   = (url_el.findtext(f"{{{ns_sitemap}}}loc") or "").strip()
            title_el = url_el.find(f".//{{{ns_news}}}title")
            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            pub_el = url_el.find(f".//{{{ns_news}}}publication_date")
            pub    = pub_el.text.strip() if pub_el is not None and pub_el.text else ""
            if title and loc:
                items.append({
                    "title":       title,
                    "url":         loc,
                    "description": "",
                    "published":   pub,
                    "source":      source_key,
                    "feed_url":    feed_url,
                })

    return items


async def fetch_feed(source_key: str, url: str, timeout: int = 12) -> List[Dict]:
    """Fetches y parsea un feed RSS/Atom/Sitemap. Retorna [] si falla."""
    items, _err = await fetch_feed_debug(source_key, url, timeout)
    return items


async def fetch_feed_debug(source_key: str, url: str, timeout: int = 12):
    """
    Variante instrumentada: devuelve (items, error_info).
    error_info = None si OK, o dict {kind, detail} si hubo problema.
    Usado por el endpoint /api/hunter/debug-fetch para diagnosticar fallos en producción.
    """
    try:
        async with httpx.AsyncClient(
            timeout=timeout, follow_redirects=True, verify=False
        ) as client:
            resp = await client.get(url, headers=_HEADERS)
            if resp.status_code != 200:
                return [], {
                    "kind": "http_error",
                    "status": resp.status_code,
                    "detail": f"HTTP {resp.status_code}",
                    "body_preview": resp.text[:200] if resp.text else "",
                }
            items = _parse_rss(resp.text, source_key, url)
            if not items:
                return [], {
                    "kind": "parse_empty",
                    "status": 200,
                    "detail": "200 OK pero parser no extrajo items",
                    "body_preview": resp.text[:200],
                    "content_type": resp.headers.get("content-type", ""),
                }
            return items, None
    except Exception as e:
        return [], {
            "kind": "exception",
            "detail": f"{type(e).__name__}: {str(e)[:200]}",
        }


async def fetch_sources(phase: str, extra_keys: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
    """
    Fetches todas las fuentes RSS correspondientes a la fase activa.
    Retorna dict {source_key: [items]}.
    También acepta extra_keys para forzar fuentes adicionales.
    """
    import asyncio

    keys = list(PHASE_SOURCES.get(phase, PHASE_SOURCES["campaign"]))
    if extra_keys:
        for k in extra_keys:
            if k not in keys and k in RSS_FEEDS:
                keys.append(k)

    # Fetch en paralelo
    tasks = []
    meta  = []   # (source_key, url)
    for key in keys:
        for url in RSS_FEEDS.get(key, []):
            tasks.append(fetch_feed(key, url))
            meta.append((key, url))

    results_flat = await asyncio.gather(*tasks)

    # Agrupa por source_key
    by_source: Dict[str, List[Dict]] = {}
    for (key, _url), items in zip(meta, results_flat):
        if key not in by_source:
            by_source[key] = []
        # Filtro Peru-relevante para fuentes internacionales
        if key in INTL_SOURCES:
            items = _filter_intl_relevant(items)
        by_source[key].extend(items)

    return by_source


def dedupe_items(items: List[Dict], max_per_source: int = 20) -> List[Dict]:
    """Deduplica por URL y limita ítems por fuente."""
    seen_urls: set = set()
    by_source: Dict[str, List[Dict]] = {}
    for item in items:
        url = item.get("url", "")
        src = item.get("source", "unknown")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        if src not in by_source:
            by_source[src] = []
        if len(by_source[src]) < max_per_source:
            by_source[src].append(item)

    out = []
    for v in by_source.values():
        out.extend(v)
    return out
