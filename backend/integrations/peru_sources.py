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
    # HTTP 200, formato RSS 2.0 verificado.
    "andina": [
        "https://andina.pe/rss/politica.xml",
    ],
    # RPP Noticias — radio/digital de mayor audiencia política en Perú.
    # HTTP 200, formato RSS 2.0 verificado.
    "rpp": [
        "https://rpp.pe/feed/",
    ],
    # JNE — feed pendiente de verificación (403/404 en pruebas directas).
    # Se mantiene para reintentos con headers de browser.
    "jne": [
        "https://www.jne.gob.pe/feed/",
    ],
    # ONPE — devuelve 403, puede requerir sesión o user-agent específico.
    "onpe": [
        "https://www.onpe.gob.pe/feed/",
    ],
}

# ── Fuentes activas por fase electoral ───────────────────────────────────────
PHASE_SOURCES: Dict[str, List[str]] = {
    "preparatory":         ["andina", "jne"],
    "pre_campaign":        ["andina", "jne", "onpe", "rpp"],
    "campaign":            ["andina", "rpp", "jne", "onpe"],
    "electoral_silence":   ["andina", "rpp"],          # + OONI en Hunter
    "election_day":        ["andina", "rpp", "onpe"],  # + OONI en Hunter
    "counting_tabulation": ["andina", "rpp", "onpe", "jne"],
    "post_election":       ["andina", "rpp", "jne", "onpe"],
    "dispute_resolution":  ["andina", "jne", "rpp"],
    "completed":           ["andina", "jne"],
}

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
    try:
        async with httpx.AsyncClient(
            timeout=timeout, follow_redirects=True, verify=False
        ) as client:
            resp = await client.get(url, headers=_HEADERS)
            if resp.status_code != 200:
                return []
            return _parse_rss(resp.text, source_key, url)
    except Exception:
        return []


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
