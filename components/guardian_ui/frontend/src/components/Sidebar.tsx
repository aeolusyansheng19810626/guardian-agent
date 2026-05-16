import { Icon } from "../Icons";
import type { HistoryItem, Lang } from "../types";
import type { Translations } from "../i18n";

const TrendMini = ({ history }: { history: HistoryItem[] }) => {
  const points = [...history].reverse().map((h) => h.score);
  if (points.length === 0) return null;

  const W = 240,
    H = 56,
    PAD = 6;
  const maxX = Math.max(points.length - 1, 1);
  const xs = points.map((_, i) => PAD + (i / maxX) * (W - PAD * 2));
  const ys = points.map((s) => PAD + (1 - s / 100) * (H - PAD * 2));

  const path = xs
    .map((x, i) => `${i ? "L" : "M"}${x.toFixed(1)},${ys[i].toFixed(1)}`)
    .join(" ");
  const area = `${path} L ${xs[xs.length - 1].toFixed(1)},${H - PAD} L ${xs[0].toFixed(1)},${H - PAD} Z`;

  const passY = PAD + (1 - 80 / 100) * (H - PAD * 2);
  const blockY = PAD + (1 - 60 / 100) * (H - PAD * 2);

  return (
    <svg className="trend-svg" viewBox={`0 0 ${W} ${H}`}>
      <defs>
        <linearGradient id="trend-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--brand-500)" stopOpacity="0.35" />
          <stop offset="100%" stopColor="var(--brand-500)" stopOpacity="0" />
        </linearGradient>
      </defs>
      <line
        x1={0}
        x2={W}
        y1={passY}
        y2={passY}
        stroke="var(--ok-500)"
        strokeDasharray="2 3"
        opacity="0.6"
      />
      <line
        x1={0}
        x2={W}
        y1={blockY}
        y2={blockY}
        stroke="var(--warn-500)"
        strokeDasharray="2 3"
        opacity="0.6"
      />
      <path d={area} fill="url(#trend-grad)" />
      <path d={path} fill="none" stroke="var(--brand-600)" strokeWidth="1.6" />
      {xs.map((x, i) => {
        const s = points[i];
        const color =
          s >= 80
            ? "var(--ok-500)"
            : s >= 60
            ? "var(--warn-500)"
            : "var(--bad-500)";
        return (
          <circle
            key={i}
            cx={x}
            cy={ys[i]}
            r="2.2"
            fill={color}
            stroke="var(--bg-elev)"
            strokeWidth="1"
          />
        );
      })}
    </svg>
  );
};

interface SidebarProps {
  t: Translations;
  lang: Lang;
  history: HistoryItem[];
  selectedIdx: number | null;
  onSelect: (idx: number) => void;
  onClear: () => void;
}

export const Sidebar = ({
  t,
  history,
  selectedIdx,
  onSelect,
  onClear,
}: SidebarProps) => {
  const count = history.length;
  const avg = count ? history.reduce((a, h) => a + h.score, 0) / count : 0;
  const passRate = count
    ? (history.filter((h) => h.verdict === "pass").length / count) * 100
    : 0;

  return (
    <aside className="sidebar">
      <div>
        <h3 className="sidebar-section-title">{t.history.title}</h3>
        <div className="stat-grid">
          <div className="stat">
            <div className="stat-label">{t.history.stats.count}</div>
            <div className="stat-value">{count}</div>
          </div>
          <div className="stat">
            <div className="stat-label">{t.history.stats.avg}</div>
            <div className="stat-value">{avg.toFixed(1)}</div>
          </div>
          <div className="stat" style={{ gridColumn: "span 2" }}>
            <div className="stat-label">{t.history.stats.pass}</div>
            <div className="row" style={{ alignItems: "baseline", gap: 10 }}>
              <div className="stat-value">
                {passRate.toFixed(0)}
                <span style={{ fontSize: 14, color: "var(--text-faint)" }}>
                  %
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div className="trend-card">
          <div className="trend-card-head">
            <span className="trend-card-title">{t.history.trend}</span>
            <span className="text-xs faint mono">{count} runs</span>
          </div>
          <TrendMini history={history} />
          <div
            className="row text-xs faint mono"
            style={{ justifyContent: "space-between", marginTop: 4 }}
          >
            <span>0</span>
            <span style={{ color: "var(--ok-500)" }}>— {t.history.passLine}</span>
            <span style={{ color: "var(--warn-500)" }}>— {t.history.blockLine}</span>
            <span>100</span>
          </div>
        </div>
      </div>

      <div
        style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}
      >
        <h3 className="sidebar-section-title">
          <Icon
            name="history"
            size={11}
            style={{ verticalAlign: "middle", marginRight: 4 }}
          />
          Recent
        </h3>
        <div className="history-list scrollable" style={{ flex: 1 }}>
          {history.length === 0 && (
            <div className="text-sm faint" style={{ padding: 10 }}>
              {t.history.empty}
            </div>
          )}
          {history.map((h) => (
            <button
              key={h.idx}
              className="history-item"
              aria-selected={selectedIdx === h.idx}
              onClick={() => onSelect(h.idx)}
            >
              <span className={`history-dot ${h.verdict}`} />
              <span className="history-main">
                <span className="history-title">
                  <span
                    className="text-xs faint mono"
                    style={{ marginRight: 6 }}
                  >
                    #{h.idx}
                  </span>
                  {h.title}
                </span>
                <span className="history-meta">
                  {t.docTypeBadge[h.docType]} · {h.ts}
                </span>
              </span>
              <span className="history-score">{h.score}</span>
            </button>
          ))}
        </div>
      </div>

      <button
        className="btn btn-ghost"
        style={{ justifyContent: "center" }}
        onClick={onClear}
      >
        <Icon name="trash" size={14} />
        {t.history.clear}
      </button>
    </aside>
  );
};
