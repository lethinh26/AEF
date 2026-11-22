"use client";

import { useEffect, useState } from "react";

type ConnectionState = "checking" | "connected" | "unavailable";

const apiBaseUrl = process.env.NEXT_PUBLIC_AEO_API_URL ?? "http://127.0.0.1:8100";

export function ApiStatus() {
  const [state, setState] = useState<ConnectionState>("checking");

  useEffect(() => {
    let active = true;
    const controller = new AbortController();

    async function checkApi() {
      try {
        const response = await fetch(`${apiBaseUrl}/health/live`, {
          cache: "no-store",
          signal: controller.signal,
        });
        if (active) setState(response.ok ? "connected" : "unavailable");
      } catch {
        if (active) setState("unavailable");
      }
    }

    void checkApi();
    const interval = window.setInterval(checkApi, 15_000);
    return () => {
      active = false;
      controller.abort();
      window.clearInterval(interval);
    };
  }, []);

  const label = {
    checking: "CHECKING API",
    connected: "API CONNECTED",
    unavailable: "API UNAVAILABLE",
  }[state];

  return <span className={`api-status api-status-${state}`}><i />{label}</span>;
}
