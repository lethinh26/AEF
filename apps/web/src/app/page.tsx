import Link from "next/link";
import { ApiStatus } from "@/components/api-status";

type IconName = "grid" | "target" | "network" | "sparkles" | "rocket" | "shield" | "layers" | "arrow";

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const shared = {
    "aria-hidden": true as const,
    fill: "none",
    height: size,
    stroke: "currentColor",
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    strokeWidth: 1.7,
    viewBox: "0 0 24 24",
    width: size,
  };

  switch (name) {
    case "grid":
      return <svg {...shared}><rect x="3.5" y="3.5" width="7" height="7" rx="2" /><rect x="13.5" y="3.5" width="7" height="7" rx="2" /><rect x="3.5" y="13.5" width="7" height="7" rx="2" /><rect x="13.5" y="13.5" width="7" height="7" rx="2" /></svg>;
    case "target":
      return <svg {...shared}><circle cx="12" cy="12" r="8.5" /><circle cx="12" cy="12" r="4.5" /><circle cx="12" cy="12" r="1" /></svg>;
    case "network":
      return <svg {...shared}><circle cx="5" cy="7" r="2.2" /><circle cx="19" cy="6" r="2.2" /><circle cx="12" cy="18" r="2.2" /><path d="m7 8.2 3.6 7.5M17.1 7.8l-3.8 8M7.3 7.2l9.4-.8" /></svg>;
    case "sparkles":
      return <svg {...shared}><path d="m12 3 1.6 5.4L19 10l-5.4 1.6L12 17l-1.6-5.4L5 10l5.4-1.6L12 3Z" /><path d="m19 15 .8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15ZM5 2l.7 2.3L8 5l-2.3.7L5 8l-.7-2.3L2 5l2.3-.7L5 2Z" /></svg>;
    case "rocket":
      return <svg {...shared}><path d="M14.5 4.5c2.2-1.4 4.3-1.7 5-1 .7.7.4 2.8-1 5l-5.2 7.8-5.6-5.6 6.8-6.2Z" /><path d="m7.7 10.3-3.2.8-2 3.2 5.1.1M13.7 16.3l-.8 3.2-3.2 2-.1-5.1M8.1 15.9c-1.8.2-3.2 1.5-3.5 3.5 2-.3 3.3-1.7 3.5-3.5Z" /><circle cx="15.7" cy="8.3" r="1.4" /></svg>;
    case "shield":
      return <svg {...shared}><path d="M12 3 20 6v5.3c0 4.6-3.1 7.9-8 9.7-4.9-1.8-8-5.1-8-9.7V6l8-3Z" /><path d="m8.5 12 2.2 2.2 4.8-4.8" /></svg>;
    case "layers":
      return <svg {...shared}><path d="m12 3 9 4.7-9 4.8-9-4.8L12 3Z" /><path d="m3 12 9 4.8 9-4.8M3 16.3l9 4.7 9-4.7" /></svg>;
    case "arrow":
      return <svg {...shared}><path d="M7 17 17 7M7 7h10v10" /></svg>;
  }
}

const navigation = [
  {
    label: "WORKSPACE",
    items: [{ label: "Overview", icon: "grid" as const, active: true }],
  },
  {
    label: "INTELLIGENCE",
    items: [
      { label: "Goals", icon: "target" as const },
      { label: "Sources", icon: "network" as const },
      { label: "Opportunities", icon: "sparkles" as const },
    ],
  },
  {
    label: "EXECUTION",
    items: [
      { label: "Missions", icon: "rocket" as const },
      { label: "Evidence", icon: "shield" as const },
    ],
  },
];

const principles = [
  {
    number: "01",
    icon: "network" as const,
    title: "Observe before acting",
    description: "Read-only integrations build a trustworthy picture of your engineering world first.",
    tone: "lilac",
  },
  {
    number: "02",
    icon: "layers" as const,
    title: "Evidence over assumptions",
    description: "Every finding should lead back to something concrete, traceable and verifiable.",
    tone: "peach",
  },
  {
    number: "03",
    icon: "shield" as const,
    title: "Guardrails at every step",
    description: "Policy and independent verification stay in the loop before systems are changed.",
    tone: "mint",
  },
];

export default function HomePage() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link className="brand" href="/" aria-label="AEO home">
          <span className="brand-symbol" aria-hidden="true">
            <span className="brand-symbol-core">A</span>
            <span className="brand-symbol-orbit" />
          </span>
          <span className="brand-copy">
            <strong>AEO</strong>
            <small>ENGINEERING OS</small>
          </span>
        </Link>

        <div className="workspace-switcher">
          <span className="workspace-avatar">A</span>
          <span className="workspace-copy"><strong>My workspace</strong><small>Local workspace</small></span>
          <span className="switcher-chevron">⌄</span>
        </div>

        <nav aria-label="Main navigation" className="navigation">
          {navigation.map((group) => (
            <div className="nav-group" key={group.label}>
              <div className="nav-group-label">{group.label}</div>
              <div className="nav-items">
                {group.items.map((item) => (
                  "active" in item && item.active ? (
                    <Link aria-current="page" className="nav-item nav-item-active" href="/" key={item.label}>
                      <span className="nav-icon"><Icon name={item.icon} /></span>
                      <span>{item.label}</span>
                      <span className="active-indicator" />
                    </Link>
                  ) : (
                    <div aria-disabled="true" className="nav-item nav-item-disabled" key={item.label}>
                      <span className="nav-icon"><Icon name={item.icon} /></span>
                      <span>{item.label}</span>
                      <span className="nav-soon">SOON</span>
                    </div>
                  )
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div className="sidebar-spacer" />

        <div className="sidebar-note">
          <div className="sidebar-note-art" aria-hidden="true">
            <span className="note-orbit note-orbit-one" />
            <span className="note-orbit note-orbit-two" />
            <span className="note-planet" />
          </div>
          <span className="sidebar-note-label">A NEW WAY TO BUILD</span>
          <strong>Engineering, in a new orbit.</strong>
          <span className="sidebar-note-caption">Your control plane is taking shape.</span>
        </div>

        <div className="sidebar-footer">
          <div className="environment-indicator"><span /> LOCAL ENVIRONMENT</div>
          <span className="version-label">v0.1.0</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>WORKSPACE</span><b>/</b> Overview</div>
          <div className="topbar-actions">
            <div className="topbar-environment"><span /> Local environment</div>
            <div className="topbar-divider" />
            <div className="topbar-mode"><Icon name="shield" size={13} /> SHADOW MODE</div>
          </div>
        </header>

        <div className="page-content">
          <section className="hero-card">
            <div className="hero-copy">
              <div className="hero-eyebrow"><span className="eyebrow-sparkle"><Icon name="sparkles" size={13} /></span> YOUR ENGINEERING CONTROL PLANE</div>
              <h1>Make room for<br /><span>what&apos;s next.</span></h1>
              <p>One calm place to understand your systems, discover opportunities and move engineering forward.</p>
              <div className="hero-meta">
                <span className="hero-phase"><i /> FOUNDATION PHASE</span>
                <span className="hero-meta-divider" />
                <span className="hero-meta-copy">AEO is getting ready for lift-off</span>
              </div>
            </div>

            <div className="hero-visual" aria-hidden="true">
              <div className="visual-stars stars-one" />
              <div className="visual-stars stars-two" />
              <div className="orbit-scene">
                <span className="orbit orbit-wide" />
                <span className="orbit orbit-tall" />
                <span className="orbit orbit-tilted" />
                <span className="planet-halo" />
                <span className="planet-shadow" />
                <span className="planet-core" />
                <span className="planet-highlight" />
                <span className="planet-ring" />
                <span className="satellite satellite-one"><i /></span>
                <span className="satellite satellite-two"><i /></span>
                <span className="visual-cross cross-one">✳</span>
                <span className="visual-cross cross-two">✦</span>
              </div>
              <div className="floating-card floating-source">
                <span className="floating-icon floating-icon-purple"><Icon name="network" size={16} /></span>
                <span><strong>Sources</strong><small>Connect your world</small></span>
                <Icon name="arrow" size={14} />
              </div>
              <div className="floating-card floating-mode">
                <span className="floating-live-dot" />
                <span><strong>Shadow mode</strong><small>Read-only by design</small></span>
              </div>
            </div>
          </section>

          <section className="overview-stats" aria-label="Workspace status">
            <article className="stat-card stat-phase">
              <div className="stat-topline"><span className="stat-label">CURRENT PHASE</span><span className="stat-icon stat-icon-lilac"><Icon name="layers" size={17} /></span></div>
              <div className="stat-main"><strong>01</strong><span>/ 07</span></div>
              <div className="stat-bottom"><span>Platform foundation</span><span className="stat-progress">14%</span></div>
              <div className="mini-progress"><i /></div>
            </article>

            <article className="stat-card stat-sources">
              <div className="stat-topline"><span className="stat-label">CONNECTED SOURCES</span><span className="stat-icon stat-icon-peach"><Icon name="network" size={17} /></span></div>
              <div className="stat-main"><strong>0</strong><span>connected</span></div>
              <div className="stat-bottom"><span>Repositories &amp; CI pipelines</span></div>
              <div className="stat-footnote"><span className="empty-source-dot" /> Waiting for your first connection</div>
            </article>

            <article className="stat-card stat-api">
              <div className="stat-topline"><span className="stat-label">CONTROL PLANE API</span><span className="stat-icon stat-icon-mint"><Icon name="shield" size={17} /></span></div>
              <div className="api-stat-content"><ApiStatus /></div>
              <div className="stat-bottom"><span>Health checks run automatically</span></div>
              <div className="stat-footnote"><span className="api-footnote-dot" /> Backend connection monitor</div>
            </article>
          </section>

          <section className="mission-section" aria-labelledby="mission-title">
            <div className="section-heading">
              <div><span className="section-kicker">THE JOURNEY</span><h2 id="mission-title">Your first mission</h2></div>
              <span className="section-counter">01 <i>/</i> 07 PHASES</span>
            </div>

            <div className="mission-grid">
              <article className="mission-card">
                <div className="mission-card-top"><span className="mission-badge"><i /> NOW BUILDING</span><span className="mission-card-index">01 — FOUNDATION</span></div>
                <h3>Lay the groundwork.</h3>
                <p>The essentials are in place. Shared contracts, persistent state and background processing give AEO a solid launchpad.</p>
                <div className="journey-track">
                  <div className="journey-step journey-step-active"><span className="journey-node"><Icon name="layers" size={14} /></span><div><strong>Platform foundation</strong><small>Core infrastructure is ready</small></div><span className="journey-state">CURRENT</span></div>
                  <div className="journey-connector" />
                  <div className="journey-step"><span className="journey-node"><Icon name="network" size={14} /></span><div><strong>Shadow Brain</strong><small>Connect repositories and CI signals</small></div><span className="journey-state">NEXT UP</span></div>
                  <div className="journey-connector" />
                  <div className="journey-step journey-step-muted"><span className="journey-node"><Icon name="sparkles" size={14} /></span><div><strong>Opportunity Engine</strong><small>Turn evidence into useful priorities</small></div><span className="journey-state">UPCOMING</span></div>
                </div>
              </article>

              <aside className="next-card">
                <div className="next-card-art" aria-hidden="true"><span className="next-orbit next-orbit-a" /><span className="next-orbit next-orbit-b" /><span className="next-planet" /><span className="next-star next-star-a">✦</span><span className="next-star next-star-b">✳</span></div>
                <span className="next-card-kicker">ON THE HORIZON</span>
                <h3>Next stop:<br /><span>Shadow Brain.</span></h3>
                <p>Give AEO a window into your repositories. The first step toward an engineering organization that can see the bigger picture.</p>
                <div className="next-card-footer"><span>PHASE 02</span><span className="next-card-line" /><span>READ-ONLY</span></div>
              </aside>
            </div>
          </section>

          <section className="principles-section" aria-labelledby="principles-title">
            <div className="section-heading principles-heading">
              <div><span className="section-kicker">BUILT DIFFERENTLY</span><h2 id="principles-title">A thoughtful way to engineer.</h2></div>
              <p>Autonomy is earned through visibility, evidence and trust.</p>
            </div>
            <div className="principle-grid">
              {principles.map((principle) => (
                <article className="principle-card" key={principle.number}>
                  <div className={`principle-icon principle-icon-${principle.tone}`}><Icon name={principle.icon} size={19} /></div>
                  <span className="principle-number">{principle.number}</span>
                  <h3>{principle.title}</h3>
                  <p>{principle.description}</p>
                </article>
              ))}
            </div>
          </section>

          <footer className="page-footer"><span><b>AEO</b> · AUTONOMOUS ENGINEERING ORGANIZATION</span><span>MADE FOR THE NEXT ERA OF ENGINEERING <i>✳</i></span></footer>
        </div>
      </main>
    </div>
  );
}
