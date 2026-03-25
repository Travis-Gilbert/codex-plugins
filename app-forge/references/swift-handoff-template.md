# Swift/AppKit Handoff Template

> Fill in each section. Every section is required, even if marked "Not applicable for v1." This document is the contract between App-Forge (architecture planning) and a future Swift-Pro plugin (implementation).

---

## 1. Window Architecture

### Main Window
- **Type**: [NSWindow with NSSplitViewController / NSTabViewController / custom]
- **Initial size**: [width x height, e.g., 1200 x 800]
- **Minimum size**: [width x height, e.g., 800 x 600]
- **Title bar style**: [standard / hidden / hidden with inline toolbar]

### Split View Configuration
- **Sidebar**: [width, collapsible?, items]
- **Content**: [main content area behavior]
- **Inspector**: [width, collapsible?, toggle shortcut]

### Toolbar
| Item | Type | Action | Shortcut |
|------|------|--------|----------|
| [item] | [button/segmented/search] | [action] | [shortcut] |

### Auxiliary Windows
| Window | Purpose | Size | Modal? |
|--------|---------|------|--------|
| [window] | [purpose] | [size] | [yes/no] |

---

## 2. Navigation Map

### Sidebar Hierarchy
```
├── [Section 1]
│   ├── [Item A]
│   └── [Item B]
├── [Section 2]
│   └── [Item C]
└── [Section 3]
```

### Detail View Routing
| Sidebar Selection | Detail View | Notes |
|-------------------|-------------|-------|
| [item] | [view] | [notes] |

### Sheets and Popovers
| Trigger | Type | Content | Size |
|---------|------|---------|------|
| [trigger] | [sheet/popover] | [content] | [size] |

### Keyboard Shortcuts
| Shortcut | Action | Scope |
|----------|--------|-------|
| ⌘N | [action] | [global/window] |
| ⌘K | [action] | [global/window] |

---

## 3. Data Model Mapping

### Entity Map
| Django Model | SwiftData Entity | Notes |
|-------------|-----------------|-------|
| [Model] | [Entity] | [notes] |

### Field-by-Field Mapping
#### [ModelName]
| Django Field | Type | SwiftData Property | Type | Notes |
|-------------|------|-------------------|------|-------|
| [field] | [type] | [property] | [type] | [notes] |

### Relationships
| Django Relationship | Type | SwiftData Equivalent | Notes |
|--------------------|------|---------------------|-------|
| [Model.field] | [FK/M2M/O2O] | [relationship type] | [notes] |

### Computed Properties
| Django Annotation/Property | SwiftData Implementation | Notes |
|---------------------------|-------------------------|-------|
| [property] | [approach] | [notes] |

### Sync Strategy
- **Direction**: [server→client / bidirectional / client→server]
- **Frequency**: [on-demand / interval / real-time]
- **Conflict resolution**: [server-wins / client-wins / manual merge]
- **Offline behavior**: [read-only cache / full offline / no offline]

---

## 4. API Integration Plan

### Endpoint Inventory
| Method | Path | Purpose | Auth Required |
|--------|------|---------|--------------|
| GET | [path] | [purpose] | [yes/no] |
| POST | [path] | [purpose] | [yes/no] |

### Auth Flow
- **Token type**: [JWT / session / OAuth2]
- **Storage**: [Keychain / UserDefaults]
- **Refresh**: [strategy]
- **Login UI**: [window type, flow description]

### Offline Cache
| Entity | Cache Strategy | TTL | Invalidation |
|--------|---------------|-----|-------------|
| [entity] | [strategy] | [ttl] | [trigger] |

### Background Refresh
- **Scheduler**: [NSBackgroundActivityScheduler / URLSession background]
- **Interval**: [frequency]
- **Constraints**: [network required, power required]

---

## 5. Native Feature Inventory

### Spotlight
| Entity | Indexed Fields | Content Type |
|--------|---------------|-------------|
| [entity] | [fields] | [UTType] |

### Quick Look
| Object Type | Preview Format | Generator |
|-------------|---------------|-----------|
| [type] | [format] | [approach] |

### Share Extensions
- **Incoming**: [what can be shared INTO the app]
- **Outgoing**: [what can be shared FROM the app]

### Widgets
| Widget | Size | Content | Refresh |
|--------|------|---------|---------|
| [widget] | [small/medium/large] | [content] | [timeline] |

### Shortcuts (Siri / Shortcuts App)
| Shortcut | Parameters | Result |
|----------|-----------|--------|
| [shortcut] | [params] | [result] |

---

## 6. Visualization Approach

### Knowledge Graph Rendering
| Approach | Pros | Cons |
|----------|------|------|
| SpriteKit | 2D, physics engine, hardware-accelerated | Limited 3D |
| Metal | Maximum performance, custom shaders | Complex, low-level |
| WKWebView + D3 | Reuse existing D3 code | WebView overhead |
| AppKit Drawing | Simple, native | No GPU acceleration |

**Recommendation**: [approach] because [reasoning]

---

## 7. Build and Distribution

### Signing
- **Method**: [Developer ID / Mac App Store]
- **Team ID**: [if known]
- **Entitlements**: [list required entitlements]

### Notarization
- **Required**: [yes/no]
- **Hardened runtime exceptions**: [list if any]

### Updates
- **Mechanism**: [Sparkle / Mac App Store / manual]
- **Update URL**: [if Sparkle]
- **Check frequency**: [interval]

### Target
- **Minimum macOS**: [version, e.g., 14.0 Sonoma]
- **Architectures**: [Universal / ARM only / Intel only]
- **Sandbox**: [yes/no, with reasoning]
