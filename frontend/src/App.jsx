import { useEffect, useCallback, lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import { LIGHT } from "./shared.js";

// ═══════════════════════════════════════════════════════════════════════
// APP SHELL — solo routing. Cada página es un chunk lazy (Sprint 2).
//   /       → LandingPage      (pages/Landing.jsx)
//   /voto   → VotoInformadoPage (pages/Voto.jsx)
//   /app    → DemocracIADashboard (pages/Dashboard.jsx)
// ═══════════════════════════════════════════════════════════════════════

const LandingPage = lazy(() => import("./pages/Landing.jsx"));
const VotoInformadoPage = lazy(() => import("./pages/Voto.jsx"));
const DemocracIADashboard = lazy(() => import("./pages/Dashboard.jsx"));

// Loader sobrio mientras Vite descarga el chunk de la página.
function RouteFallback() {
  return (
    <div style={{
      minHeight: "100vh", background: LIGHT.bg, color: LIGHT.textMuted,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontFamily: "Inter, system-ui, sans-serif", fontSize: 14, letterSpacing: 1,
    }}>
      Cargando…
    </div>
  );
}

// Compat con URLs viejas compartidas en redes / mails: ?app=true → /app, ?voto=true → /voto.
// La sitemap antes declaraba `?app=true` como canonical; ahora redirige a la ruta real.
function LegacyQueryRedirect({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get("app") === "true") {
      navigate("/app", { replace: true });
    } else if (params.get("voto") === "true") {
      navigate("/voto", { replace: true });
    }
  }, [location.search, navigate]);
  return children;
}

function LandingRoute() {
  const navigate = useNavigate();
  const onEnterApp = useCallback(() => navigate("/app"), [navigate]);
  const onShowVoto = useCallback(() => {
    navigate("/voto");
    try { window.scrollTo(0, 0); } catch { /* SSR */ }
  }, [navigate]);
  return (
    <LegacyQueryRedirect>
      <Suspense fallback={<RouteFallback />}>
        <LandingPage onEnterApp={onEnterApp} onShowVoto={onShowVoto} />
      </Suspense>
    </LegacyQueryRedirect>
  );
}

function VotoRoute() {
  const navigate = useNavigate();
  const onBack = useCallback(() => {
    navigate("/");
    try { window.scrollTo(0, 0); } catch { /* SSR */ }
  }, [navigate]);
  const onEnterApp = useCallback(() => navigate("/app"), [navigate]);
  useEffect(() => { try { window.scrollTo(0, 0); } catch { /* SSR */ } }, []);
  return (
    <Suspense fallback={<RouteFallback />}>
      <VotoInformadoPage onBack={onBack} onEnterApp={onEnterApp} />
    </Suspense>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingRoute />} />
        <Route path="/app" element={
          <Suspense fallback={<RouteFallback />}>
            <DemocracIADashboard />
          </Suspense>
        } />
        <Route path="/voto" element={<VotoRoute />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
