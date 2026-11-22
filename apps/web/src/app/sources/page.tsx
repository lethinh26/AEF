import Link from "next/link";
import { SourceSyncButton } from "@/components/source-sync-button";

export const dynamic = "force-dynamic";

type Source = {
  id: string;
  repository: string;
  display_name: string;
  url: string;
  access_mode: string;
  status: string;
  sync_status: string;
  sync_interval_seconds: number;
  last_sync_completed_at: string | null;
  next_sync_at: string | null;
  last_error_code: string | null;
  credential_required: boolean;
};

type SourcesResponse = {
  repositories: Source[];
  github_credential_configured: boolean;
  github_public_repositories: string[];
  sync_available: boolean;
  sync_interval_seconds: number;
  mode: string;
};

async function loadSources(): Promise<SourcesResponse | null> {
  const apiBaseUrl = process.env.AEO_API_INTERNAL_URL ?? "http://127.0.0.1:8100";
  try {
    const response = await fetch(new URL("/v1/sources", apiBaseUrl), {
      cache: "no-store",
      signal: AbortSignal.timeout(4_000),
    });
    if (!response.ok) return null;
    return (await response.json()) as SourcesResponse;
  } catch {
    return null;
  }
}

function formatDate(value: string | null): string {
  if (!value) return "Never";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default async function SourcesPage() {
  const data = await loadSources();

  return (
    <main className="data-page">
      <header className="data-page-header">
        <div>
          <Link className="back-link" href="/">← AEO workspace</Link>
          <span className="section-kicker">SHADOW BRAIN / INGESTION</span>
          <h1>Connected sources</h1>
          <p>Observe repositories and CI activity without granting AEO write access.</p>
        </div>
        <Link className="secondary-action" href="/evidence">View evidence →</Link>
      </header>

      {!data ? (
        <section className="data-empty-state">
          <h2>Control plane unavailable</h2>
          <p>Start the local API and database, then reload this page.</p>
        </section>
      ) : (
        <>
          <section className="source-overview-row">
            <div className="source-overview-card">
              <span className="data-label">REPOSITORIES</span>
              <strong>{data.repositories.length}</strong>
              <small>Configured for observation</small>
            </div>
            <div className="source-overview-card">
              <span className="data-label">ACCESS MODE</span>
              <strong>Read-only</strong>
              <small>No branch, commit or PR write permissions</small>
            </div>
            <div className="source-overview-card">
              <span className="data-label">POLL INTERVAL</span>
              <strong>{Math.round(data.sync_interval_seconds / 60)} min</strong>
              <small>Background sync when credentials are configured</small>
            </div>
          </section>

          {!data.github_credential_configured ? (
            <section className="credential-notice">
              <div><strong>Private repository access is waiting for a credential</strong><p>Clucky is public and can sync anonymously. New-API is private and will remain waiting until you configure a fine-grained token restricted to the selected repositories with Metadata, Contents, Issues, Pull requests and Actions set to Read-only. Store it as <code>AEO_GITHUB_TOKEN</code> in your local <code>.env</code>, then restart the API and worker.</p></div>
              <span className="notice-state">WAITING</span>
            </section>
          ) : null}

          <section className="data-section-heading">
            <div><span className="section-kicker">YOUR ENGINEERING WORLD</span><h2>Repository connections</h2></div>
            <SourceSyncButton disabled={!data.sync_available} />
          </section>

          <section className="source-list">
            {data.repositories.map((source) => (
              <article className="source-card" key={source.id}>
                <div className="source-card-main">
                  <div className="source-github-mark" aria-hidden="true">GH</div>
                  <div className="source-title-block">
                    <a href={source.url} rel="noreferrer" target="_blank">{source.display_name} ↗</a>
                    <span>{source.repository} · GitHub · {source.access_mode.replace("_", " ")}</span>
                  </div>
                </div>
                <div className="source-card-meta">
                  <span className={`sync-state sync-state-${source.sync_status}`}>{source.sync_status}</span>
                  {source.credential_required ? <small className="error-copy">Read-only token required</small> : null}
                  <small>Last sync: {formatDate(source.last_sync_completed_at)}</small>
                  {source.last_error_code ? <small className="error-copy">{source.last_error_code}</small> : null}
                </div>
              </article>
            ))}
          </section>
        </>
      )}
    </main>
  );
}
