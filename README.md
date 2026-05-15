---
title: Guardian Agent
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: false
license: mit
---

# Guardian Agent

面向 IBM 项目团队日常交付物与障害报告的多 Agent 质量审查平台（演示版）。

## 功能

- **双场景**：交付物审查（系统需求文档/设计文档等）与 障害报告审查。
- **并行子 Agent**：完整性 / 质量 / 格式合规 / 逻辑一致性（障害模式额外启用 再発防止 Agent）。
- **Guardian 裁决**：Gemini 2.5 Pro 做 LLM-as-a-judge，输出加权总分与判定（通过 / 有条件通过 / 拦截）。
- **障害报告 5-Why 辅助**：当根本原因表面化时自动生成 5-Why 链条，作为辅助内容（不算硬性拦截项）。
- **可视化**：plotly 雷达图 + 会话内提交分数趋势折线图。
- **可观测性**：LangSmith trace。
- **降级机制**：Gemini Pro → Flash → Groq Llama-3.3-70B。

## 技术栈

- 编排：LangGraph（并行 fan-out + 条件路由）
- LLM：Gemini 2.5 Pro / Flash（Vertex AI OpenAI 兼容端点）+ Groq Llama-3.3-70B
- UI：Streamlit
- 可视化：Plotly

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

```bash
pip install -r requirements.txt
cp .env.example .env  # 填入 API Key
streamlit run app.py
```

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
