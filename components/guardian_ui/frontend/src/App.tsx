import { useEffect, useRef, useState } from "react";
import { useStreamlitArgs, sendEvent, setFrameHeight } from "./StreamlitBridge";
import { I18N } from "./i18n";
import { Icon } from "./Icons";
import { TopBar } from "./components/TopBar";
import { Sidebar } from "./components/Sidebar";
import { InputPanel } from "./components/InputPanel";
import { PipelineCard } from "./components/Pipeline";
import {
  VerdictHero,
  BreakdownCard,
  ResultsTabs,
} from "./components/Results";
import type { Lang, Theme, Tab, Density } from "./types";

const PALETTES: Record<string, Record<string, string>> = {
  emerald: {
    "50": "#ecfdf5",
    "100": "#d1fae5",
    "200": "#a7f3d0",
    "300": "#6ee7b7",
    "400": "#34d399",
    "500": "#10b981",
    "600": "#059669",
    "700": "#047857",
    "800": "#065f46",
    "900": "#064e3b",
  },
  teal: {
    "50": "#f0fdfa",
    "100": "#ccfbf1",
    "200": "#99f6e4",
    "300": "#5eead4",
    "400": "#2dd4bf",
    "500": "#14b8a6",
    "600": "#0d9488",
    "700": "#0f766e",
    "800": "#115e59",
    "900": "#134e4a",
  },
  indigo: {
    "50": "#eef2ff",
    "100": "#e0e7ff",
    "200": "#c7d2fe",
    "300": "#a5b4fc",
    "400": "#818cf8",
    "500": "#6366f1",
    "600": "#4f46e5",
    "700": "#4338ca",
    "800": "#3730a3",
    "900": "#312e81",
  },
  blue: {
    "50": "#eff6ff",
    "100": "#dbeafe",
    "200": "#bfdbfe",
    "300": "#93c5fd",
    "400": "#60a5fa",
    "500": "#3b82f6",
    "600": "#2563eb",
    "700": "#1d4ed8",
    "800": "#1e40af",
    "900": "#1e3a8a",
  },
  violet: {
    "50": "#f5f3ff",
    "100": "#ede9fe",
    "200": "#ddd6fe",
    "300": "#c4b5fd",
    "400": "#a78bfa",
    "500": "#8b5cf6",
    "600": "#7c3aed",
    "700": "#6d28d9",
    "800": "#5b21b6",
    "900": "#4c1d95",
  },
};

const PALETTE_BY_COLOR: Record<string, string> = {
  "#059669": "emerald",
  "#0d9488": "teal",
  "#4f46e5": "indigo",
  "#2563eb": "blue",
  "#7c3aed": "violet",
};

export default function App() {
  const args = useStreamlitArgs();

  // Local-only buffer for textarea so per-rerun args.inputText doesn't steal focus.
  const [textBuf, setTextBuf] = useState("");
  const lastSyncedRef = useRef<string>("");

  // Sync text buffer from args only when args.inputText changes externally
  // (e.g. after USE_SAMPLE / CLEAR_INPUT). Avoid clobbering active typing.
  useEffect(() => {
    if (!args) return;
    if (args.inputText !== lastSyncedRef.current) {
      setTextBuf(args.inputText);
      lastSyncedRef.current = args.inputText;
    }
  }, [args?.inputText]);

  // Apply theme + palette to document root
  useEffect(() => {
    if (!args) return;
    document.documentElement.setAttribute("data-theme", args.theme);
    document.documentElement.setAttribute("data-density", args.density);
    const paletteName = PALETTE_BY_COLOR[args.paletteColor] || "emerald";
    const p = PALETTES[paletteName];
    Object.entries(p).forEach(([k, v]) => {
      document.documentElement.style.setProperty(`--brand-${k}`, v);
    });
  }, [args?.theme, args?.density, args?.paletteColor]);

  // Frame height — the parent page enforces height: 100vh on our iframe via
  // !important CSS, so window.innerHeight inside the iframe == the actual
  // viewport. Just report it back so Streamlit's inline-style doesn't fight.
  useEffect(() => {
    const update = () => setFrameHeight(window.innerHeight);
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  // While running, poll the backend so per-node runtime updates flow through.
  // Streamlit can't push from Python; each POLL is a no-op event that
  // triggers a script rerun, which re-syncs the worker thread's progress.
  useEffect(() => {
    if (args?.state !== "running") return;
    const id = window.setInterval(() => {
      sendEvent({ type: "POLL" });
    }, 600);
    return () => window.clearInterval(id);
  }, [args?.state]);

  if (!args) {
    return (
      <div style={{ padding: 20, color: "#888", fontFamily: "sans-serif" }}>
        Loading…
      </div>
    );
  }

  const t = I18N[args.lang];
  const result = args.result;
  const docType = args.tab;

  const onRun = () => {
    sendEvent({ type: "RUN", text: textBuf, tab: docType });
  };

  const onSample = () => {
    sendEvent({ type: "USE_SAMPLE" });
  };

  const onClearInput = () => {
    setTextBuf("");
    sendEvent({ type: "CLEAR_INPUT" });
  };

  const onTextChange = (v: string) => {
    setTextBuf(v);
  };

  return (
    <div className="app" data-density={args.density}>
      <TopBar
        t={t}
        lang={args.lang}
        setLang={(v: Lang) => sendEvent({ type: "SET_LANG", lang: v })}
        theme={args.theme}
        setTheme={(v: Theme) => sendEvent({ type: "SET_THEME", theme: v })}
        tab={args.tab}
        setTab={(v: Tab) => sendEvent({ type: "SET_TAB", tab: v })}
        state={args.state}
        paletteColor={args.paletteColor}
        setPaletteColor={(v) => sendEvent({ type: "SET_PALETTE", color: v })}
        density={args.density}
        setDensity={(v: Density) =>
          sendEvent({ type: "SET_DENSITY", density: v })
        }
      />

      <Sidebar
        t={t}
        lang={args.lang}
        history={args.history}
        selectedIdx={args.selectedHistoryIdx}
        onSelect={(idx) => sendEvent({ type: "SELECT_HISTORY", idx })}
        onClear={() => sendEvent({ type: "CLEAR_HISTORY" })}
      />

      <main className="main">
        <div className="page-head">
          <div>
            <h1 className="page-title">
              {args.tab === "incident" ? t.tabs.incident : t.tabs.delivery}
            </h1>
            <p className="page-subtitle">
              {t.appSubtitle} ·{" "}
              <span className="mono faint">{t.appTagline}</span>
            </p>
          </div>
          <div className="page-head-meta">
            <span className="badge">
              <Icon name="cpu" size={11} />{" "}
              {args.tab === "incident" ? 5 : 4} agents · parallel
            </span>
            <span>
              <span className="kbd">⌘</span> <span className="kbd">↵</span>{" "}
              {t.input.run}
            </span>
          </div>
        </div>

        <div className="workspace">
          <div className="col" style={{ gap: 18 }}>
            <InputPanel
              t={t}
              docType={docType}
              value={textBuf}
              onChange={onTextChange}
              onRun={onRun}
              onClear={onClearInput}
              onSample={onSample}
              running={args.state === "running"}
            />
          </div>

          <div className="col" style={{ gap: 18 }}>
            {args.state === "idle" && (
              <div className="empty" style={{ height: "100%" }}>
                <div className="empty-icon">
                  <Icon name="shield" size={26} />
                </div>
                <h3>{t.appName}</h3>
                <p>{t.appSubtitle}</p>
                <div
                  className="row"
                  style={{
                    justifyContent: "center",
                    gap: 6,
                    marginTop: 14,
                  }}
                >
                  <span className="badge brand">
                    <Icon name="branch" size={11} /> LangGraph
                  </span>
                  <span className="badge">
                    <Icon name="cpu" size={11} /> Gemini · Groq
                  </span>
                  <span className="badge">
                    <Icon name="activity" size={11} /> LangSmith
                  </span>
                </div>
                <div
                  className="row"
                  style={{
                    justifyContent: "center",
                    gap: 8,
                    marginTop: 18,
                  }}
                >
                  <button className="btn btn-primary" onClick={onSample}>
                    <Icon name="rocket" size={14} />
                    {{
                      zh: "运行样例",
                      ja: "サンプル実行",
                      en: "Run a sample",
                    }[args.lang]}
                  </button>
                </div>
              </div>
            )}

            {args.state === "running" && (
              <div className="card" style={{ height: "100%" }}>
                <div className="card-header">
                  <div className="card-title">
                    <span
                      className="spinner"
                      style={{
                        borderColor: "var(--border)",
                        borderTopColor: "var(--brand-600)",
                      }}
                    />
                    {t.input.running}
                  </div>
                  <span className="badge brand">
                    <Icon name="activity" size={11} /> streaming
                  </span>
                </div>
                <div className="card-body">
                  <div className="scan-bar" />
                  <ul
                    style={{
                      listStyle: "none",
                      padding: 0,
                      margin: "14px 0 0",
                      display: "flex",
                      flexDirection: "column",
                      gap: 8,
                    }}
                  >
                    {[
                      {
                        i: "branch" as const,
                        k: {
                          zh: "LangGraph 编排已启动",
                          ja: "LangGraph オーケストレーション開始",
                          en: "LangGraph orchestrated",
                        },
                      },
                      {
                        i: "cpu" as const,
                        k: {
                          zh: "并行 fan-out 到 Agent",
                          ja: "Agent へ並列 fan-out",
                          en: "Parallel fan-out to agents",
                        },
                      },
                      {
                        i: "activity" as const,
                        k: {
                          zh: "LangSmith trace 写入中",
                          ja: "LangSmith trace 書き込み中",
                          en: "LangSmith trace streaming",
                        },
                      },
                    ].map((row, i) => (
                      <li
                        key={i}
                        className="row text-sm"
                        style={{ gap: 8 }}
                      >
                        <Icon
                          name={row.i}
                          size={12}
                          style={{ color: "var(--brand-600)" }}
                        />
                        <span style={{ flex: 1 }}>{row.k[args.lang]}</span>
                        <span className="mono text-xs faint">live</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {args.state === "done" && result && (
              <div className="card" style={{ height: "100%" }}>
                <div className="card-header">
                  <div className="card-title">
                    <Icon name="target" size={14} /> {t.verdict.score}
                  </div>
                  <span
                    className={`badge ${
                      result.verdict === "pass"
                        ? "pass"
                        : result.verdict === "conditional"
                        ? "warn"
                        : "bad"
                    }`}
                  >
                    <Icon
                      name={
                        result.verdict === "pass"
                          ? "check"
                          : result.verdict === "conditional"
                          ? "sparkles"
                          : "x"
                      }
                      size={10}
                    />{" "}
                    {t.verdict[result.verdict]}
                  </span>
                </div>
                <div
                  className="card-body"
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: 14,
                  }}
                >
                  <div
                    className="row"
                    style={{ gap: 14, alignItems: "baseline" }}
                  >
                    <span className="verdict-score" style={{ margin: 0 }}>
                      <span
                        className="verdict-score-num"
                        style={{
                          fontSize: 56,
                          color:
                            result.verdict === "pass"
                              ? "var(--ok-600)"
                              : result.verdict === "conditional"
                              ? "var(--warn-600)"
                              : "var(--bad-600)",
                        }}
                      >
                        {result.totalScore}
                      </span>
                      <span className="verdict-score-denom">/100</span>
                    </span>
                    <span
                      className="text-sm muted"
                      style={{ flex: 1 }}
                    >
                      {result.issues.length}{" "}
                      {{
                        zh: "项缺陷",
                        ja: "件の指摘",
                        en: "findings",
                      }[args.lang]}
                    </span>
                  </div>
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: 6,
                    }}
                  >
                    {Object.entries(result.breakdown).map(([dim, b]) => {
                      if (!b) return null;
                      const tier =
                        b.score >= 80
                          ? "high"
                          : b.score >= 60
                          ? "mid"
                          : "low";
                      return (
                        <div
                          key={dim}
                          className="row"
                          style={{ gap: 8, fontSize: 12 }}
                        >
                          <span
                            style={{
                              width: 78,
                              color: "var(--text-muted)",
                            }}
                          >
                            {t.pipeline.nodes[dim]}
                          </span>
                          <div
                            className="bd-bar-track"
                            style={{ flex: 1, height: 6 }}
                          >
                            <div
                              className="bd-bar-fill"
                              style={{
                                width: `${b.score}%`,
                                background:
                                  tier === "low"
                                    ? "var(--bad-500)"
                                    : tier === "mid"
                                    ? "var(--warn-500)"
                                    : "var(--ok-500)",
                              }}
                            />
                          </div>
                          <span
                            className="mono"
                            style={{
                              width: 28,
                              textAlign: "right",
                              color: "var(--text)",
                            }}
                          >
                            {b.score}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {args.state !== "idle" && (
          <PipelineCard
            t={t}
            docType={docType}
            runtime={args.runtime}
            breakdown={
              args.state === "done" && result ? result.breakdown : null
            }
          />
        )}

        {args.state === "done" && result && (
          <>
            <VerdictHero
              t={t}
              lang={args.lang}
              verdict={result.verdict}
              totalScore={result.totalScore}
              latencyMs={result.latencyMs}
              tokens={result.tokens}
              primaryModel={result.primaryModel}
              fallback={result.fallback}
              submittedAt={result.submittedAt}
              docType={result.docType}
            />
            <BreakdownCard t={t} breakdown={result.breakdown} />
            <ResultsTabs t={t} lang={args.lang} data={result} />
          </>
        )}
      </main>
    </div>
  );
}
