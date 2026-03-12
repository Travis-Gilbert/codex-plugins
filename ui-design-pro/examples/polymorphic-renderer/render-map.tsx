// Polymorphic Object Renderer
//
// Each content type gets its own visual treatment.
// The render map associates type discriminant to component.
// Shared tokens (spacing, color, type) unify without homogenizing.

import type { ReactNode } from "react";

// Discriminated union for content types
type ContentItem =
  | { type: "source"; slug: string; title: string; url: string; domain: string; excerpt: string }
  | { type: "essay"; slug: string; title: string; lead: string; readingTime: number; stage: string }
  | { type: "fieldNote"; slug: string; body: string; timestamp: string }
  | { type: "shelfEntry"; slug: string; title: string; coverUrl: string; rating: number; author: string }
  | { type: "thread"; slug: string; title: string; nodeCount: number; connectionCount: number }
  | { type: "videoProject"; slug: string; title: string; phase: string; thumbnailUrl: string };

// Type-safe render map
const renderers: Record<ContentItem["type"], (item: any) => ReactNode> = {
  source: (item) => (
    <a href={item.url} className="group block py-3 border-b border-neutral-100">
      <span className="text-xs tracking-wide text-neutral-400 uppercase">
        {item.domain}
      </span>
      <p className="text-sm font-medium text-neutral-800 group-hover:text-blue-700 mt-0.5">
        {item.title}
      </p>
      <p className="text-xs text-neutral-500 mt-1 line-clamp-2">{item.excerpt}</p>
    </a>
  ),

  essay: (item) => (
    <article className="py-6">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[10px] font-medium uppercase tracking-widest text-neutral-400">
          {item.stage}
        </span>
        <span className="text-[10px] text-neutral-300">
          {item.readingTime} min
        </span>
      </div>
      <h3 className="text-lg font-semibold text-neutral-900">{item.title}</h3>
      <p className="text-sm text-neutral-600 mt-2 leading-relaxed line-clamp-3">
        {item.lead}
      </p>
    </article>
  ),

  fieldNote: (item) => (
    <div className="py-4 pl-4 border-l-2 border-neutral-200">
      <time className="text-[10px] text-neutral-400 font-mono">
        {item.timestamp}
      </time>
      <p className="text-sm text-neutral-700 mt-1 italic">{item.body}</p>
    </div>
  ),

  shelfEntry: (item) => (
    <div className="flex gap-3 py-3">
      <img
        src={item.coverUrl}
        alt=""
        className="w-12 h-16 object-cover rounded-sm flex-shrink-0"
      />
      <div className="min-w-0">
        <p className="text-sm font-medium text-neutral-800 truncate">
          {item.title}
        </p>
        <p className="text-xs text-neutral-500">{item.author}</p>
        <div className="flex gap-0.5 mt-1">
          {Array.from({ length: 5 }, (_, i) => (
            <span
              key={i}
              className={i < item.rating ? "text-amber-400" : "text-neutral-200"}
            >
              ●
            </span>
          ))}
        </div>
      </div>
    </div>
  ),

  thread: (item) => (
    <div className="py-3 flex items-center gap-3">
      <div className="w-8 h-8 rounded-full bg-violet-50 flex items-center justify-center">
        <span className="text-xs font-mono text-violet-600">{item.nodeCount}</span>
      </div>
      <div>
        <p className="text-sm font-medium text-neutral-800">{item.title}</p>
        <p className="text-[10px] text-neutral-400">
          {item.connectionCount} connections
        </p>
      </div>
    </div>
  ),

  videoProject: (item) => (
    <div className="py-3 flex gap-3">
      <div className="relative w-24 h-14 rounded overflow-hidden flex-shrink-0 bg-neutral-100">
        <img src={item.thumbnailUrl} alt="" className="w-full h-full object-cover" />
        <span className="absolute bottom-1 right-1 text-[9px] bg-black/70 text-white px-1 rounded">
          {item.phase}
        </span>
      </div>
      <p className="text-sm font-medium text-neutral-800 self-center">
        {item.title}
      </p>
    </div>
  ),
};

// The renderer itself
export function ObjectRenderer({ item }: { item: ContentItem }) {
  const render = renderers[item.type];
  if (!render) {
    console.warn(`No renderer for type: ${(item as any).type}`);
    return null;
  }
  return <>{render(item)}</>;
}

// Usage in a heterogeneous feed
export function ContentFeed({ items }: { items: ContentItem[] }) {
  return (
    <div className="divide-y divide-neutral-50">
      {items.map((item) => (
        <ObjectRenderer key={item.slug} item={item} />
      ))}
    </div>
  );
}
