import Link from "next/link";

type Overview = {
  sources_configured: number;
  sources_synced: number;
  sources_waiting_for_credential: number;
  observations: number;
  opportunities_pending: number;
};

type IconName = "arrow" | "grid" | "network" | "sparkles" | "shield";

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const shared = { "aria-hidden": true as const, fill: "none", height: size, stroke: "currentColor", strokeLinecap: "round" as const, strokeLinejoin: "round" as const, strokeWidth: 1.7, viewBox: "0 0 24 24", width: size };
  switch (name) {
    case "arrow": return <svg {...shared}><path d="M5 12h13M13 6l6 6-6 6" /></svg>;
    case "grid": return <svg {...shared}><rect x="3.5" y="3.5" width="6.5" height="6.5" rx="1.5" /><rect x="14" y="3.5" width="6.5" height="6.5" rx="1.5" /><rect x="3.5" y="14" width="6.5" height="6.5" rx="1.5" /><rect x="14" y="14" width="6.5" height="6.5" rx="1.5" /></svg>;
    case "network": return <svg {...shared}><circle cx="5" cy="7" r="2" /><circle cx="19" cy="6" r="2" /><circle cx="12" cy="18" r="2" /><path d="m7 8.2 3.4 7.4M17.2 7.7l-3.7 8M7.2 7.1l9.6-.6" /></svg>;
    case "sparkles": return <svg {...shared}><path d="m12 3 1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5L12 3Z" /><path d="m19 16 .7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7L19 16Z" /></svg>;
    case "shield": return <svg {...shared}><path d="M12 3 20 6v5.3c0 4.6-3.1 7.9-8 9.7-4.9-1.8-8-5.1-8-9.7V6l8-3Z" /><path d="m8.5 12 2.2 2.2 4.8-4.8" /></svg>;
  }
}

async function loadOverview(): Promise<Overview | null> {
  const apiBaseUrl = process.env.AEO_API_INTERNAL_URL ?? "http://127.0.0.1:8100";
  try {
    const response = await fetch(new URL("/v1/overview", apiBaseUrl), { cache: "no-store", signal: AbortSignal.timeout(3_000) });
    if (!response.ok) return null;
    return (await response.json()) as Overview;
  } catch {
    return null;
  }
}

export default async function HomePage() {
  const overview = await loadOverview();
  const sourceCount = overview?.sources_configured ?? 0;
  const syncedCount = overview?.sources_synced ?? 0;
  const observationCount = overview?.observations ?? 0;
  const opportunityCount = overview?.opportunities_pending ?? 0;

  return (
    <main className="overview-page">
      <section className="overview-hero">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-dot" /> AEO / LIVE CONTROL PLANE</div>
          <h1>Engineering clarity,<br /><em>at orbit.</em></h1>
          <p>See what is happening across your engineering world, find the signals worth attention and keep every decision grounded in evidence.</p>
          <div className="hero-actions"><Link className="button button-primary" href="/sources">Open sources <Icon name="arrow" size={15} /></Link><Link className="button button-ghost" href="/opportunities">View opportunities <Icon name="arrow" size={15} /></Link></div>
          <div className="hero-caption"><span className="caption-line" /> Read-only observation is active <span className="caption-muted">·</span> No write access granted</div>
        </div>
        <div className="hero-orbit" aria-hidden="true"><span className="hero-grid" /><span className="orbit-ring orbit-ring-one" /><span className="orbit-ring orbit-ring-two" /><span className="orbit-ring orbit-ring-three" /><span className="orbit-planet" /><span className="orbit-glow" /><i className="orbit-star orbit-star-one">✦</i><i className="orbit-star orbit-star-two">✧</i><i className="orbit-satellite" /></div>
        <div className="hero-status"><span className="status-pulse" /> SHADOW MODE <small>READ ONLY</small></div>
      </section>

      <section className="metric-grid" aria-label="Workspace metrics">
        <article className="metric-card metric-card-accent"><div className="metric-label"><span>CONNECTED SOURCES</span><Icon name="network" size={16} /></div><strong>{sourceCount}</strong><p>{syncedCount} synced <span>·</span> {overview?.sources_waiting_for_credential ?? 0} waiting for access</p></article>
        <article className="metric-card"><div className="metric-label"><span>OBSERVATIONS</span><Icon name="grid" size={16} /></div><strong>{observationCount}</strong><p>Evidence records in the world model</p></article>
        <article className="metric-card"><div className="metric-label"><span>OPEN OPPORTUNITIES</span><Icon name="sparkles" size={16} /></div><strong>{opportunityCount}</strong><p>Human-triage candidates waiting</p></article>
        <article className="metric-card metric-card-status"><div className="metric-label"><span>OPERATING MODE</span><Icon name="shield" size={16} /></div><strong>R0</strong><p><span className="green-dot" /> Investigation only · guarded</p></article>
      </section>

      <section className="dashboard-grid">
        <article className="panel signal-panel">
          <div className="panel-heading"><div><span className="section-kicker">WORLD MODEL / SIGNALS</span><h2>What AEO sees now</h2></div><Link className="panel-link" href="/evidence">Open evidence <Icon name="arrow" size={14} /></Link></div>
          <div className="signal-list">
            <div className="signal-row"><span className="signal-icon signal-icon-purple"><Icon name="network" size={16} /></span><div><strong>Clucky</strong><small>GitHub repository · public source</small></div><span className="signal-state"><i /> SYNCED</span></div>
            <div className="signal-row"><span className="signal-icon signal-icon-blue"><Icon name="grid" size={16} /></span><div><strong>{observationCount || "—"} observations indexed</strong><small>Commits, pull requests, issues and workflow runs</small></div><span className="signal-state"><i /> LIVE</span></div>
            <div className="signal-row"><span className="signal-icon signal-icon-amber"><Icon name="sparkles" size={16} /></span><div><strong>{opportunityCount || "No"} opportunity{opportunityCount === 1 ? "" : "ies"} pending</strong><small>Repeated CI failure signal · evidence attached</small></div><span className="signal-state signal-state-warm"><i /> REVIEW</span></div>
          </div>
        </article>

        <article className="panel model-panel"><div className="panel-heading"><div><span className="section-kicker">OPERATING PRINCIPLE</span><h2>Trust the trail.</h2></div><span className="panel-index">01 / 03</span></div><p>AEO does not jump from an alert to an action. It preserves the source event, groups related signals and makes uncertainty visible before a human decides what happens next.</p><div className="principle-trail"><span className="trail-node trail-node-done"><Icon name="network" size={14} /></span><i /><span className="trail-node trail-node-done"><Icon name="grid" size={14} /></span><i /><span className="trail-node"><Icon name="sparkles" size={14} /></span><i /><span className="trail-node"><Icon name="shield" size={14} /></span></div><div className="trail-labels"><span>Observe</span><span>Evidence</span><span>Decide</span><span>Verify</span></div></article>
      </section>

      <section className="lower-grid"><Link className="launch-card" href="/sources"><span className="launch-kicker">START HERE</span><strong>Explore your<br /><em>engineering world.</em></strong><span className="launch-link">View connected sources <Icon name="arrow" size={14} /></span><span className="launch-orbit launch-orbit-a" /><span className="launch-orbit launch-orbit-b" /><span className="launch-planet" /></Link><article className="quote-card"><span className="quote-mark">“</span><p>Autonomy is earned through visibility, evidence and trust.</p><span className="quote-rule" /><small>AEO / FOUNDATION PRINCIPLE</small></article></section>

      <footer className="page-footer"><span><b>AEO</b> · AUTONOMOUS ENGINEERING ORGANIZATION</span><span>LOCAL WORKSPACE <i>✦</i></span></footer>
    </main>
  );
}
