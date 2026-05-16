import { useEffect, useRef, useState } from "react";
import { Icon, BrandMark } from "../Icons";
import type { Lang, Theme, Tab, DemoState } from "../types";
import type { Translations } from "../i18n";

const PALETTE_OPTIONS = [
  { color: "#059669", name: "emerald" },
  { color: "#0d9488", name: "teal" },
  { color: "#4f46e5", name: "indigo" },
  { color: "#2563eb", name: "blue" },
  { color: "#7c3aed", name: "violet" },
];

const ColorSwatch = ({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) => {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node))
        setOpen(false);
    };
    if (open) document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  return (
    <div style={{ position: "relative" }} ref={ref}>
      <button
        className="icon-btn"
        title="主色 / Primary"
        onClick={() => setOpen((o) => !o)}
        style={{ display: "grid", placeItems: "center" }}
      >
        <span
          style={{
            display: "block",
            width: 14,
            height: 14,
            borderRadius: "50%",
            background: value,
            boxShadow:
              "0 0 0 1px rgba(0,0,0,0.06), inset 0 0 0 2px var(--bg-elev)",
            border: "1px solid var(--border)",
          }}
        />
      </button>
      {open && (
        <div
          className="card"
          style={{
            position: "absolute",
            top: 40,
            right: 0,
            padding: 8,
            display: "flex",
            gap: 6,
            zIndex: 50,
            boxShadow: "var(--shadow-lg)",
          }}
        >
          {PALETTE_OPTIONS.map((o) => (
            <button
              key={o.color}
              onClick={() => {
                onChange(o.color);
                setOpen(false);
              }}
              title={o.name}
              style={{
                width: 28,
                height: 28,
                borderRadius: 8,
                border:
                  value === o.color
                    ? "2px solid var(--text)"
                    : "1px solid var(--border)",
                background: o.color,
                cursor: "pointer",
                padding: 0,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
};

interface TopBarProps {
  t: Translations;
  lang: Lang;
  setLang: (v: Lang) => void;
  theme: Theme;
  setTheme: (v: Theme) => void;
  tab: Tab;
  setTab: (v: Tab) => void;
  state: DemoState;
  paletteColor: string;
  setPaletteColor: (v: string) => void;
}

export const TopBar = ({
  t,
  lang,
  setLang,
  theme,
  setTheme,
  tab,
  setTab,
  state,
  paletteColor,
  setPaletteColor,
}: TopBarProps) => {
  return (
    <header className="topbar">
      <div className="topbar-brand">
        <BrandMark size={28} />
        <span className="topbar-title">{t.appName}</span>
        <span className="topbar-sub">v0.9 · demo</span>
      </div>

      <div className="topbar-divider" />

      <div className="topbar-tabs" role="tablist">
        <button
          role="tab"
          className="topbar-tab"
          aria-selected={tab === "delivery"}
          onClick={() => setTab("delivery")}
        >
          <span className="topbar-tab-icon">
            <Icon name="package" size={15} />
          </span>
          {t.tabs.delivery}
        </button>
        <button
          role="tab"
          className="topbar-tab"
          aria-selected={tab === "incident"}
          onClick={() => setTab("incident")}
        >
          <span className="topbar-tab-icon">
            <Icon name="siren" size={15} />
          </span>
          {t.tabs.incident}
        </button>
      </div>

      <div className="topbar-spacer" />

      <div className="topbar-actions">
        <span className="badge brand" title={t.state[state]}>
          <Icon name="activity" size={11} />
          {t.state[state]}
        </span>

        <div className="topbar-divider" />

        <div className="seg">
          {(
            [
              { k: "zh", label: "中" },
              { k: "ja", label: "日" },
              { k: "en", label: "EN" },
            ] as { k: Lang; label: string }[]
          ).map((o) => (
            <button
              key={o.k}
              className="seg-btn"
              aria-pressed={lang === o.k}
              onClick={() => setLang(o.k)}
            >
              {o.label}
            </button>
          ))}
        </div>

        <ColorSwatch value={paletteColor} onChange={setPaletteColor} />

        <button
          className="icon-btn"
          title={t.theme[theme === "light" ? "dark" : "light"]}
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
        >
          <Icon name={theme === "light" ? "moon" : "sun"} size={16} />
        </button>

        <button className="icon-btn" title="Notifications">
          <Icon name="bell" size={16} />
        </button>

        <div className="topbar-divider" />

        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: "50%",
            background:
              "linear-gradient(135deg, var(--brand-500), var(--brand-700))",
            display: "grid",
            placeItems: "center",
            color: "white",
            fontSize: 11,
            fontWeight: 600,
          }}
        >
          YS
        </div>
      </div>
    </header>
  );
};
