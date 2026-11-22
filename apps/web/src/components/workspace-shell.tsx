"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { ApiStatus } from "./api-status";

type IconName = "grid" | "target" | "network" | "sparkles" | "rocket" | "shield" | "activity" | "settings";

function Icon({ name, size = 17 }: { name: IconName; size?: number }) {
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
      return <svg {...shared}><rect x="3.5" y="3.5" width="6.5" height="6.5" rx="1.5" /><rect x="14" y="3.5" width="6.5" height="6.5" rx="1.5" /><rect x="3.5" y="14" width="6.5" height="6.5" rx="1.5" /><rect x="14" y="14" width="6.5" height="6.5" rx="1.5" /></svg>;
    case "target":
      return <svg {...shared}><circle cx="12" cy="12" r="8.5" /><circle cx="12" cy="12" r="4.5" /><circle cx="12" cy="12" r="1" /></svg>;
    case "network":
      return <svg {...shared}><circle cx="5" cy="7" r="2" /><circle cx="19" cy="6" r="2" /><circle cx="12" cy="18" r="2" /><path d="m7 8.2 3.4 7.4M17.2 7.7l-3.7 8M7.2 7.1l9.6-.6" /></svg>;
    case "sparkles":
      return <svg {...shared}><path d="m12 3 1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5L12 3Z" /><path d="m19 16 .7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7L19 16Z" /></svg>;
    case "rocket":
      return <svg {...shared}><path d="M14.5 4.5c2.2-1.4 4.3-1.7 5-1 .7.7.4 2.8-1 5l-5.2 7.8-5.6-5.6 6.8-6.2Z" /><path d="m7.7 10.3-3.2.8-2 3.2 5.1.1M13.7 16.3l-.8 3.2-3.2 2-.1-5.1" /><circle cx="15.7" cy="8.3" r="1.4" /></svg>;
    case "shield":
      return <svg {...shared}><path d="M12 3 20 6v5.3c0 4.6-3.1 7.9-8 9.7-4.9-1.8-8-5.1-8-9.7V6l8-3Z" /><path d="m8.5 12 2.2 2.2 4.8-4.8" /></svg>;
    case "activity":
      return <svg {...shared}><path d="M3 12h4l2.1-6 4.1 12 2.2-6H21" /></svg>;
    case "settings":
      return <svg {...shared}><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6 7 7M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4" /><circle cx="12" cy="12" r="3.5" /></svg>;
  }
}

const groups = [
  {
    label: "CONTROL ROOM",
    items: [{ label: "Overview", href: "/", icon: "grid" as const }],
  },
  {
    label: "INTELLIGENCE",
    items: [
      { label: "Goals", href: "#", icon: "target" as const, soon: true },
      { label: "Sources", href: "/sources", icon: "network" as const },
      { label: "Opportunities", href: "/opportunities", icon: "sparkles" as const },
    ],
  },
  {
    label: "EXECUTION",
    items: [
      { label: "Missions", href: "#", icon: "rocket" as const, soon: true },
      { label: "Evidence", href: "/evidence", icon: "shield" as const },
    ],
  },
];

function currentLabel(pathname: string): string {
  if (pathname === "/") return "Overview";
  if (pathname.startsWith("/sources")) return "Sources";
  if (pathname.startsWith("/evidence")) return "Evidence";
  if (pathname.startsWith("/opportunities")) return "Opportunities";
  return "Control room";
}

export function WorkspaceShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const label = currentLabel(pathname);

  return (
    <div className="app-frame">
      <aside className="sidebar">
        <Link className="brand" href="/" aria-label="AEO home">
          <span className="brand-mark" aria-hidden="true"><span>A</span><i /></span>
          <span className="brand-copy"><strong>AEO</strong><small>ENGINEERING OS</small></span>
        </Link>

        <div className="workspace-switcher">
          <span className="workspace-avatar">A</span>
          <span className="workspace-copy"><strong>My workspace</strong><small>Local / shadow mode</small></span>
          <span className="workspace-chevron">⌄</span>
        </div>

        <nav aria-label="Main navigation" className="navigation">
          {groups.map((group) => (
            <div className="nav-group" key={group.label}>
              <div className="nav-group-label">{group.label}</div>
              <div className="nav-items">
                {group.items.map((item) => {
                  const isSoon = "soon" in item && item.soon === true;
                  const active = !isSoon && (item.href === "/" ? pathname === "/" : pathname.startsWith(item.href));
                  if (isSoon) {
                    return <div aria-disabled="true" className="nav-item nav-item-disabled" key={item.label}><span className="nav-icon"><Icon name={item.icon} /></span><span>{item.label}</span><span className="nav-soon">SOON</span></div>;
                  }
                  return <Link className={`nav-item${active ? " nav-item-active" : ""}`} href={item.href} key={item.label}><span className="nav-icon"><Icon name={item.icon} /></span><span>{item.label}</span>{active ? <span className="active-indicator" /> : null}</Link>;
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="sidebar-spacer" />
        <div className="sidebar-status-card">
          <div className="sidebar-status-top"><span className="status-pulse" /> SYSTEM ONLINE <span className="sidebar-status-icon"><Icon name="activity" size={14} /></span></div>
          <strong>Shadow mode is active</strong>
          <span>Read-only observation across your engineering world.</span>
        </div>
        <div className="sidebar-footer"><span><i /> LOCAL ENVIRONMENT</span><b>v0.1</b></div>
      </aside>

      <div className="shell-main">
        <header className="topbar">
          <div className="breadcrumb"><span>AEO / CONTROL ROOM</span><b>/</b> {label}</div>
          <div className="topbar-actions"><div className="topbar-live"><i /> LIVE</div><div className="topbar-divider" /><ApiStatus /><button aria-label="Settings" className="icon-button" type="button"><Icon name="settings" size={16} /></button></div>
        </header>
        <div className="shell-content">{children}</div>
      </div>
    </div>
  );
}
