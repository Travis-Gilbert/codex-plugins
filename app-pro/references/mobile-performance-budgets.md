# Mobile Performance Budgets

> LCP, INP, bundle size, battery, mid-range targets.

## Core Web Vitals (Mobile)

| Metric | Target | What It Measures |
|--------|--------|------------------|
| LCP | < 2.5s on 4G | Largest visible content painted |
| INP | < 200ms | Interaction-to-next-paint latency |
| CLS | < 0.1 | Layout stability (no jumps) |

**Test on 4G throttled connection, not WiFi.**

## JavaScript Budget

| Category | Budget | Why |
|----------|--------|-----|
| Initial bundle | < 200KB compressed | First paint speed |
| Total JS | < 500KB compressed | Parse time on mid-range |
| Per-route chunk | < 50KB compressed | Navigation speed |

### Measurement

```bash
# Next.js
npx @next/bundle-analyzer

# React Native
npx react-native-bundle-visualizer
```

## List Performance (React Native)

### FlatList Optimization

```typescript
<FlatList
  data={items}
  renderItem={renderItem}
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
  windowSize={5}           // Render 5 screens worth
  maxToRenderPerBatch={10} // 10 items per batch
  removeClippedSubviews    // Detach offscreen views
  keyExtractor={item => item.id}
/>
```

### When to Use Which List

| Component | Use When |
|-----------|----------|
| FlatList | Homogeneous list > 20 items |
| SectionList | Grouped data with headers |
| FlashList (Shopify) | 1000+ items, need 60fps |
| ScrollView | < 20 items, heterogeneous |

## Image Optimization

### Web (Next.js)

```tsx
<Image
  src={url}
  width={375}
  height={200}
  sizes="(max-width: 768px) 100vw, 50vw"
  priority={isAboveFold}
  placeholder="blur"
  blurDataURL={blurHash}
/>
```

### React Native

```tsx
<Image
  source={{ uri: url }}
  style={{ width: 375, height: 200 }}
  resizeMode="cover"
  // Use expo-image for better caching:
  // import { Image } from 'expo-image';
  // cachePolicy="memory-disk"
/>
```

## Battery Efficiency

- **No continuous animation** when screen is not visible. Use
  `AppState.addEventListener('change')` to pause.
- **Batch network requests.** Don't fire 5 parallel fetches on mount.
  Use composite endpoints.
- **Reduce GPS polling.** If location is needed, use significant-change
  monitoring instead of continuous updates.
- **Avoid wake locks.** Don't prevent the screen from sleeping unless
  actively playing media or navigating.

## Testing Methodology

### Web

- Chrome DevTools → Performance tab → CPU throttle 4x
- Lighthouse → Mobile preset
- WebPageTest → Moto G4 on 4G

### React Native

- Real device: any Android with 4GB RAM, 2-year-old processor
- Flipper → Performance plugin
- `react-native-performance` for in-app metrics
- EAS Build with `--profile production` for realistic builds
