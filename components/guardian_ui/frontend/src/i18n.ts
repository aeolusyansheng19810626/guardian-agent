import type { Lang } from "./types";

export interface Translations {
  appName: string;
  appTagline: string;
  appSubtitle: string;
  tabs: { delivery: string; incident: string };
  docTypeBadge: { delivery: string; incident: string };
  state: { idle: string; running: string; done: string };
  density: { compact: string; cozy: string };
  theme: { light: string; dark: string };
  input: {
    title: string;
    label: string;
    hint: string;
    placeholderDelivery: string;
    placeholderIncident: string;
    samples: string;
    sampleDelivery: string;
    sampleIncident: string;
    run: string;
    stop: string;
    clear: string;
    running: string;
  };
  pipeline: {
    title: string;
    subtitle: string;
    legendPending: string;
    legendRunning: string;
    legendDone: string;
    legendFlow: string;
    nodes: Record<string, string>;
    nodeRoles: Record<string, string>;
  };
  verdict: {
    pass: string;
    conditional: string;
    block: string;
    score: string;
    threshold: string;
    passLine: string;
    blockLine: string;
    latency: string;
    tokens: string;
    model: string;
    fallback: string;
    none: string;
    submittedAt: string;
  };
  breakdown: { title: string; weight: string; radarTitle: string };
  issues: {
    title: string;
    empty: string;
    severity: { high: string; med: string; low: string };
    filter: string;
  };
  suggestions: { title: string };
  fiveWhy: { title: string; sub: string; label: string; rootCause: string };
  report: { title: string; copy: string; download: string };
  history: {
    title: string;
    stats: { count: string; avg: string; pass: string };
    trend: string;
    passLine: string;
    blockLine: string;
    clear: string;
    empty: string;
  };
}

export const I18N: Record<Lang, Translations> = {
  zh: {
    appName: "Guardian Agent",
    appTagline: "多 Agent 质量审查 · LangGraph + Gemini + Groq",
    appSubtitle: "项目团队内部交付物 / 障害报告 质量审查平台",
    tabs: { delivery: "交付物审查", incident: "障害报告审查" },
    docTypeBadge: { delivery: "交付物", incident: "障害报告" },
    state: { idle: "空", running: "运行", done: "完成" },
    density: { compact: "紧凑", cozy: "舒适" },
    theme: { light: "浅色", dark: "深色" },
    input: {
      title: "提交内容",
      label: "粘贴文档内容",
      hint: "支持 Markdown · 最多 32k 字",
      placeholderDelivery: "粘贴需求 / 设计 / 测试计划等交付物正文…",
      placeholderIncident:
        "粘贴障害报告正文：发生时刻、根本原因、应急对应、再发防止策…",
      samples: "试试样例",
      sampleDelivery: "示例：系统需求文档（缺风险章节）",
      sampleIncident: "示例：服务器异常障害报告（5-Why 拦截）",
      run: "开始审查",
      stop: "停止",
      clear: "清空",
      running: "Agent 编排执行中…",
    },
    pipeline: {
      title: "Agent 编排实时进度",
      subtitle: "LangGraph DAG · 并行 fan-out + Guardian 加权裁决",
      legendPending: "等待",
      legendRunning: "执行中",
      legendDone: "已完成",
      legendFlow: "数据流",
      nodes: {
        classify: "文档分类",
        completeness: "完整性",
        quality: "质量",
        compliance: "格式合规",
        logic: "逻辑一致性",
        prevention: "再発防止",
        guardian: "Guardian 裁决",
        reporter: "报告生成",
      },
      nodeRoles: {
        classify: "Classifier",
        guardian: "LLM-as-judge",
        reporter: "Reporter",
        completeness: "Completeness Agent",
        quality: "Quality Agent",
        compliance: "Compliance Agent",
        logic: "Logic Agent",
        prevention: "Prevention Agent",
      },
    },
    verdict: {
      pass: "通过",
      conditional: "有条件通过",
      block: "拦截",
      score: "加权总分",
      threshold: "拦截 < 60 · 有条件 60–80 · 通过 ≥ 80",
      passLine: "通过线",
      blockLine: "拦截线",
      latency: "耗时",
      tokens: "Tokens",
      model: "主模型",
      fallback: "降级",
      none: "无",
      submittedAt: "提交时间",
    },
    breakdown: { title: "维度细分", weight: "权重", radarTitle: "维度雷达" },
    issues: {
      title: "问题清单",
      empty: "未发现问题，所有维度均符合要求。",
      severity: { high: "高", med: "中", low: "低" },
      filter: "全部维度",
    },
    suggestions: { title: "改进建议" },
    fiveWhy: {
      title: "5-Why 辅助分析",
      sub: "辅助内容 · 不计入硬性扣分",
      label: "Why",
      rootCause: "根本原因",
    },
    report: { title: "完整报告", copy: "复制", download: "下载 .md" },
    history: {
      title: "提交历史",
      stats: { count: "提交", avg: "平均分", pass: "通过率" },
      trend: "分数趋势",
      passLine: "通过 80",
      blockLine: "拦截 60",
      clear: "清空历史",
      empty: "暂无历史",
    },
  },
  ja: {
    appName: "Guardian Agent",
    appTagline: "マルチAgent 品質レビュー · LangGraph + Gemini + Groq",
    appSubtitle: "プロジェクト内部の成果物 / 障害報告 品質レビュー基盤",
    tabs: { delivery: "成果物レビュー", incident: "障害報告レビュー" },
    docTypeBadge: { delivery: "成果物", incident: "障害報告" },
    state: { idle: "未実行", running: "実行中", done: "完了" },
    density: { compact: "コンパクト", cozy: "ゆったり" },
    theme: { light: "ライト", dark: "ダーク" },
    input: {
      title: "入力",
      label: "ドキュメント本文を貼り付け",
      hint: "Markdown 対応 · 最大 32k 文字",
      placeholderDelivery:
        "要件 / 設計 / テスト計画などの成果物本文を貼り付け…",
      placeholderIncident:
        "障害報告本文：発生時刻・根本原因・暫定対応・再発防止策など",
      samples: "サンプル",
      sampleDelivery: "サンプル：要件定義書（リスク章欠落）",
      sampleIncident: "サンプル：サーバ異常 障害報告（5-Why 拒否）",
      run: "レビュー開始",
      stop: "停止",
      clear: "クリア",
      running: "Agent 実行中…",
    },
    pipeline: {
      title: "Agent オーケストレーション",
      subtitle: "LangGraph DAG · 並列 fan-out + Guardian 重み付け判定",
      legendPending: "待機",
      legendRunning: "実行中",
      legendDone: "完了",
      legendFlow: "データフロー",
      nodes: {
        classify: "文書分類",
        completeness: "完全性",
        quality: "品質",
        compliance: "形式遵守",
        logic: "論理整合",
        prevention: "再発防止",
        guardian: "Guardian 判定",
        reporter: "レポート生成",
      },
      nodeRoles: {
        classify: "Classifier",
        guardian: "LLM-as-judge",
        reporter: "Reporter",
        completeness: "Completeness Agent",
        quality: "Quality Agent",
        compliance: "Compliance Agent",
        logic: "Logic Agent",
        prevention: "Prevention Agent",
      },
    },
    verdict: {
      pass: "合格",
      conditional: "条件付き合格",
      block: "拒否",
      score: "重み付け総合スコア",
      threshold: "拒否 < 60 · 条件付き 60–80 · 合格 ≥ 80",
      passLine: "合格ライン",
      blockLine: "拒否ライン",
      latency: "所要時間",
      tokens: "トークン",
      model: "主モデル",
      fallback: "フォールバック",
      none: "なし",
      submittedAt: "提出時刻",
    },
    breakdown: { title: "次元別スコア", weight: "重み", radarTitle: "レーダー" },
    issues: {
      title: "指摘事項",
      empty: "問題は検出されませんでした。",
      severity: { high: "高", med: "中", low: "低" },
      filter: "全次元",
    },
    suggestions: { title: "改善提案" },
    fiveWhy: {
      title: "5-Why 補助分析",
      sub: "参考情報 · 減点対象外",
      label: "Why",
      rootCause: "根本原因",
    },
    report: { title: "詳細レポート", copy: "コピー", download: ".md ダウンロード" },
    history: {
      title: "履歴",
      stats: { count: "提出", avg: "平均", pass: "合格率" },
      trend: "スコア推移",
      passLine: "合格 80",
      blockLine: "拒否 60",
      clear: "履歴クリア",
      empty: "履歴なし",
    },
  },
  en: {
    appName: "Guardian Agent",
    appTagline: "Multi-agent quality review · LangGraph + Gemini + Groq",
    appSubtitle: "Internal QA platform for deliverables & incident reports",
    tabs: { delivery: "Deliverable", incident: "Incident report" },
    docTypeBadge: { delivery: "Deliverable", incident: "Incident" },
    state: { idle: "Idle", running: "Running", done: "Done" },
    density: { compact: "Compact", cozy: "Cozy" },
    theme: { light: "Light", dark: "Dark" },
    input: {
      title: "Submit",
      label: "Paste document",
      hint: "Markdown supported · up to 32k chars",
      placeholderDelivery:
        "Paste a spec, design, test plan or any deliverable…",
      placeholderIncident:
        "Paste an incident report: timestamps, root cause, mitigation, prevention…",
      samples: "Samples",
      sampleDelivery: "Sample: requirements doc (missing risk section)",
      sampleIncident: "Sample: server outage incident (5-Why block)",
      run: "Run review",
      stop: "Stop",
      clear: "Clear",
      running: "Agents running…",
    },
    pipeline: {
      title: "Agent orchestration",
      subtitle: "LangGraph DAG · parallel fan-out + Guardian weighted judgement",
      legendPending: "Pending",
      legendRunning: "Running",
      legendDone: "Done",
      legendFlow: "Data flow",
      nodes: {
        classify: "Classify",
        completeness: "Completeness",
        quality: "Quality",
        compliance: "Compliance",
        logic: "Logic",
        prevention: "Prevention",
        guardian: "Guardian",
        reporter: "Reporter",
      },
      nodeRoles: {
        classify: "Classifier",
        guardian: "LLM-as-judge",
        reporter: "Reporter",
        completeness: "Completeness Agent",
        quality: "Quality Agent",
        compliance: "Compliance Agent",
        logic: "Logic Agent",
        prevention: "Prevention Agent",
      },
    },
    verdict: {
      pass: "Pass",
      conditional: "Conditional",
      block: "Block",
      score: "Weighted score",
      threshold: "Block < 60 · Conditional 60–80 · Pass ≥ 80",
      passLine: "Pass line",
      blockLine: "Block line",
      latency: "Latency",
      tokens: "Tokens",
      model: "Primary",
      fallback: "Fallback",
      none: "None",
      submittedAt: "Submitted",
    },
    breakdown: { title: "Score breakdown", weight: "Weight", radarTitle: "Radar" },
    issues: {
      title: "Findings",
      empty: "No issues found, all dimensions pass.",
      severity: { high: "High", med: "Med", low: "Low" },
      filter: "All dims",
    },
    suggestions: { title: "Suggestions" },
    fiveWhy: {
      title: "5-Why assist",
      sub: "Advisory · does not affect score",
      label: "Why",
      rootCause: "Root cause",
    },
    report: { title: "Full report", copy: "Copy", download: "Download .md" },
    history: {
      title: "Submission history",
      stats: { count: "Runs", avg: "Avg", pass: "Pass rate" },
      trend: "Score trend",
      passLine: "Pass 80",
      blockLine: "Block 60",
      clear: "Clear history",
      empty: "No history yet",
    },
  },
};
