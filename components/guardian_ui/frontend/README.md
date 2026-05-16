# guardian_ui frontend

Vite + React 18 + TypeScript. Built artifact is loaded by the Streamlit
custom component declared in `components/guardian_ui/__init__.py`.

## Build (production)

```bash
cd components/guardian_ui/frontend
npm install
npm run build
```

This emits `dist/` next to `package.json`. Streamlit's `declare_component` is
configured to load from that path. Then run the app from the repo root:

```bash
streamlit run app.py
```

## Dev mode (hot reload)

```bash
# terminal 1
cd components/guardian_ui/frontend
npm run dev          # serves on http://localhost:5173

# terminal 2 (repo root)
GUARDIAN_UI_DEV=1 streamlit run app.py
# Windows PowerShell: $env:GUARDIAN_UI_DEV=1; streamlit run app.py
```

The Python side switches to `url=http://localhost:5173` when
`GUARDIAN_UI_DEV` is truthy; you get Vite HMR for everything in `src/`.

## Layout

```
src/
├── App.tsx              # Top-level layout, args→props plumbing
├── main.tsx             # ReactDOM bootstrap
├── StreamlitBridge.ts   # useStreamlitArgs + sendEvent
├── i18n.ts              # zh / ja / en translations
├── Icons.tsx            # SVG icon set + BrandMark
├── styles.css           # Design tokens + all component styles (1196 lines)
├── types.ts             # GuardianArgs / GuardianEvent / Result types
└── components/
    ├── TopBar.tsx
    ├── Sidebar.tsx
    ├── InputPanel.tsx
    ├── Pipeline.tsx
    └── Results.tsx
```

## Streamlit ↔ React contract

**Python → React** (args, every rerun):

```ts
GuardianArgs {
  lang, theme, paletteColor, density, tab, state,
  inputText, runtime, result, history,
  fallbackEvents, selectedHistoryIdx,
}
```

**React → Python** (events):

```ts
GuardianEvent =
  | { type: "RUN", text, tab }
  | { type: "USE_SAMPLE" } | { type: "CLEAR_INPUT" }
  | { type: "SET_TAB" | "SET_LANG" | "SET_THEME" | "SET_PALETTE" | "SET_DENSITY", ... }
  | { type: "SELECT_HISTORY" | "CLEAR_HISTORY", ... }
```

Each event carries `_ts` so the controller can dedup repeated values.
