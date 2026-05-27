// LANDING PAGE PUBLICA — accesible en / (root) sin auth.
// Extraída de App.jsx en Sprint 2 para code-splitting via React.lazy().
// Paleta CLARA en la misma gama que el brand (navy + terracota).

import { useState, useEffect } from "react";
import { LIGHT, API_BASE } from "../shared.js";
import { BrandLogo } from "../BrandLogo.jsx";

export default function LandingPage({ onEnterApp, onShowVoto }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/public/stats`)
      .then(r => r.ok ? r.json() : null)
      .then(data => { if (data) setStats(data); })
      .catch(() => { /* stats opcionales; la landing renderiza con — si falla */ });
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
      minHeight: "100vh", background: LIGHT.bg, color: LIGHT.ink,
      fontFamily: "Inter, 'DM Sans', system-ui, sans-serif",
    }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500;600&family=Fraunces:wght@300;500;700;900&family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />

      {/* NAV */}
      <nav aria-label="Navegación principal" style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        padding: "20px 7%", borderBottom: `1px solid ${LIGHT.border}`,
        position: "sticky", top: 0, zIndex: 100, background: LIGHT.bg + "ee",
        backdropFilter: "blur(10px)",
      }}>
        <BrandLogo size={42} withWordmark wordmarkSize={26} lightOnDark={false} />
        <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
          <a href="#producto" style={{ color: LIGHT.inkSoft, textDecoration: "none", fontSize: 14, fontWeight: 600 }}>Producto</a>
          <a href="#datos" style={{ color: LIGHT.inkSoft, textDecoration: "none", fontSize: 14, fontWeight: 600 }}>Datos</a>
          <button onClick={onShowVoto} aria-label="Ir a la solapa Voto Informado" style={{
            background: "transparent", border: "none", padding: 0,
            color: LIGHT.terracotta, fontSize: 14, fontWeight: 700, cursor: "pointer",
            letterSpacing: 0.2,
          }}>Voto Informado →</button>
          <a href="#metodologia" style={{ color: LIGHT.inkSoft, textDecoration: "none", fontSize: 14, fontWeight: 600 }}>Metodología</a>
          <button onClick={onEnterApp} aria-label="Abrir el dashboard técnico" style={{
            padding: "10px 20px", borderRadius: 8, border: `1px solid ${LIGHT.terracotta}`,
            background: LIGHT.terracotta, color: "#fff", fontSize: 14, fontWeight: 700,
            cursor: "pointer", letterSpacing: 0.3,
          }}>Acceder al dashboard →</button>
        </div>
      </nav>

      <main id="main-content">
      {/* HERO */}
      <section style={{ padding: "80px 7% 60px", maxWidth: 1400, margin: "0 auto" }}>
        <div style={{
          display: "inline-block", padding: "6px 14px", borderRadius: 20,
          background: LIGHT.terracottaBg, border: `1px solid ${LIGHT.terracottaSoft}`,
          color: LIGHT.terracotta, fontSize: 12, fontWeight: 700, letterSpacing: 1.5,
          textTransform: "uppercase", marginBottom: 24,
        }}>
          Predictive Electoral Integrity & Risk System
        </div>
        <h1 style={{
          fontSize: 64, fontWeight: 900, lineHeight: 1.1, letterSpacing: -2,
          margin: "0 0 24px", maxWidth: 900,
          fontFamily: "Fraunces, Georgia, serif", color: LIGHT.ink,
        }}>
          Inteligencia electoral basada en evidencia,<br />
          <span style={{ color: LIGHT.terracotta }}>con trazabilidad verificable.</span>
        </h1>
        <p style={{
          fontSize: 22, lineHeight: 1.6, color: LIGHT.inkSoft, maxWidth: 800,
          margin: "0 0 40px", fontWeight: 400,
        }}>
          Plataforma de inteligencia artificial diseñada para anticipar riesgos
          sobre la integridad electoral y la calidad democrática. Análisis basado
          en datasets internacionales con transparencia metodológica completa.
        </p>
        <div style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
          <button onClick={onEnterApp} style={{
            padding: "16px 32px", borderRadius: 10, border: "none",
            background: LIGHT.terracotta, color: "#fff", fontSize: 16, fontWeight: 800,
            cursor: "pointer", letterSpacing: 0.3,
            boxShadow: `0 6px 24px ${LIGHT.terracotta}33`,
          }}>Ver dashboard en vivo →</button>
          <a href="https://github.com/lachmanmariana8-sudo/democracia-peirs/blob/main/DOCS%20Proyect/PEIRS_Indices_Methodology_v1.0.md"
             target="_blank" rel="noopener noreferrer" style={{
            padding: "16px 32px", borderRadius: 10, border: `1px solid ${LIGHT.borderStrong}`,
            background: LIGHT.surface, color: LIGHT.ink, fontSize: 16, fontWeight: 700,
            textDecoration: "none", letterSpacing: 0.3,
          }}>Leer metodología</a>
        </div>
      </section>

      {/* STATS LIVE */}
      <section id="datos" style={{
        padding: "60px 7%", maxWidth: 1400, margin: "0 auto",
        borderTop: `1px solid ${LIGHT.border}`, borderBottom: `1px solid ${LIGHT.border}`,
        background: LIGHT.bgAlt,
      }}>
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 12, color: LIGHT.textMuted, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 8 }}>
            Datos en vivo · {lastUpdate ? `actualizado ${new Date(lastUpdate).toLocaleString('es-AR', { dateStyle: 'medium', timeStyle: 'short' })}` : "sincronizando..."}
          </div>
          <h2 style={{ fontSize: 36, fontWeight: 800, margin: 0, fontFamily: "Fraunces, serif", color: LIGHT.ink }}>
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
            background: LIGHT.surface, borderRadius: 16,
            border: `1px solid ${LIGHT.border}`,
            boxShadow: "0 2px 12px rgba(28, 34, 48, 0.04)",
            flexWrap: "wrap",
          }}>
            <div style={{ fontSize: 80, lineHeight: 1 }}>{primary.flag}</div>
            <div style={{ flex: 1, minWidth: 280 }}>
              <div style={{ fontSize: 11, color: LIGHT.textMuted, letterSpacing: 2,
                textTransform: "uppercase", fontWeight: 700, marginBottom: 8 }}>
                Cobertura activa
              </div>
              <h3 style={{ fontSize: 32, fontWeight: 800, margin: "0 0 8px",
                fontFamily: "Fraunces, serif", color: LIGHT.ink }}>
                {primary.name} {primary.election_date && `· Elecciones ${primary.election_date.slice(0, 4)}`}
              </h3>
              <p style={{ color: LIGHT.inkSoft, fontSize: 16, margin: "0 0 16px" }}>
                Fase actual: <span style={{ color: LIGHT.ink, fontWeight: 700 }}>{primary.phase_label || primary.phase}</span>
              </p>
              <button onClick={onEnterApp} style={{
                padding: "12px 24px", borderRadius: 8, border: `1px solid ${LIGHT.terracotta}`,
                background: "transparent", color: LIGHT.terracotta, fontSize: 14, fontWeight: 700,
                cursor: "pointer",
              }}>Explorar el monitoreo →</button>
            </div>
          </div>
        </section>
      )}

      {/* QUE HACE */}
      <section id="producto" style={{ padding: "80px 7%", maxWidth: 1400, margin: "0 auto" }}>
        <div style={{ marginBottom: 56 }}>
          <div style={{ fontSize: 12, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
            ¿Qué hace Democrac.IA?
          </div>
          <h2 style={{ fontSize: 42, fontWeight: 800, margin: "0 0 24px",
            fontFamily: "Fraunces, serif", color: LIGHT.ink, letterSpacing: -1, maxWidth: 900 }}>
            Inteligencia electoral para anticipar riesgos,<br/>
            no para describir crisis ya consumadas.
          </h2>
          <p style={{ fontSize: 18, color: LIGHT.inkSoft, maxWidth: 780, lineHeight: 1.7, margin: "0 0 16px" }}>
            Democrac.IA nace de una constatación incómoda: los riesgos sobre la
            integridad electoral se documentan tarde, cuando los daños sobre la
            confianza institucional ya ocurrieron. La cobertura mediática se
            concentra en la coyuntura del conflicto. Los informes académicos
            llegan meses después. Las misiones de observación internacional
            cubren ventanas estrechas. Entre todos ellos queda una zona ciega
            donde se incuban los problemas que después se vuelven crisis.
          </p>
          <p style={{ fontSize: 18, color: LIGHT.inkSoft, maxWidth: 780, lineHeight: 1.7, margin: 0 }}>
            Construimos un sistema que reduce esa ventana ciega. Monitoreo
            OSINT continuo, datasets internacionales estandarizados, marco
            normativo trazable y análisis predictivo con bandas de
            confianza — todo bajo trazabilidad verificable, sin sesgo
            partidario y con código abierto.
          </p>
        </div>

        {/* VALORES */}
        <div style={{
          marginBottom: 56, padding: 32,
          background: LIGHT.surfaceAlt, borderRadius: 16,
          border: `1px solid ${LIGHT.border}`,
          borderLeft: `4px solid ${LIGHT.terracotta}`,
        }}>
          <div style={{ fontSize: 11, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 16 }}>
            Nuestros valores
          </div>
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: 24,
          }}>
            <ValueItem title="Trazabilidad por diseño"
              desc="Cada índice cuantitativo tiene fórmula auditable. Cada hallazgo cita fuente con URL verificable. Sin números mágicos." />
            <ValueItem title="Apartidismo verificable"
              desc="No aceptamos financiamiento de partidos, candidatos ni fundaciones partidarias. La política se publica y se audita." />
            <ValueItem title="Evidencia sobre opinión"
              desc="Reglas determinísticas sobre datasets estructurales + IA sobre OSINT. La hipótesis sin evidencia no entra al informe." />
            <ValueItem title="Open-source"
              desc="Código bajo licencia abierta. Metodología publicada. Cualquier observador externo puede inspeccionar, cuestionar y replicar." />
            <ValueItem title="Privacidad por defecto"
              desc="Sin captura de datos personales identificables. Anonimización diferencial en cualquier métrica agregada." />
            <ValueItem title="Auditabilidad externa"
              desc="Reporte anual público de transparencia. Auditoría independiente sobre el pipeline. Comité de ética con poder de veto." />
          </div>
        </div>

        <div style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 28, fontWeight: 800, margin: "0 0 8px",
            fontFamily: "Fraunces, serif", color: LIGHT.ink }}>
            Cómo está construido
          </h3>
          <p style={{ fontSize: 16, color: LIGHT.inkSoft, maxWidth: 720, lineHeight: 1.6, margin: 0 }}>
            Pipeline híbrido: reglas determinísticas sobre datasets estructurales
            + clasificación automática con Claude Sonnet 4.6 sobre evidencia
            OSINT en tiempo real.
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

      {/* VOTO INFORMADO TEASER */}
      <section style={{
        padding: "60px 7%", maxWidth: 1400, margin: "0 auto",
      }}>
        <div style={{
          padding: 40, borderRadius: 16,
          background: LIGHT.ink, color: "#fff",
          display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 40,
          alignItems: "center",
        }} className="voto-teaser">
          <div>
            <div style={{ fontSize: 11, color: LIGHT.terracottaSoft, letterSpacing: 2,
              textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
              Un proyecto de Democrac.IA
            </div>
            <h3 style={{ fontSize: 36, fontWeight: 800, margin: "0 0 16px",
              fontFamily: "Fraunces, serif", letterSpacing: -1 }}>
              voto<span style={{ color: LIGHT.terracotta }}>.</span>informado
            </h3>
            <p style={{ fontSize: 17, lineHeight: 1.7, margin: "0 0 24px",
              color: "#e5dcd0", maxWidth: 540 }}>
              Una plataforma cívica, apartidaria y open-source para que cada
              ciudadano pueda comparar sus propias posiciones con las propuestas
              reales de cada agrupación política, antes de votar.
            </p>
            <button onClick={onShowVoto} style={{
              padding: "14px 28px", borderRadius: 10, border: "none",
              background: LIGHT.terracotta, color: "#fff", fontSize: 15, fontWeight: 800,
              cursor: "pointer", letterSpacing: 0.3,
            }}>Conocer Voto Informado →</button>
          </div>
          <div style={{
            fontFamily: "Fraunces, Georgia, serif", fontStyle: "italic",
            fontSize: 22, lineHeight: 1.5, color: LIGHT.terracottaSoft,
            borderLeft: `3px solid ${LIGHT.terracotta}`, paddingLeft: 20,
          }}>
            "Saber antes de elegir."
          </div>
        </div>
      </section>

      {/* METODOLOGIA */}
      <section id="metodologia" style={{
        padding: "80px 7%", maxWidth: 1400, margin: "0 auto",
        borderTop: `1px solid ${LIGHT.border}`,
        background: LIGHT.bgAlt,
      }}>
        <h2 style={{ fontSize: 36, fontWeight: 800, margin: "0 0 16px",
          fontFamily: "Fraunces, serif", color: LIGHT.ink }}>Transparencia metodológica</h2>
        <p style={{ fontSize: 17, color: LIGHT.inkSoft, maxWidth: 720, lineHeight: 1.6, marginBottom: 32 }}>
          Cada índice cuantitativo del informe Elite tiene fórmula auditable
          documentada. Citable formalmente por tribunales, organismos
          supranacionales y dataset partners.
        </p>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
          <a href="https://github.com/lachmanmariana8-sudo/democracia-peirs/blob/main/DOCS%20Proyect/PEIRS_Indices_Methodology_v1.0.md"
             target="_blank" rel="noopener noreferrer" style={{
            padding: "14px 24px", borderRadius: 10, border: `1px solid ${LIGHT.borderStrong}`,
            background: LIGHT.surface, color: LIGHT.ink, fontSize: 14, fontWeight: 700,
            textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 8,
          }}>📄 Metodología de Índices v1.0</a>
          <a href="https://github.com/lachmanmariana8-sudo/democracia-peirs"
             target="_blank" rel="noopener noreferrer" style={{
            padding: "14px 24px", borderRadius: 10, border: `1px solid ${LIGHT.borderStrong}`,
            background: LIGHT.surface, color: LIGHT.ink, fontSize: 14, fontWeight: 700,
            textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 8,
          }}>💻 Código fuente</a>
        </div>
      </section>

      {/* DISCLOSURE */}
      <section style={{ padding: "60px 7%", maxWidth: 1400, margin: "0 auto" }}>
        <div style={{
          padding: 32, background: LIGHT.surfaceAlt, borderRadius: 16,
          border: `1px solid ${LIGHT.terracottaSoft}`,
          borderLeft: `4px solid ${LIGHT.terracotta}`,
        }}>
          <div style={{ fontSize: 11, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
            Disclosure institucional
          </div>
          <p style={{ fontSize: 17, color: LIGHT.ink, margin: 0, lineHeight: 1.7, fontWeight: 500 }}>
            <strong>Democrac.IA no legitima ni valida resultados electorales.</strong>{" "}
            Esta plataforma emite inteligencia electoral con trazabilidad
            verificable bajo estándares internacionales de observación electoral,
            sin sesgo político-partidario.
          </p>
        </div>
      </section>
      </main>

      {/* FOOTER */}
      <footer style={{
        padding: "40px 7%", borderTop: `1px solid ${LIGHT.border}`,
        background: LIGHT.bgAlt,
        display: "flex", justifyContent: "space-between", alignItems: "center",
        flexWrap: "wrap", gap: 16, color: LIGHT.textMuted, fontSize: 13,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <BrandLogo size={28} lightOnDark={false} />
          <span>Democrac.IA · PEIRS v0.6.0</span>
        </div>
        <div style={{ display: "flex", gap: 24 }}>
          <a href="https://github.com/lachmanmariana8-sudo/democracia-peirs"
             target="_blank" rel="noopener noreferrer"
             style={{ color: LIGHT.textMuted, textDecoration: "none" }}>GitHub</a>
          <button onClick={onShowVoto} style={{
            background: "transparent", border: "none", padding: 0,
            color: LIGHT.textMuted, fontSize: 13, cursor: "pointer",
          }}>Voto Informado</button>
          <a href="#metodologia" style={{ color: LIGHT.textMuted, textDecoration: "none" }}>Metodología</a>
          <button onClick={onEnterApp} style={{
            background: "transparent", border: "none", color: LIGHT.textMuted,
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
      padding: 24, background: LIGHT.surface, borderRadius: 12,
      border: `1px solid ${accent ? LIGHT.terracottaSoft : LIGHT.border}`,
      boxShadow: "0 2px 12px rgba(28, 34, 48, 0.04)",
    }}>
      <div style={{ fontSize: 11, color: LIGHT.textMuted, letterSpacing: 1.5,
        textTransform: "uppercase", fontWeight: 700, marginBottom: 10 }}>{label}</div>
      <div style={{
        fontSize: 48, fontWeight: 900, lineHeight: 1, marginBottom: 8,
        color: accent ? LIGHT.terracotta : LIGHT.ink,
        fontFamily: "Fraunces, Georgia, serif", letterSpacing: -1.5,
      }}>{typeof value === "number" ? value.toLocaleString('es-AR') : value}</div>
      <div style={{ fontSize: 12, color: LIGHT.textDim }}>{hint}</div>
    </div>
  );
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div style={{
      padding: 24, background: LIGHT.surface, borderRadius: 12,
      border: `1px solid ${LIGHT.border}`,
      boxShadow: "0 2px 12px rgba(28, 34, 48, 0.04)",
    }}>
      <div style={{ fontSize: 32, marginBottom: 12 }}>{icon}</div>
      <h3 style={{ fontSize: 18, fontWeight: 800, margin: "0 0 8px",
        fontFamily: "Inter, sans-serif", color: LIGHT.ink }}>{title}</h3>
      <p style={{ fontSize: 14, color: LIGHT.inkSoft, margin: 0, lineHeight: 1.6 }}>{desc}</p>
    </div>
  );
}

function ValueItem({ title, desc }) {
  return (
    <div>
      <h4 style={{
        fontSize: 15, fontWeight: 800, margin: "0 0 6px",
        color: LIGHT.ink, fontFamily: "Inter, sans-serif",
        display: "flex", alignItems: "center", gap: 8,
      }}>
        <span style={{
          display: "inline-block", width: 8, height: 8, borderRadius: 4,
          background: LIGHT.terracotta,
        }} />
        {title}
      </h4>
      <p style={{ fontSize: 14, color: LIGHT.inkSoft, margin: 0, lineHeight: 1.6 }}>{desc}</p>
    </div>
  );
}
