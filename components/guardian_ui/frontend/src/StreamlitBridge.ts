import { Streamlit } from "streamlit-component-lib";
import { useEffect, useState } from "react";
import type { GuardianArgs, GuardianEvent } from "./types";

export function useStreamlitArgs(): GuardianArgs | null {
  const [args, setArgs] = useState<GuardianArgs | null>(null);

  useEffect(() => {
    const onRender = (event: Event) => {
      const detail = (event as CustomEvent).detail;
      if (detail?.args) setArgs(detail.args as GuardianArgs);
    };
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
    Streamlit.setComponentReady();
    return () => {
      Streamlit.events.removeEventListener(Streamlit.RENDER_EVENT, onRender);
    };
  }, []);

  return args;
}

export function sendEvent(event: GuardianEvent): void {
  Streamlit.setComponentValue({ ...event, _ts: Date.now() });
}

export function setFrameHeight(px: number): void {
  Streamlit.setFrameHeight(px);
}
