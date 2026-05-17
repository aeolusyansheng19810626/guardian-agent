---
title: Guardian Agent
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.39.0
app_file: app.py
pinned: false
license: mit
---

# Guardian Agent

面向项目团队日常交付物与障害报告的多 Agent 质量审查平台（演示版）。

## 功能

- **双场景**：交付物审查（系统需求文档 / 设计文档等）与 障害报告审查。
- **并行子 Agent**：完整性 / 质量 / 格式合规 / 逻辑一致性（障害模式额外启用 再発防止 Agent）。
- **Guardian 裁决**：Gemini 2.5 Pro 做 LLM-as-a-judge，输出加权总分与判定（通过 / 有条件通过 / 拦截）。
- **障害报告 5-Why 辅助**：根本原因表面化时自动生成 5-Why 链条（仅供参考，不计入硬扣分）。
- **实时 Pipeline DAG**：LangGraph 节点状态实时可视化（pending / running / done），后台线程跑 graph，前端 600ms 轮询拉取进度。
- **可视化**：Verdict gauge / 维度雷达 / 维度条形 / 分数趋势 sparkline，全部自写 SVG。
- **个性化**：浅 / 深主题、emerald / teal / indigo / blue / violet 五主色、舒适 / 紧凑两种密度、中 / 日 / 英三语切换。
- **报告导出**：完整 Markdown 报告支持复制和下载（带时间戳文件名）。
- **可观测性**：LangSmith trace。
- **降级机制**：Gemini Pro → Flash → Groq Llama-3.3-70B。

## 技术栈

- 编排：LangGraph（并行 fan-out + 条件路由）
- LLM：Gemini 2.5 Pro / Flash（Vertex AI OpenAI 兼容端点）+ Groq Llama-3.3-70B
- UI：Streamlit + 自定义 React 18 组件（vite + TypeScript），通过 `streamlit-component-lib` 双向通信
- 可视化：原生 SVG（无第三方图表库）

## 项目结构

```
guardian-agent/
├── app.py                      # Streamlit controller：session_state、event 派发、graph.stream worker thread
├── config.py                   # 模型 / 权重 / 阈值 / 认证集中配置
├── requirements.txt
├── .env.example
├── .github/workflows/
│   └── sync-to-hf.yml          # push 后自动同步到 HF Space
├── components/
│   └── guardian_ui/            # 自定义 Streamlit React 组件
│       ├── __init__.py         # declare_component（支持 GUARDIAN_UI_DEV=1 走 vite dev server）
│       └── frontend/           # vite + React + TS 工程
│           ├── package.json
│           ├── vite.config.ts
│           ├── README.md       # build / dev 命令
│           └── src/
│               ├── App.tsx
│               ├── main.tsx
│               ├── StreamlitBridge.ts       # useStreamlitArgs + sendEvent
│               ├── i18n.ts                  # 中 / 日 / 英三语
│               ├── Icons.tsx
│               ├── styles.css               # 设计 tokens + 全部组件样式
│               ├── types.ts
│               └── components/              # TopBar / Sidebar / InputPanel / Pipeline / Results
├── graph/
│   ├── state.py                # AgentState (TypedDict + reducer)
│   ├── builder.py              # LangGraph 图组装：classify → 并行 → guardian → reporter
│   └── guardian_node.py        # Guardian 加权裁决 + LLM-as-a-judge
├── agents/
│   ├── base.py                 # 共用 schema / prompt 模板 / 降级回调
│   ├── completeness.py         # 完整性（Groq 优先）
│   ├── quality.py              # 质量（Gemini Flash + 障害模式 5-Why）
│   ├── compliance.py           # 格式合规（Gemini Flash）
│   ├── logic.py                # 逻辑一致性（Gemini Flash）
│   └── prevention.py           # 再発防止（Gemini Flash，仅障害模式）
├── reporter/
│   └── generator.py            # Gemini Pro 生成 Markdown 报告 + 退化模板
├── rules/
│   ├── incident_rules.md       # 障害报告评估规则
│   └── delivery_rules.md       # 交付物评估规则
├── utils/
│   ├── classifier.py           # 文档类型识别（关键词 + LLM 兜底）
│   └── llm_factory.py          # 三家 LLM 工厂 + 降级链 + Vertex AI access token
├── tests/
│   └── ui_smoke.py             # Playwright 端到端 UI 烟测（8 项断言）
└── deliverable/                # Claude Design 高保真原型与截图（重构参考用）
```

## HuggingFace Spaces Secrets

在 Space → Settings → Variables and secrets 配置：

| 名称 | 必需 | 说明 |
|---|---|---|
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | ✅ | Vertex AI Service Account JSON 文件**全部内容**（直接粘贴） |
| `GROQ_API_KEY` | ✅ | Groq API Key |
| `LANGCHAIN_API_KEY` | 可选 | 配置后自动开启 LangSmith trace |
| `GOOGLE_CLOUD_PROJECT` | 可选 | 默认 `yansheng-project` |
| `GOOGLE_CLOUD_REGION` | 可选 | 默认 `us-central1` |

> Service Account 需开启 `aiplatform.user` 角色，作用域 `https://www.googleapis.com/auth/cloud-platform`。代码用 `google-auth` 自动刷新 access token 传给 Vertex AI OpenAI 兼容端点。

## 本地运行

### 1. 克隆仓库

```bash
git clone https://github.com/aeolusyansheng19810626/guardian-agent.git
cd guardian-agent
```

### 2. 创建虚拟环境并安装依赖

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，至少填写：

- `GROQ_API_KEY`：从 https://console.groq.com 获取
- Vertex AI 认证（二选一）：
  - `GOOGLE_APPLICATION_CREDENTIALS=/绝对路径/sa.json`（指向本地 service account JSON 文件），**或**
  - 先运行 `gcloud auth application-default login` 使用 ADC
- `LANGCHAIN_API_KEY`（可选）：开启 LangSmith trace
- `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_REGION`：默认 `yansheng-project` / `us-central1`，按需覆盖

### 4. 构建前端组件

UI 是 vite 编译的 React 组件。提交到仓库的 `components/guardian_ui/frontend/dist/` 是预编译产物，正常情况下**无需重新构建**就能直接 `streamlit run`。

如果你修改了 `frontend/src/` 下的源码，再编译一次：

```bash
cd components/guardian_ui/frontend
npm install   # 仅首次
npm run build
cd ../../..
```

也可以开 vite dev server（HMR 热更新）：

```bash
# 终端 1
cd components/guardian_ui/frontend && npm run dev   # localhost:5173

# 终端 2（仓库根目录）
# Windows PowerShell
$env:GUARDIAN_UI_DEV = "1"; streamlit run app.py
# macOS / Linux
GUARDIAN_UI_DEV=1 streamlit run app.py
```

### 5. 启动

```bash
streamlit run app.py
```

浏览器打开 http://localhost:8501

### 6. （可选）自动同步到 HuggingFace Space

仓库已配置 `.github/workflows/sync-to-hf.yml`：每次 push 到 `main` 自动镜像到 HF Space。
启用方法：在 GitHub 仓库 Secrets 添加 `HF_TOKEN`（HuggingFace Write token）。

> HF Streamlit SDK 不会执行 `npm run build`，所以仓库内必须有 `frontend/dist/` 的产物。已通过 `.gitignore` 强制让 `dist/` 受 git 追踪。

## 端到端 UI 烟测

```bash
pip install playwright pytest-playwright
python -m playwright install chromium
python tests/ui_smoke.py
```

会自动启 streamlit + 无头 chromium 跑 8 项断言（idle / Tab 切换 / 三语 / 样例 / 清空 / 主题 / 主色 / Run 触发）。

## 测试样例

**障害报告（不合格）**：
```
2024年3月15日14:00系统发生障害。原因：服务器异常。対応：重启服务器。防止策：加强监控。
```
预期：Guardian 拦截，5-Why 区域出现。

**交付物（有条件通过）**：
```
系统需求文档，包含功能需求、非功能需求（系统响应要快）、系统架构图，缺少风险章节。
```
预期：有条件通过。
