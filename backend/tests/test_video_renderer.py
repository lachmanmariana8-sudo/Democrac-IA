"""Tests del FrameRenderer del Video Producer v2 (Fase B1).

Cubre los 3 visuales implementados (solid_bg, kpi_grid, quote_panel) + el
fallback para visuales pendientes (Fase B2). No hace diffs visuales — sólo
verifica que el renderer produce PNGs válidos y no crashea.
"""
from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Skip si Pillow no está instalado (el renderer lo requiere).
PIL = pytest.importorskip("PIL")
from PIL import Image  # noqa: E402

from agents.video_producer.models import Beat, Overlay  # noqa: E402
from agents.video_producer.renderer import (  # noqa: E402
    FrameRenderer,
    render_beat_png,
)


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _assert_png(data: bytes, min_size: int = 1000) -> Image.Image:
    assert data[:8] == PNG_MAGIC, "no es un PNG válido"
    assert len(data) >= min_size, f"PNG sospechosamente chico: {len(data)} bytes"
    img = Image.open(BytesIO(data))
    img.load()
    return img


class TestSolidBg:
    def test_intro_con_title_y_source(self):
        beat = Beat(
            beat_id="b00_intro",
            kind="intro",
            duration_s=2.0,
            narration="Apertura",
            visual="solid_bg",
            overlays=[
                Overlay(kind="title", text="DemocracIA / PEIRS", position="center"),
                Overlay(kind="source", text="Observación electoral · Perú 2026", position="bottom"),
            ],
        )
        png = render_beat_png(beat, width=1080, height=1920)
        img = _assert_png(png)
        assert img.size == (1080, 1920)
        assert img.mode == "RGB"

    def test_outro_con_cta(self):
        beat = Beat(
            beat_id="b99_outro",
            kind="outro",
            duration_s=2.0,
            visual="solid_bg",
            overlays=[Overlay(kind="cta", text="democracia.ar", position="center")],
        )
        png = render_beat_png(beat, width=1080, height=1920)
        _assert_png(png)

    def test_lower_third_sobre_solid(self):
        beat = Beat(
            beat_id="b01_incident",
            kind="incident",
            duration_s=5.0,
            visual="solid_bg",
            overlays=[
                Overlay(
                    kind="lower_third",
                    text="JNE denuncia penalmente a Corvetto",
                    secondary_text="IDL-Reporteros · 12-abr-2026",
                    position="bottom",
                ),
            ],
        )
        png = render_beat_png(beat, width=1080, height=1920)
        _assert_png(png)


class TestKpiGrid:
    def test_cuatro_kpis(self):
        beat = Beat(
            beat_id="b01_stat",
            kind="stat",
            duration_s=4.0,
            visual="kpi_grid",
            visual_data={
                "kpis": [
                    {"label": "Hallazgos", "value": 1309},
                    {"label": "Críticos",  "value": 22},
                    {"label": "Altos",     "value": 289},
                    {"label": "Días",      "value": 14},
                ],
            },
        )
        png = render_beat_png(beat, width=1080, height=1920)
        _assert_png(png, min_size=3000)

    def test_kpi_grid_sin_datos(self):
        """Sin kpis en visual_data el renderer no debe crashear."""
        beat = Beat(beat_id="b_empty", kind="stat", duration_s=2.0, visual="kpi_grid")
        png = render_beat_png(beat, width=1080, height=1920)
        _assert_png(png)


class TestQuotePanel:
    def test_quote_con_atribucion(self):
        beat = Beat(
            beat_id="b05_quote",
            kind="quote",
            duration_s=6.0,
            visual="quote_panel",
            overlays=[
                Overlay(
                    kind="quote",
                    text="La crisis logística de ONPE dejó al menos 115.000 ciudadanos sin sufragar.",
                    secondary_text="Informe PEIRS · 14-abr-2026",
                    position="center",
                ),
            ],
        )
        png = render_beat_png(beat, width=1080, height=1920)
        _assert_png(png, min_size=3000)

    def test_quote_horizontal(self):
        """16:9 también debe renderizar sin crashear."""
        beat = Beat(
            beat_id="b05_quote_h",
            kind="quote",
            duration_s=6.0,
            visual="quote_panel",
            overlays=[
                Overlay(kind="quote", text="Cita en formato horizontal.", position="center"),
            ],
        )
        png = render_beat_png(beat, width=1920, height=1080)
        _assert_png(png)


class TestFallbacks:
    def test_visual_no_implementado_cae_al_fallback(self):
        """bar_chart / donut / timeline / map son Fase B2 — por ahora placeholder."""
        for vis in ("bar_chart", "donut_chart", "timeline", "map_regions"):
            beat = Beat(
                beat_id=f"b_fb_{vis}",
                kind="stat",
                duration_s=3.0,
                visual=vis,
            )
            png = render_beat_png(beat, width=1080, height=1920)
            _assert_png(png)


class TestRendererDirecto:
    def test_render_devuelve_pil_image(self):
        """FrameRenderer.render() debe devolver PIL.Image para tests visuales."""
        renderer = FrameRenderer(width=1080, height=1920)
        beat = Beat(beat_id="b00", kind="intro", duration_s=2.0, visual="solid_bg")
        img = renderer.render(beat)
        assert img.size == (1080, 1920)

    def test_dimensiones_respetadas(self):
        """Probar varias relaciones de aspecto."""
        for w, h in ((1080, 1920), (1920, 1080), (1080, 1080)):
            renderer = FrameRenderer(width=w, height=h)
            beat = Beat(beat_id="b00", kind="intro", duration_s=2.0, visual="solid_bg")
            assert renderer.render(beat).size == (w, h)
