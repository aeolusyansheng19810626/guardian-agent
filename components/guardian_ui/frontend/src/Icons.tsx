import type { CSSProperties, SVGProps } from "react";

export type IconName =
  | "shield"
  | "package"
  | "siren"
  | "play"
  | "stop"
  | "rocket"
  | "sparkles"
  | "branch"
  | "check"
  | "x"
  | "sun"
  | "moon"
  | "globe"
  | "history"
  | "trash"
  | "chevronLeft"
  | "chevronRight"
  | "chevronDown"
  | "settings"
  | "copy"
  | "download"
  | "clipboard"
  | "bulb"
  | "search"
  | "flow"
  | "layers"
  | "list"
  | "plus"
  | "upload"
  | "activity"
  | "file"
  | "chart"
  | "target"
  | "cpu"
  | "bell"
  | "code"
  | "user";

interface IconProps extends Omit<SVGProps<SVGSVGElement>, "name"> {
  name: IconName;
  size?: number;
  style?: CSSProperties;
}

const PATHS: Record<IconName, JSX.Element> = {
  shield: <path d="M12 2 4 5v7c0 5 3.4 8.4 8 10 4.6-1.6 8-5 8-10V5l-8-3Z" />,
  package: (
    <>
      <path d="M3 7.5 12 3l9 4.5v9L12 21l-9-4.5v-9Z" />
      <path d="m3 7.5 9 4.5 9-4.5" />
      <path d="M12 12v9" />
    </>
  ),
  siren: (
    <>
      <path d="M7 18v-6a5 5 0 0 1 10 0v6" />
      <path d="M5 21h14" />
      <path d="M12 4V2" />
      <path d="m4.5 7-1-1" />
      <path d="m20.5 7 1-1" />
    </>
  ),
  play: <path d="M6 4v16l14-8L6 4Z" fill="currentColor" stroke="none" />,
  stop: <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor" stroke="none" />,
  rocket: (
    <>
      <path d="M5 13c-2 1-3 4-3 6 2 0 5-1 6-3" />
      <path d="M21 3s-5-1-9 3l-3 3-3 1 3 3 1 3 3-3 3-3c4-4 3-9 3-9-3 0-5 1-5 1" />
      <circle cx="14" cy="10" r="1.5" />
    </>
  ),
  sparkles: (
    <>
      <path d="M12 3v4" />
      <path d="M12 17v4" />
      <path d="M3 12h4" />
      <path d="M17 12h4" />
      <path d="m6 6 2 2" />
      <path d="m16 16 2 2" />
      <path d="m6 18 2-2" />
      <path d="m16 8 2-2" />
    </>
  ),
  branch: (
    <>
      <circle cx="6" cy="5" r="2" />
      <circle cx="6" cy="19" r="2" />
      <circle cx="18" cy="12" r="2" />
      <path d="M6 7v10" />
      <path d="M6 12c0-3 3-5 6-5h4" />
    </>
  ),
  check: <path d="m5 12 5 5 9-11" />,
  x: (
    <>
      <path d="M6 6l12 12" />
      <path d="M18 6 6 18" />
    </>
  ),
  sun: (
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2" />
      <path d="M12 20v2" />
      <path d="m4.9 4.9 1.4 1.4" />
      <path d="m17.7 17.7 1.4 1.4" />
      <path d="M2 12h2" />
      <path d="M20 12h2" />
      <path d="m6.3 17.7-1.4 1.4" />
      <path d="m19.1 4.9-1.4 1.4" />
    </>
  ),
  moon: <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />,
  globe: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18" />
      <path d="M12 3a14 14 0 0 1 0 18" />
      <path d="M12 3a14 14 0 0 0 0 18" />
    </>
  ),
  history: (
    <>
      <path d="M3 12a9 9 0 1 0 3-6.7" />
      <polyline points="3 4 3 9 8 9" />
      <path d="M12 7v5l3 2" />
    </>
  ),
  trash: (
    <>
      <path d="M3 6h18" />
      <path d="M8 6v-2a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      <path d="M5 6h14l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6Z" />
    </>
  ),
  chevronLeft: <path d="m15 6-6 6 6 6" />,
  chevronRight: <path d="m9 6 6 6-6 6" />,
  chevronDown: <path d="m6 9 6 6 6-6" />,
  settings: (
    <>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a7.7 7.7 0 0 0 .1-3 7.7 7.7 0 0 0-.1-3l2.1-1.6-2-3.4-2.4 1a8 8 0 0 0-2.6-1.5L14 1h-4l-.5 2.5a8 8 0 0 0-2.6 1.5l-2.4-1-2 3.4L4.6 9a7.7 7.7 0 0 0 0 6l-2.1 1.6 2 3.4 2.4-1a8 8 0 0 0 2.6 1.5L10 23h4l.5-2.5a8 8 0 0 0 2.6-1.5l2.4 1 2-3.4-2.1-1.6Z" />
    </>
  ),
  copy: (
    <>
      <rect x="9" y="9" width="13" height="13" rx="2" />
      <path d="M5 15V5a2 2 0 0 1 2-2h10" />
    </>
  ),
  download: (
    <>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <path d="M7 10l5 5 5-5" />
      <path d="M12 15V3" />
    </>
  ),
  clipboard: (
    <>
      <rect x="6" y="4" width="12" height="18" rx="2" />
      <rect x="9" y="2" width="6" height="4" rx="1" />
    </>
  ),
  bulb: (
    <>
      <path d="M9 18h6" />
      <path d="M10 22h4" />
      <path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.4 1 2.3v1h6v-1c0-.9.4-1.8 1-2.3A7 7 0 0 0 12 2Z" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </>
  ),
  flow: (
    <>
      <rect x="3" y="3" width="6" height="6" rx="1" />
      <rect x="15" y="15" width="6" height="6" rx="1" />
      <path d="M9 6h6a3 3 0 0 1 3 3v6" />
    </>
  ),
  layers: (
    <>
      <path d="M12 2 2 8l10 6 10-6-10-6Z" />
      <path d="m2 16 10 6 10-6" />
      <path d="m2 12 10 6 10-6" />
    </>
  ),
  list: (
    <>
      <line x1="8" y1="6" x2="21" y2="6" />
      <line x1="8" y1="12" x2="21" y2="12" />
      <line x1="8" y1="18" x2="21" y2="18" />
      <circle cx="4" cy="6" r="1" fill="currentColor" stroke="none" />
      <circle cx="4" cy="12" r="1" fill="currentColor" stroke="none" />
      <circle cx="4" cy="18" r="1" fill="currentColor" stroke="none" />
    </>
  ),
  plus: (
    <>
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </>
  ),
  upload: (
    <>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <path d="M17 8l-5-5-5 5" />
      <path d="M12 3v12" />
    </>
  ),
  activity: <path d="M3 12h4l2-7 4 14 2-7h6" />,
  file: (
    <>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6Z" />
      <path d="M14 2v6h6" />
    </>
  ),
  chart: (
    <>
      <path d="M3 3v18h18" />
      <path d="m7 14 4-4 4 4 5-6" />
    </>
  ),
  target: (
    <>
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none" />
    </>
  ),
  cpu: (
    <>
      <rect x="5" y="5" width="14" height="14" rx="2" />
      <rect x="9" y="9" width="6" height="6" />
      <path d="M9 2v3" />
      <path d="M15 2v3" />
      <path d="M9 19v3" />
      <path d="M15 19v3" />
      <path d="M2 9h3" />
      <path d="M2 15h3" />
      <path d="M19 9h3" />
      <path d="M19 15h3" />
    </>
  ),
  bell: (
    <>
      <path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
      <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
    </>
  ),
  code: (
    <>
      <polyline points="16 18 22 12 16 6" />
      <polyline points="8 6 2 12 8 18" />
    </>
  ),
  user: (
    <>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 22c0-4 4-7 8-7s8 3 8 7" />
    </>
  ),
};

export const Icon = ({ name, size = 16, style, ...rest }: IconProps) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    style={style}
    {...rest}
  >
    {PATHS[name]}
  </svg>
);

export const BrandMark = ({ size = 28 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 28 28" fill="none">
    <defs>
      <linearGradient id="g-shield" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor="var(--brand-400)" />
        <stop offset="1" stopColor="var(--brand-700)" />
      </linearGradient>
    </defs>
    <path
      d="M14 3 5 6v6.5C5 18 8.6 21.8 14 23.5 19.4 21.8 23 18 23 12.5V6L14 3Z"
      fill="url(#g-shield)"
    />
    <path
      d="M14 3 5 6v6.5C5 18 8.6 21.8 14 23.5 19.4 21.8 23 18 23 12.5V6L14 3Z"
      stroke="rgba(255,255,255,0.25)"
    />
    <path
      d="M17.2 11.5h-3v1.6h1.7c-.18 1.05-1.05 1.7-2.05 1.7-1.45 0-2.5-1.1-2.5-2.55s1.05-2.55 2.5-2.55c.7 0 1.3.25 1.75.65l1.15-1.15A4.05 4.05 0 0 0 13.35 8.05a4.1 4.1 0 0 0-4.15 4.2A4.1 4.1 0 0 0 13.35 16.45c2.35 0 3.95-1.65 3.95-4 0-.35-.05-.65-.1-.95Z"
      fill="white"
      opacity="0.95"
    />
  </svg>
);
