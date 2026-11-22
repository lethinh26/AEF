"use client";

import { useState } from "react";

type SyncState = "idle" | "loading" | "queued" | "error";

export function SourceSyncButton({ disabled = false }: { disabled?: boolean }) {
  const [state, setState] = useState<SyncState>("idle");
  const [message, setMessage] = useState("");

  async function syncSources() {
    setState("loading");
    setMessage("");
    try {
      const response = await fetch("/api/sources/sync", { method: "POST" });
      const body = await response.json();
      if (!response.ok) {
        const detail = body.detail;
        setMessage(typeof detail?.message === "string" ? detail.message : "Could not queue a sync.");
        setState("error");
        return;
      }
      const waiting = Array.isArray(body.requires_credential) ? body.requires_credential.length : 0;
      const suffix = waiting ? ` ${waiting} private source(s) still need a read-only token.` : "";
      setMessage(`${body.queued ?? 0} repository sync job(s) queued.${suffix} Refresh in a moment to see new evidence.`);
      setState("queued");
    } catch {
      setMessage("AEO API is unavailable. Check that the local stack is running.");
      setState("error");
    }
  }

  return (
    <div className="source-sync-control">
      <button className="primary-action" disabled={disabled || state === "loading"} onClick={syncSources}>
        {state === "loading" ? "Queueing sync…" : "Sync repositories"}
      </button>
      {disabled ? <p className="helper-text">Configure the read-only GitHub credential in the local environment first.</p> : null}
      {message ? <p aria-live="polite" className={`action-message action-message-${state}`}>{message}</p> : null}
    </div>
  );
}
