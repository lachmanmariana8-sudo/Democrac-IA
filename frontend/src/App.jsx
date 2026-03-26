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

import React, { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, LineChart, Line, CartesianGrid, Legend, Cell, PieChart, Pie } from "recharts";

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
};

const RISK_LEVELS = {
  critical: { color: COLORS.danger, label: "CRÍTICO", bg: COLORS.dangerDim },
  high: { color: "#f97316", label: "ALTO", bg: "#f9731633" },
  moderate: { color: COLORS.warning, label: "MODERADO", bg: COLORS.warningDim },
  low: { color: COLORS.accent, label: "BAJO", bg: COLORS.accentDim },
};

const API_BASE = "http://localhost:8000";

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
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let frame;
    const start = performance.now();
    const animate = (now) => {
      const p = Math.min((now - start) / 900, 1);
      setDisplay(Math.round((1 - Math.pow(1 - p, 3)) * value));
      if (p < 1) frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [value]);
  return <span>{display}{suffix}</span>;
};

const LoadingScreen = () => (
  <div style={{
    minHeight: "100vh", background: COLORS.bg, display: "flex",
    flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 24,
  }}>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800&family=DM+Mono:wght@400;500;600&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,400&display=swap" rel="stylesheet" />
    <div style={{
      width: 56, height: 56, borderRadius: 12,
      background: `linear-gradient(135deg, ${COLORS.accent}, ${COLORS.info})`,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: 28, fontWeight: 900, color: COLORS.bg,
      animation: "pulse 2s ease-in-out infinite",
    }}>D</div>
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: 18, fontWeight: 700, color: COLORS.text, fontFamily: "'DM Mono', monospace" }}>
        Democrac<span style={{ color: COLORS.accent }}>.IA</span>
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

const Navbar = ({ activeView, setActiveView, apiStatus, onRefresh, refreshing, generatedAt }) => (
  <nav style={{
    display: "flex", alignItems: "center", justifyContent: "space-between",
    padding: "14px 28px",
    background: "linear-gradient(180deg, #0d1220 0%, #0a0e17 100%)",
    borderBottom: `1px solid ${COLORS.border}`,
    position: "sticky", top: 0, zIndex: 100,
  }}>
    <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
      <div style={{
        width: 36, height: 36, borderRadius: 8,
        background: `linear-gradient(135deg, ${COLORS.accent}, ${COLORS.info})`,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 18, fontWeight: 900, color: COLORS.bg,
      }}>D</div>
      <div>
        <span style={{ fontSize: 22, fontWeight: 800, color: COLORS.text, letterSpacing: 1, fontFamily: "'DM Mono', monospace" }}>
          Democrac<span style={{ color: COLORS.accent }}>.IA</span>
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
            width: 56, height: 56, borderRadius: 12, flexShrink: 0,
            background: `linear-gradient(135deg, ${COLORS.accent}, ${COLORS.info})`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 28, fontWeight: 900, color: COLORS.bg,
          }}>D</div>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 14 }}>
              <h1 style={{ margin: 0, fontSize: 30, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
                <strong style={{ color: "#ffffff", fontWeight: 900 }}>Democrac</strong>
                <strong style={{ color: "#f59e0b", fontWeight: 900 }}>.IA</strong>
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
  const [anim, setAnim] = useState(0);
  useEffect(() => {
    let frame;
    const start = performance.now();
    const animate = (now) => {
      const p = Math.min((now - start) / 1100, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setAnim(eased * (value || 0));
      if (p < 1) frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [value]);

  const r = size / 2 - 10;
  const circ = 2 * Math.PI * r;
  const pct = max > 0 ? anim / max : 0;
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
            {value !== null && value !== undefined ? (Number.isInteger(value) ? Math.round(anim) : anim.toFixed(2)) : "N/A"}
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
  return (
    <span style={{ position: "relative", display: "inline-block" }}
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
    </span>
  );
};

const InfoIcon = ({ tooltip }) => (
  <TooltipInfo text={tooltip}>
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
const generateHtmlReport = (markdown, country, runId, timestamp, reportData) => {
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

  // ── Capítulos en HTML ─────────────────────────────────────────────────────
  const chapOrder = [
    "01_executive_summary","02_political_context","03_emb_analysis",
    "04_inclusivity","05_campaign_finance","06_digital_ecosystem",
    "07_voting_day","08_electoral_justice","09_recommendations","10_ai_regulation",
  ];
  const chapHtml = chapOrder
    .filter(k => chapters[k])
    .map(k => `<section class="chapter">${mdToHtml(chapters[k])}</section>`)
    .join("\n");

  // ── Violaciones ───────────────────────────────────────────────────────────
  const violHtml = violations.length > 0 ? `
<table>
  <thead><tr><th>Artículo</th><th>Derecho</th><th>Severidad</th><th>Confianza</th></tr></thead>
  <tbody>
    ${violations.map(v => `
    <tr>
      <td><code>${v.article || "—"}</code></td>
      <td>${v.right || v.description || "—"}</td>
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

  /* ── Print ── */
  @media print {
    body { font-size: 11px; max-width: none; }
    .cover { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .kpi-strip, .charts-grid, .trace-section { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    h2 { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    blockquote { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .chapter { page-break-inside: avoid; }
    h2, h3 { page-break-after: avoid; }
    table { page-break-inside: avoid; }
    @page { margin: 18mm 15mm; size: A4; }
    .report-footer { display: flex; }
  }
</style>
</head>
<body>

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
        <div class="trace-row"><span class="trace-key">Agentes IA</span><span class="trace-val">4 (LangGraph + Claude Sonnet)</span></div>
        <div class="trace-row"><span class="trace-key">Riesgo calculado</span><span class="trace-val">${score}/100 — ${rp.label}</span></div>
        <div class="trace-row"><span class="trace-key">Violaciones</span><span class="trace-val">${violations.length} detectadas</span></div>
      </div>
    </div>
    <div class="disclaimer">
      <strong>Nota metodológica:</strong> Este informe es de carácter analítico y no constituye validación oficial de resultados electorales. Los datos son citados bajo licencias académicas abiertas (CC-BY-SA / CC-BY-4.0). La clasificación de riesgo es una estimación predictiva basada en indicadores históricos y estructurales, no en eventos futuros verificados.
    </div>
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
  const [anim, setAnim] = useState(0);
  useEffect(() => {
    let frame;
    const start = performance.now();
    const animate = (now) => {
      const p = Math.min((now - start) / 1400, 1);
      const eased = 1 - Math.pow(1 - p, 4);
      setAnim(eased * score);
      if (p < 1) frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [score]);

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
  const [anim, setAnim] = useState(0);
  const meta = DIMENSION_META[dimKey] || { label: dimKey, icon: "📊", desc: "" };

  useEffect(() => {
    const timer = setTimeout(() => {
      let frame;
      const start = performance.now();
      const animate = (now) => {
        const p = Math.min((now - start) / 900, 1);
        setAnim((1 - Math.pow(1 - p, 3)) * value);
        if (p < 1) frame = requestAnimationFrame(animate);
      };
      frame = requestAnimationFrame(animate);
      return () => cancelAnimationFrame(frame);
    }, delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

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
  const [fetchState, setFetchState] = useState({ data: null, loading: false, error: null });
  const [activeTab, setActiveTab] = useState("dashboard");
  const { data: reportData, loading, error } = fetchState;

  useEffect(() => {
    if (!runId) return;
    fetch(`${API_BASE}/api/report/${runId}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => setFetchState({ data, loading: false, error: null }))
      .catch(err => setFetchState({ data: null, loading: false, error: err.message }));
    return () => setFetchState({ data: null, loading: true, error: null });
  }, [runId]);

  const handleDownload = () => {
    if (!reportData || !country) return;
    const md = reportData.final_report_markdown || "";
    const htmlContent = generateHtmlReport(md, country, runId, reportData.timestamp, reportData);
    const blob = new Blob([htmlContent], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `PEIRS_${country.name}_${runId.slice(0,8)}_${new Date().toISOString().split("T")[0]}.html`;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a); URL.revokeObjectURL(url);
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

  const TABS = [
    { id: "dashboard", label: "📊 Dashboard", desc: "Vista ejecutiva con indicadores clave" },
    { id: "dictamen", label: "📋 Dictamen", desc: "Análisis técnico del sistema" },
    { id: "informe", label: "📄 Informe", desc: "Texto completo del reporte" },
  ];

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
          }}>⬇ HTML</button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{
        display: "flex", gap: 0,
        background: "#0d1220",
        border: `1px solid ${COLORS.border}`,
        borderTop: "none", borderBottom: "none",
      }}>
        {TABS.map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
            flex: 1, padding: "12px 16px", border: "none", cursor: "pointer",
            fontSize: 12, fontWeight: 600,
            background: activeTab === tab.id ? COLORS.surfaceLight : "transparent",
            color: activeTab === tab.id ? COLORS.accent : COLORS.textMuted,
            borderBottom: activeTab === tab.id ? `2px solid ${COLORS.accent}` : "2px solid transparent",
            transition: "all 0.2s ease",
          }}>
            {tab.label}
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

        {/* ── TAB: DASHBOARD ── */}
        {activeTab === "dashboard" && (
          <div>
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
          </div>
        )}

        {/* ── TAB: DICTAMEN ── */}
        {activeTab === "dictamen" && (
          <div>
            {dictamen.narrative ? (
              <>
                <div style={{
                  padding: "16px 20px", borderRadius: 12, marginBottom: 20,
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
              </>
            ) : (
              <div style={{ padding: 20, color: "#64748b", fontSize: 13 }}>
                Dictamen no disponible. Regenerá el análisis desde el dashboard.
              </div>
            )}
          </div>
        )}

        {/* ── TAB: INFORME ── */}
        {activeTab === "informe" && (
          <div>
            {md ? (
              <div style={{
                background: COLORS.surfaceLight, borderRadius: 10, padding: "20px 24px",
                border: `1px solid ${COLORS.border}`,
              }}>
                {renderMarkdownWithTooltips(md)}
              </div>
            ) : (
              <div style={{ color: "#64748b", fontSize: 13 }}>Informe no disponible.</div>
            )}
          </div>
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
              { icon: "🤖", title: "Pipeline de Agentes IA (LangGraph)", desc: "4 agentes especializados operan en secuencia: Ingesta OSINT → Análisis Político-Digital → Cumplimiento Legal → Generación de Informes VIP. Orquestados por LangGraph con estado compartido ElectionRiskState." },
              { icon: "🔍", title: "Fuentes OSINT Verificables", desc: "V-Dem v15 (Varieties of Democracy), Freedom House FIW 2025 (Freedom in the World), PEI 10.0 (Perceptions of Electoral Integrity). Todos los datos son open source, citados con DOI, y trazables a su fuente primaria. Sin observadores físicos: análisis 100% remoto y auditable." },
              { icon: "⚖️", title: "Base Legal: Pacto Internacional de Derechos Civiles y Políticos + Convención Americana sobre Derechos Humanos + Carta Democrática Interamericana", desc: "Cada hallazgo se vincula a artículos específicos del Pacto Internacional de Derechos Civiles y Políticos (ICCPR), la Convención Americana sobre Derechos Humanos (CADH) y la Carta Democrática Interamericana (CDI). Las violaciones se clasifican por severidad (critical/high/moderate) y nivel de verificación (confirmed/mock)." },
              { icon: "📊", title: "Índice Predictivo de Riesgo (0-100)", desc: "8 dimensiones ponderadas: FH (15%) + V-Dem (15%) + EMB (15%) + Medios (10%) + Financiamiento (10%) + Digital (10%) + Violaciones (15%) + Observación (10%)." },
              { icon: "🔐", title: "Trazabilidad Total", desc: "Cada dato tiene: source_id, confidence, data_hash SHA-256 e is_publishable. Los informes incluyen anexo de trazabilidad con Run ID, timestamp y versión del sistema." },
              { icon: "🚫", title: "Principio de No-Legitimación", desc: "PEIRS NO valida ni legitima resultados electorales. Emite un índice de riesgo predictivo para analistas, inversores y gobiernos. Los datos son para fines analíticos exclusivamente." },
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
                {["LangGraph", "Claude Sonnet", "FastAPI", "V-Dem v15", "Freedom House", "PEI 10.0", "React + Vite"].map((t, i) => (
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

  const { summary, active_alerts, watch_list } = data;

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
      <div>
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

const PERU_INNER_TABS = [
  { id: "inteligencia", label: "Inteligencia",  icon: "📡" },
  { id: "actores",      label: "Actores",        icon: "👥" },
  { id: "parlamento",   label: "Parlamento",     icon: "🏛" },
  { id: "brief",        label: "MOE Brief",      icon: "📋" },
  { id: "jornada",      label: "Jornada",        icon: "🗳" },
  { id: "informe",      label: "Informe",        icon: "📄" },
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

function PeruSituationRoom() {
  const [country, setCountry]       = useState(null);
  const [brief, setBrief]           = useState(null);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(null);
  const [moeTab, setMoeTab]         = useState("risk_context");
  const [countdown, setCountdown]   = useState({ days: 0, hrs: 0, mins: 0, secs: 0 });
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

  const ELECTION_TS = new Date("2026-04-12T08:00:00-05:00");

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/api/country/PER`).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
      fetch(`${API_BASE}/api/moe/brief/PER`).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
    ]).then(([cd, bd]) => { setCountry(cd); setBrief(bd); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  useEffect(() => {
    const tick = () => {
      const diff = ELECTION_TS - new Date();
      if (diff <= 0) { setCountdown({ days: 0, hrs: 0, mins: 0, secs: 0 }); return; }
      setCountdown({
        days: Math.floor(diff / 86400000),
        hrs:  Math.floor((diff % 86400000) / 3600000),
        mins: Math.floor((diff % 3600000) / 60000),
        secs: Math.floor((diff % 60000) / 1000),
      });
    };
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, []);

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
  }, [innerTab]);

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
      <div style={{ position: "sticky", top: 0, zIndex: 90 }}>
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
              <div style={{ display: "flex", gap: 4 }}>
                {[
                  { val: countdown.days, label: "días" },
                  { val: countdown.hrs,  label: "hrs"  },
                  { val: countdown.mins, label: "min"  },
                  { val: countdown.secs, label: "seg"  },
                ].map(({ val, label }) => (
                  <div key={label} style={{
                    textAlign: "center", padding: "4px 10px",
                    background: COLORS.surface, borderRadius: 7,
                    border: `1px solid ${COLORS.border}`,
                  }}>
                    <div style={{ fontSize: 20, fontWeight: 800, color: alertColor, fontFamily: "'DM Mono', monospace", lineHeight: 1.1 }}>
                      {String(val).padStart(2, "0")}
                    </div>
                    <div style={{ fontSize: 8, color: COLORS.textDim, letterSpacing: 1, textTransform: "uppercase" }}>{label}</div>
                  </div>
                ))}
              </div>
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
                <Card className="peru-card" style={{ marginBottom: 16 }}>
                  <SectionTitle icon="📊">Fuentes Verificadas</SectionTitle>
                  <div style={{ display: "flex", justifyContent: "space-around", padding: "10px 0 4px" }}>
                    <CircularScore value={country?.freedomScore} max={100} label="Freedom House" sublabel="FIW 2025"
                      color={country?.freedomScore < 40 ? COLORS.danger : country?.freedomScore < 65 ? COLORS.warning : COLORS.accent} size={88} />
                    <CircularScore value={country?.vdemIndex} max={1} label="V-Dem" sublabel="Lib. Democracy"
                      color={country?.vdemIndex < 0.3 ? COLORS.danger : country?.vdemIndex < 0.5 ? COLORS.warning : COLORS.accent} size={108} />
                    <CircularScore value={peiEmbs ? parseFloat(peiEmbs) : null} max={100} label="PEI — EMBs"
                      sublabel={peiYear ? `Elec. ${peiYear}` : "Sin datos"}
                      color={peiEmbs && parseFloat(peiEmbs) < 40 ? COLORS.danger : COLORS.warning} size={88} />
                  </div>
                  <div style={{ marginTop: 10, padding: "6px 10px", borderRadius: 7, background: COLORS.surfaceLight, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 10, color: COLORS.textDim }}>Convergencia entre fuentes</span>
                    <span style={{ fontSize: 13, fontWeight: 800, fontFamily: "'DM Mono', monospace",
                      color: convScore >= 75 ? COLORS.accent : convScore >= 50 ? COLORS.warning : COLORS.danger }}>
                      {convScore}/100
                    </span>
                  </div>
                </Card>
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

            {/* Comparativa historica */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
              <Card className="peru-card">
                <SectionTitle icon="📊">Comparativa Electoral: 2021 vs 2026</SectionTitle>
                {[
                  { label: "Freedom House Score", v21: 71,   v26: country?.freedomScore, unit: "/100", better: "higher" },
                  { label: "V-Dem Lib. Democracy", v21: 0.52, v26: country?.vdemIndex,   unit: "",     better: "higher" },
                  { label: "PEIRS Risk Score",      v21: 38,  v26: country?.riskScore,   unit: "/100", better: "lower"  },
                  { label: "Fragmentación Congreso", v21: "8+ bancadas", v26: "8+ bancadas (proy.)", unit: "", better: null },
                ].map(row => {
                  const v26n = typeof row.v26 === "number" ? row.v26 : null;
                  const improved    = v26n !== null && (row.better === "higher" ? v26n > row.v21  : row.better === "lower" ? v26n < row.v21 : false);
                  const deteriorated = v26n !== null && (row.better === "higher" ? v26n < row.v21  : row.better === "lower" ? v26n > row.v21 : false);
                  return (
                    <div key={row.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: `1px solid ${COLORS.border}` }}>
                      <span style={{ fontSize: 11, color: COLORS.textMuted }}>{row.label}</span>
                      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                        <span style={{ fontSize: 11, color: COLORS.textDim, fontFamily: "'DM Mono', monospace" }}>
                          2021: {row.v21}{row.unit}
                        </span>
                        <span style={{ fontSize: 11, fontWeight: 700, fontFamily: "'DM Mono', monospace",
                          color: improved ? COLORS.accent : deteriorated ? COLORS.danger : COLORS.text }}>
                          {improved ? "▲" : deteriorated ? "▼" : "●"} 2026: {v26n !== null ? v26n : row.v26}{typeof row.v26 === "number" ? row.unit : ""}
                        </span>
                      </div>
                    </div>
                  );
                })}
                <div style={{ marginTop: 12, padding: "8px 10px", borderRadius: 7, background: COLORS.dangerDim, fontSize: 10, color: COLORS.textDim, lineHeight: 1.6 }}>
                  Contexto: Perú 2026 llega con 6 presidentes en 4 años. La inestabilidad institucional crónica es el principal factor de riesgo estructural.
                </div>
              </Card>

              <Card className="peru-card">
                <SectionTitle icon="🕐">Línea del Tiempo — Crisis Democrática 2016–2026</SectionTitle>
                <div style={{ maxHeight: 260, overflowY: "auto", paddingRight: 4 }}>
                  {PERU_HIST_EVENTS.map((ev, i) => (
                    <div key={i} style={{ display: "flex", gap: 12, marginBottom: 10, alignItems: "flex-start" }}>
                      <div style={{
                        minWidth: 38, padding: "2px 6px", borderRadius: 5,
                        background: ev.year === 2026 ? alertColor + "22" : COLORS.surfaceLight,
                        border: `1px solid ${ev.year === 2026 ? alertColor + "66" : COLORS.border}`,
                        fontSize: 10, fontWeight: 700,
                        color: ev.year === 2026 ? alertColor : COLORS.textDim,
                        fontFamily: "'DM Mono', monospace", textAlign: "center",
                      }}>{ev.year}</div>
                      <div style={{ fontSize: 11, color: COLORS.textMuted, lineHeight: 1.5, paddingTop: 2 }}>{ev.label}</div>
                    </div>
                  ))}
                </div>
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
                      const isNoBancada = actor.id === "ind";
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

                // Majority marker at 66 seats (halfway across outermost arc)
                const majorityR = BASE_R + 4 * ROW_GAP + ROW_GAP * 0.5;
                const mx = cx;
                const my = cy - BASE_R - 2;

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

        {/* ══ TAB: INFORME ══ */}
        {innerTab === "informe" && (
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 3, color: COLORS.textDim, textTransform: "uppercase", marginBottom: 16, paddingBottom: 8, borderBottom: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", gap: 8 }}>
              Informe de Fondo — Análisis Completo PEIRS (9 Capítulos)
              <span style={{ flex: 1, height: 1, background: `linear-gradient(90deg, ${COLORS.border}, transparent)` }} />
            </div>
            {country?.run_id ? (
              <ReportViewer runId={country.run_id} country={country} />
            ) : (
              <div style={{ padding: 32, textAlign: "center", color: COLORS.textDim, fontFamily: "'DM Mono', monospace", fontSize: 12 }}>
                Sin reporte disponible. Ejecutá /api/analyze con country_code=PER primero.
              </div>
            )}
          </div>
        )}

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

export default function DemocracIADashboard() {
  const [activeView, setActiveView] = useState("overview");
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState("connecting");
  const [generatedAt, setGeneratedAt] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async (forceRefresh = false) => {
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
      if (!selectedCountry) setSelectedCountry(data.countries[0]?.id || null);
      setApiStatus("connected");
    } catch (err) {
      setError(err.message);
      setApiStatus("disconnected");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { fetchDashboardData(); }, []);

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
        onRefresh={() => fetchDashboardData(true)} refreshing={refreshing} generatedAt={generatedAt} />

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

