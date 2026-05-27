// Constantes y helpers compartidos entre Landing, Voto y Dashboard.
// Antes vivían inline en App.jsx (11.5k líneas, ver Sprint 2 audit).
// Solo constantes/funciones — el componente BrandLogo vive en BrandLogo.jsx.

// Paleta UNIFICADA con la landing: cremas cálidas + navy + terracota.
// Antes el dashboard usaba dark theme separado; consolidamos para coherencia
// visual en toda la web (16-may-2026).
//
// Mapeo semantico:
//   bg        : fondo principal (crema cálida)
//   surface   : cards y bloques
//   surfaceLight: highlight/hover
//   border    : separadores
//   text      : ink navy del brand
//   textMuted : grey-navy medio (subtítulos)
//   textDim   : grey-navy claro (timestamps)
//   accent    : terracota brand (CTAs, hover state)
//   danger    : rojo apagado en gama
//   warning   : ámbar dorado
//   info      : navy medio
//   purple    : violeta apagado
export const COLORS = {
  bg: "#fbf9f6",
  surface: "#ffffff",
  surfaceLight: "#f7f3ed",
  border: "#e5dcd0",
  text: "#1c2230",
  textMuted: "#5d6878",
  textDim: "#8b94a3",
  accent: "#c25a3a",
  accentDim: "#c25a3a1a",
  danger: "#c04141",
  dangerDim: "#c041411a",
  warning: "#c8893a",
  warningDim: "#c8893a1a",
  info: "#3a4356",
  infoDim: "#3a43561a",
  purple: "#7c5f8a",
  purpleDim: "#7c5f8a1a",
  textPrimary: "#1c2230",
  textSecondary: "#3a4356",
  cardBg: "#ffffff",
};

// Brand identity — colores brand "puros" (light context, print, cover de informes).
// En dashboard (dark theme) los rings usan COLORS.text para visibilidad.
export const BRAND = {
  ink: "#1c2230",        // navy oscuro (cover impreso, fondo claro)
  terracotta: "#c25a3a", // accent del punto + ".IA"
};

// Paleta clara usada en LandingPage y VotoInformadoPage (cremas + terracota).
export const LIGHT = {
  bg:           "#fbf9f6",
  bgAlt:        "#f4efe8",
  surface:      "#ffffff",
  surfaceAlt:   "#f7f3ed",
  border:       "#e5dcd0",
  borderStrong: "#d0c4b0",
  ink:          "#1c2230",
  inkSoft:      "#3a4356",
  textMuted:    "#5d6878",
  textDim:      "#8b94a3",
  terracotta:   "#c25a3a",
  terracottaSoft: "#e8b8a6",
  terracottaBg: "#fdf2ed",
  success:      "#4a7c59",
  warning:      "#c8893a",
};

export const RISK_LEVELS = {
  critical: { color: COLORS.danger, label: "CRÍTICO", bg: COLORS.dangerDim },
  high: { color: "#f97316", label: "ALTO", bg: "#f9731633" },
  moderate: { color: COLORS.warning, label: "MODERADO", bg: COLORS.warningDim },
  low: { color: COLORS.accent, label: "BAJO", bg: COLORS.accentDim },
};

export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// ── Observer API key (para endpoints caros: elite/designer) ───────────────
// Prioridad: localStorage > VITE_OBSERVER_KEY > ""
// Onboarding: si la URL trae ?key=xyz, se guarda en localStorage y se limpia la URL.
export function getObserverKey() {
  try {
    const fromLS = localStorage.getItem("peirs_observer_key");
    if (fromLS) return fromLS;
  } catch { /* localStorage unavailable */ }
  return import.meta.env.VITE_OBSERVER_KEY || "";
}

export function authHeaders(extra = {}) {
  const k = getObserverKey();
  const headers = { "Content-Type": "application/json", ...extra };
  if (k) headers["X-Observer-Key"] = k;
  return headers;
}

(function ingestKeyFromURL() {
  try {
    const u = new URL(window.location.href);
    const qk = u.searchParams.get("key");
    if (qk) {
      localStorage.setItem("peirs_observer_key", qk);
      u.searchParams.delete("key");
      window.history.replaceState({}, "", u.toString());
    }
  } catch { /* localStorage unavailable */ }
})();
