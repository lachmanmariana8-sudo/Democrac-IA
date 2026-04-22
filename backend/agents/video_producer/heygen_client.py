"""Cliente mínimo para HeyGen API v2.

Doc de referencia: https://docs.heygen.com/reference/create-video
Endpoints usados:
  - POST /v2/video/generate            — crear video desde guión
  - GET  /v1/video_status.get          — consultar estado + URL final
  - GET  /v2/avatars                   — listar avatares disponibles
  - GET  /v2/voices                    — listar voces

Todas las llamadas son síncronas y HTTP — la demora de renderización de HeyGen
(típicamente 30-120s) se maneja por polling del endpoint /v1/video_status.get
desde el orquestador o el frontend.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx


HEYGEN_BASE_URL = "https://api.heygen.com"

# Defaults sensatos — son avatares y voces públicos que HeyGen mantiene estables.
# Si cambian, sobrescribir vía env var o desde el request del usuario.
DEFAULT_AVATAR_ID = os.environ.get(
    "HEYGEN_DEFAULT_AVATAR", "Daisy-inskirt-20220818"
)
DEFAULT_VOICE_BY_LANG: Dict[str, str] = {
    "es": os.environ.get("HEYGEN_VOICE_ES", "2d5b0e6cf36f460aa7fc47e3eee4ba54"),
    "en": os.environ.get("HEYGEN_VOICE_EN", "1bd001e7e50f421d891986aad5158bc8"),
    "pt": os.environ.get("HEYGEN_VOICE_PT", "a60ebdd9da0d47b4aaaa10b4c7e3e3b4"),
    "qu": os.environ.get("HEYGEN_VOICE_QU", ""),     # quechua: requiere custom voice
}


class HeyGenError(Exception):
    """Error lanzado por el cliente HeyGen."""


class HeyGenClient:
    """Cliente minimalista de HeyGen — sin dependencias adicionales."""

    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        self.api_key = api_key or os.environ.get("HEYGEN_API_KEY", "")
        self.timeout = timeout
        if not self.api_key:
            # Permitimos instanciar sin clave (modo dry_run); las llamadas fallarán.
            pass

    def _headers(self) -> Dict[str, str]:
        return {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def is_configured(self) -> bool:
        return bool(self.api_key)

    # ── Generación de video ─────────────────────────────────────────────
    def generate_video(
        self,
        script_text: str,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None,
        language: str = "es",
        dimension_w: int = 1280,
        dimension_h: int = 720,
        background_hex: str = "#0f4f4b",
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Lanza la generación del video. Devuelve {"video_id": "..."}."""
        if not self.api_key:
            raise HeyGenError("HEYGEN_API_KEY no configurada.")

        avatar = avatar_id or DEFAULT_AVATAR_ID
        voice = voice_id or DEFAULT_VOICE_BY_LANG.get(language) or DEFAULT_VOICE_BY_LANG["es"]

        payload: Dict[str, Any] = {
            "caption": True,
            "dimension": {"width": dimension_w, "height": dimension_h},
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar,
                        "avatar_style": "normal",
                    },
                    "voice": {
                        "type": "text",
                        "input_text": script_text[:3800],  # HeyGen limita ~4k chars
                        "voice_id": voice,
                    },
                    "background": {
                        "type": "color",
                        "value": background_hex,
                    },
                }
            ],
        }
        if title:
            payload["title"] = title[:120]

        try:
            with httpx.Client(timeout=self.timeout) as client:
                r = client.post(
                    f"{HEYGEN_BASE_URL}/v2/video/generate",
                    json=payload,
                    headers=self._headers(),
                )
                if r.status_code >= 400:
                    raise HeyGenError(f"HeyGen {r.status_code}: {r.text[:500]}")
                body = r.json()
        except httpx.HTTPError as e:
            raise HeyGenError(f"HTTP error: {e}")

        data = body.get("data") or {}
        video_id = data.get("video_id") or body.get("video_id")
        if not video_id:
            raise HeyGenError(f"Respuesta HeyGen sin video_id: {body}")
        return {"video_id": video_id, "raw": body}

    # ── Consulta de estado ──────────────────────────────────────────────
    def get_status(self, video_id: str) -> Dict[str, Any]:
        """Consulta estado. Devuelve dict con status/video_url/thumbnail_url/error."""
        if not self.api_key:
            raise HeyGenError("HEYGEN_API_KEY no configurada.")
        try:
            with httpx.Client(timeout=self.timeout) as client:
                r = client.get(
                    f"{HEYGEN_BASE_URL}/v1/video_status.get",
                    params={"video_id": video_id},
                    headers=self._headers(),
                )
                if r.status_code >= 400:
                    raise HeyGenError(f"HeyGen {r.status_code}: {r.text[:300]}")
                body = r.json()
        except httpx.HTTPError as e:
            raise HeyGenError(f"HTTP error: {e}")

        data = body.get("data") or {}
        return {
            "status": data.get("status", "unknown"),
            "video_url": data.get("video_url"),
            "thumbnail_url": data.get("thumbnail_url"),
            "duration_s": data.get("duration"),
            "error": data.get("error"),
            "raw": body,
        }

    # ── Listar avatares / voces (para poblar UI) ────────────────────────
    def list_avatars(self) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []
        try:
            with httpx.Client(timeout=self.timeout) as client:
                r = client.get(f"{HEYGEN_BASE_URL}/v2/avatars", headers=self._headers())
                if r.status_code >= 400:
                    return []
                data = r.json().get("data") or {}
                # HeyGen devuelve data.avatars o similar según versión
                return (data.get("avatars") or data.get("list") or [])[:200]
        except Exception:
            return []

    def list_voices(self, language: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []
        try:
            with httpx.Client(timeout=self.timeout) as client:
                r = client.get(f"{HEYGEN_BASE_URL}/v2/voices", headers=self._headers())
                if r.status_code >= 400:
                    return []
                data = r.json().get("data") or {}
                voices = data.get("voices") or data.get("list") or []
                if language:
                    voices = [v for v in voices if (v.get("language") or "").lower().startswith(language.lower())]
                return voices[:500]
        except Exception:
            return []
