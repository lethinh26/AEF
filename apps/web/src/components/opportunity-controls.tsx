"use client";

import { useState } from "react";

export function RecomputeOpportunitiesButton() {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [idempotencyKey] = useState(() => crypto.randomUUID());

  async function recompute() {
    setBusy(true);
    setMessage("");
    try {
      const response = await fetch("/api/opportunities/recompute", {
        method: "POST",
        headers: { "Idempotency-Key": idempotencyKey },
      });
      const body = await response.json();
      if (!response.ok) throw new Error("Could not queue analysis.");
      setMessage(
        `${body.queued ?? 0} new job(s) queued; ${body.skipped_active ?? 0} already active; ${body.skipped_no_observations ?? 0} source(s) waiting for observations.`,
      );
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Analysis could not be queued.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="opportunity-recompute-control">
      <button className="primary-action" disabled={busy} onClick={recompute}>
        {busy ? "Queueing analysis…" : "Recompute from evidence"}
      </button>
      {message ? <span aria-live="polite" className="action-message">{message}</span> : null}
    </div>
  );
}

export function OpportunityTriageControls({
  id,
  status,
}: {
  id: string;
  status: string;
}) {
  const [reason, setReason] = useState("Reviewed in the Control Center");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState("");
  const [idempotencyKey] = useState(() => crypto.randomUUID());

  async function triage(action: "accept" | "defer" | "reject") {
    setBusy(true);
    setResult("");
    try {
      const response = await fetch(`/api/opportunities/${id}/triage`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Idempotency-Key": idempotencyKey },
        body: JSON.stringify({ action, reason }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Triage failed.");
      setResult(`Marked ${body.status}. Refresh to update the inbox.`);
    } catch (error) {
      setResult(error instanceof Error ? error.message : "Triage failed.");
    } finally {
      setBusy(false);
    }
  }

  if (status !== "proposed") {
    return <span className="triage-complete">This opportunity is {status}.</span>;
  }

  return (
    <div className="opportunity-triage">
      <label htmlFor={`reason-${id}`}>Review note</label>
      <input id={`reason-${id}`} value={reason} onChange={(event) => setReason(event.target.value)} maxLength={1000} />
      <div className="triage-actions">
        <button disabled={busy || !reason.trim()} onClick={() => triage("accept")}>Accept</button>
        <button disabled={busy || !reason.trim()} onClick={() => triage("defer")}>Defer</button>
        <button disabled={busy || !reason.trim()} onClick={() => triage("reject")}>Reject</button>
      </div>
      {result ? <p aria-live="polite" className="action-message">{result}</p> : null}
    </div>
  );
}
