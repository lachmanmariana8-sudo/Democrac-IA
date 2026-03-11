import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, LineChart, Line, CartesianGrid, Legend, Cell } from "recharts";

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
        <div style={{ fontSize: size / 4, fontWeight: 800, color: riskColor, fontFamily: "'JetBrains Mono', monospace", letterSpacing: -1 }}>
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
    borderRadius: 12,
    padding: 20,
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
    fontSize: 11, fontWeight: 600, fontFamily: "'JetBrains Mono', monospace",
    background: color + "22", color: color, border: `1px solid ${color}44`,
    letterSpacing: 0.5,
  }}>
    {children}
  </span>
);

const SectionTitle = ({ children, icon }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
    <span style={{ fontSize: 18 }}>{icon}</span>
    <h3 style={{ margin: 0, fontSize: 14, fontWeight: 700, color: COLORS.text, textTransform: "uppercase", letterSpacing: 2 }}>
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
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet" />
    <div style={{
      width: 56, height: 56, borderRadius: 12,
      background: `linear-gradient(135deg, ${COLORS.accent}, ${COLORS.info})`,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: 28, fontWeight: 900, color: COLORS.bg,
      animation: "pulse 2s ease-in-out infinite",
    }}>D</div>
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: 18, fontWeight: 700, color: COLORS.text, fontFamily: "'Space Mono', monospace" }}>
        Democrac<span style={{ color: COLORS.accent }}>.IA</span>
      </div>
      <div style={{ fontSize: 12, color: COLORS.textMuted, marginTop: 6 }}>
        Ejecutando pipeline de agentes PEIRS...
      </div>
    </div>
    <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
      {["OSINT Ingesta", "Análisis Político", "Legal RAG", "Reporte VIP"].map((agent, i) => (
        <div key={i} style={{
          padding: "4px 10px", borderRadius: 6, fontSize: 10, fontWeight: 600,
          fontFamily: "'JetBrains Mono', monospace", letterSpacing: 0.5,
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
      fontSize: 12, color: COLORS.textMuted, fontFamily: "'JetBrains Mono', monospace",
    }}>
      uvicorn app:app --reload --port 8000
    </div>
    <div style={{ fontSize: 11, color: COLORS.danger, fontFamily: "'JetBrains Mono', monospace", marginTop: 8 }}>
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

const Navbar = ({ activeView, setActiveView, apiStatus }) => (
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
        <span style={{ fontSize: 17, fontWeight: 800, color: COLORS.text, letterSpacing: 1, fontFamily: "'Space Mono', monospace" }}>
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
        { id: "methodology", label: "Metodología" },
      ].map(tab => (
        <button key={tab.id} onClick={() => setActiveView(tab.id)} style={{
          padding: "7px 16px", borderRadius: 8, border: "none", cursor: "pointer",
          fontSize: 12, fontWeight: 600, letterSpacing: 0.5,
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
        <span style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'JetBrains Mono', monospace" }}>
          {apiStatus === "connected" ? "API LIVE" : "OFFLINE"}
        </span>
      </div>
      <Tag color={COLORS.accent}>LIVE</Tag>
      <span style={{ fontSize: 11, color: COLORS.textDim, fontFamily: "'JetBrains Mono', monospace" }}>
        {new Date().toISOString().split("T")[0]}
      </span>
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
            <div style={{ fontWeight: 700, color: COLORS.text, fontSize: 15 }}>{country.name}</div>
            <div style={{ fontSize: 11, color: COLORS.textMuted, fontFamily: "'JetBrains Mono', monospace" }}>
              Elección: {country.date}
            </div>
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: rl.color, fontFamily: "'JetBrains Mono', monospace" }}>
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
            <div style={{ fontSize: 32, fontWeight: 800, color: stat.color, fontFamily: "'JetBrains Mono', monospace" }}>
              <AnimatedCounter value={stat.value} suffix={stat.suffix || ""} />
            </div>
            <div style={{ fontSize: 11, color: COLORS.textMuted, marginTop: 4, textTransform: "uppercase", letterSpacing: 1 }}>
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
            <PolarAngleAxis dataKey="dimension" tick={{ fill: COLORS.textMuted, fontSize: 10 }} />
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

const DetailView = ({ country }) => {
  const rl = RISK_LEVELS[country.riskLevel] || RISK_LEVELS.moderate;
  const radarData = Object.entries(country.dimensions).map(([key, val]) => ({
    dimension: DIMENSION_LABELS[key], value: val, fullMark: 100,
  }));

  return (
    <div style={{ padding: 28 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 28 }}>
        <span style={{ fontSize: 42 }}>{country.flag}</span>
        <div>
          <h2 style={{ margin: 0, fontSize: 24, fontWeight: 800, color: COLORS.text }}>{country.name}</h2>
          <div style={{ display: "flex", gap: 10, marginTop: 6, alignItems: "center" }}>
            <Tag color={rl.color}>{rl.label}</Tag>
            <span style={{ fontSize: 12, color: COLORS.textMuted }}>Elección: {country.date}</span>
            <span style={{ fontSize: 12, color: country.trend === "deteriorating" ? COLORS.danger : COLORS.accent }}>
              {country.trend === "deteriorating" ? "▼ Deterioro" : "● Estable"}
            </span>
            {country.run_id && (
              <span style={{ fontSize: 10, color: COLORS.textDim, fontFamily: "'JetBrains Mono', monospace" }}>
                run: {country.run_id.slice(0, 8)}...
              </span>
            )}
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: 20, marginBottom: 24 }}>
        <Card style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <RiskGauge score={country.riskScore} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, width: "100%", marginTop: 16 }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 20, fontWeight: 700, color: COLORS.info, fontFamily: "'JetBrains Mono', monospace" }}>
                {country.freedomScore}
              </div>
              <div style={{ fontSize: 9, color: COLORS.textMuted, textTransform: "uppercase", letterSpacing: 1 }}>Freedom H.</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 20, fontWeight: 700, color: COLORS.purple, fontFamily: "'JetBrains Mono', monospace" }}>
                {country.vdemIndex}
              </div>
              <div style={{ fontSize: 9, color: COLORS.textMuted, textTransform: "uppercase", letterSpacing: 1 }}>V-Dem</div>
            </div>
          </div>
        </Card>

        <Card>
          <SectionTitle icon="⚠️">Alertas Activas</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {country.alerts.map((alert, i) => {
              const alertColor = alert.type === "critical" ? COLORS.danger : alert.type === "high" ? "#f97316" : alert.type === "moderate" ? COLORS.warning : COLORS.accent;
              return (
                <div key={i} style={{
                  display: "flex", alignItems: "flex-start", gap: 10, padding: "10px 14px",
                  background: alertColor + "0a", borderRadius: 8, borderLeft: `3px solid ${alertColor}`,
                }}>
                  <GlowDot color={alertColor} />
                  <span style={{ fontSize: 12, color: COLORS.text, lineHeight: 1.5 }}>{alert.text}</span>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 24 }}>
        <Card>
          <SectionTitle icon="🎯">Análisis Multidimensional de Integridad</SectionTitle>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={radarData}>
              <PolarGrid stroke={COLORS.border} />
              <PolarAngleAxis dataKey="dimension" tick={{ fill: COLORS.textMuted, fontSize: 10 }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: COLORS.textDim, fontSize: 9 }} />
              <Radar dataKey="value" stroke={rl.color} fill={rl.color} fillOpacity={0.15} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <SectionTitle icon="📉">Evolución del Índice de Riesgo</SectionTitle>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={country.timeline}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
              <XAxis dataKey="month" tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: COLORS.text }}
              />
              <Line type="monotone" dataKey="score" stroke={rl.color} strokeWidth={3} dot={{ fill: rl.color, r: 5 }}
                activeDot={{ r: 7, stroke: rl.color, strokeWidth: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 24 }}>
        <Card>
          <SectionTitle icon="📺">Exposición Mediática por Actor Político</SectionTitle>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={country.mediaData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
              <XAxis type="number" domain={[0, 100]} tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: COLORS.textMuted, fontSize: 11 }} width={90} />
              <Tooltip contentStyle={{ background: COLORS.surfaceLight, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="exposure" radius={[0, 6, 6, 0]} name="% Exposición">
                {country.mediaData.map((entry, i) => (
                  <Cell key={i} fill={i === 0 ? COLORS.danger : i === 1 ? COLORS.info : i === 2 ? COLORS.warning : COLORS.textDim} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <SectionTitle icon="⚖️">Violaciones al Derecho Internacional</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {country.violations.length === 0 ? (
              <div style={{ textAlign: "center", padding: 30, color: COLORS.accent }}>
                <div style={{ fontSize: 32, marginBottom: 8 }}>✓</div>
                <div style={{ fontSize: 13 }}>Sin violaciones detectadas</div>
              </div>
            ) : (
              country.violations.map((v, i) => (
                <div key={i} style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "12px 16px", background: COLORS.dangerDim, borderRadius: 8,
                  border: `1px solid ${COLORS.danger}33`,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <GlowDot color={COLORS.danger} />
                    <span style={{ fontSize: 13, fontWeight: 600, color: COLORS.text, fontFamily: "'JetBrains Mono', monospace" }}>
                      {v}
                    </span>
                  </div>
                  <Tag color={COLORS.danger}>ACTIVA</Tag>
                </div>
              ))
            )}
          </div>
          <div style={{ marginTop: 16, padding: "10px 14px", background: COLORS.surfaceLight, borderRadius: 8, fontSize: 11, color: COLORS.textMuted, lineHeight: 1.6 }}>
            Vinculación legal generada por Legal_ComplianceAgent vía pipeline LangGraph. Corpus EOS: ICCPR, CEDAW, ICERD.
          </div>
        </Card>
      </div>

      {/* Agent Logs */}
      {country.agentLogs && country.agentLogs.length > 0 && (
        <Card style={{ marginBottom: 24 }}>
          <SectionTitle icon="🤖">Log de Agentes — Pipeline Execution</SectionTitle>
          <div style={{
            background: "#050810", borderRadius: 8, padding: 16,
            fontFamily: "'JetBrains Mono', monospace", fontSize: 11,
            maxHeight: 200, overflowY: "auto", lineHeight: 1.8,
          }}>
            {country.agentLogs.map((log, i) => {
              const isError = log.includes("ERROR");
              const isComplete = log.includes("completada") || log.includes("generado");
              const color = isError ? COLORS.danger : isComplete ? COLORS.accent : COLORS.textMuted;
              return <div key={i} style={{ color }}>{log}</div>;
            })}
          </div>
        </Card>
      )}

      <Card>
        <SectionTitle icon="📋">Estructura del Informe VIP — Capítulos Modulares</SectionTitle>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
          {[
            { num: "01", title: "Resumen Ejecutivo & Dashboard de Riesgo", status: "generated" },
            { num: "02", title: "Contexto Político y Marco Legal", status: "generated" },
            { num: "03", title: "Administración Electoral (EMB)", status: "generated" },
            { num: "04", title: "Inclusividad y Derechos Humanos", status: "generated" },
            { num: "05", title: "Campaña, Redes de Poder y Financiamiento", status: "generated" },
            { num: "06", title: "Ecosistema de Información Digital", status: "generated" },
            { num: "07", title: "Día de Votación (Inferido)", status: "pending" },
            { num: "08", title: "Justicia Electoral y Disputas", status: "generated" },
            { num: "09", title: "Matriz de Recomendaciones VIP", status: "generated" },
          ].map((ch, i) => {
            const statusColor = ch.status === "generated" ? COLORS.accent : ch.status === "processing" ? COLORS.warning : COLORS.textDim;
            const statusLabel = ch.status === "generated" ? "LISTO" : ch.status === "processing" ? "EN PROCESO" : "PENDIENTE";
            return (
              <div key={i} style={{
                padding: "14px 16px", background: COLORS.surfaceLight, borderRadius: 10,
                borderLeft: `3px solid ${statusColor}`, display: "flex", flexDirection: "column", gap: 6,
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: 18, fontWeight: 800, color: statusColor, fontFamily: "'JetBrains Mono', monospace" }}>
                    {ch.num}
                  </span>
                  <Tag color={statusColor}>{statusLabel}</Tag>
                </div>
                <div style={{ fontSize: 12, fontWeight: 600, color: COLORS.text, lineHeight: 1.4 }}>{ch.title}</div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};

const MethodologyView = () => (
  <div style={{ padding: 28, maxWidth: 800 }}>
    <h2 style={{ margin: "0 0 8px", fontSize: 22, fontWeight: 800, color: COLORS.text }}>Metodología PEIRS</h2>
    <p style={{ margin: "0 0 28px", fontSize: 13, color: COLORS.textMuted, lineHeight: 1.7 }}>
      El sistema evalúa la integridad electoral basándose exclusivamente en obligaciones del derecho internacional público y estándares de la Declaración de Principios para la Observación Internacional de Elecciones.
    </p>

    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {[
        {
          icon: "🤖", title: "Enjambre de Agentes IA (LangGraph)",
          desc: "4 agentes especializados operan en secuencia: Ingesta OSINT → Análisis Político-Digital → Cumplimiento Legal (RAG) → Generación de Informes VIP. Orquestados por LangGraph con estado compartido.",
        },
        {
          icon: "🔍", title: "Fuentes OSINT Verificables",
          desc: "Freedom House, V-Dem, portales de EMBs, APIs de redes sociales, portales judiciales y legislativos. Sin observadores físicos: todo remoto y auditable.",
        },
        {
          icon: "⚖️", title: "Base Legal: EOS + Centro Carter",
          desc: "Más de 300 documentos vectorizados: ICCPR, CEDAW, ICERD, convenciones anti-corrupción. Cada irregularidad se vincula a artículos específicos vía RAG.",
        },
        {
          icon: "📊", title: "Índice Predictivo de Riesgo (0-100)",
          desc: "8 dimensiones ponderadas: Sufragio, Marco Legal, Independencia EMB, Libertad de Medios, Financiamiento, Ecosistema Digital, Justicia Electoral e Inclusividad.",
        },
        {
          icon: "🔌", title: "API REST en Tiempo Real",
          desc: "Backend FastAPI sirve los datos del pipeline a este dashboard. Cada consulta ejecuta los 4 agentes y devuelve el análisis completo en JSON.",
        },
        {
          icon: "🚫", title: "Principio de No-Legitimación",
          desc: "PEIRS NO valida ni legitima resultados electorales. Emite un índice de riesgo predictivo para que analistas, inversores y gobiernos tomen decisiones informadas.",
        },
      ].map((item, i) => (
        <Card key={i}>
          <div style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
            <div style={{
              width: 44, height: 44, borderRadius: 10, background: COLORS.accentDim,
              display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, flexShrink: 0,
            }}>
              {item.icon}
            </div>
            <div>
              <div style={{ fontWeight: 700, color: COLORS.text, fontSize: 14, marginBottom: 4 }}>{item.title}</div>
              <div style={{ fontSize: 12, color: COLORS.textMuted, lineHeight: 1.7 }}>{item.desc}</div>
            </div>
          </div>
        </Card>
      ))}
    </div>

    <Card style={{ marginTop: 24, background: "linear-gradient(135deg, #0d1a2a 0%, #0a1628 100%)", border: `1px solid ${COLORS.accent}44` }}>
      <div style={{ textAlign: "center", padding: 16 }}>
        <div style={{ fontSize: 13, color: COLORS.accent, fontWeight: 700, textTransform: "uppercase", letterSpacing: 3, marginBottom: 8 }}>
          Stack Tecnológico
        </div>
        <div style={{ display: "flex", justifyContent: "center", gap: 16, flexWrap: "wrap" }}>
          {["LangGraph", "Claude Opus/Sonnet", "FastAPI", "PostgreSQL", "Neo4j", "Pinecone", "Playwright"].map((t, i) => (
            <Tag key={i} color={COLORS.accent}>{t}</Tag>
          ))}
        </div>
      </div>
    </Card>
  </div>
);

export default function DemocracIADashboard() {
  const [activeView, setActiveView] = useState("overview");
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState("connecting");

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/dashboard`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setCountries(data.countries);
      setSelectedCountry(data.countries[0]?.id || null);
      setApiStatus("connected");
    } catch (err) {
      setError(err.message);
      setApiStatus("disconnected");
    } finally {
      setLoading(false);
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
      background: COLORS.bg,
      color: COLORS.text,
      fontFamily: "'Outfit', 'Segoe UI', sans-serif",
    }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet" />
      <Navbar activeView={activeView} setActiveView={setActiveView} apiStatus={apiStatus} />

      {activeView === "detail" && (
        <div style={{ padding: "12px 28px 0", display: "flex", gap: 8 }}>
          {countries.map(c => (
            <button key={c.id} onClick={() => setSelectedCountry(c.id)} style={{
              padding: "6px 14px", borderRadius: 8, border: "none", cursor: "pointer",
              fontSize: 12, fontWeight: 600,
              background: selectedCountry === c.id ? COLORS.accent + "22" : COLORS.surface,
              color: selectedCountry === c.id ? COLORS.accent : COLORS.textMuted,
              border: `1px solid ${selectedCountry === c.id ? COLORS.accent + "44" : COLORS.border}`,
            }}>
              {c.flag} {c.name}
            </button>
          ))}
        </div>
      )}

      {activeView === "overview" && <OverviewView countries={countries} onSelectCountry={handleSelectCountry} />}
      {activeView === "detail" && country && <DetailView country={country} />}
      {activeView === "methodology" && <MethodologyView />}

      <footer style={{
        padding: "16px 28px", borderTop: `1px solid ${COLORS.border}`,
        display: "flex", justifyContent: "space-between", alignItems: "center",
      }}>
        <span style={{ fontSize: 10, color: COLORS.textDim, letterSpacing: 1 }}>
          DEMOCRAC.IA — PEIRS v0.1.0 — CONECTADO A BACKEND LANGGRAPH
        </span>
        <span style={{ fontSize: 10, color: COLORS.textDim }}>
          © 2026 — Inteligencia Electoral OSINT
        </span>
      </footer>
    </div>
  );
}