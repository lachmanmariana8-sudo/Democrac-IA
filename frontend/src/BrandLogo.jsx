// Logo del brand: dos círculos concéntricos + punto terracota.
// En su propio archivo para no romper react-refresh (shared.jsx solo
// exporta constantes/funciones).
import { COLORS, BRAND } from "./shared.js";

export function BrandLogo({ size = 36, withWordmark = false, wordmarkSize = 22, mono = false, lightOnDark = true }) {
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
