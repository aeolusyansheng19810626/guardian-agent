export type Lang = "zh" | "ja" | "en";
export type Theme = "light" | "dark";
export type Density = "cozy" | "compact";
export type Tab = "delivery" | "incident";
export type DemoState = "idle" | "running" | "done";
export type Verdict = "pass" | "conditional" | "block";
export type Severity = "high" | "med" | "low";
export type Dim =
  | "completeness"
  | "quality"
  | "compliance"
  | "logic"
  | "prevention";
export type NodeKey = "classify" | "guardian" | "reporter" | Dim;

export interface NodeRuntime {
  status: "pending" | "running" | "done";
  pct?: number;
  totalScore?: number;
}

export type Runtime = Partial<Record<NodeKey, NodeRuntime>>;

export interface BreakdownEntry {
  score: number;
  weight: number;
}

export interface IssueItem {
  severity: Severity;
  dimension: Dim | string;
  text: string;
}

export interface HistoryItem {
  idx: number;
  score: number;
  verdict: Verdict;
  docType: Tab;
  ts: string;
  title: string;
}

export interface GuardianResult {
  docType: Tab;
  verdict: Verdict;
  totalScore: number;
  breakdown: Partial<Record<Dim, BreakdownEntry>>;
  issues: IssueItem[];
  suggestions: string[];
  fiveWhy?: string[];
  finalReport: string;
  fallback: string | null;
  submittedAt: string;
  latencyMs: number;
  tokens: number;
  primaryModel: string;
}

export interface GuardianArgs {
  lang: Lang;
  theme: Theme;
  paletteColor: string;
  density: Density;
  tab: Tab;
  state: DemoState;
  inputText: string;
  runtime: Runtime;
  result: GuardianResult | null;
  history: HistoryItem[];
  fallbackEvents: string[];
  selectedHistoryIdx: number | null;
}

export type GuardianEvent =
  | { type: "RUN"; text: string; tab: Tab }
  | { type: "POLL" }
  | { type: "CLEAR_INPUT" }
  | { type: "SET_INPUT"; text: string }
  | { type: "SET_TAB"; tab: Tab }
  | { type: "SET_LANG"; lang: Lang }
  | { type: "SET_THEME"; theme: Theme }
  | { type: "SET_PALETTE"; color: string }
  | { type: "SET_DENSITY"; density: Density }
  | { type: "SELECT_HISTORY"; idx: number }
  | { type: "CLEAR_HISTORY" }
  | { type: "USE_SAMPLE" };
