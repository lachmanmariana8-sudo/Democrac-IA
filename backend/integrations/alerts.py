"""
DEMOCRAC.IA / PEIRS — AlertDispatchAgent (Agent 7)
Dispara notificaciones en tiempo real ante hallazgos críticos o patrones de fraude.

Canales soportados:
  - Slack (webhook URL)
  - Webhook genérico (Teams, Discord, N8N, Zapier, etc.)
  - SMTP email (async via asyncio)

Configuración via variables de entorno:
  ALERT_SLACK_WEBHOOK_URL     — URL del webhook de Slack
  ALERT_WEBHOOK_URL           — Webhook genérico (POST JSON)
  ALERT_EMAIL_TO              — Destinatario(s) separados por coma
  ALERT_EMAIL_FROM            — Remitente
  ALERT_SMTP_HOST             — Host SMTP (default: localhost)
  ALERT_SMTP_PORT             — Puerto SMTP (default: 587)
  ALERT_SMTP_USER             — Usuario SMTP (opcional)
  ALERT_SMTP_PASS             — Contraseña SMTP (opcional)
  ALERT_MIN_SEVERITY          — Severidad mínima para disparar alerta (default: critical)
  ALERT_FRAUD_SCORE_THRESHOLD — Score mínimo de fraude para alerta (default: 0.6)

Uso:
  from integrations.alerts import dispatch_alert, AlertEvent
  await dispatch_alert(AlertEvent(...))
"""

from __future__ import annotations

import os
import json
import asyncio
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from dataclasses import dataclass, field

try:
    import httpx
    _HTTPX_OK = True
except ImportError:
    _HTTPX_OK = False


# ── Configuración desde entorno ───────────────────────────────────────────────

SLACK_WEBHOOK_URL     = os.getenv("ALERT_SLACK_WEBHOOK_URL", "")
GENERIC_WEBHOOK_URL   = os.getenv("ALERT_WEBHOOK_URL", "")
EMAIL_TO              = [e.strip() for e in os.getenv("ALERT_EMAIL_TO", "").split(",") if e.strip()]
EMAIL_FROM            = os.getenv("ALERT_EMAIL_FROM", "noreply@democracia.ia")
SMTP_HOST             = os.getenv("ALERT_SMTP_HOST", "localhost")
SMTP_PORT             = int(os.getenv("ALERT_SMTP_PORT", "587"))
SMTP_USER             = os.getenv("ALERT_SMTP_USER", "")
SMTP_PASS             = os.getenv("ALERT_SMTP_PASS", "")
MIN_SEVERITY          = os.getenv("ALERT_MIN_SEVERITY", "critical")
FRAUD_SCORE_THRESHOLD = float(os.getenv("ALERT_FRAUD_SCORE_THRESHOLD", "0.6"))

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

# Historial de alertas enviadas (evita duplicados en ventana de 10 min)
_alert_history: dict = {}
DEDUP_WINDOW_SECONDS = 600


# ── Estructura del evento ─────────────────────────────────────────────────────

@dataclass
class AlertEvent:
    """Representa un evento que puede generar una alerta."""
    event_type: str                        # "critical_entry"|"pattern_detected"|"fraud_score"|"escalation"
    country_code: str
    severity: str
    title: str
    description: str
    entry_id: Optional[str] = None
    location: Optional[str] = None
    observer_id: Optional[str] = None
    phase: Optional[str] = None
    rights_at_risk: List[str] = field(default_factory=list)
    iccpr_ref: Optional[str] = None
    fraud_score: Optional[float] = None
    run_id: Optional[str] = None
    # ── Trazabilidad de fuente (Hunter RSS) ──
    source_url: Optional[str] = None       # URL del artículo original (evidence_ref del entry)
    source_name: Optional[str] = None      # Medio que publicó (Andina, El Comercio, etc.)
    source_title: Optional[str] = None     # Título original del artículo
    category: Optional[str] = None         # Categoría del hallazgo
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ── Lógica de disparo ─────────────────────────────────────────────────────────

def should_dispatch(event: AlertEvent) -> bool:
    """Determina si el evento debe generar una alerta."""
    # Verificar severidad mínima
    if SEVERITY_ORDER.get(event.severity, 0) < SEVERITY_ORDER.get(MIN_SEVERITY, 4):
        if event.event_type not in ("pattern_detected", "fraud_score", "escalation"):
            return False

    # Deduplicación: no repetir la misma alerta en la ventana
    dedup_key = f"{event.country_code}:{event.event_type}:{event.entry_id or event.title[:30]}"
    now_ts = datetime.now(timezone.utc).timestamp()
    if dedup_key in _alert_history:
        elapsed = now_ts - _alert_history[dedup_key]
        if elapsed < DEDUP_WINDOW_SECONDS:
            return False
    _alert_history[dedup_key] = now_ts

    # Verificar que hay al menos un canal configurado
    return bool(SLACK_WEBHOOK_URL or GENERIC_WEBHOOK_URL or EMAIL_TO)


# ── Formateadores ─────────────────────────────────────────────────────────────

def _format_slack(event: AlertEvent) -> dict:
    """Formatea el evento para Slack Block Kit."""
    severity_emoji = {
        "critical": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢", "info": "ℹ️"
    }.get(event.severity, "❓")

    phase_label = {
        "pre_election": "Pre-Jornada", "election_day": "Jornada Electoral",
        "post_election": "Post-Electoral",
    }.get(event.phase or "", event.phase or "—")

    fields = [
        {"type": "mrkdwn", "text": f"*País:*\n{event.country_code}"},
        {"type": "mrkdwn", "text": f"*Fase:*\n{phase_label}"},
        {"type": "mrkdwn", "text": f"*Severidad:*\n{severity_emoji} {event.severity.upper()}"},
        {"type": "mrkdwn", "text": f"*Observador:*\n{event.observer_id or '—'}"},
    ]
    if event.location:
        fields.append({"type": "mrkdwn", "text": f"*Ubicación:*\n{event.location}"})
    if event.rights_at_risk:
        fields.append({"type": "mrkdwn", "text": f"*Derechos en riesgo:*\n{'; '.join(event.rights_at_risk[:3])}"})
    if event.fraud_score is not None:
        fields.append({"type": "mrkdwn", "text": f"*Score de fraude:*\n{event.fraud_score:.0%}"})

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{severity_emoji} DEMOCRAC.IA — {event.title}"}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": event.description}
        },
        {"type": "section", "fields": fields},
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"PEIRS · {event.timestamp[:16]} UTC · entry `{event.entry_id or '—'}`"}]
        }
    ]
    return {"blocks": blocks}


def _format_generic_webhook(event: AlertEvent) -> dict:
    """Payload JSON genérico para Teams, Discord, N8N, Zapier, etc."""
    return {
        "system":       "DEMOCRAC.IA / PEIRS",
        "event_type":   event.event_type,
        "country_code": event.country_code,
        "title":        event.title,
        "description":  event.description,
        "severity":     event.severity,
        "phase":        event.phase,
        "location":     event.location,
        "observer_id":  event.observer_id,
        "entry_id":     event.entry_id,
        "rights_at_risk": event.rights_at_risk,
        "fraud_score":  event.fraud_score,
        "run_id":       event.run_id,
        "timestamp":    event.timestamp,
    }


def _format_email(event: AlertEvent) -> tuple[str, str]:
    """Retorna (subject, html_body) para email."""
    severity_label = event.severity.upper()
    phase_label = {
        "pre_election": "Pre-Jornada (48h previas)",
        "election_day": "Jornada Electoral",
        "post_election": "Post-Electoral (72h)",
    }.get(event.phase or "", event.phase or "—")

    rights_html = ""
    if event.rights_at_risk:
        items = "".join(f"<li>{r}</li>" for r in event.rights_at_risk)
        rights_html = f"<p><strong>Derechos potencialmente vulnerados:</strong><ul>{items}</ul></p>"

    subject = f"[PEIRS {severity_label}] {event.country_code} — {event.title}"
    body = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 600px;">
    <h2 style="color: {'#d32f2f' if event.severity == 'critical' else '#f57c00'};">
      DEMOCRAC.IA / PEIRS — {event.title}
    </h2>
    <table style="width:100%; border-collapse:collapse;">
      <tr><td><strong>País:</strong></td><td>{event.country_code}</td></tr>
      <tr><td><strong>Fase:</strong></td><td>{phase_label}</td></tr>
      <tr><td><strong>Severidad:</strong></td><td>{severity_label}</td></tr>
      <tr><td><strong>Observador:</strong></td><td>{event.observer_id or '—'}</td></tr>
      <tr><td><strong>Ubicación:</strong></td><td>{event.location or '—'}</td></tr>
      <tr><td><strong>Hallazgo ID:</strong></td><td>{event.entry_id or '—'}</td></tr>
      {'<tr><td><strong>Score fraude:</strong></td><td>' + f"{event.fraud_score:.0%}" + '</td></tr>' if event.fraud_score is not None else ''}
    </table>
    <p style="margin-top: 16px;"><strong>Descripción:</strong><br>{event.description}</p>
    {rights_html}
    <hr>
    <p style="color:#888; font-size:12px;">
      PEIRS · {event.timestamp[:16]} UTC · Run ID: {event.run_id or '—'}
    </p>
    </body></html>
    """
    return subject, body


# ── Despachadores por canal ───────────────────────────────────────────────────

async def _send_slack(event: AlertEvent) -> bool:
    if not SLACK_WEBHOOK_URL or not _HTTPX_OK:
        return False
    payload = _format_slack(event)
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.post(SLACK_WEBHOOK_URL, json=payload)
            return r.status_code == 200
    except Exception as exc:
        print(f"[ALERT] Slack error: {exc}")
        return False


def _format_discord_webhook(event: AlertEvent) -> dict:
    """Payload con embeds para Discord webhooks. Incluye link a fuente original cuando existe."""
    sev = event.severity.upper()
    color_map = {"CRITICAL": 0xD32F2F, "HIGH": 0xF57C00, "MEDIUM": 0xFBC02D, "LOW": 0x388E3C, "INFO": 0x1976D2}

    # Etiquetas legibles para fuentes y categorías
    source_labels = {
        "andina":     "Andina (agencia oficial)",
        "elcomercio": "El Comercio",
        "gestion":    "Gestión",
        "idl":        "IDL-Reporteros",
        "wayka":      "Wayka",
        "rpp":        "RPP Noticias",
        "jne":        "JNE (oficial)",
        "onpe":       "ONPE (oficial)",
        "ooni":       "OONI (censura digital)",
    }
    category_labels = {
        "disinformation":      "🗣️ Desinformación",
        "media_restriction":   "📰 Restricción a medios",
        "campaign_violation":  "⚖️ Violación de campaña",
        "fraud_allegation":    "🚨 Alegación de fraude",
        "hate_speech":         "💢 Discurso de odio",
        "voter_suppression":   "🚫 Supresión del voto",
        "violence":            "⚠️ Violencia política",
        "digital":             "💻 Incidente digital",
        "institutional":       "🏛️ Crisis institucional",
        "gender_violence":     "♀️ Violencia política de género",
        "transparency":        "🔍 Transparencia electoral",
        "other":               "📌 Otro",
    }

    fields = []
    fields.append({"name": "País", "value": event.country_code, "inline": True})
    fields.append({"name": "Severidad", "value": sev, "inline": True})
    if event.category:
        fields.append({"name": "Categoría", "value": category_labels.get(event.category, event.category), "inline": True})

    if event.location:
        fields.append({"name": "📍 Ubicación", "value": event.location, "inline": True})
    if event.phase:
        fields.append({"name": "Fase", "value": event.phase, "inline": True})
    if event.fraud_score is not None:
        fields.append({"name": "Score fraude", "value": f"{event.fraud_score:.0%}", "inline": True})

    # Bloque de FUENTE — lo más importante para la observadora
    if event.source_url or event.source_name:
        source_value_parts = []
        if event.source_name:
            source_value_parts.append(f"**{source_labels.get(event.source_name, event.source_name)}**")
        if event.source_title:
            # Discord soporta truncado natural; limitamos para no romper layout
            title_clip = event.source_title[:200]
            if event.source_url:
                # Discord embed soporta markdown link
                source_value_parts.append(f"[{title_clip}]({event.source_url})")
            else:
                source_value_parts.append(title_clip)
        elif event.source_url:
            source_value_parts.append(f"[Ver artículo original]({event.source_url})")
        fields.append({
            "name": "📎 Fuente original",
            "value": "\n".join(source_value_parts) or "—",
            "inline": False,
        })

    if event.rights_at_risk:
        fields.append({
            "name": "⚖️ Derechos en riesgo",
            "value": ", ".join(event.rights_at_risk[:5]),
            "inline": False,
        })

    embed = {
        "title": event.title[:256],
        "description": (event.description or "")[:2000],
        "color": color_map.get(sev, 0x9E9E9E),
        "fields": fields,
        "footer": {"text": f"PEIRS · {event.timestamp[:16]} UTC · entry {event.entry_id or '—'}"},
    }
    # Si hay URL de fuente, también la ponemos como url del embed (clickeable en el título)
    if event.source_url:
        embed["url"] = event.source_url

    return {"embeds": [embed]}


async def _send_webhook(event: AlertEvent) -> bool:
    if not GENERIC_WEBHOOK_URL or not _HTTPX_OK:
        return False
    is_discord = "discord.com/api/webhooks" in GENERIC_WEBHOOK_URL
    payload = _format_discord_webhook(event) if is_discord else _format_generic_webhook(event)
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.post(GENERIC_WEBHOOK_URL, json=payload)
            return r.status_code < 300
    except Exception as exc:
        print(f"[ALERT] Webhook error: {exc}")
        return False


async def _send_email(event: AlertEvent) -> bool:
    if not EMAIL_TO:
        return False
    subject, html_body = _format_email(event)
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = EMAIL_FROM
        msg["To"]      = ", ".join(EMAIL_TO)
        msg.attach(MIMEText(html_body, "html"))

        # Enviar en executor para no bloquear el event loop
        def _smtp_send():
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                if SMTP_PORT == 587:
                    server.starttls()
                if SMTP_USER and SMTP_PASS:
                    server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _smtp_send)
        return True
    except Exception as exc:
        print(f"[ALERT] Email error: {exc}")
        return False


# ── Función principal ─────────────────────────────────────────────────────────

async def dispatch_alert(event: AlertEvent) -> dict:
    """
    Despacha una alerta a todos los canales configurados.
    Retorna dict con el resultado por canal.
    No lanza excepciones — fallo silencioso con log.
    """
    if not should_dispatch(event):
        return {"dispatched": False, "reason": "below_threshold_or_duplicate"}

    print(f"[ALERT] Despachando: {event.event_type} — {event.country_code} — {event.severity}")

    results = await asyncio.gather(
        _send_slack(event),
        _send_webhook(event),
        _send_email(event),
        return_exceptions=True,
    )

    channels = {
        "slack":   results[0] if not isinstance(results[0], Exception) else False,
        "webhook": results[1] if not isinstance(results[1], Exception) else False,
        "email":   results[2] if not isinstance(results[2], Exception) else False,
    }
    sent_count = sum(1 for v in channels.values() if v is True)

    return {
        "dispatched":  sent_count > 0,
        "channels":    channels,
        "sent_to":     sent_count,
        "event_type":  event.event_type,
        "timestamp":   event.timestamp,
    }


def build_entry_alert(entry: dict, session: dict, patterns=None) -> AlertEvent:
    """
    Construye un AlertEvent a partir de un hallazgo recién ingresado.
    Incluye contexto de patrones si se detectaron.
    """
    severity = entry.get("severity", "info")
    category = entry.get("category", "other")
    location = entry.get("location", "")
    finding  = entry.get("finding", "")[:200]
    rights   = entry.get("rights_at_risk", [])

    # Título según tipo de evento
    if category == "fraud_allegation":
        title = f"Alegación de Fraude Electoral — {location or session.get('country_code', '?')}"
        event_type = "critical_entry"
    elif category == "hate_speech":
        title = f"Incidente de Discurso de Odio — {entry.get('target_group', 'grupo no especificado')}"
        event_type = "critical_entry"
    else:
        title = f"Hallazgo {severity.upper()} — {category} ({location or '?'})"
        event_type = "critical_entry"

    description = finding
    fraud_score = None

    if patterns and getattr(patterns, "has_significant_patterns", False):
        event_type  = "pattern_detected"
        fraud_score = getattr(patterns, "fraud_pattern_score", None)
        if fraud_score and fraud_score >= FRAUD_SCORE_THRESHOLD:
            event_type = "fraud_score"
            title = f"⚠️ PATRÓN DE FRAUDE DETECTADO ({fraud_score:.0%}) — {session.get('country_code', '?')}"
            description = getattr(patterns, "summary", finding)
        elif getattr(patterns, "escalation_detected", False):
            event_type  = "escalation"
            title = f"⚡ ESCALADA DE SEVERIDAD — {session.get('country_code', '?')}"
            description = getattr(patterns, "escalation_description", finding)

    # Traza de fuente: el Hunter rellena evidence_ref con la URL del RSS y source con el medio.
    source_url   = entry.get("evidence_ref") or entry.get("url") or None
    source_name  = entry.get("source") or None
    source_title = entry.get("title") or None

    return AlertEvent(
        event_type=event_type,
        country_code=session.get("country_code", "??"),
        severity=severity,
        title=title,
        description=description,
        entry_id=entry.get("entry_id"),
        location=location,
        observer_id=entry.get("observer_id"),
        phase=entry.get("phase"),
        rights_at_risk=rights,
        fraud_score=fraud_score,
        run_id=session.get("run_id"),
        source_url=source_url,
        source_name=source_name,
        source_title=source_title,
        category=category,
    )
