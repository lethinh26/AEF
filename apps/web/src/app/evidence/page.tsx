import Link from "next/link";

export const dynamic = "force-dynamic";

type Observation = {
  id: string;
  source: string;
  event_type: string;
  title: string;
  summary: string;
  external_url: string | null;
  occurred_at: string | null;
  observed_at: string;
  classification: string;
};

async function loadEvidence(): Promise<Observation[] | null> {
  const apiBaseUrl = process.env.AEO_API_INTERNAL_URL ?? "http://127.0.0.1:8100";
  try {
    const response = await fetch(new URL("/v1/observations?limit=100", apiBaseUrl), {
      cache: "no-store",
      signal: AbortSignal.timeout(4_000),
    });
    if (!response.ok) return null;
    const body = await response.json();
    return body.observations as Observation[];
  } catch {
    return null;
  }
}

function formatDate(value: string | null): string {
  if (!value) return "Time unavailable";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default async function EvidencePage() {
  const observations = await loadEvidence();

  return (
    <main className="data-page">
      <header className="data-page-header">
        <div>
          <Link className="back-link" href="/">← AEO workspace</Link>
          <span className="section-kicker">SHADOW BRAIN / PROVENANCE</span>
          <h1>Evidence stream</h1>
          <p>Raw observations are stored with source references, timestamps and content digests.</p>
        </div>
        <Link className="secondary-action" href="/sources">Manage sources →</Link>
      </header>

      {observations === null ? (
        <section className="data-empty-state"><h2>Evidence store unavailable</h2><p>Start the local API and database, then reload this page.</p></section>
      ) : observations.length === 0 ? (
        <section className="data-empty-state"><h2>No observations yet</h2><p>Connect the read-only GitHub credential and run the first repository sync.</p><Link className="primary-action inline-action" href="/sources">Open connected sources</Link></section>
      ) : (
        <section className="evidence-list">
          <div className="evidence-list-heading"><strong>{observations.length} latest observations</strong><span>Sorted by ingestion time</span></div>
          {observations.map((item) => (
            <article className="evidence-card" key={item.id}>
              <div className="evidence-card-top"><span className="evidence-source">{item.source}</span><time>{formatDate(item.occurred_at)}</time></div>
              <h2>{item.title}</h2>
              <p>{item.summary || item.event_type}</p>
              <div className="evidence-card-footer"><code>{item.event_type}</code><span>{item.classification}</span>{item.external_url ? <a href={item.external_url} rel="noreferrer" target="_blank">Open source ↗</a> : null}</div>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}
