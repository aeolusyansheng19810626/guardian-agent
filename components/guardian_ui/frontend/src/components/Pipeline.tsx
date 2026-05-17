import { useEffect, useRef, useState, type CSSProperties } from "react";
import { Icon } from "../Icons";
import type { IconName } from "../Icons";
import type { Tab, Runtime, NodeKey, BreakdownEntry, Dim } from "../types";
import type { Translations } from "../i18n";

const NODE_W = 168;
const NODE_H = 64;

function layout(cw: number, ch: number, agentDims: string[]) {
  const cx1 = 24;
  const cx2 = 280;
  const cxGuardian = 540;
  const cx3 = Math.max(cw - 28 - NODE_W, 780);

  const n = agentDims.length;
  const rowGap = 14;
  const totalH = n * NODE_H + (n - 1) * rowGap;
  const startY = (ch - totalH) / 2;

  const agentPos = agentDims.map((dim, i) => ({
    dim,
    x: cx2,
    y: startY + i * (NODE_H + rowGap),
  }));

  return {
    classify: { x: cx1, y: ch / 2 - NODE_H / 2 },
    agents: agentPos,
    guardian: { x: cxGuardian, y: ch / 2 - NODE_H / 2 },
    reporter: { x: cx3, y: ch / 2 - NODE_H / 2 },
  };
}

function bezier(x1: number, y1: number, x2: number, y2: number) {
  const dx = Math.max((x2 - x1) * 0.55, 30);
  return `M ${x1},${y1} C ${x1 + dx},${y1} ${x2 - dx},${y2} ${x2},${y2}`;
}

const NodeIconFor = (dim: string): IconName =>
  (({
    classify: "branch",
    completeness: "clipboard",
    quality: "sparkles",
    compliance: "check",
    logic: "flow",
    prevention: "target",
    guardian: "shield",
    reporter: "file",
  } as Record<string, IconName>)[dim] || "cpu");

const ModelFor = (dim: string) =>
  (({
    classify: { vendor: "gemini", label: "Flash" },
    completeness: { vendor: "groq", label: "Llama 70B" },
    quality: { vendor: "gemini", label: "Flash" },
    compliance: { vendor: "gemini", label: "Flash" },
    logic: { vendor: "gemini", label: "Flash" },
    prevention: { vendor: "gemini", label: "Flash" },
    guardian: { vendor: "gemini", label: "2.5 Pro" },
    reporter: { vendor: "gemini", label: "2.5 Pro" },
  } as Record<string, { vendor: string; label: string }>)[dim] || {
    vendor: "gemini",
    label: "—",
  });

interface PipelineNodeProps {
  dim: string;
  name: string;
  role: string;
  status: "pending" | "running" | "done";
  score: number | string;
  model: { vendor: string; label: string };
  style?: CSSProperties;
  runningPct?: number;
}

const PipelineNode = ({
  dim,
  name,
  role,
  status,
  score,
  model,
  style,
  runningPct = 0,
}: PipelineNodeProps) => (
  <div
    className={`node node-${dim}`}
    data-status={status}
    style={{ ...style, width: NODE_W, height: NODE_H }}
  >
    <div className="node-head">
      <span className="node-icon">
        <Icon name={NodeIconFor(dim)} size={13} />
      </span>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          lineHeight: 1.2,
          minWidth: 0,
          flex: 1,
        }}
      >
        <span className="node-name">{name}</span>
        <span className="text-xs faint mono" style={{ fontSize: 10 }}>
          {role}
        </span>
      </div>
      <span className="node-status-dot" />
    </div>
    <div className="node-meta">
      <span className={`tag-vendor ${model.vendor}`}>{model.label}</span>
      {status === "done" && (
        <span style={{ color: "var(--text)", fontWeight: 600 }}>{score}</span>
      )}
      {status === "running" && (
        <span className="mono" style={{ color: "var(--accent-600)" }}>
          {runningPct}%
        </span>
      )}
      {status === "pending" && (
        <span className="mono" style={{ color: "var(--text-faint)" }}>
          queued
        </span>
      )}
    </div>
    {status === "running" && (
      <div className="node-bar">
        <div
          className="node-bar-fill"
          style={{ width: `${runningPct}%` }}
        />
      </div>
    )}
  </div>
);

interface AgentPipelineProps {
  t: Translations;
  docType: Tab;
  runtime: Runtime;
  breakdown: Partial<Record<Dim, BreakdownEntry>> | null;
}

const AgentPipeline = ({
  t,
  docType,
  runtime,
  breakdown,
}: AgentPipelineProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ w: 800, h: 320 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const r = entries[0].contentRect;
      setSize({ w: r.width, h: r.height });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const agentDims =
    docType === "incident"
      ? ["completeness", "quality", "compliance", "logic", "prevention"]
      : ["completeness", "quality", "compliance", "logic"];

  const L = layout(size.w, size.h, agentDims);

  const get = (k: NodeKey | string) =>
    runtime[k as NodeKey] || { status: "pending" as const };

  const edgeState = (a: string, b: string) => {
    const sa = get(a).status;
    const sb = get(b).status;
    if (sa === "done" && (sb === "running" || sb === "done")) return "active";
    if (sa === "done" && sb === "pending") return "active";
    if (sa === "running" && sb === "running") return "flow";
    if (sa === "done" && sb === "running") return "flow";
    return "idle";
  };

  const renderEdge = (
    key: string,
    x1: number,
    y1: number,
    x2: number,
    y2: number,
    state: string,
  ) => {
    const cls =
      state === "flow"
        ? "edge-flow"
        : state === "active"
        ? "edge-active"
        : "edge";
    return <path key={key} className={cls} d={bezier(x1, y1, x2, y2)} />;
  };

  return (
    <div ref={containerRef} className="pipeline-canvas">
      <div className="grid-bg" />
      <svg
        className="edges"
        viewBox={`0 0 ${size.w} ${size.h}`}
        preserveAspectRatio="none"
      >
        {L.agents.map((a, i) =>
          renderEdge(
            `c-${i}`,
            L.classify.x + NODE_W,
            L.classify.y + NODE_H / 2,
            a.x,
            a.y + NODE_H / 2,
            edgeState("classify", a.dim),
          ),
        )}
        {L.agents.map((a, i) =>
          renderEdge(
            `g-${i}`,
            a.x + NODE_W,
            a.y + NODE_H / 2,
            L.guardian.x,
            L.guardian.y + NODE_H / 2,
            edgeState(a.dim, "guardian"),
          ),
        )}
        {renderEdge(
          "r-0",
          L.guardian.x + NODE_W,
          L.guardian.y + NODE_H / 2,
          L.reporter.x,
          L.reporter.y + NODE_H / 2,
          edgeState("guardian", "reporter"),
        )}
      </svg>

      <PipelineNode
        dim="classify"
        name={t.pipeline.nodes.classify}
        role={t.pipeline.nodeRoles.classify}
        status={get("classify").status}
        runningPct={get("classify").pct || 0}
        score="—"
        model={ModelFor("classify")}
        style={{ left: L.classify.x, top: L.classify.y }}
      />

      {L.agents.map((a) => (
        <PipelineNode
          key={a.dim}
          dim={a.dim}
          name={t.pipeline.nodes[a.dim]}
          role={t.pipeline.nodeRoles[a.dim]}
          status={get(a.dim).status}
          runningPct={get(a.dim).pct || 0}
          score={breakdown?.[a.dim as Dim]?.score ?? "—"}
          model={ModelFor(a.dim)}
          style={{ left: a.x, top: a.y }}
        />
      ))}

      <PipelineNode
        dim="guardian"
        name={t.pipeline.nodes.guardian}
        role={t.pipeline.nodeRoles.guardian}
        status={get("guardian").status}
        runningPct={get("guardian").pct || 0}
        score={get("guardian").totalScore ?? "—"}
        model={ModelFor("guardian")}
        style={{ left: L.guardian.x, top: L.guardian.y }}
      />

      <PipelineNode
        dim="reporter"
        name={t.pipeline.nodes.reporter}
        role={t.pipeline.nodeRoles.reporter}
        status={get("reporter").status}
        runningPct={get("reporter").pct || 0}
        score={get("reporter").status === "done" ? "✓" : "—"}
        model={ModelFor("reporter")}
        style={{ left: L.reporter.x, top: L.reporter.y }}
      />
    </div>
  );
};

interface PipelineCardProps {
  t: Translations;
  docType: Tab;
  runtime: Runtime;
  breakdown: Partial<Record<Dim, BreakdownEntry>> | null;
}

export const PipelineCard = ({
  t,
  docType,
  runtime,
  breakdown,
}: PipelineCardProps) => (
  <section className="card">
    <div className="card-header">
      <div className="card-title">
        <Icon name="branch" size={14} />
        {t.pipeline.title}
        <span
          className="text-xs faint"
          style={{ fontWeight: 400, marginLeft: 8 }}
        >
          {t.pipeline.subtitle}
        </span>
      </div>
      <div className="card-actions">
        <span className="badge brand">
          <Icon name="cpu" size={11} />
          LangGraph
        </span>
        <span className="badge">
          {docType === "incident" ? "5 agents" : "4 agents"}
        </span>
      </div>
    </div>
    <div className="card-body" style={{ padding: 12 }}>
      <div className="pipeline">
        <AgentPipeline
          t={t}
          docType={docType}
          runtime={runtime}
          breakdown={breakdown}
        />
      </div>
      <div className="pipeline-legend">
        <span className="pipeline-legend-item">
          <span
            className="pipeline-legend-dot"
            style={{ background: "var(--slate-300)" }}
          />
          {t.pipeline.legendPending}
        </span>
        <span className="pipeline-legend-item">
          <span
            className="pipeline-legend-dot"
            style={{
              background: "var(--accent-500)",
              boxShadow:
                "0 0 0 3px color-mix(in oklab, var(--accent-500) 18%, transparent)",
            }}
          />
          {t.pipeline.legendRunning}
        </span>
        <span className="pipeline-legend-item">
          <span
            className="pipeline-legend-dot"
            style={{ background: "var(--ok-500)" }}
          />
          {t.pipeline.legendDone}
        </span>
        <span className="pipeline-legend-item">
          <svg width="24" height="6">
            <path
              d="M0,3 H24"
              stroke="var(--accent-500)"
              strokeWidth="2"
              strokeDasharray="5 4"
            />
          </svg>
          {t.pipeline.legendFlow}
        </span>
      </div>
    </div>
  </section>
);
