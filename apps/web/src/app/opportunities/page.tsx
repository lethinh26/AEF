import Link from "next/link";
import {
  OpportunityTriageControls,
  RecomputeOpportunitiesButton,
} from "@/components/opportunity-controls";

export const dynamic = "force-dynamic";

type Evidence = {
  observation_id: string;
  source: string;
  event_type: string;
  title: string;
  summary: string;
  occurred_at: string | null;
  external_url: string | null;
  finding_title: string | null;
  finding_severity: string | null;
};

type Opportunity = {
  id: string;
  title: string;
  description: string;
  status: string;
  score: number | null;
  risk_class: string | null;
  created_at: string;
  updated_at: string;
  evidence_count: number;
  evidence: Evidence[];
};

async function loadOpportunities(): Promise<Opportunity[] | null> {
  const apiBaseUrl = process.env.AEO_API_INTERNAL_URL ?? "http://127.0.0.1:8100";
  try {
    const response = await fetch(new URL("/v1/opportunities?limit=50", apiBaseUrl), {
      cache: "no-store",
      signal: AbortSignal.timeout(4_000),
    });
    if (!response.ok) return null;
    const body = await response.json();
    return body.opportunities as Opportunity[];
  } catch {
    return null;
  }
}

function formatDate(value: string | null): string {
  if (!value) return "Time unavailable";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default async function OpportunitiesPage() {
  const opportunities = await loadOpportunities();

  return (
    <main className="data-page">
      <header className="data-page-header">
        <div>
          <Link className="back-link" href="/">← AEO workspace</Link>
          <span className="section-kicker">SHADOW BRAIN / DECISION SUPPORT</span>
          <h1>Opportunity inbox</h1>
          <p>Evidence-backed work candidates. A signal is not a root-cause diagnosis or permission to execute.</p>
        </div>
        <Link className="secondary-action" href="/evidence">Inspect evidence →</Link>
      </header>

      <section className="opportunity-toolbar">
        <div><strong>Deterministic discovery</strong><span>Repeated CI failures · 7-day window · minimum 3 failures · read-only investigation only</span></div>
        <RecomputeOpportunitiesButton />
      </section>

      {opportunities === null ? (
        <section className="data-empty-state"><h2>Opportunity service unavailable</h2><p>Start the local API and worker, then reload this page.</p></section>
      ) : opportunities.length === 0 ? (
        <section className="data-empty-state"><h2>No opportunities generated yet</h2><p>Recompute from the current evidence to run the deterministic CI signal rules.</p></section>
      ) : (
        <section className="opportunity-list">
          {opportunities.map((item) => (
            <article className="opportunity-card" key={item.id}>
              <div className="opportunity-card-top">
                <span className={`opportunity-status opportunity-status-${item.status}`}>{item.status}</span>
                <span className="opportunity-origin">RULE-BASED · NOT AI DIAGNOSIS</span>
              </div>
              <h2>{item.title}</h2>
              <div className="opportunity-metrics">
                <span><strong>{item.evidence_count}</strong> evidence records</span>
                <span><strong>{item.score?.toFixed(0) ?? "—"}</strong> heuristic score</span>
                <span><strong>{item.risk_class ?? "—"}</strong> proposed risk</span>
              </div>
              <p className="opportunity-description">{item.description}</p>
              <div className="opportunity-evidence">
                <div className="opportunity-evidence-heading">Supporting observations <span>{item.evidence_count}</span></div>
                {item.evidence.slice(0, 6).map((evidence) => (
                  <div className="opportunity-evidence-row" key={evidence.observation_id}>
                    <div><strong>{evidence.source}</strong><span>{evidence.title}</span></div>
                    <time>{formatDate(evidence.occurred_at)}</time>
                    {evidence.external_url ? <a href={evidence.external_url} target="_blank" rel="noreferrer">Open ↗</a> : null}
                  </div>
                ))}
                {item.evidence_count > item.evidence.length ? <small>Showing {item.evidence.length} of {item.evidence_count} linked observations.</small> : null}
              </div>
              <OpportunityTriageControls id={item.id} status={item.status} />
            </article>
          ))}
        </section>
      )}
    </main>
  );
}
