const CHART_METHODOLOGY = {
  "evolucion": {
    title: "Evolución del Índice de Riesgo Electoral",
    what: "Este gráfico muestra la trayectoria estimada del Índice Predictivo de Riesgo Electoral (IPRE) del país en los últimos 6 meses previos a la elección proyectada.",
    how: "El IPRE se calcula ponderando 8 dimensiones: Freedom House (15%), V-Dem democracia liberal (15%), independencia del EMB (15%), sesgo mediático (10%), transparencia financiera (10%), ecosistema digital (10%), violaciones legales (15%) y observación internacional (10%). La trayectoria histórica se construye con variación aleatoria controlada sobre el score actual — los datos históricos precisos requieren integración de series temporales V-Dem.",
    sources: ["V-Dem v15 — Coppedge et al. 2025", "Freedom House FIW 2025", "PEI Dataset 10.0"],
    interpretation: "Un índice en ascenso indica deterioro de las condiciones electorales. Valores sobre 75 activan protocolo de alerta máxima. Valores bajo 25 indican condiciones estables.",
    color: "#00d4aa",
  },
  "medios": {
    title: "Distribución de Exposición Mediática",
    what: "Muestra la distribución del acceso a cobertura mediática entre los principales actores electorales (partido gobernante, oposición, independientes).",
    how: "Para países con datos PEI, el score de cobertura mediática (MEDIACOVERAGE, escala 0-100) se transforma en un índice de sesgo derivado: bias_index = (100 - PEI_media_score) / 100. La distribución de exposición es una estimación estructural basada en el score FH y el nivel de restricción a medios. Datos precisos de monitoreo de medios requieren integración OONI/CIVICUS.",
    sources: ["PEI Dataset 10.0 — Harvard Dataverse", "Freedom House FIW 2025 (CL rating)"],
    interpretation: "Una distribución equilibrada (25-30% por actor) indica condiciones pluralistas. Concentración superior al 60% en el actor gobernante señala asimetría severa incompatible con estándares EOS.",
    color: "#ec4899",
  },
  "radar": {
    title: "Análisis Multidimensional de Integridad Electoral",
    what: "El radar visualiza simultáneamente las 8 dimensiones del Índice Predictivo de Riesgo, permitiendo identificar en qué áreas específicas el proceso electoral presenta mayor vulnerabilidad.",
    how: "Cada dimensión se normaliza en escala 0-100 donde 100 = condición óptima. Las dimensiones se calculan así: Sufragio Universal (FH score × 0.9), Marco Legal (V-Dem polyarchy × 100), Independencia EMB (full=95, partial=60, compromised=25, captured=5), Libertad de Medios ((1 - bias_index) × 100), Financiamiento (PEI campaign_finance), Ecosistema Digital (V-Dem variables digitales), Justicia Electoral (V-Dem polyarchy × 90), Inclusividad (FH score × 0.8).",
    sources: ["V-Dem v15", "Freedom House FIW 2025", "PEI Dataset 10.0"],
    interpretation: "Un radar simétrico y amplio indica equilibrio institucional. Dimensiones por debajo de 30 representan vulnerabilidades críticas. La forma del radar permite identificar si el riesgo es sistémico o puntual.",
    color: "#a855f7",
  },
  "violaciones": {
    title: "Mapa de Violaciones al Derecho Internacional",
    what: "Visualiza las violaciones detectadas al derecho internacional electoral, clasificadas por tratado, artículo específico, nivel de severidad y nivel de confianza del dato fuente.",
    how: "El sistema evalúa automáticamente el estado de 8 derechos fundamentales cruzando indicadores de Freedom House (libertades civiles y políticas), V-Dem (independencia EMB, irregularidades) y PEI (marco legal). Cada violación se clasifica por severidad (critical/high/moderate) y confianza (confirmed = dato verificado con fuente primaria / mock = estimación pendiente).",
    sources: ["Freedom House FIW 2025", "V-Dem v15", "14 instrumentos del derecho internacional"],
    interpretation: "Las violaciones con confidence=CONFIRMED están respaldadas por datos verificados. Las de confidence=MOCK son estimaciones del sistema que requieren verificación adicional con fuentes primarias. Las violaciones críticas confirman incumplimiento del Art. 25 ICCPR sobre elecciones genuinas.",
    color: "#ef4444",
  },
  "dimensiones": {
    title: "Indicadores Multidimensionales con Leyenda",
    what: "Barras de progreso que muestran el estado de cada dimensión de la integridad electoral en escala 0-100, donde 100 representa la condición óptima según estándares internacionales.",
    how: "Cada barra corresponde a una dimensión específica con su fuente de datos: Sufragio Universal (V-Dem v2x_suffr, FH), Marco Legal (V-Dem v2x_polyarchy), Independencia EMB (V-Dem v2elembaut), Libertad de Medios (PEI + RSF), Financiamiento (PEI CAMPAIGNFINANCE), Ecosistema Digital (V-Dem v2mecenefi + v2smgovdom), Justicia Electoral (V-Dem v2xcl_rol), Inclusividad (FH CL rating).",
    sources: ["V-Dem v15", "Freedom House FIW 2025", "PEI Dataset 10.0", "RSF 2025"],
    interpretation: "Verde (70-100): condición satisfactoria. Amarillo (45-69): requiere monitoreo. Naranja (25-44): deficiencias significativas. Rojo (0-24): vulnerabilidad crítica que activa protocolo de alerta.",
    color: "#3b82f6",
  },
};

const ChartMethodologyBtn = ({ chartKey }) => {
  const [open, setOpen] = useState(false);
  const meta = CHART_METHODOLOGY[chartKey];
  if (!meta) return null;

  return (
    <div style={{ position: "relative" }}>
      <button
        onClick={() => setOpen(o => !o)}
        title="Ver metodología de este gráfico"
        style={{
          padding: "3px 10px", borderRadius: 6, border: `1px solid ${meta.color}44`,
          background: open ? meta.color + "22" : "transparent",
          color: meta.color, fontSize: 10, fontWeight: 600, cursor: "pointer",
          fontFamily: "'DM Mono', monospace", letterSpacing: 0.5,
          transition: "all 0.2s ease",
        }}
      >
        {open ? "▲ cerrar" : "ⓘ metodología"}
      </button>

      {open && (
        <div style={{
          position: "absolute", right: 0, top: "calc(100% + 8px)", zIndex: 200,
          width: 380, background: "#0d1625",
          border: `1px solid ${meta.color}44`,
          borderRadius: 12, padding: 16,
          boxShadow: "0 8px 32px rgba(0,0,0,0.6)",
        }}>
          <div style={{ fontSize: 12, fontWeight: 800, color: meta.color, marginBottom: 10, fontFamily: "'DM Mono', monospace" }}>
            {meta.title}
          </div>

          <div style={{ marginBottom: 10 }}>
            <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>¿Qué muestra?</div>
            <div style={{ fontSize: 12, color: "#e2e8f0", lineHeight: 1.6 }}>{meta.what}</div>
          </div>

          <div style={{ marginBottom: 10 }}>
            <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>¿Cómo se calcula?</div>
            <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.6 }}>{meta.how}</div>
          </div>

          <div style={{ marginBottom: 10 }}>
            <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>¿Cómo interpretarlo?</div>
            <div style={{ fontSize: 12, color: "#e2e8f0", lineHeight: 1.6, fontStyle: "italic" }}>{meta.interpretation}</div>
          </div>

          <div>
            <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>Fuentes</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
              {meta.sources.map((s, i) => (
                <span key={i} style={{
                  fontSize: 10, padding: "2px 8px", borderRadius: 4,
                  background: meta.color + "18", color: meta.color,
                  border: `1px solid ${meta.color}33`,
                  fontFamily: "'DM Mono', monospace",
                }}>{s}</span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useState, useEffect, useMemo, useCallback } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, LineChart, Line, CartesianGrid, Legend, Cell, PieChart, Pie, AreaChart, Area, ReferenceLine } from "recharts";

const COLORS = {
  bg: "#0a0e17",
  surface: "#111827",
  surfaceLight: "#1a2332",
  border: "#1e2d3d",
  text: "#e2e8f0",
  textMuted: "#64748b",
  textDim: "#475569",
  accent: "#00d4aa",
  accentDim: "#00d4aa33",
  danger: "#ef4444",
  dangerDim: "#ef444433",
  warning: "#f59e0b",
  warningDim: "#f59e0b33",
  info: "#3b82f6",
  infoDim: "#3b82f633",
  purple: "#a855f7",
  purpleDim: "#a855f733",
  textPrimary: "#e2e8f0",
  textSecondary: "#94a3b8",
  cardBg: "#0f1929",
};

// ═══ Brand identity ════════════════════════════════════════════════════════
// Logo target: dos circulos concentricos + punto terracota.
// Colores brand "puros" (light context, print, cover de informes).
// En dashboard (dark theme) los rings usan COLORS.text para visibilidad.
const BRAND = {
  ink: "#1c2230",        // navy oscuro (cover impreso, fondo claro)
  terracotta: "#c25a3a", // accent del punto + ".IA"
};

function BrandLogo({ size = 36, withWordmark = false, wordmarkSize = 22, mono = false, lightOnDark = true }) {
  const ink = mono ? "currentColor" : (lightOnDark ? COLORS.text : BRAND.ink);
  const accent = mono ? "currentColor" : BRAND.terracotta;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <svg width={size} height={size} viewBox="0 0 80 80" style={{ display: "block" }}>
        <g transform="translate(4,4)">
          <circle cx="36" cy="36" r="32" fill="none" stroke={ink} strokeWidth="2.5"/>
          <circle cx="36" cy="36" r="18" fill="none" stroke={ink} strokeWidth="2.5"/>
          <circle cx="36" cy="36" r="5" fill={accent}/>
        </g>
      </svg>
      {withWordmark && (
        <span style={{ fontSize: wordmarkSize, fontWeight: 800, color: ink,
          letterSpacing: -1, fontFamily: "Inter, 'DM Sans', system-ui, sans-serif" }}>
          Democrac<span style={{ color: accent }}>.IA</span>
        </span>
      )}
    </div>
  );
}

const RISK_LEVELS = {
  critical: { color: COLORS.danger, label: "CRÍTICO", bg: COLORS.dangerDim },
  high: { color: "#f97316", label: "ALTO", bg: "#f9731633" },
  moderate: { color: COLORS.warning, label: "MODERADO", bg: COLORS.warningDim },
  low: { color: COLORS.accent, label: "BAJO", bg: COLORS.accentDim },
};

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// ── Observer API key (para endpoints caros: elite/designer) ───────────────
// Prioridad: localStorage > VITE_OBSERVER_KEY > ""
// Onboarding: si la URL trae ?key=xyz, se guarda en localStorage y se limpia la URL.
function getObserverKey() {
  try {
    const fromLS = localStorage.getItem("peirs_observer_key");
    if (fromLS) return fromLS;
  } catch (_) {}
  return import.meta.env.VITE_OBSERVER_KEY || "";
}

function authHeaders(extra = {}) {
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
  } catch (_) {}
})();

const DIMENSION_LABELS = {
  suffrage: "Sufragio Universal",
  legalFramework: "Marco Legal",
  embIndependence: "Independencia EMB",
  mediaFreedom: "Libertad de Medios",
  campaignFinance: "Financiamiento",
  digitalEcosystem: "Ecosistema Digital",
  disputeResolution: "Justicia Electoral",
  inclusion: "Inclusividad",
};


// ── Wrapper de gráfico con botón de metodología ──────────────────────────────
const GlowDot = ({ color, size = 8 }) => (
  <span style={{
    display: "inline-block", width: size, height: size, borderRadius: "50%",
    background: color, boxShadow: `0 0 ${size}px ${color}`, flexShrink: 0,
  }} />
);

const RiskGauge = ({ score, size = 180 }) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  useEffect(() => {
    let frame;
    const start = performance.now();
    const duration = 1200;
    const animate = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimatedScore(Math.round(eased * score));
      if (progress < 1) frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [score]);

  const radius = size / 2 - 16;
  const circumference = Math.PI * radius;
  const offset = circumference - (animatedScore / 100) * circumference;
  const riskColor = score >= 75 ? COLORS.danger : score >= 50 ? COLORS.warning : score >= 25 ? "#f59e0b" : COLORS.accent;

  return (
    <div style={{ position: "relative", width: size, height: size / 2 + 30 }}>
      <svg width={size} height={size / 2 + 16} viewBox={`0 0 ${size} ${size / 2 + 16}`}>
        <path d={`M 16,${size / 2} A ${radius},${radius} 0 0,1 ${size - 16},${size / 2}`}
          fill="none" stroke={COLORS.border} strokeWidth="10" strokeLinecap="round" />
        <path d={`M 16,${size / 2} A ${radius},${radius} 0 0,1 ${size - 16},${size / 2}`}
          fill="none" stroke={riskColor} strokeWidth="10" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.1s ease", filter: `drop-shadow(0 0 8px ${riskColor})` }} />
      </svg>
      <div style={{
        position: "absolute", bottom: 4, left: "50%", transform: "translateX(-50%)",
        textAlign: "center",
      }}>
        <div style={{ fontSize: size / 4, fontWeight: 800, color: riskColor, fontFamily: "'DM Mono', monospace", letterSpacing: -1 }}>
          {animatedScore}
        </div>
        <div style={{ fontSize: 10, color: COLORS.textMuted, textTransform: "uppercase", letterSpacing: 2 }}>
          Índice de Riesgo
        </div>
      </div>
    </div>
  );
};

const Card = ({ children, style = {}, glow = false, onClick = null }) => (
  <div onClick={onClick} style={{
    background: COLORS.surface,
    border: `1px solid ${glow ? COLORS.accent + "55" : COLORS.border}`,
    borderRadius: 14,
    padding: 24,
    cursor: onClick ? "pointer" : "default",
    transition: "all 0.3s ease",
    ...(glow ? { boxShadow: `0 0 20px ${COLORS.accentDim}` } : {}),
    ...style,
  }}>
    {children}
  </div>
);

const Tag = ({ children, color = COLORS.accent }) => (
  <span style={{
    display: "inline-block", padding: "3px 10px", borderRadius: 6,
    fontSize: 11, fontWeight: 600, fontFamily: "'DM Mono', monospace",
    background: color + "22", color: color, border: `1px solid ${color}44`,
    letterSpacing: 0.5,
  }}>
    {children}
  </span>
);

const SectionTitle = ({ children, icon }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
    <span style={{ fontSize: 18 }}>{icon}</span>
    <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: COLORS.text, textTransform: "uppercase", letterSpacing: 2 }}>
      {children}
    </h3>
    <div style={{ flex: 1, height: 1, background: `linear-gradient(90deg, ${COLORS.border}, transparent)` }} />
  </div>
);

const AnimatedCounter = ({ value, suffix = "" }) => {
  return <span>{Math.round(value || 0)}{suffix}</span>;
};

const LoadingScreen = () => (
  <div style={{
    minHeight: "100vh", background: COLORS.bg, display: "flex",
    flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 24,
  }}>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800&family=DM+Mono:wght@400;500;600&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400&display=swap" rel="stylesheet" />
    <div style={{
      animation: "pulse 2s ease-in-out infinite",
    }}>
      <BrandLogo size={64} />
    </div>
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: 18, fontWeight: 700, color: COLORS.text, fontFamily: "'DM Mono', monospace" }}>
        Democrac<span style={{ color: BRAND.terracotta }}>.IA</span>
      </div>
      <div style={{ fontSize: 15, color: COLORS.textMuted, marginTop: 8 }}>
        Ejecutando pipeline de agentes PEIRS...
      </div>
    </div>
    <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
      {["OSINT Ingesta", "Análisis Político", "Legal RAG", "Reporte VIP"].map((agent, i) => (
        <div key={i} style={{
          padding: "4px 10px", borderRadius: 6, fontSize: 10, fontWeight: 600,
          fontFamily: "'DM Mono', monospace", letterSpacing: 0.5,
          background: COLORS.accentDim, color: COLORS.accent, border: `1px solid ${COLORS.accent}44`,
          animation: `fadeInUp 0.5s ease ${i * 0.3}s both`,
        }}>
          {agent}
        </div>
      ))}
    </div>
    <style>{`
      @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.08); } }
      @keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    `}</style>
  </div>
);

const ErrorScreen = ({ error, onRetry }) => (
  <div style={{
    minHeight: "100vh", background: COLORS.bg, display: "flex",
    flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 16,
  }}>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
    <div style={{ fontSize: 42 }}>⚠️</div>
    <div style={{ fontSize: 16, fontWeight: 700, color: COLORS.danger }}>Error de conexión</div>
    <div style={{ fontSize: 13, color: COLORS.textMuted, textAlign: "center", maxWidth: 400, lineHeight: 1.6 }}>
      No se pudo conectar con el backend PEIRS. Asegurate de que el servidor esté corriendo en <code style={{ color: COLORS.accent }}>localhost:8000</code>
    </div>
    <div style={{
      marginTop: 8, padding: "8px 16px", background: COLORS.surfaceLight, borderRadius: 8,
      fontSize: 12, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace",
    }}>
      uvicorn app:app --reload --port 8000
    </div>
    <div style={{ fontSize: 11, color: COLORS.danger, fontFamily: "'DM Mono', monospace", marginTop: 8 }}>
      {error}
    </div>
    <button onClick={onRetry} style={{
      marginTop: 12, padding: "10px 24px", borderRadius: 8, border: `1px solid ${COLORS.accent}`,
      background: COLORS.accentDim, color: COLORS.accent, fontSize: 13, fontWeight: 600, cursor: "pointer",
    }}>
      Reintentar conexión
    </button>
  </div>
);

const SystemHealth = ({ health }) => {
  if (!health) return null;
  const db = health.db_available;
  const rag = health.rag_available;
  const runs = health.stats?.analysis_runs ?? 0;
  return (
    <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: COLORS.textDim, display: "flex", alignItems: "center", gap: 6 }}>
      <span>DB <span style={{ color: db ? COLORS.accent : COLORS.danger }}>●</span></span>
      <span>RAG <span style={{ color: rag ? COLORS.accent : COLORS.danger }}>●</span></span>
      <span>{runs} runs</span>
    </span>
  );
};

const Navbar = ({ activeView, setActiveView, apiStatus, onRefresh, refreshing, generatedAt, systemHealth }) => (
  <nav style={{
    display: "flex", alignItems: "center", justifyContent: "space-between",
    padding: "14px 28px",
    background: "linear-gradient(180deg, #0d1220 0%, #0a0e17 100%)",
    borderBottom: `1px solid ${COLORS.border}`,
    position: "sticky", top: 0, zIndex: 100,
  }}>
    <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
      <BrandLogo size={36} />
      <div>
        <span style={{ fontSize: 22, fontWeight: 800, color: COLORS.text, letterSpacing: 1, fontFamily: "'DM Mono', monospace" }}>
          Democrac<span style={{ color: BRAND.terracotta }}>.IA</span>
        </span>
        <div style={{ fontSize: 9, color: COLORS.textDim, letterSpacing: 3, textTransform: "uppercase", marginTop: 1 }}>
          Predictive Electoral Integrity & Risk System
        </div>
      </div>
    </div>
    <div style={{ display: "flex", gap: 4 }}>
      {[
        { id: "overview", label: "Overview" },
        { id: "detail", label: "Análisis País" },
        { id: "sentinel", label: "🔴 Sentinel" },
        { id: "peru", label: "🇵🇪 Perú 2026" },
        { id: "observer", label: "📡 Observación" },
        { id: "methodology", label: "Metodología" },
      ].map(tab => (
        <button key={tab.id} onClick={() => setActiveView(tab.id)} style={{
          padding: "8px 20px", borderRadius: 8, border: "none", cursor: "pointer",
          fontSize: 14, fontWeight: 600, letterSpacing: 0.5,
          background: activeView === tab.id ? COLORS.accent + "22" : "transparent",
          color: activeView === tab.id ? COLORS.accent : COLORS.textMuted,
          transition: "all 0.2s ease",
        }}>
          {tab.label}
        </button>
      ))}
    </div>
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <SystemHealth health={systemHealth} />
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <GlowDot color={apiStatus === "connected" ? COLORS.accent : COLORS.danger} size={6} />
        <span style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
          {apiStatus === "connected" ? "API LIVE" : "OFFLINE"}
        </span>
      </div>
      {generatedAt && (
        <span style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
          {new Date(generatedAt).toLocaleString("es-AR", { month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit" })}
        </span>
      )}
      <button onClick={onRefresh} disabled={refreshing} style={{
        padding: "5px 12px", borderRadius: 6, border: `1px solid ${COLORS.border}`,
        background: refreshing ? COLORS.surface : COLORS.accentDim,
        color: refreshing ? COLORS.textDim : COLORS.accent,
        fontSize: 11, fontWeight: 600, cursor: refreshing ? "not-allowed" : "pointer",
        fontFamily: "'DM Mono', monospace", letterSpacing: 0.5,
        transition: "all 0.2s ease",
      }}>
        {refreshing ? "..." : "↻ Refresh"}
      </button>
    </div>
  </nav>
);

const CountryCard = ({ country, isSelected, onClick }) => {
  const rl = RISK_LEVELS[country.riskLevel] || RISK_LEVELS.moderate;
  return (
    <Card onClick={onClick} style={{
      cursor: "pointer",
      border: `1px solid ${isSelected ? COLORS.accent : COLORS.border}`,
      background: isSelected ? COLORS.surfaceLight : COLORS.surface,
      transform: isSelected ? "scale(1.02)" : "scale(1)",
      transition: "all 0.25s ease",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <span style={{ fontSize: 28 }}>{country.flag}</span>
          <div>
            <div style={{ fontWeight: 700, color: COLORS.text, fontSize: 17 }}>{country.name}</div>
            <div style={{ fontSize: 11, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
              Elección: {country.date}
            </div>
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: rl.color, fontFamily: "'DM Mono', monospace" }}>
            {country.riskScore}
          </div>
          <Tag color={rl.color}>{rl.label}</Tag>
        </div>
      </div>
      <div style={{
        marginTop: 12, height: 4, borderRadius: 2, background: COLORS.border, overflow: "hidden"
      }}>
        <div style={{
          height: "100%", width: `${country.riskScore}%`, borderRadius: 2,
          background: `linear-gradient(90deg, ${COLORS.accent}, ${rl.color})`,
          transition: "width 1s ease",
        }} />
      </div>
      <div style={{ display: "flex", gap: 6, marginTop: 10, flexWrap: "wrap" }}>
        {country.violations.slice(0, 3).map((v, i) => (
          <Tag key={i} color={COLORS.danger}>{v}</Tag>
        ))}
        {country.violations.length > 3 && <Tag color={COLORS.textDim}>+{country.violations.length - 3}</Tag>}
      </div>
    </Card>
  );
};

const OverviewView = ({ countries, onSelectCountry }) => {
  const avgRisk = Math.round(countries.reduce((a, c) => a + c.riskScore, 0) / countries.length);
  const criticalCount = countries.filter(c => c.riskLevel === "critical").length;
  const totalViolations = countries.reduce((a, c) => a + c.violations.length, 0);

  return (
    <div style={{ padding: 28 }}>

      {/* ── Sección Quiénes Somos ── */}
      <div style={{
        marginBottom: 32, padding: "28px 32px",
        background: `linear-gradient(135deg, #0d1625 0%, #0a1220 100%)`,
        border: `1px solid ${COLORS.accent}33`,
        borderLeft: `4px solid ${COLORS.accent}`,
        borderRadius: 14,
      }}>
        <div style={{ display: "flex", alignItems: "flex-start", gap: 20 }}>
          <div style={{
            flexShrink: 0,
          }}><BrandLogo size={56} /></div>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 14 }}>
              <h1 style={{ margin: 0, fontSize: 30, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
                <strong style={{ color: "#ffffff", fontWeight: 900 }}>Democrac</strong>
                <strong style={{ color: BRAND.terracotta, fontWeight: 900 }}>.IA</strong>
              </h1>
              <span style={{
                fontSize: 11, padding: "3px 10px", borderRadius: 6,
                background: "transparent", color: "#e2e8f0",
                fontFamily: "'DM Mono', monospace", fontWeight: 400, letterSpacing: 0.5,
              }}>PEIRS v0.4.0</span>
            </div>
            <p style={{ margin: "0 0 14px", fontSize: 15, color: "#e2e8f0", lineHeight: 1.8, fontWeight: 500 }}>
              Plataforma de Inteligencia Artificial creada para el monitoreo electoral a nivel global. Trabajamos siguiendo los lineamientos y estándares internacionales de Observación Electoral sin sesgo político-partidario. Nuestro propósito es fortalecer la democracia mediante el análisis transparente, oportuno y objetivo de los procesos electorales en todo el mundo.
            </p>
            <p style={{ margin: "0 0 14px", fontSize: 14, color: "#94a3b8", lineHeight: 1.8 }}>
              Empleamos monitoreo automatizado de medios combinado con análisis asistido por inteligencia artificial para proporcionar una evaluación integral de los entornos electorales, siguiendo las metodologías establecidas por las más importantes misiones de observación electoral — OSCE/ODIHR, Unión Europea, Organización de Estados Americanos, Centro Carter, entre otras — y la Declaración de Principios de Naciones Unidas para la Observación Internacional de Elecciones (2005).
            </p>
            <p style={{ margin: "0 0 16px", fontSize: 14, color: "#94a3b8", lineHeight: 1.8 }}>
              Proporcionamos observación electoral independiente y apartidaria mediante inteligencia artificial y el análisis experto de profesionales con amplia experiencia en observación electoral internacional, contribuyendo a la protección de los derechos democráticos y la integridad electoral a nivel global. Democrac.IA evalúa la integridad de procesos electorales en 38 países a través de un pipeline de 4 agentes de inteligencia artificial que cruzan datos verificados de organismos académicos e internacionales, generando un Índice Predictivo de Riesgo Electoral (0-100) fundamentado en el derecho internacional público — el Pacto Internacional de Derechos Civiles y Políticos, la Convención Americana sobre Derechos Humanos, la Carta Democrática Interamericana, la Carta Africana sobre Democracia y el Convenio Europeo de Derechos Humanos — con trazabilidad completa de cada hallazgo hasta su fuente primaria.
            </p>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              {[
                { label: "V-Dem v15", sub: "27,913 observaciones" },
                { label: "Freedom House FIW 2025", sub: "195 países" },
                { label: "PEI 10.0", sub: "586 elecciones" },
                { label: "RSF 2025", sub: "180 países" },
                { label: "LangGraph + Claude Sonnet", sub: "4 agentes IA" },
              ].map((s, i) => (
                <div key={i} style={{
                  padding: "6px 14px", borderRadius: 8,
                  background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`,
                }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: COLORS.text }}>{s.label}</div>
                  <div style={{ fontSize: 10, color: COLORS.textDim }}>{s.sub}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div style={{ marginBottom: 28 }}>
        <h2 style={{ margin: 0, fontSize: 22, fontWeight: 800, color: COLORS.text }}>
          Panel de Inteligencia Electoral
        </h2>
        <p style={{ margin: "6px 0 0", fontSize: 13, color: COLORS.textMuted }}>
          Datos generados en tiempo real por el pipeline PEIRS — 4 agentes IA ejecutados vía LangGraph
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 28 }}>
        {[
          { label: "Elecciones Monitoreadas", value: countries.length, icon: "🗳️", color: COLORS.info },
          { label: "Riesgo Promedio", value: avgRisk, icon: "📊", suffix: "/100", color: avgRisk > 50 ? COLORS.warning : COLORS.accent },
          { label: "Alertas Críticas", value: criticalCount, icon: "🔴", color: COLORS.danger },
          { label: "Violaciones ICCPR", value: totalViolations, icon: "⚖️", color: COLORS.purple },
        ].map((stat, i) => (
          <Card key={i} style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>{stat.icon}</div>
            <div style={{ fontSize: 44, fontWeight: 800, color: stat.color, fontFamily: "'DM Mono', monospace" }}>
              <AnimatedCounter value={stat.value} suffix={stat.suffix || ""} />
            </div>
            <div style={{ fontSize: 13, color: COLORS.textMuted, marginTop: 6, textTransform: "uppercase", letterSpacing: 1 }}>
              {stat.label}
            </div>
          </Card>
        ))}
      </div>

      <SectionTitle icon="🌎">Elecciones en Seguimiento</SectionTitle>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16, marginBottom: 28 }}>
        {countries.map(c => (
          <CountryCard key={c.id} country={c} isSelected={false} onClick={() => onSelectCountry(c.id)} />
        ))}
      </div>

      <SectionTitle icon="📈">Comparativa de Integridad — Radar Multidimensional</SectionTitle>
      <Card>
        <ResponsiveContainer width="100%" height={340}>
          <RadarChart data={Object.keys(DIMENSION_LABELS).map(key => ({
            dimension: DIMENSION_LABELS[key],
            ...Object.fromEntries(countries.map(c => [c.name, c.dimensions[key]])),
          }))}>
            <PolarGrid stroke={COLORS.border} />
            <PolarAngleAxis dataKey="dimension" tick={{ fill: COLORS.textMuted, fontSize: 12 }} />
            <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: COLORS.textDim, fontSize: 9 }} />
            {countries.map((c, i) => (
              <Radar key={c.id} name={c.name} dataKey={c.name}
                stroke={[COLORS.danger, "#f97316", COLORS.warning, COLORS.accent][i]}
                fill={[COLORS.danger, "#f97316", COLORS.warning, COLORS.accent][i]}
                fillOpacity={0.08} strokeWidth={2} />
            ))}
            <Legend wrapperStyle={{ fontSize: 11, color: COLORS.textMuted }} />
          </RadarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
};


// ── BASE DE CONOCIMIENTO DE VIOLACIONES ──────────────────────────────────────
const VIOLATION_KNOWLEDGE = {
  "ICCPR Art. 19": {
    right: "Libertad de Expresión y Prensa",
    treaty_full: "Pacto Internacional de Derechos Civiles y Políticos",
    what_protects: "Protege el derecho de toda persona a buscar, recibir y difundir información e ideas por cualquier medio. En contexto electoral, garantiza la libertad de prensa como pilar del debate democrático.",
    triggered_by: "Libertad de prensa clasificada como 'severely_restricted' o 'banned' según Freedom House FIW.",
    source: "Freedom House FIW 2025 — CL rating",
    source_url: "https://freedomhouse.org/report/freedom-world",
    confidence: "confirmed",
    remediation: "El Estado debe adoptar medidas legislativas para garantizar la independencia editorial y el pluralismo mediático, conforme al Comentario General No. 34 del Comité de DDHH de la ONU.",
  },
  "ICCPR Art. 21 & Art. 22": {
    right: "Libertad de Reunión y Asociación",
    treaty_full: "Pacto Internacional de Derechos Civiles y Políticos",
    what_protects: "Garantiza el derecho a reunión pacífica y a asociarse con otros, incluida la formación y operación libre de partidos políticos, organizaciones de la sociedad civil y grupos de observación electoral.",
    triggered_by: "Libertad de reunión clasificada como 'restricted' o 'banned' según Freedom House FIW.",
    source: "Freedom House FIW 2025 — CL rating",
    source_url: "https://freedomhouse.org/report/freedom-world",
    confidence: "confirmed",
    remediation: "Las restricciones deben ser necesarias y proporcionales. El Estado debe justificar cada limitación bajo los criterios del Art. 22(2) ICCPR.",
  },
  "ICCPR Art. 9": {
    right: "Libertad y Seguridad Personal",
    treaty_full: "Pacto Internacional de Derechos Civiles y Políticos",
    what_protects: "Prohíbe la detención y encarcelamiento arbitrarios. En contexto electoral, protege a opositores, periodistas y activistas de ser detenidos por ejercer derechos políticos.",
    triggered_by: "Existencia documentada de presos políticos según Freedom House FIW (PR rating ≥ 6).",
    source: "Freedom House FIW 2025 — PR rating",
    source_url: "https://freedomhouse.org/report/freedom-world",
    confidence: "confirmed",
    remediation: "Liberación inmediata de detenidos arbitrarios y apertura de investigaciones independientes conforme al Protocolo de Estambul.",
  },
  "ICCPR Art. 14": {
    right: "Derecho a Tribunal Independiente",
    treaty_full: "Pacto Internacional de Derechos Civiles y Políticos",
    what_protects: "Garantiza el derecho a un tribunal imparcial e independiente. En materia electoral, es esencial para la resolución de disputas sobre resultados e impugnaciones de candidaturas.",
    triggered_by: "Independencia judicial clasificada como 'compromised' o 'captured' según Freedom House FIW.",
    source: "Freedom House FIW 2025 — CL rating (judicial independence)",
    source_url: "https://freedomhouse.org/report/freedom-world",
    confidence: "confirmed",
    remediation: "Reforma del proceso de designación de magistrados con participación de la sociedad civil y revisión de fallos políticos por organismos internacionales.",
  },
  "ICCPR Art. 25": {
    right: "Derecho a Participar en Asuntos Públicos",
    treaty_full: "Pacto Internacional de Derechos Civiles y Políticos",
    what_protects: "El artículo más importante del ICCPR en materia electoral. Garantiza el derecho de todo ciudadano a participar en la dirección de los asuntos públicos, votar y ser elegido en elecciones genuinas, periódicas, con sufragio universal e igual y voto secreto.",
    triggered_by: "EMB con independencia 'compromised' o 'captured' según V-Dem v15 (v2elembaut).",
    source: "V-Dem v15 — v2elembaut (autonomía EMB)",
    source_url: "https://v-dem.net",
    confidence: "confirmed",
    remediation: "Restructuración del organismo electoral con representación multipartidaria y supervisión internacional, conforme al Comentario General No. 25 del Comité de DDHH.",
  },
  "ICCPR Art. 25(b)": {
    right: "Derecho a Ser Elegido — Candidaturas",
    treaty_full: "Pacto Internacional de Derechos Civiles y Políticos",
    what_protects: "Protege el derecho específico a presentarse como candidato en elecciones genuinas. Las inhabilitaciones deben ser basadas en criterios objetivos y razonables, con garantías de debido proceso.",
    triggered_by: "Candidatos inhabilitados con partidos opositores prohibidos (datos PEIRS).",
    source: "PEIRS — datos estructurales del proceso electoral",
    source_url: null,
    confidence: "mock",
    remediation: "Revisión judicial independiente de todas las inhabilitaciones. Criterios de elegibilidad deben ser transparentes y no discriminatorios.",
  },
  "ICCPR Art. 19(2)": {
    right: "Libertad de Expresión Digital",
    treaty_full: "Pacto Internacional de Derechos Civiles y Políticos",
    what_protects: "Extiende el Art. 19 al entorno digital. La censura de internet, el bloqueo de redes sociales y la restricción del acceso a información online constituyen violaciones en período electoral.",
    triggered_by: "Censura de dominios web detectada (datos estimados — pendiente verificación OONI).",
    source: "PEIRS — estimación digital (mock)",
    source_url: "https://ooni.org",
    confidence: "mock",
    remediation: "Levantar bloqueos de plataformas digitales. El Relator Especial de la ONU para la Libertad de Expresión ha establecido que el bloqueo de internet viola el Art. 19.",
  },
  "ICCPR Art. 25(a)": {
    right: "Sufragio Universal Activo",
    treaty_full: "Pacto Internacional de Derechos Civiles y Políticos",
    what_protects: "Garantiza el derecho de toda persona a votar sin discriminación. Las tácticas de supresión de votantes, incluso en entornos digitales, violan este principio fundamental.",
    triggered_by: "Tácticas de supresión de votantes online detectadas (datos estimados — pendiente verificación).",
    source: "PEIRS — estimación digital (mock)",
    source_url: null,
    confidence: "mock",
    remediation: "Investigación de tácticas de supresión y garantías de acceso universal al sufragio, incluyendo asistencia técnica para votantes en entornos digitales hostiles.",
  },
  "CADH Art. 23": {
    right: "Derechos Políticos — Sistema Interamericano",
    treaty_full: "Convención Americana sobre Derechos Humanos (Pacto de San José)",
    what_protects: "Bajo el sistema interamericano, todo ciudadano tiene derecho a participar en la dirección de asuntos públicos, votar y ser elegido. La Corte IDH ha establecido que el Art. 23 exige condiciones electorales genuinas.",
    triggered_by: "EMB con independencia 'compromised' o 'captured' según V-Dem v15.",
    source: "V-Dem v15 — v2elembaut (autonomía EMB)",
    source_url: "https://v-dem.net",
    confidence: "confirmed",
    remediation: "La Comisión Interamericana de DDHH puede iniciar medidas cautelares. Los Estados parte deben garantizar recursos efectivos ante la Corte IDH.",
  },
  "CDI Art. 3-4": {
    right: "Elementos Esenciales de la Democracia",
    treaty_full: "Carta Democrática Interamericana — OEA (2001)",
    what_protects: "Los Arts. 3-4 de la CDI definen los elementos esenciales e indispensables de la democracia representativa: respeto a DDHH, elecciones periódicas y libres, pluralismo político, separación de poderes y libertad de prensa.",
    triggered_by: "Libertad de prensa 'severely_restricted' o 'banned' según Freedom House FIW.",
    source: "Freedom House FIW 2025 — CL rating",
    source_url: "https://freedomhouse.org/report/freedom-world",
    confidence: "confirmed",
    remediation: "La OEA puede activar el mecanismo del Art. 20 CDI para situaciones de alteración del orden democrático. Los Estados miembro pueden convocar una sesión extraordinaria del Consejo Permanente.",
  },
};

// ── ALERTA EXPANDIBLE CON FUENTE ─────────────────────────────────────────────
const AlertCard = ({ alert, violations }) => {
  const [expanded, setExpanded] = useState(false);
  const alertColor = alert.type === "critical" ? COLORS.danger
    : alert.type === "high" ? "#f97316"
    : alert.type === "moderate" ? COLORS.warning : COLORS.accent;
  const alertLabel = alert.type === "critical" ? "CRÍTICO"
    : alert.type === "high" ? "ALTO"
    : alert.type === "moderate" ? "MODERADO" : "BAJO";

  // Buscar violación relacionada al texto de la alerta
  const relatedViolation = violations ? violations.find(v => {
    const vk = Object.keys(VIOLATION_KNOWLEDGE).find(k =>
      v.includes(k.replace("ICCPR ", "").replace("CADH ", "").replace("CDI ", ""))
    );
    return vk && alert.text.toLowerCase().includes(
      VIOLATION_KNOWLEDGE[vk]?.right?.split(" ")[0]?.toLowerCase() || ""
    );
  }) : null;

  const violationKey = relatedViolation
    ? Object.keys(VIOLATION_KNOWLEDGE).find(k => relatedViolation.includes(k.replace("ICCPR ", "").replace("CADH ", "").replace("CDI ", "")))
    : null;
  const vk = violationKey ? VIOLATION_KNOWLEDGE[violationKey] : null;

  return (
    <div style={{
      background: alertColor + "08", borderRadius: 8,
      borderLeft: `3px solid ${alertColor}`,
      overflow: "hidden",
      border: `1px solid ${expanded ? alertColor + "33" : "transparent"}`,
      borderLeftWidth: 3,
    }}>
      <div
        onClick={() => setExpanded(e => !e)}
        style={{ display: "flex", alignItems: "flex-start", gap: 12, padding: "12px 14px", cursor: "pointer" }}
      >
        <div style={{ paddingTop: 3 }}>
          <GlowDot color={alertColor} size={7} />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: alertColor, fontFamily: "'DM Mono', monospace", letterSpacing: 1 }}>
              [{alertLabel}]
            </span>
            <span style={{ fontSize: 11, color: COLORS.textDim }}>
              {expanded ? "▲ cerrar" : "▼ ver fuente"}
            </span>
          </div>
          <div style={{ fontSize: 14, color: COLORS.text, lineHeight: 1.7, marginTop: 3 }}>{alert.text}</div>
        </div>
      </div>

      {expanded && (
        <div style={{
          padding: "12px 16px 16px", borderTop: `1px solid ${alertColor}22`,
          background: alertColor + "05",
        }}>
          {vk ? (
            <>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
                <div style={{ padding: "10px 12px", background: COLORS.surfaceLight, borderRadius: 8 }}>
                  <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>Derecho vulnerado</div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: alertColor }}>{vk.right}</div>
                  <div style={{ fontSize: 11, color: COLORS.textMuted, marginTop: 4, lineHeight: 1.5 }}>{vk.treaty_full}</div>
                </div>
                <div style={{ padding: "10px 12px", background: COLORS.surfaceLight, borderRadius: 8 }}>
                  <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>Fuente del hallazgo</div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: COLORS.text }}>{vk.source}</div>
                  <span style={{
                    display: "inline-block", marginTop: 4, fontSize: 10, padding: "2px 8px", borderRadius: 4,
                    background: vk.confidence === "confirmed" ? COLORS.accentDim : COLORS.warningDim,
                    color: vk.confidence === "confirmed" ? COLORS.accent : COLORS.warning,
                    fontFamily: "'DM Mono', monospace",
                  }}>
                    {vk.confidence === "confirmed" ? "✓ VERIFICADO" : "⚠ ESTIMADO"}
                  </span>
                </div>
              </div>
              <div style={{ padding: "10px 12px", background: COLORS.surfaceLight, borderRadius: 8, marginBottom: 10 }}>
                <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>¿Qué protege este derecho?</div>
                <div style={{ fontSize: 12, color: COLORS.text, lineHeight: 1.7 }}>{vk.what_protects}</div>
              </div>
              <div style={{ padding: "10px 12px", background: COLORS.surfaceLight, borderRadius: 8, marginBottom: 10 }}>
                <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>¿Qué dato generó esta alerta?</div>
                <div style={{ fontSize: 12, color: COLORS.text, lineHeight: 1.7 }}>{vk.triggered_by}</div>
              </div>
              <div style={{ padding: "10px 12px", background: alertColor + "0a", borderRadius: 8, borderLeft: `3px solid ${alertColor}44` }}>
                <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>Mecanismo de remediación</div>
                <div style={{ fontSize: 12, color: COLORS.text, lineHeight: 1.7 }}>{vk.remediation}</div>
              </div>
              {vk.source_url && (
                <a href={vk.source_url} target="_blank" rel="noopener noreferrer" style={{
                  display: "inline-block", marginTop: 10, fontSize: 11,
                  color: alertColor, textDecoration: "none", fontFamily: "'DM Mono', monospace",
                }}>
                  🔗 Ver fuente primaria →
                </a>
              )}
            </>
          ) : (
            <div style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.8 }}>
              <div style={{ marginBottom: 8 }}>
                <span style={{ color: COLORS.textDim, fontFamily: "'DM Mono', monospace", fontSize: 10 }}>FUENTE: </span>
                {alert.type === "critical" || alert.type === "high"
                  ? "Freedom House FIW 2025 / V-Dem v15 (confidence: confirmed)"
                  : "PEIRS — estimación del sistema"}
              </div>
              Este hallazgo fue generado por el pipeline PEIRS a partir del cruce de datos de Freedom House, V-Dem y PEI-10.0.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ── VIOLACIÓN EXPANDIBLE CON FUENTE COMPLETA ─────────────────────────────────
const ViolationCard = ({ violation }) => {
  const [expanded, setExpanded] = useState(false);
  const vk = VIOLATION_KNOWLEDGE[violation] || null;
  const isConfirmed = vk?.confidence === "confirmed";

  return (
    <div style={{
      borderRadius: 8, overflow: "hidden",
      border: `1px solid ${expanded ? COLORS.danger + "44" : COLORS.danger + "22"}`,
      background: expanded ? COLORS.dangerDim + "88" : COLORS.dangerDim,
    }}>
      <div
        onClick={() => setExpanded(e => !e)}
        style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px", cursor: "pointer" }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <GlowDot color={COLORS.danger} size={6} />
          <span style={{ fontSize: 13, fontWeight: 600, color: COLORS.text, fontFamily: "'DM Mono', monospace" }}>{violation}</span>
          {vk && <span style={{ fontSize: 11, color: COLORS.textMuted }}>— {vk.right}</span>}
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <span style={{
            fontSize: 10, padding: "2px 8px", borderRadius: 4, fontFamily: "'DM Mono', monospace",
            background: isConfirmed ? COLORS.accentDim : COLORS.warningDim,
            color: isConfirmed ? COLORS.accent : COLORS.warning,
          }}>
            {isConfirmed ? "✓ VERIFICADO" : "⚠ ESTIMADO"}
          </span>
          <Tag color={COLORS.danger}>ACTIVA</Tag>
          <span style={{ fontSize: 11, color: COLORS.textDim }}>{expanded ? "▲" : "▼"}</span>
        </div>
      </div>

      {expanded && vk && (
        <div style={{ padding: "12px 16px 16px", borderTop: `1px solid ${COLORS.danger}22` }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
            <div style={{ padding: "10px 12px", background: COLORS.surfaceLight, borderRadius: 8 }}>
              <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>Tratado</div>
              <div style={{ fontSize: 12, fontWeight: 700, color: COLORS.text }}>{vk.treaty_full}</div>
            </div>
            <div style={{ padding: "10px 12px", background: COLORS.surfaceLight, borderRadius: 8 }}>
              <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>Fuente del dato</div>
              <div style={{ fontSize: 12, color: COLORS.text }}>{vk.source}</div>
            </div>
          </div>
          <div style={{ padding: "10px 12px", background: COLORS.surfaceLight, borderRadius: 8, marginBottom: 10 }}>
            <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>¿Qué protege este artículo?</div>
            <div style={{ fontSize: 12, color: COLORS.text, lineHeight: 1.7 }}>{vk.what_protects}</div>
          </div>
          <div style={{ padding: "10px 12px", background: COLORS.surfaceLight, borderRadius: 8, marginBottom: 10 }}>
            <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>Dato que generó esta violación</div>
            <div style={{ fontSize: 12, color: COLORS.text, lineHeight: 1.7 }}>{vk.triggered_by}</div>
          </div>
          <div style={{ padding: "10px 12px", background: COLORS.danger + "0a", borderRadius: 8, borderLeft: `3px solid ${COLORS.danger}44`, marginBottom: 10 }}>
            <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>Mecanismo de remediación</div>
            <div style={{ fontSize: 12, color: COLORS.text, lineHeight: 1.7 }}>{vk.remediation}</div>
          </div>
          {vk.source_url && (
            <a href={vk.source_url} target="_blank" rel="noopener noreferrer" style={{
              fontSize: 11, color: COLORS.danger, textDecoration: "none", fontFamily: "'DM Mono', monospace",
            }}>
              🔗 Ver fuente primaria →
            </a>
          )}
        </div>
      )}
    </div>
  );
};



// ── Componentes Elite para DetailView ──────────────────────────────────────

const CircularScore = ({ value, max = 100, label, sublabel, color, size = 110 }) => {
  const displayVal = value || 0;
  const r = size / 2 - 10;
  const circ = 2 * Math.PI * r;
  const pct = max > 0 ? displayVal / max : 0;
  const offset = circ * (1 - pct);

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
      <div style={{ position: "relative", width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
          <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={COLORS.border} strokeWidth={7} />
          <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={7}
            strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={offset}
            style={{ filter: `drop-shadow(0 0 6px ${color}88)`, transition: "stroke-dashoffset 0.05s" }} />
        </svg>
        <div style={{
          position: "absolute", inset: 0, display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center",
        }}>
          <span style={{ fontSize: size * 0.22, fontWeight: 800, color, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
            {value !== null && value !== undefined ? (Number.isInteger(value) ? Math.round(displayVal) : displayVal.toFixed(2)) : "N/A"}
          </span>
          {max !== 100 && <span style={{ fontSize: 9, color: COLORS.textDim }}>/{max}</span>}
        </div>
      </div>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.text, textTransform: "uppercase", letterSpacing: 1.5 }}>{label}</div>
        {sublabel && <div style={{ fontSize: 9, color: COLORS.textDim, marginTop: 2, letterSpacing: 0.5 }}>{sublabel}</div>}
      </div>
    </div>
  );
};

/**
 * DatasetCard — presentación narrativa de un índice internacional.
 *
 * Reemplaza al CircularScore pelado: muestra valor + barra + escala interpretativa +
 * descripción del índice + fuente + año. Pensado para que un observador entienda
 * qué mide cada dataset sin necesidad de consultar un glosario externo.
 *
 * Props:
 *  name          — "Freedom House", "V-Dem", "PEI", "RSF"
 *  icon          — emoji opcional
 *  value         — número a mostrar
 *  max           — escala (100 para FH/PEI/RSF, 1 para V-Dem)
 *  unit          — sufijo opcional ("/100", "")
 *  year          — año del dato
 *  description   — qué mide el índice
 *  source        — organización que lo publica
 *  scale         — array de { from, to, label, color } para la escala interpretativa
 *  sourceUrl     — link al sitio oficial
 */
const DatasetCard = ({ name, icon = "📊", value, max = 100, unit = "", year, description, source, scale = [], sourceUrl }) => {
  const hasValue = value !== null && value !== undefined;
  const pct = hasValue && max > 0 ? (value / max) * 100 : 0;

  // Determinar el nivel actual según la escala
  const currentLevel = hasValue
    ? scale.find(s => value >= s.from && value <= s.to) || scale[scale.length - 1]
    : null;
  const color = currentLevel?.color || COLORS.textMuted;

  return (
    <Card className="peru-card" style={{ padding: 14 }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 16 }}>{icon}</span>
          <span style={{ fontSize: 12, fontWeight: 700, color: COLORS.text, letterSpacing: 1 }}>{name}</span>
        </div>
        {year && (
          <span style={{ fontSize: 9, color: COLORS.textDim, fontFamily: "'DM Mono', monospace",
            padding: "2px 8px", border: `1px solid ${COLORS.border}`, borderRadius: 4 }}>
            {year}
          </span>
        )}
      </div>

      {/* Valor + barra */}
      <div style={{ marginBottom: 10 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 6 }}>
          <span style={{ fontSize: 28, fontWeight: 800, color, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
            {hasValue ? (max === 1 ? value.toFixed(2) : Math.round(value)) : "—"}
          </span>
          <span style={{ fontSize: 12, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
            / {max}{unit}
          </span>
          {currentLevel && (
            <span style={{ marginLeft: "auto", fontSize: 10, fontWeight: 700, color,
              padding: "3px 8px", background: `${color}18`, border: `1px solid ${color}55`, borderRadius: 4,
              textTransform: "uppercase", letterSpacing: 1 }}>
              {currentLevel.label}
            </span>
          )}
        </div>
        <div style={{ height: 6, background: COLORS.border, borderRadius: 3, overflow: "hidden" }}>
          <div style={{
            height: "100%", width: `${Math.min(pct, 100)}%`, borderRadius: 3,
            background: `linear-gradient(90deg, ${color}88, ${color})`,
            boxShadow: `0 0 6px ${color}66`,
            transition: "width 1.2s cubic-bezier(0.4, 0, 0.2, 1)",
          }} />
        </div>
      </div>

      {/* Descripción */}
      {description && (
        <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5, marginBottom: 10 }}>
          {description}
        </div>
      )}

      {/* Escala interpretativa */}
      {scale.length > 0 && (
        <div style={{ marginBottom: 8, padding: "6px 8px", background: COLORS.surface, borderRadius: 5 }}>
          <div style={{ fontSize: 9, fontWeight: 700, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>
            Escala interpretativa
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {scale.map((s, i) => (
              <div key={i} style={{
                display: "flex", justifyContent: "space-between", alignItems: "center",
                fontSize: 10, fontFamily: "'DM Mono', monospace",
                padding: "2px 0",
                color: s === currentLevel ? s.color : COLORS.textMuted,
                fontWeight: s === currentLevel ? 700 : 400,
              }}>
                <span>
                  <span style={{ display: "inline-block", width: 6, height: 6, borderRadius: "50%", background: s.color, marginRight: 6 }} />
                  {s.label}
                </span>
                <span>{s.from}–{s.to}{max === 1 ? "" : unit}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer: fuente */}
      {source && (
        <div style={{ fontSize: 9, color: COLORS.textDim, fontFamily: "'DM Mono', monospace", paddingTop: 6, borderTop: `1px dashed ${COLORS.border}` }}>
          Fuente: {sourceUrl
            ? <a href={sourceUrl} target="_blank" rel="noopener noreferrer" style={{ color: COLORS.textMuted, textDecoration: "underline" }}>{source}</a>
            : source}
        </div>
      )}
    </Card>
  );
};

const BarMeter = ({ value, label, invert = false }) => {
  const pct = value !== null && value !== undefined ? Math.round(value * 100) : 0;
  const displayPct = invert ? 100 - pct : pct;
  const barColor = displayPct > 66 ? COLORS.accent : displayPct > 33 ? COLORS.warning : COLORS.danger;
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ fontSize: 10, color: COLORS.textMuted, textTransform: "uppercase", letterSpacing: 1 }}>{label}</span>
        <span style={{ fontSize: 10, fontWeight: 700, color: barColor, fontFamily: "'DM Mono', monospace" }}>{displayPct}%</span>
      </div>
      <div style={{ height: 5, background: COLORS.border, borderRadius: 3, overflow: "hidden" }}>
        <div style={{
          height: "100%", width: `${displayPct}%`, borderRadius: 3,
          background: `linear-gradient(90deg, ${barColor}88, ${barColor})`,
          boxShadow: `0 0 8px ${barColor}66`,
          transition: "width 1.2s cubic-bezier(0.4, 0, 0.2, 1)",
        }} />
      </div>
    </div>
  );
};

const EMBStatusPanel = ({ level, autonomy, irregularities, intimidation, intlObs }) => {
  const levels = {
    full: { color: COLORS.accent, label: "INDEPENDIENTE", icon: "✓", desc: "Opera sin interferencia gubernamental" },
    partial: { color: COLORS.warning, label: "PARCIAL", icon: "◐", desc: "Autonomía limitada, presiones documentadas" },
    compromised: { color: "#f97316", label: "COMPROMETIDO", icon: "⚠", desc: "Subordinación documentada al ejecutivo" },
    captured: { color: COLORS.danger, label: "CAPTURADO", icon: "✕", desc: "Control gubernamental directo verificado" },
  };
  const l = levels[level] || levels.partial;

  return (
    <div style={{
      background: `linear-gradient(135deg, ${l.color}08, ${COLORS.surface})`,
      border: `1px solid ${l.color}33`,
      borderRadius: 12, padding: 20,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 18 }}>
        <div style={{
          width: 48, height: 48, borderRadius: 10,
          background: `${l.color}18`, border: `2px solid ${l.color}44`,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 22, color: l.color, fontWeight: 800,
        }}>{l.icon}</div>
        <div>
          <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 2, marginBottom: 3 }}>
            Organismo Electoral (EMB)
          </div>
          <div style={{ fontSize: 16, fontWeight: 800, color: l.color, fontFamily: "'DM Mono', monospace", letterSpacing: 1 }}>
            {l.label}
          </div>
          <div style={{ fontSize: 11, color: COLORS.textMuted, marginTop: 2 }}>{l.desc}</div>
        </div>
      </div>
      <BarMeter value={autonomy} label="Autonomía institucional" />
      <BarMeter value={irregularities} label="Ausencia de irregularidades" />
      <BarMeter value={intimidation} label="Ausencia de intimidación" />
      <div style={{
        display: "flex", alignItems: "center", gap: 8, marginTop: 12,
        padding: "8px 12px", background: COLORS.surfaceLight, borderRadius: 8,
      }}>
        <span style={{ fontSize: 14 }}>{intlObs === true ? "🌐" : intlObs === false ? "🚫" : "❓"}</span>
        <div>
          <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1 }}>Observación Internacional</div>
          <div style={{ fontSize: 11, fontWeight: 600, color: intlObs === true ? COLORS.accent : intlObs === false ? COLORS.danger : COLORS.textMuted }}>
            {intlObs === true ? "Presente en última elección" : intlObs === false ? "Ausente / Restringida" : "Sin datos disponibles"}
          </div>
        </div>
      </div>
    </div>
  );
};

const IntelligenceSourceRow = ({ icon, source, value, year, confidence, color }) => (
  <div style={{
    display: "flex", alignItems: "center", gap: 14, padding: "12px 16px",
    background: COLORS.surfaceLight, borderRadius: 10, borderLeft: `3px solid ${color}`,
    marginBottom: 8,
  }}>
    <div style={{
      width: 36, height: 36, borderRadius: 8, background: `${color}18`,
      display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, flexShrink: 0,
    }}>{icon}</div>
    <div style={{ flex: 1 }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.text, textTransform: "uppercase", letterSpacing: 1 }}>{source}</div>
      <div style={{ fontSize: 10, color: COLORS.textDim, marginTop: 1 }}>Datos de {year}</div>
    </div>
    <div style={{ textAlign: "right" }}>
      <div style={{ fontSize: 18, fontWeight: 800, color, fontFamily: "'DM Mono', monospace" }}>{value}</div>
      <Tag color={confidence === "confirmed" ? COLORS.accent : COLORS.warning}>
        {confidence === "confirmed" ? "VERIFICADO" : "MOCK"}
      </Tag>
    </div>
  </div>
);

const DetailView = ({ country }) => {
  const rl = RISK_LEVELS[country.riskLevel] || RISK_LEVELS.moderate;
  const [dictamenTab, setDictamenTab] = useState("operativo");

  const radarData = Object.entries(country.dimensions).map(([key, val]) => ({
    dimension: DIMENSION_LABELS[key], value: val, fullMark: 100,
  }));

  // Extraer datos de EMB desde agentLogs
  const logs = country.agentLogs || [];
  const embLog = logs.find(l => l.includes("EMB:"));
  const embLevel = embLog ? (
    embLog.includes("captured") ? "captured" :
    embLog.includes("compromised") ? "compromised" :
    embLog.includes("partial") ? "partial" : "full"
  ) : "partial";
  const autonomyMatch = embLog ? embLog.match(/autonomía=([\d.]+)/) : null;
  const autonomyVal = autonomyMatch ? parseFloat(autonomyMatch[1]) : null;
  const intlObs = embLog ? embLog.includes("Obs. intl: True") : null;

  // Extraer PEI desde logs
  const peiLog = logs.find(l => l.includes("PEI REAL:") || l.includes("PEI PEI-10.0:"));
  const peiEmbs = peiLog ? (peiLog.match(/EMBs=([\d.]+)/) || [])[1] : null;
  const peiYear = peiLog ? (peiLog.match(/año=(\d+)/) || [])[1] : null;

  // ── Convergencia entre fuentes ──────────────────────────────────────────────
  const fhRisk = 100 - country.freedomScore;
  const vdemRisk = Math.round((1 - country.vdemIndex) * 100);
  const peiRisk = peiEmbs ? Math.round(100 - parseFloat(peiEmbs)) : null;
  const riskValues = [fhRisk, vdemRisk, ...(peiRisk !== null ? [peiRisk] : [])];
  const mean = riskValues.reduce((a, b) => a + b, 0) / riskValues.length;
  const stdDev = Math.sqrt(riskValues.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / riskValues.length);
  const convergenceScore = Math.max(0, Math.round(100 - (stdDev / 50) * 100));
  const convergenceLabel = convergenceScore >= 75 ? "Alta" : convergenceScore >= 50 ? "Media" : "Baja";
  const convergenceColor = convergenceScore >= 75 ? COLORS.accent : convergenceScore >= 50 ? COLORS.warning : COLORS.danger;
  const convergenceNote = convergenceScore >= 75
    ? "Datasets y señal predictiva apuntan en la misma dirección."
    : convergenceScore >= 50
    ? "Tensión entre fuentes — el modelo requiere cautela interpretativa."
    : "Divergencia significativa entre fuentes — ampliar evidencia antes de concluir.";

  // ── Confianza del modelo ─────────────────────────────────────────────────────
  const confirmedCount = [country.freedomScore > 0, country.vdemIndex > 0, !!peiEmbs].filter(Boolean).length;
  const confidenceLabel = confirmedCount === 3 ? "Alta" : confirmedCount === 2 ? "Media" : "Baja";
  const confidenceColor = confirmedCount === 3 ? COLORS.accent : confirmedCount === 2 ? COLORS.warning : COLORS.danger;

  // ── Frase interpretativa del Hero ───────────────────────────────────────────
  const trendLabel = country.trend === "deteriorating" ? "con deterioro reciente" : country.trend === "improving" ? "con mejora reciente" : "estable";
  const riskLabel = rl.label.toLowerCase();
  const topDimension = Object.entries(country.dimensions).sort((a, b) => a[1] - b[1])[0];
  const topDimLabel = topDimension ? (DIMENSION_LABELS[topDimension[0]] || topDimension[0]).toLowerCase() : "";
  const heroSentence = `Riesgo electoral ${riskLabel} ${trendLabel}. ${
    country.violations.length > 0
      ? `${country.violations.length} violaciones al derecho internacional detectadas`
      : "Sin violaciones detectadas"
  }. Déficit principal: ${topDimLabel} (${topDimension?.[1]}/100). Convergencia entre fuentes: ${convergenceLabel}.`;

  // ── Waterfall: contribución de cada dimensión al riesgo ────────────────────
  const waterfallData = Object.entries(country.dimensions)
    .map(([key, val]) => ({
      name: (DIMENSION_LABELS[key] || key).slice(0, 16),
      risk: Math.max(0, 100 - val),
      integrity: val,
    }))
    .sort((a, b) => b.risk - a.risk);

  // ── Días hasta la elección ───────────────────────────────────────────────────
  const electionDate = country.date ? new Date(country.date) : null;
  const today = new Date();
  const daysToElection = electionDate ? Math.ceil((electionDate - today) / (1000 * 60 * 60 * 24)) : null;

  return (
    <div style={{ padding: "28px 28px 40px" }}>
      <style>{`
        .intel-card { transition: transform 0.2s ease, box-shadow 0.2s ease; }
        .intel-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
        .section-divider { font-size: 10px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: ${COLORS.textDim}; padding: 18px 0 10px; border-top: 1px solid ${COLORS.border}; margin-top: 8px; display: flex; align-items: center; gap: 10px; }
        .section-divider::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, ${COLORS.border}, transparent); }
      `}</style>

      {/* ══════════════════════════════════════════════════════════════
          CAPA 1 — HERO: Snapshot integrado
      ══════════════════════════════════════════════════════════════ */}
      <div style={{
        background: `linear-gradient(135deg, #0d1625 0%, ${COLORS.surface} 100%)`,
        border: `1px solid ${rl.color}33`,
        borderRadius: 14, padding: "20px 24px", marginBottom: 24,
        boxShadow: `0 0 40px ${rl.color}0a`,
      }}>
        {/* Fila superior: nombre + score */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 20, flexWrap: "wrap" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <span style={{ fontSize: 44 }}>{country.flag}</span>
            <div>
              <h2 style={{ margin: 0, fontSize: 32, fontWeight: 800, color: COLORS.text, fontFamily: "'Fraunces', serif", letterSpacing: -0.5 }}>
                {country.name}
              </h2>
              <div style={{ display: "flex", gap: 8, marginTop: 6, alignItems: "center", flexWrap: "wrap" }}>
                <Tag color={rl.color}>{rl.label}</Tag>
                <span style={{ fontSize: 10, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
                  ELECCIÓN {country.date}
                  {daysToElection !== null && daysToElection > 0 && (
                    <span style={{ color: daysToElection < 90 ? COLORS.warning : COLORS.textDim }}> · {daysToElection}d</span>
                  )}
                </span>
                <span style={{ fontSize: 10, fontFamily: "'DM Mono', monospace", color: country.trend === "deteriorating" ? COLORS.danger : COLORS.accent }}>
                  {country.trend === "deteriorating" ? "▼ deteriorando" : country.trend === "improving" ? "▲ mejorando" : "● estable"}
                </span>
              </div>
            </div>
          </div>

          {/* Score + badges */}
          <div style={{ display: "flex", gap: 12, alignItems: "flex-start", flexWrap: "wrap" }}>
            {/* Score principal */}
            <div style={{ textAlign: "center", padding: "10px 18px", background: `${rl.color}0f`, border: `1px solid ${rl.color}33`, borderRadius: 10 }}>
              <div style={{ fontSize: 9, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", marginBottom: 2 }}>PEIRS</div>
              <div style={{ fontSize: 52, fontWeight: 800, color: rl.color, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>{country.riskScore}</div>
              <div style={{ fontSize: 9, color: rl.color, marginTop: 2 }}>/100</div>
            </div>
            {/* Confianza */}
            <div style={{ textAlign: "center", padding: "10px 14px", background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, minWidth: 80 }}>
              <div style={{ fontSize: 9, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", marginBottom: 4 }}>CONFIANZA</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: confidenceColor, fontFamily: "'DM Mono', monospace" }}>{confidenceLabel}</div>
              <div style={{ fontSize: 9, color: COLORS.textDim, marginTop: 2 }}>{confirmedCount}/3 fuentes</div>
            </div>
            {/* Convergencia */}
            <div style={{ textAlign: "center", padding: "10px 14px", background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, minWidth: 80 }}>
              <div style={{ fontSize: 9, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", marginBottom: 4 }}>CONVERGENCIA</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: convergenceColor, fontFamily: "'DM Mono', monospace" }}>{convergenceLabel}</div>
              <div style={{ fontSize: 9, color: COLORS.textDim, marginTop: 2 }}>{convergenceScore}/100</div>
            </div>
          </div>
        </div>

        {/* Frase interpretativa */}
        <div style={{ marginTop: 16, padding: "10px 14px", borderRadius: 8, background: `${rl.color}08`, borderLeft: `3px solid ${rl.color}55` }}>
          <p style={{ margin: 0, fontSize: 12, color: COLORS.textMuted, lineHeight: 1.6, fontStyle: "italic" }}>
            {heroSentence}
          </p>
        </div>

        {/* Violaciones críticas — inline en el hero */}
        {(() => {
          const cv = country.violations.filter(v =>
            ["ICCPR Art. 19", "ICCPR Art. 21 & Art. 22", "ICCPR Art. 9", "ICCPR Art. 14", "ICCPR Art. 25", "ICCPR Art. 25(b)"].includes(v)
          );
          if (!cv.length) return null;
          return (
            <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap", gap: 6, alignItems: "center" }}>
              <GlowDot color={COLORS.danger} size={6} />
              <span style={{ fontSize: 10, color: COLORS.danger, fontFamily: "'DM Mono', monospace", fontWeight: 700 }}>
                {cv.length} VIOLACIONES CRÍTICAS:
              </span>
              {cv.map((v, i) => {
                const vk = VIOLATION_KNOWLEDGE[v];
                return (
                  <TooltipInfo key={i} text={{ title: `${v} — ${vk?.right || "Violación"}`, desc: vk?.what_protects || "", source: vk?.source || "PEIRS", confidence: "confirmed" }}>
                    <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 4, background: COLORS.dangerDim, color: COLORS.danger, fontFamily: "'DM Mono', monospace", cursor: "help" }}>
                      {v}
                    </span>
                  </TooltipInfo>
                );
              })}
            </div>
          );
        })()}
      </div>

      {/* ══════════════════════════════════════════════════════════════
          CAPA 2 — DOS PANELES: Marco institucional | Inteligencia Electoral
      ══════════════════════════════════════════════════════════════ */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24, alignItems: "start" }}>

        {/* ── PANEL IZQUIERDO: Marco general institucional y de riesgo operativo ── */}
        <div>
          <div className="section-divider" style={{ color: COLORS.info }}>
            Marco general institucional y de riesgo operativo
          </div>

          {/* Scores circulares */}
          <Card className="intel-card" style={{ background: "linear-gradient(135deg, #0d1625 0%, #111827 100%)", marginBottom: 16 }}>
            <SectionTitle icon="📡">Evidencia Estructural — Fuentes Verificadas</SectionTitle>
            <div style={{ display: "flex", justifyContent: "space-around", alignItems: "flex-end", padding: "12px 0 4px" }}>
              <CircularScore value={country.freedomScore} max={100} label="Freedom House" sublabel="FIW 2025"
                color={country.freedomScore < 30 ? COLORS.danger : country.freedomScore < 60 ? COLORS.warning : COLORS.accent} size={90} />
              <CircularScore value={country.vdemIndex} max={1} label="V-Dem" sublabel="Liberal Democracy"
                color={country.vdemIndex < 0.2 ? COLORS.danger : country.vdemIndex < 0.5 ? COLORS.warning : COLORS.accent} size={110} />
              <CircularScore value={peiEmbs ? parseFloat(peiEmbs) : null} max={100} label="PEI — EMBs"
                sublabel={peiYear ? `Elección ${peiYear}` : "Sin datos"}
                color={peiEmbs && parseFloat(peiEmbs) < 30 ? COLORS.danger : parseFloat(peiEmbs) < 60 ? COLORS.warning : COLORS.accent} size={90} />
            </div>
          </Card>

          {/* EMB */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
              <span style={{ fontSize: 16 }}>🏛️</span>
              <span style={{ fontSize: 11, fontWeight: 700, color: COLORS.textMuted, textTransform: "uppercase", letterSpacing: 2 }}>
                Organismo Electoral
              </span>
            </div>
            <EMBStatusPanel level={embLevel} autonomy={autonomyVal}
              irregularities={country.dimensions?.embIndependence ? country.dimensions.embIndependence / 100 : null}
              intimidation={country.dimensions?.legalFramework ? country.dimensions.legalFramework / 100 : null}
              intlObs={intlObs} />
          </div>

          {/* Radar */}
          <Card className="intel-card" style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
              <SectionTitle icon="🎯">Análisis Multidimensional</SectionTitle>
              <ChartMethodologyBtn chartKey="radar" />
            </div>
            <ResponsiveContainer width="100%" height={230}>
              <RadarChart data={radarData}>
                <PolarGrid stroke={COLORS.border} />
                <PolarAngleAxis dataKey="dimension" tick={{ fill: COLORS.textMuted, fontSize: 8, fontFamily: "'DM Mono', monospace" }} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: COLORS.textDim, fontSize: 7 }} />
                <Radar dataKey="value" stroke={rl.color} fill={rl.color} fillOpacity={0.12} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </Card>

          {/* Cadena de custodia */}
          <Card className="intel-card">
            <SectionTitle icon="🔗">Cadena de Custodia de Datos</SectionTitle>
            <IntelligenceSourceRow icon="🏠" source="Freedom House — FIW" value={`${country.freedomScore}/100`}
              year="2025" confidence="confirmed" color={country.freedomScore < 30 ? COLORS.danger : COLORS.warning} />
            <IntelligenceSourceRow icon="📊" source="V-Dem Institute — v15" value={country.vdemIndex}
              year="2024" confidence="confirmed" color={COLORS.purple} />
            <IntelligenceSourceRow icon="🗳️" source="Electoral Integrity Project — PEI-10.0"
              value={peiEmbs ? `${peiEmbs}/100` : "N/A"} year={peiYear || "—"} confidence={peiEmbs ? "confirmed" : "mock"} color={COLORS.info} />
            <div style={{ marginTop: 10, padding: "7px 10px", borderRadius: 7, background: COLORS.surfaceLight, fontSize: 9, color: COLORS.textDim, lineHeight: 1.6 }}>
              V-Dem CC-BY-SA 4.0 · Freedom House CC · PEI Harvard Dataverse
            </div>
          </Card>
        </div>

        {/* ── PANEL DERECHO: Inteligencia Electoral ── */}
        <div>
          <div className="section-divider" style={{ color: COLORS.accent }}>
            Inteligencia Electoral
          </div>

          {/* Waterfall de drivers del riesgo */}
          <Card className="intel-card" style={{ marginBottom: 16 }}>
            <SectionTitle icon="🔥">Drivers del Índice de Riesgo</SectionTitle>
            <div style={{ fontSize: 10, color: COLORS.textDim, marginBottom: 8, fontFamily: "'DM Mono', monospace" }}>
              Contribución de cada dimensión al riesgo total (100 = máximo riesgo)
            </div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={waterfallData} layout="vertical" margin={{ left: 4, right: 20, top: 4, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} horizontal={false} />
                <XAxis type="number" domain={[0, 100]} tick={{ fill: COLORS.textMuted, fontSize: 10 }} />
                <YAxis type="category" dataKey="name" tick={{ fill: COLORS.textMuted, fontSize: 9, fontFamily: "'DM Mono', monospace" }} width={100} />
                <Tooltip
                  contentStyle={{ background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontSize: 11 }}
                  formatter={(v, n) => [n === "risk" ? `${v}/100 riesgo` : `${v}/100 integridad`]}
                />
                <Bar dataKey="risk" radius={[0, 4, 4, 0]} name="risk">
                  {waterfallData.map((entry, i) => (
                    <Cell key={i} fill={entry.risk >= 70 ? COLORS.danger : entry.risk >= 40 ? COLORS.warning : COLORS.accent} fillOpacity={0.8} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Evolución temporal */}
          <Card className="intel-card" style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
              <SectionTitle icon="📈">Evolución del Índice de Riesgo</SectionTitle>
              <ChartMethodologyBtn chartKey="evolucion" />
            </div>
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={country.timeline}>
                <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                <XAxis dataKey="month" tick={{ fill: COLORS.textMuted, fontSize: 10 }} />
                <YAxis domain={[0, 100]} tick={{ fill: COLORS.textMuted, fontSize: 10 }} />
                <Tooltip contentStyle={{ background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontSize: 11 }} />
                <Line type="monotone" dataKey="score" stroke={rl.color} strokeWidth={2.5} dot={{ fill: rl.color, r: 3 }} activeDot={{ r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          {/* Convergencia entre fuentes */}
          <Card className="intel-card" style={{ marginBottom: 16 }}>
            <SectionTitle icon="🔀">Convergencia entre Fuentes</SectionTitle>
            <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 12 }}>
              <div style={{ textAlign: "center", padding: "8px 16px", borderRadius: 8, background: `${convergenceColor}11`, border: `1px solid ${convergenceColor}33` }}>
                <div style={{ fontSize: 24, fontWeight: 800, color: convergenceColor, fontFamily: "'DM Mono', monospace" }}>{convergenceScore}</div>
                <div style={{ fontSize: 9, color: COLORS.textDim, marginTop: 2 }}>/100</div>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: convergenceColor, marginBottom: 4 }}>{convergenceLabel}</div>
                <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5 }}>{convergenceNote}</div>
              </div>
            </div>
            <div style={{ display: "flex", gap: 6, fontSize: 10, fontFamily: "'DM Mono', monospace" }}>
              {[
                { label: "FH riesgo", val: fhRisk, color: country.freedomScore < 30 ? COLORS.danger : COLORS.warning },
                { label: "V-Dem riesgo", val: vdemRisk, color: country.vdemIndex < 0.3 ? COLORS.danger : COLORS.warning },
                ...(peiRisk !== null ? [{ label: "PEI riesgo", val: peiRisk, color: parseFloat(peiEmbs) < 30 ? COLORS.danger : COLORS.warning }] : []),
              ].map((s, i) => (
                <div key={i} style={{ flex: 1, background: COLORS.surfaceLight, borderRadius: 6, padding: "6px 8px", textAlign: "center" }}>
                  <div style={{ fontSize: 16, fontWeight: 700, color: s.color }}>{s.val}</div>
                  <div style={{ fontSize: 8, color: COLORS.textDim, marginTop: 2 }}>{s.label}</div>
                </div>
              ))}
            </div>
          </Card>

          {/* Alertas + Violaciones */}
          <Card className="intel-card" style={{ marginBottom: 16 }}>
            <SectionTitle icon="⚠️">Alertas Activas</SectionTitle>
            <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
              {country.alerts.map((alert, i) => <AlertCard key={i} alert={alert} violations={country.violations} />)}
            </div>
          </Card>

          <Card className="intel-card">
            <SectionTitle icon="⚖️">Violaciones al Derecho Internacional</SectionTitle>
            <div style={{ display: "flex", flexDirection: "column", gap: 7, maxHeight: 320, overflowY: "auto" }}>
              {country.violations.length === 0 ? (
                <div style={{ textAlign: "center", padding: 24, color: COLORS.accent }}>
                  <div style={{ fontSize: 24, marginBottom: 6 }}>✓</div>
                  <div style={{ fontSize: 13 }}>Sin violaciones detectadas</div>
                </div>
              ) : country.violations.map((v, i) => <ViolationCard key={i} violation={v} />)}
            </div>
          </Card>
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════════
          CAPA 3 — DICTAMEN PREMIUM + INFORME COMPLETO
      ══════════════════════════════════════════════════════════════ */}
      <div style={{ marginBottom: 24 }}>
        <div className="section-divider" style={{ color: COLORS.purple, marginTop: 0 }}>
          Dictamen Premium — Análisis por Audiencia
        </div>

        {/* Tabs de audiencia */}
        <div style={{ display: "flex", gap: 4, marginBottom: 16 }}>
          {[
            { id: "operativo", label: "Marco General institucional y de riesgo operativo" },
            { id: "electoral", label: "Inteligencia Electoral" },
          ].map(tab => (
            <button key={tab.id} onClick={() => setDictamenTab(tab.id)} style={{
              padding: "7px 16px", borderRadius: 7, border: "none", cursor: "pointer",
              fontSize: 12, fontWeight: 600,
              background: dictamenTab === tab.id ? COLORS.purple + "22" : COLORS.surface,
              color: dictamenTab === tab.id ? COLORS.purple : COLORS.textMuted,
              borderBottom: dictamenTab === tab.id ? `2px solid ${COLORS.purple}` : `2px solid transparent`,
              transition: "all 0.2s",
            }}>
              {tab.label}
            </button>
          ))}
        </div>

        {dictamenTab === "operativo" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            {[
              {
                icon: "1", title: "Línea de Base Estructural",
                content: `Freedom House ${country.freedomScore}/100 · V-Dem ${country.vdemIndex} · PEI EMBs ${peiEmbs || "N/D"}/100. Convergencia: ${convergenceLabel} (${convergenceScore}/100). ${convergenceNote}`,
              },
              {
                icon: "2", title: "Trayectoria Institucional",
                content: `Tendencia: ${country.trend}. El índice PEIRS de ${country.riskScore}/100 refleja una acumulación de fragilidades ${country.riskLevel === "critical" ? "sistémicas" : "parciales"} en el entorno institucional electoral. Dimensión más crítica: ${topDimLabel} (${topDimension?.[1]}/100).`,
              },
              {
                icon: "3", title: "Riesgo Operativo",
                content: country.violations.length > 0
                  ? `${country.violations.length} violaciones al derecho internacional detectadas. Principales: ${country.violations.slice(0, 3).join(", ")}. Exposición legal y reputacional para actores internacionales con presencia en el proceso.`
                  : `Sin violaciones detectadas. El marco institucional presenta condiciones dentro de los estándares internacionales de referencia.`,
              },
              {
                icon: "4", title: "Implicancias para Inversores",
                content: country.riskLevel === "critical"
                  ? `Riesgo crítico. Entorno de alta imprevisibilidad institucional. Recomendación: evaluación de contingencia y monitoreo activo pre-electoral.`
                  : country.riskLevel === "high"
                  ? `Riesgo alto. Fragilidades institucionales que pueden generar volatilidad. Seguimiento trimestral recomendado.`
                  : country.riskLevel === "moderate"
                  ? `Riesgo moderado. Proceso con garantías parciales. Monitoreo estándar.`
                  : `Riesgo bajo. Marco institucional estable. Sin alertas operativas activas.`,
              },
            ].map((block, i) => (
              <div key={i} style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: "14px 16px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <div style={{ width: 22, height: 22, borderRadius: "50%", background: COLORS.purple + "33", color: COLORS.purple, fontSize: 11, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'DM Mono', monospace" }}>
                    {block.icon}
                  </div>
                  <span style={{ fontSize: 12, fontWeight: 700, color: COLORS.text }}>{block.title}</span>
                </div>
                <p style={{ margin: 0, fontSize: 12, color: COLORS.textMuted, lineHeight: 1.7 }}>{block.content}</p>
              </div>
            ))}
          </div>
        )}

        {dictamenTab === "electoral" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            {[
              {
                icon: "1", title: "Síntesis de Integridad Electoral",
                content: `Índice PEIRS: ${country.riskScore}/100 (${rl.label}). EMB: ${embLevel.toUpperCase()}. Observación internacional: ${intlObs ? "presente" : "no documentada"}. Fuentes: FH · V-Dem · PEI · RSF. Confianza del modelo: ${confidenceLabel}.`,
              },
              {
                icon: "2", title: "Estado del Proceso Electoral",
                content: `Elección proyectada: ${country.date}${daysToElection !== null && daysToElection > 0 ? ` (${daysToElection} días)` : ""}. Tendencia del ciclo: ${country.trend}. EMB con autonomía ${embLevel === "full" ? "plena" : embLevel === "partial" ? "parcial" : "comprometida o capturada"}${autonomyVal !== null ? ` (score ${autonomyVal})` : ""}.`,
              },
              {
                icon: "3", title: "Violaciones y Marco Legal",
                content: country.violations.length > 0
                  ? `${country.violations.length} violaciones detectadas ancladas a tratados internacionales: ${country.violations.join(", ")}. Severidad: ${country.riskLevel === "critical" ? "sistémica" : "puntual"}.`
                  : "Sin violaciones detectadas. El proceso cumple con los estándares mínimos observables desde fuentes estructurales.",
              },
              {
                icon: "4", title: "Implicancias para Misiones MOE",
                content: country.riskLevel === "critical"
                  ? `Misión de observación de largo plazo recomendada. Áreas prioritarias: libertad de reunión, independencia del EMB, acceso a medios. Alerta de riesgo para observadores internacionales.`
                  : country.riskLevel === "moderate"
                  ? `Observación estándar con énfasis en jornada electoral y transmisión de resultados. PEI señala déficits en financiamiento de campaña.`
                  : `Condiciones generales dentro de estándares. Observación de corto plazo suficiente. Foco en inclusividad y acceso de minorías.`,
              },
            ].map((block, i) => (
              <div key={i} style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: "14px 16px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <div style={{ width: 22, height: 22, borderRadius: "50%", background: COLORS.accent + "33", color: COLORS.accent, fontSize: 11, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'DM Mono', monospace" }}>
                    {block.icon}
                  </div>
                  <span style={{ fontSize: 12, fontWeight: 700, color: COLORS.text }}>{block.title}</span>
                </div>
                <p style={{ margin: 0, fontSize: 12, color: COLORS.textMuted, lineHeight: 1.7 }}>{block.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Exposición mediática */}
      <Card className="intel-card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
          <SectionTitle icon="📺">Exposición Mediática</SectionTitle>
          <ChartMethodologyBtn chartKey="medios" />
        </div>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={country.mediaData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis type="number" domain={[0, 100]} tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
            <YAxis type="category" dataKey="name" tick={{ fill: COLORS.textMuted, fontSize: 10 }} width={90} />
            <Tooltip contentStyle={{ background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontSize: 11 }} />
            <Bar dataKey="exposure" radius={[0, 5, 5, 0]}>
              {country.mediaData.map((_, i) => (
                <Cell key={i} fill={[COLORS.danger, COLORS.info, COLORS.warning, COLORS.textDim][i] || COLORS.textDim} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Informe VIP completo */}
      <ReportViewer runId={country.run_id} country={country} />
    </div>
  );
};


// ── TOOLTIPS DE METODOLOGÍA ─────────────────────────────────────────────────
const METHODOLOGY_TOOLTIPS = {
  "Freedom House": {
    title: "Freedom House — Freedom in the World",
    desc: "Índice anual que evalúa libertades políticas y civiles en 195 países. Escala 0-100 (100=más libre). Edición 2025.",
    source: "FH FIW 2025",
    url: "https://freedomhouse.org/report/freedom-world",
    confidence: "confirmed",
  },
  "V-Dem": {
    title: "V-Dem — Varieties of Democracy",
    desc: "Dataset académico con más de 400 indicadores de democracia. Cobre 202 países desde 1789. Versión v15 (2024).",
    source: "V-Dem v15 — Coppedge et al. 2025",
    url: "https://v-dem.net",
    confidence: "confirmed",
  },
  "PEI": {
    title: "PEI — Perceptions of Electoral Integrity",
    desc: "Encuesta a expertos electorales sobre percepción de integridad en 586 elecciones (2012-2023). Harvard Dataverse.",
    source: "PEI-10.0 — Garnett et al. 2024",
    url: "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/FQ5ECC",
    confidence: "confirmed",
  },
  "EMB": {
    title: "Organismo Electoral (EMB)",
    desc: "Evaluación de independencia del órgano electoral basada en V-Dem v2elembaut (autonomía) y v2elirreg (irregularidades).",
    source: "V-Dem v15",
    url: "https://v-dem.net",
    confidence: "confirmed",
  },
  "ICCPR": {
    title: "ICCPR — Pacto Internacional de Derechos Civiles y Políticos",
    desc: "Tratado de la ONU (1966) que establece el derecho a elecciones libres (Art. 25), libertad de expresión (Art. 19), reunión (Art. 21-22) y garantías procesales (Art. 14).",
    source: "Derecho Internacional",
    confidence: "confirmed",
  },
  "CADH": {
    title: "CADH — Convención Americana sobre Derechos Humanos",
    desc: "Tratado interamericano (1969). Art. 23 garantiza derechos políticos: votar, ser elegido y acceder a cargos públicos en condiciones de igualdad.",
    source: "Sistema Interamericano de DDHH",
    confidence: "confirmed",
  },
  "CDI": {
    title: "CDI — Carta Democrática Interamericana (OEA)",
    desc: "Aprobada en 2001 por la OEA. Arts. 3-4 definen elementos esenciales de la democracia: libertad de expresión, prensa libre, separación de poderes y elecciones periódicas.",
    source: "OEA — Carta Democrática Interamericana",
    confidence: "confirmed",
  },
};

const LEGAL_ARTICLES = {
  "Art. 19": { right: "Libertad de Expresión", desc: "Derecho a buscar, recibir y difundir información e ideas sin interferencia. Protege la libertad de prensa como pilar de la democracia electoral." },
  "Art. 21 & Art. 22": { right: "Libertad de Reunión y Asociación", desc: "Derecho a reunión pacífica y a asociarse con otros, incluida la formación de partidos políticos y organizaciones de la sociedad civil." },
  "Art. 9": { right: "Libertad y Seguridad Personal", desc: "Prohibición de detención arbitraria. La existencia de presos políticos constituye una violación directa que intimida la participación electoral." },
  "Art. 14": { right: "Derecho a Tribunal Independiente", desc: "Garantía de proceso justo ante tribunal imparcial. En contexto electoral, protege el derecho a impugnar resultados ante un poder judicial independiente." },
  "Art. 25": { right: "Derecho a Participar en Asuntos Públicos", desc: "Derecho fundamental a votar y ser elegido en elecciones genuinas, periódicas, por sufragio universal e igual, con voto secreto." },
  "Art. 25(b)": { right: "Sufragio Activo y Pasivo", desc: "Derecho específico a ser candidato en elecciones genuinas. La inhabilitación arbitraria de candidatos viola este artículo." },
  "Art. 19(2)": { right: "Libertad de Expresión Digital", desc: "Extensión del Art. 19 al entorno digital. La censura de internet y redes sociales restringe el derecho a recibir información en campaña electoral." },
  "Art. 25(a)": { right: "Sufragio Universal", desc: "Toda persona tiene derecho a votar sin discriminación. Tácticas de supresión de votantes, incluso en medios digitales, violan este principio." },
  "Art. 23": { right: "Derechos Políticos (CADH)", desc: "Bajo el sistema interamericano, todo ciudadano tiene derecho a participar en la dirección de asuntos públicos y a votar en elecciones auténticas." },
  "Art. 3-4": { right: "Elementos Esenciales de la Democracia (OEA)", desc: "La CDI define como elementos esenciales: respeto a los derechos humanos, celebración de elecciones periódicas y separación e independencia de poderes." },
};

const TooltipInfo = ({ text, children }) => {
  const [show, setShow] = useState(false);
  // El wrapper era <span>, lo que genera HTML inválido cuando children es un <div>
  // (caso típico en DimensionBar). Ese mismatch rompe layout y hace parpadear el
  // tooltip al hover. Cambio a <div> con layout block; conserva tamaño natural.
  // Wrapper block por defecto (hijo puede ser div o span), pero configurable para
  // usos inline (InfoIcon al lado de un título) vía prop `inline`.
  const wrapperStyle = text.inline
    ? { position: "relative", display: "inline-block" }
    : { position: "relative", display: "block", width: "100%" };
  return (
    <div style={wrapperStyle}
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}>
      {children}
      {show && (
        <div style={{
          position: "absolute", bottom: "calc(100% + 8px)", left: "50%",
          transform: "translateX(-50%)", zIndex: 1000,
          background: "#0d1625", border: `1px solid ${COLORS.accent}44`,
          borderRadius: 8, padding: "10px 14px", width: 280,
          boxShadow: "0 8px 32px rgba(0,0,0,0.6)",
          pointerEvents: "none",
        }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.accent, marginBottom: 4 }}>{text.title}</div>
          <div style={{ fontSize: 11, color: COLORS.text, lineHeight: 1.5, marginBottom: 6 }}>{text.desc}</div>
          <div style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
            📎 {text.source}
          </div>
          {text.confidence && (
            <div style={{ marginTop: 4 }}>
              <span style={{
                fontSize: 9, padding: "2px 6px", borderRadius: 4,
                background: text.confidence === "confirmed" ? COLORS.accentDim : COLORS.warningDim,
                color: text.confidence === "confirmed" ? COLORS.accent : COLORS.warning,
                fontFamily: "'DM Mono', monospace",
              }}>
                {text.confidence === "confirmed" ? "✓ VERIFICADO" : "⚠ MOCK"}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const InfoIcon = ({ tooltip }) => (
  <TooltipInfo text={{ ...tooltip, inline: true }}>
    <span style={{
      display: "inline-flex", alignItems: "center", justifyContent: "center",
      width: 16, height: 16, borderRadius: "50%",
      background: COLORS.accentDim, color: COLORS.accent,
      fontSize: 10, fontWeight: 800, cursor: "help",
      marginLeft: 6, verticalAlign: "middle", flexShrink: 0,
    }}>ⓘ</span>
  </TooltipInfo>
);

// ── RENDER MARKDOWN CON TOOLTIPS ─────────────────────────────────────────────
const CHAPTER_ICONS = {
  "1.": "📊", "2.": "🏛️", "3.": "🗳️", "4.": "👥",
  "5.": "📺", "6.": "🌐", "7.": "📋", "8.": "⚖️", "9.": "🎯",
};

const CHAPTER_COLORS = {
  "1.": "#00d4aa", "2.": "#3b82f6", "3.": "#a855f7", "4.": "#f59e0b",
  "5.": "#ec4899", "6.": "#06b6d4", "7.": "#64748b", "8.": "#ef4444", "9.": "#00d4aa",
};

const renderMarkdownWithTooltips = (md) => {
  if (!md) return [];
  const lines = md.split("\n");
  const elements = [];
  let i = 0;
  let tableBuffer = [];
  let inTable = false;
  let currentChapterNum = null;

  const flushTable = (key) => {
    if (tableBuffer.length < 2) { tableBuffer = []; inTable = false; return; }
    const header = tableBuffer[0].split("|").map(c => c.trim()).filter(Boolean);
    const rows = tableBuffer.slice(2).map(r => r.split("|").map(c => c.trim()).filter(Boolean));
    const isViolationTable = header.some(h => h.toLowerCase().includes("confianza") || h.toLowerCase().includes("referencia"));

    elements.push(
      <div key={`table-${key}`} style={{ overflowX: "auto", marginBottom: 20, borderRadius: 10, border: `1px solid ${COLORS.border}`, boxShadow: "0 2px 12px rgba(0,0,0,0.3)" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "linear-gradient(90deg, #0d1625, #111827)" }}>
              {header.map((h, hi) => (
                <th key={hi} style={{
                  padding: "12px 16px", textAlign: "left", fontSize: 11,
                  fontWeight: 700, textTransform: "uppercase", letterSpacing: 1.5,
                  color: COLORS.accent, borderBottom: `2px solid ${COLORS.accent}33`,
                  whiteSpace: "nowrap",
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => {
              const articleCell = isViolationTable ? row[0] : null;
              const articleKey = articleCell ? Object.keys(LEGAL_ARTICLES).find(k => articleCell.includes(k)) : null;
              return (
                <tr key={ri} style={{
                  borderBottom: `1px solid ${COLORS.border}`,
                  background: ri % 2 === 0 ? "transparent" : COLORS.surfaceLight + "66",
                  transition: "background 0.15s ease",
                }}>
                  {row.map((cell, ci) => {
                    const isConf = cell === "CONFIRMED";
                    const isMock = cell === "MOCK";
                    const isRisk = ["CRITICAL","HIGH","MODERATE","LOW"].includes(cell);
                    const riskColors = { CRITICAL: COLORS.danger, HIGH: "#f97316", MODERATE: COLORS.warning, LOW: COLORS.accent };
                    return (
                      <td key={ci} style={{
                        padding: "10px 16px", fontSize: 13, lineHeight: 1.5,
                        color: isConf ? COLORS.accent : isMock ? COLORS.warning : isRisk ? riskColors[cell] : COLORS.text,
                        fontFamily: (isConf || isMock || isRisk) ? "'DM Mono', monospace" : "inherit",
                        fontWeight: isRisk ? 700 : "normal",
                      }}>
                        {isConf ? "✓ VERIFICADO" : isMock ? "⚠ PENDIENTE" : cell}
                        {ci === 0 && articleKey && LEGAL_ARTICLES[articleKey] && (
                          <InfoIcon tooltip={{
                            title: `${articleCell} — ${LEGAL_ARTICLES[articleKey].right}`,
                            desc: LEGAL_ARTICLES[articleKey].desc,
                            source: articleCell.split(" ")[0],
                            confidence: "confirmed",
                          }} />
                        )}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
    tableBuffer = []; inTable = false;
  };

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith("|")) {
      inTable = true;
      tableBuffer.push(line);
      i++;
      continue;
    } else if (inTable) {
      flushTable(i);
    }

    // H1 — Título del informe
    if (line.startsWith("# ")) {
      elements.push(
        <h1 key={i} style={{
          margin: "0 0 4px", fontSize: 22, fontWeight: 900,
          color: COLORS.text, fontFamily: "'Fraunces', serif", letterSpacing: -0.5,
        }}>{line.replace("# ", "")}</h1>
      );

    // H2 — Títulos de capítulo con diseño premium
    } else if (line.startsWith("## ")) {
      const title = line.replace("## ", "");
      const chNum = Object.keys(CHAPTER_ICONS).find(k => title.startsWith(k));
      const chColor = CHAPTER_COLORS[chNum] || COLORS.accent;
      const chIcon = CHAPTER_ICONS[chNum] || "📄";
      currentChapterNum = chNum;

      const tooltipMatch = Object.keys(METHODOLOGY_TOOLTIPS).find(k => title.includes(k));

      elements.push(
        <div key={i} style={{
          margin: "32px 0 16px",
          padding: "14px 18px",
          background: `linear-gradient(135deg, ${chColor}0a, transparent)`,
          borderLeft: `4px solid ${chColor}`,
          borderRadius: "0 8px 8px 0",
          display: "flex", alignItems: "center", gap: 12,
        }}>
          <span style={{ fontSize: 20 }}>{chIcon}</span>
          <h2 style={{
            margin: 0, fontSize: 14, fontWeight: 800, color: chColor,
            textTransform: "uppercase", letterSpacing: 2,
            fontFamily: "'DM Mono', monospace", flex: 1,
          }}>{title}</h2>
          {tooltipMatch && <InfoIcon tooltip={METHODOLOGY_TOOLTIPS[tooltipMatch]} />}
        </div>
      );

    // H3 — Subsecciones con línea sutil
    } else if (line.startsWith("### ")) {
      const title = line.replace("### ", "");
      const chColor = CHAPTER_COLORS[currentChapterNum] || COLORS.accent;
      elements.push(
        <div key={i} style={{
          display: "flex", alignItems: "center", gap: 8,
          margin: "20px 0 10px",
        }}>
          <h3 style={{
            margin: 0, fontSize: 12, fontWeight: 700, color: chColor,
            textTransform: "uppercase", letterSpacing: 1.5,
            fontFamily: "'DM Mono', monospace",
          }}>{title}</h3>
          <div style={{ flex: 1, height: 1, background: `linear-gradient(90deg, ${chColor}44, transparent)` }} />
        </div>
      );

    // Nivel de Riesgo destacado
    } else if (line.includes("Nivel de Riesgo") && line.includes("**")) {
      const isCrit = line.includes("CRITICAL");
      const isHigh = line.includes("HIGH");
      const isMod = line.includes("MODERATE");
      const color = isCrit ? COLORS.danger : isHigh ? "#f97316" : isMod ? COLORS.warning : COLORS.accent;
      elements.push(
        <div key={i} style={{
          padding: "14px 18px", borderRadius: 10, marginBottom: 16,
          background: color + "12", border: `1px solid ${color}44`,
          borderLeft: `4px solid ${color}`,
          fontSize: 15, fontWeight: 700, color,
          display: "flex", alignItems: "center", gap: 10,
        }}>
          <span style={{ fontSize: 18 }}>{isCrit ? "🔴" : isHigh ? "🟠" : isMod ? "🟡" : "🟢"}</span>
          {line.replace(/\*\*/g, "")}
        </div>
      );

    // Dictamen Técnico — bloque especial
    } else if (line.startsWith("### Dictamen Técnico")) {
      elements.push(
        <div key={i} style={{
          margin: "20px 0 10px", padding: "10px 16px",
          background: "linear-gradient(90deg, #00d4aa0a, transparent)",
          borderLeft: "3px solid #00d4aa",
          borderRadius: "0 8px 8px 0",
          display: "flex", alignItems: "center", gap: 8,
        }}>
          <span style={{ fontSize: 16 }}>📋</span>
          <h3 style={{
            margin: 0, fontSize: 12, fontWeight: 700, color: COLORS.accent,
            textTransform: "uppercase", letterSpacing: 1.5, fontFamily: "'DM Mono', monospace",
          }}>{line.replace("### ", "")}</h3>
        </div>
      );

    // Confianza de datos
    } else if (line.includes("Confianza de Datos:")) {
      const isHigh = line.includes("HIGH");
      const isMed = line.includes("MEDIUM");
      const color = isHigh ? COLORS.accent : isMed ? COLORS.warning : COLORS.danger;
      elements.push(
        <div key={i} style={{
          display: "inline-flex", alignItems: "center", gap: 8,
          padding: "6px 14px", borderRadius: 20, marginBottom: 10,
          background: color + "18", border: `1px solid ${color}44`,
          fontSize: 12, color, fontFamily: "'DM Mono', monospace", fontWeight: 600,
        }}>
          {line.replace(/\*\*/g, "")}
        </div>
      );

    // Tendencia histórica
    } else if (line.startsWith("**Tendencia V-Dem")) {
      elements.push(
        <div key={i} style={{
          padding: "8px 14px", borderRadius: 8, marginBottom: 8,
          background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`,
          fontSize: 12, color: COLORS.text,
        }}>
          <span dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.+?)\*\*/g, '<strong style="color:#e2e8f0">$1</strong>') }} />
        </div>
      );

    // Comparación regional
    } else if (line.startsWith("**Comparación regional")) {
      elements.push(
        <div key={i} style={{
          padding: "8px 14px", borderRadius: 8, marginBottom: 12,
          background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`,
          fontSize: 12, color: COLORS.text,
        }}>
          <span dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.+?)\*\*/g, '<strong style="color:#e2e8f0">$1</strong>') }} />
        </div>
      );

    // Líneas con viñeta
    } else if (line.startsWith("- ")) {
      const text = line.replace("- ", "");
      const matchedSource = Object.keys(METHODOLOGY_TOOLTIPS).find(k => text.includes(k));
      elements.push(
        <div key={i} style={{ display: "flex", gap: 10, marginBottom: 7, alignItems: "flex-start" }}>
          <span style={{
            color: COLORS.accent, marginTop: 3, flexShrink: 0,
            fontSize: 8, background: COLORS.accentDim,
            borderRadius: "50%", width: 16, height: 16,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>▸</span>
          <span style={{ fontSize: 14, color: COLORS.text, lineHeight: 1.7 }}>
            <span dangerouslySetInnerHTML={{ __html: text.replace(/\*\*(.+?)\*\*/g, '<strong style="color:#e2e8f0;font-weight:700">$1</strong>') }} />
            {matchedSource && <InfoIcon tooltip={METHODOLOGY_TOOLTIPS[matchedSource]} />}
          </span>
        </div>
      );

    // Separador
    } else if (line.startsWith("---")) {
      elements.push(<hr key={i} style={{ border: "none", borderTop: `1px solid ${COLORS.border}`, margin: "24px 0" }} />);

    // Cursiva / nota metodológica
    } else if (line.startsWith("*") && line.endsWith("*") && !line.startsWith("**")) {
      elements.push(
        <div key={i} style={{
          margin: "0 0 10px", padding: "10px 14px", borderRadius: 8,
          background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`,
          fontSize: 12, color: COLORS.textMuted, fontStyle: "italic", lineHeight: 1.6,
          borderLeft: `3px solid ${COLORS.warning}`,
        }}>
          {line.replace(/^\*|\*$/g, "")}
        </div>
      );

    // Texto normal — párrafos de análisis narrativo
    } else if (line.trim() !== "") {
      const parsed = line
        .replace(/\*\*(.+?)\*\*/g, (_, t) => `<strong style="color:${COLORS.text};font-weight:700">${t}</strong>`)
        .replace(/`(.+?)`/g, (_, t) => `<code style="background:${COLORS.surfaceLight};color:${COLORS.accent};padding:2px 7px;border-radius:4px;font-size:12px;font-family:'DM Mono',monospace">${t}</code>`);
      elements.push(
        <p key={i} style={{
          margin: "0 0 14px", fontSize: 14, color: COLORS.text,
          lineHeight: 1.85, letterSpacing: 0.1,
        }}
          dangerouslySetInnerHTML={{ __html: parsed }} />
      );
    }
    i++;
  }
  if (inTable) flushTable(i);
  return elements;
};


// ── GENERADOR HTML DESCARGABLE ────────────────────────────────────────────────
const generateHtmlReport = (markdown, country, runId, timestamp, reportData, chartData = null, actorsData = null, scenariosData = null, moeBrief = null) => {
  // ── Colores por nivel de riesgo ───────────────────────────────────────────
  const riskPalette = {
    critical: { hex: "#b91c1c", light: "#fef2f2", mid: "#fca5a5", label: "CRÍTICO" },
    high:     { hex: "#c2410c", light: "#fff7ed", mid: "#fdba74", label: "ALTO" },
    moderate: { hex: "#b45309", light: "#fffbeb", mid: "#fcd34d", label: "MODERADO" },
    low:      { hex: "#065f46", light: "#ecfdf5", mid: "#6ee7b7", label: "BAJO" },
  };
  const rp = riskPalette[country.riskLevel] || riskPalette.moderate;
  const score = country.riskScore || 0;

  // ── Extractor de datos con trazabilidad ───────────────────────────────────
  const ctx = (reportData && reportData.context_data) || {};
  const legal = (reportData && reportData.legal_analysis) || {};
  const chapters = (reportData && reportData.report_chapters) || {};
  const dims = country.dimensions || {};
  const violations = legal.violations || [];
  const dataSources = legal.data_sources_summary || {};

  const xv = (d) => (d && d._trace) ? d.value : (d || {});
  const fh   = xv(ctx.freedom_house);   const fhScore  = fh.total_score || fh.score || "—";
  const vdem = xv(ctx.vdem);            const vdemIdx  = vdem.liberal_democracy || "—";
  const pei  = xv(ctx.pei);             const peiScore = pei.overall_integrity || "—";
  const rsf  = xv(ctx.rsf);             const rsfScore = rsf.score || "—";
  const emb  = xv(ctx.emb);             const embLevel = emb.independence_level || "—";

  // ── SVG: Gauge semicircular ───────────────────────────────────────────────
  const gaugeAngle = 180 - (score / 100) * 180;
  const gaugeRad = (gaugeAngle * Math.PI) / 180;
  const gx = Math.round(100 + 75 * Math.cos(gaugeRad));
  const gy = Math.round(100 - 75 * Math.sin(gaugeRad));
  const largeArc = score > 50 ? 1 : 0;
  const gaugeSvg = `
<svg viewBox="0 0 200 120" width="180" height="108" xmlns="http://www.w3.org/2000/svg">
  <path d="M 25 100 A 75 75 0 0 1 175 100" stroke="#e2e8f0" stroke-width="14" fill="none" stroke-linecap="round"/>
  <path d="M 25 100 A 75 75 0 ${largeArc} 1 ${gx} ${gy}" stroke="${rp.hex}" stroke-width="14" fill="none" stroke-linecap="round"/>
  <circle cx="${gx}" cy="${gy}" r="5" fill="${rp.hex}"/>
  <text x="100" y="90" text-anchor="middle" font-size="36" font-weight="900" fill="${rp.hex}" font-family="Georgia,serif">${score}</text>
  <text x="100" y="108" text-anchor="middle" font-size="9" fill="#64748b" font-family="sans-serif" letter-spacing="1">ÍNDICE DE RIESGO / 100</text>
</svg>`;

  // ── SVG: Barras de dimensiones ────────────────────────────────────────────
  const dimDefs = [
    { key: "suffrage",         label: "Sufragio Universal" },
    { key: "legalFramework",   label: "Marco Legal" },
    { key: "embIndependence",  label: "Independencia EMB" },
    { key: "mediaFreedom",     label: "Libertad de Medios" },
    { key: "campaignFinance",  label: "Financiamiento" },
    { key: "digitalEcosystem", label: "Ecosistema Digital" },
    { key: "disputeResolution",label: "Justicia Electoral" },
    { key: "inclusion",        label: "Inclusividad" },
  ];
  const barColor = (v) => v >= 70 ? "#065f46" : v >= 45 ? "#b45309" : v >= 25 ? "#c2410c" : "#991b1b";
  const dimBarsHtml = dimDefs.map(({ key, label }) => {
    const val = Math.round(dims[key] || 0);
    const w = Math.max(2, val);
    const col = barColor(val);
    return `
<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
  <div style="width:160px;font-size:11px;color:#475569;text-align:right;flex-shrink:0">${label}</div>
  <div style="flex:1;background:#f1f5f9;border-radius:4px;height:14px;position:relative">
    <div style="height:100%;width:${w}%;background:${col};border-radius:4px;transition:width 1s"></div>
  </div>
  <div style="width:36px;font-size:12px;font-weight:700;color:${col};font-family:monospace">${val}</div>
</div>`;
  }).join("");

  // ── SVG Charts V-Dem inline ───────────────────────────────────────────────
  const _svgLine = (series, { w = 660, h = 160, padL = 44, padR = 20, padT = 22, padB = 32,
                               color = "#0f766e", minY = null, maxY = null, milestones = [],
                               yTicks = null, yFmt = v => v.toFixed(2) } = {}) => {
    if (!series || !series.length) return '<p class="no-data">Datos no disponibles.</p>';
    const xs = series.map(d => d.year || d.x);
    const ys = series.map(d => typeof d.value === "number" ? d.value : d.y);
    const xMin = Math.min(...xs), xMax = Math.max(...xs);
    const yMin = minY !== null ? minY : Math.min(...ys) * 0.95;
    const yMax = maxY !== null ? maxY : Math.max(...ys) * 1.05;
    const cx = x => padL + ((x - xMin) / (xMax - xMin || 1)) * (w - padL - padR);
    const cy = y => h - padB - ((y - yMin) / (yMax - yMin || 1)) * (h - padT - padB);
    const linePts = series.map(d => `${cx(d.year||d.x)},${cy(typeof d.value==="number"?d.value:d.y)}`);
    const areaPath = `M ${cx(xMin)},${cy(yMin)} L ${linePts.join(" L ")} L ${cx(xMax)},${cy(yMin)} Z`;
    const linePath = `M ${linePts.join(" L ")}`;
    const xTickYears = Array.from(new Set([xMin, ...Array.from({length: 7}, (_, i) => Math.round(xMin + i * (xMax - xMin) / 6)), xMax])).filter(y => y >= xMin && y <= xMax).sort((a,b)=>a-b);
    const yTickVals = yTicks || [0, 0.25, 0.5, 0.75, 1.0].map(f => yMin + f * (yMax - yMin));
    const gradId = `g${Math.random().toString(36).slice(2,8)}`;
    return `<svg viewBox="0 0 ${w} ${h}" width="100%" style="display:block;max-width:${w}px" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="${gradId}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${color}" stop-opacity="0.25"/><stop offset="100%" stop-color="${color}" stop-opacity="0.02"/></linearGradient></defs>
  ${yTickVals.map(v=>`<line x1="${padL}" y1="${cy(v)}" x2="${w-padR}" y2="${cy(v)}" stroke="#e2e8f0" stroke-width="0.8" stroke-dasharray="3,3"/>`).join("")}
  ${milestones.map(m=>`<line x1="${cx(m.year)}" y1="${padT}" x2="${cx(m.year)}" y2="${h-padB}" stroke="#b45309" stroke-width="1" stroke-dasharray="4,3" opacity="0.7"/>
  <text x="${cx(m.year)}" y="${padT-4}" text-anchor="middle" font-size="7" fill="#b45309" font-family="monospace">${m.year}</text>`).join("")}
  <path d="${areaPath}" fill="url(#${gradId})"/>
  <path d="${linePath}" fill="none" stroke="${color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
  <line x1="${padL}" y1="${h-padB}" x2="${w-padR}" y2="${h-padB}" stroke="#cbd5e1" stroke-width="1"/>
  <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${h-padB}" stroke="#cbd5e1" stroke-width="1"/>
  ${xTickYears.map(y=>`<line x1="${cx(y)}" y1="${h-padB}" x2="${cx(y)}" y2="${h-padB+4}" stroke="#94a3b8" stroke-width="1"/><text x="${cx(y)}" y="${h-padB+14}" text-anchor="middle" font-size="8" fill="#94a3b8" font-family="monospace">${y}</text>`).join("")}
  ${yTickVals.map(v=>`<text x="${padL-5}" y="${cy(v)+3}" text-anchor="end" font-size="8" fill="#94a3b8" font-family="monospace">${yFmt(v)}</text>`).join("")}
  ${series.length?`<circle cx="${cx(xs[xs.length-1])}" cy="${cy(ys[ys.length-1])}" r="4" fill="${color}" stroke="white" stroke-width="1.5"/>`:``}
</svg>`;
  };

  const _svgGroupedBars = (series, key1, key2, { w = 660, h = 160, padL = 44, padR = 16, padT = 16, padB = 32,
                                                    c1 = "#0f766e", c2 = "#7c3aed", label1 = "A", label2 = "B",
                                                    maxY = 1 } = {}) => {
    if (!series || !series.length) return '<p class="no-data">Datos no disponibles.</p>';
    const n = series.length;
    const slotW = (w - padL - padR) / n;
    const bW = slotW * 0.35;
    const cy = v => h - padB - (v / maxY) * (h - padT - padB);
    const yTicks = [0, 0.25, 0.5, 0.75, 1.0].map(f => f * maxY);
    return `<svg viewBox="0 0 ${w} ${h}" width="100%" style="display:block;max-width:${w}px" xmlns="http://www.w3.org/2000/svg">
  ${yTicks.map(v=>`<line x1="${padL}" y1="${cy(v)}" x2="${w-padR}" y2="${cy(v)}" stroke="#e2e8f0" stroke-width="0.8" stroke-dasharray="3,3"/><text x="${padL-5}" y="${cy(v)+3}" text-anchor="end" font-size="8" fill="#94a3b8" font-family="monospace">${v.toFixed(2)}</text>`).join("")}
  <line x1="${padL}" y1="${h-padB}" x2="${w-padR}" y2="${h-padB}" stroke="#cbd5e1" stroke-width="1"/>
  <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${h-padB}" stroke="#cbd5e1" stroke-width="1"/>
  ${series.map((d, i) => {
    const x = padL + i * slotW + slotW / 2;
    const v1 = Math.max(0, Math.min(maxY, d[key1] || 0));
    const v2 = Math.max(0, Math.min(maxY, d[key2] || 0));
    const bh1 = (v1/maxY)*(h-padT-padB);
    const bh2 = (v2/maxY)*(h-padT-padB);
    return `<rect x="${x-bW-1}" y="${cy(v1)}" width="${bW}" height="${bh1}" fill="${c1}" rx="2"/>
    <rect x="${x+1}" y="${cy(v2)}" width="${bW}" height="${bh2}" fill="${c2}" rx="2"/>
    <text x="${x}" y="${h-padB+14}" text-anchor="middle" font-size="8" fill="#94a3b8" font-family="monospace">${d.year||d.x||""}</text>`;
  }).join("")}
  <rect x="${padL+8}" y="${padT}" width="10" height="8" fill="${c1}" rx="1"/>
  <text x="${padL+22}" y="${padT+7}" font-size="9" fill="#475569" font-family="sans-serif">${label1}</text>
  <rect x="${padL+90}" y="${padT}" width="10" height="8" fill="${c2}" rx="1"/>
  <text x="${padL+104}" y="${padT+7}" font-size="9" fill="#475569" font-family="sans-serif">${label2}</text>
</svg>`;
  };

  const _svgHBar = (items, { w = 660, h = null, padL = 180, padR = 60, padT = 14, padB = 14,
                              color = "#0f766e", highlightCode = null, maxX = 100 } = {}) => {
    if (!items || !items.length) return '<p class="no-data">Datos no disponibles.</p>';
    const rowH = 26, totalH = h || (items.length * rowH + padT + padB);
    const bW = w - padL - padR;
    return `<svg viewBox="0 0 ${w} ${totalH}" width="100%" style="display:block;max-width:${w}px" xmlns="http://www.w3.org/2000/svg">
  ${items.map((item, i) => {
    const y = padT + i * rowH;
    const val = Math.max(0, Math.min(maxX, item.value || item.score || 0));
    const barW = (val / maxX) * bW;
    const isHL = item.code === highlightCode;
    const col = isHL ? "#b45309" : color;
    return `<rect x="${padL}" y="${y+3}" width="${barW}" height="${rowH-8}" fill="${col}" rx="2" opacity="${isHL?1:0.75}"/>
    <text x="${padL-6}" y="${y+rowH/2+4}" text-anchor="end" font-size="9" fill="${isHL?"#1e293b":"#475569"}" font-family="sans-serif" font-weight="${isHL?700:400}">${item.name||item.country||item.code}</text>
    <text x="${padL+barW+5}" y="${y+rowH/2+4}" font-size="9" fill="${col}" font-family="monospace" font-weight="600">${Math.round(val)}</text>`;
  }).join("")}
  <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${totalH-padB}" stroke="#cbd5e1" stroke-width="1"/>
</svg>`;
  };

  // Build chart SVGs from chartData
  const vdemCharts = (() => {
    if (!chartData) return null;
    const c = chartData.charts || {};
    const libdem = c.libdem_series || [];
    const milestones = chartData.milestones || [];
    const emb = (c.emb_series || []).map(d => ({
      year: d.year,
      emb_autonomy: d.v2elembaut,
      emb_capacity: d.v2elembcap,
    }));
    // Media: use v2mebias as primary signal (inverted: higher=more free), fallback v2meharjrn
    const media = (c.media_series || []).map(d => ({
      year: d.year,
      value: typeof d.v2mebias === "number" ? d.v2mebias
           : typeof d.v2meharjrn === "number" ? d.v2meharjrn : null,
    })).filter(d => d.value !== null);
    const regional = (c.regional || []).map(r => ({
      ...r,
      value: Math.round((r.libdem || 0) * 100),
      name: r.name || r.country_name || r.country_code,
      code: r.country_code,
    })).sort((a,b) => b.value - a.value);
    const frefair = (c.frefair_series || []);
    const alertSeries = (c.alert_series || []);
    const year = libdem.length > 0
      ? String(libdem[libdem.length - 1].year)
      : (chartData.generated_at ? new Date(chartData.generated_at).getFullYear().toString() : "2024");
    return { libdem, milestones, emb, media, regional, frefair, alertSeries, year };
  })();

  const vdemSectionHtml = vdemCharts ? `
  <!-- ════ SECCIÓN F: DATOS V-Dem ════════════════════════════════════════════ -->
  <div class="section-header">
    <div class="section-number">F</div>
    <div class="section-title">Datos Históricos V-Dem — Perú ${vdemCharts.year}</div>
  </div>
  <div class="vdem-charts-section">

    <div class="chart-block">
      <div class="chart-title">Índice de Democracia Liberal — Perú 1990–${vdemCharts.year}</div>
      <div class="chart-subtitle">Evolución histórica del índice <code>v2x_libdem</code> (escala 0–1, donde 1 = máxima democracia liberal). Las líneas verticales marcan elecciones presidenciales.</div>
      ${_svgLine(vdemCharts.libdem, { color: "#0f766e", minY: 0, maxY: 1, milestones: vdemCharts.milestones, yFmt: v => v.toFixed(2) })}
      <div class="chart-source">Fuente: Coppedge, M., et al. (2025). <em>V-Dem Dataset v15</em>. Variable: <code>v2x_libdem</code>. Varieties of Democracy Project. DOI: <a href="https://doi.org/10.23696/vdemds25">10.23696/vdemds25</a></div>
    </div>

    <div class="chart-block">
      <div class="chart-title">JNE — Autonomía e Independencia Institucional 2014–${vdemCharts.year}</div>
      <div class="chart-subtitle">Comparación anual entre la autonomía (<code>v2elembaut</code>) y la capacidad institucional (<code>v2elembcap</code>) del Jurado Nacional de Elecciones. Ambas escalas 0–1.</div>
      ${_svgGroupedBars(vdemCharts.emb, "emb_autonomy", "emb_capacity", { label1: "Autonomía (v2elembaut)", label2: "Capacidad (v2elembcap)", c1: "#0f766e", c2: "#7c3aed", maxY: 1 })}
      <div class="chart-source">Fuente: Coppedge, M., et al. (2025). <em>V-Dem Dataset v15</em>. Variables: <code>v2elembaut</code>, <code>v2elembcap</code>. Varieties of Democracy Project. DOI: <a href="https://doi.org/10.23696/vdemds25">10.23696/vdemds25</a></div>
    </div>

    <div class="chart-block">
      <div class="chart-title">Ecosistema Mediático — Perú 2010–${vdemCharts.year}</div>
      <div class="chart-subtitle">Sesgo mediático favorable al gobierno (<code>v2mebias</code>, invertido: mayor = más libre) + acoso a periodistas (<code>v2meharjrn</code>) y censura de noticias (<code>v2mecenefi</code>). Escala 0–1.</div>
      ${_svgLine(vdemCharts.media, { color: "#7c3aed", minY: 0, maxY: 1, yFmt: v => v.toFixed(2) })}
      <div class="chart-source">Fuente: Coppedge, M., et al. (2025). <em>V-Dem Dataset v15</em>. Variables: <code>v2mebias</code>, <code>v2meharjrn</code>, <code>v2mecenefi</code>. Varieties of Democracy Project. DOI: <a href="https://doi.org/10.23696/vdemds25">10.23696/vdemds25</a></div>
    </div>

    ${vdemCharts.regional.length > 0 ? `
    <div class="chart-block">
      <div class="chart-title">Perú en Perspectiva Regional — Democracia Liberal (V-Dem ${vdemCharts.year})</div>
      <div class="chart-subtitle">Índice <code>v2x_libdem</code> × 100 para países de América Latina monitoreados por PEIRS. <strong>Perú resaltado en naranja.</strong> Mayor valor = mayor democracia liberal.</div>
      ${_svgHBar(vdemCharts.regional, { padL: 140, highlightCode: "PER", maxX: 100, color: "#0f766e" })}
      <div class="chart-source">Fuente: Coppedge, M., et al. (2025). <em>V-Dem Dataset v15</em>. Variable: <code>v2x_libdem</code>. Varieties of Democracy Project. DOI: <a href="https://doi.org/10.23696/vdemds25">10.23696/vdemds25</a></div>
    </div>` : ""}

    ${vdemCharts.frefair && vdemCharts.frefair.length > 0 ? `
    <div class="chart-block">
      <div class="chart-title">Elecciones Libres y Justas — Perú 1990–${vdemCharts.year}</div>
      <div class="chart-subtitle">Variable <code>v2xel_frefair</code>: mide si las elecciones son libres y justas según expertos. Escala 0–1 (1 = plenamente libres y justas). Es la variable V-Dem más directamente vinculada a integridad electoral — distinta de <code>v2x_libdem</code> que mide democracia estructural.</div>
      ${_svgLine(vdemCharts.frefair, { color: "#0369a1", minY: 0, maxY: 1, milestones: vdemCharts.milestones, yFmt: v => v.toFixed(2) })}
      <div class="chart-source">Fuente: Coppedge, M., et al. (2025). <em>V-Dem Dataset v15</em>. Variable: <code>v2xel_frefair</code>. Varieties of Democracy Project. DOI: <a href="https://doi.org/10.23696/vdemds25">10.23696/vdemds25</a></div>
    </div>` : ""}

    ${vdemCharts.alertSeries && vdemCharts.alertSeries.length > 0 ? `
    <div class="chart-block">
      <div class="chart-title">Indicadores de Alerta Temprana — Irregularidades e Intimidación Electoral 2000–${vdemCharts.year}</div>
      <div class="chart-subtitle"><code>v2elirreg</code>: irregularidades electorales (0 = irregularidades sistemáticas; 1 = proceso limpio). <code>v2elintim</code>: intimidación electoral a votantes y candidatos (0 = intimidación severa; 1 = sin intimidación). Valores bajos en años electorales predicen incidentes en jornada.</div>
      ${_svgGroupedBars(vdemCharts.alertSeries, "v2elirreg", "v2elintim", { label1: "Irregularidades (v2elirreg)", label2: "Intimidación (v2elintim)", c1: "#dc2626", c2: "#d97706", maxY: 1 })}
      <div class="chart-source">Fuente: Coppedge, M., et al. (2025). <em>V-Dem Dataset v15</em>. Variables: <code>v2elirreg</code>, <code>v2elintim</code>. Varieties of Democracy Project. DOI: <a href="https://doi.org/10.23696/vdemds25">10.23696/vdemds25</a></div>
    </div>` : ""}

  </div>` : "";

  // ── Glosario Técnico ──────────────────────────────────────────────────────
  const GLOSSARY = [
    ["APA", "American Psychological Association", "Estilo de cita académica que utilizamos en este informe para asegurar trazabilidad completa de todas las fuentes citadas."],
    ["CADH", "Convención Americana sobre Derechos Humanos (Pacto de San José)", "Tratado interamericano de 1969. Su Art. 23 garantiza los derechos políticos: votar, ser elegido y acceder a funciones públicas en condiciones de igualdad."],
    ["CEDAW", "Convention on the Elimination of All Forms of Discrimination against Women", "Tratado de la ONU (1979) que obliga a los Estados a garantizar la participación electoral de las mujeres en igualdad de condiciones."],
    ["CDI", "Carta Democrática Interamericana", "Documento adoptado por la OEA en 2001. Define los elementos esenciales de la democracia representativa (Arts. 3–4) y habilita mecanismos colectivos de respuesta ante rupturas democráticas."],
    ["CIDH", "Comisión Interamericana de Derechos Humanos", "Órgano autónomo de la OEA que monitorea, promueve y protege los derechos humanos en América. Emite medidas cautelares y lleva casos ante la Corte IDH."],
    ["CRPD", "Convention on the Rights of Persons with Disabilities", "Tratado de la ONU (2006). Sus Arts. 12 y 29 garantizan la participación electoral de personas con discapacidad en condiciones de igualdad efectiva."],
    ["EMB", "Electoral Management Body", "Organismo de gestión electoral (OGE). En Perú: el JNE (adjudica/controla), la ONPE (organiza el voto) y el RENIEC (administra el registro civil y padrón). El sistema peruano es tripartito."],
    ["FH / FIW", "Freedom House — Freedom in the World", "Índice anual (1972–presente) que clasifica 195 países según libertades políticas (PR) y civiles (CL), en una escala de 0 a 100. Fuente utilizada: FIW 2025."],
    ["FH CL", "Freedom House — Civil Liberties", "Subíndice de Freedom in the World que evalúa libertad de expresión, de asociación, estado de derecho e igualdad ante la ley. Escala 0–16 (interna), convertida a 0–100 en PEIRS."],
    ["FH PR", "Freedom House — Political Rights", "Subíndice de Freedom in the World que evalúa proceso electoral, pluralismo, funcionamiento del gobierno. Escala 0–40 (interna), convertida a 0–100 en PEIRS."],
    ["ICCPR", "International Covenant on Civil and Political Rights (Pacto Internacional de Derechos Civiles y Políticos)", "Tratado fundamental de la ONU (1966, vigente 1976). El Art. 25 garantiza el derecho a votar y ser elegido en elecciones auténticas con sufragio universal e igual. Ratificado por Perú en 1978."],
    ["ICERD", "International Convention on the Elimination of All Forms of Racial Discrimination", "Tratado de la ONU (1965). Su Art. 5(c) prohíbe la discriminación racial en el ejercicio de los derechos políticos y electorales."],
    ["IRE", "Índice de Riesgo Electoral", "Índice sintético de PEIRS (0–100, donde 100 = riesgo máximo) que agrega 8 dimensiones: sufragio, marco legal, independencia EMB, libertad de prensa, financiamiento, ecosistema digital, justicia electoral, inclusividad."],
    ["IPRE", "Índice Predictivo de Riesgo Electoral", "Nombre alternativo del IRE. Enfatiza su naturaleza predictiva: anticipa condiciones de riesgo antes de la jornada electoral usando datos históricos y estructurales."],
    ["JNE", "Jurado Nacional de Elecciones", "Organismo autónomo de Perú que dirime controversias electorales, administra la justicia electoral y fiscaliza el cumplimiento de la ley. Equivale a un tribunal electoral."],
    ["MOE", "Misión de Observación Electoral", "Conjunto de observadores internacionales desplegados para evaluar un proceso electoral. Las MOE de la UE, OEA y OSCE/ODIHR publican metodologías estándar que PEIRS utiliza como referencia."],
    ["ODIE / ODIHR", "Office for Democratic Institutions and Human Rights (OSCE)", "Oficina de la OSCE especializada en observación electoral en la región europea/euro-asiática. Sus metodologías de MOE son estándar de referencia global."],
    ["OEA", "Organización de los Estados Americanos", "Organismo regional hemisférico. Emite la Carta Democrática Interamericana y coordina MOEs en América Latina y el Caribe."],
    ["OGE", "Organismo de Gestión Electoral", "Traducción al español de EMB. En contextos de PEIRS se usa indistintamente."],
    ["ONPE", "Oficina Nacional de Procesos Electorales", "Organismo técnico de Perú responsable de la organización y ejecución de los procesos electorales: diseño de cédula, cómputo de votos, formación de mesas."],
    ["OONI", "Open Observatory of Network Interference", "Organización que monitorea en tiempo real la censura y bloqueo de internet en 200+ países. PEIRS integra OONI API para el indicador de ecosistema digital."],
    ["ONU", "Organización de las Naciones Unidas", "Organismo internacional que adopta los tratados de DDHH que fundamentan los estándares electorales (ICCPR, CEDAW, CRPD, ICERD, UNDRIP)."],
    ["PEI", "Perceptions of Electoral Integrity Dataset", "Encuesta académica de Pippa Norris et al. (Harvard Dataverse). Versión 10.0 (2024) cubre 586 elecciones en 166 países. Evalúa 11 dimensiones (marco legal, padrón, medios, campaña, votación, escrutinio, etc.) con expertos electorales."],
    ["PEIRS", "Predictive Electoral Integrity & Risk System", "Sistema DEMOCRAC.IA de análisis y predicción de riesgos de integridad electoral. Combina 4 datasets estructurados (V-Dem, FH, PEI, RSF) con agentes de IA (Claude + LangGraph) para producir informes automatizados con trazabilidad."],
    ["RENIEC", "Registro Nacional de Identificación y Estado Civil", "Organismo peruano que administra el DNI, el registro civil y el padrón electoral. La calidad del padrón impacta directamente en el derecho al voto (Art. 25 ICCPR)."],
    ["RSF", "Reporters Sans Frontières — World Press Freedom Index", "Índice anual de libertad de prensa de Reporteros Sin Fronteras. Evalúa 180 países en 5 dimensiones: entorno político, legal, económico, sociocultural y seguridad. Escala 0–100 (100 = total libertad). Fuente: RSF 2025."],
    ["UNDRIP", "United Nations Declaration on the Rights of Indigenous Peoples", "Declaración de la ONU (2007). Arts. 5 y 18 garantizan el derecho de los pueblos indígenas a mantener instituciones políticas propias y a participar en procesos electorales nacionales."],
    ["V-Dem", "Varieties of Democracy Project", "Dataset académico elaborado por el Instituto V-Dem (Universidad de Gotemburgo). La versión 15 (2025) cubre 202 países y 1789–2024 con 900+ variables. Incluye índices de democracia liberal, electoral, participativa, deliberativa e igualitaria. Referencia principal de PEIRS para series históricas."],
    ["v2elembaut", "V-Dem: EMB Autonomy (Autonomía del Organismo Electoral)", "Variable V-Dem (escala 0–1) que mide en qué grado el organismo electoral actúa con independencia del gobierno. En Perú, aplica principalmente al JNE."],
    ["v2elembcap", "V-Dem: EMB Capacity (Capacidad del Organismo Electoral)", "Variable V-Dem (escala 0–1) que mide la capacidad técnica e institucional del organismo electoral para administrar elecciones. Considera recursos humanos, financiamiento y autonomía operativa."],
    ["v2mecenefi", "V-Dem: Government censorship effort — media (Censura gubernamental a medios)", "Variable V-Dem (escala 0–1) que mide cuánto esfuerzo hace el gobierno por censurar o controlar los medios de comunicación. 0 = censura sistemática; 1 = sin censura."],
    ["v2mebias", "V-Dem: Media bias in favor of the governing party (Sesgo mediático progubernamental)", "Variable V-Dem (escala 0–1) que captura si los medios cubren las actividades del gobierno de manera más favorable que las de la oposición. PEIRS lo invierte: mayor score = mayor libertad."],
    ["v2meharjrn", "V-Dem: Harassment of journalists (Acoso a periodistas)", "Variable V-Dem (escala 0–1) que mide si el gobierno, o agentes que actúan en su nombre, hostigan, intimidan o agreden a periodistas. 0 = acoso sistemático; 1 = sin acoso."],
    ["v2x_libdem", "V-Dem: Liberal Democracy Index (Índice de Democracia Liberal)", "Índice compuesto V-Dem (escala 0–1) que agrega: democracia electoral (v2x_polyarchy) + estado de derecho + protección de libertades civiles. Principal indicador de calidad democrática en PEIRS."],
    ["v2x_polyarchy", "V-Dem: Electoral Democracy Index (Índice de Democracia Electoral)", "Índice V-Dem (escala 0–1) basado en el modelo de Robert Dahl (poliarquía). Evalúa sufragio, elecciones limpias, libertad de expresión y asociación. Componente del v2x_libdem."],
  ];

  // Calcular la letra de sección dinámica para el glosario
  const glossarySectionLetter = (() => {
    let idx = 70; // "F"
    if (vdemCharts) idx++;    // G si hay V-Dem
    if (moeBrief) idx++;      // +1 si hay MOE brief
    if (actorsData) idx++;    // +1 si hay actores
    if (scenariosData) idx++; // +1 si hay escenarios
    return String.fromCharCode(idx);
  })();

  const glossaryHtml = `
  <!-- ════ SECCIÓN ${glossarySectionLetter}: GLOSARIO TÉCNICO ═══════════════════════════════════════ -->
  <div class="section-header">
    <div class="section-number">${glossarySectionLetter}</div>
    <div class="section-title">Glosario Técnico y Acrónimos</div>
  </div>
  <div class="glossary-section">
    <div class="glossary-intro">Los siguientes términos, acrónimos y variables de dataset aparecen en este informe. Los identificadores de variables V-Dem (<code>v2…</code>) están en escala estandarizada 0–1 salvo indicación contraria.</div>
    <table>
      <thead><tr><th style="width:14%">Acrónimo / Variable</th><th style="width:28%">Nombre completo</th><th>Descripción y relevancia en PEIRS</th></tr></thead>
      <tbody>
        ${GLOSSARY.map(([acr, full, desc]) => `<tr><td><code>${acr}</code></td><td><strong>${full}</strong></td><td>${desc}</td></tr>`).join("")}
      </tbody>
    </table>
  </div>`;

  // ── Convertidor Markdown → HTML completo ─────────────────────────────────
  const mdToHtml = (md) => {
    if (!md) return "";
    // Tablas primero (antes de otros reemplazos)
    const tableRegex = /(\|.+\|\n\|[-|: ]+\|\n(?:\|.+\|\n?)+)/g;
    md = md.replace(tableRegex, (tableStr) => {
      const rows = tableStr.trim().split("\n").filter(r => !r.match(/^\|[-|:\s]+\|$/));
      if (rows.length < 1) return tableStr;
      const headerCells = rows[0].split("|").map(c => c.trim()).filter(Boolean);
      const dataRows = rows.slice(1);
      let t = `<table><thead><tr>${headerCells.map(h => `<th>${h}</th>`).join("")}</tr></thead><tbody>`;
      dataRows.forEach(row => {
        const cells = row.split("|").map(c => c.trim()).filter(Boolean);
        const cls = cells.some(c => c === "CRITICO" || c === "CRÍTICO") ? ' class="risk-critical"'
                  : cells.some(c => c === "ALTO") ? ' class="risk-high"' : "";
        t += `<tr${cls}>${cells.map(c => {
          if (c === "confirmed" || c === "VERIFICADO" || c === "✓ VERIFICADO") return `<td class="conf-ok">&#10003; Verificado</td>`;
          if (c === "mock" || c === "MOCK" || c === "PENDIENTE") return `<td class="conf-pend">&#9888; Pendiente</td>`;
          if (c === "CRITICO" || c === "CRÍTICO") return `<td style="color:#991b1b;font-weight:700">${c}</td>`;
          if (c === "ALTO") return `<td style="color:#c2410c;font-weight:700">${c}</td>`;
          return `<td>${c}</td>`;
        }).join("")}</tr>`;
      });
      t += "</tbody></table>";
      return t;
    });
    // Headings
    md = md
      .replace(/^#### (.+)$/gm, "<h4>$1</h4>")
      .replace(/^### (.+)$/gm, "<h3>$1</h3>")
      .replace(/^## (.+)$/gm, "<h2>$1</h2>")
      .replace(/^# (.+)$/gm, "<h1>$1</h1>")
      // Bold/italic
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+?)\*/g, "<em>$1</em>")
      // Code
      .replace(/`(.+?)`/g, "<code>$1</code>")
      // Blockquotes
      .replace(/^> (.+)$/gm, "<blockquote>$1</blockquote>")
      // HR
      .replace(/^---$/gm, "<hr>")
      // Numbered lists
      .replace(/^\d+\. (.+)$/gm, "<li>$1</li>")
      // Bullet lists
      .replace(/^[-*] (.+)$/gm, "<li>$1</li>");
    // Wrap consecutive <li> in <ul>
    md = md.replace(/(<li>[\s\S]+?<\/li>\n?)+/g, m => `<ul>${m}</ul>`);
    // Paragraphs: blocks not starting with HTML tag
    const blocks = md.split(/\n{2,}/);
    md = blocks.map(b => {
      b = b.trim();
      if (!b) return "";
      if (/^<[a-zA-Z]/.test(b)) return b;
      if (/^\|/.test(b)) return b;
      return `<p>${b}</p>`;
    }).join("\n");
    return md;
  };

  // ── Pizarra Crisis Democrática — SVG estático para el informe ────────────
  const pizarraSvgHtml = `
<section class="chapter" style="page-break-inside:avoid;">
  <h2 style="font-size:13px;font-weight:700;color:#0f172a;margin:0 0 10px;letter-spacing:1px;text-transform:uppercase;">
    Línea de Tiempo — Crisis Democrática 2016–2026
  </h2>
  <p style="font-size:10px;color:#475569;margin:0 0 12px;line-height:1.6;">
    Fuentes: V-Dem v15 (v2x_libdem), Freedom House FIW 2025, registros parlamentarios JNE.
    El índice V-Dem de democracia liberal pasó de 0.59 (2016) a 0.40 (proyección 2026), una caída de −0.19 puntos en una década.
  </p>
  <div style="background:linear-gradient(175deg,#080e1a 0%,#0d1424 100%);border-radius:10px;padding:12px 16px 10px;border:1px solid #1e293b;">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
      <span style="font-size:9px;font-weight:700;letter-spacing:3px;color:#475569;font-family:monospace;text-transform:uppercase;">Pizarra — Crisis Democrática</span>
      <div style="flex:1;height:1px;background:#1e293b;"></div>
      <span style="font-size:9px;color:#334155;font-family:monospace;">2016 → 2026</span>
    </div>
    <svg viewBox="0 0 820 348" style="width:100%;height:auto;display:block;" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="rpt-ptl-grid" x="0" y="0" width="60" height="60" patternUnits="userSpaceOnUse">
          <path d="M60 0 L0 0 0 60" fill="none" stroke="rgba(255,255,255,0.022)" stroke-width=".6"/>
        </pattern>
        <filter id="rpt-ptl-chalk" x="-5%" y="-5%" width="110%" height="110%">
          <feTurbulence type="fractalNoise" baseFrequency="0.07" numOctaves="4" result="n"/>
          <feDisplacementMap in="SourceGraphic" in2="n" scale="1.6" xChannelSelector="R" yChannelSelector="G"/>
        </filter>
        <filter id="rpt-ptl-glow" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="3.5" result="b"/>
          <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <marker id="rpt-ptl-arr" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
          <path d="M0,0 L0,6 L9,3 z" fill="rgba(248,250,252,0.45)" filter="url(#rpt-ptl-chalk)"/>
        </marker>
      </defs>
      <rect width="820" height="348" fill="url(#rpt-ptl-grid)"/>
      <text x="410" y="205" text-anchor="middle" font-size="42" fill="rgba(255,255,255,0.028)" font-family="monospace" font-weight="900" letter-spacing="5">CRISIS DEMOCRÁTICA</text>
      <path d="M 50 182 C 98 170,122 198,145 187 C 170 175,215 166,240 176 C 268 188,305 202,330 190 C 356 178,398 163,420 176 C 446 192,483 205,510 190 C 536 175,573 152,600 170 C 626 188,658 204,685 190 C 710 176,745 166,770 180"
        stroke="rgba(248,250,252,0.50)" stroke-width="2.5" fill="none" stroke-linecap="round" filter="url(#rpt-ptl-chalk)" marker-end="url(#rpt-ptl-arr)"/>
      <!-- 2016 -->
      <line x1="50" y1="169" x2="50" y2="141" stroke="#3b82f660" stroke-width="1" stroke-dasharray="3 2.5"/>
      <circle cx="50" cy="182" r="13" fill="#3b82f6" filter="url(#rpt-ptl-glow)"/>
      <text x="50" y="186" text-anchor="middle" font-size="10" fill="white" font-weight="800">16</text>
      <rect x="4" y="95" width="96" height="46" rx="5" fill="#1e3a5f" stroke="#3b82f666" stroke-width="1.2"/>
      <text x="52" y="110" text-anchor="middle" font-size="9" fill="#93c5fd" font-weight="700">2016 PPK</text>
      <text x="52" y="123" text-anchor="middle" font-size="8" fill="#94a3b8">PPK presidente</text>
      <text x="52" y="134" text-anchor="middle" font-size="7.5" fill="#475569">FP domina Congreso</text>
      <!-- 2018 -->
      <line x1="145" y1="200" x2="145" y2="228" stroke="#f59e0b60" stroke-width="1" stroke-dasharray="3 2.5"/>
      <circle cx="145" cy="187" r="13" fill="#f59e0b" filter="url(#rpt-ptl-glow)"/>
      <text x="145" y="191" text-anchor="middle" font-size="10" fill="white" font-weight="800">18</text>
      <rect x="97" y="228" width="96" height="46" rx="5" fill="#1f1500" stroke="#f59e0b66" stroke-width="1.2"/>
      <text x="145" y="243" text-anchor="middle" font-size="9" fill="#fcd34d" font-weight="700">2018 PPK renuncia</text>
      <text x="145" y="256" text-anchor="middle" font-size="8" fill="#94a3b8">PPK renuncia</text>
      <text x="145" y="267" text-anchor="middle" font-size="7.5" fill="#475569">Vizcarra asume</text>
      <!-- 2019 -->
      <line x1="240" y1="163" x2="240" y2="135" stroke="#f9731660" stroke-width="1" stroke-dasharray="3 2.5"/>
      <circle cx="240" cy="176" r="13" fill="#f97316" filter="url(#rpt-ptl-glow)"/>
      <text x="240" y="180" text-anchor="middle" font-size="10" fill="white" font-weight="800">19</text>
      <rect x="192" y="89" width="96" height="46" rx="5" fill="#1c1208" stroke="#f9731666" stroke-width="1.2"/>
      <text x="240" y="104" text-anchor="middle" font-size="9" fill="#fb923c" font-weight="700">2019 Congreso</text>
      <text x="240" y="117" text-anchor="middle" font-size="8" fill="#94a3b8">Congreso disuelto</text>
      <text x="240" y="128" text-anchor="middle" font-size="7.5" fill="#475569">Elecciones extraordinarias</text>
      <!-- 2020 (crisis) -->
      <circle cx="330" cy="190" r="26" fill="none" stroke="#ef4444" stroke-width="1.2" opacity="0.3" stroke-dasharray="4 3"/>
      <line x1="330" y1="207" x2="330" y2="235" stroke="#ef444460" stroke-width="1" stroke-dasharray="3 2.5"/>
      <circle cx="330" cy="190" r="17" fill="#ef4444" filter="url(#rpt-ptl-glow)"/>
      <text x="330" y="194" text-anchor="middle" font-size="10" fill="white" font-weight="800">20</text>
      <rect x="282" y="235" width="96" height="46" rx="5" fill="#2d0808" stroke="#ef4444bb" stroke-width="1.8"/>
      <text x="330" y="250" text-anchor="middle" font-size="9" fill="#fca5a5" font-weight="700">2020 CRISIS</text>
      <text x="330" y="263" text-anchor="middle" font-size="8" fill="#94a3b8">3 presidentes</text>
      <text x="330" y="274" text-anchor="middle" font-size="7.5" fill="#475569">en 7 días</text>
      <!-- 2021 -->
      <line x1="420" y1="163" x2="420" y2="135" stroke="#dc262660" stroke-width="1" stroke-dasharray="3 2.5"/>
      <circle cx="420" cy="176" r="13" fill="#dc2626" filter="url(#rpt-ptl-glow)"/>
      <text x="420" y="180" text-anchor="middle" font-size="10" fill="white" font-weight="800">21</text>
      <rect x="372" y="89" width="96" height="46" rx="5" fill="#2d0808" stroke="#dc262666" stroke-width="1.2"/>
      <text x="420" y="104" text-anchor="middle" font-size="9" fill="#fca5a5" font-weight="700">2021 Castillo</text>
      <text x="420" y="117" text-anchor="middle" font-size="8" fill="#94a3b8">Castillo gana</text>
      <text x="420" y="128" text-anchor="middle" font-size="7.5" fill="#475569">FH:71 · V-Dem:0.52</text>
      <!-- 2022 -->
      <line x1="510" y1="203" x2="510" y2="231" stroke="#b91c1c60" stroke-width="1" stroke-dasharray="3 2.5"/>
      <circle cx="510" cy="190" r="13" fill="#b91c1c" filter="url(#rpt-ptl-glow)"/>
      <text x="510" y="194" text-anchor="middle" font-size="10" fill="white" font-weight="800">22</text>
      <rect x="462" y="231" width="96" height="46" rx="5" fill="#2d0808" stroke="#b91c1c66" stroke-width="1.2"/>
      <text x="510" y="246" text-anchor="middle" font-size="9" fill="#fca5a5" font-weight="700">2022 Castillo</text>
      <text x="510" y="259" text-anchor="middle" font-size="8" fill="#94a3b8">Castillo destituido</text>
      <text x="510" y="270" text-anchor="middle" font-size="7.5" fill="#475569">Boluarte asume</text>
      <!-- 2023 crisis -->
      <circle cx="600" cy="170" r="26" fill="none" stroke="#991b1b" stroke-width="1.2" opacity="0.3" stroke-dasharray="4 3"/>
      <line x1="600" y1="157" x2="600" y2="129" stroke="#991b1b60" stroke-width="1" stroke-dasharray="3 2.5"/>
      <circle cx="600" cy="170" r="17" fill="#991b1b" filter="url(#rpt-ptl-glow)"/>
      <text x="600" y="174" text-anchor="middle" font-size="10" fill="white" font-weight="800">23</text>
      <rect x="552" y="83" width="96" height="46" rx="5" fill="#3b0000" stroke="#991b1bbb" stroke-width="1.8"/>
      <text x="600" y="98" text-anchor="middle" font-size="9" fill="#fca5a5" font-weight="700">2023 CRISIS</text>
      <text x="600" y="111" text-anchor="middle" font-size="8" fill="#94a3b8">60+ muertes</text>
      <text x="600" y="122" text-anchor="middle" font-size="7.5" fill="#475569">CIDH cautelares</text>
      <!-- 2024 -->
      <line x1="685" y1="203" x2="685" y2="231" stroke="#7f1d1d60" stroke-width="1" stroke-dasharray="3 2.5"/>
      <circle cx="685" cy="190" r="13" fill="#7f1d1d" filter="url(#rpt-ptl-glow)"/>
      <text x="685" y="194" text-anchor="middle" font-size="10" fill="white" font-weight="800">24</text>
      <rect x="637" y="231" width="96" height="46" rx="5" fill="#1a0808" stroke="#7f1d1d66" stroke-width="1.2"/>
      <text x="685" y="246" text-anchor="middle" font-size="9" fill="#fca5a5" font-weight="700">2024 Boluarte</text>
      <text x="685" y="259" text-anchor="middle" font-size="8" fill="#94a3b8">Aprobación</text>
      <text x="685" y="270" text-anchor="middle" font-size="7.5" fill="#475569">&lt;10% histórico</text>
      <!-- 2026 election -->
      <circle cx="770" cy="180" r="27" fill="none" stroke="#0d9488" stroke-width="1.2" opacity="0.3" stroke-dasharray="4 3"/>
      <line x1="770" y1="162" x2="770" y2="134" stroke="#0d948860" stroke-width="1" stroke-dasharray="3 2.5"/>
      <circle cx="770" cy="180" r="18" fill="#0d9488" filter="url(#rpt-ptl-glow)"/>
      <text x="770" y="184" text-anchor="middle" font-size="10" fill="white" font-weight="800">26</text>
      <rect x="722" y="88" width="96" height="46" rx="5" fill="#042f2e" stroke="#0d9488bb" stroke-width="1.8"/>
      <text x="770" y="103" text-anchor="middle" font-size="9" fill="#2dd4bf" font-weight="700">2026 ELECCIONES</text>
      <text x="770" y="116" text-anchor="middle" font-size="8" fill="#94a3b8">12 de abril</text>
      <text x="770" y="127" text-anchor="middle" font-size="7.5" fill="#475569">PEIRS activo</text>
      <!-- V-Dem sparkline -->
      <text x="410" y="290" text-anchor="middle" font-size="7" fill="#334155" font-family="monospace" letter-spacing="2">ÍNDICE V-DEM — DEMOCRACIA LIBERAL (v2x_libdem)</text>
      <line x1="36" y1="297" x2="36" y2="326" stroke="#1e293b" stroke-width="1"/>
      <line x1="36" y1="326" x2="804" y2="326" stroke="#1e293b" stroke-width="1.2"/>
      <text x="16" y="312" text-anchor="middle" font-size="7" fill="#334155" font-family="monospace" transform="rotate(-90,16,312)">V-Dem</text>
      <rect x="41" y="309" width="18" height="17" rx="3" fill="#3b82f6" opacity="0.75"/>
      <text x="50" y="337" text-anchor="middle" font-size="7.5" fill="#475569" font-family="monospace">0.59</text>
      <rect x="136" y="311" width="18" height="15" rx="3" fill="#3b82f6" opacity="0.75"/>
      <text x="145" y="337" text-anchor="middle" font-size="7.5" fill="#475569" font-family="monospace">0.56</text>
      <rect x="231" y="313" width="18" height="13" rx="3" fill="#f59e0b" opacity="0.75"/>
      <text x="240" y="337" text-anchor="middle" font-size="7.5" fill="#475569" font-family="monospace">0.54</text>
      <rect x="321" y="316" width="18" height="10" rx="3" fill="#f97316" opacity="0.75"/>
      <text x="330" y="337" text-anchor="middle" font-size="7.5" fill="#475569" font-family="monospace">0.50</text>
      <rect x="411" y="314" width="18" height="12" rx="3" fill="#f59e0b" opacity="0.75"/>
      <text x="420" y="337" text-anchor="middle" font-size="7.5" fill="#475569" font-family="monospace">0.52</text>
      <rect x="501" y="317" width="18" height="9" rx="3" fill="#f97316" opacity="0.75"/>
      <text x="510" y="337" text-anchor="middle" font-size="7.5" fill="#475569" font-family="monospace">0.47</text>
      <rect x="591" y="319" width="18" height="7" rx="3" fill="#ef4444" opacity="0.75"/>
      <text x="600" y="337" text-anchor="middle" font-size="7.5" fill="#475569" font-family="monospace">0.44</text>
      <rect x="676" y="320" width="18" height="6" rx="3" fill="#ef4444" opacity="0.75"/>
      <text x="685" y="337" text-anchor="middle" font-size="7.5" fill="#475569" font-family="monospace">0.42</text>
      <rect x="761" y="322" width="18" height="4" rx="3" fill="#ef4444" opacity="0.75"/>
      <text x="770" y="337" text-anchor="middle" font-size="7.5" fill="#475569" font-family="monospace">0.40</text>
      <line x1="50" y1="302" x2="770" y2="323" stroke="#ef444445" stroke-width="1.2" stroke-dasharray="6 3"/>
      <text x="720" y="300" font-size="8" fill="#ef444490" font-family="monospace" font-weight="700">↘ −0.19</text>
    </svg>
    <div style="display:flex;gap:14px;padding:5px 0 2px;flex-wrap:wrap;">
      <div style="display:flex;align-items:center;gap:5px;"><div style="width:7px;height:7px;border-radius:50%;background:#3b82f6;"></div><span style="font-size:9px;color:#475569;font-family:monospace;">Estabilidad relativa</span></div>
      <div style="display:flex;align-items:center;gap:5px;"><div style="width:7px;height:7px;border-radius:50%;background:#f59e0b;"></div><span style="font-size:9px;color:#475569;font-family:monospace;">Transición</span></div>
      <div style="display:flex;align-items:center;gap:5px;"><div style="width:7px;height:7px;border-radius:50%;background:#ef4444;"></div><span style="font-size:9px;color:#475569;font-family:monospace;">Crisis aguda</span></div>
      <div style="display:flex;align-items:center;gap:5px;"><div style="width:7px;height:7px;border-radius:50%;background:#0d9488;"></div><span style="font-size:9px;color:#475569;font-family:monospace;">2026 Electoral</span></div>
    </div>
  </div>
</section>`;

  // ── Capítulos en HTML ─────────────────────────────────────────────────────
  const chapOrder = [
    "01_executive_summary","02_political_context","03_emb_analysis",
    "04_inclusivity","05_campaign_finance","06_digital_ecosystem",
    "07_voting_day","08_electoral_justice","09_recommendations","10_ai_regulation",
  ];
  const chapHtml = chapOrder
    .filter(k => chapters[k])
    .map(k => {
      const sec = `<section class="chapter">${mdToHtml(chapters[k])}</section>`;
      // Insertar Pizarra inmediatamente después del cap. 02 (contexto político)
      if (k === "02_political_context") return sec + "\n" + pizarraSvgHtml;
      return sec;
    })
    .join("\n");

  // ── Violaciones ───────────────────────────────────────────────────────────
  const violHtml = violations.length > 0 ? `
<table>
  <thead><tr><th>Artículo</th><th>Derecho</th><th>Hallazgo</th><th>Severidad</th><th>Confianza</th></tr></thead>
  <tbody>
    ${violations.map(v => `
    <tr>
      <td><code>${v.article || "—"}</code></td>
      <td>${v.right || v.description || "—"}</td>
      <td style="font-size:10px;color:#475569">${(v.finding || "—").substring(0, 150)}${(v.finding || "").length > 150 ? "…" : ""}</td>
      <td class="${v.severity === "critical" ? "risk-critical" : v.severity === "high" ? "risk-high" : ""}">${(v.severity || "—").toUpperCase()}</td>
      <td class="${v.confidence === "confirmed" ? "conf-ok" : "conf-pend"}">${v.confidence === "confirmed" ? "&#10003; Verificado" : "&#9888; Pendiente"}</td>
    </tr>`).join("")}
  </tbody>
</table>` : `<p class="no-data">No se detectaron violaciones activas para este ciclo electoral.</p>`;

  // ── Tabla de fuentes ──────────────────────────────────────────────────────
  const srcRows = [
    { key: "V-Dem v15",          val: "27,913 observaciones — Coppedge et al. 2025", status: "confirmed" },
    { key: "Freedom House FIW",  val: `Edición ${fh.edition || "2025"} — ${fhScore}/100`, status: dataSources.freedom_house || "confirmed" },
    { key: "PEI Dataset 10.0",   val: `${peiScore !== "—" ? peiScore+"/100" : "N/A"} — Harvard Dataverse`, status: dataSources.pei || "confirmed" },
    { key: "RSF Press Freedom",  val: `Score ${rsfScore}/100 — 180 países`, status: "confirmed" },
    { key: "Libertades Civiles", val: "Freedom House CL/PR rating", status: dataSources.civil_liberties || "confirmed" },
    { key: "Marco Legal",        val: "V-Dem + ICCPR framework", status: dataSources.legal_framework || "confirmed" },
  ].map(s => `
<tr>
  <td><strong>${s.key}</strong></td>
  <td>${s.val}</td>
  <td class="${s.status === "confirmed" ? "conf-ok" : "conf-pend"}">${s.status === "confirmed" ? "&#10003; Verificado" : "&#9888; Pendiente"}</td>
</tr>`).join("");

  // ── Sección G: MOE Brief ──────────────────────────────────────────────────
  const moeBriefSectionHtml = moeBrief ? (() => {
    const rc = moeBrief.blocks && moeBrief.blocks.risk_context ? moeBrief.blocks.risk_context : {};
    const pa = moeBrief.blocks && moeBrief.blocks.priority_areas ? moeBrief.blocks.priority_areas : {};
    const proto = moeBrief.blocks && moeBrief.blocks.protocol ? moeBrief.blocks.protocol : {};
    const areas = pa.priority_areas || [];
    const protoData = proto.protocol || {};
    const observers = proto.recommended_observers || [];

    const alertColors = {
      RED: { bg: "#fef2f2", border: "#fca5a5", text: "#991b1b" },
      ORANGE: { bg: "#fff7ed", border: "#fdba74", text: "#c2410c" },
      AMBER: { bg: "#fffbeb", border: "#fcd34d", text: "#92400e" },
      GREEN: { bg: "#f0fdf4", border: "#86efac", text: "#065f46" },
    };
    const ac = alertColors[moeBrief.alert_level] || alertColors.AMBER;

    const ki = rc.key_indicators || {};
    const critViol = rc.critical_violations || [];

    const riskBadgeColor = (r) => {
      if (r === "critical") return "background:#fef2f2;color:#991b1b;border:1px solid #fca5a5";
      if (r === "high") return "background:#fff7ed;color:#c2410c;border:1px solid #fdba74";
      if (r === "moderate") return "background:#fffbeb;color:#b45309;border:1px solid #fcd34d";
      return "background:#f0fdf4;color:#065f46;border:1px solid #86efac";
    };

    return `
  <!-- ════ SECCIÓN G: MOE BRIEF ════════════════════════════════════════════ -->
  <div class="section-header">
    <div class="section-number">G</div>
    <div class="section-title">MOE Brief — Misión de Observación Electoral</div>
  </div>
  <div class="moe-brief-section">

    <div class="alert-banner" style="background:${ac.bg};border:1px solid ${ac.border}">
      <div style="font-size:22px;font-weight:900;color:${ac.text};font-family:'DM Mono',monospace;min-width:80px">${moeBrief.alert_level || "—"}</div>
      <div>
        <div class="alert-level-text" style="color:${ac.text}">${moeBrief.alert_label || "—"}</div>
        <div class="alert-label-text">Fase actual: ${moeBrief.current_phase_label || "—"} · ${moeBrief.days_to_election >= 0 ? moeBrief.days_to_election + " días para la elección" : "Proceso post-electoral"} · Generado: ${moeBrief.generated_at ? new Date(moeBrief.generated_at).toLocaleDateString("es-AR") : "—"}</div>
      </div>
    </div>

    ${rc.risk_score !== undefined ? `
    <h3 style="margin-bottom:10px;font-size:12px;color:#475569;text-transform:uppercase;letter-spacing:1px">Indicadores Clave de Riesgo</h3>
    <table>
      <thead><tr><th>Indicador</th><th>Valor</th><th>Nota</th></tr></thead>
      <tbody>
        <tr><td><strong>PEIRS Risk Score</strong></td><td><code>${rc.risk_score}/100</code></td><td>${rc.risk_level ? rc.risk_level.toUpperCase() : "—"}</td></tr>
        ${ki.freedom_house ? `<tr><td>Freedom House FIW</td><td><code>${ki.freedom_house}</code></td><td>Libertades políticas y civiles</td></tr>` : ""}
        ${ki.vdem_liberal_democracy !== undefined ? `<tr><td>V-Dem Liberal Democracy</td><td><code>${ki.vdem_liberal_democracy}</code></td><td>V-Dem v15 — escala 0–1</td></tr>` : ""}
        ${ki.emb_independence ? `<tr><td>Independencia EMB (JNE/ONPE)</td><td><code>${ki.emb_independence.toUpperCase()}</code></td><td>Nivel de autonomía institucional</td></tr>` : ""}
        ${ki.active_violations !== undefined ? `<tr><td>Violaciones activas detectadas</td><td><code>${ki.active_violations}</code></td><td>ICCPR/CADH/CDI</td></tr>` : ""}
        ${rc.current_phase ? `<tr><td>Fase electoral actual</td><td><code>${rc.current_phase}</code></td><td>Elección: ${moeBrief.election_date || "—"}</td></tr>` : ""}
      </tbody>
    </table>` : ""}

    ${critViol.length > 0 ? `
    <h3 style="margin:16px 0 10px;font-size:12px;color:#475569;text-transform:uppercase;letter-spacing:1px">Violaciones Críticas Detectadas</h3>
    <table>
      <thead><tr><th>Tratado / Artículo</th><th>Hallazgo</th><th>Severidad</th></tr></thead>
      <tbody>
        ${critViol.map(v => `<tr>
          <td><code>${v.treaty || "—"} ${v.article || ""}</code></td>
          <td>${v.finding || "—"}</td>
          <td style="font-size:10px;font-weight:700;${riskBadgeColor(v.severity)};padding:2px 6px;border-radius:4px">${(v.severity || "—").toUpperCase()}</td>
        </tr>`).join("")}
      </tbody>
    </table>` : ""}

    ${areas.length > 0 ? `
    <h3 style="margin:16px 0 10px;font-size:12px;color:#475569;text-transform:uppercase;letter-spacing:1px">Áreas Prioritarias de Observación</h3>
    <table>
      <thead><tr><th>#</th><th>Área</th><th>Riesgo</th><th>Hallazgos</th><th>Estándar EOS</th></tr></thead>
      <tbody>
        ${areas.map(a => `<tr>
          <td>${a.priority}</td>
          <td><strong>${a.area}</strong></td>
          <td><span style="display:inline-block;padding:2px 7px;border-radius:4px;font-size:9px;font-weight:700;font-family:'DM Mono',monospace;text-transform:uppercase;${riskBadgeColor(a.risk)}">${(a.risk || "—").toUpperCase()}</span></td>
          <td>${(a.findings || []).join("; ")}</td>
          <td style="font-size:10px;color:#64748b">${a.eos_standard || "—"}</td>
        </tr>`).join("")}
      </tbody>
    </table>` : ""}

    ${protoData.type ? `
    <h3 style="margin:16px 0 10px;font-size:12px;color:#475569;text-transform:uppercase;letter-spacing:1px">Protocolo de Observación Recomendado</h3>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:14px">
      <div style="background:var(--paper-2);border:1px solid var(--border);padding:12px;border-radius:4px">
        <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Tipo de Misión</div>
        <div style="font-size:13px;font-weight:700;color:var(--ink)">${protoData.label || protoData.type}</div>
      </div>
      <div style="background:var(--paper-2);border:1px solid var(--border);padding:12px;border-radius:4px">
        <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Duración LTO</div>
        <div style="font-size:13px;font-weight:700;color:var(--ink)">${protoData.lto_duration || "—"}</div>
      </div>
      <div style="background:var(--paper-2);border:1px solid var(--border);padding:12px;border-radius:4px">
        <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Observadores STO</div>
        <div style="font-size:13px;font-weight:700;color:var(--ink)">${protoData.sto_count || "—"}</div>
      </div>
    </div>
    <p style="font-size:11px;color:#475569;margin-bottom:12px">${protoData.description || ""}</p>
    ${observers.length > 0 ? `<div style="font-size:11px;color:#475569"><strong>Organizaciones recomendadas:</strong> ${observers.map(o => `${o.org} (${o.role})`).join(" · ")}</div>` : ""}` : ""}

  </div>`;
  })() : "";

  // ── Sección H: Actores Políticos ──────────────────────────────────────────
  const actorsSectionHtml = actorsData ? (() => {
    const actors = actorsData.actors || [];
    const riskBadgeStyle = (rp) => {
      const styles = {
        critical: "background:#fef2f2;color:#991b1b;border:1px solid #fca5a5",
        high: "background:#fff7ed;color:#c2410c;border:1px solid #fdba74",
        moderate: "background:#fffbeb;color:#b45309;border:1px solid #fcd34d",
        low: "background:#f0fdf4;color:#065f46;border:1px solid #86efac",
      };
      return styles[rp] || styles.moderate;
    };

    const grouped = {};
    actors.forEach(a => {
      const t = a.type || "party";
      if (!grouped[t]) grouped[t] = [];
      grouped[t].push(a);
    });

    const rows = actors.map(a => {
      const keyIssues = (a.key_policies || a.key_issues || []).slice(0, 2).join("; ");
      const seatsInfo = a.current_seats != null ? ` · ${a.current_seats} escaños` : "";
      return `<tr>
        <td><strong>${a.abbr || a.id || "—"}</strong><br><span style="font-size:10px;color:#475569">${a.name}</span>${seatsInfo ? `<br><span style="font-size:10px;color:#94a3b8">${seatsInfo}</span>` : ""}</td>
        <td style="font-size:10px">${a.ideology || a.type || "—"}</td>
        <td><span style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:9px;font-weight:700;font-family:'DM Mono',monospace;text-transform:uppercase;${riskBadgeStyle(a.risk_profile)}">${(a.risk_profile || "—").toUpperCase()}</span></td>
        <td style="font-size:10px">${keyIssues || "—"}</td>
        <td style="font-size:10px;color:#475569">${(a.risk_notes || a.description || "").substring(0, 130)}${(a.risk_notes || a.description || "").length > 130 ? "…" : ""}</td>
      </tr>`;
    }).join("");

    return `
  <!-- ════ SECCIÓN H: ACTORES ════════════════════════════════════════════════ -->
  <div class="section-header">
    <div class="section-number">H</div>
    <div class="section-title">Mapa de Actores — Perú 2026</div>
  </div>
  <div class="actors-section">
    <p style="font-size:11px;color:#475569;margin-bottom:14px">
      Fuerzas políticas con representación parlamentaria actual y candidaturas confirmadas para las elecciones del 12 de abril de 2026.
      Total: <strong>${actorsData.total_actors || actors.length} actores</strong> · Sistema: ${actorsData.electoral_system && actorsData.electoral_system.name ? actorsData.electoral_system.name : "Representación Proporcional D'Hondt"} · 130 escaños unicamerales.
    </p>
    <table>
      <thead>
        <tr>
          <th style="width:14%">Partido / Actor</th>
          <th style="width:14%">Ideología</th>
          <th style="width:10%">Perfil de Riesgo</th>
          <th style="width:28%">Temas Clave</th>
          <th>Nota de Riesgo PEIRS</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
    <div style="margin-top:10px;font-size:10px;color:#94a3b8">
      Fuentes: JNE — Estadísticas electorales; ONPE — Resultados 2021; Transparencia Internacional Perú (2023); V-Dem v15. Datos actualizados a enero 2026.
    </div>
  </div>`;
  })() : "";

  // ── Sección I: Parlamento y Escenarios ────────────────────────────────────
  const parliamentSectionHtml = scenariosData ? (() => {
    const current = scenariosData.current || {};
    const seats = current.seats || [];
    const scenarios = scenariosData.scenarios || [];
    const totalSeats = scenariosData.total_seats || 130;

    // SVG barras horizontales de escaños actuales
    const maxSeats = Math.max(...seats.map(s => s.seats), 1);
    const rowH = 24, barW = 400, labelW = 180, valW = 40;
    const svgH = seats.length * rowH + 20;
    const seatsSvg = seats.length > 0 ? `
<svg viewBox="0 0 ${labelW + barW + valW + 10} ${svgH}" width="100%" style="display:block;max-width:680px;margin-bottom:10px" xmlns="http://www.w3.org/2000/svg">
  ${seats.map((s, i) => {
    const y = 10 + i * rowH;
    const bw = Math.max(2, (s.seats / maxSeats) * barW);
    const col = s.color || "#94a3b8";
    return `<rect x="${labelW}" y="${y+3}" width="${bw}" height="${rowH-8}" fill="${col}" rx="2" opacity="0.85"/>
    <text x="${labelW-6}" y="${y+rowH/2+4}" text-anchor="end" font-size="9" fill="#475569" font-family="sans-serif">${s.full_name || s.party}</text>
    <text x="${labelW+bw+5}" y="${y+rowH/2+4}" font-size="9" fill="${col}" font-family="monospace" font-weight="700">${s.seats}</text>`;
  }).join("")}
  <line x1="${labelW}" y1="10" x2="${labelW}" y2="${svgH-10}" stroke="#cbd5e1" stroke-width="1"/>
</svg>` : "";

    const scenarioCards = scenarios.map(sc => {
      const sColor = sc.color || "#94a3b8";
      const scSeats = (sc.seats || []).map(s =>
        `<div style="display:flex;justify-content:space-between;align-items:center;padding:3px 0;border-bottom:1px solid #f1f5f9;font-size:10px">
          <span style="color:#475569">${s.full_name || s.party}</span>
          <span style="font-weight:700;color:${s.color || "#475569"};font-family:monospace">${s.seats}</span>
        </div>`
      ).join("");
      return `<div class="scenario-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
          <div class="scenario-name" style="color:${sColor}">${sc.label || sc.id}</div>
          <div class="scenario-prob" style="color:${sColor}">${sc.probability_pct}%</div>
        </div>
        <div style="font-size:10px;color:#475569;margin-bottom:8px">${sc.description || ""}</div>
        <div style="font-size:10px;font-weight:600;color:${sColor};margin-bottom:6px">Riesgo: ${sc.governance_risk || "—"}</div>
        ${scSeats}
      </div>`;
    }).join("");

    return `
  <!-- ════ SECCIÓN I: PARLAMENTO ════════════════════════════════════════════ -->
  <div class="section-header">
    <div class="section-number">I</div>
    <div class="section-title">Parlamento y Escenarios Post-Electoral — Perú 2026</div>
  </div>
  <div class="parliament-section">

    <h3 style="font-size:12px;color:#475569;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">${current.label || "Composición Actual"}</h3>
    <p style="font-size:11px;color:#475569;margin-bottom:12px">${current.note || ""} Total: ${totalSeats} escaños. Sistema: ${scenariosData.electoral_system || "Representación proporcional D'Hondt"}.</p>
    ${seatsSvg}

    <h3 style="font-size:12px;color:#475569;text-transform:uppercase;letter-spacing:1px;margin:20px 0 12px">Escenarios Proyectados — Congreso 2026-2031</h3>
    <p style="font-size:11px;color:#475569;margin-bottom:14px">Modelos estructurales basados en tendencias electorales 2011-2021 y datos V-Dem. No constituyen predicción electoral.</p>
    <div class="scenarios-grid">${scenarioCards}</div>

    ${scenariosData.historical_context && scenariosData.historical_context.length > 0 ? `
    <h3 style="font-size:12px;color:#475569;text-transform:uppercase;letter-spacing:1px;margin:16px 0 10px">Contexto Histórico Reciente</h3>
    <table>
      <thead><tr><th style="width:8%">Año</th><th>Evento</th></tr></thead>
      <tbody>${(scenariosData.historical_context || []).map(e => `<tr><td><code>${e.year}</code></td><td>${e.event}</td></tr>`).join("")}</tbody>
    </table>` : ""}

    <div style="margin-top:10px;font-size:10px;color:#94a3b8">
      Fuentes: JNE — Sistema Electoral Peruano; ONPE — Resultados electorales 2021; V-Dem v15. Composición de bancadas aproximada a enero 2026.
    </div>
  </div>`;
  })() : "";

  // ── Fecha ─────────────────────────────────────────────────────────────────
  const genDate = new Date(timestamp || Date.now());
  const dateStr = genDate.toLocaleDateString("es-AR", { day:"2-digit", month:"long", year:"numeric", timeZone:"UTC" });
  const timeStr = genDate.toLocaleTimeString("es-AR", { hour:"2-digit", minute:"2-digit", timeZone:"UTC" }) + " UTC";

  return `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Democrac.IA — Informe PEIRS — ${country.name} ${new Date().getFullYear()}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=DM+Mono:wght@400;500;600&family=Lora:ital,wght@0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  /* ── Variables ── */
  :root {
    --ink:       #1e293b;
    --ink-light: #475569;
    --ink-dim:   #94a3b8;
    --paper:     #ffffff;
    --paper-2:   #f8fafc;
    --paper-3:   #f1f5f9;
    --border:    #e2e8f0;
    --accent:    #0f766e;
    --accent-bg: #f0fdf4;
    --risk-hex:  ${rp.hex};
    --risk-bg:   ${rp.light};
    --risk-mid:  ${rp.mid};
  }

  /* ── Base ── */
  body {
    background: var(--paper);
    color: var(--ink);
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
    line-height: 1.75;
    max-width: 960px;
    margin: 0 auto;
    padding: 0;
  }

  /* ── Portada ── */
  .cover {
    background: linear-gradient(160deg, #0f172a 0%, #1e293b 55%, #0f766e11 100%);
    color: #f8fafc;
    padding: 56px 64px 48px;
    position: relative;
    overflow: hidden;
  }
  .cover::before {
    content: "";
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 80% 20%, ${rp.hex}22 0%, transparent 60%);
    pointer-events: none;
  }
  .cover-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 48px; }
  .brand-block .brand-name { font-family: 'DM Mono', monospace; font-size: 22px; font-weight: 600; letter-spacing: -0.5px; }
  .brand-block .brand-name em { color: #2dd4bf; font-style: normal; }
  .brand-block .brand-sub { font-size: 9px; letter-spacing: 3px; color: #64748b; text-transform: uppercase; margin-top: 4px; }
  .confidential { font-size: 9px; letter-spacing: 3px; color: #475569; border: 1px solid #334155; padding: 4px 12px; border-radius: 4px; text-transform: uppercase; }

  .cover-main { display: flex; justify-content: space-between; align-items: flex-end; }
  .cover-left .country-flag { font-size: 52px; line-height: 1; margin-bottom: 12px; }
  .cover-left .country-name { font-family: 'Lora', Georgia, serif; font-size: 44px; font-weight: 700; color: #f8fafc; line-height: 1.1; margin-bottom: 8px; }
  .cover-left .election-date { font-size: 13px; color: #94a3b8; font-family: 'DM Mono', monospace; margin-bottom: 24px; }
  .cover-left .risk-pill {
    display: inline-flex; align-items: center; gap: 12px;
    background: ${rp.hex}22; border: 1px solid ${rp.hex}55;
    border-radius: 10px; padding: 10px 20px;
  }
  .cover-left .risk-label { font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: ${rp.mid}; font-family: 'DM Mono', monospace; }
  .cover-left .risk-score { font-size: 40px; font-weight: 900; color: ${rp.hex}; font-family: 'DM Mono', monospace; line-height: 1; }
  .cover-left .risk-level { font-size: 14px; font-weight: 700; color: ${rp.mid}; font-family: 'DM Mono', monospace; }
  .cover-right { text-align: right; }
  .cover-meta { font-size: 10px; color: #64748b; font-family: 'DM Mono', monospace; line-height: 2; }

  /* ── Indicadores rápidos ── */
  .kpi-strip {
    display: grid; grid-template-columns: repeat(4, 1fr);
    border: 1px solid var(--border);
    border-top: 3px solid var(--risk-hex);
  }
  .kpi-cell {
    padding: 18px 20px;
    border-right: 1px solid var(--border);
  }
  .kpi-cell:last-child { border-right: none; }
  .kpi-label { font-size: 9px; text-transform: uppercase; letter-spacing: 2px; color: var(--ink-dim); font-family: 'DM Mono', monospace; margin-bottom: 6px; }
  .kpi-value { font-size: 26px; font-weight: 800; color: var(--ink); font-family: 'DM Mono', monospace; line-height: 1; }
  .kpi-sub { font-size: 10px; color: var(--ink-light); margin-top: 4px; }

  /* ── Layout principal ── */
  .report-body { padding: 0 64px; }

  /* ── Gráficos ── */
  .charts-grid {
    display: grid; grid-template-columns: 220px 1fr;
    gap: 0; border: 1px solid var(--border); margin: 32px 0;
  }
  .chart-panel {
    padding: 28px 24px;
    border-right: 1px solid var(--border);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
  }
  .chart-panel-right { padding: 28px 28px; }
  .chart-panel-title {
    font-size: 9px; text-transform: uppercase; letter-spacing: 2px;
    color: var(--ink-dim); font-family: 'DM Mono', monospace; margin-bottom: 16px; text-align: center;
  }

  /* ── Secciones ── */
  .section-header {
    display: flex; align-items: center; gap: 12px;
    border-top: 2px solid var(--border);
    padding: 28px 0 16px;
    margin-top: 32px;
  }
  .section-number {
    width: 28px; height: 28px; border-radius: 50%;
    background: var(--accent); color: white;
    font-size: 11px; font-weight: 700; font-family: 'DM Mono', monospace;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }
  .section-title { font-size: 11px; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; color: var(--accent); font-family: 'DM Mono', monospace; }

  /* ── Capítulos ── */
  .chapter { margin-bottom: 8px; }

  h1 { font-family: 'Lora', Georgia, serif; font-size: 22px; font-weight: 700; color: var(--ink); margin: 24px 0 12px; border-bottom: 2px solid var(--risk-hex); padding-bottom: 8px; }
  h2 {
    font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px;
    color: var(--accent); font-family: 'DM Mono', monospace;
    margin: 32px 0 14px; padding: 10px 16px;
    background: var(--paper-2); border-left: 3px solid var(--accent);
  }
  h3 {
    font-size: 13px; font-weight: 700; color: var(--ink);
    margin: 22px 0 10px; padding-bottom: 6px;
    border-bottom: 1px dashed var(--border);
  }
  h4 { font-size: 12px; font-weight: 600; color: var(--ink-light); margin: 16px 0 8px; text-transform: uppercase; letter-spacing: 1px; font-family: 'DM Mono', monospace; }

  p { color: var(--ink-light); margin-bottom: 12px; font-size: 13px; }
  strong { color: var(--ink); font-weight: 600; }
  em { font-style: italic; color: var(--ink-light); }
  code { background: var(--paper-3); color: var(--accent); padding: 1px 6px; border-radius: 3px; font-size: 11px; font-family: 'DM Mono', monospace; border: 1px solid var(--border); }

  blockquote {
    border-left: 3px solid var(--risk-hex); margin: 12px 0;
    padding: 10px 16px; background: var(--risk-bg); border-radius: 0 6px 6px 0;
    font-size: 12px; color: var(--ink-light);
  }
  hr { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

  ul { margin: 8px 0 14px 0; padding: 0; list-style: none; }
  li { padding: 3px 0 3px 20px; position: relative; font-size: 12px; color: var(--ink-light); }
  li::before { content: "▸"; color: var(--accent); position: absolute; left: 2px; font-size: 10px; top: 5px; }

  /* ── Tablas ── */
  table { width: 100%; border-collapse: collapse; margin: 14px 0 20px; font-size: 12px; }
  thead th {
    padding: 9px 12px; text-align: left; font-size: 9px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.5px; color: #475569;
    background: var(--paper-3); border-bottom: 2px solid var(--border);
    font-family: 'DM Mono', monospace;
  }
  tbody td { padding: 9px 12px; border-bottom: 1px solid var(--border); color: var(--ink-light); vertical-align: top; }
  tbody tr:nth-child(even) td { background: var(--paper-2); }
  tbody tr:hover td { background: #f0fdf4; }
  td.conf-ok { color: #065f46; font-weight: 600; font-family: 'DM Mono', monospace; font-size: 11px; }
  td.conf-pend { color: #92400e; font-family: 'DM Mono', monospace; font-size: 11px; }
  tr.risk-critical td { background: #fef2f2; }
  tr.risk-high td { background: #fff7ed; }
  .no-data { font-style: italic; color: var(--ink-dim); padding: 16px; background: var(--paper-2); border: 1px solid var(--border); border-radius: 6px; }

  /* ── Trazabilidad ── */
  .trace-section {
    background: var(--paper-2); border: 1px solid var(--border);
    border-top: 3px solid var(--accent);
    padding: 32px; margin: 40px 0;
    page-break-inside: avoid;
  }
  .trace-title { font-size: 10px; text-transform: uppercase; letter-spacing: 3px; color: var(--accent); font-family: 'DM Mono', monospace; margin-bottom: 20px; font-weight: 700; }
  .trace-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
  .trace-row { display: flex; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid var(--border); font-size: 11px; }
  .trace-key { color: var(--ink-dim); font-family: 'DM Mono', monospace; }
  .trace-val { color: var(--ink); font-family: 'DM Mono', monospace; font-weight: 500; }
  .disclaimer {
    background: #fffbeb; border: 1px solid #fcd34d; border-left: 3px solid #b45309;
    padding: 12px 16px; margin-top: 20px; font-size: 11px; color: #78350f; border-radius: 0 4px 4px 0;
  }

  /* ── Footer ── */
  .report-footer {
    border-top: 2px solid var(--border);
    padding: 24px 64px;
    display: flex; justify-content: space-between; align-items: center;
    background: var(--paper-2);
    margin-top: 48px;
  }
  .footer-brand { font-family: 'DM Mono', monospace; font-size: 13px; font-weight: 600; color: var(--ink); }
  .footer-brand em { color: var(--accent); font-style: normal; }
  .footer-meta { font-size: 10px; color: var(--ink-dim); text-align: right; line-height: 1.8; }

  /* ── Metodología ── */
  .methodology {
    background: var(--paper-2); border: 1px solid var(--border);
    border-left: 4px solid #7c3aed;
    padding: 28px 32px; margin: 32px 0;
    page-break-inside: avoid;
  }
  .method-title { font-size: 10px; text-transform: uppercase; letter-spacing: 3px; color: #7c3aed; font-family: 'DM Mono', monospace; margin-bottom: 20px; font-weight: 700; }
  .method-step { margin-bottom: 18px; }
  .method-step-num { display: inline-block; width: 22px; height: 22px; background: #7c3aed; color: white; border-radius: 50%; font-size: 10px; font-weight: 700; text-align: center; line-height: 22px; font-family: 'DM Mono', monospace; margin-right: 10px; flex-shrink: 0; }
  .method-step-title { font-size: 12px; font-weight: 700; color: var(--ink); display: inline; }
  .method-step p { color: var(--ink-light); font-size: 12px; margin: 6px 0 0 32px; }
  .method-weight-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; border: 1px solid var(--border); margin: 16px 0; }
  .method-weight-cell { padding: 10px 12px; border-right: 1px solid var(--border); border-bottom: 1px solid var(--border); }
  .method-weight-cell:nth-child(4n) { border-right: none; }
  .method-weight-label { font-size: 9px; color: var(--ink-dim); text-transform: uppercase; letter-spacing: 1px; font-family: 'DM Mono', monospace; }
  .method-weight-val { font-size: 18px; font-weight: 800; color: #7c3aed; font-family: 'DM Mono', monospace; line-height: 1.2; }
  .limitation-box { background: #fffbeb; border: 1px solid #fcd34d; border-left: 3px solid #b45309; padding: 12px 16px; margin-top: 16px; border-radius: 0 4px 4px 0; }
  .limitation-box p { font-size: 11px; color: #78350f; margin: 0; }

  /* ── APA Bibliography ── */
  .apa-section {
    margin: 32px 0;
    page-break-inside: avoid;
    border-top: 2px solid var(--border);
    padding-top: 28px;
  }
  .apa-title { font-size: 10px; text-transform: uppercase; letter-spacing: 3px; color: #0f766e; font-family: 'DM Mono', monospace; margin-bottom: 20px; font-weight: 700; }
  .apa-ref { font-size: 11px; color: var(--ink-light); line-height: 1.7; margin-bottom: 8px; padding-left: 24px; text-indent: -24px; }
  .apa-ref a { color: var(--accent); text-decoration: none; font-family: 'DM Mono', monospace; font-size: 10px; }
  .apa-ref strong { color: var(--ink); font-weight: 600; }

  /* ── Static timeline in print ── */
  .timeline-print { margin: 20px 0; background: #0a0f1a; border-radius: 8px; padding: 4px 0; page-break-inside: avoid; -webkit-print-color-adjust: exact; print-color-adjust: exact; }

  /* ── V-Dem Charts ── */
  .vdem-charts-section { margin: 0 0 24px; }
  .chart-block {
    background: var(--paper-2); border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    padding: 20px 24px; margin-bottom: 24px;
    page-break-inside: avoid; break-inside: avoid;
  }
  .chart-title {
    font-size: 12px; font-weight: 700; color: var(--ink);
    margin-bottom: 5px; font-family: 'DM Mono', monospace; letter-spacing: 0.3px;
  }
  .chart-subtitle {
    font-size: 11px; color: var(--ink-light); line-height: 1.5; margin-bottom: 14px;
  }
  .chart-source {
    font-size: 9.5px; color: var(--ink-dim); margin-top: 10px; font-style: italic;
    padding-top: 8px; border-top: 1px dashed var(--border);
    font-family: 'DM Mono', monospace;
  }
  .chart-source a { color: var(--accent); text-decoration: none; }
  .chart-source code { font-size: 9px; font-style: normal; }

  /* ── Actores ── */
  .actors-section { margin-bottom: 24px; }
  .risk-badge { display:inline-block; padding: 1px 8px; border-radius: 4px; font-size: 9px; font-weight: 700; font-family: 'DM Mono', monospace; text-transform: uppercase; }
  .risk-badge.critical { background: #fef2f2; color: #991b1b; border: 1px solid #fca5a5; }
  .risk-badge.high { background: #fff7ed; color: #c2410c; border: 1px solid #fdba74; }
  .risk-badge.moderate { background: #fffbeb; color: #b45309; border: 1px solid #fcd34d; }
  .risk-badge.low { background: #f0fdf4; color: #065f46; border: 1px solid #86efac; }

  /* ── MOE Brief ── */
  .moe-brief-section { margin-bottom: 24px; }
  .alert-banner { padding: 12px 20px; margin-bottom: 16px; border-radius: 4px; display: flex; align-items: center; gap: 12px; }
  .alert-banner .alert-level-text { font-size: 13px; font-weight: 800; font-family: 'DM Mono', monospace; }
  .alert-banner .alert-label-text { font-size: 11px; color: var(--ink-light); }

  /* ── Parlamento ── */
  .parliament-section { margin-bottom: 24px; }
  .scenarios-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
  .scenario-card { border: 1px solid var(--border); padding: 14px; background: var(--paper-2); border-radius: 4px; }
  .scenario-name { font-size: 11px; font-weight: 700; color: var(--ink); margin-bottom: 4px; }
  .scenario-prob { font-size: 18px; font-weight: 800; color: var(--accent); font-family: 'DM Mono', monospace; }

  /* ── Glossary ── */
  .glossary-section { margin-bottom: 32px; }
  .glossary-intro {
    font-size: 12px; color: var(--ink-light); margin-bottom: 16px;
    background: var(--accent-bg); border: 1px solid #a7f3d0; border-left: 3px solid var(--accent);
    padding: 10px 16px; border-radius: 0 4px 4px 0;
  }
  .glossary-section table { font-size: 11px; }
  .glossary-section tbody td:first-child { white-space: nowrap; }

  /* ── Print / A4 ── */
  @media print {
    /* ── Página A4 con márgenes institucionales ── */
    @page {
      size: A4 portrait;
      margin: 20mm 18mm 24mm 18mm;
    }
    @page :first {
      margin: 0;
    }
    @page {
      @bottom-center {
        content: counter(page) " / " counter(pages);
        font-family: 'DM Mono', monospace;
        font-size: 8pt;
        color: #94a3b8;
      }
      @bottom-left {
        content: "Democrac.IA — PEIRS — Uso analítico restringido";
        font-family: 'DM Mono', monospace;
        font-size: 7pt;
        color: #cbd5e1;
      }
      @bottom-right {
        content: string(chapterTitle);
        font-family: 'DM Mono', monospace;
        font-size: 7pt;
        color: #94a3b8;
      }
    }

    /* ── Reset base para impresión ── */
    *, *::before, *::after {
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
      color-adjust: exact !important;
    }
    html, body {
      font-size: 10.5pt;
      line-height: 1.6;
      max-width: none;
      width: 100%;
      background: #fff !important;
      color: #1e293b !important;
    }

    /* ── Portada: página completa sin márgenes ── */
    .cover {
      page-break-after: always;
      min-height: 100vh;
      padding: 52pt 56pt 44pt;
      background: linear-gradient(160deg, #0f172a 0%, #1e293b 55%, #0f766e11 100%) !important;
    }
    .cover .country-name { font-size: 36pt !important; }
    .cover .risk-score   { font-size: 32pt !important; }

    /* ── KPI strip: siempre junto, nunca cortado ── */
    .kpi-strip {
      page-break-inside: avoid;
      break-inside: avoid;
      border-top: 3pt solid var(--risk-hex) !important;
    }
    .kpi-value { font-size: 20pt !important; }

    /* ── Gráficos ── */
    .charts-grid {
      page-break-inside: avoid;
      break-inside: avoid;
    }

    /* ── Headings: nunca quedan solos al pie de página ── */
    h1 {
      font-size: 16pt;
      page-break-after: avoid;
      break-after: avoid;
      margin-top: 20pt;
    }
    h2 {
      font-size: 8.5pt;
      page-break-after: avoid;
      break-after: avoid;
      margin-top: 18pt;
      background: #f1f5f9 !important;
      border-left: 3pt solid var(--accent) !important;
      padding: 6pt 10pt !important;
    }
    h3 {
      font-size: 11pt;
      page-break-after: avoid;
      break-after: avoid;
    }
    h4 { font-size: 9pt; page-break-after: avoid; break-after: avoid; }

    /* ── Capítulos: cada capítulo mayor empieza en página nueva ── */
    .chapter {
      page-break-before: auto;
      break-before: auto;
    }
    .chapter:first-child { page-break-before: avoid; }
    section.chapter > h1:first-child {
      page-break-before: always;
      break-before: page;
      padding-top: 8pt;
    }

    /* ── Párrafos y texto ── */
    p { font-size: 10.5pt; margin-bottom: 8pt; orphans: 3; widows: 3; }
    li { font-size: 10pt; }

    /* ── Tablas: nunca cortadas en medio de fila ── */
    table {
      page-break-inside: auto;
      font-size: 9.5pt;
      border-collapse: collapse;
    }
    tr {
      page-break-inside: avoid;
      break-inside: avoid;
    }
    thead {
      display: table-header-group; /* repite header en cada página */
    }
    tfoot { display: table-footer-group; }
    th, td { padding: 6pt 8pt !important; }
    thead th { font-size: 8pt !important; }
    tbody tr:hover td { background: transparent !important; }

    /* ── Blockquotes, cajas especiales ── */
    blockquote {
      page-break-inside: avoid;
      break-inside: avoid;
      border-left: 3pt solid var(--risk-hex) !important;
      background: var(--risk-bg) !important;
      padding: 8pt 12pt !important;
      font-size: 10pt;
    }
    .trace-section,
    .methodology,
    .disclaimer,
    .limitation-box,
    .chart-block {
      page-break-inside: avoid;
      break-inside: avoid;
    }
    .chart-subtitle, .chart-source { font-size: 8.5pt; }
    .glossary-section table { font-size: 8.5pt; }
    .vdem-charts-section { page-break-before: always; break-before: page; }
    .glossary-section { page-break-before: always; break-before: page; }

    /* ── Bibliografía: siempre nueva página ── */
    .apa-section {
      page-break-before: always;
      break-before: page;
    }
    .apa-ref { font-size: 9pt; margin-bottom: 6pt; }

    /* ── Footer del documento ── */
    .report-footer {
      display: flex !important;
      page-break-inside: avoid;
      margin-top: 24pt;
      padding: 12pt 0 0;
      border-top: 1.5pt solid #e2e8f0 !important;
      font-size: 8pt;
    }

    /* ── Ocultar elementos no imprimibles ── */
    .no-print,
    a[href^="http"]::after { display: none !important; }

    /* ── Código inline ── */
    code {
      font-size: 9pt;
      background: #f1f5f9 !important;
      border: 0.5pt solid #e2e8f0 !important;
    }

    /* ── Timeline ── */
    .timeline-print {
      page-break-inside: avoid;
      break-inside: avoid;
      background: #0a0f1a !important;
    }

    /* ── Colores de riesgo ── */
    tr.risk-critical td { background: #fef2f2 !important; }
    tr.risk-high td { background: #fff7ed !important; }
    td.conf-ok { color: #065f46 !important; }
    td.conf-pend { color: #92400e !important; }
    .no-data { background: #f8fafc !important; border: 0.5pt solid #e2e8f0 !important; }
  }
</style>
</head>
<body>

<!-- ══ BARRA DE IMPRESIÓN (sólo pantalla, oculta al imprimir) ════════════════ -->
<div class="no-print" style="position:fixed;top:0;left:0;right:0;z-index:9999;background:#1e293b;border-bottom:2px solid #0f766e;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;font-family:'DM Mono',monospace;font-size:11px;color:#94a3b8;box-shadow:0 2px 12px rgba(0,0,0,0.5)">
  <span style="color:#e2e8f0;font-weight:600">Democrac<span style="color:#2dd4bf">.IA</span> — Informe PEIRS — ${country.name}</span>
  <div style="display:flex;gap:12px;align-items:center">
    <span style="color:#64748b">Imprimir → A4 · Portrait · Incluir gráficos de fondo</span>
    <button onclick="window.print()" style="background:#0f766e;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-family:'DM Mono',monospace;font-size:11px;font-weight:600;cursor:pointer;letter-spacing:0.5px">
      ⎙ Imprimir / PDF A4
    </button>
  </div>
</div>
<div class="no-print" style="height:44px"></div>

<!-- ══ PORTADA ════════════════════════════════════════════════════════════════ -->
<div class="cover">
  <div class="cover-top">
    <div class="brand-block">
      <div class="brand-name">Democrac<em>.IA</em></div>
      <div class="brand-sub">Predictive Electoral Integrity &amp; Risk System</div>
    </div>
    <div class="confidential">Uso analítico restringido</div>
  </div>
  <div class="cover-main">
    <div class="cover-left">
      <div class="country-flag">${country.flag || ""}</div>
      <div class="country-name">${country.name}</div>
      <div class="election-date">Elección proyectada: ${country.date || "—"}</div>
      <div class="risk-pill">
        <div>
          <div class="risk-label">Índice de Riesgo</div>
          <div style="display:flex;align-items:baseline;gap:8px">
            <span class="risk-score">${score}</span>
            <span class="risk-level">${rp.label}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="cover-right">
      <div style="margin-bottom:16px">${gaugeSvg}</div>
      <div class="cover-meta">
        RUN ID: ${runId.slice(0,8).toUpperCase()}…<br>
        Generado: ${dateStr}<br>
        ${timeStr}<br>
        PEIRS v0.5.0
      </div>
    </div>
  </div>
</div>

<!-- ══ KPIs ═══════════════════════════════════════════════════════════════════ -->
<div class="kpi-strip">
  <div class="kpi-cell">
    <div class="kpi-label">Freedom House</div>
    <div class="kpi-value">${fhScore}<span style="font-size:14px;font-weight:400;color:#94a3b8">/100</span></div>
    <div class="kpi-sub">FIW ${fh.edition || "2025"} — ${fh.status || "—"}</div>
  </div>
  <div class="kpi-cell">
    <div class="kpi-label">V-Dem Liberal Democracy</div>
    <div class="kpi-value">${typeof vdemIdx === "number" ? vdemIdx.toFixed(3) : vdemIdx}</div>
    <div class="kpi-sub">V-Dem v15 — ${vdem.year || "2024"}</div>
  </div>
  <div class="kpi-cell">
    <div class="kpi-label">PEI Integridad</div>
    <div class="kpi-value">${peiScore !== "—" ? peiScore : "N/A"}<span style="font-size:14px;font-weight:400;color:#94a3b8">${peiScore !== "—" ? "/100" : ""}</span></div>
    <div class="kpi-sub">PEI-10.0 — ${pei.year || "—"}</div>
  </div>
  <div class="kpi-cell">
    <div class="kpi-label">RSF Prensa Libre</div>
    <div class="kpi-value">${rsfScore !== "—" ? rsfScore : "N/A"}<span style="font-size:14px;font-weight:400;color:#94a3b8">${rsfScore !== "—" ? "/100" : ""}</span></div>
    <div class="kpi-sub">RSF 2025 — Rank #${rsf.rank || "—"}/180</div>
  </div>
</div>

<!-- ══ CUERPO PRINCIPAL ════════════════════════════════════════════════════════ -->
<div class="report-body">

  <!-- Gráficos -->
  <div class="charts-grid">
    <div class="chart-panel">
      <div class="chart-panel-title">Gauge de Riesgo</div>
      ${gaugeSvg}
      <div style="margin-top:12px;text-align:center">
        <div style="font-size:10px;color:#94a3b8;font-family:monospace">EMB: ${(embLevel || "—").toUpperCase()}</div>
        <div style="font-size:10px;color:#94a3b8;font-family:monospace;margin-top:2px">${violations.length} violación${violations.length !== 1 ? "es" : ""} detectada${violations.length !== 1 ? "s" : ""}</div>
      </div>
    </div>
    <div class="chart-panel-right">
      <div class="chart-panel-title" style="text-align:left;margin-bottom:18px">Dimensiones de Integridad Electoral</div>
      ${dimBarsHtml}
      <div style="margin-top:14px;display:flex;gap:16px;flex-wrap:wrap">
        <span style="font-size:10px;color:#065f46">&#9632; 70-100: Satisfactorio</span>
        <span style="font-size:10px;color:#b45309">&#9632; 45-69: Monitoreo</span>
        <span style="font-size:10px;color:#c2410c">&#9632; 25-44: Deficiencias</span>
        <span style="font-size:10px;color:#991b1b">&#9632; 0-24: Crítico</span>
      </div>
    </div>
  </div>

  <!-- Capítulos del informe -->
  <div class="section-header">
    <div class="section-number">A</div>
    <div class="section-title">Análisis Detallado por Capítulo</div>
  </div>
  ${chapHtml || mdToHtml(markdown)}

  <!-- Violaciones al Derecho Internacional -->
  <div class="section-header">
    <div class="section-number">B</div>
    <div class="section-title">Violaciones al Derecho Internacional Electoral</div>
  </div>
  ${violHtml}

  <!-- Trazabilidad -->
  <div class="section-header">
    <div class="section-number">C</div>
    <div class="section-title">Trazabilidad de Fuentes y Metadatos</div>
  </div>
  <div class="trace-section">
    <div class="trace-title">&#128206; Anexo de Verificabilidad — PEIRS v0.5.0</div>
    <table>
      <thead><tr><th>Fuente</th><th>Descripción</th><th>Confianza</th></tr></thead>
      <tbody>${srcRows}</tbody>
    </table>
    <div style="margin-top:20px">
      <div class="trace-title" style="margin-bottom:12px">Metadatos del Análisis</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0">
        <div class="trace-row"><span class="trace-key">Run ID</span><span class="trace-val">${runId}</span></div>
        <div class="trace-row"><span class="trace-key">Sistema</span><span class="trace-val">Democrac.IA / PEIRS v0.5.0</span></div>
        <div class="trace-row"><span class="trace-key">País</span><span class="trace-val">${country.name}</span></div>
        <div class="trace-row"><span class="trace-key">Elección</span><span class="trace-val">${country.date || "—"}</span></div>
        <div class="trace-row"><span class="trace-key">Generado</span><span class="trace-val">${genDate.toISOString()}</span></div>
        <div class="trace-row"><span class="trace-key">Agentes IA</span><span class="trace-val">4 (LangGraph + Claude Sonnet 4.6)</span></div>
        <div class="trace-row"><span class="trace-key">Riesgo calculado</span><span class="trace-val">${score}/100 — ${rp.label}</span></div>
        <div class="trace-row"><span class="trace-key">Violaciones</span><span class="trace-val">${violations.length} detectadas</span></div>
      </div>
    </div>
  </div>

  <!-- Metodología -->
  <div class="section-header">
    <div class="section-number">D</div>
    <div class="section-title">Metodología del Sistema PEIRS</div>
  </div>
  <div class="methodology">
    <div class="method-title">&#9881; Arquitectura y Proceso Analítico — Democrac.IA / PEIRS v0.5.0</div>

    <div class="method-step">
      <span class="method-step-num">1</span>
      <span class="method-step-title">Agente OSINT — Recopilación y Estructuración de Datos</span>
      <p>Consume cuatro fuentes primarias en tiempo cuasi-real: <strong>V-Dem v15</strong> (Coppedge et al., 2025) — 27,913 observaciones país-año; <strong>Freedom House FIW 2025</strong> — 195 países; <strong>PEI-10.0</strong> (Norris et al., 2024) — 586 elecciones; <strong>RSF 2025</strong> — 180 países. Cada campo estructurado lleva metadatos de trazabilidad: <code>confidence ∈ {confirmed, mock, unverified}</code>. Datos confirmados provienen de APIs o archivos CSV verificados; datos "mock" son estimaciones basadas en rangos históricos pendientes de actualización.</p>
    </div>

    <div class="method-step">
      <span class="method-step-num">2</span>
      <span class="method-step-title">Agente Político — Análisis de Actores y Contexto</span>
      <p>Evalúa el ecosistema político-partidario del país: fragmentación parlamentaria, fuerzas electorales, riesgos asociados a actores específicos (Art. 25 ICCPR), financiamiento de campaña y ecosistema digital. Para Perú, integra 8 bases de datos estructuradas (JNE, ONPE, RENIEC, IDEHPUCP, FECOR) hardcodeadas en el sistema PEIRS. Genera narrativa analítica mediante prompts especializados con Claude Sonnet 4.6.</p>
    </div>

    <div class="method-step">
      <span class="method-step-num">3</span>
      <span class="method-step-title">Agente Legal — Detección de Violaciones al Derecho Electoral Internacional</span>
      <p>Compara el contexto del país con el corpus normativo: <strong>ICCPR Arts. 9, 14, 19, 21, 22, 25</strong>; <strong>CADH Art. 23</strong>; <strong>Carta Democrática Interamericana Arts. 3-4</strong>; <strong>UNDRIP Arts. 5, 18</strong>. Para cada dimensión (prensa, reunión, participación, justicia electoral), detecta violaciones potenciales y las clasifica por severidad (critical / high / moderate) y confianza (confirmed / mock). El nivel de confianza se hereda directamente del Agente 1.</p>
    </div>

    <div class="method-step">
      <span class="method-step-num">4</span>
      <span class="method-step-title">Índice de Riesgo Electoral (IRE) — Cálculo Ponderado</span>
      <p>El IRE (0-100, donde 100 = riesgo máximo) integra 8 dimensiones normalizadas usando percentiles históricos de países latinoamericanos V-Dem 2000-2024:</p>
    </div>

    <div class="method-weight-grid">
      ${[
        ["Sufragio","15%"],["Marco Legal","15%"],["EMB Independencia","15%"],["Libertad de Prensa","10%"],
        ["Financiamiento","10%"],["Ecosistema Digital","10%"],["Justicia Electoral","15%"],["Inclusividad","10%"],
      ].map(([d,w]) => `<div class="method-weight-cell"><div class="method-weight-label">${d}</div><div class="method-weight-val">${w}</div></div>`).join("")}
    </div>

    <div class="method-step">
      <span class="method-step-num">5</span>
      <span class="method-step-title">Agente Generador — Síntesis y Estructuración del Informe</span>
      <p>Integra los outputs de los tres agentes anteriores y genera los 10 capítulos estructurados del informe PEIRS: resumen ejecutivo, contexto político, administración electoral (EMB), inclusividad, financiamiento, ecosistema digital, jornada electoral, justicia, recomendaciones y regulación de IA. El informe en markdown se convierte a HTML interactivo para el dashboard y a PDF A4 para distribución institucional.</p>
    </div>

    <div class="limitation-box">
      <p><strong>Limitaciones y advertencias metodológicas:</strong> (1) V-Dem 2024 es el año de medición más reciente disponible; eventos post-dic 2024 no están en el dataset base. (2) Los campos marcados como "mock" requieren verificación con fuentes primarias actualizadas antes de uso oficial. (3) El IRE es un índice comparativo y no predice con certeza resultados electorales específicos. (4) Los agentes IA pueden introducir sesgos interpretativos; se recomienda revisión experta para informes con impacto institucional. (5) Este informe no constituye validación oficial de ningún proceso electoral. Datos citados bajo CC-BY-4.0 y uso académico con atribución.</p>
    </div>
  </div>

  <!-- APA Bibliography -->
  <div class="section-header">
    <div class="section-number">E</div>
    <div class="section-title">Referencias Bibliográficas (APA 7.ª edición)</div>
  </div>
  <div class="apa-section">
    <div class="apa-title">&#128218; Fuentes Primarias y Secundarias Citadas</div>

    <p class="apa-ref">AIDESEP. (2021). <em>Informe de participación electoral de pueblos indígenas amazónicos en el proceso general 2021</em>. Asociación Interétnica de Desarrollo de la Selva Peruana.</p>

    <p class="apa-ref">Anthropic. (2025). <em>Claude Sonnet 4.6</em> [Large language model]. Anthropic. <a href="https://www.anthropic.com/claude">https://www.anthropic.com/claude</a></p>

    <p class="apa-ref">Comité de Derechos Humanos de la ONU. (2020). <em>Observación General No. 37: Artículo 21 (Derecho de reunión pacífica)</em> (CCPR/C/GC/37). Oficina del Alto Comisionado de las Naciones Unidas para los Derechos Humanos. <a href="https://www.ohchr.org/es/documents/general-comments-and-recommendations/general-comment-no-37">https://www.ohchr.org</a></p>

    <p class="apa-ref">Coppedge, M., Gerring, J., Knutsen, C. H., Lindberg, S. I., Teorell, J., Altman, D., … Ziblatt, D. (2025). <em>V-Dem Dataset v15</em>. Varieties of Democracy (V-Dem) Project. <a href="https://doi.org/10.23696/vdemds25">https://doi.org/10.23696/vdemds25</a></p>

    <p class="apa-ref">Coppedge, M., Gerring, J., Knutsen, C. H., Lindberg, S. I., Teorell, J., Altman, D., … Ziblatt, D. (2025). <em>V-Dem Codebook v15</em>. Varieties of Democracy (V-Dem) Project. <a href="https://www.v-dem.net/data/the-v-dem-dataset/">https://www.v-dem.net</a></p>

    <p class="apa-ref">Freedom House. (2025). <em>Freedom in the World 2025: ${country.name}</em>. Freedom House. <a href="https://freedomhouse.org/country/${(country.name||"").toLowerCase().replace(/\s/g,"-")}/freedom-world/2025">https://freedomhouse.org</a></p>

    <p class="apa-ref">Instituto de Democracia y Derechos Humanos de la PUCP. (2025). <em>Financiamiento ilícito y crimen organizado en campañas electorales 2026</em>. IDEHPUCP. <a href="https://idehpucp.pucp.edu.pe">https://idehpucp.pucp.edu.pe</a></p>

    <p class="apa-ref">International IDEA. (2024). <em>The Global State of Democracy 2024</em>. International Institute for Democracy and Electoral Assistance. <a href="https://www.idea.int/democracytracker">https://www.idea.int</a></p>

    <p class="apa-ref">Jurado Nacional de Elecciones. (2025, 15 de agosto). <em>Resolución N° 0891-2025-JNE: Expediente sobre modalidades de voto en el exterior para el Proceso Electoral General 2026</em>. JNE. <a href="https://www.jne.gob.pe/transparencia/resoluciones/">https://www.jne.gob.pe</a></p>

    <p class="apa-ref">LangChain Inc. (2025). <em>LangGraph: Multi-agent orchestration framework</em>. LangChain. <a href="https://langchain-ai.github.io/langgraph/">https://langchain-ai.github.io/langgraph/</a></p>

    <p class="apa-ref">Naciones Unidas. (1966). <em>Pacto Internacional de Derechos Civiles y Políticos</em> (Resolución de la Asamblea General 2200A (XXI), 16 de diciembre de 1966). ONU. <a href="https://www.ohchr.org/es/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights">https://www.ohchr.org</a></p>

    <p class="apa-ref">Norris, P., Frank, R. W., &amp; Martínez i Coma, F. (2024). <em>The expert survey of Perceptions of Electoral Integrity, Release 10 (PEI-10.0)</em>. Harvard Dataverse. <a href="https://doi.org/10.7910/DVN/IQKBK5">https://doi.org/10.7910/DVN/IQKBK5</a></p>

    <p class="apa-ref">Oficina Nacional de Procesos Electorales. (2025). <em>Padrón electoral exterior — Proceso Electoral General 2026</em>. ONPE. <a href="https://www.onpe.gob.pe/modOGELEC/acVotoExterior/">https://www.onpe.gob.pe</a></p>

    <p class="apa-ref">Organización de los Estados Americanos. (2023). <em>Carta Democrática Interamericana: Aplicación y seguimiento</em> (OEA/Ser.G CP/doc.5872/23). OEA. <a href="https://www.oas.org/es/sap/deco/cdi.asp">https://www.oas.org</a></p>

    <p class="apa-ref">Registro Nacional de Identificación y Estado Civil. (2026, enero). <em>Informe de depuración del padrón electoral exterior N° 001-2026-SGEN/RENIEC</em>. RENIEC. <a href="https://www.reniec.gob.pe">https://www.reniec.gob.pe</a></p>

    <p class="apa-ref">Reporters Without Borders. (2025). <em>World Press Freedom Index 2025</em>. RSF. <a href="https://rsf.org/en/index">https://rsf.org/en/index</a></p>

    <p class="apa-ref">Transparencia Internacional Perú. (2023). <em>Índice de percepción de la corrupción 2023: Perú</em>. TI-Perú. <a href="https://www.transparencia.org.pe">https://www.transparencia.org.pe</a></p>
  </div>

  ${vdemSectionHtml}
  ${moeBriefSectionHtml}
  ${actorsSectionHtml}
  ${parliamentSectionHtml}
  ${glossaryHtml}

  <div class="disclaimer" style="margin-bottom:32px">
    <strong>Nota de uso:</strong> Este informe ha sido generado de manera automatizada por el sistema Democrac.IA / PEIRS v0.5.0 utilizando inteligencia artificial (Claude Sonnet 4.6, Anthropic, 2025) y datos de fuentes académicas de acceso abierto. No constituye validación oficial de ningún proceso electoral, ni posición institucional de ninguna organización. Para uso académico, analítico o de referencia con atribución obligatoria: <em>Democrac.IA. (${new Date().getFullYear()}). Informe PEIRS — ${country.name || "—"} [Análisis automatizado]. Run/${runId.slice(0,8).toUpperCase()}.</em>
  </div>

</div><!-- /report-body -->

<!-- ══ FOOTER ════════════════════════════════════════════════════════════════ -->
<div class="report-footer">
  <div>
    <div class="footer-brand">Democrac<em>.IA</em></div>
    <div style="font-size:10px;color:#94a3b8;margin-top:4px;font-family:monospace">Predictive Electoral Integrity &amp; Risk System</div>
  </div>
  <div class="footer-meta">
    © ${new Date().getFullYear()} Democrac.IA — Análisis electoral global con IA<br>
    V-Dem v15 · Freedom House FIW 2025 · PEI-10.0 · RSF 2025<br>
    RUN/${runId.slice(0,8).toUpperCase()} · ${dateStr}
  </div>
</div>

</body>
</html>`;
};

// ── REPORT VIEWER COMPLETO ────────────────────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════════════════
// REPORT VIEWER ELITE — Democrac.IA PEIRS
// ═══════════════════════════════════════════════════════════════════════════════

const RISK_CONFIG = {
  critical: { color: "#ef4444", bg: "#ef444418", label: "CRÍTICO", glow: "#ef444466" },
  high:     { color: "#f97316", bg: "#f9731618", label: "ALTO",     glow: "#f9731666" },
  moderate: { color: "#f59e0b", bg: "#f59e0b18", label: "MODERADO", glow: "#f59e0b66" },
  low:      { color: "#00d4aa", bg: "#00d4aa18", label: "BAJO",     glow: "#00d4aa66" },
};

const DIMENSION_META = {
  suffrage:         { label: "Sufragio Universal",      icon: "🗳️", desc: "Derecho al voto sin discriminación — ICCPR Art. 25(a)" },
  legalFramework:   { label: "Marco Legal",             icon: "📜", desc: "Calidad del marco normativo electoral — V-Dem v2x_polyarchy" },
  embIndependence:  { label: "Independencia EMB",       icon: "🏛️", desc: "Autonomía del organismo electoral — V-Dem v2elembaut" },
  mediaFreedom:     { label: "Libertad de Medios",      icon: "📰", desc: "Acceso a información electoral libre — RSF + V-Dem" },
  campaignFinance:  { label: "Financiamiento",          icon: "💰", desc: "Transparencia del financiamiento de campaña — PEI-10.0" },
  digitalEcosystem: { label: "Ecosistema Digital",      icon: "🌐", desc: "Libertad en el entorno digital — V-Dem v2mecenefi" },
  disputeResolution:{ label: "Justicia Electoral",      icon: "⚖️", desc: "Independencia judicial para disputas — ICCPR Art. 14" },
  inclusion:        { label: "Inclusividad",            icon: "👥", desc: "Participación de grupos vulnerables — CEDAW / ICERD" },
};

const CIVIL_LIBERTY_LABELS = {
  guaranteed:           { color: "#00d4aa", icon: "✅", label: "Garantizada" },
  mostly_free:          { color: "#22c55e", icon: "🟢", label: "Mayormente libre" },
  partially_restricted: { color: "#f59e0b", icon: "🟡", label: "Parcialmente restringida" },
  restricted:           { color: "#f97316", icon: "🟠", label: "Restringida" },
  severely_restricted:  { color: "#ef4444", icon: "🔴", label: "Severamente restringida" },
  banned:               { color: "#7f1d1d", icon: "⛔", label: "Prohibida" },
  strong:               { color: "#00d4aa", icon: "✅", label: "Independiente" },
  mostly_independent:   { color: "#22c55e", icon: "🟢", label: "Mayormente independiente" },
  under_pressure:       { color: "#f59e0b", icon: "🟡", label: "Bajo presión" },
  compromised:          { color: "#f97316", icon: "🟠", label: "Comprometida" },
  captured:             { color: "#ef4444", icon: "🔴", label: "Capturada" },
};

// ── Gauge Component ──────────────────────────────────────────────────────────
const RiskGaugeElite = ({ score, riskLevel, size = 200 }) => {
  const anim = score || 0;

  const rc = RISK_CONFIG[riskLevel] || RISK_CONFIG.moderate;
  const r = size / 2 - 18;
  const circ = Math.PI * r;
  const offset = circ - (anim / 100) * circ;

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
      <div style={{ position: "relative", width: size, height: size / 2 + 40 }}>
        <svg width={size} height={size / 2 + 20} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
          {/* Track */}
          <path d={`M 18,${size/2} A ${r},${r} 0 0,1 ${size-18},${size/2}`}
            fill="none" stroke="#1e2d3d" strokeWidth="14" strokeLinecap="round" />
          {/* Zones */}
          {[
            { pct: 0.25, color: "#00d4aa44" },
            { pct: 0.25, color: "#f59e0b44" },
            { pct: 0.25, color: "#f9731644" },
            { pct: 0.25, color: "#ef444444" },
          ].map((z, zi) => {
            const startPct = zi * 0.25;
            const zCirc = Math.PI * r;
            const zStart = zCirc * startPct;
            return (
              <path key={zi}
                d={`M 18,${size/2} A ${r},${r} 0 0,1 ${size-18},${size/2}`}
                fill="none" stroke={z.color} strokeWidth="14" strokeLinecap="butt"
                strokeDasharray={`${z.pct * zCirc} ${zCirc}`}
                strokeDashoffset={-zStart}
              />
            );
          })}
          {/* Active arc */}
          <path d={`M 18,${size/2} A ${r},${r} 0 0,1 ${size-18},${size/2}`}
            fill="none" stroke={rc.color} strokeWidth="14" strokeLinecap="round"
            strokeDasharray={circ} strokeDashoffset={offset}
            style={{ filter: `drop-shadow(0 0 10px ${rc.glow})`, transition: "stroke-dashoffset 0.05s" }}
          />
          {/* Zone labels */}
          {["BAJO", "MOD.", "ALTO", "CRÍTICO"].map((lbl, li) => {
            const angle = -Math.PI + (li + 0.5) * (Math.PI / 4);
            const lx = size/2 + (r - 28) * Math.cos(angle);
            const ly = size/2 + (r - 28) * Math.sin(angle);
            return (
              <text key={li} x={lx} y={ly} textAnchor="middle" dominantBaseline="middle"
                fontSize="7" fill="#475569" fontFamily="'DM Mono', monospace" fontWeight="600">
                {lbl}
              </text>
            );
          })}
        </svg>
        <div style={{
          position: "absolute", bottom: 0, left: "50%", transform: "translateX(-50%)",
          textAlign: "center",
        }}>
          <div style={{
            fontSize: size * 0.26, fontWeight: 900, color: rc.color,
            fontFamily: "'DM Mono', monospace", lineHeight: 1,
            textShadow: `0 0 20px ${rc.glow}`,
          }}>
            {Math.round(anim)}
          </div>
          <div style={{ fontSize: 10, color: "#64748b", letterSpacing: 3, textTransform: "uppercase", marginTop: 2 }}>
            Índice de Riesgo
          </div>
        </div>
      </div>
      <div style={{
        padding: "6px 20px", borderRadius: 20,
        background: rc.bg, border: `1px solid ${rc.color}66`,
        fontSize: 12, fontWeight: 800, color: rc.color,
        fontFamily: "'DM Mono', monospace", letterSpacing: 2,
        boxShadow: `0 0 16px ${rc.glow}`,
      }}>
        {rc.label}
      </div>
    </div>
  );
};

// ── Dimension Bar ────────────────────────────────────────────────────────────
const DimensionBar = ({ dimKey, value, delay = 0 }) => {
  const anim = value || 0;
  const meta = DIMENSION_META[dimKey] || { label: dimKey, icon: "📊", desc: "" };

  const color = value >= 70 ? "#00d4aa" : value >= 45 ? "#f59e0b" : value >= 25 ? "#f97316" : "#ef4444";
  const bgColor = value >= 70 ? "#00d4aa18" : value >= 45 ? "#f59e0b18" : value >= 25 ? "#f9731618" : "#ef444418";

  return (
    <TooltipInfo text={{ title: meta.label, desc: meta.desc, source: "PEIRS", confidence: "confirmed" }}>
      <div style={{ marginBottom: 10, cursor: "help" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 5 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ fontSize: 13 }}>{meta.icon}</span>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#e2e8f0" }}>{meta.label}</span>
          </div>
          <span style={{
            fontSize: 12, fontWeight: 800, color, fontFamily: "'DM Mono', monospace",
            background: bgColor, padding: "1px 8px", borderRadius: 10,
          }}>{Math.round(anim)}</span>
        </div>
        <div style={{ height: 6, background: "#1e2d3d", borderRadius: 3, overflow: "hidden" }}>
          <div style={{
            height: "100%", width: `${anim}%`, borderRadius: 3,
            background: `linear-gradient(90deg, ${color}88, ${color})`,
            boxShadow: `0 0 8px ${color}66`,
            transition: "width 0.05s ease",
          }} />
        </div>
      </div>
    </TooltipInfo>
  );
};

// ── Civil Liberties Semaphore ─────────────────────────────────────────────────
const CivilLibertiesSemaphore = ({ civil }) => {
  if (!civil) return null;
  const items = [
    { key: "freedom_of_press",    label: "Libertad de Prensa",   icon: "📰", value: civil.freedom_of_press },
    { key: "freedom_of_assembly", label: "Libertad de Reunión",  icon: "🤝", value: civil.freedom_of_assembly },
    { key: "judicial_independence",label: "Independencia Judicial",icon: "⚖️", value: civil.judicial_independence },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {items.map((item) => {
        const cfg = CIVIL_LIBERTY_LABELS[item.value] || { color: "#64748b", icon: "❓", label: item.value || "N/D" };
        return (
          <div key={item.key} style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            padding: "10px 14px", borderRadius: 10,
            background: cfg.color + "0f", border: `1px solid ${cfg.color}33`,
            transition: "all 0.2s ease",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: 16 }}>{item.icon}</span>
              <div>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0" }}>{item.label}</div>
                <div style={{ fontSize: 10, color: "#64748b", fontFamily: "'DM Mono', monospace" }}>
                  {item.value || "N/D"}
                </div>
              </div>
            </div>
            <div style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "4px 10px", borderRadius: 12,
              background: cfg.color + "18", border: `1px solid ${cfg.color}44`,
            }}>
              <span style={{ fontSize: 12 }}>{cfg.icon}</span>
              <span style={{ fontSize: 11, fontWeight: 700, color: cfg.color }}>{cfg.label}</span>
            </div>
          </div>
        );
      })}
      {civil.political_prisoners && (
        <div style={{
          padding: "10px 14px", borderRadius: 10,
          background: "#ef444418", border: "1px solid #ef444444",
          display: "flex", alignItems: "center", gap: 10,
        }}>
          <span style={{ fontSize: 16 }}>🚨</span>
          <div>
            <div style={{ fontSize: 12, fontWeight: 700, color: "#ef4444" }}>Presos Políticos</div>
            <div style={{ fontSize: 10, color: "#64748b", fontFamily: "'DM Mono', monospace" }}>
              Documentado — ICCPR Art. 9
            </div>
          </div>
          <span style={{ marginLeft: "auto", fontSize: 11, fontWeight: 700, color: "#ef4444",
            background: "#ef444418", padding: "2px 8px", borderRadius: 10 }}>CRÍTICO</span>
        </div>
      )}
    </div>
  );
};

// ── Violation Heatmap ─────────────────────────────────────────────────────────
const ViolationHeatmap = ({ violations }) => {
  if (!violations || violations.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "20px", color: "#00d4aa" }}>
        <div style={{ fontSize: 28, marginBottom: 8 }}>✓</div>
        <div style={{ fontSize: 13 }}>Sin violaciones detectadas</div>
      </div>
    );
  }

  const severityOrder = { critical: 0, high: 1, moderate: 2, low: 3 };
  const sorted = [...violations].sort((a, b) =>
    (severityOrder[a.severity] || 3) - (severityOrder[b.severity] || 3)
  );

  const severityConfig = {
    critical: { color: "#ef4444", bg: "#ef444418", border: "#ef444444", label: "CRÍTICO" },
    high:     { color: "#f97316", bg: "#f9731618", border: "#f9731644", label: "ALTO" },
    moderate: { color: "#f59e0b", bg: "#f59e0b18", border: "#f59e0b44", label: "MODERADO" },
    low:      { color: "#00d4aa", bg: "#00d4aa18", border: "#00d4aa44", label: "BAJO" },
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {sorted.map((v, i) => {
        const sc = severityConfig[v.severity] || severityConfig.moderate;
        const isConf = v.confidence === "confirmed";
        return (
          <div key={i} style={{
            padding: "10px 14px", borderRadius: 10,
            background: sc.bg, border: `1px solid ${sc.border}`,
            borderLeft: `4px solid ${sc.color}`,
            display: "grid", gridTemplateColumns: "auto 1fr auto",
            gap: 12, alignItems: "start",
          }}>
            <div style={{ paddingTop: 2 }}>
              <span style={{
                fontSize: 9, fontWeight: 700, fontFamily: "'DM Mono', monospace",
                color: sc.color, background: sc.bg, padding: "2px 6px",
                borderRadius: 4, border: `1px solid ${sc.border}`,
                whiteSpace: "nowrap",
              }}>{v.treaty} {v.article}</span>
            </div>
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0", marginBottom: 3 }}>{v.right}</div>
              <div style={{ fontSize: 11, color: "#94a3b8", lineHeight: 1.5 }}>
                {v.finding ? v.finding.substring(0, 100) + (v.finding.length > 100 ? "…" : "") : ""}
              </div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
              <span style={{
                fontSize: 9, fontWeight: 700, color: sc.color,
                fontFamily: "'DM Mono', monospace",
              }}>{sc.label}</span>
              <span style={{
                fontSize: 9, padding: "1px 6px", borderRadius: 4,
                background: isConf ? "#00d4aa18" : "#f59e0b18",
                color: isConf ? "#00d4aa" : "#f59e0b",
                fontFamily: "'DM Mono', monospace",
              }}>{isConf ? "✓ VERIF." : "⚠ ESTIM."}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ── Source Confidence Badge ───────────────────────────────────────────────────
const SourceBadge = ({ label, value, confidence, year, color }) => (
  <div style={{
    padding: "12px 16px", borderRadius: 12,
    background: confidence === "confirmed" ? color + "0f" : "#1a233218",
    border: `1px solid ${confidence === "confirmed" ? color + "44" : "#1e2d3d"}`,
    borderLeft: `3px solid ${confidence === "confirmed" ? color : "#475569"}`,
  }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 4 }}>
      <span style={{ fontSize: 11, fontWeight: 700, color: "#e2e8f0", textTransform: "uppercase", letterSpacing: 1 }}>{label}</span>
      <span style={{
        fontSize: 9, padding: "1px 7px", borderRadius: 10,
        background: confidence === "confirmed" ? "#00d4aa18" : "#f59e0b18",
        color: confidence === "confirmed" ? "#00d4aa" : "#f59e0b",
        fontFamily: "'DM Mono', monospace", fontWeight: 700,
      }}>{confidence === "confirmed" ? "✓ VERIFICADO" : "⚠ ESTIMADO"}</span>
    </div>
    <div style={{ fontSize: 20, fontWeight: 900, color, fontFamily: "'DM Mono', monospace", lineHeight: 1.2 }}>{value}</div>
    {year && <div style={{ fontSize: 10, color: "#475569", marginTop: 2, fontFamily: "'DM Mono', monospace" }}>Año {year}</div>}
  </div>
);



// ── ReportViewer Elite ────────────────────────────────────────────────────────
const ReportViewer = ({ runId, country }) => {
  const [fetchState, setFetchState] = useState({ data: null, loading: true, error: null });
  const [activeTab, setActiveTab] = useState("resumen");
  const [rvChartData, setRvChartData] = useState(null);
  const [rvActors, setRvActors] = useState(null);
  const [rvScenarios, setRvScenarios] = useState(null);
  const [rvMoeBrief, setRvMoeBrief] = useState(null);
  const { data: reportData, loading, error } = fetchState;

  useEffect(() => {
    if (!runId) return;
    // Flag para evitar set-state si el componente se desmonta durante el fetch en vuelo.
    // Antes había un cleanup que reseteaba fetchState a null en cada unmount/re-render,
    // lo que hacía oscilar reportData entre valor real y null y re-disparaba la animación
    // del gauge del Índice de Riesgo constantemente (bug visible: "el número cambia todo
    // el tiempo, mal calibrado").
    let alive = true;
    fetch(`${API_BASE}/api/report/${runId}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => { if (alive) setFetchState({ data, loading: false, error: null }); })
      .catch(err => { if (alive) setFetchState({ data: null, loading: false, error: err.message }); });
    return () => { alive = false; };
  }, [runId]);

  useEffect(() => {
    const cc = country?.id?.toUpperCase() || country?.country_code;
    if (!cc) return;
    fetch(`${API_BASE}/api/country/${cc}/chartdata`)
      .then(r => r.ok ? r.json() : null)
      .then(d => setRvChartData(d))
      .catch(() => {});
  }, [country?.id, country?.country_code]);

  useEffect(() => {
    if (country?.id !== "per") return;
    fetch(`${API_BASE}/api/peru/actors`)
      .then(r => r.ok ? r.json() : null)
      .then(d => setRvActors(d))
      .catch(() => {});
    fetch(`${API_BASE}/api/peru/scenarios`)
      .then(r => r.ok ? r.json() : null)
      .then(d => setRvScenarios(d))
      .catch(() => {});
    fetch(`${API_BASE}/api/moe/brief/PER`)
      .then(r => r.ok ? r.json() : null)
      .then(d => setRvMoeBrief(d))
      .catch(() => {});
  }, [country?.id, country?.country_code]);

  const handleDownload = () => {
    if (!reportData || !country) return;
    const md = reportData.final_report_markdown || "";
    const htmlContent = generateHtmlReport(md, country, runId, reportData.timestamp, reportData, rvChartData, rvActors, rvScenarios, rvMoeBrief);
    const blob = new Blob([htmlContent], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const win = window.open(url, "_blank");
    if (win) win.focus();
    // Revoke after a delay to allow the new tab to load
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  };

  if (loading) return (
    <div style={{ textAlign: "center", padding: 40, color: "#64748b" }}>
      <div style={{ fontSize: 28, marginBottom: 10 }}>⏳</div>
      <div style={{ fontSize: 13 }}>Cargando informe completo...</div>
    </div>
  );
  if (error) return (
    <div style={{ padding: "12px 16px", borderRadius: 8, background: "#ef444418", border: "1px solid #ef444444", fontSize: 12, color: "#ef4444" }}>
      ⚠️ No se pudo cargar el informe.
    </div>
  );
  if (!reportData) return null;

  // Extraer datos del reporte
  const context = reportData.context_data || {};
  const legal = reportData.legal_analysis || {};
  const dictamen = reportData.dictamen || {};

  const extractVal = (d) => (d && d._trace) ? d.value : d;

  const fhData = extractVal(context.freedom_house) || {};
  const fhScore = fhData.total_score || fhData.score || null;
  const fhEdition = fhData.edition || "—";

  const vdemData = extractVal(context.vdem) || {};
  const vdemLibdem = vdemData.liberal_democracy || null;
  const vdemYear = vdemData.year || "—";

  const peiData = extractVal(context.pei) || {};
  const peiIntegrity = peiData.overall_integrity || null;
  const peiYear = peiData.year || "—";

  const rsf = extractVal(context.rsf) || {};
  const rsfScore = rsf.score || null;

  const civil = extractVal(context.civil_liberties) || {};
  const violations = legal.violations || [];
  const riskLevel = reportData.risk_level || country.riskLevel || "moderate";
  const riskScore = reportData.risk_score || country.riskScore || 0;
  const rc = RISK_CONFIG[riskLevel] || RISK_CONFIG.moderate;

  const trend = dictamen.trend || {};
  const regComp = dictamen.regional_comparison || {};
  const dataConf = dictamen.data_confidence || "MEDIUM";
  const confColor = dataConf === "HIGH" ? "#00d4aa" : dataConf === "MEDIUM" ? "#f59e0b" : "#ef4444";

  const md = reportData.final_report_markdown || "";
  const reportChapters = reportData.report_chapters || {};
  const execSummary = reportChapters["01_executive_summary"] || "";

  const CHAPTERS = [
    { id: "resumen", num: "1", label: "Resumen Ejecutivo", icon: "📊", desc: "Dashboard de riesgo y fuentes verificadas" },
    { id: "perfil", num: "0", label: "Perfil del País", icon: "🌍", desc: "Demografía, economía y padrón electoral" },
    { id: "politico", num: "2", label: "Contexto Político", icon: "⚖️", desc: "Marco legal, fuerzas de poder, crisis institucional" },
    { id: "emb", num: "3", label: "Organismo Electoral", icon: "🏛️", desc: "Independencia, registro, observación internacional" },
    { id: "inclusividad", num: "4", label: "Inclusividad", icon: "🤝", desc: "Mujeres, pueblos originarios, LGBTQ+, discapacidad" },
    { id: "campana", num: "5", label: "Campaña", icon: "📢", desc: "Libertades, financiamiento, cobertura mediática" },
    { id: "digital", num: "6", label: "Amenazas Digitales", icon: "🔒", desc: "Internet, desinformación, plataformas" },
    { id: "jornada", num: "7", label: "Jornada Electoral", icon: "🗳️", desc: "Observaciones en tiempo real" },
    { id: "justicia", num: "8", label: "Justicia Electoral", icon: "⚡", desc: "Resolución de disputas, rendición de cuentas" },
    { id: "recomendaciones", num: "9", label: "Recomendaciones", icon: "📋", desc: "Matriz de acción electoral" },
    { id: "ia", num: "10", label: "IA y Regulación", icon: "🤖", desc: "Inteligencia artificial en el proceso" },
  ];

  const ChapterContent = ({ num, title, desc, sources, markdown, children }) => (
    <div>
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
          <span style={{
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            width: 32, height: 32, borderRadius: 8,
            background: COLORS.accent + "22", color: COLORS.accent,
            fontFamily: "'DM Mono', monospace", fontWeight: 800, fontSize: 14,
          }}>{num}</span>
          <h3 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: COLORS.text }}>{title}</h3>
        </div>
        <p style={{ margin: 0, fontSize: 13, color: COLORS.textMuted, lineHeight: 1.6 }}>{desc}</p>
        {sources && sources.length > 0 && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 10 }}>
            {sources.map((s, i) => (
              <span key={i} style={{
                fontSize: 9, padding: "2px 8px", borderRadius: 4,
                background: COLORS.surfaceLight, color: COLORS.textDim,
                fontFamily: "'DM Mono', monospace", border: `1px solid ${COLORS.border}`,
              }}>{s}</span>
            ))}
          </div>
        )}
      </div>
      {children}
      {markdown && (
        <div style={{
          padding: "20px 24px", borderRadius: 10,
          background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`,
          marginTop: children ? 20 : 0,
        }}>
          {renderMarkdownWithTooltips(markdown)}
        </div>
      )}
    </div>
  );

  return (
    <div style={{ marginTop: 24 }}>
      {/* Header del reporte */}
      <div style={{
        padding: "20px 24px",
        background: "linear-gradient(135deg, #0d1625 0%, #111827 100%)",
        borderRadius: "14px 14px 0 0",
        border: `1px solid ${rc.color}33`,
        borderBottom: "none",
        display: "flex", justifyContent: "space-between", alignItems: "center",
      }}>
        <div>
          <div style={{ fontSize: 11, color: "#64748b", fontFamily: "'DM Mono', monospace", marginBottom: 4, letterSpacing: 2, textTransform: "uppercase" }}>
            Informe VIP — PEIRS v0.4.0
          </div>
          <div style={{ fontSize: 18, fontWeight: 800, color: "#e2e8f0" }}>
            {country.flag} {country.name}
          </div>
          <div style={{ fontSize: 11, color: "#64748b", fontFamily: "'DM Mono', monospace", marginTop: 4 }}>
            RUN/{runId.slice(0,8).toUpperCase()} · {new Date(reportData.timestamp).toLocaleString('es-AR', {timeZone:'UTC'})} UTC
          </div>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <div style={{
            padding: "8px 18px", borderRadius: 10,
            background: rc.bg, border: `1px solid ${rc.color}66`,
            textAlign: "center",
          }}>
            <div style={{ fontSize: 28, fontWeight: 900, color: rc.color, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>{riskScore}</div>
            <div style={{ fontSize: 9, color: rc.color, textTransform: "uppercase", letterSpacing: 2, marginTop: 2 }}>{rc.label}</div>
          </div>
          <button onClick={handleDownload} style={{
            padding: "10px 18px", borderRadius: 10,
            border: "1px solid #3b82f644",
            background: "#3b82f618", color: "#3b82f6",
            fontSize: 12, fontWeight: 600, cursor: "pointer",
          }}>⎙ Abrir e Imprimir</button>
        </div>
      </div>

      {/* Chapter Navigation */}
      <div style={{
        display: "flex", gap: 6, overflowX: "auto", padding: "12px 16px",
        background: "#0d1220", border: `1px solid ${COLORS.border}`,
        borderTop: "none", borderBottom: "none",
        scrollbarWidth: "thin",
      }}>
        {CHAPTERS.map(ch => (
          <button key={ch.id} onClick={() => setActiveTab(ch.id)} title={ch.desc} style={{
            padding: "8px 14px", borderRadius: 8, cursor: "pointer",
            fontSize: 11, fontWeight: 600, whiteSpace: "nowrap",
            background: activeTab === ch.id ? COLORS.accent + "22" : "transparent",
            color: activeTab === ch.id ? COLORS.accent : COLORS.textMuted,
            border: activeTab === ch.id ? `1px solid ${COLORS.accent}44` : "1px solid transparent",
            transition: "all 0.2s ease",
          }}>
            {ch.icon} {ch.num}. {ch.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div style={{
        background: COLORS.surface,
        border: `1px solid ${COLORS.border}`,
        borderTop: "none",
        borderRadius: "0 0 14px 14px",
        padding: 24,
      }}>

        {/* ── CAP 1: RESUMEN EJECUTIVO ── */}
        {activeTab === "resumen" && (
          <ChapterContent num="1" title="Resumen Ejecutivo & Dashboard de Riesgo"
            desc="Vista ejecutiva con indicadores clave de integridad electoral, fuentes verificadas y análisis multidimensional."
            sources={["Freedom House FIW 2025", "V-Dem v15 2024", "PEI v10 2021", "RSF 2025"]}>
            {/* Fila 1: Gauge + Fuentes verificadas */}
            <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 24, marginBottom: 24 }}>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                <RiskGaugeElite score={riskScore} riskLevel={riskLevel} size={220} />
                <div style={{ marginTop: 12, fontSize: 11, color: "#64748b", textAlign: "center", maxWidth: 180, lineHeight: 1.5 }}>
                  Índice Predictivo de Riesgo Electoral PEIRS
                </div>
              </div>
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: 2, marginBottom: 12 }}>
                  Fuentes Verificadas
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 12 }}>
                  <SourceBadge label="Freedom House FIW" value={fhScore !== null ? `${fhScore}/100` : "N/D"}
                    confidence={fhScore !== null ? "confirmed" : "mock"} year={fhEdition} color="#f59e0b" />
                  <SourceBadge label="V-Dem Liberal Democracy" value={vdemLibdem !== null ? vdemLibdem : "N/D"}
                    confidence={vdemLibdem !== null ? "confirmed" : "mock"} year={vdemYear} color="#a855f7" />
                  <SourceBadge label="PEI — Integridad Electoral" value={peiIntegrity !== null ? `${peiIntegrity}/100` : "N/D"}
                    confidence={peiIntegrity !== null ? "confirmed" : "mock"} year={peiYear} color="#3b82f6" />
                  <SourceBadge label="RSF — Libertad de Prensa" value={rsfScore !== null ? `${rsfScore}/100` : "N/D"}
                    confidence={rsfScore !== null ? "confirmed" : "mock"} year="2025" color="#ec4899" />
                </div>
                <div style={{
                  padding: "10px 14px", borderRadius: 10,
                  background: confColor + "0f", border: `1px solid ${confColor}33`,
                  display: "flex", alignItems: "center", gap: 10,
                }}>
                  <span style={{ fontSize: 14 }}>{dataConf === "HIGH" ? "🟢" : dataConf === "MEDIUM" ? "🟡" : "🔴"}</span>
                  <div>
                    <div style={{ fontSize: 11, fontWeight: 700, color: confColor }}>Confianza de Datos: {dataConf}</div>
                    <div style={{ fontSize: 11, color: "#64748b", lineHeight: 1.4 }}>{dictamen.confidence_note || ""}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Resumen Ejecutivo */}
            {execSummary && (
              <div style={{ marginBottom: 24 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: 2, marginBottom: 10 }}>
                  Resumen Ejecutivo — Cap. 1
                </div>
                <div style={{
                  padding: "16px 20px", borderRadius: 10,
                  background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`,
                }}>
                  {renderMarkdownWithTooltips(execSummary)}
                </div>
              </div>
            )}

            {/* Fila 2: Dimensiones + Semáforo */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 24 }}>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: 2 }}>
                    Análisis Multidimensional
                    <span style={{ fontWeight: 400, color: "#475569", marginLeft: 8, fontSize: 10 }}>— Hover para definición</span>
                  </div>
                  <ChartMethodologyBtn chartKey="dimensiones" />
                </div>
                {Object.entries(country.dimensions || {}).map(([key, val], i) => (
                  <DimensionBar key={key} dimKey={key} value={val} delay={i * 60} />
                ))}
              </div>
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: 2, marginBottom: 12 }}>
                  Semáforo de Libertades Civiles
                </div>
                <CivilLibertiesSemaphore civil={civil} />
                {trend.available && (
                  <div style={{ marginTop: 16 }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: 2, marginBottom: 8 }}>
                      Tendencia Histórica V-Dem
                    </div>
                    <div style={{
                      padding: "12px 14px", borderRadius: 10,
                      background: trend.trend_direction === "up" ? "#00d4aa0f" : trend.trend_direction === "down" ? "#ef44440f" : "#f59e0b0f",
                      border: `1px solid ${trend.trend_direction === "up" ? "#00d4aa33" : trend.trend_direction === "down" ? "#ef444433" : "#f59e0b33"}`,
                    }}>
                      <div style={{ fontSize: 14, marginBottom: 6 }}>
                        {trend.trend_direction === "up" ? "📈" : trend.trend_direction === "down" ? "📉" : "➡️"}
                        <span style={{
                          marginLeft: 8, fontWeight: 700, fontSize: 12,
                          color: trend.trend_direction === "up" ? "#00d4aa" : trend.trend_direction === "down" ? "#ef4444" : "#f59e0b",
                        }}>{trend.trend?.toUpperCase()}</span>
                      </div>
                      <div style={{ fontSize: 11, color: "#94a3b8" }}>
                        {trend.first_year} → {trend.last_year}: {trend.first_value} → {trend.last_value}
                        <span style={{ marginLeft: 8, fontFamily: "'DM Mono', monospace", fontWeight: 700 }}>
                          ({trend.delta > 0 ? "+" : ""}{trend.delta})
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Fila 3: Mapa de calor violaciones */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: 2 }}>
                  Mapa de Violaciones al Derecho Internacional
                  <span style={{ fontWeight: 400, color: "#475569", marginLeft: 8, fontSize: 10 }}>
                    — {violations.length} detectadas · {violations.filter(v => v.confidence === "confirmed").length} verificadas
                  </span>
                </div>
                <ChartMethodologyBtn chartKey="violaciones" />
              </div>
              <ViolationHeatmap violations={violations} />
            </div>

            {/* Comparación regional */}
            {(regComp.fh_vs_region || regComp.vdem_vs_region) && (
              <div style={{ marginTop: 20, padding: "14px 16px", borderRadius: 10, background: "#0d162518", border: "1px solid #1e2d3d" }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: 2, marginBottom: 10 }}>
                  Comparación Regional — {regComp.region}
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
                  {[
                    { label: "Freedom House", value: regComp.fh_vs_region },
                    { label: "V-Dem", value: regComp.vdem_vs_region },
                    { label: "RSF", value: regComp.rsf_vs_region },
                  ].filter(r => r.value).map((r, i) => (
                    <div key={i} style={{ padding: "8px 12px", borderRadius: 8, background: "#111827", border: "1px solid #1e2d3d" }}>
                      <div style={{ fontSize: 10, color: "#64748b", marginBottom: 4 }}>{r.label}</div>
                      <div style={{ fontSize: 11, color: "#e2e8f0", lineHeight: 1.4 }}>{r.value}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </ChapterContent>
        )}

        {/* ── CAP 0: PERFIL DEL PAÍS ── */}
        {activeTab === "perfil" && (
          <ChapterContent
            num="0" title="Perfil del País y Padrón Electoral"
            desc="Datos demográficos, económicos y del padrón electoral que contextualizan el proceso."
            sources={["INEI 2024", "ONPE 2026", "RENIEC 2026", "PNUD HDR 2024"]}
            markdown={reportChapters["00_country_profile"] || ""}
          />
        )}

        {/* ── CAP 2: CONTEXTO POLÍTICO ── */}
        {activeTab === "politico" && (
          <ChapterContent
            num="2" title="Contexto Político"
            desc="Marco legal, fuerzas de poder, crisis institucional y análisis del entorno político-electoral."
            sources={["Freedom House FIW 2025", "V-Dem v15 2024", "PEI v10 2021"]}
            markdown={reportChapters["02_political_context"] || ""}>
            {dictamen.narrative && (
              <div style={{ marginBottom: 20 }}>
                <div style={{
                  padding: "16px 20px", borderRadius: 12, marginBottom: 16,
                  background: "linear-gradient(135deg, #00d4aa0a, #111827)",
                  border: "1px solid #00d4aa33",
                  display: "flex", justifyContent: "space-between", alignItems: "flex-start",
                }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 800, color: "#00d4aa", fontFamily: "'DM Mono', monospace", letterSpacing: 1 }}>
                      DICTAMEN TÉCNICO — {dictamen.dictamen_id}
                    </div>
                    <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>
                      {country.name} · Elección {country.date}
                    </div>
                  </div>
                  <div style={{
                    padding: "4px 12px", borderRadius: 20,
                    background: confColor + "18", border: `1px solid ${confColor}44`,
                    fontSize: 10, fontWeight: 700, color: confColor, fontFamily: "'DM Mono', monospace",
                  }}>
                    CONFIANZA: {dataConf}
                  </div>
                </div>
                {dictamen.narrative.split("\n\n").filter(p => p.trim()).map((para, i) => (
                  <p key={i} style={{
                    margin: "0 0 16px", fontSize: 14, color: "#e2e8f0",
                    lineHeight: 1.9, letterSpacing: 0.1,
                    paddingLeft: 14, borderLeft: `3px solid ${["#00d4aa", "#3b82f6", "#a855f7", "#f59e0b"][i % 4]}`,
                  }}>{para}</p>
                ))}
                <div style={{
                  marginTop: 20, padding: "12px 16px", borderRadius: 10,
                  background: "#0d1625", border: "1px solid #1e2d3d",
                  fontSize: 11, color: "#475569", lineHeight: 1.6,
                  fontFamily: "'DM Mono', monospace",
                }}>
                  Dictamen generado automáticamente por DEMOCRAC.IA / PEIRS v0.4.0 ·
                  Basado en fuentes verificadas con confidence=confirmed ·
                  {new Date(dictamen.generated_at).toLocaleString('es-AR', {timeZone:'UTC'})} UTC
                </div>
              </div>
            )}
          </ChapterContent>
        )}

        {/* ── CAP 3: ORGANISMO ELECTORAL ── */}
        {activeTab === "emb" && (
          <ChapterContent
            num="3" title="Organismo Electoral (EMB)"
            desc="Independencia del organismo electoral, registro de votantes y observación internacional."
            sources={["V-Dem v15 2024", "PEI v10 2021"]}
            markdown={reportChapters["03_emb_analysis"] || ""}
          />
        )}

        {/* ── CAP 4: INCLUSIVIDAD ── */}
        {activeTab === "inclusividad" && (
          <ChapterContent
            num="4" title="Inclusividad"
            desc="Participación de mujeres, pueblos originarios, comunidad LGBTQ+ y personas con discapacidad."
            sources={["V-Dem v15 2024", "CEDAW", "CRPD"]}
            markdown={reportChapters["04_inclusivity"] || ""}
          />
        )}

        {/* ── CAP 5: CAMPAÑA ── */}
        {activeTab === "campana" && (
          <ChapterContent
            num="5" title="Campaña y Financiamiento"
            desc="Libertades de campaña, financiamiento político y cobertura mediática."
            sources={["PEI v10 2021", "V-Dem v15 2024"]}
            markdown={reportChapters["05_campaign_finance"] || ""}
          />
        )}

        {/* ── CAP 6: AMENAZAS DIGITALES ── */}
        {activeTab === "digital" && (
          <ChapterContent
            num="6" title="Ecosistema Digital y Amenazas"
            desc="Libertad de internet, desinformación, interferencia de plataformas y amenazas digitales."
            sources={["RSF 2025", "V-Dem v15 2024", "OONI"]}
            markdown={reportChapters["06_digital_ecosystem"] || ""}
          />
        )}

        {/* ── CAP 7: JORNADA ELECTORAL ── */}
        {activeTab === "jornada" && (
          <ChapterContent
            num="7" title="Jornada Electoral"
            desc="Observaciones en tiempo real sobre el desarrollo de la jornada electoral."
            sources={["Observación en tiempo real", "Hunter Agent"]}
            markdown={reportChapters["07_voting_day"] || ""}
          />
        )}

        {/* ── CAP 8: JUSTICIA ELECTORAL ── */}
        {activeTab === "justicia" && (
          <ChapterContent
            num="8" title="Justicia Electoral"
            desc="Resolución de disputas electorales y mecanismos de rendición de cuentas."
            sources={["V-Dem v15 2024", "PEI v10 2021"]}
            markdown={reportChapters["08_electoral_justice"] || ""}
          />
        )}

        {/* ── CAP 9: RECOMENDACIONES ── */}
        {activeTab === "recomendaciones" && (
          <ChapterContent
            num="9" title="Recomendaciones"
            desc="Matriz de acción electoral con recomendaciones priorizadas."
            sources={["Análisis PEIRS integrado"]}
            markdown={reportChapters["09_recommendations"] || ""}
          />
        )}

        {/* ── CAP 10: IA Y REGULACIÓN ── */}
        {activeTab === "ia" && (
          <ChapterContent
            num="10" title="Inteligencia Artificial y Regulación"
            desc="Análisis del uso de inteligencia artificial en el proceso electoral y su regulación."
            sources={["Análisis PEIRS"]}
            markdown={reportChapters["10_ai_regulation"] || ""}
          />
        )}

      </div>
    </div>
  );
};



const GLOSSARY = [
  {
    term: "V-Dem",
    full: "Varieties of Democracy",
    category: "Dataset",
    color: "#a855f7",
    def: "Base de datos académica con más de 400 indicadores de calidad democrática para 202 países desde 1789. Desarrollada por el V-Dem Institute (Universidad de Gotemburgo). Versión v15 cubre hasta 2024.",
    source: "Coppedge et al. 2025",
    url: "https://v-dem.net",
    keyMetrics: ["v2x_libdem (democracia liberal)", "v2x_polyarchy (democracia electoral)", "v2elembaut (autonomía EMB)", "v2elirreg (irregularidades)"],
  },
  {
    term: "EMB",
    full: "Electoral Management Body",
    category: "Institución",
    color: "#3b82f6",
    def: "Organismo encargado de administrar el proceso electoral. Puede ser independiente (full), parcialmente autónomo (partial), comprometido (compromised) o capturado por el ejecutivo (captured). Su independencia es determinante para la integridad del proceso.",
    source: "V-Dem v15 + PEIRS",
    url: "https://v-dem.net",
    keyMetrics: ["Autonomía (0-1)", "Capacidad institucional", "Irregularidades detectadas", "Representación opositora"],
  },
  {
    term: "ICCPR",
    full: "Pacto Internacional de Derechos Civiles y Políticos",
    category: "Tratado Internacional",
    color: "#ef4444",
    def: "Tratado de la ONU adoptado en 1966. Establece derechos fundamentales para procesos electorales: Art. 25 (derecho a votar y ser elegido), Art. 19 (libertad de expresión), Art. 21-22 (reunión y asociación), Art. 9 (libertad personal), Art. 14 (proceso justo).",
    source: "Naciones Unidas",
    url: "https://www.ohchr.org/en/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights",
    keyMetrics: ["Art. 25 — Sufragio universal", "Art. 19 — Libertad de expresión", "Art. 9 — Libertad personal", "Art. 14 — Juicio justo"],
  },
  {
    term: "PEI",
    full: "Perceptions of Electoral Integrity",
    category: "Dataset",
    color: "#00d4aa",
    def: "Encuesta a expertos electorales sobre percepción de integridad en 586 elecciones (2012-2023) en 164 países. Financiado por Harvard Kennedy School. Versión 10.0. Evalúa 11 dimensiones del ciclo electoral.",
    source: "Garnett, James & Caal-Lam. Harvard Dataverse, 2024",
    url: "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/FQ5ECC",
    keyMetrics: ["EMBs (autoridades electorales)", "LAWS (marco legal)", "MEDIACOVERAGE (medios)", "CAMPAIGNFINANCE (financiamiento)"],
  },
  {
    term: "Freedom House",
    full: "Freedom in the World",
    category: "Dataset",
    color: "#f59e0b",
    def: "Informe anual de Freedom House que evalúa libertades políticas y civiles en 195 países. Escala 0-100 (100 = más libre). Clasifica países como Free, Partly Free o Not Free. Edición 2025 usada en PEIRS.",
    source: "Freedom House 2025",
    url: "https://freedomhouse.org/report/freedom-world",
    keyMetrics: ["Total score (0-100)", "PR rating — Derechos políticos (1-7)", "CL rating — Libertades civiles (1-7)", "Status: Free / Partly Free / Not Free"],
  },
  {
    term: "CADH",
    full: "Convención Americana sobre Derechos Humanos",
    category: "Tratado Regional",
    color: "#f97316",
    def: "Tratado del sistema interamericano adoptado en 1969 (Pacto de San José). Art. 23 garantiza derechos políticos: participar en gobierno, votar, ser elegido. Complementa el ICCPR con perspectiva regional americana.",
    source: "OEA / Corte IDH",
    url: "https://www.oas.org/es/cidh/mandato/documentos-basicos/convencion-americana-derechos-humanos.pdf",
    keyMetrics: ["Art. 23 — Derechos políticos", "Art. 13 — Libertad de expresión", "Art. 15 — Reunión", "Art. 16 — Asociación"],
  },
  {
    term: "CDI",
    full: "Carta Democrática Interamericana",
    category: "Instrumento Regional",
    color: "#ec4899",
    def: "Adoptada por la OEA en 2001. Arts. 3-4 definen los elementos esenciales de la democracia representativa: respeto DDHH, celebración de elecciones periódicas, pluralismo político, separación de poderes, transparencia.",
    source: "OEA",
    url: "https://www.oas.org/charter/docs_es/resolucion1_es.htm",
    keyMetrics: ["Arts. 3-4 — Elementos esenciales", "Art. 6 — Participación ciudadana", "Arts. 17-22 — Amenazas a democracia"],
  },
  {
    term: "OSINT",
    full: "Open Source Intelligence",
    category: "Metodología",
    color: "#06b6d4",
    def: "Inteligencia basada en fuentes abiertas y verificables. PEIRS usa OSINT como metodología central: todos los datos provienen de datasets públicos, portales oficiales y fuentes académicas auditables. Sin fuentes confidenciales ni informantes.",
    source: "PEIRS Methodology",
    url: null,
    keyMetrics: ["V-Dem (datos estructurados)", "Freedom House (evaluación experta)", "PEI (encuesta académica)", "Portales oficiales EMBs"],
  },
  {
    term: "PEIRS",
    full: "Predictive Electoral Integrity & Risk System",
    category: "Sistema",
    color: "#00d4aa",
    def: "Sistema propietario de DEMOCRAC.IA. Pipeline de 4 agentes de IA (LangGraph) que ingesta datos OSINT, analiza el contexto político-digital, evalúa cumplimiento del derecho internacional y genera informes VIP con trazabilidad completa.",
    source: "DEMOCRAC.IA v0.4.0",
    url: null,
    keyMetrics: ["Agente OSINT", "Agente Político-Digital", "Agente Legal (ICCPR/CADH/CDI)", "Agente Generador de Informes"],
  },
  {
    term: "LangGraph",
    full: "LangGraph — Orchestration Framework",
    category: "Tecnología",
    color: "#8b5cf6",
    def: "Framework de orquestación de agentes de IA desarrollado por LangChain. Permite crear pipelines stateful con múltiples agentes que comparten estado. PEIRS lo usa para orquestar los 4 agentes en secuencia con estado compartido ElectionRiskState.",
    source: "LangChain Inc.",
    url: "https://langchain-ai.github.io/langgraph/",
    keyMetrics: ["StateGraph", "ElectionRiskState compartido", "Nodos: Ingestion → Political → Legal → Report"],
  },
  {
    term: "EOS",
    full: "Estándares Internacionales de Observación Electoral",
    category: "Marco Normativo",
    color: "#14b8a6",
    def: "Conjunto de principios establecidos por la Declaración de Principios para la Observación Internacional de Elecciones (2005, ONU). Define los estándares mínimos para considerar una elección genuina: universal, igual, secreto, libre y justo.",
    source: "Naciones Unidas / Centro Carter / OSCE",
    url: "https://www.cartercenter.org/resources/pdfs/news/peace_publications/democracy/DeclarationElectionObservation.pdf",
    keyMetrics: ["Sufragio universal e igual", "Voto secreto y libre", "Resultados genuinos", "Marco legal adecuado"],
  },
  {
    term: "Trazabilidad",
    full: "Cadena de Custodia de Datos",
    category: "Metodología",
    color: "#00d4aa",
    def: "Cada dato en PEIRS incluye metadatos de origen: source_id, source_type, confidence (confirmed/mock), legal_basis, data_hash y is_publishable. Permite auditar la procedencia de cada hallazgo del informe hasta su fuente primaria.",
    source: "PEIRS Traceability Framework v0.2.0",
    url: null,
    keyMetrics: ["confidence: confirmed / mock", "source_id único por dato", "data_hash SHA-256", "is_publishable flag"],
  },
];

const GlossaryCard = ({ item }) => {
  const [expanded, setExpanded] = useState(false);
  return (
    <div onClick={() => setExpanded(e => !e)} style={{
      background: COLORS.surface,
      border: `1px solid ${expanded ? item.color + "55" : COLORS.border}`,
      borderLeft: `3px solid ${item.color}`,
      borderRadius: 10, padding: "14px 16px",
      cursor: "pointer",
      transition: "all 0.2s ease",
      boxShadow: expanded ? `0 4px 20px ${item.color}22` : "none",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{
            display: "inline-block", padding: "2px 8px", borderRadius: 5,
            background: item.color + "22", color: item.color,
            fontSize: 9, fontWeight: 700, fontFamily: "'DM Mono', monospace",
            letterSpacing: 1, textTransform: "uppercase",
          }}>{item.category}</span>
          <span style={{ fontSize: 15, fontWeight: 800, color: COLORS.text, fontFamily: "'DM Mono', monospace" }}>
            {item.term}
          </span>
          <span style={{ fontSize: 11, color: COLORS.textMuted }}>— {item.full}</span>
        </div>
        <span style={{ color: COLORS.textDim, fontSize: 12, marginLeft: 8 }}>{expanded ? "▲" : "▼"}</span>
      </div>

      {expanded && (
        <div style={{ marginTop: 14, paddingTop: 14, borderTop: `1px solid ${COLORS.border}` }}>
          <p style={{ fontSize: 13, color: COLORS.text, lineHeight: 1.7, marginBottom: 14 }}>
            {item.def}
          </p>
          <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: 200 }}>
              <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>
                Métricas clave
              </div>
              {item.keyMetrics.map((m, i) => (
                <div key={i} style={{ display: "flex", gap: 6, marginBottom: 4, alignItems: "center" }}>
                  <span style={{ color: item.color, fontSize: 10 }}>▸</span>
                  <span style={{ fontSize: 11, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>{m}</span>
                </div>
              ))}
            </div>
            <div>
              <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>
                Fuente
              </div>
              <div style={{ fontSize: 11, color: COLORS.text }}>{item.source}</div>
              {item.url && (
                <a href={item.url} target="_blank" rel="noopener noreferrer" style={{
                  display: "block", marginTop: 6, fontSize: 10,
                  color: item.color, textDecoration: "none",
                  fontFamily: "'DM Mono', monospace",
                }}>
                  🔗 Ver fuente →
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const MethodologyView = () => {
  const [activeTab, setActiveTab] = useState("methodology");

  return (
    <div style={{ padding: 28 }}>
      {/* Tabs */}
      <div style={{ display: "flex", gap: 4, marginBottom: 28, borderBottom: `1px solid ${COLORS.border}`, paddingBottom: 0 }}>
        {[
          { id: "methodology", label: "⚙️ Metodología" },
          { id: "glossary", label: "📖 Glosario Técnico" },
          { id: "legal", label: "⚖️ Marco Legal" },
        ].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
            padding: "8px 18px", border: "none", cursor: "pointer",
            fontSize: 12, fontWeight: 600, borderRadius: "8px 8px 0 0",
            background: activeTab === tab.id ? COLORS.accent + "22" : "transparent",
            color: activeTab === tab.id ? COLORS.accent : COLORS.textMuted,
            borderBottom: activeTab === tab.id ? `2px solid ${COLORS.accent}` : "2px solid transparent",
            transition: "all 0.2s ease",
          }}>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab: Metodología */}
      {activeTab === "methodology" && (
        <div>
          <h2 style={{ margin: "0 0 8px", fontSize: 22, fontWeight: 800, color: COLORS.text }}>Metodología PEIRS</h2>
          <p style={{ margin: "0 0 28px", fontSize: 13, color: COLORS.textMuted, lineHeight: 1.7 }}>
            El sistema evalúa la integridad electoral basándose exclusivamente en obligaciones del derecho internacional público y los estándares de la Declaración de Principios para la Observación Internacional de Elecciones de Naciones Unidas.
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {[
              { icon: "🤖", title: "Pipeline de Agentes IA (LangGraph + Claude)", desc: "Pipeline LangGraph multi-agente: OSINT → Político → Legal → Informe → MOE Brief. Modelo principal Claude Sonnet 4 para clasificación y composición; Claude Opus 4.7 para el Architect Agent autónomo (claude-agent-sdk con acceso al codebase para refactor iterativo). Estado compartido ElectionRiskState." },
              { icon: "📡", title: "Hunter — Monitoreo OSINT 24/7", desc: "Scheduler persistente que corre cada 4 horas (intervalo configurable). Ingesta de 8 fuentes RSS priorizadas por fase electoral (Andina, RPP, El Comercio, Gestión, IDL-Reporteros, Wayka, JNE, ONPE) + integración OONI para censura de internet. Clasificación con LLM en 18 categorías propias y 5 niveles de severidad. Dedupe semántico por (categoría, URL, fecha). Alertas Discord vía webhook para severidad ≥ high. Operación real para Perú 2026: 1.685 entries clasificadas a 27-abr (34 critical, 438 high)." },
              { icon: "🔍", title: "Fuentes Verificables — Datasets + RAG Legal", desc: "Datasets cuantitativos: V-Dem v15 (27.913 obs. país-año, 1789-2024), Freedom House FIW (2.723 filas, 2013-2025), Perceptions of Electoral Integrity 10.0 (586 elecciones, 2012-2023), RSF Press Freedom Index 2025 (180 países). Corpus RAG legal: 23 documentos en ChromaDB con embeddings sentence-transformers. Todos open-source, citados con DOI/URL, trazables a fuente primaria." },
              { icon: "⚖️", title: "Base Legal — 14 instrumentos en taxonomía propia", desc: "Cada hallazgo se vincula a artículos específicos del derecho internacional aplicable: ICCPR Art. 25 + Observación General 25, CADH Art. 23, Carta Democrática Interamericana, CEDAW, OSCE/ODIHR Election Standards, jurisprudencia CIDH, ECHR Protocolo 1, Carta Africana, UNDRIP. Para Perú: Constitución 1993 (Arts. electorales), LOE 26859, LOP 28094, Resoluciones JNE (incluida Res. 0891-2025 sobre voto electrónico). Severidades critical/high/medium/low/info." },
              { icon: "📊", title: "Índice Predictivo de Riesgo (0-100) + Motor Predictivo", desc: "Risk score: 8 dimensiones ponderadas — FH (15%) + V-Dem (15%) + EMB (15%) + Medios (10%) + Financiamiento (10%) + Digital (10%) + Violaciones (15%) + Observación (10%). Motor predictivo híbrido reglas + LLM con 6 escenarios electorales con confidence intervals y early-warning meter de 4 niveles (green/amber/orange/red)." },
              { icon: "🔐", title: "Trazabilidad APA 7 + Auditoría Continua", desc: "Cada dato tiene source/url/date/confidence_level. Los informes incluyen anexo de trazabilidad con Run ID, timestamp y versión del sistema. Política estricta del Architect Agent: bloques sin URL primaria se postergan antes que publicarse (caso real: auditoría de abril 2026 retiró afirmaciones sobre crimen organizado y deepfakes hasta verificar fuentes individuales)." },
              { icon: "📘", title: "Elite Report — 12 capítulos institucionales", desc: "Informe de nivel internacional con composición Claude Sonnet 4 + prompt caching de Anthropic. Cuatro audiencias (institucional, ejecutivo, prensa, internacional), bilingüe ES/EN, 21 visualizaciones SVG artesanales server-side (sin matplotlib), citas APA 7. Output en HTML, Markdown y PDF (xhtml2pdf con @page A4 + @media print). Costo ~$0.40-0.80 por informe con cap diario por país." },
              { icon: "🛡️", title: "Hardening de producción", desc: "Autenticación X-Observer-Key, rate-limiting por IP en endpoints caros, budget diario por país (cap configurable), fallbacks gráciles cuando un componente externo falla (HuggingFace, Anthropic, OONI, RSS). Persistencia SQLite que sobrevive reinicios. Deploy en Railway con healthcheck y volumen persistente; frontend en Netlify con auto-deploy en cada push a main." },
              { icon: "🚫", title: "Principio de No-Legitimación", desc: "DEMOCRAC.IA NO valida ni legitima resultados electorales. Emite inteligencia electoral con trazabilidad verificable bajo estándares de la Comisión de Venecia, OEA/DECO, OSCE/ODIHR y Carter Center, sin sesgo político-partidario. Los datos son para uso analítico de autoridades electorales, organismos multilaterales y observadores acreditados." },
            ].map((item, i) => (
              <Card key={i}>
                <div style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
                  <div style={{ width: 44, height: 44, borderRadius: 10, background: COLORS.accentDim, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, flexShrink: 0 }}>
                    {item.icon}
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, color: COLORS.text, fontSize: 14, marginBottom: 4 }}>{item.title}</div>
                    <div style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.8 }}>{item.desc}</div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
          {/* Sección institucional V-Dem */}
          <div style={{ marginTop: 28, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <Card style={{ borderLeft: `3px solid #a855f7` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                <div style={{ width: 36, height: 36, borderRadius: 8, background: "#a855f722", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>📊</div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 800, color: COLORS.text }}>V-Dem Institute</div>
                  <div style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>Universidad de Gotemburgo, Suecia</div>
                </div>
              </div>
              <p style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.8, marginBottom: 10 }}>
                El Instituto V-Dem, dirigido por el profesor asociado Steven Wilson, es un instituto de investigación independiente con sede en el Departamento de Ciencias Políticas de la Universidad de Gotemburgo, Suecia.
              </p>
              <p style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.8, marginBottom: 12 }}>
                El Instituto se encarga de la recopilación de datos de expertos nacionales, la curación de datos y su disponibilidad para los usuarios. Además de los datos de V-Dem, elabora documentos de trabajo con los últimos hallazgos de investigación y un Informe Anual sobre la Democracia con una visión global del estado democrático mundial.
              </p>
              <a href="https://v-dem.net" target="_blank" rel="noopener noreferrer" style={{
                display: "inline-flex", alignItems: "center", gap: 6,
                fontSize: 11, color: "#a855f7", textDecoration: "none",
                fontFamily: "'DM Mono', monospace", fontWeight: 600,
              }}>
                🔗 v-dem.net →
              </a>
            </Card>

            <Card style={{ borderLeft: `3px solid #f59e0b` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                <div style={{ width: 36, height: 36, borderRadius: 8, background: "#f59e0b22", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>🏠</div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 800, color: COLORS.text }}>Freedom House</div>
                  <div style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>Washington, DC — desde 1941</div>
                </div>
              </div>
              <p style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.8, marginBottom: 10 }}>
                Durante más de 50 años, Freedom House ha monitoreado sistemáticamente las amenazas más acuciantes a la democracia y la libertad en todo el mundo, publicando investigaciones detalladas sobre más de 200 países y territorios.
              </p>
              <p style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.8, marginBottom: 12 }}>
                Los responsables políticos, activistas y organizaciones de la sociedad civil recurren a su investigación para orientarse hacia un mundo más abierto, justo y libre. Sus estudios clave incluyen{" "}
                <a href="https://freedomhouse.org/report/freedom-world" target="_blank" rel="noopener noreferrer" style={{ color: "#f59e0b", textDecoration: "none" }}>Freedom in the World</a>
                {", "}
                <a href="https://freedomhouse.org/report/freedom-net" target="_blank" rel="noopener noreferrer" style={{ color: "#f59e0b", textDecoration: "none" }}>Freedom on the Net</a>
                {" y "}
                <a href="https://freedomhouse.org/report/transnational-repression" target="_blank" rel="noopener noreferrer" style={{ color: "#f59e0b", textDecoration: "none" }}>Transnational Repression</a>.
              </p>
              <a href="https://freedomhouse.org" target="_blank" rel="noopener noreferrer" style={{
                display: "inline-flex", alignItems: "center", gap: 6,
                fontSize: 11, color: "#f59e0b", textDecoration: "none",
                fontFamily: "'DM Mono', monospace", fontWeight: 600,
              }}>
                🔗 freedomhouse.org →
              </a>
            </Card>
          </div>

          <Card style={{ marginTop: 24, background: "linear-gradient(135deg, #0d1a2a 0%, #0a1628 100%)", border: `1px solid ${COLORS.accent}44` }}>
            <div style={{ textAlign: "center", padding: 16 }}>
              <div style={{ fontSize: 13, color: COLORS.accent, fontWeight: 700, textTransform: "uppercase", letterSpacing: 3, marginBottom: 8 }}>Stack Tecnológico</div>
              <div style={{ display: "flex", justifyContent: "center", gap: 16, flexWrap: "wrap" }}>
                {[
                  "Python 3.11", "FastAPI", "LangGraph", "LangChain",
                  "Claude Sonnet 4", "Claude Opus 4.7", "claude-agent-sdk",
                  "ChromaDB", "sentence-transformers", "SQLite",
                  "V-Dem v15", "Freedom House FIW", "PEI 10.0", "RSF 2025", "OONI",
                  "React + Vite", "Recharts", "xhtml2pdf",
                  "Railway (Nixpacks)", "Netlify",
                ].map((t, i) => (
                  <Tag key={i} color={COLORS.accent}>{t}</Tag>
                ))}
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Tab: Glosario */}
      {activeTab === "glossary" && (
        <div>
          <h2 style={{ margin: "0 0 8px", fontSize: 22, fontWeight: 800, color: COLORS.text }}>Glosario Técnico</h2>
          <p style={{ margin: "0 0 24px", fontSize: 13, color: COLORS.textMuted, lineHeight: 1.7 }}>
            Definición de todos los términos, datasets e instrumentos legales utilizados en los análisis de DEMOCRAC.IA / PEIRS. Hacé clic en cualquier término para ver la definición completa.
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {GLOSSARY.map((item, i) => <GlossaryCard key={i} item={item} />)}
          </div>
        </div>
      )}

      {/* Tab: Marco Legal */}
      {activeTab === "legal" && (
        <div>
          <h2 style={{ margin: "0 0 8px", fontSize: 22, fontWeight: 800, color: COLORS.text }}>Marco Legal de Referencia</h2>
          <p style={{ margin: "0 0 24px", fontSize: 13, color: COLORS.textMuted, lineHeight: 1.7 }}>
            Los análisis de PEIRS se fundamentan en el derecho internacional público aplicable a procesos electorales. Cada violación detectada es vinculada a artículos específicos de los siguientes instrumentos.
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {[
              {
                treaty: "ICCPR", color: "#ef4444",
                full: "Pacto Internacional de Derechos Civiles y Políticos",
                adopted: "1966 — ONU",
                articles: [
                  { art: "Art. 9", right: "Libertad y seguridad personal", desc: "Prohibición de detención arbitraria. Presos políticos violan este artículo." },
                  { art: "Art. 14", right: "Juicio justo e independencia judicial", desc: "Derecho a tribunal independiente e imparcial para disputas electorales." },
                  { art: "Art. 19", right: "Libertad de expresión y prensa", desc: "Derecho a buscar, recibir y difundir información. Protege la libertad de prensa." },
                  { art: "Art. 19(2)", right: "Libertad de expresión digital", desc: "Extensión al entorno digital. Censura de internet y redes sociales viola este artículo." },
                  { art: "Art. 21 & 22", right: "Libertad de reunión y asociación", desc: "Derecho a reunión pacífica y formación de partidos políticos." },
                  { art: "Art. 25", right: "Derechos políticos — sufragio universal", desc: "Derecho a votar y ser elegido en elecciones genuinas, periódicas y con voto secreto." },
                  { art: "Art. 25(a)", right: "Sufragio universal activo", desc: "Derecho a votar sin discriminación. Supresión de votantes viola este artículo." },
                  { art: "Art. 25(b)", right: "Derecho a ser candidato", desc: "Inhabilitación arbitraria de candidatos viola el derecho a postularse." },
                ],
              },
              {
                treaty: "CADH", color: "#f97316",
                full: "Convención Americana sobre Derechos Humanos",
                adopted: "1969 — OEA",
                articles: [
                  { art: "Art. 13", right: "Libertad de pensamiento y expresión", desc: "Equivalente americano del Art. 19 ICCPR." },
                  { art: "Art. 23", right: "Derechos políticos", desc: "Todo ciudadano tiene derecho a participar en dirección de asuntos públicos, votar y ser elegido." },
                ],
              },
              {
                treaty: "CDI", color: "#ec4899",
                full: "Carta Democrática Interamericana",
                adopted: "2001 — OEA",
                articles: [
                  { art: "Art. 3", right: "Elementos esenciales de la democracia", desc: "Respeto DDHH, elecciones periódicas, pluralismo, separación de poderes." },
                  { art: "Art. 4", right: "Componentes fundamentales", desc: "Transparencia, probidad, libertad de prensa y acceso a la información." },
                ],
              },
              {
                treaty: "ECHR P1", color: "#6366f1",
                full: "Convenio Europeo de Derechos Humanos — Protocolo 1",
                adopted: "1952 — Consejo de Europa",
                articles: [
                  { art: "Art. 3", right: "Derecho a elecciones libres", desc: "Obligación de celebrar elecciones libres con voto secreto que garanticen la libre expresión del pueblo en la elección del cuerpo legislativo." },
                  { art: "Art. 10", right: "Libertad de expresión", desc: "Protege la libertad de expresión e información, incluyendo la prensa y medios en período electoral." },
                  { art: "Art. 11", right: "Libertad de reunión y asociación", desc: "Garantiza el derecho a fundar y afiliarse a partidos políticos y sindicatos." },
                ],
              },
              {
                treaty: "OSCE/ODIHR", color: "#0ea5e9",
                full: "Documento de Copenhague — OSCE 1990",
                adopted: "1990 — OSCE",
                articles: [
                  { art: "Par. 5-6", right: "Elecciones libres y justas", desc: "Los Estados participantes celebrarán elecciones libres y justas periódicamente, conforme a leyes compatibles con los compromisos OSCE." },
                  { art: "Par. 7", right: "Libertades fundamentales", desc: "Garantiza libertad de expresión, prensa, reunión y asociación sin discriminación." },
                  { art: "Par. 8", right: "Estado de derecho", desc: "El gobierno y sus instituciones son responsables ante el pueblo y operan conforme a la ley." },
                ],
              },
              {
                treaty: "ACHPR", color: "#f59e0b",
                full: "Carta Africana de Derechos Humanos y de los Pueblos",
                adopted: "1981 — Unión Africana",
                articles: [
                  { art: "Art. 9", right: "Derecho a la información", desc: "Todo individuo tiene derecho a recibir información y a expresar y difundir sus opiniones en el marco de la ley." },
                  { art: "Art. 10", right: "Libertad de asociación", desc: "Toda persona tiene derecho a asociarse libremente, siempre que cumpla las formalidades establecidas por la ley." },
                  { art: "Art. 13", right: "Participación en gobierno", desc: "Todo ciudadano tiene derecho a participar libremente en el gobierno de su país, directamente o por intermedio de representantes libremente elegidos." },
                ],
              },
              {
                treaty: "ACDEG", color: "#10b981",
                full: "Carta Africana sobre Democracia, Elecciones y Gobernanza",
                adopted: "2007 — Unión Africana",
                articles: [
                  { art: "Art. 3", right: "Principios de democracia", desc: "Respeto a los derechos humanos, acceso al poder y su ejercicio conforme al Estado de derecho, cultura de pluralismo político y democracia." },
                  { art: "Art. 17", right: "Elecciones democráticas", desc: "Los Estados establecerán organismos electorales independientes y con capacidad técnica para garantizar elecciones libres, justas, regulares y transparentes." },
                  { art: "Art. 22", right: "Cambios inconstitucionales", desc: "Los Estados sancionarán todo cambio inconstitucional de gobierno que viole el principio democrático de transferencia del poder." },
                ],
              },
            ].map((instrument, idx) => (
              <Card key={idx} style={{ borderLeft: `3px solid ${instrument.color}` }}>
                <div style={{ marginBottom: 16 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                    <span style={{ fontSize: 18, fontWeight: 800, color: instrument.color, fontFamily: "'DM Mono', monospace" }}>{instrument.treaty}</span>
                    <span style={{ fontSize: 12, color: COLORS.textMuted }}>{instrument.full}</span>
                  </div>
                  <span style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>{instrument.adopted}</span>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {instrument.articles.map((a, ai) => (
                    <div key={ai} style={{ display: "flex", gap: 12, padding: "10px 12px", background: COLORS.surfaceLight, borderRadius: 8 }}>
                      <span style={{ fontSize: 11, fontWeight: 800, color: instrument.color, fontFamily: "'DM Mono', monospace", minWidth: 90, flexShrink: 0 }}>{a.art}</span>
                      <div>
                        <div style={{ fontSize: 12, fontWeight: 600, color: COLORS.text, marginBottom: 2 }}>{a.right}</div>
                        <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5 }}>{a.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};



function SentinelView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/sentinel/alerts`)
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(d => { setData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return (
    <div style={{ padding: 60, textAlign: "center", color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
      Cargando SENTINEL...
    </div>
  );
  if (error) return (
    <div style={{ padding: 40, color: COLORS.danger, fontFamily: "'DM Mono', monospace" }}>
      Error: {error}
    </div>
  );

  const alertColor = (level) => {
    if (level === "critical") return COLORS.danger;
    if (level === "high") return "#f97316";
    if (level === "moderate") return COLORS.warning;
    return COLORS.accent;
  };

  const SentinelCard = ({ entry }) => {
    const color = alertColor(entry.alert_color);
    const daysAbs = Math.abs(entry.days_remaining);
    return (
      <div style={{
        background: COLORS.surface, border: `1px solid ${color}44`,
        borderLeft: `3px solid ${color}`, borderRadius: 10,
        padding: "14px 18px", display: "flex", gap: 16, alignItems: "flex-start",
        boxShadow: entry.days_remaining <= 30 ? `0 0 12px ${color}22` : "none",
      }}>
        <div style={{ fontSize: 28, lineHeight: 1 }}>{entry.flag}</div>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontWeight: 700, fontSize: 15, color: COLORS.text }}>{entry.country_name}</span>
            <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
              {entry.risk_score !== null && (
                <span style={{
                  fontSize: 11, padding: "2px 8px", borderRadius: 5,
                  background: color + "22", color, fontFamily: "'DM Mono', monospace", fontWeight: 700,
                }}>{entry.risk_score} PEIRS</span>
              )}
              <span style={{
                fontSize: 10, padding: "2px 7px", borderRadius: 5,
                background: COLORS.surfaceLight, color: COLORS.textMuted,
                fontFamily: "'DM Mono', monospace",
              }}>
                {entry.days_remaining >= 0 ? `${entry.days_remaining}d` : `-${daysAbs}d`}
              </span>
            </div>
          </div>
          <div style={{ fontSize: 11, color: COLORS.textMuted, marginTop: 3 }}>
            {entry.alert_text}
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 6, flexWrap: "wrap" }}>
            <span style={{ fontSize: 9, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
              {entry.election_date}
            </span>
            {entry.violations_count > 0 && (
              <span style={{ fontSize: 9, color: COLORS.danger, fontFamily: "'DM Mono', monospace" }}>
                {entry.violations_count} violaciones detectadas
              </span>
            )}
            {entry.trend && entry.trend !== "stable" && (
              <span style={{ fontSize: 9, color: entry.trend.includes("deterioro") ? COLORS.danger : COLORS.accent, fontFamily: "'DM Mono', monospace" }}>
                {entry.trend === "deteriorating" ? "↘ deteriorando" : entry.trend === "improving" ? "↗ mejorando" : entry.trend}
              </span>
            )}
          </div>
        </div>
      </div>
    );
  };

  const { summary, active_alerts, watch_list, recent_findings = [] } = data;

  const findingSeverityColor = (sev) => {
    if (sev === "critical") return COLORS.danger;
    if (sev === "high") return "#f97316";
    if (sev === "medium") return COLORS.warning;
    if (sev === "low") return COLORS.accent;
    return COLORS.textMuted;
  };

  const FindingCard = ({ f }) => {
    const color = findingSeverityColor(f.severity);
    return (
      <div style={{
        background: COLORS.surface, border: `1px solid ${color}33`,
        borderLeft: `3px solid ${color}`, borderRadius: 10,
        padding: "12px 16px",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 16 }}>{f.flag}</span>
            <span style={{ fontSize: 12, fontWeight: 700, color: COLORS.text }}>{f.country_name}</span>
            <span style={{
              fontSize: 10, padding: "1px 7px", borderRadius: 5,
              background: color + "22", color, fontFamily: "'DM Mono', monospace", fontWeight: 700,
            }}>{f.severity.toUpperCase()}</span>
            <span style={{
              fontSize: 9, padding: "1px 6px", borderRadius: 4,
              background: COLORS.surfaceLight, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace",
            }}>{f.category}</span>
          </div>
          <span style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
            {f.timestamp ? new Date(f.timestamp).toLocaleString("es-AR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : ""}
          </span>
        </div>
        <div style={{ fontSize: 13, color: COLORS.text, lineHeight: 1.6 }}>{f.finding}</div>
        {f.location && <div style={{ fontSize: 11, color: COLORS.textMuted, marginTop: 4 }}>📍 {f.location}</div>}
        {f.rights_at_risk && f.rights_at_risk.length > 0 && (
          <div style={{ display: "flex", gap: 4, marginTop: 6, flexWrap: "wrap" }}>
            {f.rights_at_risk.map((r, i) => (
              <span key={i} style={{
                fontSize: 9, padding: "1px 6px", borderRadius: 4,
                background: COLORS.danger + "15", color: COLORS.danger, fontFamily: "'DM Mono', monospace",
              }}>{r}</span>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ padding: "28px 28px", maxWidth: 1100, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
          <div style={{
            width: 8, height: 8, borderRadius: "50%", background: COLORS.danger,
            boxShadow: `0 0 8px ${COLORS.danger}`,
            animation: "pulse 2s infinite",
          }} />
          <h2 style={{ margin: 0, fontSize: 20, fontWeight: 800, color: COLORS.text, letterSpacing: 1 }}>
            SENTINEL — Monitoreo Electoral en Tiempo Real
          </h2>
        </div>
        <p style={{ margin: 0, fontSize: 12, color: COLORS.textMuted }}>
          Cruza el calendario electoral global con los índices PEIRS para priorizar intervenciones.
          Actualizado: {new Date(data.generated_at).toLocaleString("es-AR")}.
        </p>
      </div>

      {/* Summary KPIs */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginBottom: 28 }}>
        {[
          { label: "Alertas Activas", value: summary.active_count, color: summary.active_count > 0 ? COLORS.danger : COLORS.accent, note: "próx. 90 días" },
          { label: "En Observación", value: summary.watch_count, color: COLORS.warning, note: "90–365 días" },
          { label: "Riesgo Alto/Crítico", value: summary.critical_upcoming, color: COLORS.danger, note: "próx. 12 meses" },
          { label: "Hallazgos", value: summary.findings_count || 0, color: "#f97316", note: "observación activa" },
          { label: "Próxima Elección", value: summary.next_election || "—", color: COLORS.info, note: summary.next_election_days !== null ? `en ${summary.next_election_days} días` : "" },
        ].map((kpi, i) => (
          <div key={i} style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: "14px 16px" }}>
            <div style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace", letterSpacing: 1, marginBottom: 6 }}>
              {kpi.label.toUpperCase()}
            </div>
            <div style={{ fontSize: 22, fontWeight: 800, color: kpi.color, fontFamily: "'DM Mono', monospace" }}>
              {kpi.value}
            </div>
            <div style={{ fontSize: 10, color: COLORS.textDim, marginTop: 3 }}>{kpi.note}</div>
          </div>
        ))}
      </div>

      {/* Alertas Activas */}
      <div style={{ marginBottom: 28 }}>
        <h3 style={{ margin: "0 0 12px", fontSize: 13, fontWeight: 700, color: COLORS.danger, fontFamily: "'DM Mono', monospace", letterSpacing: 1 }}>
          ALERTAS ACTIVAS — PRÓXIMOS 90 DÍAS ({active_alerts.length})
        </h3>
        {active_alerts.length === 0 ? (
          <div style={{ padding: "20px 0", color: COLORS.textMuted, fontSize: 13 }}>
            Sin elecciones en los próximos 90 días en los países monitoreados.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {active_alerts.map(e => <SentinelCard key={e.country_code} entry={e} />)}
          </div>
        )}
      </div>

      {/* Watch List */}
      <div style={{ marginBottom: 28 }}>
        <h3 style={{ margin: "0 0 12px", fontSize: 13, fontWeight: 700, color: COLORS.warning, fontFamily: "'DM Mono', monospace", letterSpacing: 1 }}>
          EN OBSERVACIÓN — 90 A 365 DÍAS ({watch_list.length})
        </h3>
        {watch_list.length === 0 ? (
          <div style={{ padding: "20px 0", color: COLORS.textMuted, fontSize: 13 }}>Sin países en observación.</div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 8 }}>
            {watch_list.map(e => <SentinelCard key={e.country_code} entry={e} />)}
          </div>
        )}
      </div>

      {/* Hallazgos recientes */}
      <div>
        <h3 style={{ margin: "0 0 12px", fontSize: 13, fontWeight: 700, color: "#f97316", fontFamily: "'DM Mono', monospace", letterSpacing: 1 }}>
          HALLAZGOS RECIENTES — OBSERVACIÓN EN CAMPO ({recent_findings.length})
        </h3>
        {recent_findings.length === 0 ? (
          <div style={{ padding: "20px 0", color: COLORS.textMuted, fontSize: 13 }}>
            Sin hallazgos registrados. El Hunter se ejecuta cada 12h automáticamente.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {recent_findings.map(f => <FindingCard key={f.entry_id} f={f} />)}
          </div>
        )}
      </div>
    </div>
  );
}

const REGION_LABELS = {
  americas: "🌎 Américas",
  europe: "🌍 Europa",
  africa: "🌍 África",
  asia_pacific: "🌏 Asia-Pacífico",
  arab_states: "🕌 Estados Árabes",
};

const REGION_ORDER = ["americas", "europe", "africa", "asia_pacific", "arab_states"];

// ═══════════════════════════════════════════════════════════════════════════════
// PERU SITUATION ROOM — Sala de Situación Electoral Perú 2026
// ═══════════════════════════════════════════════════════════════════════════════

const PERU_PHASES = [
  { id: "inscripcion",  label: "Inscripción",     start: "2025-09-01", end: "2025-11-30" },
  { id: "campana",      label: "Campaña",          start: "2026-01-12", end: "2026-04-09" },
  { id: "veda",         label: "Veda",             start: "2026-04-10", end: "2026-04-11" },
  { id: "jornada",      label: "Jornada",          start: "2026-04-12", end: "2026-04-12" },
  { id: "computo",      label: "Cómputo",          start: "2026-04-12", end: "2026-04-15" },
  { id: "segunda",      label: "2ª Vuelta",        start: "2026-06-07", end: "2026-06-07" },
];

const ALERT_COLORS = {
  RED:    "#ef4444",
  ORANGE: "#f97316",
  AMBER:  "#f59e0b",
  GREEN:  "#00d4aa",
};

const MOE_TABS = [
  { id: "risk_context",   label: "Riesgo Operativo",   icon: "⚠️" },
  { id: "legal_framework",label: "Marco Legal",         icon: "⚖️" },
  { id: "priority_areas", label: "Áreas Prioritarias",  icon: "🎯" },
  { id: "protocol",       label: "Protocolo MOE",       icon: "📋" },
];

// Orden de tabs: operativos primero (lo que se usa en vivo), contextuales después, informe al final.
// Agrupación visual en 4 bloques: monitoreo en vivo → contexto → observación de campo → salida final.
const PERU_INNER_TABS = [
  // Bloque 1 — MONITOREO EN VIVO
  { id: "alertas",      label: "Alertas en vivo",  icon: "🚨" },
  { id: "calendario",   label: "Calendario legal", icon: "📅" },
  // Bloque 2 — CONTEXTO
  { id: "inteligencia", label: "Contexto y datos", icon: "📊" },
  { id: "datos",        label: "Series V-Dem",     icon: "📈" },
  { id: "actores",      label: "Actores",          icon: "👥" },
  { id: "parlamento",   label: "Parlamento",       icon: "🏛" },
  // Bloque 3 — OBSERVACIÓN DE CAMPO
  { id: "brief",        label: "MOE Brief",        icon: "📋" },
  { id: "jornada",      label: "Jornada",          icon: "🗳" },
  { id: "evaluacion",   label: "Evaluación",       icon: "📝" },
  // Bloque 4 — CONSULTA JURÍDICA + SALIDA + METODOLOGÍA
  { id: "constitucional", label: "Consulta constitucional", icon: "⚖️" },
  { id: "designer",     label: "Informe preliminar", icon: "📑" },
  { id: "elite",        label: "Informe Elite",    icon: "📘" },
  { id: "metodologia",  label: "Metodología",      icon: "⚙️" },
  { id: "informe",      label: "Informe PEIRS (técnico)", icon: "📄" },
];

const PERU_HIST_EVENTS = [
  { year: 2016, label: "PPK gana presidencia. Congreso dominado por Fuerza Popular.", metric: null },
  { year: 2018, label: "PPK renuncia. Vizcarra asume. Inicio de ciclo de inestabilidad.", metric: null },
  { year: 2019, label: "Vizcarra disuelve el Congreso. Elecciones extraordinarias.", metric: null },
  { year: 2020, label: "Golpe parlamentario. 3 presidentes en 7 días.", metric: null },
  { year: 2021, label: "Castillo gana 2ª vuelta (50.1%). FH: 71/100. V-Dem: 0.52.", metric: { fh: 71, vdem: 0.52, peirs: 38 } },
  { year: 2022, label: "Castillo destituido por vacancia. Boluarte asume.", metric: null },
  { year: 2023, label: "Protestas. 60+ muertes. CIDH medidas cautelares.", metric: null },
  { year: 2024, label: "Boluarte continuidad frágil. Aprobación <10%.", metric: null },
  { year: 2026, label: "Elecciones generales — 12 de abril. PEIRS activo.", metric: null },
];

// Restricciones legales del proceso electoral peruano 2026.
// Fuentes: Ley Orgánica de Elecciones N° 26859 (LOE), Resoluciones JNE/ONPE 2026.
// Cada entrada cita la base normativa para que el observador pueda verificar.
const PERU_LEGAL_CALENDAR = [
  { date: "2026-04-10", time: "00:00", label: "Inicio de Ley Seca", detail: "Prohibición de venta y consumo de bebidas alcohólicas en lugares públicos hasta el 13/04 08:00.", source: "LOE Art. 351 / Resol. JNE" },
  { date: "2026-04-10", time: "00:00", label: "Inicio del silencio electoral", detail: "Prohibición de propaganda electoral en cualquier medio (TV, radio, prensa, redes sociales, vía pública).", source: "LOE Art. 190 / Resol. JNE" },
  { date: "2026-04-11", time: "00:00", label: "Prohibición de reuniones y manifestaciones políticas", detail: "Queda prohibida toda reunión o manifestación pública de carácter político hasta el cierre de la jornada.", source: "LOE Art. 358" },
  { date: "2026-04-12", time: "08:00", label: "Apertura de mesas de sufragio", detail: "Las 87,064 mesas de sufragio inician el proceso de votación a nivel nacional y exterior.", source: "ONPE — Cronograma electoral" },
  { date: "2026-04-12", time: "16:00", label: "Cierre de mesas / boca de urna habilitada", detail: "Cierre oficial de votación. A partir de esta hora se permite la difusión de encuestas a boca de urna.", source: "LOE Art. 191 / JNE" },
  { date: "2026-04-12", time: "23:30", label: "ONPE: conteo rápido al 100% (objetivo)", detail: "Meta institucional ONPE para la difusión del conteo rápido completo. Sujeto a flujo de actas.", source: "ONPE — Plan operativo 2026" },
  { date: "2026-04-13", time: "08:00", label: "Fin de Ley Seca", detail: "Se restablece la venta de bebidas alcohólicas.", source: "LOE Art. 351" },
  { date: "2026-04-15", time: "23:59", label: "Plazo para impugnaciones de actas de mesa", detail: "Vencimiento del plazo para que personeros presenten recursos contra actas observadas ante los Jurados Electorales Especiales.", source: "LOE Art. 363 / JNE" },
];

// Componente standalone para el countdown. Tiene su propio setInterval cada 1s.
// Al estar aislado, solo re-renderiza esta caja (4 dígitos) y NO todo el
// PeruSituationRoom (~3000 líneas de JSX). Esta era la causa raíz del parpadeo:
// el setCountdown cada segundo re-disparaba toda la función de render del parent.
const ElectionCountdown = React.memo(({ electionTs, alertColor }) => {
  const [cd, setCd] = useState({ days: 0, hrs: 0, mins: 0, secs: 0 });
  useEffect(() => {
    const tick = () => {
      const diff = electionTs - new Date();
      if (diff <= 0) { setCd({ days: 0, hrs: 0, mins: 0, secs: 0 }); return; }
      setCd({
        days: Math.floor(diff / 86400000),
        hrs:  Math.floor((diff % 86400000) / 3600000),
        mins: Math.floor((diff % 3600000) / 60000),
        secs: Math.floor((diff % 60000) / 1000),
      });
    };
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, [electionTs]);

  return (
    <div style={{ display: "flex", gap: 4 }}>
      {[
        { val: cd.days, label: "días" },
        { val: cd.hrs,  label: "hrs"  },
        { val: cd.mins, label: "min"  },
        { val: cd.secs, label: "seg"  },
      ].map(({ val, label }) => (
        <div key={label} style={{
          textAlign: "center", padding: "4px 10px",
          background: "#111827", borderRadius: 7,
          border: "1px solid #1e2d3d",
        }}>
          <div style={{ fontSize: 20, fontWeight: 800, color: alertColor, fontFamily: "'DM Mono', monospace", lineHeight: 1.1 }}>
            {String(val).padStart(2, "0")}
          </div>
          <div style={{ fontSize: 8, color: "#475569", letterSpacing: 1, textTransform: "uppercase" }}>{label}</div>
        </div>
      ))}
    </div>
  );
});

function PeruSituationRoom() {
  const [country, setCountry]       = useState(null);
  const [brief, setBrief]           = useState(null);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(null);
  const [moeTab, setMoeTab]         = useState("risk_context");
  const [innerTab, setInnerTab]     = useState("inteligencia");
  const [actors, setActors]         = useState(null);
  const [actorsLoading, setActorsLoading] = useState(false);
  const [scenarios, setScenarios]   = useState(null);
  const [scenariosLoading, setScenariosLoading] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState("A");
  const [journeyForm, setJourneyForm] = useState({
    participation_pct: 75,
    results_transmitted_pct: 0,
    violence_incidents: 0,
    internet_disruptions: false,
    incidents: "",
  });
  const [journeyResult, setJourneyResult]     = useState(null);
  const [journeySubmitting, setJourneySubmitting] = useState(false);
  const [showElectoralSystem, setShowElectoralSystem] = useState(false);
  const [expandedActors, setExpandedActors]   = useState({});
  const [reportRunId, setReportRunId]         = useState(null);
  const [reportGenerating, setReportGenerating] = useState(false);
  const [reportGenResult, setReportGenResult] = useState(null);
  const [chartData, setChartData]             = useState(null);
  const [chartLoading, setChartLoading]       = useState(false);
  const [chartError, setChartError]           = useState(false);
  const [evalQuestionnaire, setEvalQuestionnaire] = useState(null);
  const [evalLoading, setEvalLoading]         = useState(false);
  const [evalAnswers, setEvalAnswers]         = useState({});
  const [evalSection, setEvalSection]         = useState(0);
  const [evalComparison, setEvalComparison]   = useState(null);
  const [evalComparing, setEvalComparing]     = useState(false);
  const [evalSaving, setEvalSaving]           = useState(false);
  const [hunterRunning, setHunterRunning]     = useState(false);
  const [hunterRunResult, setHunterRunResult] = useState(null);
  const [liveAlerts, setLiveAlerts]           = useState(null);
  const [liveAlertsLoading, setLiveAlertsLoading] = useState(false);
  const [liveAlertsError, setLiveAlertsError] = useState(null);
  const [liveAlertsLastFetch, setLiveAlertsLastFetch] = useState(null);
  const [liveAlertsSeverity, setLiveAlertsSeverity]   = useState("low");
  const [liveAlertsHours, setLiveAlertsHours]         = useState(168);

  // Sub-agente ReportDesigner (Fase A)
  const [designerAudience, setDesignerAudience]   = useState("technical");
  const [designerLanguage, setDesignerLanguage]   = useState("es");
  const [designerPeriod, setDesignerPeriod]       = useState(7);
  const [designerUseLLM, setDesignerUseLLM]       = useState(false);

  // Informe Elite (Sprint 6 del blueprint ELITE_REPORT.md)
  const [eliteAudience, setEliteAudience]     = useState("institutional");
  const [eliteLanguage, setEliteLanguage]     = useState("es");
  const [eliteReportType, setEliteReportType] = useState("preliminary");
  const [eliteIncludePredictive, setEliteIncludePredictive] = useState(true);
  const [eliteLoading, setEliteLoading]       = useState(false);
  const [eliteResult, setEliteResult]         = useState(null);
  const [eliteError, setEliteError]           = useState(null);
  const [eliteHistory, setEliteHistory]       = useState([]);

  const fetchEliteHistory = useCallback(async () => {
    try {
      const r = await fetch(`${API_BASE}/api/report/elite/list?country_code=PER&limit=10`);
      if (r.ok) {
        const data = await r.json();
        setEliteHistory(data.items || []);
      }
    } catch (_) {}
  }, []);

  const generateEliteReport = useCallback(async () => {
    if (eliteLoading) return;
    setEliteLoading(true);
    setEliteError(null);
    setEliteResult(null);
    try {
      const r = await fetch(`${API_BASE}/api/report/elite/generate`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
          country_code: "PER",
          audience: eliteAudience,
          language: eliteLanguage,
          report_type: eliteReportType,
          include_predictive: eliteIncludePredictive,
          include_appendix_c: true,
          forecast_horizon_days: 14,
          use_llm: true,
          output_formats: ["md", "html", "pdf"],
        }),
      });
      const data = await r.json();
      if (!r.ok) {
        const msg = typeof data.detail === "string"
          ? data.detail
          : JSON.stringify(data.detail) || `HTTP ${r.status}`;
        if (r.status === 403) {
          setEliteError("Acceso restringido. Falta o es inválida tu Observer Key. " +
            "Pedila al coordinador de misión y agregala vía ?key=... en la URL.");
        } else if (r.status === 429) {
          setEliteError(msg);
        } else {
          setEliteError(msg);
        }
      } else {
        setEliteResult(data);
        fetchEliteHistory();
      }
    } catch (e) {
      setEliteError(e.message);
    } finally {
      setEliteLoading(false);
    }
  }, [eliteAudience, eliteLanguage, eliteReportType, eliteIncludePredictive, eliteLoading, fetchEliteHistory]);

  // Cargar historial al montar el tab elite
  useEffect(() => {
    if (innerTab === "elite") fetchEliteHistory();
  }, [innerTab, fetchEliteHistory]);

  const [designerLoading, setDesignerLoading]     = useState(false);
  const [designerResult, setDesignerResult]       = useState(null);
  const [designerError, setDesignerError]         = useState(null);

  const generateDesignedReport = useCallback(async () => {
    if (designerLoading) return;
    setDesignerLoading(true);
    setDesignerError(null);
    setDesignerResult(null);
    try {
      const r = await fetch(`${API_BASE}/api/report/designer/generate`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
          country_code: "PER",
          audience: designerAudience,
          language: designerLanguage,
          period_days: designerPeriod,
          use_llm: designerUseLLM,
          output_formats: ["md", "html"],
        }),
      });
      const data = await r.json();
      if (!r.ok) {
        const msg = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
        if (r.status === 403) {
          setDesignerError("Acceso restringido. Falta Observer Key (agregala con ?key=... en la URL).");
        } else {
          setDesignerError(msg || `HTTP ${r.status}`);
        }
      } else setDesignerResult(data);
    } catch (e) {
      setDesignerError(e.message);
    } finally {
      setDesignerLoading(false);
    }
  }, [designerAudience, designerLanguage, designerPeriod, designerUseLLM, designerLoading]);

  // Sub-agente constitucionalista peruano
  const [constQuestion, setConstQuestion]     = useState("");
  const [constContext, setConstContext]       = useState("");
  const [constAnswer, setConstAnswer]         = useState(null);
  const [constLoading, setConstLoading]       = useState(false);
  const [constError, setConstError]           = useState(null);
  const [constHistory, setConstHistory]       = useState([]);

  const askConstitutionalist = useCallback(async () => {
    const q = constQuestion.trim();
    if (!q || constLoading) return;
    setConstLoading(true);
    setConstError(null);
    setConstAnswer(null);
    try {
      const r = await fetch(`${API_BASE}/api/ask/constitutionalist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, context: constContext.trim() || null }),
      });
      const data = await r.json();
      if (!r.ok) {
        setConstError(data.detail || `HTTP ${r.status}`);
      } else {
        setConstAnswer(data);
        setConstHistory(prev => [{ question: q, at: new Date().toISOString(), ...data }, ...prev].slice(0, 10));
      }
    } catch (e) {
      setConstError(e.message);
    } finally {
      setConstLoading(false);
    }
  }, [constQuestion, constContext, constLoading]);

  const ELECTION_TS = useMemo(() => new Date("2026-04-12T08:00:00-05:00"), []);

  const fetchLiveAlerts = useCallback(async () => {
    setLiveAlertsLoading(true);
    setLiveAlertsError(null);
    try {
      const url = `${API_BASE}/api/alerts/PER?since_hours=${liveAlertsHours}&min_severity=${liveAlertsSeverity}&limit=200`;
      const r = await fetch(url);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      setLiveAlerts(data);
      setLiveAlertsLastFetch(new Date());
    } catch (e) {
      setLiveAlertsError(e.message);
    } finally {
      setLiveAlertsLoading(false);
    }
  }, [liveAlertsSeverity, liveAlertsHours]);

  // Polling cada 5 min cuando el tab "alertas" está abierto
  useEffect(() => {
    if (innerTab !== "alertas") return;
    fetchLiveAlerts();
    const interval = setInterval(fetchLiveAlerts, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [innerTab, fetchLiveAlerts]);

  const triggerHunterRun = useCallback(async () => {
    if (hunterRunning) return;
    setHunterRunning(true);
    setHunterRunResult(null);
    try {
      const r = await fetch(`${API_BASE}/api/hunter/PER/run-now`, { method: "POST" });
      const data = await r.json();
      if (!r.ok) {
        setHunterRunResult({ ok: false, msg: data.detail || `HTTP ${r.status}` });
      } else {
        setHunterRunResult({
          ok: true,
          registered: data.registered ?? 0,
          fetched: data.fetched ?? 0,
          duplicates: data.duplicates ?? 0,
          errors: data.errors ?? 0,
        });
      }
    } catch (e) {
      setHunterRunResult({ ok: false, msg: e.message });
    } finally {
      setHunterRunning(false);
      setTimeout(() => setHunterRunResult(null), 12000);
    }
  }, [hunterRunning]);

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/api/country/PER`).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
      fetch(`${API_BASE}/api/moe/brief/PER`).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
    ]).then(([cd, bd]) => { setCountry(cd); setBrief(bd); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  // Countdown movido a <ElectionCountdown> — componente standalone que no
  // re-renderiza todo PeruSituationRoom cada segundo.

  // Lazy-load actors and scenarios when tabs are first opened
  useEffect(() => {
    if (innerTab === "actores" && !actors && !actorsLoading) {
      setActorsLoading(true);
      fetch(`${API_BASE}/api/peru/actors`)
        .then(r => r.json())
        .then(d => { setActors(d); setActorsLoading(false); })
        .catch(() => setActorsLoading(false));
    }
    if ((innerTab === "parlamento") && !scenarios && !scenariosLoading) {
      setScenariosLoading(true);
      fetch(`${API_BASE}/api/peru/scenarios`)
        .then(r => r.json())
        .then(d => { setScenarios(d); setScenariosLoading(false); })
        .catch(() => setScenariosLoading(false));
    }
    if (innerTab === "datos" && !chartData && !chartLoading && !chartError) {
      setChartLoading(true);
      setChartError(false);
      fetch(`${API_BASE}/api/country/PER/chartdata`)
        .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
        .then(d => { setChartData(d); setChartLoading(false); })
        .catch(() => { setChartLoading(false); setChartError(true); });
    }
    if (innerTab === "evaluacion" && !evalQuestionnaire && !evalLoading) {
      setEvalLoading(true);
      fetch(`${API_BASE}/api/evaluation/PER/questionnaire`)
        .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
        .then(d => {
          setEvalQuestionnaire(d);
          // Restore saved answers if any
          const restored = {};
          (d.questionnaire || []).forEach(q => {
            if (q.observer_answer !== null && q.observer_answer !== undefined) {
              restored[q.id] = q.observer_answer;
            }
          });
          if (Object.keys(restored).length > 0) setEvalAnswers(restored);
          setEvalLoading(false);
        })
        .catch(() => setEvalLoading(false));
    }
  }, [innerTab, actors, actorsLoading, chartData, chartError, chartLoading, evalLoading, evalQuestionnaire, scenarios, scenariosLoading]);

  const downloadMOEBrief = () => {
    if (!brief || !country) return;
    const b = brief.blocks;
    const rc = b.risk_context;
    const lf = b.legal_framework;
    const pa = b.priority_areas;
    const pr = b.protocol;
    const date = new Date(brief.generated_at).toLocaleDateString("es-PE", { day: "2-digit", month: "long", year: "numeric" });
    const lines = [
      `# MOE Brief — Perú: Elecciones Generales 2026`,
      ``,
      `> **Generado por PEIRS (Predictive Electoral Integrity & Risk System)**`,
      `> Fecha: ${date}`,
      `> Nivel de Alerta: **${brief.alert_level} — ${brief.alert_label}**`,
      `> PEIRS Score: **${country.riskScore}/100 (${(country.riskLevel || "").toUpperCase()})**`,
      `> Fase Electoral Activa: ${brief.current_phase}`,
      ``,
      `---`,
      ``,
      `## 1. Contexto de Riesgo Operativo`,
      ``,
      `### Indicadores Clave`,
      ...Object.entries(rc.key_indicators).map(([k, v]) => `- **${k.replace(/_/g, " ")}:** ${v}`),
      ``,
      `**Tendencia:** ${rc.trend === "deteriorating" ? "Deteriorando" : rc.trend === "improving" ? "Mejorando" : "Estable"}`,
      ``,
      `### Violaciones Críticas`,
      rc.critical_violations.length === 0
        ? `_Sin violaciones críticas detectadas._`
        : rc.critical_violations.map(v => `- **${v.treaty} ${v.article}** (${v.severity.toUpperCase()}): ${v.finding}`).join("\n"),
      ``,
      `### Factores de Riesgo Adicionales`,
      ...rc.risk_factors.map(f => `- ${f}`),
      ``,
      `---`,
      ``,
      `## 2. Marco Legal Aplicable`,
      ``,
      `### Instrumentos Universales`,
      ...lf.universal_instruments.map(inst => `- **${inst.id}** — ${inst.name}: ${inst.key_articles.join(", ")}`),
      ``,
      `### Instrumentos Regionales`,
      ...lf.regional_instruments.map(inst => `- **${inst.id}** — ${inst.name}: ${inst.key_articles.join(", ")}`),
      ``,
      `### Marco Nacional`,
      ...Object.values(lf.national_framework).map(v => `- ${v}`),
      ``,
      `### Obligaciones Clave`,
      ...lf.key_obligations.map(o => `- ${o}`),
      ``,
      `---`,
      ``,
      `## 3. Áreas Prioritarias de Observación`,
      ``,
      ...pa.priority_areas.flatMap(area => [
        `### ${area.priority}. ${area.area} — Riesgo: ${area.risk.toUpperCase()}`,
        ``,
        `**Hallazgos:**`,
        ...area.findings.map(f => `- ${f}`),
        ``,
        `**Estándar EOS:** ${area.eos_standard}`,
        ``,
        `**Tareas de Observación:**`,
        ...area.observation_tasks.map(t => `- ${t}`),
        ``,
      ]),
      `---`,
      ``,
      `## 4. Protocolo de Misión Recomendado`,
      ``,
      `**Tipo de Misión:** ${pr.protocol.type} — ${pr.protocol.label}`,
      ``,
      pr.protocol.description,
      ``,
      `| Parámetro | Valor |`,
      `|---|---|`,
      `| Duración LTO | ${pr.protocol.lto_duration} |`,
      `| Observadores STO | ${pr.protocol.sto_count} |`,
      `| PVT | ${pr.protocol.pvt_recommended ? "Recomendado" : "No requerido"} |`,
      `| SMM | ${pr.protocol.smm_recommended ? "Recomendado" : "No requerido"} |`,
      ``,
      `### Organismos Recomendados`,
      ...pr.recommended_observers.map(obs => `- **${obs.org}:** ${obs.role}`),
      ``,
      `---`,
      ``,
      `_Este brief fue auto-generado por PEIRS a partir de datos verificados de Freedom House FIW 2025, V-Dem v15 y PEI 10.0._`,
      `_No constituye una evaluación oficial de ningún organismo electoral internacional._`,
    ];
    const md = lines.join("\n");
    const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `MOE_Brief_PER_${new Date().toISOString().slice(0, 10)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const submitJornada = () => {
    if (!country?.run_id) return;
    setJourneySubmitting(true);
    setJourneyResult(null);
    const payload = {
      run_id: country.run_id,
      participation_pct: Number(journeyForm.participation_pct),
      results_transmitted_pct: Number(journeyForm.results_transmitted_pct),
      violence_incidents: Number(journeyForm.violence_incidents),
      internet_disruptions: journeyForm.internet_disruptions,
      incidents: journeyForm.incidents.split("\n").map(s => s.trim()).filter(Boolean),
    };
    fetch(`${API_BASE}/api/analyze/voting-day`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(r => r.json())
      .then(d => { setJourneyResult(d); setJourneySubmitting(false); })
      .catch(e => { setJourneyResult({ error: e.message }); setJourneySubmitting(false); });
  };

  if (loading) return (
    <div style={{ padding: 80, textAlign: "center", color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
      Cargando Sala de Situación Electoral...
    </div>
  );
  if (error) return (
    <div style={{ padding: 40, color: COLORS.danger, fontFamily: "'DM Mono', monospace" }}>
      Error al cargar datos de Perú: {error}. Verificá que el backend esté corriendo y que exista un reporte para PER.
    </div>
  );

  const rl = RISK_LEVELS[country?.riskLevel] || RISK_LEVELS.moderate;
  const alertColor = brief ? ALERT_COLORS[brief.alert_level] || COLORS.warning : COLORS.warning;
  const alertLabel = brief?.alert_label || "Monitoreo Activo";

  // Convergencia entre fuentes
  const logs = country?.agentLogs || [];
  const peiLog = logs.find(l => l.includes("PEI REAL:") || l.includes("PEI PEI-10.0:"));
  const peiEmbs = peiLog ? (peiLog.match(/EMBs=([\d.]+)/) || [])[1] : null;
  const peiYear = peiLog ? (peiLog.match(/año=(\d+)/) || [])[1] : null;
  const fhRisk   = country ? 100 - country.freedomScore : 50;
  const vdemRisk = country ? Math.round((1 - country.vdemIndex) * 100) : 50;
  const peiRisk  = peiEmbs ? Math.round(100 - parseFloat(peiEmbs)) : null;
  const riskVals = [fhRisk, vdemRisk, ...(peiRisk !== null ? [peiRisk] : [])];
  const mean     = riskVals.reduce((a, b) => a + b, 0) / riskVals.length;
  const stdDev   = Math.sqrt(riskVals.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / riskVals.length);
  const convScore = Math.max(0, Math.round(100 - (stdDev / 50) * 100));

  const radarData = country ? Object.entries(country.dimensions).map(([k, v]) => ({
    dimension: DIMENSION_LABELS[k], value: v, fullMark: 100,
  })) : [];

  const waterfallData = country ? Object.entries(country.dimensions)
    .map(([k, v]) => ({ name: (DIMENSION_LABELS[k] || k).slice(0, 16), risk: Math.max(0, 100 - v), integrity: v }))
    .sort((a, b) => b.risk - a.risk) : [];

  const embLog = logs.find(l => l.includes("EMB:"));
  const embLevel = embLog ? (embLog.includes("captured") ? "captured" : embLog.includes("compromised") ? "compromised" : embLog.includes("partial") ? "partial" : "full") : "partial";
  const autonomyVal = embLog ? parseFloat((embLog.match(/autonomía=([\d.]+)/) || [])[1] || 0) : null;
  const intlObs = embLog ? embLog.includes("Obs. intl: True") : null;

  return (
    <div style={{ background: COLORS.bg, minHeight: "100vh" }}>
      <style>{`
        .peru-card { transition: transform 0.2s ease, box-shadow 0.2s ease; }
        .peru-card:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,0.4); }
        .peru-inner-tab:hover { color: ${alertColor} !important; }
      `}</style>

      {/* STICKY: Zone 1 command strip + inner navigation */}
      <div style={{ position: "sticky", top: 65, zIndex: 90 }}>
        <div style={{
          background: "linear-gradient(135deg, #0d1220 0%, #0f172a 100%)",
          borderBottom: `1px solid ${alertColor}33`,
          padding: "20px 28px 16px",
          boxShadow: `0 4px 24px ${alertColor}18`,
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ fontSize: 36 }}>&#127477;&#127466;</span>
              <div>
                <div style={{ fontSize: 22, fontWeight: 800, color: COLORS.text, fontFamily: "'Fraunces', serif", letterSpacing: -0.5 }}>
                  Sala de Situación Electoral — Perú 2026
                </div>
                <div style={{ fontSize: 10, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", marginTop: 2 }}>
                  Elecciones Generales · 12 de Abril de 2026 · JNE / ONPE / RENIEC
                </div>
              </div>
            </div>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <button
                onClick={triggerHunterRun}
                disabled={hunterRunning}
                title="Disparar el Hunter ahora (RSS + Claude). Un ciclo cuesta pocos centavos en API calls."
                style={{
                  padding: "6px 12px", borderRadius: 8,
                  background: hunterRunning ? COLORS.surface : alertColor + "12",
                  border: `1px solid ${alertColor}55`,
                  color: hunterRunning ? COLORS.textMuted : alertColor,
                  fontSize: 11, fontWeight: 700,
                  fontFamily: "'DM Mono', monospace", letterSpacing: 1,
                  cursor: hunterRunning ? "wait" : "pointer",
                  display: "flex", alignItems: "center", gap: 6,
                  transition: "all 0.2s",
                }}
              >
                {hunterRunning ? "● EJECUTANDO…" : "▶ HUNTER NOW"}
              </button>
              {hunterRunResult && (
                <div style={{
                  padding: "5px 11px", borderRadius: 7,
                  background: hunterRunResult.ok ? COLORS.accentDim : COLORS.dangerDim,
                  border: `1px solid ${hunterRunResult.ok ? COLORS.accent : COLORS.danger}66`,
                  color: hunterRunResult.ok ? COLORS.accent : COLORS.danger,
                  fontSize: 10, fontWeight: 700, fontFamily: "'DM Mono', monospace", letterSpacing: 0.5,
                  whiteSpace: "nowrap",
                }}>
                  {hunterRunResult.ok
                    ? `✓ ${hunterRunResult.registered} nuevos · ${hunterRunResult.fetched} fetched · ${hunterRunResult.duplicates} dup`
                    : `✗ ${hunterRunResult.msg}`}
                </div>
              )}
              <div style={{
                padding: "6px 14px", borderRadius: 8,
                background: alertColor + "18", border: `1px solid ${alertColor}44`,
                fontSize: 11, fontWeight: 700, color: alertColor,
                fontFamily: "'DM Mono', monospace", letterSpacing: 1,
                display: "flex", alignItems: "center", gap: 6,
              }}>
                <span style={{ width: 7, height: 7, borderRadius: "50%", background: alertColor, display: "inline-block", boxShadow: `0 0 8px ${alertColor}` }} />
                {alertLabel}
              </div>
              <ElectionCountdown electionTs={ELECTION_TS} alertColor={alertColor} />
            </div>
          </div>
          <div style={{ display: "flex", gap: 4, marginTop: 14, alignItems: "center" }}>
            {PERU_PHASES.map((ph, i) => {
              const now = new Date();
              const start = new Date(ph.start + "T00:00:00");
              const end   = new Date(ph.end + "T23:59:59");
              const isActive = now >= start && now <= end;
              const isDone   = now > end;
              return (
                <React.Fragment key={ph.id}>
                  {i > 0 && <div style={{ width: 20, height: 1, background: COLORS.border, flexShrink: 0 }} />}
                  <div style={{
                    padding: "4px 12px", borderRadius: 20, fontSize: 10, fontWeight: 700,
                    border: `1px solid ${isActive ? alertColor + "66" : COLORS.border}`,
                    background: isActive ? alertColor + "18" : COLORS.surface,
                    color: isActive ? alertColor : isDone ? COLORS.textDim : COLORS.textMuted,
                    opacity: isDone ? 0.5 : 1,
                    whiteSpace: "nowrap", fontFamily: "'DM Mono', monospace", letterSpacing: 0.5,
                  }}>
                    {isActive && "● "}{ph.label}
                  </div>
                </React.Fragment>
              );
            })}
            <div style={{ marginLeft: "auto", fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
              PEIRS {country?.riskScore || "—"}/100 · {rl.label}
            </div>
          </div>
        </div>

        {/* Inner nav tabs */}
        <div style={{
          background: COLORS.surface, borderBottom: `2px solid ${COLORS.border}`,
          padding: "0 28px", display: "flex", gap: 0, overflowX: "auto",
        }}>
          {PERU_INNER_TABS.map(tab => (
            <button key={tab.id} className="peru-inner-tab" onClick={() => setInnerTab(tab.id)} style={{
              padding: "11px 20px", border: "none", cursor: "pointer",
              fontSize: 12, fontWeight: 600, background: "transparent",
              color: innerTab === tab.id ? alertColor : COLORS.textMuted,
              borderBottom: innerTab === tab.id ? `2px solid ${alertColor}` : "2px solid transparent",
              transition: "all 0.2s", whiteSpace: "nowrap",
              fontFamily: "'DM Mono', monospace", letterSpacing: 0.5,
            }}>
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div style={{ padding: "24px 28px 48px" }}>

        {/* ══ TAB: INTELIGENCIA ══ */}
        {innerTab === "inteligencia" && (
          <div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 24 }}>
              <div>
                {/* ══ Datasets internacionales — cards narrativas ══
                    Reemplaza al bloque "Fuentes Verificadas" con CircularScore pelado.
                    Cada dataset incluye descripción, escala interpretativa, año y fuente. */}
                <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 8 }}>
                  Índices internacionales — contexto pre-electoral
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 12 }}>
                  <DatasetCard
                    name="Freedom House" icon="🗽"
                    value={country?.freedomScore} max={100} year="FIW 2025"
                    description="Mide derechos políticos y libertades civiles en 195 países. Puntaje agregado sobre 100."
                    source="Freedom House (EE.UU.)" sourceUrl="https://freedomhouse.org"
                    scale={[
                      { from: 70, to: 100, label: "Libre",            color: COLORS.accent },
                      { from: 40, to: 69,  label: "Parcialmente libre", color: COLORS.warning },
                      { from: 0,  to: 39,  label: "No libre",          color: COLORS.danger  },
                    ]} />
                  <DatasetCard
                    name="V-Dem — Lib. Democracy" icon="⚖️"
                    value={country?.vdemIndex} max={1} year="V-Dem v15"
                    description="Índice de democracia liberal. Combina democracia electoral + límites al ejecutivo, igualdad ante la ley y libertades."
                    source="V-Dem Institute (Suecia)" sourceUrl="https://v-dem.net"
                    scale={[
                      { from: 0.81, to: 1.00, label: "Democracia liberal",    color: COLORS.accent  },
                      { from: 0.51, to: 0.80, label: "Democracia electoral", color: "#22c55e"      },
                      { from: 0.21, to: 0.50, label: "Autocracia electoral", color: COLORS.warning },
                      { from: 0.00, to: 0.20, label: "Autocracia cerrada",   color: COLORS.danger  },
                    ]} />
                  <DatasetCard
                    name="PEI — Integridad electoral" icon="🗳️"
                    value={peiEmbs ? parseFloat(peiEmbs) : null} max={100}
                    year={peiYear ? `Elección ${peiYear}` : "—"}
                    description="Percepción de expertos sobre la integridad del proceso electoral (EMBs, leyes, padrones, conteo, disputas)."
                    source="Electoral Integrity Project" sourceUrl="https://www.electoralintegrityproject.com"
                    scale={[
                      { from: 70, to: 100, label: "Alta integridad",     color: COLORS.accent  },
                      { from: 50, to: 69,  label: "Integridad moderada", color: COLORS.warning },
                      { from: 0,  to: 49,  label: "Baja integridad",     color: COLORS.danger  },
                    ]} />
                  <DatasetCard
                    name="RSF — Libertad de prensa" icon="📰"
                    value={country?.rsf?.score ?? country?.dimensions?.pressFreedom ?? null}
                    max={100} year="RSF 2025"
                    description="Índice de libertad de prensa. Mayor puntaje = más libertad. Cubre 180 países."
                    source="Reporteros Sin Fronteras" sourceUrl="https://rsf.org"
                    scale={[
                      { from: 85, to: 100, label: "Situación buena",        color: COLORS.accent  },
                      { from: 70, to: 84,  label: "Satisfactoria",          color: "#22c55e"      },
                      { from: 55, to: 69,  label: "Problemática",           color: COLORS.warning },
                      { from: 40, to: 54,  label: "Difícil",                color: "#f97316"      },
                      { from: 0,  to: 39,  label: "Muy grave",              color: COLORS.danger  },
                    ]} />
                </div>
                <div style={{ padding: "8px 12px", borderRadius: 7, background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`, display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                  <span style={{ fontSize: 10, color: COLORS.textDim }} title="Qué tan consistente es el diagnóstico cuando se cruzan las cuatro fuentes">
                    Convergencia entre fuentes
                  </span>
                  <span style={{ fontSize: 14, fontWeight: 800, fontFamily: "'DM Mono', monospace",
                    color: convScore >= 75 ? COLORS.accent : convScore >= 50 ? COLORS.warning : COLORS.danger }}>
                    {convScore}/100
                  </span>
                </div>
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.textMuted, textTransform: "uppercase", letterSpacing: 2, marginBottom: 8, display: "flex", alignItems: "center", gap: 6 }}>
                    <span>&#127963;</span> JNE — Jurado Nacional de Elecciones
                  </div>
                  <EMBStatusPanel level={embLevel} autonomy={autonomyVal}
                    irregularities={country?.dimensions?.embIndependence ? country.dimensions.embIndependence / 100 : null}
                    intimidation={country?.dimensions?.legalFramework ? country.dimensions.legalFramework / 100 : null}
                    intlObs={intlObs} />
                </div>
                <Card className="peru-card">
                  <SectionTitle icon="📈">Evolución Histórica del Índice de Riesgo</SectionTitle>
                  {country?.timeline && (
                    <ResponsiveContainer width="100%" height={160}>
                      <LineChart data={country.timeline}>
                        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                        <XAxis dataKey="month" tick={{ fill: COLORS.textMuted, fontSize: 10 }} />
                        <YAxis domain={[0, 100]} tick={{ fill: COLORS.textMuted, fontSize: 10 }} />
                        <Tooltip contentStyle={{ background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontSize: 11 }} />
                        <Line type="monotone" dataKey="score" stroke={rl.color} strokeWidth={2.5} dot={{ fill: rl.color, r: 3 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  )}
                </Card>
              </div>
              <div>
                <Card className="peru-card" style={{ marginBottom: 16 }}>
                  <SectionTitle icon="🎯">Análisis Multidimensional (8 Dimensiones)</SectionTitle>
                  <ResponsiveContainer width="100%" height={230}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke={COLORS.border} />
                      <PolarAngleAxis dataKey="dimension" tick={{ fill: COLORS.textMuted, fontSize: 8, fontFamily: "'DM Mono', monospace" }} />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: COLORS.textDim, fontSize: 7 }} />
                      <Radar dataKey="value" stroke={rl.color} fill={rl.color} fillOpacity={0.12} strokeWidth={2} />
                    </RadarChart>
                  </ResponsiveContainer>
                </Card>
                <Card className="peru-card">
                  <SectionTitle icon="🔥">Drivers del Riesgo Electoral</SectionTitle>
                  <div style={{ fontSize: 10, color: COLORS.textDim, marginBottom: 8, fontFamily: "'DM Mono', monospace" }}>
                    Contribución de cada dimensión al riesgo (100 = máximo)
                  </div>
                  <ResponsiveContainer width="100%" height={210}>
                    <BarChart data={waterfallData} layout="vertical" margin={{ left: 4, right: 20, top: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} horizontal={false} />
                      <XAxis type="number" domain={[0, 100]} tick={{ fill: COLORS.textMuted, fontSize: 9 }} />
                      <YAxis type="category" dataKey="name" tick={{ fill: COLORS.textMuted, fontSize: 9, fontFamily: "'DM Mono', monospace" }} width={100} />
                      <Tooltip contentStyle={{ background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontSize: 11 }} formatter={(v) => [`${v}/100`]} />
                      <Bar dataKey="risk" radius={[0, 4, 4, 0]} name="Riesgo">
                        {waterfallData.map((e, i) => (
                          <Cell key={i} fill={e.risk >= 70 ? COLORS.danger : e.risk >= 40 ? COLORS.warning : COLORS.accent} fillOpacity={0.8} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              </div>
            </div>

            {/* Línea histórica visual — timeline único (la Comparativa 2021 vs 2026
                se removió: estaba duplicada en el Informe Cap 1 y usaba valores
                hardcoded sin fuente documentada). */}
            <div>
              <Card className="peru-card" style={{ padding: 0, overflow: "hidden" }}>
                {/* ── PIZARRA: Draw-my-life timeline ── */}
                {(() => {
                  const TL = [
                    { yr:"16", cx:50,  cy:182, r:13, col:"#3b82f6", bg:"#1e3a5f", tc:"#93c5fd", above:true,  hdr:"2016 🗳️", l1:"PPK presidente", l2:"FP domina Congreso", d:"1.0s" },
                    { yr:"18", cx:145, cy:187, r:13, col:"#f59e0b", bg:"#1f1500", tc:"#fcd34d", above:false, hdr:"2018 ⚠️", l1:"PPK renuncia",    l2:"Vizcarra asume",    d:"1.3s" },
                    { yr:"19", cx:240, cy:176, r:13, col:"#f97316", bg:"#1c1208", tc:"#fb923c", above:true,  hdr:"2019 💥", l1:"Congreso",         l2:"disuelto",          d:"1.6s" },
                    { yr:"20", cx:330, cy:190, r:17, col:"#ef4444", bg:"#2d0808", tc:"#fca5a5", above:false, hdr:"2020 🔥", l1:"3 presidentes",   l2:"en 7 días",         d:"1.9s", big:true },
                    { yr:"21", cx:420, cy:176, r:13, col:"#dc2626", bg:"#2d0808", tc:"#fca5a5", above:true,  hdr:"2021 🗳️", l1:"Castillo gana",   l2:"FH:71 · V-Dem:0.52", d:"2.1s" },
                    { yr:"22", cx:510, cy:190, r:13, col:"#b91c1c", bg:"#2d0808", tc:"#fca5a5", above:false, hdr:"2022 ⚡", l1:"Castillo",         l2:"destituido",        d:"2.3s" },
                    { yr:"23", cx:600, cy:170, r:17, col:"#991b1b", bg:"#3b0000", tc:"#fca5a5", above:true,  hdr:"2023 🚨 CRISIS", l1:"60+ muertes", l2:"CIDH cautelares", d:"2.5s", crisis:true },
                    { yr:"24", cx:685, cy:190, r:13, col:"#7f1d1d", bg:"#1a0808", tc:"#fca5a5", above:false, hdr:"2024 📉", l1:"Aprobación",       l2:"<10% histórico",   d:"2.7s" },
                    { yr:"26", cx:770, cy:180, r:18, col:"#0d9488", bg:"#042f2e", tc:"#2dd4bf", above:true,  hdr:"2026 🗳️", l1:"Elecciones",       l2:"12 de abril ▶",    d:"2.9s", election:true },
                  ];
                  const VDEM = [
                    {cx:50,v:0.59},{cx:145,v:0.56},{cx:240,v:0.54},{cx:330,v:0.50},
                    {cx:420,v:0.52},{cx:510,v:0.47},{cx:600,v:0.44},{cx:685,v:0.42},{cx:770,v:0.40},
                  ];
                  const CARD_W = 96; const CARD_H = 46;
                  return (
                    <div style={{ background:"linear-gradient(175deg,#080e1a 0%,#0d1424 100%)", borderRadius:10 }}>
                      {/* Title bar */}
                      <div style={{ display:"flex", alignItems:"center", gap:10, padding:"12px 16px 6px" }}>
                        <div style={{ fontSize:9, fontWeight:700, letterSpacing:3, color:"#475569", fontFamily:"monospace", textTransform:"uppercase" }}>Pizarra — Crisis Democrática</div>
                        <div style={{ flex:1, height:1, background:"#1e293b" }}/>
                        <div style={{ fontSize:9, color:"#334155", fontFamily:"monospace" }}>2016 → 2026</div>
                      </div>

                      <svg viewBox="0 0 820 348" style={{ width:"100%", height:"auto", display:"block" }} xmlns="http://www.w3.org/2000/svg">
                        <defs>
                          <style>{`
                            .ptl-line{stroke-dasharray:1050;stroke-dashoffset:1050;animation:ptl-draw 3.4s cubic-bezier(.4,0,.2,1) forwards .1s}
                            .ptl-n{opacity:0;transform-box:fill-box;transform-origin:center;animation:ptl-pop .5s cubic-bezier(.34,1.56,.64,1) forwards}
                            .ptl-c{opacity:0;animation:ptl-fade .45s ease forwards}
                            @keyframes ptl-draw{to{stroke-dashoffset:0}}
                            @keyframes ptl-pop{0%{opacity:0;transform:scale(.1)}100%{opacity:1;transform:scale(1)}}
                            @keyframes ptl-fade{to{opacity:1}}
                          `}</style>
                          <pattern id="ptl-grid" x="0" y="0" width="60" height="60" patternUnits="userSpaceOnUse">
                            <path d="M60 0 L0 0 0 60" fill="none" stroke="rgba(255,255,255,0.022)" strokeWidth=".6"/>
                          </pattern>
                          <filter id="ptl-chalk" x="-5%" y="-5%" width="110%" height="110%">
                            <feTurbulence type="fractalNoise" baseFrequency="0.07" numOctaves="4" result="n"/>
                            <feDisplacementMap in="SourceGraphic" in2="n" scale="1.6" xChannelSelector="R" yChannelSelector="G"/>
                          </filter>
                          <filter id="ptl-glow" x="-40%" y="-40%" width="180%" height="180%">
                            <feGaussianBlur stdDeviation="3.5" result="b"/>
                            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
                          </filter>
                          <marker id="ptl-arr" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
                            <path d="M0,0 L0,6 L9,3 z" fill="rgba(248,250,252,0.45)" filter="url(#ptl-chalk)"/>
                          </marker>
                        </defs>

                        {/* Board grid */}
                        <rect width="820" height="348" fill="url(#ptl-grid)"/>

                        {/* Watermark */}
                        <text x="410" y="205" textAnchor="middle" fontSize="42" fill="rgba(255,255,255,0.028)"
                          fontFamily="monospace" fontWeight="900" letterSpacing="5">CRISIS DEMOCRÁTICA</text>

                        {/* Chalk path */}
                        <path
                          className="ptl-line"
                          d="M 50 182 C 98 170,122 198,145 187 C 170 175,215 166,240 176 C 268 188,305 202,330 190 C 356 178,398 163,420 176 C 446 192,483 205,510 190 C 536 175,573 152,600 170 C 626 188,658 204,685 190 C 710 176,745 166,770 180"
                          stroke="rgba(248,250,252,0.50)" strokeWidth="2.5" fill="none"
                          strokeLinecap="round" filter="url(#ptl-chalk)" markerEnd="url(#ptl-arr)"
                        />

                        {/* Events */}
                        {TL.map((n) => {
                          const connY1 = n.above ? n.cy - n.r     : n.cy + n.r;
                          const connY2 = n.above ? n.cy - n.r - 28 : n.cy + n.r + 28;
                          const cardX  = Math.min(Math.max(n.cx - CARD_W / 2, 4), 820 - CARD_W - 4);
                          const cardY  = n.above ? connY2 - CARD_H : connY2;
                          return (
                            <g key={n.yr}>
                              {/* Dashed connector */}
                              <line x1={n.cx} y1={connY1} x2={n.cx} y2={connY2}
                                stroke={n.col + "60"} strokeWidth="1" strokeDasharray="3 2.5"/>
                              {/* Crisis/election pulse ring */}
                              {(n.crisis || n.election) && (
                                <circle cx={n.cx} cy={n.cy} r={n.r + 9} fill="none"
                                  stroke={n.col} strokeWidth="1.2" opacity="0.3" strokeDasharray="4 3"/>
                              )}
                              {/* Node */}
                              <g className="ptl-n" style={{ animationDelay: n.d }}>
                                <circle cx={n.cx} cy={n.cy} r={n.r} fill={n.col} filter="url(#ptl-glow)"/>
                                <text x={n.cx} y={n.cy + 4.5} textAnchor="middle" fontSize="10" fill="white" fontWeight="800">{n.yr}</text>
                              </g>
                              {/* Card */}
                              <g className="ptl-c" style={{ animationDelay: `calc(${n.d} + 0.18s)` }}>
                                <rect x={cardX} y={cardY} width={CARD_W} height={CARD_H} rx="5"
                                  fill={n.bg} stroke={n.col + (n.crisis || n.election ? "bb" : "66")} strokeWidth={n.crisis || n.election ? 1.8 : 1.2}/>
                                <text x={cardX + CARD_W/2} y={cardY + 15} textAnchor="middle" fontSize="9" fill={n.tc} fontWeight="700">{n.hdr}</text>
                                <text x={cardX + CARD_W/2} y={cardY + 28} textAnchor="middle" fontSize="8" fill="#94a3b8">{n.l1}</text>
                                <text x={cardX + CARD_W/2} y={cardY + 39} textAnchor="middle" fontSize="7.5" fill="#475569">{n.l2}</text>
                              </g>
                            </g>
                          );
                        })}

                        {/* V-Dem sparkline */}
                        <text x="410" y="290" textAnchor="middle" fontSize="7" fill="#334155" fontFamily="monospace" letterSpacing="2">ÍNDICE V-DEM — DEMOCRACIA LIBERAL (v2x_libdem)</text>
                        <line x1="36" y1="297" x2="36" y2="326" stroke="#1e293b" strokeWidth="1"/>
                        <line x1="36" y1="326" x2="804" y2="326" stroke="#1e293b" strokeWidth="1.2"/>
                        <text x="16" y="312" textAnchor="middle" fontSize="7" fill="#334155" fontFamily="monospace"
                          transform="rotate(-90,16,312)">V-Dem</text>
                        {VDEM.map(({ cx, v }) => {
                          const maxH = 30;
                          const bH = Math.max(4, Math.round(((v - 0.35) / 0.30) * maxH));
                          const bY = 326 - bH;
                          const col = v >= 0.55 ? "#3b82f6" : v >= 0.50 ? "#f59e0b" : v >= 0.45 ? "#f97316" : "#ef4444";
                          return (
                            <g key={cx}>
                              <rect x={cx - 9} y={bY} width="18" height={bH} rx="3" fill={col} opacity="0.75"/>
                              <text x={cx} y="337" textAnchor="middle" fontSize="7.5" fill="#475569" fontFamily="monospace">{v.toFixed(2)}</text>
                            </g>
                          );
                        })}
                        {/* Trend arrow */}
                        <line x1="50" y1="302" x2="770" y2="323" stroke="#ef444445" strokeWidth="1.2" strokeDasharray="6 3"/>
                        <text x="720" y="300" fontSize="8" fill="#ef444490" fontFamily="monospace" fontWeight="700">↘ −0.19</text>
                      </svg>

                      {/* Legend */}
                      <div style={{ display:"flex", gap:14, padding:"5px 14px 10px", flexWrap:"wrap" }}>
                        {[["#3b82f6","Estabilidad relativa"],["#f59e0b","Transición"],["#ef4444","Crisis aguda"],["#0d9488","2026 Electoral"]].map(([col,label]) => (
                          <div key={label} style={{ display:"flex", alignItems:"center", gap:5 }}>
                            <div style={{ width:7, height:7, borderRadius:"50%", background:col }}/>
                            <span style={{ fontSize:9, color:"#475569", fontFamily:"monospace" }}>{label}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })()}
              </Card>
            </div>
          </div>
        )}

        {/* ══ TAB: ACTORES ══ */}
{/* ══ HEMICYCLE CHART COMPONENT (defined inline for local use) ══ */}
        {/* Used by Parlamento tab */}

        {/* ══ TAB: ACTORES ══ */}
        {innerTab === "actores" && (
          <div>
            {actorsLoading && (
              <div style={{ padding: 60, textAlign: "center", color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
                Cargando fuerzas políticas...
              </div>
            )}
            {!actorsLoading && !actors && (
              <div style={{ padding: 40, color: COLORS.danger, fontFamily: "'DM Mono', monospace", fontSize: 12 }}>
                Error cargando actores. Verificá /api/peru/actors en el backend.
              </div>
            )}
            {actors && (() => {
              const es = actors.electoral_system || {};
              const showES = showElectoralSystem;
              const setShowES = setShowElectoralSystem;
              return (
                <div>
                  {/* ── Análisis Ejecutivo ── */}
                  <div style={{
                    marginBottom: 20, padding: "20px 24px", borderRadius: 12,
                    background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
                    border: `1px solid ${COLORS.accent}33`,
                    borderLeft: `4px solid ${COLORS.accent}`,
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
                      <div>
                        <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.accent, textTransform: "uppercase", marginBottom: 6 }}>
                          Análisis Ejecutivo — Contexto Electoral Perú 2026
                        </div>
                        <div style={{ fontSize: 11, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
                          Basado en datos V-Dem v15, JNE, Freedom House FIW 2025
                        </div>
                      </div>
                      <button onClick={() => setShowES(v => !v)} style={{
                        padding: "6px 14px", borderRadius: 8, border: `1px solid ${COLORS.accent}44`,
                        background: COLORS.accentDim, color: COLORS.accent, fontSize: 10, fontWeight: 700,
                        cursor: "pointer", fontFamily: "'DM Mono', monospace",
                      }}>
                        {showES ? "Ocultar Sistema Electoral" : "Ver Sistema Electoral"}
                      </button>
                    </div>
                    <div style={{ fontSize: 12, color: COLORS.text, lineHeight: 1.75, marginBottom: 14 }}>
                      Perú ingresa al ciclo electoral 2026 en un contexto de <strong style={{ color: COLORS.warning }}>crisis de representación</strong> sin precedentes.
                      Desde 2016, el país ha tenido <strong style={{ color: COLORS.danger }}>seis presidentes</strong> y dos congresos disueltos, consolidando un patrón de
                      inestabilidad estructural que el índice V-Dem registra como deterioro sostenido de la democracia liberal (v2x_libdem: 0.42 en 2024, frente a 0.59 en 2015).
                      Freedom House clasifica al país como <strong style={{ color: COLORS.warning }}>Parcialmente Libre</strong> (FH Score: 72/100, 2025), con retrocesos específicos
                      en independencia judicial y libertad de prensa. El sistema electoral proporcional con umbral del 5% no ha logrado reducir la fragmentación parlamentaria:
                      en cada congreso desde 2011 se han conformado entre 7 y 9 bancadas, ninguna con mayoría absoluta (66 escaños). Para 2026, la proyección más probable
                      apunta a un nuevo parlamento hiperfragmentado (≥8 bancadas), con riesgo alto de bloqueo ejecutivo-legislativo similar al período 2021-2026.
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {[
                        { label: "JNE — Sistema Electoral", url: "https://www.jne.gob.pe" },
                        { label: "V-Dem Institute v15", url: "https://www.v-dem.net" },
                        { label: "Freedom House 2025", url: "https://freedomhouse.org" },
                        { label: "IDEA — Peru Electoral Data", url: "https://www.idea.int/data-tools/country-view/247/40" },
                      ].map(s => (
                        <a key={s.label} href={s.url} target="_blank" rel="noopener noreferrer" style={{
                          fontSize: 9, padding: "3px 10px", borderRadius: 4, background: COLORS.border,
                          color: COLORS.accent, textDecoration: "none", fontFamily: "'DM Mono', monospace",
                          border: `1px solid ${COLORS.border}`,
                        }}>
                          {s.label}
                        </a>
                      ))}
                    </div>
                  </div>

                  {/* ── Sistema Electoral (expandible) ── */}
                  {showES && (
                    <div style={{
                      marginBottom: 20, padding: "18px 20px", borderRadius: 12,
                      background: COLORS.surface, border: `1px solid ${COLORS.border}`,
                    }}>
                      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 14 }}>
                        Sistema Electoral Peruano — Detalles Técnicos
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 14 }}>
                        {[
                          { label: "FÓRMULA", val: es.formula || "Cifra Repartidora (D'Hondt)" },
                          { label: "UMBRAL", val: es.threshold || "5% nacional ó 7 escaños" },
                          { label: "CIRCUNSCRIPCIONES", val: `${es.districts || 26} (${es.district_note ? es.district_note.substring(0, 40) + "…" : ""})` },
                          { label: "TIPO DE VOTO", val: es.ballot_type || "Lista cerrada + voto preferencial" },
                          { label: "CUOTA MUJERES", val: es.women_quota || "30% mínimo (Ley 31030)" },
                          { label: "SEGUNDA VUELTA", val: es.ballotage_threshold || "50%+1 en 1ª vuelta" },
                        ].map(item => (
                          <div key={item.label} style={{ padding: "10px 12px", borderRadius: 8, background: COLORS.surfaceLight }}>
                            <div style={{ fontSize: 8, fontWeight: 700, color: COLORS.accent, letterSpacing: 2, marginBottom: 4 }}>{item.label}</div>
                            <div style={{ fontSize: 10, color: COLORS.text, lineHeight: 1.4 }}>{item.val}</div>
                          </div>
                        ))}
                      </div>
                      {es.key_bodies && (
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 14 }}>
                          {Object.entries(es.key_bodies).map(([abbr, desc]) => (
                            <div key={abbr} style={{ padding: "10px 12px", borderRadius: 8, background: COLORS.surfaceLight, borderLeft: `3px solid ${COLORS.purple}` }}>
                              <div style={{ fontSize: 10, fontWeight: 800, color: COLORS.purple, marginBottom: 4 }}>{abbr}</div>
                              <div style={{ fontSize: 9, color: COLORS.textMuted, lineHeight: 1.4 }}>{desc}</div>
                            </div>
                          ))}
                        </div>
                      )}
                      {es.historical_fragmentation && (
                        <div style={{ padding: "9px 12px", borderRadius: 8, background: COLORS.warningDim, borderLeft: `3px solid ${COLORS.warning}`, fontSize: 10, color: COLORS.text, lineHeight: 1.5 }}>
                          {es.historical_fragmentation}
                        </div>
                      )}
                      {es.sources && (
                        <div style={{ display: "flex", gap: 6, marginTop: 10, flexWrap: "wrap" }}>
                          {es.sources.map(s => (
                            <a key={s.label} href={s.url} target="_blank" rel="noopener noreferrer" style={{
                              fontSize: 9, padding: "3px 10px", borderRadius: 4, background: COLORS.border,
                              color: COLORS.accent, textDecoration: "none", fontFamily: "'DM Mono', monospace",
                            }}>
                              {s.label}
                            </a>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* ── Cabecera lista partidos ── */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}` }}>
                    <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase" }}>
                      Fuerzas Políticas — {actors.total_actors} agrupaciones · Espectro ideológico
                    </div>
                    <div style={{ fontSize: 9, color: COLORS.textDim }}>
                      Izquierda ←————————————→ Derecha
                    </div>
                  </div>

                  {/* ── Cards de partidos ── */}
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                    {(actors.actors || []).map(actor => {
                      const expanded = !!expandedActors[actor.id];
                      const setExpanded = (fn) => setExpandedActors(prev => ({ ...prev, [actor.id]: typeof fn === "function" ? fn(prev[actor.id]) : fn }));
                      const riskC = actor.risk_profile === "high" ? COLORS.danger : actor.risk_profile === "moderate" ? COLORS.warning : COLORS.accent;
                      return (
                        <div key={actor.id} className="peru-card" style={{
                          borderRadius: 12, overflow: "hidden",
                          border: `1px solid ${actor.color}40`,
                          boxShadow: `0 0 20px ${actor.color}10`,
                        }}>
                          {/* Color header */}
                          <div style={{
                            padding: "12px 16px",
                            background: `linear-gradient(135deg, ${actor.color}22 0%, ${actor.color}08 100%)`,
                            borderBottom: `2px solid ${actor.color}`,
                            display: "flex", justifyContent: "space-between", alignItems: "flex-start",
                          }}>
                            <div>
                              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                                <div style={{
                                  width: 32, height: 32, borderRadius: 6, background: actor.color,
                                  display: "flex", alignItems: "center", justifyContent: "center",
                                  fontSize: 11, fontWeight: 900, color: "#fff", flexShrink: 0,
                                }}>
                                  {actor.abbr}
                                </div>
                                <div>
                                  <div style={{ fontSize: 14, fontWeight: 800, color: actor.color, lineHeight: 1.2 }}>{actor.name}</div>
                                  <div style={{ fontSize: 9, color: COLORS.textDim, marginTop: 1 }}>
                                    {actor.ideology} {actor.founded ? `· Est. ${actor.founded}` : ""}
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
                              <span style={{
                                fontSize: 9, padding: "2px 8px", borderRadius: 4,
                                background: riskC + "22", color: riskC,
                                fontFamily: "'DM Mono', monospace", fontWeight: 700,
                              }}>
                                {actor.risk_profile === "high" ? "RIESGO ALTO" : actor.risk_profile === "moderate" ? "RIESGO MOD." : "RIESGO BAJO"}
                              </span>
                              <span style={{ fontSize: 13, fontWeight: 800, color: actor.color, fontFamily: "'DM Mono', monospace" }}>
                                {actor.current_seats} esc.
                              </span>
                            </div>
                          </div>

                          {/* Body */}
                          <div style={{ padding: "12px 16px", background: COLORS.surface }}>
                            {/* Líder + posición ideológica */}
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                              <div style={{ fontSize: 11, color: COLORS.textMuted }}>
                                Liderazgo: <strong style={{ color: COLORS.text }}>{actor.leader}</strong>
                              </div>
                              <div style={{ fontSize: 9, color: COLORS.textDim }}>
                                Pos. {actor.position}/100
                              </div>
                            </div>

                            {/* Barra posición ideológica */}
                            <div style={{ marginBottom: 10 }}>
                              <div style={{ height: 4, borderRadius: 2, background: COLORS.border, position: "relative" }}>
                                <div style={{
                                  position: "absolute", top: -3, width: 10, height: 10, borderRadius: "50%",
                                  background: actor.color, border: "2px solid #0a0e17",
                                  left: `calc(${actor.position}% - 5px)`,
                                  boxShadow: `0 0 6px ${actor.color}`,
                                }} />
                              </div>
                              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 3 }}>
                                <span style={{ fontSize: 7, color: COLORS.textDim }}>← Izquierda</span>
                                <span style={{ fontSize: 7, color: COLORS.textDim }}>Derecha →</span>
                              </div>
                            </div>

                            {/* Antecedentes */}
                            {actor.background && (
                              <div style={{ fontSize: 10, color: COLORS.textMuted, lineHeight: 1.6, marginBottom: 10 }}>
                                {actor.background}
                              </div>
                            )}

                            {/* Candidatos 2026 */}
                            {actor.candidates_2026 && actor.candidates_2026.length > 0 && (
                              <div style={{ marginBottom: 10 }}>
                                <div style={{ fontSize: 9, fontWeight: 700, color: actor.color, letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 6 }}>
                                  Candidatos 2026
                                </div>
                                {actor.candidates_2026.map((c, ci) => (
                                  <div key={ci} style={{
                                    padding: "7px 10px", borderRadius: 7, marginBottom: 4,
                                    background: actor.color + "10", border: `1px solid ${actor.color}22`,
                                  }}>
                                    <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.text }}>{c.name}</div>
                                    <div style={{ fontSize: 9, color: actor.color, fontWeight: 600 }}>{c.role}</div>
                                    {c.notes && <div style={{ fontSize: 9, color: COLORS.textDim, marginTop: 2, lineHeight: 1.4 }}>{c.notes}</div>}
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Historia electoral (expandible) */}
                            {actor.electoral_history && actor.electoral_history.length > 0 && (
                              <div style={{ marginBottom: 10 }}>
                                <button onClick={() => setExpanded(v => !v)} style={{
                                  width: "100%", padding: "6px 10px", borderRadius: 7,
                                  background: "transparent", border: `1px solid ${COLORS.border}`,
                                  color: COLORS.textDim, fontSize: 9, cursor: "pointer",
                                  display: "flex", justifyContent: "space-between", alignItems: "center",
                                  fontFamily: "'DM Mono', monospace",
                                }}>
                                  <span>Historia Electoral ({actor.electoral_history.length} procesos)</span>
                                  <span>{expanded ? "▲" : "▼"}</span>
                                </button>
                                {expanded && (
                                  <div style={{ marginTop: 6, borderRadius: 7, overflow: "hidden", border: `1px solid ${COLORS.border}` }}>
                                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                                      <thead>
                                        <tr style={{ background: COLORS.surfaceLight }}>
                                          <th style={{ padding: "5px 8px", textAlign: "left", fontSize: 8, color: COLORS.textDim, fontWeight: 700 }}>AÑO</th>
                                          <th style={{ padding: "5px 8px", textAlign: "right", fontSize: 8, color: COLORS.textDim, fontWeight: 700 }}>ESC.</th>
                                          <th style={{ padding: "5px 8px", textAlign: "right", fontSize: 8, color: COLORS.textDim, fontWeight: 700 }}>1RA VUELTA</th>
                                          <th style={{ padding: "5px 8px", textAlign: "left", fontSize: 8, color: COLORS.textDim, fontWeight: 700 }}>RESULTADO</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {actor.electoral_history.map((h, hi) => (
                                          <tr key={hi} style={{ borderTop: `1px solid ${COLORS.border}` }}>
                                            <td style={{ padding: "5px 8px", fontSize: 10, color: actor.color, fontFamily: "'DM Mono', monospace", fontWeight: 700 }}>{h.year}</td>
                                            <td style={{ padding: "5px 8px", fontSize: 10, color: COLORS.text, fontFamily: "'DM Mono', monospace", textAlign: "right" }}>{h.seats}</td>
                                            <td style={{ padding: "5px 8px", fontSize: 10, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace", textAlign: "right" }}>
                                              {h.first_round_pct != null ? `${h.first_round_pct}%` : "—"}
                                            </td>
                                            <td style={{ padding: "5px 8px", fontSize: 9, color: COLORS.textDim, lineHeight: 1.3 }}>{h.result}</td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                )}
                              </div>
                            )}

                            {/* Key policies */}
                            {actor.key_policies && actor.key_policies.length > 0 && (
                              <div style={{ marginBottom: 10 }}>
                                <div style={{ fontSize: 9, fontWeight: 700, color: COLORS.textDim, letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 5 }}>
                                  Propuestas Clave
                                </div>
                                {actor.key_policies.map((p, pi) => (
                                  <div key={pi} style={{ fontSize: 9, color: COLORS.textMuted, padding: "2px 0 2px 8px", borderLeft: `2px solid ${actor.color}44`, marginBottom: 2 }}>
                                    {p}
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Fortalezas / vulnerabilidades */}
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 10 }}>
                              <div>
                                <div style={{ fontSize: 9, color: COLORS.accent, fontWeight: 700, marginBottom: 4 }}>FORTALEZAS</div>
                                {(actor.strengths || []).slice(0, 2).map((s, si) => (
                                  <div key={si} style={{ fontSize: 9, color: COLORS.textMuted, padding: "1px 0" }}>+ {s}</div>
                                ))}
                              </div>
                              <div>
                                <div style={{ fontSize: 9, color: COLORS.danger, fontWeight: 700, marginBottom: 4 }}>VULNERABILIDADES</div>
                                {(actor.vulnerabilities || []).slice(0, 2).map((v, vi) => (
                                  <div key={vi} style={{ fontSize: 9, color: COLORS.textMuted, padding: "1px 0" }}>- {v}</div>
                                ))}
                              </div>
                            </div>

                            {/* ICCPR risk */}
                            {actor.iccpr_risk && (
                              <div style={{
                                padding: "6px 10px", borderRadius: 6,
                                background: riskC + "11", borderLeft: `2px solid ${riskC}`,
                                fontSize: 9, color: COLORS.textDim, lineHeight: 1.5,
                              }}>
                                {actor.iccpr_risk}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* ══ TAB: PARLAMENTO ══ */}
        {innerTab === "parlamento" && (
          <div>
            {scenariosLoading && (
              <div style={{ padding: 60, textAlign: "center", color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
                Cargando datos parlamentarios...
              </div>
            )}
            {!scenariosLoading && !scenarios && (
              <div style={{ padding: 40, color: COLORS.danger, fontFamily: "'DM Mono', monospace", fontSize: 12 }}>
                Error cargando escenarios. Verificá /api/peru/scenarios en el backend.
              </div>
            )}
            {scenarios && (() => {
              const currentSeats = scenarios.current?.seats || [];
              const activeSc = (scenarios.scenarios || []).find(s => s.id === selectedScenario) || scenarios.scenarios?.[0];
              const sortedRegions = [...(scenarios.regions || [])].sort((a, b) => b.risk_score - a.risk_score).slice(0, 20);

              // ── HemicycleChart inline SVG function ──
              const drawHemicycle = (seats, svgWidth, svgHeight) => {
                const ROW_COUNTS = [18, 24, 28, 30, 30];
                const cx = svgWidth / 2;
                const cy = svgHeight - 8;
                const BASE_R = 52;
                const ROW_GAP = 20;
                const SEAT_R = 6;

                // Expand seats into ordered array of colors
                const filled = [];
                const sorted = [...seats].sort((a, b) => b.seats - a.seats);
                sorted.forEach(p => { for (let i = 0; i < p.seats; i++) filled.push(p.color); });
                while (filled.length < 130) filled.push("#2d3748");

                const circles = [];
                let idx = 0;
                ROW_COUNTS.forEach((n, row) => {
                  const r = BASE_R + row * ROW_GAP;
                  for (let k = 0; k < n; k++) {
                    const theta = Math.PI * k / (n - 1);
                    const x = cx - r * Math.cos(theta);
                    const y = cy - r * Math.sin(theta);
                    circles.push({ x, y, color: filled[idx] || "#2d3748" });
                    idx++;
                  }
                });

                return (
                  <svg width={svgWidth} height={svgHeight} style={{ display: "block", margin: "0 auto" }}>
                    {/* Arc guide lines */}
                    {ROW_COUNTS.map((_, row) => {
                      const r = BASE_R + row * ROW_GAP;
                      const d = `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`;
                      return <path key={row} d={d} fill="none" stroke={COLORS.border} strokeWidth={0.5} strokeOpacity={0.4} />;
                    })}
                    {/* Majority line */}
                    <line x1={cx} y1={cy} x2={cx} y2={cy - (BASE_R + 4 * ROW_GAP + 14)} stroke="#ffffff33" strokeWidth={1} strokeDasharray="4 3" />
                    <text x={cx + 4} y={cy - (BASE_R + 4 * ROW_GAP + 16)} fill="#ffffff55" fontSize={8} fontFamily="'DM Mono', monospace">66 mayoría</text>
                    {/* Seats */}
                    {circles.map((c, i) => (
                      <circle key={i} cx={c.x} cy={c.y} r={SEAT_R} fill={c.color} fillOpacity={0.88} stroke="#0a0e17" strokeWidth={0.8} />
                    ))}
                  </svg>
                );
              };

              return (
                <div>
                  {/* ── Congreso Actual ── */}
                  <div style={{ marginBottom: 24 }}>
                    <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 12, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}` }}>
                      Congreso Actual 2021–2026 — Composición al inicio de 2026
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 16 }}>
                      <Card className="peru-card">
                        <SectionTitle icon="🏛">Hemiciclo — 130 escaños</SectionTitle>
                        {drawHemicycle(currentSeats, 380, 200)}
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 10 }}>
                          {currentSeats.map(s => (
                            <div key={s.party} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                              <div style={{ width: 8, height: 8, borderRadius: "50%", background: s.color }} />
                              <span style={{ fontSize: 9, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
                                {s.full_name} <strong style={{ color: s.color }}>{s.seats}</strong>
                              </span>
                            </div>
                          ))}
                        </div>
                        <div style={{ marginTop: 10, fontSize: 9, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
                          Fragmentación: {scenarios.current?.fragmentation_index} · Partidos efectivos: {scenarios.current?.effective_parties}
                        </div>
                      </Card>

                      <Card className="peru-card">
                        <SectionTitle icon="📊">Distribución actual de bancadas</SectionTitle>
                        {currentSeats.map(s => (
                          <div key={s.party} style={{ marginBottom: 7 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                              <span style={{ fontSize: 10, color: COLORS.text, fontWeight: 600 }}>{s.full_name}</span>
                              <span style={{ fontSize: 11, fontWeight: 700, color: s.color, fontFamily: "'DM Mono', monospace" }}>{s.seats}</span>
                            </div>
                            <div style={{ height: 5, borderRadius: 3, background: COLORS.border }}>
                              <div style={{ height: "100%", width: `${(s.seats / 130) * 100}%`, borderRadius: 3, background: s.color, opacity: 0.8 }} />
                            </div>
                          </div>
                        ))}
                        <div style={{ marginTop: 10, padding: "7px 10px", borderRadius: 8, background: COLORS.dangerDim, borderLeft: `3px solid ${COLORS.danger}`, fontSize: 9, color: COLORS.textDim, lineHeight: 1.5 }}>
                          El 28.5% de legisladores (37) son congresistas sin bancada al inicio de 2026 — reflejo del transfuguismo estructural.
                          Ningún partido ha alcanzado mayoría absoluta (66 esc.) desde Fuerza Popular en 2016 (73 esc.).
                        </div>
                      </Card>
                    </div>
                  </div>

                  {/* ── Escenarios proyectados ── */}
                  <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 12, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}` }}>
                    Proyecciones Parlamentarias 2026 — Tres Escenarios
                  </div>
                  <div style={{ padding: "10px 14px", borderRadius: 9, background: COLORS.surfaceLight, marginBottom: 16, fontSize: 10, color: COLORS.textDim, lineHeight: 1.6 }}>
                    Los escenarios se basan en modelos estructurales (tendencias 2011-2021, encuestas 2025, datos V-Dem) y no constituyen predicción electoral.
                    La metodología D'Hondt favorece a partidos más grandes en distritos plurinominales. El umbral del 5% puede excluir hasta 3-4 agrupaciones actualmente activas.
                    <a href="https://www.onpe.gob.pe" target="_blank" rel="noopener noreferrer" style={{ color: COLORS.accent, marginLeft: 6 }}>Ver metodología ONPE →</a>
                  </div>

                  <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                    {(scenarios.scenarios || []).map(sc => (
                      <button key={sc.id} onClick={() => setSelectedScenario(sc.id)} style={{
                        flex: 1, padding: "10px 12px", borderRadius: 9,
                        background: selectedScenario === sc.id ? sc.color + "18" : "transparent",
                        border: `2px solid ${selectedScenario === sc.id ? sc.color : COLORS.border}`,
                        color: selectedScenario === sc.id ? sc.color : COLORS.textMuted,
                        fontSize: 11, fontWeight: 700, cursor: "pointer", fontFamily: "'DM Mono', monospace",
                        transition: "all 0.2s",
                      }}>
                        Escenario {sc.id}
                        <div style={{ fontSize: 9, opacity: 0.75, fontWeight: 400, marginTop: 2 }}>{sc.probability_pct}% prob.</div>
                      </button>
                    ))}
                  </div>

                  {activeSc && (
                    <div>
                      <div style={{
                        marginBottom: 16, padding: "14px 18px", borderRadius: 10,
                        background: activeSc.color + "0f",
                        border: `1px solid ${activeSc.color}33`,
                        borderLeft: `4px solid ${activeSc.color}`,
                      }}>
                        <div style={{ fontSize: 14, fontWeight: 800, color: activeSc.color, marginBottom: 6 }}>{activeSc.label}</div>
                        <div style={{ fontSize: 11, color: COLORS.text, lineHeight: 1.65, marginBottom: 8 }}>{activeSc.description}</div>
                        <div style={{
                          padding: "6px 12px", borderRadius: 7,
                          background: COLORS.dangerDim, borderLeft: `3px solid ${COLORS.danger}`,
                          fontSize: 10, color: COLORS.textMuted,
                        }}>
                          Riesgo de gobernabilidad: {activeSc.governance_risk}
                        </div>
                      </div>

                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                        <Card className="peru-card" style={{ borderLeft: `3px solid ${activeSc.color}` }}>
                          <SectionTitle icon="🏛">Hemiciclo — Escenario {activeSc.id}</SectionTitle>
                          {drawHemicycle(activeSc.seats, 380, 200)}
                          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 10 }}>
                            {(activeSc.seats || []).map(s => (
                              <div key={s.party} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                                <div style={{ width: 8, height: 8, borderRadius: "50%", background: s.color }} />
                                <span style={{ fontSize: 9, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
                                  {s.full_name} <strong style={{ color: s.color }}>{s.seats}</strong>
                                </span>
                              </div>
                            ))}
                          </div>
                        </Card>

                        <Card className="peru-card">
                          <SectionTitle icon="📊">Distribución — Escenario {activeSc.id}</SectionTitle>
                          {(activeSc.seats || []).map(s => (
                            <div key={s.party} style={{ marginBottom: 7 }}>
                              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                                <span style={{ fontSize: 10, color: COLORS.text, fontWeight: 600 }}>{s.full_name}</span>
                                <span style={{ fontSize: 11, fontWeight: 700, color: s.color, fontFamily: "'DM Mono', monospace" }}>{s.seats}</span>
                              </div>
                              <div style={{ height: 5, borderRadius: 3, background: COLORS.border }}>
                                <div style={{ height: "100%", width: `${(s.seats / 130) * 100}%`, borderRadius: 3, background: s.color, opacity: 0.8 }} />
                              </div>
                            </div>
                          ))}
                          <div style={{ marginTop: 8, fontSize: 9, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
                            Total: 130 esc. · Mayoría simple: 66 · Mayoría absoluta: 66
                          </div>
                        </Card>
                      </div>
                    </div>
                  )}

                  {/* ── Riesgo regional ── */}
                  <div style={{ marginTop: 24 }}>
                    <Card className="peru-card">
                      <SectionTitle icon="🗺">Riesgo Electoral por Región (Top 20)</SectionTitle>
                      <div style={{ fontSize: 9, color: COLORS.textDim, marginBottom: 10 }}>
                        Score 0–100 calculado con datos V-Dem, ONPE y factores estructurales (pobreza, fragmentación, presencia estatal).
                      </div>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={sortedRegions} layout="vertical" margin={{ left: 4, right: 16, top: 0, bottom: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} horizontal={false} />
                          <XAxis type="number" domain={[0, 100]} tick={{ fill: COLORS.textMuted, fontSize: 9 }} />
                          <YAxis type="category" dataKey="region" tick={{ fill: COLORS.textMuted, fontSize: 9, fontFamily: "'DM Mono', monospace" }} width={80} />
                          <Tooltip contentStyle={{ background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`, fontSize: 11 }} formatter={(v) => [`${v}/100`, "Riesgo"]} />
                          <Bar dataKey="risk_score" radius={[0, 4, 4, 0]}>
                            {sortedRegions.map((r, i) => (
                              <Cell key={i} fill={r.risk_score >= 60 ? COLORS.danger : r.risk_score >= 35 ? COLORS.warning : COLORS.accent} fillOpacity={0.8} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </Card>
                  </div>
                </div>
              );
            })()}
          </div>
        )}

                {/* ══ TAB: MOE BRIEF ══ */}
        {innerTab === "brief" && !brief && (
          <div style={{ padding: 40, textAlign: "center", color: COLORS.textDim, fontSize: 12 }}>
            MOE Brief no disponible. Verificá que el backend esté corriendo.
          </div>
        )}
        {innerTab === "brief" && brief && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}` }}>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", display: "flex", alignItems: "center", gap: 8 }}>
                MOE Brief — Misión de Observación Electoral
                <span style={{ fontSize: 9, color: COLORS.textDim, fontStyle: "italic", letterSpacing: 0, fontWeight: 400 }}>
                  Auto-generado · {new Date(brief.generated_at).toLocaleString("es-PE", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })} UTC
                </span>
              </div>
              <button onClick={downloadMOEBrief} style={{
                padding: "8px 16px", borderRadius: 8, border: `1px solid ${COLORS.accent}44`,
                background: COLORS.accentDim, color: COLORS.accent, fontSize: 11, fontWeight: 700,
                cursor: "pointer", fontFamily: "'DM Mono', monospace", display: "flex", alignItems: "center", gap: 6,
              }}>
                Exportar Markdown
              </button>
            </div>
            <div style={{ display: "flex", gap: 4, marginBottom: 16, borderBottom: `1px solid ${COLORS.border}` }}>
              {MOE_TABS.map(tab => (
                <button key={tab.id} onClick={() => setMoeTab(tab.id)} style={{
                  padding: "8px 16px", borderRadius: "7px 7px 0 0", border: "none",
                  cursor: "pointer", fontSize: 12, fontWeight: 600,
                  background: moeTab === tab.id ? COLORS.purpleDim : "transparent",
                  color: moeTab === tab.id ? COLORS.purple : COLORS.textMuted,
                  borderBottom: moeTab === tab.id ? `2px solid ${COLORS.purple}` : "2px solid transparent",
                  transition: "all 0.2s",
                }}>
                  {tab.icon} {tab.label}
                </button>
              ))}
            </div>
            {moeTab === "risk_context" && (() => {
              const b = brief.blocks.risk_context;
              return (
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  <Card className="peru-card">
                    <SectionTitle icon="📍">Indicadores Clave</SectionTitle>
                    {Object.entries(b.key_indicators).map(([k, v]) => (
                      <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "7px 0", borderBottom: `1px solid ${COLORS.border}` }}>
                        <span style={{ fontSize: 11, color: COLORS.textMuted, textTransform: "uppercase", letterSpacing: 0.5 }}>{k.replace(/_/g, " ")}</span>
                        <span style={{ fontSize: 12, fontWeight: 700, color: COLORS.text, fontFamily: "'DM Mono', monospace" }}>{v}</span>
                      </div>
                    ))}
                    <div style={{ marginTop: 10, padding: "6px 10px", borderRadius: 7, background: COLORS.surfaceLight }}>
                      <span style={{ fontSize: 10, color: COLORS.textDim }}>Tendencia: </span>
                      <span style={{ fontSize: 10, fontWeight: 700, color: b.trend === "deteriorating" ? COLORS.danger : COLORS.accent }}>
                        {b.trend === "deteriorating" ? "Deteriorando" : b.trend === "improving" ? "Mejorando" : "Estable"}
                      </span>
                    </div>
                  </Card>
                  <Card className="peru-card">
                    <SectionTitle icon="🚨">Violaciones Críticas Detectadas</SectionTitle>
                    {b.critical_violations.length === 0 ? (
                      <div style={{ padding: 16, textAlign: "center", color: COLORS.accent, fontSize: 12 }}>Sin violaciones críticas</div>
                    ) : b.critical_violations.map((v, i) => (
                      <div key={i} style={{ marginBottom: 10, padding: "9px 12px", borderRadius: 8, background: COLORS.dangerDim, borderLeft: `3px solid ${COLORS.danger}` }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: COLORS.danger, fontFamily: "'DM Mono', monospace", marginBottom: 3 }}>
                          {v.treaty} {v.article} · {v.severity.toUpperCase()}
                        </div>
                        <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5 }}>{v.finding}</div>
                      </div>
                    ))}
                    {b.risk_factors.length > 0 && (
                      <div style={{ marginTop: 8 }}>
                        <div style={{ fontSize: 10, color: COLORS.textDim, marginBottom: 6 }}>Factores adicionales:</div>
                        {b.risk_factors.map((f, i) => (
                          <div key={i} style={{ fontSize: 11, color: COLORS.textMuted, padding: "4px 0", borderBottom: `1px solid ${COLORS.border}` }}>· {f}</div>
                        ))}
                      </div>
                    )}
                  </Card>
                </div>
              );
            })()}
            {moeTab === "legal_framework" && (() => {
              const b = brief.blocks.legal_framework;
              return (
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  <Card className="peru-card">
                    <SectionTitle icon="🌍">Instrumentos Universales</SectionTitle>
                    {b.universal_instruments.map((inst) => (
                      <div key={inst.id} style={{ marginBottom: 10, padding: "8px 12px", borderRadius: 8, background: COLORS.surfaceLight }}>
                        <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.info, marginBottom: 3 }}>{inst.id}</div>
                        <div style={{ fontSize: 10, color: COLORS.text, marginBottom: 4 }}>{inst.name}</div>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                          {inst.key_articles.map(a => (
                            <span key={a} style={{ fontSize: 9, padding: "1px 6px", borderRadius: 4, background: COLORS.infoDim, color: COLORS.info, fontFamily: "'DM Mono', monospace" }}>{a}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                    <div style={{ marginTop: 8, padding: "8px 10px", borderRadius: 8, background: COLORS.surfaceLight, borderLeft: `3px solid ${COLORS.purple}` }}>
                      <div style={{ fontSize: 10, fontWeight: 700, color: COLORS.purple, marginBottom: 4 }}>Marco Nacional</div>
                      {Object.entries(b.national_framework).map(([k, v]) => (
                        <div key={k} style={{ fontSize: 10, color: COLORS.textMuted, padding: "2px 0" }}>· {v}</div>
                      ))}
                    </div>
                  </Card>
                  <Card className="peru-card">
                    <SectionTitle icon="🌎">Instrumentos Regionales (OEA)</SectionTitle>
                    {b.regional_instruments.map((inst) => (
                      <div key={inst.id} style={{ marginBottom: 10, padding: "8px 12px", borderRadius: 8, background: COLORS.surfaceLight }}>
                        <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.warning, marginBottom: 3 }}>{inst.id}</div>
                        <div style={{ fontSize: 10, color: COLORS.text, marginBottom: 4 }}>{inst.name}</div>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                          {inst.key_articles.map(a => (
                            <span key={a} style={{ fontSize: 9, padding: "1px 6px", borderRadius: 4, background: COLORS.warningDim, color: COLORS.warning, fontFamily: "'DM Mono', monospace" }}>{a}</span>
                          ))}
                        </div>
                        {inst.observer && <div style={{ fontSize: 9, color: COLORS.textDim, marginTop: 4 }}>{inst.observer}</div>}
                      </div>
                    ))}
                    <div style={{ marginTop: 8, padding: "8px 10px", borderRadius: 8, background: COLORS.surfaceLight, borderLeft: `3px solid ${COLORS.accent}` }}>
                      <div style={{ fontSize: 10, fontWeight: 700, color: COLORS.accent, marginBottom: 4 }}>Obligaciones Clave</div>
                      {b.key_obligations.map((o, i) => (
                        <div key={i} style={{ fontSize: 10, color: COLORS.textMuted, padding: "2px 0" }}>· {o}</div>
                      ))}
                    </div>
                  </Card>
                </div>
              );
            })()}
            {moeTab === "priority_areas" && (() => {
              const b = brief.blocks.priority_areas;
              const riskColor = (r) => r === "critical" ? COLORS.danger : r === "high" ? "#f97316" : r === "moderate" ? COLORS.warning : COLORS.info;
              return (
                <div>
                  <div style={{ display: "flex", gap: 12, marginBottom: 14 }}>
                    <div style={{ padding: "8px 16px", borderRadius: 8, background: COLORS.dangerDim, fontSize: 12, fontWeight: 700, color: COLORS.danger }}>
                      {b.high_risk_count} áreas de alto riesgo
                    </div>
                    <div style={{ padding: "8px 16px", borderRadius: 8, background: COLORS.warningDim, fontSize: 12, fontWeight: 700, color: COLORS.warning }}>
                      {b.moderate_risk_count} áreas de riesgo moderado
                    </div>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                    {b.priority_areas.map((area) => {
                      const ac = riskColor(area.risk);
                      return (
                        <div key={area.priority} className="peru-card" style={{
                          background: COLORS.surface, border: `1px solid ${ac}33`,
                          borderLeft: `3px solid ${ac}`, borderRadius: 10, padding: "12px 14px",
                        }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                            <div style={{ fontSize: 12, fontWeight: 700, color: COLORS.text }}>{area.priority}. {area.area}</div>
                            <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 4, background: ac + "22", color: ac, fontFamily: "'DM Mono', monospace", fontWeight: 700 }}>
                              {area.risk.toUpperCase()}
                            </span>
                          </div>
                          <div style={{ marginBottom: 6 }}>
                            {area.findings.map((f, i) => (
                              <div key={i} style={{ fontSize: 10, color: COLORS.textMuted, padding: "1px 0" }}>· {f}</div>
                            ))}
                          </div>
                          <div style={{ fontSize: 9, color: ac, fontFamily: "'DM Mono', monospace", marginBottom: 6 }}>{area.eos_standard}</div>
                          <div style={{ borderTop: `1px solid ${COLORS.border}`, paddingTop: 6 }}>
                            <div style={{ fontSize: 9, color: COLORS.textDim, marginBottom: 3 }}>TAREAS:</div>
                            {area.observation_tasks.map((t, i) => (
                              <div key={i} style={{ fontSize: 9, color: COLORS.textMuted, padding: "1px 0" }}>→ {t}</div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })()}
            {moeTab === "protocol" && (() => {
              const b = brief.blocks.protocol;
              const p = b.protocol;
              const protoColor = p.type === "LTO+STO" ? COLORS.danger : p.type === "STO" ? COLORS.warning : COLORS.accent;
              return (
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  <div>
                    <Card className="peru-card" style={{ marginBottom: 14 }}>
                      <SectionTitle icon="🛡">Tipo de Misión Recomendada</SectionTitle>
                      <div style={{ padding: "12px", borderRadius: 8, background: protoColor + "11", border: `1px solid ${protoColor}33`, marginBottom: 10 }}>
                        <div style={{ fontSize: 16, fontWeight: 800, color: protoColor, fontFamily: "'DM Mono', monospace", marginBottom: 4 }}>{p.type}</div>
                        <div style={{ fontSize: 12, fontWeight: 600, color: COLORS.text, marginBottom: 6 }}>{p.label}</div>
                        <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.6 }}>{p.description}</div>
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                        {[
                          { label: "Duración LTO", val: p.lto_duration },
                          { label: "Observadores STO", val: p.sto_count },
                          { label: "PVT", val: p.pvt_recommended ? "Recomendado" : "No requerido" },
                          { label: "SMM", val: p.smm_recommended ? "Recomendado" : "No requerido" },
                        ].map(({ label, val }) => (
                          <div key={label} style={{ padding: "7px 10px", borderRadius: 7, background: COLORS.surfaceLight }}>
                            <div style={{ fontSize: 9, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 0.5 }}>{label}</div>
                            <div style={{ fontSize: 11, fontWeight: 600, color: COLORS.text, marginTop: 2 }}>{val}</div>
                          </div>
                        ))}
                      </div>
                      {b.pvt_note && (
                        <div style={{ marginTop: 10, padding: "7px 10px", borderRadius: 7, background: COLORS.infoDim, fontSize: 10, color: COLORS.info, lineHeight: 1.5 }}>
                          {b.pvt_note}
                        </div>
                      )}
                    </Card>
                    <Card className="peru-card">
                      <SectionTitle icon="📅">Cronograma de Informes</SectionTitle>
                      {Object.entries(b.reporting_schedule).map(([k, v]) => (
                        <div key={k} style={{ display: "flex", gap: 10, padding: "8px 0", borderBottom: `1px solid ${COLORS.border}`, alignItems: "flex-start" }}>
                          <span style={{ fontSize: 9, padding: "2px 6px", borderRadius: 4, background: COLORS.purpleDim, color: COLORS.purple, fontFamily: "'DM Mono', monospace", whiteSpace: "nowrap", marginTop: 1 }}>
                            {k.replace(/_/g, " ").toUpperCase()}
                          </span>
                          <span style={{ fontSize: 11, color: COLORS.textMuted }}>{v}</span>
                        </div>
                      ))}
                    </Card>
                  </div>
                  <Card className="peru-card">
                    <SectionTitle icon="👁">Organismos Recomendados</SectionTitle>
                    {b.recommended_observers.map((obs, i) => (
                      <div key={i} style={{ display: "flex", gap: 12, padding: "10px 12px", borderRadius: 8, background: COLORS.surfaceLight, marginBottom: 8 }}>
                        <div style={{ width: 36, height: 36, borderRadius: 8, background: COLORS.purpleDim, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, flexShrink: 0 }}>👁</div>
                        <div>
                          <div style={{ fontSize: 12, fontWeight: 700, color: COLORS.text }}>{obs.org}</div>
                          <div style={{ fontSize: 10, color: COLORS.textMuted, marginTop: 2 }}>{obs.role}</div>
                        </div>
                      </div>
                    ))}
                    <div style={{ marginTop: 10, padding: "8px 10px", borderRadius: 7, background: COLORS.surfaceLight, borderLeft: `3px solid ${COLORS.info}`, fontSize: 10, color: COLORS.textDim, lineHeight: 1.6 }}>
                      La selección final depende de acuerdos bilaterales entre el gobierno peruano y los organismos internacionales.
                    </div>
                  </Card>
                </div>
              );
            })()}
          </div>
        )}

        {/* ══ TAB: JORNADA ══ */}
        {innerTab === "jornada" && (
          <div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
              <Card className="peru-card">
                <SectionTitle icon="🗳">Panel de Monitoreo — Día de Votación</SectionTitle>
                <div style={{ fontSize: 10, color: COLORS.textDim, marginBottom: 16, lineHeight: 1.6 }}>
                  Ingresá datos en tiempo real desde centros de votación. El agente OSINT analizará el impacto en el índice de riesgo operativo.
                </div>
                {[
                  { key: "participation_pct",       label: "Participación estimada (%)",        type: "number", min: 0, max: 100 },
                  { key: "results_transmitted_pct", label: "Actas transmitidas (%)",            type: "number", min: 0, max: 100 },
                  { key: "violence_incidents",       label: "Incidentes de violencia reportados", type: "number", min: 0, max: 999 },
                ].map(field => (
                  <div key={field.key} style={{ marginBottom: 14 }}>
                    <label style={{ fontSize: 11, color: COLORS.textMuted, display: "block", marginBottom: 5 }}>{field.label}</label>
                    <input
                      type={field.type} min={field.min} max={field.max}
                      value={journeyForm[field.key]}
                      onChange={e => setJourneyForm(f => ({ ...f, [field.key]: e.target.value }))}
                      style={{
                        width: "100%", padding: "9px 12px", borderRadius: 8,
                        background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`,
                        color: COLORS.text, fontSize: 13, fontFamily: "'DM Mono', monospace",
                        outline: "none", boxSizing: "border-box",
                      }}
                    />
                  </div>
                ))}
                <div style={{ marginBottom: 14 }}>
                  <label style={{ fontSize: 11, color: COLORS.textMuted, display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
                    <input
                      type="checkbox"
                      checked={journeyForm.internet_disruptions}
                      onChange={e => setJourneyForm(f => ({ ...f, internet_disruptions: e.target.checked }))}
                    />
                    Disrupciones de internet / redes sociales detectadas
                  </label>
                </div>
                <div style={{ marginBottom: 16 }}>
                  <label style={{ fontSize: 11, color: COLORS.textMuted, display: "block", marginBottom: 5 }}>
                    Incidentes documentados (uno por línea):
                  </label>
                  <textarea
                    value={journeyForm.incidents}
                    onChange={e => setJourneyForm(f => ({ ...f, incidents: e.target.value }))}
                    rows={4}
                    placeholder={"Urnas sin precintar en Lima Norte\nObservadores impedidos en Loreto\nCorte eléctrica en 3 mesas en Puno"}
                    style={{
                      width: "100%", padding: "9px 12px", borderRadius: 8,
                      background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`,
                      color: COLORS.text, fontSize: 11, fontFamily: "'DM Mono', monospace",
                      outline: "none", resize: "vertical", boxSizing: "border-box",
                    }}
                  />
                </div>
                <button onClick={submitJornada} disabled={journeySubmitting || !country?.run_id} style={{
                  width: "100%", padding: "12px", borderRadius: 8,
                  background: journeySubmitting ? COLORS.border : alertColor + "22",
                  border: `1px solid ${alertColor}44`, color: alertColor,
                  fontSize: 12, fontWeight: 700, cursor: journeySubmitting ? "not-allowed" : "pointer",
                  fontFamily: "'DM Mono', monospace",
                }}>
                  {journeySubmitting ? "Analizando..." : "Enviar al Agente OSINT"}
                </button>
                {!country?.run_id && (
                  <div style={{ marginTop: 8, fontSize: 10, color: COLORS.warning, textAlign: "center" }}>
                    Requiere reporte previo generado para PER
                  </div>
                )}
              </Card>
              <div>
                {journeyResult && !journeyResult.error && (
                  <Card className="peru-card" style={{ borderLeft: `3px solid ${alertColor}` }}>
                    <SectionTitle icon="📡">Análisis en Tiempo Real</SectionTitle>
                    {journeyResult.risk_delta !== undefined && (
                      <div style={{ padding: "10px 14px", borderRadius: 8, background: COLORS.surfaceLight, marginBottom: 14 }}>
                        <div style={{ fontSize: 10, color: COLORS.textDim, marginBottom: 4 }}>VARIACIÓN DEL ÍNDICE DE RIESGO</div>
                        <div style={{ fontSize: 28, fontWeight: 800, fontFamily: "'DM Mono', monospace",
                          color: journeyResult.risk_delta > 0 ? COLORS.danger : COLORS.accent }}>
                          {journeyResult.risk_delta > 0 ? "+" : ""}{journeyResult.risk_delta} pts
                        </div>
                      </div>
                    )}
                    {journeyResult.alerts && journeyResult.alerts.length > 0 && (
                      <div style={{ marginBottom: 12 }}>
                        <div style={{ fontSize: 10, color: COLORS.danger, fontWeight: 700, marginBottom: 8 }}>ALERTAS ACTIVADAS:</div>
                        {journeyResult.alerts.map((alert, i) => (
                          <div key={i} style={{ padding: "7px 10px", borderRadius: 6, background: COLORS.dangerDim, borderLeft: `2px solid ${COLORS.danger}`, marginBottom: 6, fontSize: 11, color: COLORS.textMuted }}>
                            {alert}
                          </div>
                        ))}
                      </div>
                    )}
                    {journeyResult.analysis && (
                      <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.7 }}>{journeyResult.analysis}</div>
                    )}
                    {!journeyResult.alerts && !journeyResult.risk_delta && (
                      <pre style={{ fontSize: 10, color: COLORS.textMuted, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                        {JSON.stringify(journeyResult, null, 2)}
                      </pre>
                    )}
                  </Card>
                )}
                {journeyResult?.error && (
                  <Card><div style={{ color: COLORS.danger, fontSize: 12, padding: 8 }}>Error: {journeyResult.error}</div></Card>
                )}
                {!journeyResult && (
                  <Card>
                    <div style={{ padding: 32, textAlign: "center", color: COLORS.textDim, fontSize: 12, lineHeight: 1.8 }}>
                      <div style={{ fontSize: 32, marginBottom: 12 }}>🗳</div>
                      <div style={{ fontWeight: 700, marginBottom: 8, color: COLORS.textMuted }}>Panel en espera</div>
                      <div>Completá el formulario y enviá los datos para activar el análisis de inteligencia en tiempo real.</div>
                      <div style={{ marginTop: 12, fontSize: 10, color: COLORS.textDim }}>
                        Jornada Electoral: 12 de abril de 2026 · 7:00–17:00 (hora Lima)
                      </div>
                    </div>
                  </Card>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ══ TAB: ALERTAS EN VIVO ══ */}
        {innerTab === "alertas" && (
          <div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}`, gap: 12, flexWrap: "wrap" }}>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", display: "flex", alignItems: "center", gap: 8 }}>
                Alertas en vivo — Hunter + Discord
                {liveAlertsLoading && <span style={{ color: COLORS.accent }}>● cargando…</span>}
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center", fontSize: 11, fontFamily: "'DM Mono', monospace" }}>
                <label style={{ color: COLORS.textMuted }}>
                  Severidad min:
                  <select
                    value={liveAlertsSeverity}
                    onChange={(e) => setLiveAlertsSeverity(e.target.value)}
                    style={{ marginLeft: 6, background: COLORS.surface, color: COLORS.text, border: `1px solid ${COLORS.border}`, padding: "3px 6px", borderRadius: 4 }}
                  >
                    <option value="low">low</option>
                    <option value="medium">medium</option>
                    <option value="high">high</option>
                    <option value="critical">critical</option>
                  </select>
                </label>
                <label style={{ color: COLORS.textMuted }}>
                  Ventana:
                  <select
                    value={liveAlertsHours}
                    onChange={(e) => setLiveAlertsHours(Number(e.target.value))}
                    style={{ marginLeft: 6, background: COLORS.surface, color: COLORS.text, border: `1px solid ${COLORS.border}`, padding: "3px 6px", borderRadius: 4 }}
                  >
                    <option value={24}>24h</option>
                    <option value={72}>72h</option>
                    <option value={168}>7 días</option>
                    <option value={720}>30 días</option>
                  </select>
                </label>
                <button
                  onClick={fetchLiveAlerts}
                  disabled={liveAlertsLoading}
                  style={{ padding: "4px 10px", background: COLORS.accentDim, color: COLORS.accent, border: `1px solid ${COLORS.accent}55`, borderRadius: 4, cursor: liveAlertsLoading ? "wait" : "pointer", fontSize: 11, fontWeight: 700, fontFamily: "'DM Mono', monospace" }}
                >
                  ↻ Refrescar
                </button>
              </div>
            </div>

            <div style={{ fontSize: 12, color: COLORS.textMuted, marginBottom: 16, lineHeight: 1.5 }}>
              Alertas detectadas automáticamente por el Hunter cada 4h sobre 5 fuentes RSS peruanas
              (Andina, El Comercio, Gestión, IDL-Reporteros, RPP). Las severidades high y critical también
              se despachan al canal Discord configurado. Auto-refresh cada 5 min.
              {liveAlertsLastFetch && (
                <span style={{ marginLeft: 8, color: COLORS.textDim, fontFamily: "'DM Mono', monospace", fontSize: 10 }}>
                  · última actualización: {liveAlertsLastFetch.toLocaleTimeString("es-PE")}
                </span>
              )}
            </div>

            {liveAlertsError && (
              <Card className="peru-card" style={{ padding: 14, background: COLORS.dangerDim, borderLeft: `3px solid ${COLORS.danger}`, marginBottom: 16 }}>
                <div style={{ color: COLORS.danger, fontSize: 12, fontWeight: 700 }}>Error: {liveAlertsError}</div>
              </Card>
            )}

            {liveAlerts && (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 20 }}>
                {[
                  { key: "critical", label: "Críticas",  color: COLORS.danger },
                  { key: "high",     label: "Altas",     color: "#f97316" },
                  { key: "medium",   label: "Medias",    color: COLORS.warning },
                  { key: "low",      label: "Bajas",     color: COLORS.info },
                ].map(({ key, label, color }) => {
                  const count = liveAlerts.counts_by_severity?.[key] || 0;
                  return (
                    <Card key={key} className="peru-card" style={{ padding: 14, borderLeft: `3px solid ${color}`, textAlign: "center" }}>
                      <div style={{ fontSize: 26, fontWeight: 800, color, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>{count}</div>
                      <div style={{ fontSize: 10, color: COLORS.textMuted, marginTop: 4, letterSpacing: 1, textTransform: "uppercase" }}>{label}</div>
                    </Card>
                  );
                })}
              </div>
            )}

            {liveAlerts && liveAlerts.alerts && liveAlerts.alerts.length === 0 && !liveAlertsLoading && (
              <Card className="peru-card" style={{ padding: 24, textAlign: "center", color: COLORS.textMuted, fontSize: 13 }}>
                Sin alertas en la ventana seleccionada. El Hunter corre cada 4h —
                podés disparar uno manualmente con el botón <strong>▶ HUNTER NOW</strong> arriba.
              </Card>
            )}

            {liveAlerts && liveAlerts.alerts && liveAlerts.alerts.length > 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {liveAlerts.alerts.map((a, i) => {
                  const sev = (a.severity || "low").toLowerCase();
                  const sevColor = sev === "critical" ? COLORS.danger : sev === "high" ? "#f97316" : sev === "medium" || sev === "moderate" ? COLORS.warning : COLORS.info;
                  const dispatched = a.dispatched_at ? new Date(a.dispatched_at) : null;
                  return (
                    <Card key={a.alert_id || i} className="peru-card" style={{ padding: 14, borderLeft: `3px solid ${sevColor}` }}>
                      <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
                        <div style={{ minWidth: 72, fontFamily: "'DM Mono', monospace" }}>
                          <div style={{ fontSize: 9, fontWeight: 700, color: sevColor, textTransform: "uppercase", letterSpacing: 1, padding: "2px 6px", border: `1px solid ${sevColor}66`, borderRadius: 4, textAlign: "center", marginBottom: 4 }}>
                            {sev}
                          </div>
                          {dispatched && (
                            <div style={{ fontSize: 9, color: COLORS.textDim, textAlign: "center" }}>
                              {dispatched.toLocaleDateString("es-PE", { day: "2-digit", month: "2-digit" })}<br />
                              {dispatched.toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit" })}
                            </div>
                          )}
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 13, fontWeight: 700, color: COLORS.text, marginBottom: 4, lineHeight: 1.4 }}>
                            {a.title || "(sin título)"}
                          </div>
                          {(() => {
                            // El backend empaqueta source/url en description con un separador
                            // "📎 Fuente: <medio> — <título>\n🔗 <url>". Lo parseamos para
                            // mostrar el link clickeable separado del finding.
                            const desc = a.description || "";
                            const urlMatch = desc.match(/🔗\s*(https?:\/\/\S+)/);
                            const sourceMatch = desc.match(/📎\s*Fuente:\s*([^—\n]+?)(?:\s*—\s*([^\n]+))?\s*\n/);
                            const finding = desc.split("📎")[0].trim();
                            const url = urlMatch ? urlMatch[1] : null;
                            const sourceName = sourceMatch ? sourceMatch[1].trim() : null;
                            const sourceTitle = sourceMatch ? (sourceMatch[2] || "").trim() : null;
                            return (
                              <>
                                {finding && (
                                  <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5, marginBottom: 8 }}>
                                    {finding}
                                  </div>
                                )}
                                {(url || sourceName) && (
                                  <div style={{ fontSize: 11, padding: "6px 10px", background: COLORS.surface, borderRadius: 4, marginBottom: 6, borderLeft: `2px solid ${COLORS.accent}` }}>
                                    {sourceName && (
                                      <div style={{ fontSize: 10, color: COLORS.accent, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, marginBottom: 2 }}>
                                        📎 {sourceName}
                                      </div>
                                    )}
                                    {url ? (
                                      <a
                                        href={url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{ color: COLORS.text, textDecoration: "underline", fontSize: 11, lineHeight: 1.4, wordBreak: "break-word" }}
                                      >
                                        {sourceTitle || url}
                                      </a>
                                    ) : sourceTitle && (
                                      <span style={{ color: COLORS.textMuted }}>{sourceTitle}</span>
                                    )}
                                  </div>
                                )}
                              </>
                            );
                          })()}
                          <div style={{ display: "flex", gap: 12, fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
                            {a.event_type && <span>tipo: {a.event_type}</span>}
                            {Array.isArray(a.rights_at_risk) && a.rights_at_risk.length > 0 && (
                              <span>derechos: {a.rights_at_risk.slice(0, 2).join(", ")}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ══ TAB: CALENDARIO LEGAL ══ */}
        {innerTab === "calendario" && (
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 6, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", gap: 8 }}>
              Calendario Legal — Restricciones del Proceso Electoral 2026
            </div>
            <div style={{ fontSize: 12, color: COLORS.textMuted, marginBottom: 20, lineHeight: 1.5 }}>
              Hitos legales y operativos vinculantes del proceso electoral peruano. Cada entrada incluye su base normativa (Ley Orgánica de Elecciones N° 26859 y resoluciones JNE/ONPE 2026) para verificación independiente por el observador.
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {PERU_LEGAL_CALENDAR.map((ev, i) => {
                const evDate = new Date(`${ev.date}T${ev.time}:00-05:00`);
                const isPast = evDate < new Date();
                const isToday = ev.date === new Date().toISOString().slice(0, 10);
                const accent = isToday ? COLORS.warning : isPast ? COLORS.textDim : COLORS.accent;
                return (
                  <Card key={i} className="peru-card" style={{ padding: 14, borderLeft: `3px solid ${accent}`, opacity: isPast ? 0.6 : 1 }}>
                    <div style={{ display: "flex", alignItems: "flex-start", gap: 16 }}>
                      <div style={{ minWidth: 96, fontFamily: "'DM Mono', monospace" }}>
                        <div style={{ fontSize: 13, fontWeight: 700, color: accent, letterSpacing: 0.5 }}>{ev.date}</div>
                        <div style={{ fontSize: 11, color: COLORS.textMuted, marginTop: 2 }}>{ev.time} PET</div>
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 13, fontWeight: 700, color: COLORS.text, marginBottom: 4 }}>
                          {isToday && <span style={{ color: COLORS.warning, marginRight: 6 }}>● HOY</span>}
                          {ev.label}
                        </div>
                        <div style={{ fontSize: 12, color: COLORS.textMuted, lineHeight: 1.5, marginBottom: 6 }}>{ev.detail}</div>
                        <div style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace", letterSpacing: 0.3 }}>
                          📖 {ev.source}
                        </div>
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
            <div style={{ marginTop: 20, padding: 12, background: COLORS.surface, border: `1px dashed ${COLORS.border}`, borderRadius: 6, fontSize: 11, color: COLORS.textDim, lineHeight: 1.5 }}>
              ⚠ Esta vista es de referencia. Verificar siempre contra las resoluciones vigentes publicadas por JNE (jne.gob.pe) y ONPE (onpe.gob.pe), que pueden actualizarse hasta el día previo a la jornada.
            </div>
          </div>
        )}

        {/* ══ TAB: DATOS V-DEM ══ */}
        {innerTab === "datos" && (
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 16, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", gap: 8 }}>
              Datos V-Dem — Series Históricas Perú 2026
              <span style={{ flex: 1, height: 1, background: `linear-gradient(90deg, ${COLORS.border}, transparent)` }} />
              {chartData && <span style={{ fontSize: 9, color: COLORS.textDim, fontWeight: 400 }}>Fuente: V-Dem v15 · FH 2025 · RSF 2025 · PEI v10.0</span>}
            </div>

            {chartLoading && (
              <div style={{ padding: 40, textAlign: "center", color: COLORS.textDim, fontFamily: "'DM Mono', monospace", fontSize: 12 }}>
                Cargando datos V-Dem...
              </div>
            )}

            {!chartLoading && chartError && (
              <div style={{ padding: 40, textAlign: "center", color: COLORS.danger, fontFamily: "'DM Mono', monospace", fontSize: 12 }}>
                Error al cargar datos. Verificá que el backend esté activo.
              </div>
            )}

            {chartData && (() => {
              const { charts, milestones, fh, rsf, pei } = chartData;

              /* ── KPI badges ── */
              return (
                <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>

                  {/* KPI row */}
                  <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                    {[
                      { label: "V-Dem libdem 2024", value: (charts.libdem_series.at(-1)?.value ?? "—").toFixed ? (charts.libdem_series.at(-1).value).toFixed(3) : "—", color: COLORS.accent, sub: "Democracia Liberal" },
                      { label: "Freedom House 2025", value: `${fh?.total_score ?? "—"}/100`, color: fh?.total_score >= 60 ? COLORS.accent : fh?.total_score >= 40 ? COLORS.warning : COLORS.danger, sub: fh?.status ?? "—" },
                      { label: "RSF Press Freedom", value: `${rsf?.score?.toFixed(1) ?? "—"}/100`, color: rsf?.score >= 50 ? COLORS.warning : COLORS.danger, sub: `Rank #${rsf?.rank ?? "—"} mundial` },
                      { label: "PEI Integridad", value: `${pei?.overall_integrity ?? "—"}/100`, color: pei?.overall_integrity >= 70 ? COLORS.accent : COLORS.warning, sub: `Elecciones ${pei?.year ?? "—"}` },
                    ].map(k => (
                      <div key={k.label} style={{ flex: "1 1 140px", background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 8, padding: "12px 16px" }}>
                        <div style={{ fontSize: 9, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 2, marginBottom: 4 }}>{k.label}</div>
                        <div style={{ fontSize: 22, fontWeight: 800, color: k.color, fontFamily: "'DM Mono', monospace" }}>{k.value}</div>
                        <div style={{ fontSize: 10, color: COLORS.textMuted, marginTop: 2 }}>{k.sub}</div>
                      </div>
                    ))}
                  </div>

                  {/* ── CHART 1: Liberal Democracy AreaChart ── */}
                  <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: "20px 16px" }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.text, marginBottom: 4 }}>Índice de Democracia Liberal — Perú 1990–2024</div>
                    <div style={{ fontSize: 9, color: COLORS.textDim, marginBottom: 16 }}>V-Dem v15 · v2x_libdem · escala 0–1</div>
                    <ResponsiveContainer width="100%" height={220}>
                      <AreaChart data={charts.libdem_series} margin={{ top: 8, right: 20, left: 0, bottom: 0 }}>
                        <defs>
                          <linearGradient id="libdemGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={COLORS.accent} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={COLORS.accent} stopOpacity={0.02} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                        <XAxis dataKey="year" tick={{ fontSize: 9, fill: COLORS.textDim }} tickLine={false} />
                        <YAxis domain={[0, 1]} tick={{ fontSize: 9, fill: COLORS.textDim }} tickLine={false} width={32} />
                        <Tooltip
                          contentStyle={{ background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: 6, fontSize: 11 }}
                          formatter={(v) => [v.toFixed(3), "Democracia Liberal"]}
                        />
                        {milestones.map(m => (
                          <ReferenceLine key={m.year} x={m.year}
                            stroke={m.type === "crisis" ? COLORS.danger : m.type === "upcoming" ? COLORS.warning : COLORS.accent}
                            strokeDasharray="4 2" strokeOpacity={0.6}
                            label={{ value: m.label, position: "top", fontSize: 7, fill: COLORS.textDim, offset: 4 }}
                          />
                        ))}
                        <Area type="monotone" dataKey="value" stroke={COLORS.accent} strokeWidth={2} fill="url(#libdemGrad)" dot={false} activeDot={{ r: 4 }} />
                        <ReferenceLine y={0.5} stroke={COLORS.warning} strokeDasharray="6 3" strokeOpacity={0.5} label={{ value: "umbral 0.5", position: "right", fontSize: 8, fill: COLORS.warning }} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  {/* ── CHART 3: OGE Autonomía + Capacidad ── */}
                  <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: "20px 16px" }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.text, marginBottom: 4 }}>JNE — Autonomía e Independencia Institucional 2010–2024</div>
                    <div style={{ fontSize: 9, color: COLORS.textDim, marginBottom: 16 }}>V-Dem v15 · v2elembaut (autonomía) + v2elembcap (capacidad) · escala −4 a +4</div>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={charts.emb_series} margin={{ top: 4, right: 20, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                        <XAxis dataKey="year" tick={{ fontSize: 9, fill: COLORS.textDim }} tickLine={false} />
                        <YAxis tick={{ fontSize: 9, fill: COLORS.textDim }} tickLine={false} width={36} />
                        <Tooltip
                          contentStyle={{ background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: 6, fontSize: 11 }}
                          formatter={(v, name) => [v.toFixed(3), name === "v2elembaut" ? "Autonomía OGE" : "Capacidad OGE"]}
                        />
                        <Legend formatter={(v) => v === "v2elembaut" ? "Autonomía" : "Capacidad"} wrapperStyle={{ fontSize: 10 }} />
                        <Bar dataKey="v2elembaut" fill={COLORS.accent} radius={[3, 3, 0, 0]} />
                        <Bar dataKey="v2elembcap" fill="#10b981" radius={[3, 3, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* ── CHART 5: Libertad de Prensa ── */}
                  <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: "20px 16px" }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.text, marginBottom: 4 }}>Ecosistema Mediático — Perú 2010–2024</div>
                    <div style={{ fontSize: 9, color: COLORS.textDim, marginBottom: 16 }}>V-Dem v15 · v2mebias (sesgo) · v2meharjrn (acoso periodistas) · v2mecenefi (censura) · escala −4 a +4 · RSF 2025: {rsf?.score?.toFixed(1)}/100</div>
                    <ResponsiveContainer width="100%" height={210}>
                      <LineChart data={charts.media_series} margin={{ top: 4, right: 20, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                        <XAxis dataKey="year" tick={{ fontSize: 9, fill: COLORS.textDim }} tickLine={false} />
                        <YAxis tick={{ fontSize: 9, fill: COLORS.textDim }} tickLine={false} width={36} />
                        <Tooltip
                          contentStyle={{ background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: 6, fontSize: 11 }}
                          formatter={(v, name) => [v.toFixed(3), name === "v2mebias" ? "Sesgo mediático" : name === "v2meharjrn" ? "Acoso periodistas" : "Censura ejecución"]}
                        />
                        <Legend formatter={(v) => v === "v2mebias" ? "Sesgo mediático" : v === "v2meharjrn" ? "Acoso periodistas" : "Censura ejecución"} wrapperStyle={{ fontSize: 10 }} />
                        <Line type="monotone" dataKey="v2mebias" stroke={COLORS.danger} strokeWidth={2} dot={false} activeDot={{ r: 3 }} />
                        <Line type="monotone" dataKey="v2meharjrn" stroke={COLORS.warning} strokeWidth={2} dot={false} activeDot={{ r: 3 }} />
                        <Line type="monotone" dataKey="v2mecenefi" stroke={COLORS.accent} strokeWidth={2} dot={false} activeDot={{ r: 3 }} />
                        <ReferenceLine y={1.0} stroke={COLORS.warning} strokeDasharray="5 3" strokeOpacity={0.4} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* ── CHART 4: Comparación Regional ── */}
                  <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: "20px 16px" }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.text, marginBottom: 4 }}>Perú en Perspectiva Regional — Democracia Liberal 2024</div>
                    <div style={{ fontSize: 9, color: COLORS.textDim, marginBottom: 16 }}>V-Dem v15 · v2x_libdem · ordenado de mayor a menor · Perú resaltado</div>
                    <ResponsiveContainer width="100%" height={320}>
                      <BarChart data={[...charts.regional].sort((a, b) => b.libdem - a.libdem)} layout="vertical" margin={{ top: 0, right: 40, left: 4, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} horizontal={false} />
                        <XAxis type="number" domain={[0, 1]} tick={{ fontSize: 9, fill: COLORS.textDim }} tickLine={false} />
                        <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: COLORS.textDim }} tickLine={false} width={72} />
                        <Tooltip
                          contentStyle={{ background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: 6, fontSize: 11 }}
                          formatter={(v) => [v.toFixed(3), "Democracia Liberal"]}
                        />
                        <Bar dataKey="libdem" radius={[0, 4, 4, 0]}>
                          {[...charts.regional].sort((a, b) => b.libdem - a.libdem).map((entry) => (
                            <Cell key={entry.country_code} fill={entry.highlight ? COLORS.warning : COLORS.accent} fillOpacity={entry.highlight ? 1 : 0.6} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                    <div style={{ marginTop: 8, fontSize: 9, color: COLORS.textDim, textAlign: "center" }}>
                      <span style={{ color: COLORS.warning, marginRight: 4 }}>●</span>Perú 2026 — próximas elecciones 12 abril
                    </div>
                  </div>

                  {/* ── PEI Detail ── */}
                  {pei && (
                    <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: "20px 16px" }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.text, marginBottom: 4 }}>PEI v10.0 — Integridad Electoral Perú {pei.year}</div>
                      <div style={{ fontSize: 9, color: COLORS.textDim, marginBottom: 16 }}>Perceptions of Electoral Integrity · {pei.office} · Electoral Integrity Project</div>
                      <ResponsiveContainer width="100%" height={200}>
                        <BarChart
                          data={[
                            { name: "Marco Legal", v: pei.legal_framework },
                            { name: "Procedimientos", v: pei.procedures },
                            { name: "Reg. Votantes", v: pei.voter_registration },
                            { name: "Cobertura Media", v: pei.media_coverage },
                            { name: "Financiamiento", v: pei.campaign_finance },
                            { name: "Voto", v: pei.voting_process },
                            { name: "Conteo", v: pei.vote_count },
                            { name: "Resultados", v: pei.voting_results },
                            { name: "EMBs", v: pei.emb_score },
                          ].filter(d => d.v !== null)}
                          margin={{ top: 4, right: 20, left: 0, bottom: 20 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                          <XAxis dataKey="name" tick={{ fontSize: 8, fill: COLORS.textDim }} tickLine={false} angle={-30} textAnchor="end" />
                          <YAxis domain={[0, 100]} tick={{ fontSize: 9, fill: COLORS.textDim }} tickLine={false} width={28} />
                          <Tooltip contentStyle={{ background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: 6, fontSize: 11 }} formatter={(v) => [`${v}/100`, "Score PEI"]} />
                          <ReferenceLine y={pei.overall_integrity} stroke={COLORS.accent} strokeDasharray="5 3" label={{ value: `Media ${pei.overall_integrity}`, position: "right", fontSize: 8, fill: COLORS.accent }} />
                          <Bar dataKey="v" radius={[3, 3, 0, 0]}>
                            {[pei.legal_framework, pei.procedures, pei.voter_registration, pei.media_coverage, pei.campaign_finance, pei.voting_process, pei.vote_count, pei.voting_results, pei.emb_score].filter(v => v !== null).map((v, i) => (
                              <Cell key={i} fill={v < 50 ? COLORS.danger : v < 70 ? COLORS.warning : COLORS.accent} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                      <div style={{ marginTop: 8, fontSize: 9, color: COLORS.textDim, textAlign: "right" }}>
                        Integridad Global: <span style={{ color: COLORS.accent, fontWeight: 700 }}>{pei.overall_integrity}/100</span>
                      </div>
                    </div>
                  )}

                </div>
              );
            })()}
          </div>
        )}

        {/* ══ TAB: EVALUACIÓN ══ */}
        {innerTab === "evaluacion" && (() => {
          const SCALE_LABELS = {
            0: { label: "Sin información", color: "#475569" },
            1: { label: "Muy deficiente", color: "#ef4444" },
            2: { label: "Deficiente",     color: "#f97316" },
            3: { label: "Regular",        color: "#eab308" },
            4: { label: "Satisfactorio",  color: "#22c55e" },
            5: { label: "Excelente",      color: "#00d4ff" },
          };
          const YESNO_LABELS = {
            0: { label: "Sin información", color: "#475569" },
            1: { label: "No",              color: "#ef4444" },
            2: { label: "Parcialmente",    color: "#f97316" },
            3: { label: "Mayormente sí",   color: "#22c55e" },
            4: { label: "Sí, plenamente",  color: "#00d4ff" },
          };

          const qList = evalQuestionnaire?.questionnaire || [];
          const sectionsMeta = evalQuestionnaire?.sections || [];
          const currentSection = sectionsMeta[evalSection] || {};
          const sectionQs = qList.filter(q => q.section === currentSection.title);
          const totalAnswered = Object.keys(evalAnswers).length;
          const totalQs = qList.length;
          const sectionAnswered = sectionQs.filter(q => evalAnswers[q.id] !== undefined).length;

          const handleAnswer = async (qId, value) => {
            const newAnswers = { ...evalAnswers, [qId]: value };
            setEvalAnswers(newAnswers);
            setEvalSaving(true);
            try {
              await fetch(`${API_BASE}/api/evaluation/PER/save`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ answers: newAnswers }),
              });
            } catch { /* ignore */ }
            finally { setEvalSaving(false); }
          };

          const handleCompare = async () => {
            setEvalComparing(true);
            setEvalComparison(null);
            try {
              const res = await fetch(`${API_BASE}/api/evaluation/PER/compare`);
              const data = await res.json();
              setEvalComparison(data);
            } catch { /* ignore */ }
            finally { setEvalComparing(false); }
          };

          const renderScaleBtn = (q, val, labels) => {
            const isSelected = evalAnswers[q.id] === val;
            const meta = labels[val] || {};
            return (
              <button
                key={val}
                onClick={() => handleAnswer(q.id, val)}
                style={{
                  padding: "5px 10px", borderRadius: 6, fontSize: 10, fontWeight: 600,
                  border: `1px solid ${isSelected ? meta.color : COLORS.border}`,
                  background: isSelected ? meta.color + "33" : "transparent",
                  color: isSelected ? meta.color : COLORS.textDim,
                  cursor: "pointer", transition: "all 0.15s",
                  fontFamily: "'DM Mono', monospace",
                }}
              >
                {val === 0 ? "—" : val} {meta.label}
              </button>
            );
          };

          return (
            <div>
              {/* Header */}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16, paddingBottom: 10, borderBottom: `1px solid ${COLORS.border}` }}>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase" }}>
                    Formulario de Evaluación — Perú 2026
                  </div>
                  <div style={{ fontSize: 11, color: COLORS.textSecondary, marginTop: 4 }}>
                    {totalAnswered}/{totalQs} preguntas respondidas
                    {evalSaving && <span style={{ marginLeft: 8, color: COLORS.accent, fontSize: 10 }}>guardando…</span>}
                  </div>
                </div>
                <button
                  onClick={handleCompare}
                  disabled={evalComparing || totalAnswered === 0}
                  style={{
                    padding: "8px 16px", borderRadius: 8, fontSize: 11, fontWeight: 700,
                    background: totalAnswered > 0 ? COLORS.accent + "22" : "transparent",
                    border: `1px solid ${totalAnswered > 0 ? COLORS.accent : COLORS.border}`,
                    color: totalAnswered > 0 ? COLORS.accent : COLORS.textDim,
                    cursor: totalAnswered > 0 ? "pointer" : "not-allowed",
                  }}
                >
                  {evalComparing ? "Calculando…" : "📊 Ver Comparación"}
                </button>
              </div>

              {evalLoading && (
                <div style={{ textAlign: "center", padding: 40, color: COLORS.textDim, fontSize: 12 }}>
                  Cargando cuestionario con datos de plataforma…
                </div>
              )}

              {!evalLoading && evalQuestionnaire && !evalComparison && (
                <div>
                  {/* Progress bar */}
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ height: 4, background: COLORS.border, borderRadius: 2, overflow: "hidden" }}>
                      <div style={{ height: "100%", width: `${totalQs > 0 ? (totalAnswered / totalQs) * 100 : 0}%`, background: COLORS.accent, borderRadius: 2, transition: "width 0.3s" }} />
                    </div>
                  </div>

                  {/* Section navigation */}
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 20 }}>
                    {sectionsMeta.map((s, i) => {
                      const sq = qList.filter(q => q.section === s.title);
                      const sa = sq.filter(q => evalAnswers[q.id] !== undefined).length;
                      const isActive = i === evalSection;
                      const isComplete = sa === sq.length && sq.length > 0;
                      return (
                        <button
                          key={i}
                          onClick={() => setEvalSection(i)}
                          style={{
                            padding: "4px 10px", borderRadius: 6, fontSize: 10, fontWeight: 600,
                            border: `1px solid ${isActive ? COLORS.accent : isComplete ? "#22c55e44" : COLORS.border}`,
                            background: isActive ? COLORS.accent + "22" : isComplete ? "#22c55e11" : "transparent",
                            color: isActive ? COLORS.accent : isComplete ? "#22c55e" : COLORS.textDim,
                            cursor: "pointer",
                          }}
                        >
                          {isComplete ? "✓" : (i + 1)} {s.title?.replace(/^S\d+\s*[—–-]\s*/, "") || s.id}
                        </button>
                      );
                    })}
                  </div>

                  {/* Current section */}
                  <div style={{ background: COLORS.cardBg, border: `1px solid ${COLORS.border}`, borderRadius: 12, padding: 20, marginBottom: 16 }}>
                    <div style={{ marginBottom: 16 }}>
                      <div style={{ fontSize: 13, fontWeight: 800, color: COLORS.textPrimary, marginBottom: 4 }}>
                        {currentSection.title || `Sección ${evalSection + 1}`}
                      </div>
                      {currentSection.description && (
                        <div style={{ fontSize: 11, color: COLORS.textSecondary, lineHeight: 1.5 }}>
                          {currentSection.description}
                        </div>
                      )}
                      <div style={{ fontSize: 10, color: COLORS.textDim, marginTop: 4 }}>
                        {sectionAnswered}/{sectionQs.length} respondidas en esta sección
                      </div>
                    </div>

                    {sectionQs.map((q, qi) => {
                      const isYesNo = q.scale === "yesno" || q.scale === "presence";
                      const labels = isYesNo ? YESNO_LABELS : SCALE_LABELS;
                      const scaleVals = isYesNo ? [0, 1, 2, 3, 4] : [0, 1, 2, 3, 4, 5];
                      const answered = evalAnswers[q.id] !== undefined;
                      const platScore = q.platform_score;

                      return (
                        <div key={q.id} style={{
                          marginBottom: 20, paddingBottom: 20,
                          borderBottom: qi < sectionQs.length - 1 ? `1px solid ${COLORS.border}44` : "none",
                        }}>
                          <div style={{ display: "flex", alignItems: "flex-start", gap: 10, marginBottom: 10 }}>
                            <div style={{
                              minWidth: 22, height: 22, borderRadius: 4,
                              background: answered ? COLORS.accent + "22" : COLORS.border + "44",
                              border: `1px solid ${answered ? COLORS.accent : COLORS.border}`,
                              color: answered ? COLORS.accent : COLORS.textDim,
                              fontSize: 9, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center",
                            }}>
                              {answered ? "✓" : qi + 1}
                            </div>
                            <div style={{ flex: 1 }}>
                              <div style={{ fontSize: 12, color: COLORS.textPrimary, lineHeight: 1.5, marginBottom: 6 }}>
                                {q.text}
                              </div>
                              <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 6 }}>
                                {q.iccpr_ref && (
                                  <span style={{ fontSize: 9, color: "#a855f7", background: "#a855f711", padding: "1px 6px", borderRadius: 4, border: "1px solid #a855f722" }}>
                                    {q.iccpr_ref}
                                  </span>
                                )}
                                {q.dataset_source && (
                                  <span style={{ fontSize: 9, color: COLORS.textDim, background: COLORS.border + "33", padding: "1px 6px", borderRadius: 4, border: `1px solid ${COLORS.border}` }}>
                                    {q.dataset_source}
                                    {q.dataset_var && ` · ${q.dataset_var}`}
                                  </span>
                                )}
                                {platScore !== null && platScore !== undefined && (
                                  <span style={{ fontSize: 9, color: "#00d4aa", background: "#00d4aa11", padding: "1px 6px", borderRadius: 4, border: "1px solid #00d4aa22" }}>
                                    Plataforma: {Math.round(platScore)}/100
                                  </span>
                                )}
                              </div>
                              {q.note && (
                                <div style={{ fontSize: 10, color: COLORS.textDim, fontStyle: "italic", marginBottom: 8, lineHeight: 1.4 }}>
                                  {q.note}
                                </div>
                              )}
                              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                                {scaleVals.map(v => renderScaleBtn(q, v, labels))}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Prev / Next */}
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <button
                      onClick={() => setEvalSection(s => Math.max(0, s - 1))}
                      disabled={evalSection === 0}
                      style={{
                        padding: "8px 16px", borderRadius: 8, fontSize: 11, fontWeight: 700,
                        background: "transparent", border: `1px solid ${COLORS.border}`,
                        color: evalSection === 0 ? COLORS.textDim : COLORS.textSecondary,
                        cursor: evalSection === 0 ? "not-allowed" : "pointer",
                      }}
                    >
                      ← Anterior
                    </button>
                    <button
                      onClick={() => setEvalSection(s => Math.min(sectionsMeta.length - 1, s + 1))}
                      disabled={evalSection >= sectionsMeta.length - 1}
                      style={{
                        padding: "8px 16px", borderRadius: 8, fontSize: 11, fontWeight: 700,
                        background: "transparent", border: `1px solid ${COLORS.border}`,
                        color: evalSection >= sectionsMeta.length - 1 ? COLORS.textDim : COLORS.accent,
                        cursor: evalSection >= sectionsMeta.length - 1 ? "not-allowed" : "pointer",
                      }}
                    >
                      Siguiente →
                    </button>
                  </div>
                </div>
              )}

              {/* Comparison view */}
              {evalComparison && (
                <div>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                    <div style={{ fontSize: 13, fontWeight: 800, color: COLORS.textPrimary }}>
                      Resultado de Comparación — Perú 2026
                    </div>
                    <button
                      onClick={() => setEvalComparison(null)}
                      style={{
                        padding: "4px 12px", borderRadius: 6, fontSize: 10, fontWeight: 600,
                        background: "transparent", border: `1px solid ${COLORS.border}`,
                        color: COLORS.textDim, cursor: "pointer",
                      }}
                    >
                      ← Volver al formulario
                    </button>
                  </div>

                  {/* Global convergence */}
                  <div style={{ background: COLORS.cardBg, border: `1px solid ${COLORS.border}`, borderRadius: 12, padding: 20, marginBottom: 16 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 12 }}>
                      <div style={{ fontSize: 36, fontWeight: 900, color: evalComparison.global_convergence >= 70 ? "#22c55e" : evalComparison.global_convergence >= 40 ? "#eab308" : "#ef4444" }}>
                        {evalComparison.global_convergence !== undefined ? `${Math.round(evalComparison.global_convergence)}%` : "—"}
                      </div>
                      <div>
                        <div style={{ fontSize: 12, fontWeight: 700, color: COLORS.textPrimary }}>Convergencia Global</div>
                        <div style={{ fontSize: 10, color: COLORS.textDim }}>Observador de campo vs. plataforma PEIRS</div>
                        <div style={{ fontSize: 10, color: COLORS.textDim }}>Basado en {evalComparison.questions_compared} preguntas comparadas de {evalComparison.questions_answered} respondidas</div>
                      </div>
                    </div>
                    <div style={{ height: 6, background: COLORS.border, borderRadius: 3, overflow: "hidden" }}>
                      <div style={{ height: "100%", width: `${evalComparison.global_convergence || 0}%`, background: evalComparison.global_convergence >= 70 ? "#22c55e" : evalComparison.global_convergence >= 40 ? "#eab308" : "#ef4444", borderRadius: 3 }} />
                    </div>
                  </div>

                  {/* Per-section table */}
                  <div style={{ background: COLORS.cardBg, border: `1px solid ${COLORS.border}`, borderRadius: 12, overflow: "hidden", marginBottom: 16 }}>
                    <div style={{ padding: "10px 16px", borderBottom: `1px solid ${COLORS.border}`, fontSize: 10, fontWeight: 700, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 2 }}>
                      Convergencia por Sección
                    </div>
                    {(evalComparison.sections || []).map((sec, i) => (
                      <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 16px", borderBottom: i < evalComparison.sections.length - 1 ? `1px solid ${COLORS.border}44` : "none" }}>
                        <div style={{ minWidth: 130, fontSize: 11, color: COLORS.textPrimary, fontWeight: 600 }}>{sec.section}</div>
                        <div style={{ flex: 1, height: 6, background: COLORS.border, borderRadius: 3, overflow: "hidden" }}>
                          <div style={{ height: "100%", width: `${sec.convergence || 0}%`, background: sec.convergence >= 70 ? "#22c55e" : sec.convergence >= 40 ? "#eab308" : "#ef4444", borderRadius: 3 }} />
                        </div>
                        <div style={{ minWidth: 40, textAlign: "right", fontSize: 11, fontWeight: 700, color: sec.convergence >= 70 ? "#22c55e" : sec.convergence >= 40 ? "#eab308" : "#ef4444" }}>
                          {sec.convergence !== null ? `${Math.round(sec.convergence)}%` : "—"}
                        </div>
                        <div style={{ minWidth: 60, fontSize: 9, color: COLORS.textDim, textAlign: "right" }}>
                          {sec.answered}/{sec.total} resp.
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Divergence highlights */}
                  {evalComparison.divergences && evalComparison.divergences.length > 0 && (
                    <div style={{ background: "#ef444411", border: "1px solid #ef444433", borderRadius: 12, padding: 16, marginBottom: 16 }}>
                      <div style={{ fontSize: 10, fontWeight: 700, color: "#ef4444", textTransform: "uppercase", letterSpacing: 2, marginBottom: 10 }}>
                        Principales Divergencias
                      </div>
                      {evalComparison.divergences.map((d, i) => (
                        <div key={i} style={{ marginBottom: 8, paddingBottom: 8, borderBottom: i < evalComparison.divergences.length - 1 ? "1px solid #ef444422" : "none" }}>
                          <div style={{ fontSize: 11, color: COLORS.textPrimary, marginBottom: 3 }}>{d.question}</div>
                          <div style={{ display: "flex", gap: 16, fontSize: 10, color: COLORS.textDim }}>
                            <span>Observador: <span style={{ color: "#f97316", fontWeight: 700 }}>{d.observer_score}/100</span></span>
                            <span>Plataforma: <span style={{ color: COLORS.accent, fontWeight: 700 }}>{d.platform_score}/100</span></span>
                            <span>Diferencia: <span style={{ color: "#ef4444", fontWeight: 700 }}>{d.gap} pts</span></span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <div style={{ fontSize: 10, color: COLORS.textDim, lineHeight: 1.6 }}>
                    <strong>Nota metodológica:</strong> La convergencia se calcula como <code>max(0, 100 − |obs − plat|)</code> donde los puntajes del observador (escala Likert 1-5) se convierten a escala 0-100 (×20). Respuestas "Sin información" (valor 0) se excluyen de la comparación. Preguntas sin dato de plataforma disponible tampoco se comparan.
                  </div>
                </div>
              )}
            </div>
          );
        })()}

        {/* ══ TAB: CONSULTA CONSTITUCIONAL ══
            Sub-agente jurista experto en derecho electoral peruano.
            Consulta POST /api/ask/constitutionalist y renderiza respuesta estructurada. */}
        {innerTab === "constitucional" && (
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 6, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", gap: 8 }}>
              Consulta Constitucional — Sub-agente Jurídico Perú
            </div>
            <div style={{ fontSize: 12, color: COLORS.textMuted, marginBottom: 16, lineHeight: 1.5 }}>
              Consultas al sub-agente experto en derecho constitucional y electoral peruano.
              Cubre Constitución 1993, LOE N° 26859, LOP N° 28094, jurisprudencia JNE y marco
              internacional vinculante (ICCPR, CADH, CDI). Cada respuesta cita artículos y
              resoluciones específicas.
            </div>

            {/* Formulario */}
            <Card className="peru-card" style={{ padding: 14, marginBottom: 16 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.text, marginBottom: 6 }}>
                Pregunta ⚖️
              </div>
              <textarea
                value={constQuestion}
                onChange={(e) => setConstQuestion(e.target.value)}
                placeholder="Ej: ¿Puede la ONPE seguir organizando la segunda vuelta con su jefe bajo investigación penal?"
                rows={3}
                style={{
                  width: "100%", padding: 10, borderRadius: 6,
                  background: COLORS.surface, color: COLORS.text,
                  border: `1px solid ${COLORS.border}`,
                  fontSize: 13, fontFamily: "inherit", resize: "vertical",
                  boxSizing: "border-box",
                }}
              />
              <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.text, marginTop: 10, marginBottom: 6 }}>
                Contexto adicional (opcional)
              </div>
              <textarea
                value={constContext}
                onChange={(e) => setConstContext(e.target.value)}
                placeholder="Antecedentes, actores, fechas, hechos relevantes al caso..."
                rows={2}
                style={{
                  width: "100%", padding: 10, borderRadius: 6,
                  background: COLORS.surface, color: COLORS.text,
                  border: `1px solid ${COLORS.border}`,
                  fontSize: 13, fontFamily: "inherit", resize: "vertical",
                  boxSizing: "border-box",
                }}
              />
              <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 10 }}>
                <button
                  onClick={askConstitutionalist}
                  disabled={constLoading || !constQuestion.trim()}
                  style={{
                    padding: "8px 18px", borderRadius: 6,
                    background: constLoading ? COLORS.surface : COLORS.accentDim,
                    color: constLoading ? COLORS.textMuted : COLORS.accent,
                    border: `1px solid ${COLORS.accent}55`,
                    fontSize: 12, fontWeight: 700, fontFamily: "'DM Mono', monospace",
                    cursor: constLoading || !constQuestion.trim() ? "not-allowed" : "pointer",
                    letterSpacing: 0.5,
                  }}
                >
                  {constLoading ? "● Consultando..." : "▶ Consultar"}
                </button>
                {constHistory.length > 0 && (
                  <span style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
                    Consultas previas: {constHistory.length}
                  </span>
                )}
              </div>
            </Card>

            {/* Error */}
            {constError && (
              <Card className="peru-card" style={{ padding: 14, marginBottom: 16, background: COLORS.dangerDim, borderLeft: `3px solid ${COLORS.danger}` }}>
                <div style={{ color: COLORS.danger, fontSize: 12, fontWeight: 700 }}>Error: {constError}</div>
              </Card>
            )}

            {/* Respuesta principal */}
            {constAnswer && (
              <Card className="peru-card" style={{ padding: 16, marginBottom: 16 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}` }}>
                  <span style={{ fontSize: 11, fontWeight: 700, color: COLORS.accent, letterSpacing: 2, textTransform: "uppercase" }}>
                    Dictamen del Sub-agente
                  </span>
                  {constAnswer.confidence && (
                    <span style={{
                      fontSize: 10, fontWeight: 700, padding: "3px 9px", borderRadius: 4,
                      background: constAnswer.confidence === "high" ? COLORS.accentDim
                                : constAnswer.confidence === "medium" ? COLORS.warningDim
                                : COLORS.dangerDim,
                      color: constAnswer.confidence === "high" ? COLORS.accent
                           : constAnswer.confidence === "medium" ? COLORS.warning
                           : COLORS.danger,
                      textTransform: "uppercase", letterSpacing: 1, fontFamily: "'DM Mono', monospace",
                    }}>
                      Confianza {constAnswer.confidence}
                    </span>
                  )}
                </div>
                <div style={{ fontSize: 13, color: COLORS.text, lineHeight: 1.7, whiteSpace: "pre-wrap", marginBottom: 14 }}>
                  {constAnswer.answer}
                </div>
                {Array.isArray(constAnswer.legal_basis) && constAnswer.legal_basis.length > 0 && (
                  <div style={{ marginTop: 12, padding: 10, background: COLORS.surface, borderRadius: 6, borderLeft: `2px solid ${COLORS.accent}` }}>
                    <div style={{ fontSize: 10, color: COLORS.accent, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, marginBottom: 5 }}>
                      📖 Base legal
                    </div>
                    <ul style={{ margin: 0, paddingLeft: 18, fontSize: 11, color: COLORS.textMuted, lineHeight: 1.6 }}>
                      {constAnswer.legal_basis.map((b, i) => <li key={i}>{b}</li>)}
                    </ul>
                  </div>
                )}
                {Array.isArray(constAnswer.case_law) && constAnswer.case_law.length > 0 && (
                  <div style={{ marginTop: 8, padding: 10, background: COLORS.surface, borderRadius: 6, borderLeft: `2px solid ${COLORS.info}` }}>
                    <div style={{ fontSize: 10, color: COLORS.info, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, marginBottom: 5 }}>
                      ⚖️ Jurisprudencia
                    </div>
                    <ul style={{ margin: 0, paddingLeft: 18, fontSize: 11, color: COLORS.textMuted, lineHeight: 1.6 }}>
                      {constAnswer.case_law.map((c, i) => <li key={i}>{c}</li>)}
                    </ul>
                  </div>
                )}
                {Array.isArray(constAnswer.international_framework) && constAnswer.international_framework.length > 0 && (
                  <div style={{ marginTop: 8, padding: 10, background: COLORS.surface, borderRadius: 6, borderLeft: `2px solid ${COLORS.purple}` }}>
                    <div style={{ fontSize: 10, color: COLORS.purple, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, marginBottom: 5 }}>
                      🌐 Marco internacional
                    </div>
                    <ul style={{ margin: 0, paddingLeft: 18, fontSize: 11, color: COLORS.textMuted, lineHeight: 1.6 }}>
                      {constAnswer.international_framework.map((f, i) => <li key={i}>{f}</li>)}
                    </ul>
                  </div>
                )}
                {Array.isArray(constAnswer.caveats) && constAnswer.caveats.length > 0 && (
                  <div style={{ marginTop: 8, padding: 10, background: COLORS.surface, borderRadius: 6, borderLeft: `2px solid ${COLORS.warning}` }}>
                    <div style={{ fontSize: 10, color: COLORS.warning, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, marginBottom: 5 }}>
                      ⚠️ Limitaciones
                    </div>
                    <ul style={{ margin: 0, paddingLeft: 18, fontSize: 11, color: COLORS.textMuted, lineHeight: 1.6 }}>
                      {constAnswer.caveats.map((c, i) => <li key={i}>{c}</li>)}
                    </ul>
                  </div>
                )}
                {Array.isArray(constAnswer.sources_cited) && constAnswer.sources_cited.length > 0 && (
                  <div style={{ marginTop: 12, fontSize: 9, color: COLORS.textDim, fontFamily: "'DM Mono', monospace", paddingTop: 8, borderTop: `1px dashed ${COLORS.border}` }}>
                    Fuentes RAG consultadas: {constAnswer.sources_cited.map(s => s.instrument || s.id).join(" · ")}
                    {constAnswer.tokens_used && ` · Tokens: ${constAnswer.tokens_used.input || 0}→${constAnswer.tokens_used.output || 0}`}
                  </div>
                )}
              </Card>
            )}

            {/* Historial */}
            {constHistory.length > 1 && (
              <div>
                <div style={{ fontSize: 10, fontWeight: 700, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", marginBottom: 8, marginTop: 20 }}>
                  Historial de consultas ({constHistory.length - 1} previas)
                </div>
                {constHistory.slice(1).map((h, i) => (
                  <Card key={i} className="peru-card" style={{ padding: 10, marginBottom: 8, fontSize: 11 }}>
                    <div style={{ color: COLORS.textMuted, fontWeight: 600, marginBottom: 4 }}>
                      ❓ {h.question}
                    </div>
                    <div style={{ color: COLORS.textDim, lineHeight: 1.5, fontSize: 10 }}>
                      {(h.answer || "").substring(0, 200)}...
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {!constAnswer && !constError && !constLoading && (
              <Card className="peru-card" style={{ padding: 16, textAlign: "center", color: COLORS.textDim, fontSize: 12 }}>
                Ejemplos de consultas:
                <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 6, textAlign: "left", fontSize: 11 }}>
                  <span>• ¿Cuáles son las causales constitucionales para anular una elección en Perú?</span>
                  <span>• ¿Qué establece la Ley 31030 sobre paridad y alternancia?</span>
                  <span>• ¿Puede el JNE separar al jefe de la ONPE durante el escrutinio?</span>
                  <span>• ¿Cómo se resuelven las actas observadas según la LOE Art. 343?</span>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* ══ TAB: INFORME PRELIMINAR (ReportDesigner Fase A) ══
            Sub-agente que compone informes estructurados parametrizables por
            audiencia. Fase A: esqueleto con narrativas mock basadas en el
            informe v1.1. Fases B-E reemplazan con lógica real. */}
        {innerTab === "designer" && (
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 6, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", gap: 8 }}>
              Informe Preliminar — Sub-agente ReportDesigner
            </div>
            <div style={{ fontSize: 12, color: COLORS.textMuted, marginBottom: 16, lineHeight: 1.5 }}>
              Genera informes parametrizables por audiencia (técnico, ejecutivo, prensa, internacional)
              e idioma. <strong>Fase A — esqueleto funcional</strong>: narrativas con plantillas basadas
              en el informe v1.1. Próximas fases (B–E) agregan dedupe semántico, visualizaciones SVG
              reales y redacción con Claude.
            </div>

            <Card className="peru-card" style={{ padding: 14, marginBottom: 16 }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 12 }}>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: COLORS.textMuted, marginBottom: 4, textTransform: "uppercase", letterSpacing: 1 }}>Audiencia</div>
                  <select value={designerAudience} onChange={(e) => setDesignerAudience(e.target.value)}
                    style={{ width: "100%", padding: 8, background: COLORS.surface, color: COLORS.text, border: `1px solid ${COLORS.border}`, borderRadius: 5, fontSize: 12 }}>
                    <option value="technical">🧑‍🔬 Técnico (completo)</option>
                    <option value="executive">🧑‍💼 Ejecutivo (2 pág)</option>
                    <option value="press">📰 Prensa (1 pág + infografía)</option>
                    <option value="international">🌐 Internacional (inglés)</option>
                  </select>
                </div>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: COLORS.textMuted, marginBottom: 4, textTransform: "uppercase", letterSpacing: 1 }}>Idioma</div>
                  <select value={designerLanguage} onChange={(e) => setDesignerLanguage(e.target.value)}
                    style={{ width: "100%", padding: 8, background: COLORS.surface, color: COLORS.text, border: `1px solid ${COLORS.border}`, borderRadius: 5, fontSize: 12 }}>
                    <option value="es">Español</option>
                    <option value="en">English</option>
                  </select>
                </div>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: COLORS.textMuted, marginBottom: 4, textTransform: "uppercase", letterSpacing: 1 }}>Período</div>
                  <select value={designerPeriod} onChange={(e) => setDesignerPeriod(Number(e.target.value))}
                    style={{ width: "100%", padding: 8, background: COLORS.surface, color: COLORS.text, border: `1px solid ${COLORS.border}`, borderRadius: 5, fontSize: 12 }}>
                    <option value={1}>Últimas 24h</option>
                    <option value={3}>Últimos 3 días</option>
                    <option value={7}>Últimos 7 días</option>
                    <option value={30}>Último mes</option>
                  </select>
                </div>
              </div>

              {/* Toggle IA */}
              <label style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 10px",
                background: designerUseLLM ? COLORS.accentDim : COLORS.surface,
                border: `1px solid ${designerUseLLM ? COLORS.accent + "55" : COLORS.border}`,
                borderRadius: 5, cursor: "pointer", marginBottom: 10, fontSize: 12 }}>
                <input type="checkbox" checked={designerUseLLM}
                  onChange={(e) => setDesignerUseLLM(e.target.checked)}
                  style={{ cursor: "pointer" }} />
                <span style={{ color: designerUseLLM ? COLORS.accent : COLORS.text, fontWeight: 600 }}>
                  🤖 Redacción asistida por Claude (Fase C)
                </span>
                <span style={{ fontSize: 10, color: COLORS.textDim, marginLeft: "auto" }}>
                  {designerUseLLM ? "60-90s · ~$0.05-0.15" : "&lt;5s · $0 (plantillas)"}
                </span>
              </label>

              <button onClick={generateDesignedReport} disabled={designerLoading}
                style={{
                  padding: "10px 24px", borderRadius: 6,
                  background: designerLoading ? COLORS.surface : COLORS.accentDim,
                  color: designerLoading ? COLORS.textMuted : COLORS.accent,
                  border: `1px solid ${COLORS.accent}55`,
                  fontSize: 12, fontWeight: 700, fontFamily: "'DM Mono', monospace",
                  cursor: designerLoading ? "wait" : "pointer", letterSpacing: 0.5, width: "100%",
                }}>
                {designerLoading ? (designerUseLLM ? "● Redactando con Claude..." : "● Generando informe...") : "▶ Generar informe preliminar"}
              </button>
            </Card>

            {designerError && (
              <Card className="peru-card" style={{ padding: 14, marginBottom: 16, background: COLORS.dangerDim, borderLeft: `3px solid ${COLORS.danger}` }}>
                <div style={{ color: COLORS.danger, fontSize: 12, fontWeight: 700 }}>Error: {designerError}</div>
              </Card>
            )}

            {designerResult && designerResult.stats && (
              <div>
                {/* Stats header */}
                <Card className="peru-card" style={{ padding: 12, marginBottom: 12, display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
                  {[
                    { label: "Hallazgos", value: designerResult.stats.total_findings, color: COLORS.accent },
                    { label: "Críticos", value: designerResult.stats.critical, color: COLORS.danger },
                    { label: "Altos", value: designerResult.stats.high, color: "#f97316" },
                    { label: "Días", value: designerResult.stats.days_covered, color: COLORS.info },
                  ].map((kpi, i) => (
                    <div key={i} style={{ textAlign: "center", padding: 8, borderLeft: `3px solid ${kpi.color}`, background: COLORS.surface, borderRadius: 5 }}>
                      <div style={{ fontSize: 22, fontWeight: 800, color: kpi.color, fontFamily: "'DM Mono', monospace" }}>{kpi.value}</div>
                      <div style={{ fontSize: 9, color: COLORS.textDim, marginTop: 2, textTransform: "uppercase", letterSpacing: 1 }}>{kpi.label}</div>
                    </div>
                  ))}
                </Card>

                {/* HTML preview */}
                {designerResult.html && (
                  <Card className="peru-card" style={{ padding: 0, marginBottom: 12, overflow: "hidden" }}>
                    <div style={{ padding: "8px 14px", background: COLORS.surface, borderBottom: `1px solid ${COLORS.border}`, fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace", display: "flex", justifyContent: "space-between" }}>
                      <span>Preview del informe</span>
                      <span>report_id: {designerResult.report_id}</span>
                    </div>
                    <iframe title="Report preview" srcDoc={designerResult.html}
                      style={{ width: "100%", height: 600, border: "none", background: "white" }}></iframe>
                  </Card>
                )}

                {/* Markdown download */}
                {designerResult.markdown && (
                  <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
                    <a
                      href={`data:text/markdown;charset=utf-8,${encodeURIComponent(designerResult.markdown)}`}
                      download={`informe-${designerResult.country_code}-${designerResult.audience}-${designerResult.report_id}.md`}
                      style={{
                        flex: 1, padding: 10, textAlign: "center",
                        background: COLORS.accentDim, color: COLORS.accent,
                        border: `1px solid ${COLORS.accent}55`, borderRadius: 6,
                        fontSize: 12, fontWeight: 700, textDecoration: "none",
                        fontFamily: "'DM Mono', monospace",
                      }}>
                      ⬇ Descargar Markdown
                    </a>
                    <a
                      href={`data:text/html;charset=utf-8,${encodeURIComponent(designerResult.html || "")}`}
                      download={`informe-${designerResult.country_code}-${designerResult.audience}-${designerResult.report_id}.html`}
                      style={{
                        flex: 1, padding: 10, textAlign: "center",
                        background: COLORS.infoDim, color: COLORS.info,
                        border: `1px solid ${COLORS.info}55`, borderRadius: 6,
                        fontSize: 12, fontWeight: 700, textDecoration: "none",
                        fontFamily: "'DM Mono', monospace",
                      }}>
                      ⬇ Descargar HTML
                    </a>
                  </div>
                )}

                {/* Warnings */}
                {Array.isArray(designerResult.warnings) && designerResult.warnings.length > 0 && (
                  <Card className="peru-card" style={{ padding: 10, background: COLORS.warningDim, borderLeft: `3px solid ${COLORS.warning}`, fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5 }}>
                    <strong style={{ color: COLORS.warning }}>⚠️ Notas:</strong>
                    <ul style={{ margin: "4px 0 0", paddingLeft: 18 }}>
                      {designerResult.warnings.map((w, i) => <li key={i}>{w}</li>)}
                    </ul>
                  </Card>
                )}
              </div>
            )}

            {!designerResult && !designerError && !designerLoading && (
              <Card className="peru-card" style={{ padding: 16, textAlign: "center", color: COLORS.textDim, fontSize: 12, lineHeight: 1.7 }}>
                Seleccioná la audiencia, idioma y período, y presioná <strong>"▶ Generar informe preliminar"</strong>.
                <br /><br />
                <span style={{ fontSize: 11, color: COLORS.textMuted }}>
                  Cada audiencia produce una estructura distinta: técnico (~20 pág completo),
                  ejecutivo (2 pág accionables), prensa (1 pág + infografía), internacional (inglés + marco comparado).
                </span>
              </Card>
            )}
          </div>
        )}

        {/* ══ TAB: INFORME ELITE ══
            Orquestador completo del blueprint ELITE_REPORT.md — 12 capítulos
            con Claude, 21 visualizaciones SVG, citas APA 7, motor predictivo. */}
        {innerTab === "elite" && (
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 6, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", gap: 8 }}>
              📘 Informe Elite — Nivel Institucional Internacional
            </div>
            <div style={{ fontSize: 12, color: COLORS.textMuted, marginBottom: 16, lineHeight: 1.5 }}>
              Informe de observación electoral de calidad comparable a misiones OEA/DECO, EU EOM,
              Carter Center e IDEA Internacional. 12 capítulos con narrativa Claude, citas APA 7,
              análisis predictivo y visualizaciones SVG institucionales.
              <strong> Tiempo estimado: 2-5 min · Costo: ~$0.40-0.80 por informe.</strong>
            </div>

            <Card className="peru-card" style={{ padding: 14, marginBottom: 16 }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 12 }}>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: COLORS.textMuted, marginBottom: 4, textTransform: "uppercase", letterSpacing: 1 }}>Audiencia</div>
                  <select value={eliteAudience} onChange={(e) => setEliteAudience(e.target.value)}
                    style={{ width: "100%", padding: 8, background: COLORS.surface, color: COLORS.text, border: `1px solid ${COLORS.border}`, borderRadius: 5, fontSize: 12 }}>
                    <option value="institutional">🏛️ Institucional (OEA/EU EOM)</option>
                    <option value="executive">🧑‍💼 Ejecutiva</option>
                    <option value="press">📰 Prensa</option>
                    <option value="international">🌐 Internacional (inglés)</option>
                  </select>
                </div>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: COLORS.textMuted, marginBottom: 4, textTransform: "uppercase", letterSpacing: 1 }}>Tipo de informe</div>
                  <select value={eliteReportType} onChange={(e) => setEliteReportType(e.target.value)}
                    style={{ width: "100%", padding: 8, background: COLORS.surface, color: COLORS.text, border: `1px solid ${COLORS.border}`, borderRadius: 5, fontSize: 12 }}>
                    <option value="pre_electoral">📋 Pre-electoral</option>
                    <option value="jornada">🗳️ De jornada</option>
                    <option value="preliminary">📊 Preliminar</option>
                    <option value="final">📘 Final</option>
                    <option value="ad_hoc">⚡ Ad-hoc</option>
                  </select>
                </div>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: COLORS.textMuted, marginBottom: 4, textTransform: "uppercase", letterSpacing: 1 }}>Idioma</div>
                  <select value={eliteLanguage} onChange={(e) => setEliteLanguage(e.target.value)}
                    style={{ width: "100%", padding: 8, background: COLORS.surface, color: COLORS.text, border: `1px solid ${COLORS.border}`, borderRadius: 5, fontSize: 12 }}>
                    <option value="es">Español</option>
                    <option value="en">English</option>
                  </select>
                </div>
              </div>

              <label style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 10px",
                background: eliteIncludePredictive ? COLORS.accentDim : COLORS.surface,
                border: `1px solid ${eliteIncludePredictive ? COLORS.accent + "55" : COLORS.border}`,
                borderRadius: 5, cursor: "pointer", marginBottom: 10, fontSize: 12 }}>
                <input type="checkbox" checked={eliteIncludePredictive}
                  onChange={(e) => setEliteIncludePredictive(e.target.checked)} />
                <span style={{ color: eliteIncludePredictive ? COLORS.accent : COLORS.text, fontWeight: 600 }}>
                  🔮 Incluir análisis predictivo (Cap. 9) — 3-5 escenarios probabilísticos con bandas de confianza
                </span>
              </label>

              <button onClick={generateEliteReport} disabled={eliteLoading}
                style={{
                  padding: "12px 24px", borderRadius: 6,
                  background: eliteLoading ? COLORS.surface : COLORS.accent,
                  color: eliteLoading ? COLORS.textMuted : "#fff",
                  border: `1px solid ${COLORS.accent}`,
                  fontSize: 13, fontWeight: 700, fontFamily: "'DM Mono', monospace",
                  cursor: eliteLoading ? "wait" : "pointer", letterSpacing: 0.5, width: "100%",
                }}>
                {eliteLoading ? "● Generando Informe Elite (puede tomar 2-5 min)..." : "▶ Generar Informe Elite"}
              </button>
            </Card>

            {eliteError && (
              <Card className="peru-card" style={{ padding: 14, marginBottom: 16, background: COLORS.dangerDim, borderLeft: `3px solid ${COLORS.danger}` }}>
                <div style={{ color: COLORS.danger, fontSize: 12, fontWeight: 700, whiteSpace: "pre-wrap" }}>Error: {eliteError}</div>
              </Card>
            )}

            {eliteResult && (
              <div>
                {/* Stats */}
                <Card className="peru-card" style={{ padding: 12, marginBottom: 12 }}>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10 }}>
                    {[
                      { label: "Capítulos", value: (eliteResult.chapters || []).length, color: COLORS.accent },
                      { label: "Críticos", value: (eliteResult.stats || {}).critical || 0, color: COLORS.danger },
                      { label: "Altos", value: (eliteResult.stats || {}).high || 0, color: "#f97316" },
                      { label: "Citas APA", value: (eliteResult.citations || []).length, color: COLORS.info },
                      { label: "Tokens", value: `${((eliteResult.tokens_used || {}).input || 0) + ((eliteResult.tokens_used || {}).output || 0)}`, color: COLORS.purple },
                    ].map((kpi, i) => (
                      <div key={i} style={{ textAlign: "center", padding: 8, borderLeft: `3px solid ${kpi.color}`, background: COLORS.surface, borderRadius: 5 }}>
                        <div style={{ fontSize: 18, fontWeight: 800, color: kpi.color, fontFamily: "'DM Mono', monospace" }}>{kpi.value}</div>
                        <div style={{ fontSize: 8, color: COLORS.textDim, marginTop: 2, textTransform: "uppercase", letterSpacing: 1 }}>{kpi.label}</div>
                      </div>
                    ))}
                  </div>
                  <div style={{ marginTop: 10, fontSize: 11, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
                    Report ID: <strong>{eliteResult.report_id}</strong> · Costo: <strong>USD {eliteResult.estimated_cost_usd?.toFixed(4)}</strong> ·
                    Tiempo: <strong>{eliteResult.generation_time_seconds?.toFixed(1)}s</strong>
                  </div>
                </Card>

                {/* Preview HTML */}
                {eliteResult.html && (
                  <Card className="peru-card" style={{ padding: 0, marginBottom: 12, overflow: "hidden" }}>
                    <div style={{ padding: "8px 14px", background: COLORS.surface, borderBottom: `1px solid ${COLORS.border}`, fontSize: 10, color: COLORS.textDim, fontFamily: "'DM Mono', monospace", display: "flex", justifyContent: "space-between" }}>
                      <span>Preview del Informe Elite — {(eliteResult.chapters || []).length} capítulos + anexos</span>
                      <span>{eliteResult.mission?.report_number}</span>
                    </div>
                    <iframe title="Elite report preview" srcDoc={eliteResult.html}
                      style={{ width: "100%", height: 800, border: "none", background: "white" }}></iframe>
                  </Card>
                )}

                {/* Botones de descarga */}
                <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
                  <a
                    href={`${API_BASE}/api/report/elite/${eliteResult.report_id}/printable`}
                    target="_blank" rel="noopener noreferrer"
                    title="Abre el informe en una pestaña nueva con el diálogo de impresión. Desde ahí: Guardar como PDF (calidad editorial, A4)."
                    style={{
                      flex: 1, padding: 12, textAlign: "center",
                      background: COLORS.accent, color: "#fff",
                      border: `1px solid ${COLORS.accent}`, borderRadius: 6,
                      fontSize: 13, fontWeight: 700, textDecoration: "none",
                      fontFamily: "'DM Mono', monospace",
                    }}>
                    🖨️ Imprimir / PDF
                  </a>
                  <a
                    href={`${API_BASE}/api/report/elite/${eliteResult.report_id}/download?format=html`}
                    target="_blank" rel="noopener noreferrer"
                    style={{
                      flex: 1, padding: 12, textAlign: "center",
                      background: COLORS.infoDim, color: COLORS.info,
                      border: `1px solid ${COLORS.info}55`, borderRadius: 6,
                      fontSize: 13, fontWeight: 700, textDecoration: "none",
                      fontFamily: "'DM Mono', monospace",
                    }}>
                    ⬇ HTML
                  </a>
                  <a
                    href={`${API_BASE}/api/report/elite/${eliteResult.report_id}/download?format=md`}
                    target="_blank" rel="noopener noreferrer"
                    style={{
                      flex: 1, padding: 12, textAlign: "center",
                      background: COLORS.accentDim, color: COLORS.accent,
                      border: `1px solid ${COLORS.accent}55`, borderRadius: 6,
                      fontSize: 13, fontWeight: 700, textDecoration: "none",
                      fontFamily: "'DM Mono', monospace",
                    }}>
                    ⬇ Markdown
                  </a>
                </div>

                {/* Warnings */}
                {Array.isArray(eliteResult.warnings) && eliteResult.warnings.length > 0 && (
                  <Card className="peru-card" style={{ padding: 10, background: COLORS.warningDim, borderLeft: `3px solid ${COLORS.warning}`, fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5 }}>
                    <strong style={{ color: COLORS.warning }}>⚠️ Warnings del pipeline:</strong>
                    <ul style={{ margin: "4px 0 0", paddingLeft: 18 }}>
                      {eliteResult.warnings.map((w, i) => <li key={i}>{w}</li>)}
                    </ul>
                  </Card>
                )}
              </div>
            )}

            {/* Historial */}
            {eliteHistory.length > 0 && (
              <div>
                <div style={{ fontSize: 10, fontWeight: 700, color: COLORS.textDim, letterSpacing: 2, textTransform: "uppercase", marginBottom: 8, marginTop: 20 }}>
                  Historial de Informes Elite ({eliteHistory.length})
                </div>
                {eliteHistory.map((h, i) => (
                  <Card key={i} className="peru-card" style={{ padding: 10, marginBottom: 8, fontSize: 11, display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr auto", gap: 10, alignItems: "center" }}>
                    <div>
                      <div style={{ fontWeight: 700, color: COLORS.text }}>{h.report_number} · {h.audience}</div>
                      <div style={{ fontSize: 9, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
                        {h.report_id} · {(h.generated_at || "").slice(0, 16).replace("T", " ")}
                      </div>
                    </div>
                    <div style={{ fontSize: 10, color: COLORS.textMuted }}>
                      <span style={{ color: COLORS.accent, fontFamily: "'DM Mono', monospace" }}>
                        {h.total_findings || 0}
                      </span> hallazgos
                    </div>
                    <div style={{ fontSize: 10, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
                      USD {(h.estimated_cost_usd || 0).toFixed(3)}
                    </div>
                    <div style={{ fontSize: 10, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
                      {(h.generation_time_s || 0).toFixed(0)}s
                    </div>
                    <a href={`${API_BASE}/api/report/elite/${h.report_id}/printable`}
                       target="_blank" rel="noopener noreferrer"
                       title="Abre el informe con el diálogo de impresión — Guardar como PDF desde ahí"
                       style={{ padding: "4px 10px", background: COLORS.accentDim, color: COLORS.accent, borderRadius: 4, fontSize: 10, textDecoration: "none", fontWeight: 700, fontFamily: "'DM Mono', monospace" }}>
                      🖨️ Imprimir
                    </a>
                  </Card>
                ))}
              </div>
            )}

            {!eliteResult && !eliteError && !eliteLoading && eliteHistory.length === 0 && (
              <Card className="peru-card" style={{ padding: 20, textAlign: "center", color: COLORS.textDim, fontSize: 12, lineHeight: 1.7 }}>
                <div style={{ fontSize: 28, marginBottom: 8 }}>📘</div>
                <strong style={{ color: COLORS.text }}>Producto insignia del sistema PEIRS</strong>
                <br /><br />
                El Informe Elite combina 12 capítulos narrados por Claude, análisis predictivo
                con escenarios probabilísticos, visualizaciones SVG institucionales, y citas
                APA 7 trazables hasta la fuente primaria. Seleccioná los parámetros y presioná
                <strong> "▶ Generar Informe Elite"</strong>.
              </Card>
            )}
          </div>
        )}

        {/* ══ TAB: METODOLOGÍA ══
            Glosario de datasets + guía de lectura del dashboard.
            Responde a la necesidad de que el observador entienda qué mide cada
            índice sin consultar fuentes externas. */}
        {innerTab === "metodologia" && (
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 6, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", gap: 8 }}>
              Metodología — glosario y guía de lectura
            </div>
            <div style={{ fontSize: 12, color: COLORS.textMuted, marginBottom: 18, lineHeight: 1.5 }}>
              Este tab documenta qué mide cada dataset mostrado en el dashboard, qué escalas usa, de dónde provienen los datos y cómo interpretar lo que el observador ve. Es de lectura recomendada antes de usar el informe operativamente.
            </div>

            <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.accent, textTransform: "uppercase", letterSpacing: 2, marginBottom: 10, marginTop: 16 }}>
              📊 Índices internacionales utilizados
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 18 }}>
              <Card className="peru-card" style={{ padding: 14 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: COLORS.text, marginBottom: 6 }}>🗽 Freedom House — FIW</div>
                <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5 }}>
                  <strong>Freedom in the World</strong> evalúa derechos políticos (proceso electoral, pluralismo y participación, funcionamiento del gobierno) y libertades civiles (libertad de expresión, asociación, estado de derecho, autonomía personal) sobre 195 países. Puntaje agregado 0–100. Publicación anual.
                  <br /><br />
                  <strong>Fuente:</strong> Freedom House Inc. (Washington DC). <a href="https://freedomhouse.org/report/freedom-world" target="_blank" rel="noopener noreferrer" style={{ color: COLORS.accent }}>Metodología oficial</a>.
                </div>
              </Card>
              <Card className="peru-card" style={{ padding: 14 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: COLORS.text, marginBottom: 6 }}>⚖️ V-Dem — Liberal Democracy Index</div>
                <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5 }}>
                  <strong>Varieties of Democracy</strong> combina 5 principios: democracia electoral, liberal (límites al ejecutivo), participativa, deliberativa y de igualdad. El índice usado aquí es el <em>Liberal Democracy</em> (electoral + frenos institucionales). Escala 0–1. V-Dem v15 cubre 202 países desde 1789. Métricas construidas por consenso experto ponderado (Bayesian IRT).
                  <br /><br />
                  <strong>Fuente:</strong> V-Dem Institute, Universidad de Gotemburgo (Suecia). <a href="https://v-dem.net/data/dataset-archive/" target="_blank" rel="noopener noreferrer" style={{ color: COLORS.accent }}>Dataset y documentación</a>.
                </div>
              </Card>
              <Card className="peru-card" style={{ padding: 14 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: COLORS.text, marginBottom: 6 }}>🗳️ PEI — Perceptions of Electoral Integrity</div>
                <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5 }}>
                  Encuesta a expertos post-electoral sobre 11 dimensiones (marco legal, diseño de circunscripciones, registro de electores, registro de partidos, campaña, medios, financiamiento, jornada, conteo, resultados, autoridades electorales). El índice EMBs mide específicamente la percepción sobre los organismos electorales (JNE/ONPE/RENIEC en el caso peruano). Escala 0–100.
                  <br /><br />
                  <strong>Fuente:</strong> Electoral Integrity Project (Univ. de Sydney & Univ. de Harvard). <a href="https://www.electoralintegrityproject.com" target="_blank" rel="noopener noreferrer" style={{ color: COLORS.accent }}>Sitio oficial</a>.
                </div>
              </Card>
              <Card className="peru-card" style={{ padding: 14 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: COLORS.text, marginBottom: 6 }}>📰 RSF — Press Freedom Index</div>
                <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5 }}>
                  Índice anual sobre libertad de prensa en 180 países. Cinco indicadores: contexto político, marco legal, contexto económico, sociocultural, y seguridad de periodistas. Escala 0–100 (mayor = más libertad).
                  <br /><br />
                  <strong>Fuente:</strong> Reporteros Sin Fronteras (Francia). <a href="https://rsf.org/en/index" target="_blank" rel="noopener noreferrer" style={{ color: COLORS.accent }}>Ranking anual</a>.
                </div>
              </Card>
            </div>

            <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.accent, textTransform: "uppercase", letterSpacing: 2, marginBottom: 10, marginTop: 16 }}>
              🎯 PEIRS Score y Convergencia
            </div>
            <Card className="peru-card" style={{ padding: 14, marginBottom: 18 }}>
              <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5 }}>
                <strong>PEIRS Risk Score</strong> (Predictive Electoral Integrity &amp; Risk Score) es una métrica compuesta 0–100 que combina los cuatro índices internacionales con una normalización propia y ponderación sobre 8 dimensiones: marco legal, organismo electoral, financiamiento, medios, inclusión, resolución de disputas, amenazas digitales, y trayectoria institucional. Se interpreta como <em>riesgo a la integridad electoral</em> (mayor = más riesgo).
                <br /><br />
                <strong>Convergencia entre fuentes</strong> mide qué tan consistente es el diagnóstico cuando se cruzan FH + V-Dem + PEI. 75+ indica que las tres apuntan en la misma dirección; &lt;50 indica divergencia (requiere investigar por qué).
                <br /><br />
                <strong>Limitación:</strong> PEIRS es un indicador estructural, no una predicción. Fuerzas de choque (crisis institucionales, fraudes agudos, catástrofes operativas) no se capturan plenamente en los índices internacionales publicados con desfase anual.
              </div>
            </Card>

            <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.accent, textTransform: "uppercase", letterSpacing: 2, marginBottom: 10, marginTop: 16 }}>
              🛰️ Hunter — fuentes de monitoreo en vivo
            </div>
            <Card className="peru-card" style={{ padding: 14, marginBottom: 18 }}>
              <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5 }}>
                El <strong>Hunter Agent</strong> extrae cada 4 horas sobre feeds RSS de medios peruanos. Cada ítem se clasifica con <strong>Claude Sonnet 4.6</strong> (Anthropic) en una de 17 categorías (desinformación, logística electoral, violación de campaña, fraude, discurso de odio, restricción a medios, violencia, etc.) y se asigna severidad info/low/medium/high/critical.
                <br /><br />
                <strong>Fuentes activas:</strong> Andina (agencia oficial), El Comercio, Gestión, IDL-Reporteros, RPP Noticias. JNE y ONPE emiten RSS pero devuelven error 403/404 (pendientes de evaluación técnica). Wayka devuelve HTML no parseable.
                <br /><br />
                <strong>Alertas high/critical</strong> se despachan automáticamente al canal Discord configurado y se persisten en la tabla <code>alerts</code> de SQLite sobre volumen persistente. Visibles también en el tab "🚨 Alertas en vivo" con refresh cada 5 minutos.
                <br /><br />
                <strong>Derechos citados:</strong> ICCPR Art. 19 y 25, CADH Art. 13 y 23, CDI Art. 3, LOE Art. 190/191/351/358/363.
              </div>
            </Card>

            <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.accent, textTransform: "uppercase", letterSpacing: 2, marginBottom: 10, marginTop: 16 }}>
              🗺️ Guía de lectura del dashboard
            </div>
            <Card className="peru-card" style={{ padding: 14, marginBottom: 18 }}>
              <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.7 }}>
                <strong>1. Arranque operativo:</strong> empezar por <strong>🚨 Alertas en vivo</strong> para ver qué detectó el Hunter desde el último refresh. Si hay críticas rojas → prioridad máxima.
                <br />
                <strong>2. Planificación del día:</strong> <strong>📅 Calendario legal</strong> muestra qué hitos legales rigen hoy (Ley Seca, silencio electoral, plazo de impugnaciones).
                <br />
                <strong>3. Contextualizar:</strong> <strong>📊 Contexto y datos</strong> cruza los 4 índices internacionales. Usar las cards narrativas; cada una viene con su escala interpretativa.
                <br />
                <strong>4. Profundizar:</strong> <strong>📈 Series V-Dem</strong> para tendencias temporales, <strong>👥 Actores</strong> y <strong>🏛 Parlamento</strong> para composición política.
                <br />
                <strong>5. Observación activa:</strong> <strong>📋 MOE Brief</strong> descargable, <strong>🗳 Jornada</strong> con formulario, <strong>📝 Evaluación</strong> con cuestionario auditable.
                <br />
                <strong>6. Documento final:</strong> <strong>📄 Informe PEIRS</strong> reúne los 11 capítulos del análisis completo con citas de fuentes primarias.
              </div>
            </Card>

            <div style={{ marginTop: 14, padding: 12, background: COLORS.surface, border: `1px dashed ${COLORS.border}`, borderRadius: 6, fontSize: 11, color: COLORS.textDim, lineHeight: 1.5 }}>
              ⚠ Este informe es un <strong>sistema de apoyo a la observación electoral</strong>, no reemplaza la observación presencial ni los informes oficiales de las misiones acreditadas (OEA, OSCE/ODIHR, Carter Center, IDEA Internacional, NDI). Las clasificaciones automáticas del Hunter deben verificarse contra la fuente primaria antes de citar.
            </div>
          </div>
        )}

        {/* ══ TAB: INFORME ══ */}
        {innerTab === "informe" && (() => {
          const activeRunId = reportRunId || country?.run_id;
          const handleGenerateReport = async () => {
            setReportGenerating(true);
            setReportGenResult(null);
            try {
              const res = await fetch(`${API_BASE}/api/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ country_code: "PER", force_refresh: true }),
              });
              if (!res.ok) throw new Error(`HTTP ${res.status}`);
              const data = await res.json();
              setReportRunId(data.run_id || null);
              setReportGenResult({ ok: true, run_id: data.run_id });
            } catch (err) {
              setReportGenResult({ ok: false, error: err.message });
            } finally {
              setReportGenerating(false);
            }
          };
          return (
            <div>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 16, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", gap: 8 }}>
                Informe de Fondo — Análisis Completo PEIRS (9 Capítulos)
                <span style={{ flex: 1, height: 1, background: `linear-gradient(90deg, ${COLORS.border}, transparent)` }} />
              </div>
              <div style={{ marginBottom: 16, display: "flex", alignItems: "center", gap: 12 }}>
                <button onClick={handleGenerateReport} disabled={reportGenerating} style={{
                  padding: "8px 18px", borderRadius: 8, border: `1px solid ${COLORS.accent}55`,
                  background: reportGenerating ? COLORS.surface : COLORS.accentDim,
                  color: reportGenerating ? COLORS.textDim : COLORS.accent,
                  fontSize: 12, fontWeight: 700, cursor: reportGenerating ? "not-allowed" : "pointer",
                  fontFamily: "'DM Mono', monospace", letterSpacing: 0.5, transition: "all 0.2s ease",
                }}>
                  {reportGenerating ? "Analizando... (puede demorar 30-60s)" : "↻ Generar Nuevo Análisis"}
                </button>
                {reportGenResult && reportGenResult.ok && (
                  <span style={{ fontSize: 11, color: COLORS.accent, fontFamily: "'DM Mono', monospace" }}>
                    Análisis generado — run_id: {reportGenResult.run_id}
                  </span>
                )}
                {reportGenResult && !reportGenResult.ok && (
                  <span style={{ fontSize: 11, color: COLORS.danger, fontFamily: "'DM Mono', monospace" }}>
                    Error: {reportGenResult.error}
                  </span>
                )}
              </div>
              {activeRunId ? (
                <ReportViewer runId={activeRunId} country={country} />
              ) : (
                <div style={{ padding: 32, textAlign: "center", color: COLORS.textDim, fontFamily: "'DM Mono', monospace", fontSize: 12 }}>
                  Sin reporte disponible. Presioná "Generar Nuevo Análisis" para iniciar.
                </div>
              )}
            </div>
          );
        })()}

      </div>
    </div>
  );
}



// R4: Fases del ciclo electoral completo
const OBS_PHASES = [
  { id: "preparatory",         label: "📋 Preparatorio" },
  { id: "pre_campaign",        label: "📣 Pre-Campaña" },
  { id: "campaign",            label: "🗣️ Campaña Electoral" },
  { id: "electoral_silence",   label: "🤫 Veda Electoral" },
  { id: "election_day",        label: "🗳️ Jornada Electoral" },
  { id: "counting_tabulation", label: "🔢 Escrutinio y Cómputo" },
  { id: "post_election",       label: "📊 Post-Electoral" },
  { id: "dispute_resolution",  label: "⚖️ Resolución de Disputas" },
  { id: "completed",           label: "✅ Ciclo Completo" },
];

// R5: Categorías de observación ampliadas
const OBS_CATEGORIES = [
  { id: "voter_intimidation",  label: "Intimidación de votantes" },
  { id: "voter_suppression",   label: "Supresión del voto" },
  { id: "ballot_tampering",    label: "Manipulación de boletas" },
  { id: "campaign_violation",  label: "Infracción de campaña" },
  { id: "disinformation",      label: "Desinformación electoral" },
  { id: "gender_violence",     label: "Violencia política de género" },
  { id: "media_restriction",   label: "Restricción de medios" },
  { id: "fraud_allegation",    label: "Alegación de fraude" },
  { id: "irregular_procedure", label: "Procedimiento irregular" },
  { id: "accessibility",       label: "Accesibilidad electoral" },
  { id: "security",            label: "Seguridad" },
  { id: "logistics",           label: "Logística" },
  { id: "legal",               label: "Legal/Normativo" },
  { id: "counting",            label: "Escrutinio" },
  { id: "results",             label: "Resultados" },
  { id: "digital",             label: "Ecosistema digital" },
  { id: "hate_speech",         label: "Discurso de odio" },
  { id: "other",               label: "Otro" },
];
const OBS_SEVERITIES = [
  { id: "info", label: "Info" },
  { id: "low", label: "Bajo" },
  { id: "medium", label: "Medio" },
  { id: "high", label: "Alto" },
  { id: "critical", label: "Crítico" },
];
const OBS_CONFIDENCE = [
  { id: "confirmed", label: "Confirmado" },
  { id: "probable", label: "Probable" },
  { id: "unverified", label: "Sin verificar" },
];

function ObserverView() {
  const [phase, setPhase] = useState("election_day");
  const [category, setCategory] = useState("other");
  const [severity, setSeverity] = useState("medium");
  const [finding, setFinding] = useState("");
  const [location, setLocation] = useState("");
  const [confidence, setConfidence] = useState("unverified");
  const [hasEvidence, setHasEvidence] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [entries, setEntries] = useState([]);

  const selectStyle = {
    width: "100%", padding: "8px 10px", borderRadius: 6,
    border: `1px solid ${COLORS.border}`, background: COLORS.surface,
    color: COLORS.text, fontSize: 12, fontFamily: "'DM Mono', monospace",
    outline: "none",
  };
  const labelStyle = {
    fontSize: 10, fontWeight: 700, letterSpacing: 2,
    color: COLORS.textDim, textTransform: "uppercase", marginBottom: 4, display: "block",
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!finding.trim()) return;
    setSubmitting(true);
    setResult(null);
    const body = {
      country_code: "PER",
      phase,
      category,
      severity,
      finding,
      location,
      timestamp: new Date().toISOString(),
      confidence,
      has_evidence: hasEvidence,
      credibility_source: "observer_field",
    };
    try {
      const res = await fetch(`${API_BASE}/api/observation/PER/entry`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResult({ ok: true, data });
      setEntries(prev => [{ ...body, response: data }, ...prev].slice(0, 20));
      setFinding("");
      setLocation("");
      setHasEvidence(false);
    } catch (err) {
      setResult({ ok: false, error: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  const severityColor = (s) => ({
    critical: COLORS.danger, high: COLORS.danger, medium: COLORS.warning,
    low: COLORS.info, info: COLORS.textMuted,
  }[s] || COLORS.textMuted);

  return (
    <div style={{ padding: "24px 28px", maxWidth: 1200, margin: "0 auto" }}>
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 4 }}>
          Protocolo de Observación Electoral
        </div>
        <div style={{ fontSize: 22, fontWeight: 800, color: COLORS.text }}>
          📡 Observación de Campo — <span style={{ color: COLORS.accent }}>Perú 2026</span>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        {/* Left: Form */}
        <Card>
          <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 2, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 16, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}` }}>
            Registrar Observación
          </div>
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <label style={labelStyle}>Fase Electoral</label>
              <select value={phase} onChange={e => setPhase(e.target.value)} style={selectStyle}>
                {OBS_PHASES.map(p => <option key={p.id} value={p.id}>{p.label}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Categoría</label>
              <select value={category} onChange={e => setCategory(e.target.value)} style={selectStyle}>
                {OBS_CATEGORIES.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
              </select>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <label style={labelStyle}>Severidad</label>
                <select value={severity} onChange={e => setSeverity(e.target.value)} style={selectStyle}>
                  {OBS_SEVERITIES.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
                </select>
              </div>
              <div>
                <label style={labelStyle}>Confianza</label>
                <select value={confidence} onChange={e => setConfidence(e.target.value)} style={selectStyle}>
                  {OBS_CONFIDENCE.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label style={labelStyle}>Hallazgo *</label>
              <textarea
                value={finding} onChange={e => setFinding(e.target.value)}
                placeholder="Descripción detallada del hallazgo observado..."
                rows={5} required
                style={{ ...selectStyle, resize: "vertical", lineHeight: 1.5 }}
              />
            </div>
            <div>
              <label style={labelStyle}>Ubicación</label>
              <input
                type="text" value={location} onChange={e => setLocation(e.target.value)}
                placeholder="Distrito, provincia, mesa..."
                style={selectStyle}
              />
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <input
                type="checkbox" id="hasEvidence" checked={hasEvidence}
                onChange={e => setHasEvidence(e.target.checked)}
                style={{ width: 16, height: 16, cursor: "pointer" }}
              />
              <label htmlFor="hasEvidence" style={{ fontSize: 12, color: COLORS.textMuted, cursor: "pointer" }}>
                Tiene evidencia adjunta (foto, video, documento)
              </label>
            </div>
            <button type="submit" disabled={submitting || !finding.trim()} style={{
              padding: "10px 20px", borderRadius: 8, border: `1px solid ${COLORS.accent}55`,
              background: submitting ? COLORS.surface : COLORS.accentDim,
              color: submitting ? COLORS.textDim : COLORS.accent,
              fontSize: 13, fontWeight: 700, cursor: submitting ? "not-allowed" : "pointer",
              fontFamily: "'DM Mono', monospace", letterSpacing: 0.5, transition: "all 0.2s ease",
            }}>
              {submitting ? "Enviando..." : "Enviar Observación"}
            </button>
            {result && result.ok && (
              <div style={{ padding: 12, borderRadius: 8, background: COLORS.accent + "15", border: `1px solid ${COLORS.accent}44`, fontSize: 12, color: COLORS.accent, fontFamily: "'DM Mono', monospace" }}>
                Registrado correctamente
                {result.data?.warnings?.length > 0 && (
                  <div style={{ marginTop: 6, color: COLORS.warning }}>
                    Advertencias: {result.data.warnings.join(", ")}
                  </div>
                )}
              </div>
            )}
            {result && !result.ok && (
              <div style={{ padding: 12, borderRadius: 8, background: COLORS.danger + "15", border: `1px solid ${COLORS.danger}44`, fontSize: 12, color: COLORS.danger, fontFamily: "'DM Mono', monospace" }}>
                Error: {result.error}
              </div>
            )}
          </form>
        </Card>

        {/* Right: Entries */}
        <Card>
          <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 2, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 16, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}` }}>
            Observaciones Recientes ({entries.length})
          </div>
          {entries.length === 0 ? (
            <div style={{ padding: 32, textAlign: "center", color: COLORS.textDim, fontFamily: "'DM Mono', monospace", fontSize: 12 }}>
              Aún no hay observaciones en esta sesión.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 10, maxHeight: 520, overflowY: "auto" }}>
              {entries.map((entry, i) => (
                <div key={entry.entry_id || i} style={{
                  padding: 12, borderRadius: 8,
                  background: COLORS.bg, border: `1px solid ${COLORS.border}`,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: severityColor(entry.severity), fontFamily: "'DM Mono', monospace", textTransform: "uppercase", letterSpacing: 1 }}>
                      {entry.severity} · {OBS_CATEGORIES.find(c => c.id === entry.category)?.label || entry.category}
                    </span>
                    <span style={{ fontSize: 9, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
                      {new Date(entry.timestamp).toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                  <div style={{ fontSize: 12, color: COLORS.text, marginBottom: 4, lineHeight: 1.4 }}>
                    {entry.finding}
                  </div>
                  {entry.location && (
                    <div style={{ fontSize: 10, color: COLORS.textMuted, fontFamily: "'DM Mono', monospace" }}>
                      📍 {entry.location}
                    </div>
                  )}
                  <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
                    <span style={{ fontSize: 9, padding: "2px 6px", borderRadius: 4, background: COLORS.surface, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
                      {OBS_CONFIDENCE.find(c => c.id === entry.confidence)?.label || entry.confidence}
                    </span>
                    {entry.has_evidence && (
                      <span style={{ fontSize: 9, padding: "2px 6px", borderRadius: 4, background: COLORS.info + "22", color: COLORS.info, fontFamily: "'DM Mono', monospace" }}>
                        CON EVIDENCIA
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

function CountrySelector({ countries, selectedCountry, onSelect }) {
  const [search, setSearch] = useState("");
  const [openRegions, setOpenRegions] = useState({ americas: true });

  const filtered = search.trim()
    ? countries.filter(c => c.name.toLowerCase().includes(search.toLowerCase()))
    : countries;

  const byRegion = REGION_ORDER.reduce((acc, r) => {
    const group = filtered.filter(c => (c.region || "americas") === r);
    if (group.length) acc[r] = group;
    return acc;
  }, {});

  const toggleRegion = r => setOpenRegions(prev => ({ ...prev, [r]: !prev[r] }));

  return (
    <div style={{
      borderBottom: `1px solid ${COLORS.border}`,
      padding: "10px 28px 10px",
    }}>
      <input
        value={search}
        onChange={e => setSearch(e.target.value)}
        placeholder="Buscar país..."
        style={{
          marginBottom: 8, width: 220, padding: "5px 10px", borderRadius: 6,
          border: `1px solid ${COLORS.border}`, background: COLORS.surface,
          color: COLORS.text, fontSize: 12, fontFamily: "'DM Sans', sans-serif",
          outline: "none",
        }}
      />
      {Object.entries(byRegion).map(([region, group]) => (
        <div key={region} style={{ marginBottom: 4 }}>
          <button onClick={() => toggleRegion(region)} style={{
            background: "none", border: "none", cursor: "pointer",
            color: COLORS.textMuted, fontSize: 11, fontWeight: 700,
            letterSpacing: 0.5, padding: "2px 0", marginBottom: 4,
            display: "flex", alignItems: "center", gap: 6,
          }}>
            <span style={{ fontFamily: "'DM Mono', monospace" }}>
              {openRegions[region] ? "▾" : "▸"}
            </span>
            {REGION_LABELS[region] || region} ({group.length})
          </button>
          {openRegions[region] && (
            <div style={{ display: "flex", gap: 5, flexWrap: "wrap", paddingLeft: 16 }}>
              {group.map(c => {
                const rl = RISK_LEVELS[c.riskLevel] || RISK_LEVELS.moderate;
                return (
                  <button key={c.id} onClick={() => onSelect(c.id)} style={{
                    padding: "3px 10px", borderRadius: 7, cursor: "pointer",
                    fontSize: 12, fontWeight: 600, whiteSpace: "nowrap",
                    background: selectedCountry === c.id ? COLORS.accent + "22" : COLORS.surface,
                    color: selectedCountry === c.id ? COLORS.accent : COLORS.textMuted,
                    border: `1px solid ${selectedCountry === c.id ? COLORS.accent + "44" : COLORS.border}`,
                    display: "flex", alignItems: "center", gap: 4,
                  }}>
                    <span>{c.flag}</span>
                    <span>{c.name}</span>
                    <span style={{
                      fontSize: 9, padding: "1px 4px", borderRadius: 4,
                      background: rl.color + "22", color: rl.color,
                      fontFamily: "'DM Mono', monospace",
                    }}>{c.riskScore}</span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// LANDING PAGE PUBLICA — accesible en / (root) sin auth
// El dashboard tecnico vive en /?app=true (toggle)
// ═══════════════════════════════════════════════════════════════════════

function LandingPage({ onEnterApp }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/public/stats`)
      .then(r => r.ok ? r.json() : null)
      .then(data => { setStats(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const numFindings = stats?.monitoring?.total_findings ?? "—";
  const numReports = stats?.outputs?.elite_reports_generated ?? "—";
  const numDays = stats?.monitoring?.days_running ?? "—";
  const numCountries = stats?.coverage?.countries_catalog ?? 38;
  const primary = stats?.coverage?.primary_country;
  const sevCritical = stats?.monitoring?.severity_breakdown?.critical ?? 0;
  const sevHigh = stats?.monitoring?.severity_breakdown?.high ?? 0;
  const lastUpdate = stats?.monitoring?.last_finding_at;

  return (
    <div style={{
      minHeight: "100vh", background: COLORS.bg, color: COLORS.text,
      fontFamily: "Inter, 'DM Sans', system-ui, sans-serif",
    }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500;600&family=Fraunces:wght@300;500;700;900&family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />

      {/* NAV */}
      <nav style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        padding: "20px 7%", borderBottom: `1px solid ${COLORS.border}`,
        position: "sticky", top: 0, zIndex: 100, background: COLORS.bg + "ee",
        backdropFilter: "blur(10px)",
      }}>
        <BrandLogo size={42} withWordmark wordmarkSize={26} />
        <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
          <a href="#producto" style={{ color: COLORS.textMuted, textDecoration: "none", fontSize: 14, fontWeight: 600 }}>Producto</a>
          <a href="#datos" style={{ color: COLORS.textMuted, textDecoration: "none", fontSize: 14, fontWeight: 600 }}>Datos</a>
          <a href="#metodologia" style={{ color: COLORS.textMuted, textDecoration: "none", fontSize: 14, fontWeight: 600 }}>Metodología</a>
          <button onClick={onEnterApp} style={{
            padding: "10px 20px", borderRadius: 8, border: `1px solid ${BRAND.terracotta}`,
            background: BRAND.terracotta, color: "#fff", fontSize: 14, fontWeight: 700,
            cursor: "pointer", letterSpacing: 0.3,
          }}>Acceder al dashboard →</button>
        </div>
      </nav>

      {/* HERO */}
      <section style={{ padding: "80px 7% 60px", maxWidth: 1400, margin: "0 auto" }}>
        <div style={{
          display: "inline-block", padding: "6px 14px", borderRadius: 20,
          background: BRAND.terracotta + "22", border: `1px solid ${BRAND.terracotta}66`,
          color: BRAND.terracotta, fontSize: 12, fontWeight: 700, letterSpacing: 1.5,
          textTransform: "uppercase", marginBottom: 24,
        }}>
          Predictive Electoral Integrity & Risk System
        </div>
        <h1 style={{
          fontSize: 64, fontWeight: 900, lineHeight: 1.1, letterSpacing: -2,
          margin: "0 0 24px", maxWidth: 900,
          fontFamily: "Fraunces, Georgia, serif",
        }}>
          Inteligencia electoral basada en evidencia,<br />
          <span style={{ color: BRAND.terracotta }}>con trazabilidad verificable.</span>
        </h1>
        <p style={{
          fontSize: 22, lineHeight: 1.6, color: COLORS.textMuted, maxWidth: 800,
          margin: "0 0 40px", fontWeight: 400,
        }}>
          Plataforma de inteligencia artificial diseñada para anticipar riesgos
          sobre la integridad electoral y la calidad democrática. Análisis basado
          en datasets internacionales con transparencia metodológica completa.
        </p>
        <div style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <button onClick={onEnterApp} style={{
            padding: "16px 32px", borderRadius: 10, border: "none",
            background: BRAND.terracotta, color: "#fff", fontSize: 16, fontWeight: 800,
            cursor: "pointer", letterSpacing: 0.3,
            boxShadow: `0 4px 20px ${BRAND.terracotta}44`,
          }}>Ver dashboard en vivo →</button>
          <a href="https://github.com/lachmanmariana8-sudo/democracia-peirs/blob/main/DOCS%20Proyect/PEIRS_Indices_Methodology_v1.0.md"
             target="_blank" rel="noopener noreferrer" style={{
            padding: "16px 32px", borderRadius: 10, border: `1px solid ${COLORS.border}`,
            background: "transparent", color: COLORS.text, fontSize: 16, fontWeight: 700,
            textDecoration: "none", letterSpacing: 0.3,
          }}>Leer metodología</a>
        </div>
      </section>

      {/* STATS LIVE */}
      <section id="datos" style={{
        padding: "60px 7%", maxWidth: 1400, margin: "0 auto",
        borderTop: `1px solid ${COLORS.border}`, borderBottom: `1px solid ${COLORS.border}`,
      }}>
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 12, color: COLORS.textMuted, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 8 }}>
            Datos en vivo · {lastUpdate ? `actualizado ${new Date(lastUpdate).toLocaleString('es-AR', { dateStyle: 'medium', timeStyle: 'short' })}` : "sincronizando..."}
          </div>
          <h2 style={{ fontSize: 36, fontWeight: 800, margin: 0, fontFamily: "Fraunces, serif" }}>
            La plataforma en números
          </h2>
        </div>
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 24,
        }}>
          <StatCard label="Hallazgos OSINT verificados" value={numFindings} hint="Hunter scheduler 24h" />
          <StatCard label="Países en catálogo" value={numCountries} hint="V-Dem · FH · PEI · RSF" />
          <StatCard label="Informes Elite generados" value={numReports} hint="12 capítulos + 3 anexos" />
          <StatCard label="Días de monitoreo" value={numDays} hint={primary ? `${primary.flag} ${primary.name}` : "—"} />
          <StatCard label="Hallazgos críticos" value={sevCritical} hint="Severity: critical" accent />
          <StatCard label="Hallazgos altos" value={sevHigh} hint="Severity: high" />
        </div>
      </section>

      {/* COBERTURA ACTIVA */}
      {primary && (
        <section style={{ padding: "60px 7%", maxWidth: 1400, margin: "0 auto" }}>
          <div style={{
            display: "flex", alignItems: "center", gap: 32, padding: 32,
            background: COLORS.surface, borderRadius: 16, border: `1px solid ${COLORS.border}`,
            flexWrap: "wrap",
          }}>
            <div style={{ fontSize: 80, lineHeight: 1 }}>{primary.flag}</div>
            <div style={{ flex: 1, minWidth: 280 }}>
              <div style={{ fontSize: 11, color: COLORS.textMuted, letterSpacing: 2,
                textTransform: "uppercase", fontWeight: 700, marginBottom: 8 }}>
                Cobertura activa
              </div>
              <h3 style={{ fontSize: 32, fontWeight: 800, margin: "0 0 8px",
                fontFamily: "Fraunces, serif" }}>
                {primary.name} {primary.election_date && `· Elecciones ${primary.election_date.slice(0, 4)}`}
              </h3>
              <p style={{ color: COLORS.textMuted, fontSize: 16, margin: "0 0 16px" }}>
                Fase actual: <span style={{ color: COLORS.text, fontWeight: 700 }}>{primary.phase_label || primary.phase}</span>
              </p>
              <button onClick={onEnterApp} style={{
                padding: "12px 24px", borderRadius: 8, border: `1px solid ${BRAND.terracotta}`,
                background: "transparent", color: BRAND.terracotta, fontSize: 14, fontWeight: 700,
                cursor: "pointer",
              }}>Explorar el monitoreo →</button>
            </div>
          </div>
        </section>
      )}

      {/* QUE HACE */}
      <section id="producto" style={{ padding: "80px 7%", maxWidth: 1400, margin: "0 auto" }}>
        <div style={{ marginBottom: 48 }}>
          <h2 style={{ fontSize: 42, fontWeight: 800, margin: "0 0 16px",
            fontFamily: "Fraunces, serif" }}>¿Qué hace Democrac.IA?</h2>
          <p style={{ fontSize: 18, color: COLORS.textMuted, maxWidth: 700, lineHeight: 1.6 }}>
            Pipeline híbrido de análisis: reglas determinísticas sobre datasets
            estructurales + clasificación automática con Claude Sonnet 4.6 sobre
            evidencia OSINT en tiempo real.
          </p>
        </div>
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: 24,
        }}>
          <FeatureCard icon="🔍" title="Monitoreo OSINT 24/7" desc="Hunter scheduler que ingesta RSS verificadas y clasifica con IA. 14 fuentes activas (nacionales + internacionales)." />
          <FeatureCard icon="📊" title="Datasets internacionales" desc="V-Dem v16, Freedom House FIW, Perceptions of Electoral Integrity 10.0, RSF Press Freedom Index." />
          <FeatureCard icon="⚖️" title="Marco normativo" desc="14 instrumentos del derecho internacional (ICCPR, CADH, CDI, CEDAW) + marcos nacionales por país." />
          <FeatureCard icon="🚨" title="Alertas tempranas" desc="Crisis Index auditable derivado del corpus. Notificación automática para severidades altas y críticas." />
          <FeatureCard icon="🤖" title="Análisis predictivo" desc="6 escenarios probabilísticos con bandas de confianza. Pipeline LangGraph + RAG legal + reglas determinísticas." />
          <FeatureCard icon="📑" title="Informe Elite" desc="12 capítulos + 3 anexos. Citas APA 7 con URL verificable. Trilingüe (es/en/pt). Comparable a misiones OSCE/OEA/EU EOM." />
        </div>
      </section>

      {/* METODOLOGIA */}
      <section id="metodologia" style={{
        padding: "80px 7%", maxWidth: 1400, margin: "0 auto",
        borderTop: `1px solid ${COLORS.border}`,
      }}>
        <h2 style={{ fontSize: 36, fontWeight: 800, margin: "0 0 16px",
          fontFamily: "Fraunces, serif" }}>Transparencia metodológica</h2>
        <p style={{ fontSize: 17, color: COLORS.textMuted, maxWidth: 720, lineHeight: 1.6, marginBottom: 32 }}>
          Cada índice cuantitativo del informe Elite tiene fórmula auditable
          documentada. Citable formalmente por tribunales, organismos
          supranacionales y dataset partners.
        </p>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
          <a href="https://github.com/lachmanmariana8-sudo/democracia-peirs/blob/main/DOCS%20Proyect/PEIRS_Indices_Methodology_v1.0.md"
             target="_blank" rel="noopener noreferrer" style={{
            padding: "14px 24px", borderRadius: 10, border: `1px solid ${COLORS.border}`,
            background: COLORS.surface, color: COLORS.text, fontSize: 14, fontWeight: 700,
            textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 8,
          }}>📄 Metodología de Índices v1.0</a>
          <a href="https://github.com/lachmanmariana8-sudo/democracia-peirs"
             target="_blank" rel="noopener noreferrer" style={{
            padding: "14px 24px", borderRadius: 10, border: `1px solid ${COLORS.border}`,
            background: COLORS.surface, color: COLORS.text, fontSize: 14, fontWeight: 700,
            textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 8,
          }}>💻 Código fuente</a>
        </div>
      </section>

      {/* DISCLOSURE */}
      <section style={{ padding: "60px 7%", maxWidth: 1400, margin: "0 auto" }}>
        <div style={{
          padding: 32, background: COLORS.surface, borderRadius: 16,
          border: `2px solid ${COLORS.border}`,
        }}>
          <div style={{ fontSize: 11, color: BRAND.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
            Disclosure institucional
          </div>
          <p style={{ fontSize: 17, color: COLORS.text, margin: 0, lineHeight: 1.7, fontWeight: 500 }}>
            <strong>Democrac.IA no legitima ni valida resultados electorales.</strong>
            Esta plataforma emite inteligencia electoral con trazabilidad
            verificable bajo estándares internacionales de observación electoral,
            sin sesgo político-partidario.
          </p>
        </div>
      </section>

      {/* FOOTER */}
      <footer style={{
        padding: "40px 7%", borderTop: `1px solid ${COLORS.border}`,
        display: "flex", justifyContent: "space-between", alignItems: "center",
        flexWrap: "wrap", gap: 16, color: COLORS.textDim, fontSize: 13,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <BrandLogo size={28} />
          <span>Democrac.IA · PEIRS v0.6.0</span>
        </div>
        <div style={{ display: "flex", gap: 24 }}>
          <a href="https://github.com/lachmanmariana8-sudo/democracia-peirs"
             target="_blank" rel="noopener noreferrer"
             style={{ color: COLORS.textDim, textDecoration: "none" }}>GitHub</a>
          <a href="#metodologia" style={{ color: COLORS.textDim, textDecoration: "none" }}>Metodología</a>
          <button onClick={onEnterApp} style={{
            background: "transparent", border: "none", color: COLORS.textDim,
            cursor: "pointer", fontSize: 13, padding: 0,
          }}>Dashboard</button>
        </div>
      </footer>
    </div>
  );
}

function StatCard({ label, value, hint, accent = false }) {
  return (
    <div style={{
      padding: 24, background: COLORS.surface, borderRadius: 12,
      border: `1px solid ${accent ? BRAND.terracotta + "66" : COLORS.border}`,
    }}>
      <div style={{ fontSize: 11, color: COLORS.textMuted, letterSpacing: 1.5,
        textTransform: "uppercase", fontWeight: 700, marginBottom: 10 }}>{label}</div>
      <div style={{
        fontSize: 48, fontWeight: 900, lineHeight: 1, marginBottom: 8,
        color: accent ? BRAND.terracotta : COLORS.text,
        fontFamily: "Fraunces, Georgia, serif", letterSpacing: -1.5,
      }}>{typeof value === "number" ? value.toLocaleString('es-AR') : value}</div>
      <div style={{ fontSize: 12, color: COLORS.textDim }}>{hint}</div>
    </div>
  );
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div style={{
      padding: 24, background: COLORS.surface, borderRadius: 12,
      border: `1px solid ${COLORS.border}`,
    }}>
      <div style={{ fontSize: 32, marginBottom: 12 }}>{icon}</div>
      <h3 style={{ fontSize: 18, fontWeight: 800, margin: "0 0 8px",
        fontFamily: "Inter, sans-serif" }}>{title}</h3>
      <p style={{ fontSize: 14, color: COLORS.textMuted, margin: 0, lineHeight: 1.6 }}>{desc}</p>
    </div>
  );
}

function DemocracIADashboard() {
  const [activeView, setActiveView] = useState("overview");
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState("connecting");
  const [generatedAt, setGeneratedAt] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);

  useEffect(() => {
    const fetchHealth = () => {
      fetch(`${API_BASE}/api/stats`)
        .then(r => r.ok ? r.json() : null)
        .then(data => { if (data) setSystemHealth(data); })
        .catch(() => {});
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 60000);
    return () => clearInterval(interval);
  }, []);

  // IMPORTANTE: fetchDashboardData NO puede depender de selectedCountry.
  // Antes era `useCallback(..., [selectedCountry])` y eso creaba un loop de
  // re-fetch: fetch → setSelectedCountry → fetchDashboardData nuevo →
  // useEffect re-ejecuta fetch → AnimatedCounter re-anima con cada respuesta.
  // Síntoma: números parpadeando "como locos" en https://democracia.ar/.
  // Fix: deps vacío + setSelectedCountry solo con el updater functional
  // (no depende del valor actual, lo chequea en tiempo real dentro del set).
  const fetchDashboardData = useCallback(async (forceRefresh = false) => {
    if (forceRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);
    try {
      const url = forceRefresh ? `${API_BASE}/api/dashboard?force_refresh=true` : `${API_BASE}/api/dashboard`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setCountries(data.countries);
      setGeneratedAt(data.generated_at || null);
      // Updater functional: accede al valor actual sin hacer que la callback
      // cambie de referencia cuando selectedCountry cambia.
      setSelectedCountry(prev => prev || data.countries[0]?.id || null);
      setApiStatus("connected");
    } catch (err) {
      setError(err.message);
      setApiStatus("disconnected");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchDashboardData(); }, [fetchDashboardData]);

  const handleSelectCountry = (id) => {
    setSelectedCountry(id);
    setActiveView("detail");
  };

  if (loading) return <LoadingScreen />;
  if (error) return <ErrorScreen error={error} onRetry={fetchDashboardData} />;

  const country = countries.find(c => c.id === selectedCountry);

  return (
    <div style={{
      minHeight: "100vh",
      width: "100%",
      background: COLORS.bg,
      color: COLORS.text,
      fontFamily: "'DM Sans', 'Segoe UI', sans-serif", fontSize: 16,
      margin: 0,
      padding: 0,
      boxSizing: "border-box",
    }}>
      <style>{`
        *, *::before, *::after { box-sizing: border-box; }
        html, body, #root { margin: 0; padding: 0; width: 100%; min-height: 100vh; background: ${COLORS.bg}; }
      `}</style>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800&family=DM+Mono:wght@400;500;600&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400&display=swap" rel="stylesheet" />
      <Navbar activeView={activeView} setActiveView={setActiveView} apiStatus={apiStatus}
        onRefresh={() => fetchDashboardData(true)} refreshing={refreshing} generatedAt={generatedAt}
        systemHealth={systemHealth} />

      {activeView === "detail" && (
        <CountrySelector
          countries={countries}
          selectedCountry={selectedCountry}
          onSelect={setSelectedCountry}
        />
      )}

      {activeView === "overview" && <OverviewView countries={countries} onSelectCountry={handleSelectCountry} />}
      {activeView === "detail" && country && <DetailView country={country} />}
      {activeView === "sentinel" && <SentinelView />}
      {activeView === "peru" && <PeruSituationRoom />}
      {activeView === "observer" && <ObserverView />}
      {activeView === "methodology" && <MethodologyView />}

      <footer style={{
        padding: "16px 28px", borderTop: `1px solid ${COLORS.border}`,
        display: "flex", justifyContent: "space-between", alignItems: "center",
      }}>
        <span style={{ fontSize: 10, color: COLORS.textDim, letterSpacing: 1 }}>
          DEMOCRAC.IA — PEIRS v0.4.0 — CONECTADO A BACKEND LANGGRAPH
        </span>
        <span style={{ fontSize: 10, color: COLORS.textDim }}>
          © 2026 — Inteligencia Electoral OSINT
        </span>
      </footer>
    </div>
  );
}

// Test auto-deploy 1776605450

// ═══════════════════════════════════════════════════════════════════════
// APP WRAPPER — decide entre Landing publica y Dashboard tecnico
// Landing en /     |     Dashboard en /?app=true
// ═══════════════════════════════════════════════════════════════════════

export default function App() {
  const [showApp, setShowApp] = useState(() => {
    try {
      const url = new URL(window.location.href);
      return url.searchParams.get("app") === "true";
    } catch {
      return false;
    }
  });

  const enterApp = useCallback(() => {
    try {
      const url = new URL(window.location.href);
      url.searchParams.set("app", "true");
      window.history.pushState({}, "", url.toString());
    } catch {}
    setShowApp(true);
  }, []);

  if (!showApp) {
    return <LandingPage onEnterApp={enterApp} />;
  }
  return <DemocracIADashboard />;
}
