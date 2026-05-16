import { Icon } from "../Icons";
import type { Tab } from "../types";
import type { Translations } from "../i18n";

interface InputPanelProps {
  t: Translations;
  docType: Tab;
  value: string;
  onChange: (v: string) => void;
  onRun: () => void;
  onClear: () => void;
  onSample: () => void;
  running: boolean;
}

export const InputPanel = ({
  t,
  docType,
  value,
  onChange,
  onRun,
  onClear,
  onSample,
  running,
}: InputPanelProps) => {
  const placeholder =
    docType === "incident"
      ? t.input.placeholderIncident
      : t.input.placeholderDelivery;

  const sample =
    docType === "incident" ? t.input.sampleIncident : t.input.sampleDelivery;
  const charCount = value.length;

  return (
    <section className="card" style={{ display: "flex", flexDirection: "column" }}>
      <div className="card-header">
        <div className="card-title">
          <Icon name="upload" size={14} />
          {t.input.title}
          <span className="badge brand" style={{ marginLeft: 6 }}>
            <Icon name={docType === "incident" ? "siren" : "package"} size={11} />
            {t.docTypeBadge[docType]}
          </span>
        </div>
        <div className="card-actions">
          <span className="text-xs mono faint">
            {charCount.toLocaleString()} / 32,000
          </span>
        </div>
      </div>

      <div
        className="card-body"
        style={{ display: "flex", flexDirection: "column", gap: 12 }}
      >
        <div>
          <div className="field-label">
            <span>{t.input.label}</span>
            <span className="hint">{t.input.hint}</span>
          </div>
          <textarea
            className="textarea"
            placeholder={placeholder}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            spellCheck={false}
          />
        </div>

        <div className="sample-bar">
          <span
            className="text-xs faint"
            style={{ marginRight: 6, alignSelf: "center" }}
          >
            <Icon name="sparkles" size={11} style={{ marginRight: 4 }} />
            {t.input.samples}:
          </span>
          <button className="sample-chip" onClick={onSample}>
            <Icon name={docType === "incident" ? "siren" : "package"} size={11} />
            {sample}
          </button>
        </div>

        <div className="row" style={{ gap: 10, marginTop: 4 }}>
          {!running ? (
            <button
              className="btn btn-primary btn-lg"
              onClick={onRun}
              style={{ flex: 1 }}
            >
              <Icon name="rocket" size={15} />
              {t.input.run}
            </button>
          ) : (
            <button className="btn btn-primary btn-lg" disabled style={{ flex: 1 }}>
              <span className="spinner" />
              {t.input.running}
            </button>
          )}
          <button className="btn btn-lg" onClick={onClear}>
            <Icon name="x" size={14} />
            {t.input.clear}
          </button>
        </div>
      </div>
    </section>
  );
};
