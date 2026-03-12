// Polymorphic List — AsyncState pattern with all 4 data states
//
// Demonstrates:
// - AsyncState<T> discriminated union: loading / error / empty / success
// - Skeleton shape-matching (aria-hidden + aria-busy)
// - Empty state with explanation + CTA
// - Error state with retry action + role="alert"
// - Polymorphic rendering: each item type gets a distinct layout
// - Pagination: partial state with "Load more" trigger

import * as React from "react";
import { cn } from "@/lib/utils";

// ─── Types ────────────────────────────────────────────────────────────────────

type AsyncState<T> =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "empty" }
  | { status: "success"; data: T[]; hasMore?: boolean };

// Two distinct item types with different visual treatments
type ProjectItem = {
  kind: "project";
  id: string;
  name: string;
  status: "active" | "paused" | "archived";
  updatedAt: string;
  memberCount: number;
};

type InviteItem = {
  kind: "invite";
  id: string;
  fromName: string;
  fromAvatar: string;
  projectName: string;
  sentAt: string;
};

type FeedItem = ProjectItem | InviteItem;

// ─── Skeleton components ──────────────────────────────────────────────────────

function ProjectRowSkeleton() {
  return (
    <div
      aria-hidden="true"  // Decorative — screen reader doesn't need this
      className="flex items-center gap-3 rounded-card border border-border bg-surface-1 px-4 py-3"
    >
      <div className="h-8 w-8 rounded-full bg-surface-3 animate-pulse flex-shrink-0" />
      <div className="flex-1 space-y-1.5">
        <div className="h-3.5 w-40 rounded bg-surface-3 animate-pulse" />
        <div className="h-3 w-24 rounded bg-surface-3 animate-pulse" />
      </div>
      <div className="h-5 w-14 rounded-full bg-surface-3 animate-pulse" />
    </div>
  );
}

function ListSkeleton({ count = 4 }: { count?: number }) {
  return (
    // aria-busy tells screen readers content is loading
    <div
      aria-busy="true"
      aria-label="Loading items"
      className="space-y-2"
    >
      {Array.from({ length: count }).map((_, i) => (
        <ProjectRowSkeleton key={i} />
      ))}
    </div>
  );
}

// ─── Individual item renderers ─────────────────────────────────────────────────
//
// Each type gets a distinct visual treatment based on what it IS.

function ProjectRow({ item }: { item: ProjectItem }) {
  const statusColors = {
    active:   "bg-green-9/10 text-green-11",
    paused:   "bg-gray-4 text-gray-9",
    archived: "bg-gray-3 text-gray-8",
  };

  return (
    <a
      href={`/projects/${item.id}`}
      className={cn(
        "flex items-center gap-3 rounded-card border border-border bg-surface-1 px-4 py-3",
        "hover:bg-surface-2 transition-colors group"
      )}
    >
      {/* Status dot */}
      <div className="h-8 w-8 rounded-full bg-brand-subtle flex items-center justify-center flex-shrink-0">
        <span className="text-xs font-semibold text-brand-text">
          {item.name[0].toUpperCase()}
        </span>
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-content-1 truncate group-hover:text-brand transition-colors">
          {item.name}
        </p>
        <p className="text-xs text-content-3 mt-0.5">
          {item.memberCount} member{item.memberCount !== 1 ? "s" : ""} · Updated {item.updatedAt}
        </p>
      </div>

      <span className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium capitalize",
        statusColors[item.status]
      )}>
        {item.status}
      </span>
    </a>
  );
}

function InviteCard({ item, onAccept, onDecline }: {
  item: InviteItem;
  onAccept: (id: string) => void;
  onDecline: (id: string) => void;
}) {
  return (
    // Invitation gets a visually distinct treatment: highlighted border
    <div className="flex items-center gap-3 rounded-card border border-brand/30 bg-brand-subtle px-4 py-3">
      <img
        src={item.fromAvatar}
        alt=""
        className="h-8 w-8 rounded-full flex-shrink-0 object-cover"
      />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-content-1">
          <span className="font-medium">{item.fromName}</span>
          {" invited you to "}
          <span className="font-medium">{item.projectName}</span>
        </p>
        <p className="text-xs text-content-3 mt-0.5">{item.sentAt}</p>
      </div>
      <div className="flex gap-1.5 flex-shrink-0">
        <button
          onClick={() => onDecline(item.id)}
          className="rounded-button border border-border bg-surface-1 px-2.5 py-1 text-xs text-content-2 hover:bg-surface-2 transition-colors"
        >
          Decline
        </button>
        <button
          onClick={() => onAccept(item.id)}
          className="rounded-button bg-brand text-white px-2.5 py-1 text-xs hover:bg-brand-hover transition-colors"
        >
          Accept
        </button>
      </div>
    </div>
  );
}

// ─── Main list component ───────────────────────────────────────────────────────

interface FeedListProps {
  state: AsyncState<FeedItem>;
  onRetry: () => void;
  onLoadMore?: () => void;
  onAcceptInvite: (id: string) => void;
  onDeclineInvite: (id: string) => void;
}

export function FeedList({
  state,
  onRetry,
  onLoadMore,
  onAcceptInvite,
  onDeclineInvite,
}: FeedListProps) {
  // ── Loading ──
  if (state.status === "loading") {
    return <ListSkeleton count={4} />;
  }

  // ── Error ──
  if (state.status === "error") {
    return (
      <div
        role="alert"
        className="rounded-card border border-destructive/30 bg-destructive/5 px-6 py-8 text-center"
      >
        <p className="text-sm font-medium text-destructive">{state.message}</p>
        <p className="mt-1 text-xs text-content-3">
          Your changes are saved. This might be a temporary issue.
        </p>
        <button
          onClick={onRetry}
          className="mt-3 text-sm text-brand hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand rounded"
        >
          Try again
        </button>
      </div>
    );
  }

  // ── Empty ──
  if (state.status === "empty") {
    return (
      <div className="rounded-card border border-border border-dashed px-6 py-12 text-center">
        <p className="text-sm font-medium text-content-1">No projects yet</p>
        <p className="mt-1 text-sm text-content-3">
          Projects you create or join will appear here.
        </p>
        <a
          href="/projects/new"
          className="mt-4 inline-flex items-center rounded-button bg-brand text-white px-4 py-2 text-sm font-medium hover:bg-brand-hover transition-colors"
        >
          Create your first project
        </a>
      </div>
    );
  }

  // ── Success (populated) ──
  return (
    // aria-busy=false: content is loaded
    <section aria-busy={false} aria-label="Projects and invitations">
      <div className="space-y-2">
        {state.data.map(item => {
          if (item.kind === "project") {
            return <ProjectRow key={item.id} item={item} />;
          }
          if (item.kind === "invite") {
            return (
              <InviteCard
                key={item.id}
                item={item}
                onAccept={onAcceptInvite}
                onDecline={onDeclineInvite}
              />
            );
          }
          // TypeScript exhaustive check — will error if a new kind is added
          // without a renderer
          const _exhaustive: never = item;
          return null;
        })}
      </div>

      {state.hasMore && (
        <div className="mt-4 text-center">
          <button
            onClick={onLoadMore}
            className="text-sm text-brand hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand rounded"
          >
            Load more
          </button>
        </div>
      )}
    </section>
  );
}

// ─── Interactive demo ─────────────────────────────────────────────────────────

const MOCK_ITEMS: FeedItem[] = [
  {
    kind: "invite",
    id: "inv-1",
    fromName: "Priya Patel",
    fromAvatar: "https://i.pravatar.cc/64?u=priya",
    projectName: "Design System v2",
    sentAt: "2 hours ago",
  },
  {
    kind: "project",
    id: "proj-1",
    name: "Marketing Site",
    status: "active",
    updatedAt: "today",
    memberCount: 5,
  },
  {
    kind: "project",
    id: "proj-2",
    name: "Mobile App",
    status: "paused",
    updatedAt: "3 days ago",
    memberCount: 8,
  },
  {
    kind: "project",
    id: "proj-3",
    name: "Legacy CMS",
    status: "archived",
    updatedAt: "2 months ago",
    memberCount: 2,
  },
];

type DemoState = "loading" | "error" | "empty" | "success";

export function FeedListDemo() {
  const [scenario, setScenario] = React.useState<DemoState>("success");

  const state: AsyncState<FeedItem> =
    scenario === "loading" ? { status: "loading" } :
    scenario === "error"   ? { status: "error", message: "Failed to load projects. Check your connection." } :
    scenario === "empty"   ? { status: "empty" } :
    { status: "success", data: MOCK_ITEMS, hasMore: true };

  return (
    <div className="max-w-xl mx-auto p-6 space-y-4">
      {/* Scenario switcher */}
      <div className="flex gap-2 flex-wrap">
        {(["loading", "error", "empty", "success"] as const).map(s => (
          <button
            key={s}
            onClick={() => setScenario(s)}
            className={cn(
              "rounded-full px-3 py-1 text-xs font-medium transition-colors",
              scenario === s
                ? "bg-brand text-white"
                : "border border-border text-content-2 hover:bg-surface-2"
            )}
          >
            {s}
          </button>
        ))}
      </div>

      <FeedList
        state={state}
        onRetry={() => setScenario("success")}
        onAcceptInvite={id => console.log("Accepted invite", id)}
        onDeclineInvite={id => console.log("Declined invite", id)}
      />
    </div>
  );
}
