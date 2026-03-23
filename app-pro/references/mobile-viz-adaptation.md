# Mobile Visualization Adaptation

> Per-viz-type adaptation level selection.

## The Four Levels

| Level | Name | Effort | Description |
|-------|------|--------|-------------|
| 1 | Responsive resize | Low | Render at container width |
| 2 | Simplified rendering | Medium | Same type, reduced detail |
| 3 | Alternative representation | High | Different viz, same data |
| 4 | Defer to native | Highest | Use native Canvas/GL in RN |

## Decision Matrix

| Visualization | Adaptation Level | Rationale |
|---------------|-----------------|-----------|
| Bar chart | 1: Resize | Simple geometry, scales well |
| Line chart | 1: Resize | Works at any width |
| Area chart | 1: Resize | Same as line chart |
| Scatter plot (< 100 points) | 1: Resize | Manageable density |
| Scatter plot (100+ points) | 2: Simplify | Reduce points, add density viz |
| Pie/donut | 1: Resize | Circular geometry works anywhere |
| Force graph (< 50 nodes) | 2: Simplify | Hide labels, reduce edges |
| Force graph (50-200) | 3: Substitute | Searchable list + subgraph on tap |
| Force graph (200+) | 4: Native | WebView cannot handle render load |
| Treemap (< 3 levels) | 1-2: Resize/simplify | Top levels visible |
| Treemap (3+ levels) | 2: Simplify | Show top 2 levels only |
| Sankey diagram | 3: Substitute | Table or ranked flow list |
| Chord diagram | 3: Substitute | Matrix table or list |
| Timeline (linear) | 1-2: Resize + scroll | Natural horizontal swipe |
| Geographic map | 1: Resize | Maps are mobile-native |
| Network diagram | 2-3: Depends on density | See force graph rules |

## D3 Mobile Patterns

### 1. Touch Replaces Hover

```javascript
// Desktop
node.on('mouseover', showTooltip).on('mouseout', hideTooltip);

// Mobile: toggle on tap
node.on('click', function(event, d) {
  const isActive = d3.select(this).classed('active');
  d3.selectAll('.node').classed('active', false);
  if (!isActive) {
    d3.select(this).classed('active', true);
    showDetailPanel(d);
  } else {
    hideDetailPanel();
  }
});
```

### 2. Precomputed Layouts

Run force simulation at build time or on the server:

```javascript
// Build script (not client-side)
const simulation = d3.forceSimulation(nodes)
  .force('charge', d3.forceManyBody().strength(-100))
  .force('link', d3.forceLink(links))
  .force('center', d3.forceCenter(width/2, height/2));

// Run to completion
simulation.tick(300);

// Save positions
const positioned = nodes.map(n => ({ ...n, x: n.x, y: n.y }));
fs.writeFileSync('positioned-graph.json', JSON.stringify(positioned));
```

On mobile, render static positions. Only run simulation if user drags.

### 3. Canvas for Large Datasets

SVG: each element is a DOM node. Expensive for 100+ elements.
Canvas: paints to bitmap. No DOM overhead.

```javascript
// Canvas renderer for force graph
const canvas = d3.select('#graph').append('canvas');
const ctx = canvas.node().getContext('2d');

function draw() {
  ctx.clearRect(0, 0, width, height);
  links.forEach(l => { ctx.beginPath(); /* draw line */ });
  nodes.forEach(n => { ctx.beginPath(); /* draw circle */ });
}
```

### 4. Progressive Disclosure

Show top-N nodes by degree/importance. Expand on interaction:

```javascript
const visibleNodes = nodes
  .sort((a, b) => b.degree - a.degree)
  .slice(0, 30);

// On tap: expand neighborhood
node.on('click', (event, d) => {
  const neighbors = links
    .filter(l => l.source === d || l.target === d)
    .map(l => l.source === d ? l.target : l.source);
  addToVisible(neighbors);
});
```

### 5. Contained Pan/Zoom

```javascript
const zoom = d3.zoom()
  .scaleExtent([0.5, 4])
  .translateExtent([[0, 0], [width, height]])
  .on('zoom', (event) => {
    g.attr('transform', event.transform);
  });

// Wrapper captures touch; surrounding page scrolls normally
svg.call(zoom);
```

Double-tap to reset: `svg.on('dblclick.zoom', null)` then add custom
double-tap handler that resets to identity transform.

## React Native Visualization Libraries

| Library | API Style | Renderer | Best For |
|---------|-----------|----------|----------|
| Victory Native | Declarative JSX | Skia | Standard charts |
| react-native-skia | Imperative Canvas | Skia GPU | Custom 2D, high perf |
| expo-gl | WebGL/Three.js | OpenGL ES | 3D only |
| react-native-svg | SVG JSX | Native SVG | Simple diagrams (< 100 elements) |

## Frame Budget

16ms per frame for 60fps. Measure with:

- **Web**: `performance.mark()` / `performance.measure()`
- **RN Skia**: `useFrameCallback` timing
- **Chrome DevTools**: Performance tab, frame timeline

If a frame consistently exceeds 16ms on 4x CPU throttle, reduce
complexity (fewer nodes, simpler geometry, Canvas over SVG).
