// VOTO INFORMADO — solapa pública dedicada al proyecto cívico.
// Extraída de App.jsx en Sprint 2 para code-splitting via React.lazy().
// Página estática (sin estado): solo usa LIGHT + BrandLogo.

import { LIGHT } from "../shared.js";
import { BrandLogo } from "../BrandLogo.jsx";

export default function VotoInformadoPage({ onBack, onEnterApp }) {
  return (
    <div style={{
      minHeight: "100vh", background: LIGHT.bg, color: LIGHT.ink,
      fontFamily: "Inter, 'DM Sans', system-ui, sans-serif",
    }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Fraunces:wght@300;500;700;900&family=Inter:wght@400;500;600;700;800;900&family=Source+Serif+Pro:ital,wght@1,400;1,600&display=swap" rel="stylesheet" />

      {/* NAV */}
      <nav aria-label="Navegación Voto Informado" style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        padding: "20px 7%", borderBottom: `1px solid ${LIGHT.border}`,
        position: "sticky", top: 0, zIndex: 100, background: LIGHT.bg + "ee",
        backdropFilter: "blur(10px)",
      }}>
        <BrandLogo size={42} withWordmark wordmarkSize={26} lightOnDark={false} />
        <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
          <button onClick={onBack} aria-label="Volver a la página principal de Democrac.IA" style={{
            background: "transparent", border: "none", padding: 0,
            color: LIGHT.inkSoft, fontSize: 14, fontWeight: 600, cursor: "pointer",
          }}>← Volver a Democrac.IA</button>
          <button onClick={onEnterApp} aria-label="Abrir el dashboard técnico" style={{
            padding: "10px 20px", borderRadius: 8, border: `1px solid ${LIGHT.borderStrong}`,
            background: LIGHT.surface, color: LIGHT.ink, fontSize: 14, fontWeight: 700,
            cursor: "pointer", letterSpacing: 0.3,
          }}>Dashboard →</button>
        </div>
      </nav>

      <main id="main-content">
      {/* HERO */}
      <section style={{
        padding: "100px 7% 60px", maxWidth: 1400, margin: "0 auto",
        display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: 60,
        alignItems: "center",
      }} className="voto-hero">
        <div>
          <div style={{
            display: "inline-block", padding: "6px 14px", borderRadius: 20,
            background: LIGHT.terracottaBg, border: `1px solid ${LIGHT.terracottaSoft}`,
            color: LIGHT.terracotta, fontSize: 12, fontWeight: 700, letterSpacing: 1.5,
            textTransform: "uppercase", marginBottom: 24,
          }}>
            Un proyecto de Democrac.IA
          </div>
          <h1 style={{
            fontSize: 72, fontWeight: 900, lineHeight: 1, letterSpacing: -3,
            margin: "0 0 24px",
            fontFamily: "Fraunces, Georgia, serif", color: LIGHT.ink,
          }}>
            voto<span style={{ color: LIGHT.terracotta }}>.</span>informado
          </h1>
          <p style={{
            fontSize: 24, lineHeight: 1.5, color: LIGHT.inkSoft, fontStyle: "italic",
            fontFamily: "Source Serif Pro, Georgia, serif",
            margin: "0 0 24px", maxWidth: 560,
          }}>
            Saber antes de elegir. Una plataforma cívica para el ejercicio
            del voto consciente.
          </p>
          <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", marginBottom: 20 }}>
            {["Apartidaria", "Gratuita", "Anónima", "Verificable", "Open-source"].map((chip) => (
              <span key={chip} style={{
                padding: "8px 14px", borderRadius: 6,
                background: LIGHT.surface, border: `1px solid ${LIGHT.border}`,
                fontSize: 12, fontWeight: 700, color: LIGHT.inkSoft, letterSpacing: 0.5,
              }}>{chip}</span>
            ))}
          </div>
          <div style={{
            padding: "12px 16px", borderRadius: 8,
            background: LIGHT.bgAlt, border: `1px solid ${LIGHT.border}`,
            fontSize: 13, color: LIGHT.inkSoft, lineHeight: 1.6, maxWidth: 560,
          }}>
            <strong style={{ color: LIGHT.ink }}>Lo que no hace:</strong>{" "}
            no recomienda candidatos, no predice ganadores, no registra tu voto,
            no captura datos personales identificables.
          </div>
        </div>
        <PhoneMockupWelcome />
      </section>

      {/* QUE ES */}
      <section style={{
        padding: "60px 7%", maxWidth: 1100, margin: "0 auto",
      }}>
        <div style={{ fontSize: 12, color: LIGHT.terracotta, letterSpacing: 2,
          textTransform: "uppercase", fontWeight: 700, marginBottom: 16 }}>
          ¿Qué es Voto Informado?
        </div>
        <h2 style={{ fontSize: 38, fontWeight: 800, margin: "0 0 24px",
          fontFamily: "Fraunces, serif", color: LIGHT.ink, letterSpacing: -1,
          maxWidth: 900 }}>
          Una aplicación para comparar tus posiciones con las propuestas
          reales de cada agrupación política — sin saber, mientras respondés,
          a qué partido pertenece cada propuesta.
        </h2>
        <div style={{
          display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40,
          marginTop: 32,
        }} className="voto-twocol">
          <p style={{ fontSize: 17, color: LIGHT.inkSoft, lineHeight: 1.7, margin: 0 }}>
            En la mayoría de las democracias contemporáneas, los partidos
            disponen de información sofisticada sobre los votantes mientras
            los votantes disponen, en el mejor de los casos, de cobertura
            mediática fragmentada y una intuición construida en pocos minutos
            frente al cuarto oscuro. Voto Informado reduce esa asimetría con
            un instrumento simple: comparación programática estructurada,
            anónima y verificable.
          </p>
          <p style={{ fontSize: 17, color: LIGHT.inkSoft, lineHeight: 1.7, margin: 0 }}>
            El usuario responde a veinte propuestas concretas presentadas
            sin atribución partidaria. Recién al final se revela qué partido
            sostiene cada propuesta. La devolución muestra los cinco partidos
            más cercanos a sus respuestas — nunca un único ganador, siempre
            con la advertencia explícita de que no es una recomendación de
            voto sino una medida de coincidencia.
          </p>
        </div>
      </section>

      {/* PRIVACIDAD POR DISEÑO */}
      <section style={{
        padding: "60px 7%", maxWidth: 1100, margin: "0 auto",
      }}>
        <div style={{ marginBottom: 28, maxWidth: 820 }}>
          <div style={{ fontSize: 12, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
            Tu privacidad, por diseño
          </div>
          <h2 style={{ fontSize: 32, fontWeight: 800, margin: "0 0 16px",
            fontFamily: "Fraunces, serif", color: LIGHT.ink, letterSpacing: -0.5 }}>
            Es la pregunta #1 que se hace cualquier persona antes de bajar
            una app que registra posiciones políticas. Esta es la respuesta corta.
          </h2>
        </div>
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: 16, marginBottom: 24,
        }}>
          <PrivacyItem
            title="Cero datos identificables"
            desc="Sin email, sin teléfono, sin documento, sin dirección IP persistente, sin ID de dispositivo del fabricante." />
          <PrivacyItem
            title="Anonimización diferencial"
            desc="El ruido estadístico se calibra en la ingesta — no después. Previene reconstrucción por correlación de queries." />
          <PrivacyItem
            title="K-anonymity ≥ 500"
            desc="Ninguna métrica agregada se publica si la celda de datos contiene menos de 500 respuestas. Si una región no alcanza, sube al nivel superior." />
          <PrivacyItem
            title="Auditoría externa anual"
            desc="Una firma independiente audita el pipeline completo. El reporte se publica íntegro, incluyendo cualquier hallazgo crítico." />
        </div>
        <div style={{
          padding: "16px 20px", borderRadius: 8,
          background: LIGHT.ink, color: "#fff",
          fontSize: 15, lineHeight: 1.6, fontStyle: "italic",
          fontFamily: "Source Serif Pro, Georgia, serif",
        }}>
          "Si nuestra base de datos completa se filtrara mañana, ningún
          ciudadano podría ser identificado por sus respuestas."
        </div>
      </section>

      {/* PROPOSITO */}
      <section style={{
        padding: "60px 7%", maxWidth: 1400, margin: "0 auto",
      }}>
        <div style={{
          padding: 40, borderRadius: 16,
          background: LIGHT.surfaceAlt, border: `1px solid ${LIGHT.border}`,
          borderLeft: `4px solid ${LIGHT.terracotta}`,
        }}>
          <div style={{ fontSize: 12, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 16 }}>
            Propósito
          </div>
          <p style={{
            fontSize: 22, lineHeight: 1.6, color: LIGHT.ink, margin: 0,
            fontFamily: "Source Serif Pro, Georgia, serif", fontStyle: "italic",
            maxWidth: 900,
          }}>
            "El voto informado no es el voto correcto. Es el voto consciente.
            Esa es la única corrección que una democracia debe perseguir."
          </p>
          <div style={{
            marginTop: 24, paddingTop: 24,
            borderTop: `1px solid ${LIGHT.border}`,
            display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 24,
          }}>
            <PurposeItem
              n="01"
              title="Reducir la asimetría"
              desc="Entre lo que los partidos saben de los votantes y lo que los votantes saben de los partidos."
            />
            <PurposeItem
              n="02"
              title="Comparar antes de elegir"
              desc="Vas a responder a veinte propuestas concretas sin saber a qué partido pertenecen. Al final vas a ver con qué agrupaciones coincidís realmente — y, frecuentemente, descubrir sorpresas."
            />
            <PurposeItem
              n="03"
              title="Reactivar el sentido del voto"
              desc="Cuando los ciudadanos comprueban que existen diferencias programáticas concretas entre las opciones, el voto vuelve a ser una decisión que importa."
            />
          </div>
        </div>
      </section>

      {/* MOCKUPS */}
      <section style={{
        padding: "80px 7%", maxWidth: 1400, margin: "0 auto",
        borderTop: `1px solid ${LIGHT.border}`,
      }}>
        <div style={{ marginBottom: 48, maxWidth: 760 }}>
          <div style={{ fontSize: 12, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
            Diseño para celulares
          </div>
          <h2 style={{ fontSize: 36, fontWeight: 800, margin: "0 0 16px",
            fontFamily: "Fraunces, serif", color: LIGHT.ink, letterSpacing: -1 }}>
            Una experiencia móvil sobria, sin gamificación
          </h2>
          <p style={{ fontSize: 17, color: LIGHT.inkSoft, lineHeight: 1.6, margin: 0 }}>
            Tres momentos del recorrido: bienvenida, quiz de afinidad sobre
            propuestas reales, devolución matizada con cinco coincidencias
            principales. Sin notificaciones push, sin rankings, sin scoring
            narrativo, sin algoritmo opaco.
          </p>
        </div>
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: 32, alignItems: "start", justifyItems: "center",
        }}>
          <PhoneFrame label="Bienvenida">
            <PhoneMockupWelcome compact />
          </PhoneFrame>
          <PhoneFrame label="Quiz · pregunta tipo">
            <PhoneMockupQuiz />
          </PhoneFrame>
          <PhoneFrame label="Resultado de afinidad">
            <PhoneMockupResult />
          </PhoneFrame>
        </div>
      </section>

      {/* DIEZ FUNCIONES */}
      <section style={{
        padding: "80px 7%", maxWidth: 1400, margin: "0 auto",
        borderTop: `1px solid ${LIGHT.border}`, background: LIGHT.bgAlt,
      }}>
        <div style={{ marginBottom: 40, maxWidth: 760 }}>
          <div style={{ fontSize: 12, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
            Las diez funciones
          </div>
          <h2 style={{ fontSize: 36, fontWeight: 800, margin: "0 0 16px",
            fontFamily: "Fraunces, serif", color: LIGHT.ink, letterSpacing: -1 }}>
            Una herramienta para cada momento del ciclo electoral
          </h2>
        </div>
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: 16,
        }}>
          {[
            ["01", "Mini Quiz de afinidad", "Veinte propuestas reales presentadas sin atribución partidaria."],
            ["02", "Plataformas partidarias", "Acceso curado a las plataformas oficiales con cita textual al documento original."],
            ["03", "Tus derechos cívicos", "Catálogo de derechos del elector con cita legal y fuente normativa."],
            ["04", "Cómo se vota", "Tutorial paso a paso del acto de votar, con audio guiado opcional."],
            ["05", "Verificación de padrón", "Consulta directa al padrón electoral oficial. Sin almacenamiento."],
            ["06", "Tu mesa de votación", "Localización geográfica de la mesa asignada con ruta sugerida."],
            ["07", "Glosario interactivo", "PASO, balotaje, padrón, fiscal, voto en blanco, justicia electoral."],
            ["08", "Línea de tiempo electoral", "Calendario completo del proceso, desde convocatoria hasta resultados."],
            ["09", "Mitos vs. hechos", "Fact-checking permanente contrastado con la legislación vigente."],
            ["10", "Diario cívico personal", "Notas privadas que viven solo en el dispositivo. Sin sincronización."],
          ].map(([n, title, desc]) => (
            <FunctionRow key={n} n={n} title={title} desc={desc} />
          ))}
        </div>
      </section>

      {/* DECISIONES METODOLOGICAS */}
      <section style={{
        padding: "80px 7%", maxWidth: 1200, margin: "0 auto",
      }}>
        <div style={{ marginBottom: 40, maxWidth: 820 }}>
          <div style={{ fontSize: 12, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
            Decisiones metodológicas
          </div>
          <h2 style={{ fontSize: 36, fontWeight: 800, margin: "0 0 16px",
            fontFamily: "Fraunces, serif", color: LIGHT.ink, letterSpacing: -1 }}>
            Qué hace a este proyecto distinto de un quiz de afinidad genérico
          </h2>
          <p style={{ fontSize: 16, color: LIGHT.inkSoft, lineHeight: 1.7, margin: 0 }}>
            Ocho definiciones de scope que respondieron a debates reales del
            equipo, agrupadas en tres bloques: modelo de datos, transparencia
            y alcance. Las explicitamos porque cambian el resultado de la app
            y porque cualquier observador externo debería poder cuestionarlas.
          </p>
        </div>

        {/* SUB-BLOQUE 1: Plataforma + trayectoria legislativa */}
        <div style={{
          padding: 32, borderRadius: 14,
          background: LIGHT.surface, border: `1px solid ${LIGHT.border}`,
          marginBottom: 20,
        }}>
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start",
            marginBottom: 20, flexWrap: "wrap" }}>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.terracottaBg, color: LIGHT.terracotta,
              fontSize: 11, fontWeight: 700, letterSpacing: 1.5,
              textTransform: "uppercase",
            }}>Decisión 01</div>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.bgAlt, color: LIGHT.inkSoft,
              fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
            }}>Plataforma + trayectoria</div>
          </div>
          <h3 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 16px",
            color: LIGHT.ink, fontFamily: "Fraunces, serif", letterSpacing: -0.5 }}>
            El partido no es solo lo que promete: también lo que vota
          </h3>
          <p style={{ fontSize: 15, color: LIGHT.inkSoft, lineHeight: 1.7, margin: "0 0 16px" }}>
            Una plataforma escrita es una hipótesis. Lo que cuenta es cómo
            votan los legisladores del partido cuando llega el momento de
            decidir. En América Latina, la distancia entre promesa de campaña
            y comportamiento en función es estructural — no anecdótica. Por eso
            Voto Informado cruza dos capas:
          </p>
          <div style={{
            display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16,
            marginBottom: 16,
          }} className="voto-twocol">
            <div style={{
              padding: 16, background: LIGHT.bgAlt, borderRadius: 8,
              border: `1px solid ${LIGHT.border}`,
            }}>
              <div style={{ fontSize: 11, color: LIGHT.terracotta, letterSpacing: 1.5,
                fontWeight: 700, textTransform: "uppercase", marginBottom: 6 }}>Capa A</div>
              <div style={{ fontSize: 14, fontWeight: 700, color: LIGHT.ink, marginBottom: 4 }}>
                Plataforma declarada
              </div>
              <div style={{ fontSize: 13, color: LIGHT.inkSoft, lineHeight: 1.55 }}>
                Las propuestas escritas para esta elección, presentadas ante
                la justicia electoral. Citables, verificables, hipotéticas.
              </div>
            </div>
            <div style={{
              padding: 16, background: LIGHT.bgAlt, borderRadius: 8,
              border: `1px solid ${LIGHT.border}`,
            }}>
              <div style={{ fontSize: 11, color: LIGHT.terracotta, letterSpacing: 1.5,
                fontWeight: 700, textTransform: "uppercase", marginBottom: 6 }}>Capa B</div>
              <div style={{ fontSize: 14, fontWeight: 700, color: LIGHT.ink, marginBottom: 4 }}>
                Trayectoria legislativa
              </div>
              <div style={{ fontSize: 13, color: LIGHT.inkSoft, lineHeight: 1.55 }}>
                Cómo votaron los legisladores del partido los últimos 4 años
                en temas equivalentes. Citables, verificables, fácticas.
              </div>
            </div>
          </div>
          <p style={{ fontSize: 14, color: LIGHT.inkSoft, lineHeight: 1.65, margin: 0,
            padding: "12px 14px", background: LIGHT.terracottaBg,
            border: `1px solid ${LIGHT.terracottaSoft}`, borderRadius: 8 }}>
            <strong style={{ color: LIGHT.terracotta }}>Coherencia visible.</strong>{" "}
            Cuando hay distancia entre ambas capas — un partido prometió X
            pero sus legisladores votaron Y — la app lo señala explícitamente.
            La rendición de cuentas deja de depender de la memoria del votante.
          </p>
        </div>

        {/* SUB-BLOQUE 2: 8 ejes */}
        <div style={{
          padding: 32, borderRadius: 14,
          background: LIGHT.surface, border: `1px solid ${LIGHT.border}`,
          marginBottom: 20,
        }}>
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start",
            marginBottom: 20, flexWrap: "wrap" }}>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.terracottaBg, color: LIGHT.terracotta,
              fontSize: 11, fontWeight: 700, letterSpacing: 1.5,
              textTransform: "uppercase",
            }}>Decisión 02</div>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.bgAlt, color: LIGHT.inkSoft,
              fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
            }}>8 ejes, no 7</div>
          </div>
          <h3 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 16px",
            color: LIGHT.ink, fontFamily: "Fraunces, serif", letterSpacing: -0.5 }}>
            La calidad democrática como eje propio, no como tema dentro de otros
          </h3>
          <p style={{ fontSize: 15, color: LIGHT.inkSoft, lineHeight: 1.7, margin: "0 0 20px" }}>
            Los quizzes cívicos suelen organizar el cuestionario por temas:
            economía, salud, seguridad, ambiente. Eso funciona en democracias
            estables. En contextos de erosión democrática — y en buena parte
            de América Latina lo estamos — lo que está en juego no es solo
            <em> qué políticas</em> se implementan, sino <em>bajo qué reglas
            del juego</em> se implementan. Por eso separamos el eje:
          </p>
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 10, marginBottom: 20,
          }}>
            {[
              ["Economía y trabajo", false],
              ["Salud y educación", false],
              ["Seguridad y justicia", false],
              ["Ambiente y energía", false],
              ["Derechos humanos", false],
              ["Reforma institucional", false],
              ["Política internacional", false],
              ["Calidad democrática procedimental", true],
            ].map(([label, isNew]) => (
              <div key={label} style={{
                padding: "12px 14px", borderRadius: 8,
                background: isNew ? LIGHT.terracottaBg : LIGHT.bgAlt,
                border: `1px solid ${isNew ? LIGHT.terracottaSoft : LIGHT.border}`,
                fontSize: 13, fontWeight: isNew ? 800 : 600,
                color: isNew ? LIGHT.terracotta : LIGHT.inkSoft,
                display: "flex", alignItems: "center", gap: 8,
              }}>
                {isNew && <span style={{ fontSize: 10, padding: "2px 6px",
                  background: LIGHT.terracotta, color: "#fff", borderRadius: 3,
                  letterSpacing: 0.5 }}>NUEVO</span>}
                {label}
              </div>
            ))}
          </div>
          <div style={{
            padding: 18, background: LIGHT.bgAlt, borderRadius: 8,
            border: `1px solid ${LIGHT.border}`,
          }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: LIGHT.ink, marginBottom: 10 }}>
              El eje de calidad democrática mide compromiso con:
            </div>
            <ul style={{ margin: 0, padding: 0, listStyle: "none",
              display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: 8 }}>
              {[
                "Separación de poderes",
                "Independencia judicial",
                "Libertad de prensa",
                "Reglas de alternancia y reelección",
                "Pluralismo en órganos de control",
                "Respeto a resultados electorales",
              ].map((item) => (
                <li key={item} style={{ fontSize: 13, color: LIGHT.inkSoft,
                  display: "flex", gap: 8, alignItems: "flex-start" }}>
                  <span style={{ color: LIGHT.terracotta, fontWeight: 700, flexShrink: 0 }}>·</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
          <p style={{ fontSize: 13.5, color: LIGHT.textMuted, lineHeight: 1.6,
            margin: "16px 0 0", fontStyle: "italic" }}>
            Cuando alguien deja de respetar las reglas del juego, las políticas
            sectoriales se vuelven secundarias. Por eso este eje no se distribuye
            entre los otros: tiene peso propio y el usuario lo pondera por separado.
          </p>
        </div>

        {/* SUB-BLOQUE 3: Tres entidades */}
        <div style={{
          padding: 32, borderRadius: 14,
          background: LIGHT.surface, border: `1px solid ${LIGHT.border}`,
        }}>
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start",
            marginBottom: 20, flexWrap: "wrap" }}>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.terracottaBg, color: LIGHT.terracotta,
              fontSize: 11, fontWeight: 700, letterSpacing: 1.5,
              textTransform: "uppercase",
            }}>Decisión 03</div>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.bgAlt, color: LIGHT.inkSoft,
              fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
            }}>Modelo de datos</div>
          </div>
          <h3 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 16px",
            color: LIGHT.ink, fontFamily: "Fraunces, serif", letterSpacing: -0.5 }}>
            Partido, candidato y lista son tres entidades distintas
          </h3>
          <p style={{ fontSize: 15, color: LIGHT.inkSoft, lineHeight: 1.7, margin: "0 0 20px" }}>
            En sistemas con voto preferencial, voto cruzado o listas abiertas
            (Brasil, Perú, parte de la región), el voto no va al "partido" sino
            a un candidato individual o a una lista. Decir solo "agrupación
            política" oscurece la decisión. Voto Informado separa las tres
            entidades:
          </p>
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: 12,
          }}>
            <EntityCard
              label="Partido"
              defn="La organización formal. Plataforma oficial, marca histórica, identidad ideológica declarada."
              ex="Frente Cívico Verde"
            />
            <EntityCard
              label="Candidato"
              defn="La persona en la boleta. Puede tener posiciones propias que difieren del partido. Antecedentes verificables."
              ex="María López — Senado · LP"
            />
            <EntityCard
              label="Lista"
              defn="La combinación específica de candidatos que un partido o coalición presenta en este distrito y elección."
              ex="Lista 158 — Cámara de Diputados"
            />
          </div>
          <p style={{ fontSize: 13.5, color: LIGHT.textMuted, lineHeight: 1.6,
            margin: "20px 0 0", fontStyle: "italic" }}>
            En la pantalla de resultados del quiz, si una propuesta es sostenida
            por el partido pero rechazada explícitamente por la candidata
            cabeza de lista, ambas posiciones se muestran. El usuario decide
            cuál pesa más.
          </p>
        </div>

        {/* GROUP HEADER · TRANSPARENCIA */}
        <div style={{ margin: "48px 0 20px", display: "flex",
          alignItems: "center", gap: 14 }}>
          <div style={{ flex: 1, height: 1, background: LIGHT.border }} />
          <div style={{
            fontSize: 11, color: LIGHT.terracotta, letterSpacing: 2.5,
            fontWeight: 700, textTransform: "uppercase",
            padding: "4px 12px", background: LIGHT.bg,
          }}>Transparencia y diseño</div>
          <div style={{ flex: 1, height: 1, background: LIGHT.border }} />
        </div>

        {/* SUB-BLOQUE 4: Sesgo afectivo */}
        <div style={{
          padding: 32, borderRadius: 14,
          background: LIGHT.surface, border: `1px solid ${LIGHT.border}`,
          marginBottom: 20,
        }}>
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start",
            marginBottom: 20, flexWrap: "wrap" }}>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.terracottaBg, color: LIGHT.terracotta,
              fontSize: 11, fontWeight: 700, letterSpacing: 1.5,
              textTransform: "uppercase",
            }}>Decisión 04</div>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.bgAlt, color: LIGHT.inkSoft,
              fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
            }}>Sesgo afectivo visible</div>
          </div>
          <h3 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 16px",
            color: LIGHT.ink, fontFamily: "Fraunces, serif", letterSpacing: -0.5 }}>
            Convertir el sesgo identitario en aprendizaje cívico
          </h3>
          <p style={{ fontSize: 15, color: LIGHT.inkSoft, lineHeight: 1.7, margin: "0 0 16px" }}>
            Cuando los votantes conocen la afiliación partidaria de una
            propuesta, su evaluación se contamina por su disposición previa
            hacia ese partido. El mismo enunciado se evalúa positivamente si
            se atribuye al partido propio y negativamente si se atribuye al
            rival. Esto está documentado en la literatura de psicología
            política contemporánea.
          </p>
          <p style={{ fontSize: 15, color: LIGHT.inkSoft, lineHeight: 1.7, margin: "0 0 16px" }}>
            En lugar de simplemente ocultar la atribución durante el quiz
            (que ya hacemos) y revelarla al final, agregamos una segunda
            pantalla opcional con esta pregunta:
          </p>
          <div style={{
            padding: 20, background: LIGHT.bgAlt, borderRadius: 8,
            border: `1px solid ${LIGHT.border}`,
            fontFamily: "Source Serif Pro, Georgia, serif", fontStyle: "italic",
            fontSize: 17, color: LIGHT.ink, lineHeight: 1.5, marginBottom: 16,
          }}>
            "Si hubieras sabido a qué partido pertenecía cada propuesta,
            ¿hubieras respondido distinto? Estas tres propuestas las marcaste
            con un grado de acuerdo distinto al promedio de respondentes con
            tu perfil ideológico declarado."
          </div>
          <p style={{ fontSize: 14, color: LIGHT.inkSoft, lineHeight: 1.65, margin: 0,
            padding: "12px 14px", background: LIGHT.terracottaBg,
            border: `1px solid ${LIGHT.terracottaSoft}`, borderRadius: 8 }}>
            <strong style={{ color: LIGHT.terracotta }}>No es humillación, es alfabetización.</strong>{" "}
            Hacer el sesgo visible explícitamente lo convierte en herramienta
            de auto-conocimiento, no en juicio. La feature es opcional y se
            puede saltear sin penalización en el flujo.
          </p>
        </div>

        {/* SUB-BLOQUE 5: Financiamiento + antecedentes */}
        <div style={{
          padding: 32, borderRadius: 14,
          background: LIGHT.surface, border: `1px solid ${LIGHT.border}`,
          marginBottom: 20,
        }}>
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start",
            marginBottom: 20, flexWrap: "wrap" }}>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.terracottaBg, color: LIGHT.terracotta,
              fontSize: 11, fontWeight: 700, letterSpacing: 1.5,
              textTransform: "uppercase",
            }}>Decisión 05</div>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.bgAlt, color: LIGHT.inkSoft,
              fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
            }}>Transparencia financiera y judicial</div>
          </div>
          <h3 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 16px",
            color: LIGHT.ink, fontFamily: "Fraunces, serif", letterSpacing: -0.5 }}>
            Lo que un partido recibe y arrastra es información pública —
            la hacemos accesible
          </h3>
          <p style={{ fontSize: 15, color: LIGHT.inkSoft, lineHeight: 1.7, margin: "0 0 20px" }}>
            Donantes registrados, gastos de campaña declarados, causas
            judiciales abiertas, declaraciones juradas patrimoniales,
            antecedentes empresariales. Toda esta información es pública en
            registros estatales pero queda invisibilizada en documentos densos
            y dispersos. Voto Informado la consolida en una vista por partido
            y por candidato, citando siempre la fuente oficial:
          </p>
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 12, marginBottom: 16,
          }}>
            <TransparencyLayer
              icon="💰"
              title="Financiamiento"
              desc="Donantes en últimas 2 campañas (con montos y fechas) + gastos declarados ante la justicia electoral."
            />
            <TransparencyLayer
              icon="⚖️"
              title="Antecedentes judiciales"
              desc="Causas penales y civiles vigentes con número de expediente y juzgado interviniente. Sin presunción de culpabilidad."
            />
            <TransparencyLayer
              icon="📋"
              title="Declaraciones juradas"
              desc="Patrimonio declarado al inicio y al final de cada mandato. Variación porcentual visible."
            />
          </div>
          <p style={{ fontSize: 13.5, color: LIGHT.textMuted, lineHeight: 1.6,
            margin: 0, fontStyle: "italic" }}>
            No reemplaza al periodismo de investigación: lo complementa con un
            punto de entrada estructurado para que el ciudadano común pueda
            mirar lo mismo que mira un periodista especializado.
          </p>
        </div>

        {/* SUB-BLOQUE 6: Propuestas no-falsables */}
        <div style={{
          padding: 32, borderRadius: 14,
          background: LIGHT.surface, border: `1px solid ${LIGHT.border}`,
          marginBottom: 20,
        }}>
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start",
            marginBottom: 20, flexWrap: "wrap" }}>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.terracottaBg, color: LIGHT.terracotta,
              fontSize: 11, fontWeight: 700, letterSpacing: 1.5,
              textTransform: "uppercase",
            }}>Decisión 06</div>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.bgAlt, color: LIGHT.inkSoft,
              fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
            }}>Calidad programática</div>
          </div>
          <h3 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 16px",
            color: LIGHT.ink, fontFamily: "Fraunces, serif", letterSpacing: -0.5 }}>
            No toda propuesta es operacionalizable. Lo señalamos.
          </h3>
          <p style={{ fontSize: 15, color: LIGHT.inkSoft, lineHeight: 1.7, margin: "0 0 20px" }}>
            Las plataformas usan a veces lenguaje retórico sin compromisos
            verificables: "promoveremos el desarrollo sustentable",
            "trabajaremos por la justicia social". Estas frases no son
            falsables — no se puede chequear si se cumplieron ni si se
            incumplieron. Voto Informado las identifica con un indicador
            visual y no las incluye en el quiz de afinidad.
          </p>
          <div style={{
            display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12,
            marginBottom: 16,
          }} className="voto-twocol">
            <div style={{
              padding: 16, background: "#f0f7f0", borderRadius: 8,
              border: `1px solid #bcd5bc`,
            }}>
              <div style={{ fontSize: 11, color: "#4a7c59", letterSpacing: 1.5,
                fontWeight: 700, textTransform: "uppercase", marginBottom: 6 }}>
                ✓ Operacionalizable
              </div>
              <div style={{ fontSize: 14, color: LIGHT.ink, lineHeight: 1.5,
                fontFamily: "Source Serif Pro, Georgia, serif", fontStyle: "italic" }}>
                "Crear un régimen impositivo simplificado para monotributistas
                y pymes con alícuota única del 12%."
              </div>
              <div style={{ fontSize: 12, color: "#5a8a6a", marginTop: 8 }}>
                Verificable: se hizo o no se hizo. Existe vara para evaluar
                cumplimiento.
              </div>
            </div>
            <div style={{
              padding: 16, background: LIGHT.bgAlt, borderRadius: 8,
              border: `1px solid ${LIGHT.borderStrong}`,
            }}>
              <div style={{ fontSize: 11, color: LIGHT.textMuted, letterSpacing: 1.5,
                fontWeight: 700, textTransform: "uppercase", marginBottom: 6 }}>
                ⚠ No-falsable
              </div>
              <div style={{ fontSize: 14, color: LIGHT.ink, lineHeight: 1.5,
                fontFamily: "Source Serif Pro, Georgia, serif", fontStyle: "italic" }}>
                "Promoveremos el crecimiento económico sostenible y la
                inclusión social."
              </div>
              <div style={{ fontSize: 12, color: LIGHT.textMuted, marginTop: 8 }}>
                No hay vara. Cualquier gestión puede declararse cumplidora
                de esta promesa.
              </div>
            </div>
          </div>
          <p style={{ fontSize: 13.5, color: LIGHT.textMuted, lineHeight: 1.6,
            margin: 0, fontStyle: "italic" }}>
            Es alfabetización cívica: enseña a distinguir entre propuesta y
            retórica. Los partidos pueden replicar — y publicamos sus
            replicas — pero no negociamos la distinción.
          </p>
        </div>

        {/* GROUP HEADER · ALCANCE */}
        <div style={{ margin: "48px 0 20px", display: "flex",
          alignItems: "center", gap: 14 }}>
          <div style={{ flex: 1, height: 1, background: LIGHT.border }} />
          <div style={{
            fontSize: 11, color: LIGHT.terracotta, letterSpacing: 2.5,
            fontWeight: 700, textTransform: "uppercase",
            padding: "4px 12px", background: LIGHT.bg,
          }}>Alcance</div>
          <div style={{ flex: 1, height: 1, background: LIGHT.border }} />
        </div>

        {/* SUB-BLOQUE 7: Multilingüismo */}
        <div style={{
          padding: 32, borderRadius: 14,
          background: LIGHT.surface, border: `1px solid ${LIGHT.border}`,
          marginBottom: 20,
        }}>
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start",
            marginBottom: 20, flexWrap: "wrap" }}>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.terracottaBg, color: LIGHT.terracotta,
              fontSize: 11, fontWeight: 700, letterSpacing: 1.5,
              textTransform: "uppercase",
            }}>Decisión 07</div>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.bgAlt, color: LIGHT.inkSoft,
              fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
            }}>Multilingüismo desde el lanzamiento</div>
          </div>
          <h3 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 16px",
            color: LIGHT.ink, fontFamily: "Fraunces, serif", letterSpacing: -0.5 }}>
            Lenguas originarias como derecho, no como feature opcional
          </h3>
          <p style={{ fontSize: 15, color: LIGHT.inkSoft, lineHeight: 1.7, margin: "0 0 20px" }}>
            El voto informado en lenguas originarias está protegido por el
            <strong> Convenio 169 OIT</strong> y por la <strong>Declaración
            de Naciones Unidas sobre los Derechos de los Pueblos Indígenas</strong>.
            Voto Informado se compromete a entregar la app en las lenguas
            oficialmente reconocidas de cada país desde el lanzamiento — no
            como agregado posterior cuando "haya recursos".
          </p>
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: 10, marginBottom: 16,
          }}>
            {[
              ["Perú", "Quechua · Aymara"],
              ["Bolivia", "Quechua · Aymara · Guaraní"],
              ["Paraguay", "Guaraní (cooficial)"],
              ["México", "Náhuatl · Maya · Mixteco · Zapoteco"],
              ["Guatemala", "K'iche' · Q'eqchi' · Mam · Kaqchikel"],
              ["Ecuador", "Quichua · Shuar"],
            ].map(([country, langs]) => (
              <div key={country} style={{
                padding: "12px 14px", borderRadius: 8,
                background: LIGHT.bgAlt, border: `1px solid ${LIGHT.border}`,
              }}>
                <div style={{ fontSize: 13, fontWeight: 800, color: LIGHT.ink,
                  marginBottom: 4 }}>{country}</div>
                <div style={{ fontSize: 12, color: LIGHT.inkSoft,
                  fontFamily: "DM Mono, ui-monospace, monospace" }}>{langs}</div>
              </div>
            ))}
          </div>
          <p style={{ fontSize: 13.5, color: LIGHT.textMuted, lineHeight: 1.6,
            margin: 0, fontStyle: "italic" }}>
            "Un derecho que no se ejerce en la lengua del titular es un
            derecho que no se ejerce plenamente." La traducción es realizada
            en colaboración con organizaciones de cada comunidad lingüística,
            no por servicios automatizados.
          </p>
        </div>

        {/* SUB-BLOQUE 8: Ciclo electoral completo */}
        <div style={{
          padding: 32, borderRadius: 14,
          background: LIGHT.surface, border: `1px solid ${LIGHT.border}`,
        }}>
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start",
            marginBottom: 20, flexWrap: "wrap" }}>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.terracottaBg, color: LIGHT.terracotta,
              fontSize: 11, fontWeight: 700, letterSpacing: 1.5,
              textTransform: "uppercase",
            }}>Decisión 08</div>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.bgAlt, color: LIGHT.inkSoft,
              fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
            }}>Ciclo electoral completo</div>
          </div>
          <h3 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 16px",
            color: LIGHT.ink, fontFamily: "Fraunces, serif", letterSpacing: -0.5 }}>
            Más que presidenciales: legislativas, municipales y consultas
          </h3>
          <p style={{ fontSize: 15, color: LIGHT.inkSoft, lineHeight: 1.7, margin: "0 0 20px" }}>
            La atención mediática se concentra en presidenciales, pero la
            mayoría de las decisiones que afectan al ciudadano se toman en
            legislativas, municipales y referéndums. Voto Informado tiene
            arquitectura para soportar las cuatro categorías, cada una con
            su lógica propia:
          </p>
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 12,
          }}>
            <ElectionTypeCard
              n="01"
              title="Presidencial"
              desc="Candidato único por boleta. Quiz sobre plataforma del partido + posiciones del candidato."
            />
            <ElectionTypeCard
              n="02"
              title="Legislativa"
              desc="Lista + candidatos individuales. Quiz + análisis de divergencia entre partido y cabeza de lista."
            />
            <ElectionTypeCard
              n="03"
              title="Municipal"
              desc="Candidato + plataforma local. Quiz adaptado a competencias municipales (no nacionales)."
            />
            <ElectionTypeCard
              n="04"
              title="Referéndum / Consulta"
              desc="Pregunta única. Análisis de implicancias jurídicas y precedentes antes de votar."
            />
          </div>
          <p style={{ fontSize: 13.5, color: LIGHT.textMuted, lineHeight: 1.6,
            margin: "20px 0 0", fontStyle: "italic" }}>
            Una elección sin entender qué se está decidiendo no es una
            elección informada. Las consultas populares son las más
            invisibilizadas y, paradójicamente, las más vinculantes.
          </p>
        </div>

        {/* GROUP HEADER · OPERACIÓN INTERNA */}
        <div style={{ margin: "48px 0 20px", display: "flex",
          alignItems: "center", gap: 14 }}>
          <div style={{ flex: 1, height: 1, background: LIGHT.border }} />
          <div style={{
            fontSize: 11, color: LIGHT.terracotta, letterSpacing: 2.5,
            fontWeight: 700, textTransform: "uppercase",
            padding: "4px 12px", background: LIGHT.bg,
          }}>Operación interna</div>
          <div style={{ flex: 1, height: 1, background: LIGHT.border }} />
        </div>

        {/* SUB-BLOQUE 9: Acceso interno operativo */}
        <div style={{
          padding: 32, borderRadius: 14,
          background: LIGHT.surface, border: `1px solid ${LIGHT.border}`,
        }}>
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start",
            marginBottom: 20, flexWrap: "wrap" }}>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.terracottaBg, color: LIGHT.terracotta,
              fontSize: 11, fontWeight: 700, letterSpacing: 1.5,
              textTransform: "uppercase",
            }}>Decisión 09</div>
            <div style={{
              padding: "4px 10px", borderRadius: 6,
              background: LIGHT.bgAlt, color: LIGHT.inkSoft,
              fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
            }}>Acceso interno · Nivel A</div>
          </div>
          <h3 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 16px",
            color: LIGHT.ink, fontFamily: "Fraunces, serif", letterSpacing: -0.5 }}>
            Lo que el equipo puede ver es lo mismo que cualquier auditor externo puede ver
          </h3>
          <p style={{ fontSize: 15, color: LIGHT.inkSoft, lineHeight: 1.7, margin: "0 0 16px" }}>
            Toda app necesita un dashboard operativo interno para detectar
            bugs, abusos del sistema y decisiones de producto. La pregunta
            ética no es <em>si</em> existe, sino <em>qué ve</em>. Voto
            Informado adopta la regla más estricta posible: el equipo accede
            exclusivamente a métricas operativas y a los mismos agregados
            públicos que cualquier ciudadano. Nada político-sensible que no
            sea simultáneamente auditable por un tercero.
          </p>
          <div style={{
            display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12,
            marginBottom: 16,
          }} className="voto-twocol">
            <div style={{
              padding: 16, background: "#f0f7f0", borderRadius: 8,
              border: `1px solid #bcd5bc`,
            }}>
              <div style={{ fontSize: 11, color: "#4a7c59", letterSpacing: 1.5,
                fontWeight: 700, textTransform: "uppercase", marginBottom: 8 }}>
                ✓ Lo que el equipo ve
              </div>
              <ul style={{ margin: 0, padding: 0, listStyle: "none",
                display: "grid", gap: 6 }}>
                {[
                  "Tasa de finalización del quiz",
                  "Distribución por modo y lengua",
                  "Crashes por versión / plataforma",
                  "Embudo de abandono por pregunta",
                  "Anomalías de tráfico (anti-spam)",
                  "Agregados públicos antes del freeze pre-electoral",
                ].map((it) => (
                  <li key={it} style={{ fontSize: 13, color: LIGHT.ink,
                    lineHeight: 1.5, display: "flex", gap: 8 }}>
                    <span style={{ color: "#4a7c59" }}>·</span>
                    <span>{it}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div style={{
              padding: 16, background: "#fdecec", borderRadius: 8,
              border: `1px solid #f5b8b8`,
            }}>
              <div style={{ fontSize: 11, color: "#a02828", letterSpacing: 1.5,
                fontWeight: 700, textTransform: "uppercase", marginBottom: 8 }}>
                ✗ Lo que el equipo no ve
              </div>
              <ul style={{ margin: 0, padding: 0, listStyle: "none",
                display: "grid", gap: 6 }}>
                {[
                  "Respuestas individuales de ningún usuario",
                  "Datos personales identificables (no se capturan)",
                  "Cortes geográficos por debajo de k-anonymity = 500",
                  "Afinidad por distritos pequeños o franjas etarias",
                  "Información política-sensible no auditable",
                  "Datos en bruto de la tabla de eventos",
                ].map((it) => (
                  <li key={it} style={{ fontSize: 13, color: LIGHT.ink,
                    lineHeight: 1.5, display: "flex", gap: 8 }}>
                    <span style={{ color: "#a02828" }}>·</span>
                    <span>{it}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div style={{
            padding: 18, background: LIGHT.bgAlt, borderRadius: 8,
            border: `1px solid ${LIGHT.border}`, marginBottom: 16,
          }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: LIGHT.ink, marginBottom: 10 }}>
              Garantías técnicas de la asimetría declarada:
            </div>
            <ul style={{ margin: 0, padding: 0, listStyle: "none",
              display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
              gap: 10 }}>
              {[
                ["Separación física de bases", "El admin solo lee tablas materializadas con k-anon ya aplicado. La tabla de eventos crudos es inaccesible."],
                ["Audit log inmutable", "Cada consulta del admin queda registrada con timestamp y query. Disponible para auditoría externa."],
                ["MFA obligatorio + IP allowlist", "Acceso protegido con segundo factor. Sin sesiones persistentes."],
                ["Scope declarado y publicado", "El catálogo de métricas operativas es público en el repositorio open-source."],
              ].map(([t, d]) => (
                <li key={t} style={{ fontSize: 13, color: LIGHT.inkSoft, lineHeight: 1.55 }}>
                  <strong style={{ color: LIGHT.ink }}>{t}.</strong> {d}
                </li>
              ))}
            </ul>
          </div>
          <p style={{ fontSize: 14, color: LIGHT.inkSoft, lineHeight: 1.65, margin: 0,
            padding: "12px 14px", background: LIGHT.terracottaBg,
            border: `1px solid ${LIGHT.terracottaSoft}`, borderRadius: 8 }}>
            <strong style={{ color: LIGHT.terracotta }}>Asimetría declarada, no oculta.</strong>{" "}
            Lo que el equipo ve es exactamente lo que cualquier auditor
            externo podría revisar.
          </p>
        </div>
      </section>

      {/* APARTIDISMO */}
      <section style={{
        padding: "80px 7%", maxWidth: 1100, margin: "0 auto",
      }}>
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 12, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
            La promesa apartidaria
          </div>
          <h2 style={{ fontSize: 36, fontWeight: 800, margin: "0 0 24px",
            fontFamily: "Fraunces, serif", color: LIGHT.ink, letterSpacing: -1 }}>
            Trazabilidad como antídoto al sesgo
          </h2>
          <p style={{ fontSize: 17, color: LIGHT.inkSoft, lineHeight: 1.7, margin: 0,
            maxWidth: 820 }}>
            El apartidismo no es una afirmación que se hace. Es una propiedad
            que se construye con mecanismos verificables. Cinco compromisos
            arquitectónicos que cualquier observador externo puede
            inspeccionar:
          </p>
        </div>
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: 20,
        }}>
          <CommitmentCard n="01" title="Cita literal verificable"
            desc="Cada propuesta cita textualmente la plataforma oficial del partido, con referencia exacta al capítulo y artículo." />
          <CommitmentCard n="02" title="Sub-comité de ética externo"
            desc="El cuestionario es aprobado antes de cada elección por tres expertos sin afiliación partidaria. Acta pública." />
          <CommitmentCard n="03" title="Algoritmo abierto"
            desc="La fórmula de scoring es de código abierto, reproducible. Cualquier desarrollador puede verificar el cálculo." />
          <CommitmentCard n="04" title="Test de balance por release"
            desc="Antes de publicar, se ejecuta una simulación contra cada plataforma. Si un partido obtiene puntaje sesgado, se rebalancea." />
          <CommitmentCard n="05" title="Sin financiamiento partidario"
            desc="No aceptamos dinero de partidos, candidatos, fundaciones partidarias ni organismos vinculados a actores en contienda." />
        </div>
      </section>

      {/* DERECHOS QUE PROTEGE */}
      <section style={{
        padding: "80px 7%", maxWidth: 1200, margin: "0 auto",
        borderTop: `1px solid ${LIGHT.border}`,
      }}>
        <div style={{ marginBottom: 40, maxWidth: 820 }}>
          <div style={{ fontSize: 12, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
            Marco normativo
          </div>
          <h2 style={{ fontSize: 36, fontWeight: 800, margin: "0 0 20px",
            fontFamily: "Fraunces, serif", color: LIGHT.ink, letterSpacing: -1 }}>
            Derechos civiles y políticos que materializa
          </h2>
          <p style={{ fontSize: 17, color: LIGHT.inkSoft, lineHeight: 1.7, margin: 0 }}>
            Voto Informado no inventa derechos: hace operativos derechos ya
            reconocidos en el sistema interamericano y universal de derechos
            humanos. Cada función responde a una obligación convencional
            concreta. El derecho al voto sin información disponible es un
            derecho formal vacío — esta herramienta busca que deje de serlo.
          </p>
        </div>

        {/* Derechos directos */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 11, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 14 }}>
            Derechos directamente protegidos
          </div>
          <div style={{
            background: LIGHT.surface, borderRadius: 12,
            border: `1px solid ${LIGHT.border}`, overflow: "hidden",
          }}>
            {[
              ["Voto informado y elecciones auténticas",
                "Condición material del derecho al voto: una elección sin información disponible no es 'auténtica' en sentido convencional.",
                "Art. 23 CADH · Art. 25 PIDCP"],
              ["Acceso a información pública",
                "La aplicación hace accesible información que ya es pública pero está dispersa en documentos densos.",
                "Art. 13 CADH · Claude Reyes vs. Chile (Corte IDH, 2006)"],
              ["Libertad de pensamiento y expresión política",
                "La libertad de formarse una opinión política presupone acceso a información plural y comparable.",
                "Art. 13 CADH · Art. 19 PIDCP"],
              ["Privacidad y protección de datos personales",
                "Anonimización diferencial con ruido calibrado en captura. Sin recolección de datos identificables.",
                "Art. 11 CADH · Art. 17 PIDCP"],
              ["Secreto del voto",
                "La app no captura datos identificables ni el voto efectivo. Solo coincidencia programática.",
                "Derivado del Art. 23 CADH"],
              ["Igualdad material en participación política",
                "Diseño universal y modo inclusivo cumplen la igualdad sustantiva, no solo formal.",
                "Arts. 1 y 24 CADH"],
            ].map(([title, desc, cite], idx, arr) => (
              <RightRow key={title} title={title} desc={desc} cite={cite}
                last={idx === arr.length - 1} />
            ))}
          </div>
        </div>

        {/* Efectos sistémicos */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 11, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 14 }}>
            Derechos indirectamente fortalecidos (efectos sistémicos)
          </div>
          <div style={{
            background: LIGHT.surface, borderRadius: 12,
            border: `1px solid ${LIGHT.border}`, overflow: "hidden",
          }}>
            {[
              ["Rendición de cuentas",
                "La cita-fuente verificable convierte las plataformas en compromisos auditables ex-post.",
                "Principio derivado · IDEA Internacional · OEA"],
              ["Pluralismo y competencia partidaria",
                "Comparación estructurada fortalece la competencia programática frente a la competencia puramente identitaria.",
                "Art. 16 CADH · Art. 22 PIDCP"],
              ["Participación de personas con discapacidad",
                "El modo inclusivo (WCAG 2.2 AA) cumple la obligación convencional de garantizar accesibilidad electoral.",
                "Art. 29 CDPD"],
              ["Participación política de pueblos indígenas",
                "El multilingüismo previsto (Quechua, Aymara, Guaraní, lenguas originarias) materializa este derecho.",
                "Convenio 169 OIT · Declaración ONU sobre Pueblos Indígenas"],
            ].map(([title, desc, cite], idx, arr) => (
              <RightRow key={title} title={title} desc={desc} cite={cite}
                last={idx === arr.length - 1} />
            ))}
          </div>
        </div>

        {/* Riesgos mitigados */}
        <div style={{
          padding: 24, borderRadius: 12,
          background: LIGHT.surfaceAlt, border: `1px solid ${LIGHT.border}`,
          borderLeft: `4px solid ${LIGHT.terracotta}`,
        }}>
          <div style={{ fontSize: 11, color: LIGHT.terracotta, letterSpacing: 2,
            textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
            Riesgos democráticos que mitiga
          </div>
          <ul style={{ margin: 0, padding: 0, listStyle: "none",
            display: "grid", gap: 10 }}>
            <li style={{ fontSize: 14, color: LIGHT.inkSoft, lineHeight: 1.6,
              display: "flex", gap: 10 }}>
              <span style={{ color: LIGHT.terracotta, fontWeight: 700 }}>·</span>
              <span><strong style={{ color: LIGHT.ink }}>Desinformación electoral</strong> —
                atenta contra el carácter "auténtico" de la elección exigido por el Art. 23.1 CADH.</span>
            </li>
            <li style={{ fontSize: 14, color: LIGHT.inkSoft, lineHeight: 1.6,
              display: "flex", gap: 10 }}>
              <span style={{ color: LIGHT.terracotta, fontWeight: 700 }}>·</span>
              <span><strong style={{ color: LIGHT.ink }}>Polarización afectiva</strong> —
                cuando los votantes rechazan al adversario por identidad grupal y no por desacuerdo programático real, el pluralismo se erosiona.</span>
            </li>
            <li style={{ fontSize: 14, color: LIGHT.inkSoft, lineHeight: 1.6,
              display: "flex", gap: 10 }}>
              <span style={{ color: LIGHT.terracotta, fontWeight: 700 }}>·</span>
              <span><strong style={{ color: LIGHT.ink }}>Captura algorítmica de la agenda</strong> —
                las plataformas digitales optimizan el conflicto sobre la deliberación. Voto Informado opera en sentido contrario.</span>
            </li>
          </ul>
        </div>
      </section>

      {/* CIERRE */}
      <section style={{
        padding: "60px 7%", maxWidth: 1400, margin: "0 auto",
      }}>
        <div style={{
          padding: 48, borderRadius: 16,
          background: LIGHT.ink, color: "#fff",
          textAlign: "center",
        }}>
          <p style={{
            fontSize: 32, lineHeight: 1.4, margin: "0 0 12px",
            fontFamily: "Fraunces, Georgia, serif", fontStyle: "italic",
            color: LIGHT.terracottaSoft, fontWeight: 300,
          }}>
            "Saber antes de elegir."
          </p>
          <p style={{
            fontSize: 15, color: "#e5dcd0", margin: 0, maxWidth: 640,
            marginLeft: "auto", marginRight: "auto", lineHeight: 1.7,
          }}>
            Una promesa modesta. Pero la democracia no se sostiene de
            promesas grandes — se sostiene de instrumentos que funcionan.
            Voto Informado es uno de esos instrumentos.
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
          <span>Voto Informado · un proyecto de Democrac.IA</span>
        </div>
        <button onClick={onBack} style={{
          background: "transparent", border: "none", color: LIGHT.textMuted,
          cursor: "pointer", fontSize: 13, padding: 0,
        }}>← Volver al sitio principal</button>
      </footer>
    </div>
  );
}

function PurposeItem({ n, title, desc }) {
  return (
    <div>
      <div style={{
        fontSize: 11, color: LIGHT.terracotta, letterSpacing: 2,
        fontWeight: 700, marginBottom: 6, fontFamily: "Fraunces, serif",
      }}>{n}</div>
      <h4 style={{ fontSize: 16, fontWeight: 800, margin: "0 0 6px", color: LIGHT.ink }}>{title}</h4>
      <p style={{ fontSize: 14, color: LIGHT.inkSoft, margin: 0, lineHeight: 1.6 }}>{desc}</p>
    </div>
  );
}

function FunctionRow({ n, title, desc }) {
  return (
    <div style={{
      padding: 20, background: LIGHT.surface, borderRadius: 10,
      border: `1px solid ${LIGHT.border}`,
      display: "flex", gap: 14, alignItems: "flex-start",
    }}>
      <div style={{
        fontFamily: "Fraunces, Georgia, serif", fontSize: 22,
        fontWeight: 700, color: LIGHT.terracotta, lineHeight: 1,
        minWidth: 32, fontStyle: "italic",
      }}>{n}</div>
      <div>
        <h4 style={{ fontSize: 15, fontWeight: 800, margin: "0 0 4px", color: LIGHT.ink }}>{title}</h4>
        <p style={{ fontSize: 13, color: LIGHT.inkSoft, margin: 0, lineHeight: 1.5 }}>{desc}</p>
      </div>
    </div>
  );
}

function TransparencyLayer({ icon, title, desc }) {
  return (
    <div style={{
      padding: 18, borderRadius: 10,
      background: LIGHT.bgAlt, border: `1px solid ${LIGHT.border}`,
    }}>
      <div style={{ fontSize: 26, marginBottom: 8 }}>{icon}</div>
      <div style={{ fontSize: 14, fontWeight: 800, color: LIGHT.ink,
        marginBottom: 6 }}>{title}</div>
      <div style={{ fontSize: 13, color: LIGHT.inkSoft, lineHeight: 1.55 }}>
        {desc}
      </div>
    </div>
  );
}

function ElectionTypeCard({ n, title, desc }) {
  return (
    <div style={{
      padding: 18, borderRadius: 10,
      background: LIGHT.bgAlt, border: `1px solid ${LIGHT.border}`,
      display: "flex", flexDirection: "column", gap: 8,
    }}>
      <div style={{
        fontSize: 11, color: LIGHT.terracotta, letterSpacing: 1.5,
        fontWeight: 700, fontFamily: "Fraunces, Georgia, serif",
        fontStyle: "italic",
      }}>{n}</div>
      <div style={{ fontSize: 14, fontWeight: 800, color: LIGHT.ink }}>
        {title}
      </div>
      <div style={{ fontSize: 13, color: LIGHT.inkSoft, lineHeight: 1.55 }}>
        {desc}
      </div>
    </div>
  );
}

function EntityCard({ label, defn, ex }) {
  return (
    <div style={{
      padding: 18, borderRadius: 10,
      background: LIGHT.bgAlt, border: `1px solid ${LIGHT.border}`,
      display: "flex", flexDirection: "column", gap: 10,
    }}>
      <div style={{
        fontSize: 11, color: LIGHT.terracotta, letterSpacing: 2,
        fontWeight: 700, textTransform: "uppercase",
      }}>{label}</div>
      <div style={{ fontSize: 13, color: LIGHT.inkSoft, lineHeight: 1.55, flex: 1 }}>
        {defn}
      </div>
      <div style={{
        fontSize: 12, color: LIGHT.ink, fontWeight: 600,
        fontFamily: "DM Mono, ui-monospace, monospace",
        padding: "8px 10px", background: LIGHT.surface,
        border: `1px solid ${LIGHT.border}`, borderRadius: 6,
      }}>
        ej. {ex}
      </div>
    </div>
  );
}

function PrivacyItem({ title, desc }) {
  return (
    <div style={{
      padding: 18, background: LIGHT.surface, borderRadius: 10,
      border: `1px solid ${LIGHT.border}`,
    }}>
      <h4 style={{ fontSize: 14, fontWeight: 800, margin: "0 0 6px", color: LIGHT.ink,
        display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{
          display: "inline-block", width: 6, height: 6, borderRadius: 3,
          background: LIGHT.terracotta,
        }} />
        {title}
      </h4>
      <p style={{ fontSize: 13, color: LIGHT.inkSoft, margin: 0, lineHeight: 1.55 }}>{desc}</p>
    </div>
  );
}

function RightRow({ title, desc, cite, last }) {
  return (
    <div style={{
      padding: "18px 22px",
      borderBottom: last ? "none" : `1px solid ${LIGHT.border}`,
      display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 24,
      alignItems: "start",
    }} className="right-row">
      <div>
        <h4 style={{ fontSize: 15, fontWeight: 800, margin: "0 0 6px", color: LIGHT.ink }}>
          {title}
        </h4>
        <p style={{ fontSize: 13.5, color: LIGHT.inkSoft, margin: 0, lineHeight: 1.55 }}>
          {desc}
        </p>
      </div>
      <div style={{
        fontSize: 12, color: LIGHT.terracotta, fontWeight: 700,
        letterSpacing: 0.3, fontFamily: "DM Mono, ui-monospace, monospace",
        lineHeight: 1.5, paddingTop: 2,
      }}>
        {cite}
      </div>
    </div>
  );
}

function CommitmentCard({ n, title, desc }) {
  return (
    <div style={{
      padding: 24, background: LIGHT.surface, borderRadius: 12,
      border: `1px solid ${LIGHT.border}`,
      boxShadow: "0 2px 8px rgba(28, 34, 48, 0.04)",
    }}>
      <div style={{
        fontSize: 11, color: LIGHT.terracotta, letterSpacing: 2,
        fontWeight: 700, marginBottom: 8,
      }}>{n}</div>
      <h4 style={{ fontSize: 16, fontWeight: 800, margin: "0 0 8px", color: LIGHT.ink }}>{title}</h4>
      <p style={{ fontSize: 13.5, color: LIGHT.inkSoft, margin: 0, lineHeight: 1.6 }}>{desc}</p>
    </div>
  );
}

// ── Phone mockups ─────────────────────────────────────────────────────
function PhoneFrame({ label, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{
        width: 260, height: 540, borderRadius: 36,
        background: LIGHT.ink, padding: 14,
        boxShadow: "0 18px 50px rgba(28, 34, 48, 0.18)",
        position: "relative",
      }}>
        <div style={{
          position: "absolute", top: 8, left: "50%", transform: "translateX(-50%)",
          width: 90, height: 6, borderRadius: 4, background: "#2a3247",
        }} />
        <div style={{
          width: "100%", height: "100%", borderRadius: 24,
          background: LIGHT.surface, overflow: "hidden", position: "relative",
        }}>
          {children}
        </div>
      </div>
      {label && (
        <div style={{
          marginTop: 14, fontSize: 12, color: LIGHT.textMuted,
          fontStyle: "italic", fontFamily: "Source Serif Pro, Georgia, serif",
        }}>{label}</div>
      )}
    </div>
  );
}

function PhoneMockupWelcome({ compact = false }) {
  if (compact) {
    return (
      <div style={{
        padding: "32px 20px", height: "100%",
        background: LIGHT.ink, color: "#fff",
        display: "flex", flexDirection: "column",
        justifyContent: "space-between",
      }}>
        <div style={{
          fontSize: 10, letterSpacing: 2, fontWeight: 700,
          color: LIGHT.terracottaSoft, textTransform: "uppercase",
        }}>Democrac.IA</div>
        <div>
          <div style={{
            fontSize: 30, fontWeight: 900, lineHeight: 1, letterSpacing: -1.5,
            fontFamily: "Fraunces, Georgia, serif", marginBottom: 16,
          }}>
            voto<span style={{ color: LIGHT.terracotta }}>.</span>informado
          </div>
          <div style={{
            fontFamily: "Source Serif Pro, Georgia, serif",
            fontStyle: "italic", fontSize: 13, color: "#cdd3dd", marginBottom: 24,
          }}>
            "Saber antes de elegir."
          </div>
          <button style={{
            width: "100%", padding: "12px", borderRadius: 8, border: "none",
            background: LIGHT.terracotta, color: "#fff",
            fontSize: 13, fontWeight: 700, cursor: "pointer",
          }}>Empezá →</button>
          <div style={{
            textAlign: "center", marginTop: 14, fontSize: 11,
            color: "#8b94a3", letterSpacing: 0.5,
          }}>anónima · gratuita</div>
        </div>
        <div />
      </div>
    );
  }
  return (
    <PhoneFrame>
      <div style={{
        padding: "40px 24px", height: "100%",
        background: LIGHT.ink, color: "#fff",
        display: "flex", flexDirection: "column",
      }}>
        <div style={{
          fontSize: 10, letterSpacing: 2, fontWeight: 700,
          color: LIGHT.terracottaSoft, textTransform: "uppercase",
          marginBottom: 80,
        }}>Democrac.IA</div>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: 36, fontWeight: 900, lineHeight: 1, letterSpacing: -1.5,
            fontFamily: "Fraunces, Georgia, serif", marginBottom: 20,
          }}>
            voto<span style={{ color: LIGHT.terracotta }}>.</span>informado
          </div>
          <div style={{
            fontFamily: "Source Serif Pro, Georgia, serif",
            fontStyle: "italic", fontSize: 15, color: "#cdd3dd", marginBottom: 32,
          }}>
            "Saber antes de elegir."
          </div>
          <button style={{
            width: "100%", padding: "14px", borderRadius: 8, border: "none",
            background: LIGHT.terracotta, color: "#fff",
            fontSize: 14, fontWeight: 700, cursor: "pointer",
          }}>Empezá →</button>
          <div style={{
            textAlign: "center", marginTop: 16, fontSize: 12,
            color: "#8b94a3", letterSpacing: 0.5,
          }}>anónima · gratuita</div>
        </div>
      </div>
    </PhoneFrame>
  );
}

function PhoneMockupQuiz() {
  return (
    <div style={{
      padding: "18px 18px", height: "100%", background: LIGHT.surface,
      display: "flex", flexDirection: "column",
    }}>
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        fontSize: 11, color: LIGHT.textMuted, fontWeight: 600, marginBottom: 8,
      }}>
        <span>×</span>
        <span>4 de 20</span>
      </div>
      <div style={{
        height: 3, background: LIGHT.border, borderRadius: 2, marginBottom: 18,
        overflow: "hidden",
      }}>
        <div style={{ height: "100%", width: "20%", background: LIGHT.terracotta }} />
      </div>
      <div style={{
        fontSize: 10, letterSpacing: 1.5, fontWeight: 700,
        color: LIGHT.terracotta, textTransform: "uppercase", marginBottom: 14,
      }}>📊 Economía</div>
      <div style={{
        padding: 14, background: LIGHT.surfaceAlt, borderRadius: 10,
        border: `1px solid ${LIGHT.border}`, marginBottom: 16,
      }}>
        <div style={{
          fontSize: 9, color: LIGHT.textMuted, letterSpacing: 1, fontWeight: 700,
          textTransform: "uppercase", marginBottom: 6,
        }}>Propuesta · plataforma oficial</div>
        <div style={{ fontSize: 13, color: LIGHT.ink, lineHeight: 1.4, fontWeight: 500 }}>
          Crear un régimen impositivo simplificado para monotributistas y pymes.
        </div>
      </div>
      <div style={{
        fontSize: 11, color: LIGHT.textMuted, textAlign: "center", marginBottom: 12,
      }}>¿Cuán de acuerdo estás?</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        <div style={{
          padding: "11px 14px", borderRadius: 8,
          border: `2px solid ${LIGHT.terracotta}`,
          fontSize: 12, color: LIGHT.terracotta, fontWeight: 700, textAlign: "center",
        }}>Muy de acuerdo</div>
        <div style={{
          padding: "11px 14px", borderRadius: 8,
          border: `1px solid ${LIGHT.border}`,
          fontSize: 12, color: LIGHT.inkSoft, textAlign: "center",
        }}>De acuerdo</div>
        <div style={{
          padding: "11px 14px", borderRadius: 8,
          border: `1px solid ${LIGHT.border}`,
          fontSize: 12, color: LIGHT.inkSoft, textAlign: "center",
        }}>No tengo postura</div>
      </div>
    </div>
  );
}

function PhoneMockupResult() {
  const bars = [
    ["Frente Cívico Verde", 78, LIGHT.terracotta],
    ["Coalición Reformista", 64, "#3a4356"],
    ["Movimiento Social", 51, "#c25a3a99"],
    ["Unión Federal", 42, "#c8893a"],
  ];
  return (
    <div style={{
      height: "100%", background: LIGHT.surface,
      display: "flex", flexDirection: "column",
    }}>
      <div style={{
        padding: "18px 18px 22px", background: LIGHT.terracotta, color: "#fff",
      }}>
        <div style={{
          fontSize: 10, letterSpacing: 1.5, fontWeight: 700,
          textTransform: "uppercase", opacity: 0.85, marginBottom: 6,
          display: "flex", justifyContent: "space-between",
        }}>
          <span>×</span>
          <span>Resultado</span>
          <span>↗</span>
        </div>
        <div style={{ fontSize: 9, fontWeight: 700, letterSpacing: 1,
          opacity: 0.85, marginTop: 10, marginBottom: 4 }}>TU AFINIDAD</div>
        <div style={{
          fontSize: 15, fontWeight: 800, lineHeight: 1.3,
          fontFamily: "Fraunces, Georgia, serif",
        }}>Coincidís más con propuestas del Frente Cívico Verde</div>
        <div style={{ fontSize: 11, opacity: 0.9, marginTop: 6 }}>
          78% · 4 partidos cerca
        </div>
      </div>
      <div style={{ padding: 14, flex: 1, background: LIGHT.surface }}>
        <div style={{
          padding: 12, background: LIGHT.surfaceAlt, borderRadius: 10,
          border: `1px solid ${LIGHT.border}`,
        }}>
          <div style={{
            fontSize: 9, color: LIGHT.textMuted, letterSpacing: 1, fontWeight: 700,
            textTransform: "uppercase", marginBottom: 10,
          }}>Las cinco principales</div>
          {bars.map(([name, pct, color]) => (
            <div key={name} style={{ marginBottom: 9 }}>
              <div style={{
                display: "flex", justifyContent: "space-between",
                fontSize: 11, fontWeight: 600, color: LIGHT.ink, marginBottom: 3,
              }}>
                <span>{name}</span>
                <span style={{ color: LIGHT.textMuted }}>{pct}%</span>
              </div>
              <div style={{
                height: 4, background: LIGHT.border, borderRadius: 2, overflow: "hidden",
              }}>
                <div style={{ height: "100%", width: `${pct}%`, background: color }} />
              </div>
            </div>
          ))}
        </div>
        <div style={{
          marginTop: 12, padding: 10, background: LIGHT.terracottaBg,
          border: `1px solid ${LIGHT.terracottaSoft}`, borderRadius: 8,
          fontSize: 10, color: LIGHT.terracotta, lineHeight: 1.4,
        }}>
          No es una recomendación de voto. Mide coincidencia con propuestas declaradas.
        </div>
      </div>
    </div>
  );
}

