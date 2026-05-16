import { useMemo, useState } from "react";
import { Icon } from "../Icons";
import type {
  GuardianResult,
  Lang,
  Verdict,
  BreakdownEntry,
  Dim,
  IssueItem,
} from "../types";
import type { Translations } from "../i18n";

interface VerdictHeroProps {
  t: Translations;
  lang: Lang;
  verdict: Verdict;
  totalScore: number;
  latencyMs: number;
  tokens: number;
  primaryModel: string;
  fallback: string | null;
  submittedAt: string;
  docType: string;
}

export const VerdictHero = ({
  t,
  lang,
  verdict,
  totalScore,
  latencyMs,
  tokens,
  primaryModel,
  fallback,
  submittedAt,
}: VerdictHeroProps) => {
  const palette = {
    pass: {
      color: "var(--ok-600)",
      icon: "check" as const,
      headline: t.verdict.pass,
    },
    conditional: {
      color: "var(--warn-600)",
      icon: "sparkles" as const,
      headline: t.verdict.conditional,
    },
    block: {
      color: "var(--bad-600)",
      icon: "x" as const,
      headline: t.verdict.block,
    },
  }[verdict];

  const summaries = {
    pass: {
      zh: "符合质量要求，可推进下一阶段。",
      ja: "品質要件を満たしており、次工程へ進行可能。",
      en: "Meets the quality bar — ready to advance.",
    },
    conditional: {
      zh: "存在可改进项，建议修订后再次提交。",
      ja: "改善余地あり。修正後の再提出を推奨。",
      en: "Has improvement points — revise and resubmit.",
    },
    block: {
      zh: "存在关键缺失或不合规项，不予通过。",
      ja: "重要な欠落または不適合があるため不合格。",
      en: "Critical gaps or non-compliance — not approved.",
    },
  }[verdict];

  const pct = Math.max(0, Math.min(100, totalScore));

  return (
    <section
      className="verdict"
      style={{ ["--verdict-accent" as string]: palette.color }}
    >
      <div className="verdict-grid">
        <div className="verdict-left">
          <span className="verdict-tag">
            <Icon name={palette.icon} size={13} />
            {palette.headline}
          </span>
          <div className="verdict-score">
            <span className="verdict-score-num">{totalScore}</span>
            <span className="verdict-score-denom">/ 100</span>
          </div>
          <p className="verdict-summary">
            {summaries[lang] || summaries.en}
          </p>
        </div>

        <div className="verdict-right">
          <div className="gauge">
            <div className="gauge-track">
              <div className="gauge-fill" />
              <div className="gauge-thresholds">
                <span className="gauge-th" style={{ left: "60%" }} />
                <span className="gauge-th" style={{ left: "80%" }} />
                <span
                  className="gauge-th-label"
                  style={{ left: "60%", color: "var(--warn-600)" }}
                >
                  60
                </span>
                <span
                  className="gauge-th-label"
                  style={{ left: "80%", color: "var(--ok-600)" }}
                >
                  80
                </span>
              </div>
              <div
                className="gauge-marker"
                style={{ left: `${pct}%` }}
                title={`${totalScore}/100`}
              />
            </div>
            <div className="gauge-axis">
              <span>0 · {t.verdict.block}</span>
              <span>{t.verdict.conditional}</span>
              <span>{t.verdict.pass} · 100</span>
            </div>
          </div>
        </div>
      </div>

      <dl className="verdict-meta">
        <div className="row" style={{ gap: 4 }}>
          <dt>{t.verdict.submittedAt}</dt>
          <dd>{submittedAt}</dd>
        </div>
        <div className="row" style={{ gap: 4 }}>
          <dt>{t.verdict.latency}</dt>
          <dd>{(latencyMs / 1000).toFixed(2)}s</dd>
        </div>
        <div className="row" style={{ gap: 4 }}>
          <dt>{t.verdict.tokens}</dt>
          <dd>{tokens.toLocaleString()}</dd>
        </div>
        <div className="row" style={{ gap: 4 }}>
          <dt>{t.verdict.model}</dt>
          <dd>{primaryModel}</dd>
        </div>
        <div className="row" style={{ gap: 4 }}>
          <dt>{t.verdict.fallback}</dt>
          <dd>{fallback || t.verdict.none}</dd>
        </div>
      </dl>
    </section>
  );
};

const Radar = ({
  breakdown,
  t,
}: {
  breakdown: Partial<Record<Dim, BreakdownEntry>>;
  t: Translations;
}) => {
  const dims = Object.keys(breakdown) as Dim[];
  const N = dims.length;
  const cx = 150,
    cy = 150,
    R = 110;
  const angle = (i: number) => -Math.PI / 2 + (i / N) * Math.PI * 2;

  const ringR = [0.25, 0.5, 0.75, 1];

  const polygon = (vals: number[]) =>
    vals
      .map((v, i) => {
        const r = (v / 100) * R;
        return `${cx + r * Math.cos(angle(i))},${cy + r * Math.sin(angle(i))}`;
      })
      .join(" ");

  const labels = dims.map((dim, i) => {
    const r = R + 18;
    const x = cx + r * Math.cos(angle(i));
    const y = cy + r * Math.sin(angle(i));
    return { dim, x, y, score: breakdown[dim]!.score };
  });

  return (
    <svg className="radar" viewBox="0 0 300 300">
      {ringR.map((rr, i) => (
        <circle
          key={i}
          className="radar-grid"
          cx={cx}
          cy={cy}
          r={R * rr}
        />
      ))}
      {dims.map((_, i) => (
        <line
          key={i}
          className="radar-axis"
          x1={cx}
          y1={cy}
          x2={cx + R * Math.cos(angle(i))}
          y2={cy + R * Math.sin(angle(i))}
        />
      ))}
      <polygon
        className="radar-shape"
        points={polygon(dims.map((d) => breakdown[d]!.score))}
      />
      {dims.map((d, i) => {
        const r = (breakdown[d]!.score / 100) * R;
        const x = cx + r * Math.cos(angle(i));
        const y = cy + r * Math.sin(angle(i));
        return <circle key={d} className="radar-point" cx={x} cy={y} r="3" />;
      })}
      {labels.map(({ dim, x, y, score }) => {
        const ax = Math.cos(angle(dims.indexOf(dim)));
        const anchor =
          Math.abs(ax) < 0.2 ? "middle" : ax > 0 ? "start" : "end";
        return (
          <g key={dim}>
            <text
              className="radar-label"
              x={x}
              y={y}
              textAnchor={anchor}
              dominantBaseline="middle"
            >
              {t.pipeline.nodes[dim]}
            </text>
            <text
              className="radar-value"
              x={x}
              y={y + 12}
              textAnchor={anchor}
              dominantBaseline="middle"
            >
              {score}
            </text>
          </g>
        );
      })}
      {[25, 50, 75, 100].map((v, i) => (
        <text
          key={v}
          className="radar-value"
          x={cx + 4}
          y={cy - R * ringR[i] + 2}
        >
          {v}
        </text>
      ))}
    </svg>
  );
};

export const BreakdownCard = ({
  t,
  breakdown,
}: {
  t: Translations;
  breakdown: Partial<Record<Dim, BreakdownEntry>>;
}) => {
  const dims = Object.keys(breakdown) as Dim[];
  return (
    <section className="card">
      <div className="card-header">
        <div className="card-title">
          <Icon name="layers" size={14} /> {t.breakdown.title}
        </div>
      </div>
      <div className="breakdown-grid">
        <div className="bd-radar-wrap">
          <Radar breakdown={breakdown} t={t} />
        </div>
        <div className="bd-bars-wrap">
          {dims.map((dim) => {
            const b = breakdown[dim]!;
            const tier = b.score >= 80 ? "high" : b.score >= 60 ? "mid" : "low";
            return (
              <div key={dim} className="bd-bar-row" data-tier={tier}>
                <div className="bd-bar-label">
                  {t.pipeline.nodes[dim]}
                  <small>
                    {t.breakdown.weight} · {(b.weight * 100).toFixed(0)}%
                  </small>
                </div>
                <div className="bd-bar-track">
                  <div
                    className="bd-bar-fill"
                    style={{ width: `${b.score}%` }}
                  />
                </div>
                <div className="bd-bar-value">
                  {b.score}
                  <span
                    className="faint"
                    style={{ fontSize: 10, fontWeight: 400 }}
                  >
                    /100
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

const IssuesList = ({
  t,
  issues,
}: {
  t: Translations;
  issues: IssueItem[];
}) => {
  const sevOrder: Record<string, number> = { high: 0, med: 1, low: 2 };
  const sorted = [...issues].sort(
    (a, b) => sevOrder[a.severity] - sevOrder[b.severity],
  );
  if (!issues.length)
    return (
      <div className="empty" style={{ margin: 12 }}>
        <div className="empty-icon">
          <Icon name="check" size={22} />
        </div>
        <p>{t.issues.empty}</p>
      </div>
    );
  return (
    <div className="issues-list" style={{ padding: 6 }}>
      {sorted.map((i, k) => (
        <div key={k} className="issue">
          <span className={`issue-sev ${i.severity}`}>
            {t.issues.severity[i.severity]}
          </span>
          <span className="issue-dim">
            {t.pipeline.nodes[i.dimension] || i.dimension}
          </span>
          <span className="issue-text">{i.text}</span>
          <span className="issue-tags">
            <span className="text-xs mono faint">
              #{(k + 1).toString().padStart(2, "0")}
            </span>
          </span>
        </div>
      ))}
    </div>
  );
};

const FiveWhy = ({
  t,
  items,
}: {
  t: Translations;
  items: string[];
}) => {
  if (!items?.length) return null;
  return (
    <div className="five-why" style={{ padding: "8px 14px 14px" }}>
      {items.map((w, i) => (
        <div key={i} className="why-row">
          <div className="why-num">{i + 1}</div>
          <div className="why-text">
            <strong>
              {t.fiveWhy.label} {i + 1}.
            </strong>{" "}
            {w}
            {i === items.length - 1 && <small>→ {t.fiveWhy.rootCause}</small>}
          </div>
        </div>
      ))}
    </div>
  );
};

const Suggestions = ({
  items,
}: {
  items: string[];
}) => {
  if (!items?.length) return null;
  return (
    <div className="sugg-list" style={{ padding: "8px 14px 14px" }}>
      {items.map((s, i) => (
        <div key={i} className="sugg">
          <span className="sugg-num">
            {(i + 1).toString().padStart(2, "0")}
          </span>
          <span className="sugg-text">{s}</span>
        </div>
      ))}
    </div>
  );
};

const renderMarkdown = (md: string): string => {
  if (!md) return "";
  let h = md;
  h = h.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  h = h.replace(/^### (.*)$/gm, "<h3>$1</h3>");
  h = h.replace(/^## (.*)$/gm, "<h2>$1</h2>");
  h = h.replace(/^# (.*)$/gm, "<h1>$1</h1>");
  h = h.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  h = h.replace(/`([^`]+)`/g, "<code>$1</code>");
  h = h.replace(/^&gt; (.*)$/gm, "<blockquote>$1</blockquote>");
  h = h.replace(/(^|\n)((?:\d+\.\s.+\n?)+)/g, (_, pre, block) => {
    const items = (block as string)
      .trim()
      .split(/\n/)
      .map((l: string) => l.replace(/^\d+\.\s/, ""))
      .map((l: string) => `<li>${l}</li>`)
      .join("");
    return `${pre}<ol>${items}</ol>`;
  });
  h = h.replace(/(^|\n)((?:- .+\n?)+)/g, (_, pre, block) => {
    const items = (block as string)
      .trim()
      .split(/\n/)
      .map((l: string) => l.replace(/^- /, ""))
      .map((l: string) => `<li>${l}</li>`)
      .join("");
    return `${pre}<ul>${items}</ul>`;
  });
  h = h
    .split(/\n{2,}/)
    .map((p) => {
      if (/^<(h1|h2|h3|ul|ol|blockquote)/.test(p)) return p;
      return `<p>${p.replace(/\n/g, "<br/>")}</p>`;
    })
    .join("\n");
  return h;
};

const ReportPanel = ({
  t,
  report,
}: {
  t: Translations;
  report: string;
}) => {
  const html = useMemo(() => renderMarkdown(report), [report]);
  return (
    <div style={{ padding: "0 18px 18px" }}>
      <div className="row" style={{ gap: 6, marginBottom: 8 }}>
        <button className="btn">
          <Icon name="copy" size={13} /> {t.report.copy}
        </button>
        <button className="btn">
          <Icon name="download" size={13} /> {t.report.download}
        </button>
      </div>
      <div
        className="report-md"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  );
};

export const ResultsTabs = ({
  t,
  data,
}: {
  t: Translations;
  lang: Lang;
  data: GuardianResult;
}) => {
  const [tab, setTab] = useState<string>("issues");
  const showFiveWhy =
    data.docType === "incident" && (data.fiveWhy?.length ?? 0) > 0;

  const tabs = [
    {
      k: "issues",
      label: t.issues.title,
      icon: "list" as const,
      count: data.issues.length,
    },
    {
      k: "suggestions",
      label: t.suggestions.title,
      icon: "bulb" as const,
      count: data.suggestions.length,
    },
    ...(showFiveWhy
      ? [
          {
            k: "fiveWhy",
            label: t.fiveWhy.title,
            icon: "search" as const,
            count: data.fiveWhy!.length,
          },
        ]
      : []),
    {
      k: "report",
      label: t.report.title,
      icon: "file" as const,
      count: null as number | null,
    },
  ];

  return (
    <section className="card">
      <div className="tabs-strip">
        {tabs.map((tg) => (
          <button
            key={tg.k}
            className="tab-strip-btn"
            aria-selected={tab === tg.k}
            onClick={() => setTab(tg.k)}
          >
            <Icon name={tg.icon} size={13} />
            {tg.label}
            {tg.count !== null && (
              <span className="tab-strip-count">{tg.count}</span>
            )}
          </button>
        ))}
      </div>

      {tab === "issues" && <IssuesList t={t} issues={data.issues} />}
      {tab === "suggestions" && <Suggestions items={data.suggestions} />}
      {tab === "fiveWhy" && (
        <div>
          <div
            style={{
              padding: "12px 14px 0",
              color: "var(--text-muted)",
              fontSize: 12,
            }}
          >
            <Icon
              name="search"
              size={12}
              style={{ marginRight: 6 }}
            />
            {t.fiveWhy.sub}
          </div>
          <FiveWhy t={t} items={data.fiveWhy || []} />
        </div>
      )}
      {tab === "report" && <ReportPanel t={t} report={data.finalReport} />}
    </section>
  );
};
