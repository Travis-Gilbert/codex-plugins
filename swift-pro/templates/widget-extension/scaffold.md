# WidgetKit Extension Template

## Directory Structure

```
AppNameWidgetExtension/
  AppNameWidget.swift          # Widget struct + configuration
  TimelineProvider.swift       # Timeline entry generation
  WidgetEntryView.swift        # Widget view
  AppNameWidgetBundle.swift    # Widget bundle (multiple widgets)
  SharedData.swift             # App Groups data bridge
  Intent/
    ConfigurationIntent.swift  # AppIntentConfiguration
```

## TimelineProvider

```swift
import WidgetKit

struct Provider: AppIntentTimelineProvider {
    typealias Entry = SimpleEntry
    typealias Intent = ConfigurationIntent

    func placeholder(in context: Context) -> SimpleEntry {
        SimpleEntry(date: .now, title: "Loading...", value: "--", configuration: ConfigurationIntent())
    }

    func snapshot(for configuration: ConfigurationIntent, in context: Context) async -> SimpleEntry {
        // Return representative data for the widget gallery
        SimpleEntry(date: .now, title: "Tasks", value: "5 remaining", configuration: configuration)
    }

    func timeline(for configuration: ConfigurationIntent, in context: Context) async -> Timeline<SimpleEntry> {
        var entries: [SimpleEntry] = []

        let data = await fetchData(for: configuration)
        let currentDate = Date.now

        // Generate entries for the next 5 hours
        for hourOffset in 0..<5 {
            let entryDate = Calendar.current.date(byAdding: .hour, value: hourOffset, to: currentDate)!
            let entry = SimpleEntry(
                date: entryDate,
                title: data.title,
                value: data.value,
                configuration: configuration
            )
            entries.append(entry)
        }

        // Refresh after the last entry's date
        return Timeline(entries: entries, policy: .atEnd)
    }

    private func fetchData(for configuration: ConfigurationIntent) async -> (title: String, value: String) {
        // Read from App Groups shared container or network
        let defaults = UserDefaults(suiteName: "group.com.example.appname")
        let count = defaults?.integer(forKey: "taskCount") ?? 0
        return (title: configuration.category?.name ?? "Tasks", value: "\(count) remaining")
    }
}
```

## Timeline Entry

```swift
import WidgetKit

struct SimpleEntry: TimelineEntry {
    let date: Date
    let title: String
    let value: String
    let configuration: ConfigurationIntent
}
```

## Widget Struct

```swift
import WidgetKit
import SwiftUI

struct AppNameWidget: Widget {
    let kind: String = "AppNameWidget"

    var body: some WidgetConfiguration {
        AppIntentConfiguration(
            kind: kind,
            intent: ConfigurationIntent.self,
            provider: Provider()
        ) { entry in
            WidgetEntryView(entry: entry)
                .containerBackground(.fill.tertiary, for: .widget)
        }
        .configurationDisplayName("App Summary")
        .description("Shows a quick summary of your data.")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge, .accessoryCircular, .accessoryRectangular, .accessoryInline])
    }
}
```

## Entry View

```swift
import SwiftUI
import WidgetKit

struct WidgetEntryView: View {
    @Environment(\.widgetFamily) var family
    var entry: Provider.Entry

    var body: some View {
        switch family {
        case .systemSmall:
            smallView
        case .systemMedium:
            mediumView
        case .systemLarge:
            largeView
        case .accessoryCircular:
            circularView
        case .accessoryRectangular:
            rectangularView
        case .accessoryInline:
            inlineView
        default:
            smallView
        }
    }

    // MARK: - Family-Specific Layouts

    private var smallView: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(entry.title)
                .font(.headline)
                .foregroundStyle(.secondary)
            Spacer()
            Text(entry.value)
                .font(.title)
                .fontWeight(.bold)
                .minimumScaleFactor(0.5)
            Text(entry.date, style: .relative)
                .font(.caption2)
                .foregroundStyle(.tertiary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var mediumView: some View {
        HStack {
            smallView
            Spacer()
            // Add a chart, progress ring, or secondary info
            Image(systemName: "chart.bar.fill")
                .font(.system(size: 48))
                .foregroundStyle(.tint)
        }
    }

    private var largeView: some View {
        VStack(alignment: .leading, spacing: 8) {
            smallView
            Divider()
            // List of items or detailed content
            ForEach(0..<4, id: \.self) { i in
                HStack {
                    Image(systemName: "circle")
                    Text("Item \(i + 1)")
                    Spacer()
                }
                .font(.subheadline)
            }
            Spacer()
        }
    }

    // MARK: - Lock Screen / Watch Complications

    private var circularView: some View {
        ZStack {
            AccessoryWidgetBackground()
            Text(entry.value)
                .font(.headline)
                .widgetAccentable()
        }
    }

    private var rectangularView: some View {
        VStack(alignment: .leading) {
            Text(entry.title)
                .font(.headline)
                .widgetAccentable()
            Text(entry.value)
                .font(.caption)
        }
    }

    private var inlineView: some View {
        Text("\(entry.title): \(entry.value)")
    }
}
```

## AppIntentConfiguration

```swift
import AppIntents
import WidgetKit

struct ConfigurationIntent: WidgetConfigurationIntent {
    static var title: LocalizedStringResource = "Configure Widget"
    static var description: IntentDescription = "Choose what to display."

    @Parameter(title: "Category")
    var category: CategoryEntity?
}

struct CategoryEntity: AppEntity {
    static var typeDisplayRepresentation = TypeDisplayRepresentation(name: "Category")
    static var defaultQuery = CategoryQuery()

    var id: String
    var name: String

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)")
    }
}

struct CategoryQuery: EntityQuery {
    func entities(for identifiers: [String]) async throws -> [CategoryEntity] {
        allCategories().filter { identifiers.contains($0.id) }
    }

    func suggestedEntities() async throws -> [CategoryEntity] {
        allCategories()
    }

    func defaultResult() async -> CategoryEntity? {
        allCategories().first
    }

    private func allCategories() -> [CategoryEntity] {
        [
            CategoryEntity(id: "tasks", name: "Tasks"),
            CategoryEntity(id: "goals", name: "Goals"),
            CategoryEntity(id: "habits", name: "Habits"),
        ]
    }
}
```

## App Groups Shared Data

```swift
import Foundation

enum SharedData {
    static let suiteName = "group.com.example.appname"

    static var defaults: UserDefaults? {
        UserDefaults(suiteName: suiteName)
    }

    // Write from main app
    static func update(taskCount: Int) {
        defaults?.set(taskCount, forKey: "taskCount")
    }

    // Read from widget
    static var taskCount: Int {
        defaults?.integer(forKey: "taskCount") ?? 0
    }

    // For complex shared data, use a shared JSON file:
    static var containerURL: URL? {
        FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: suiteName)
    }

    static func writeShared<T: Encodable>(_ value: T, filename: String) throws {
        guard let url = containerURL?.appendingPathComponent(filename) else { return }
        let data = try JSONEncoder().encode(value)
        try data.write(to: url)
    }

    static func readShared<T: Decodable>(_ type: T.Type, filename: String) throws -> T? {
        guard let url = containerURL?.appendingPathComponent(filename),
              FileManager.default.fileExists(atPath: url.path) else { return nil }
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode(T.self, from: data)
    }
}
```

## Widget Bundle (Multiple Widgets)

```swift
import WidgetKit
import SwiftUI

@main
struct AppNameWidgetBundle: WidgetBundle {
    var body: some Widget {
        AppNameWidget()
        AppNameLiveActivityWidget()  // If using Live Activities
    }
}
```

## Setup Checklist

- [ ] Add Widget Extension target in Xcode
- [ ] Enable App Groups capability on both main app and widget extension
- [ ] Use the same App Group identifier in both targets
- [ ] Add shared files to both targets or use a shared framework
- [ ] Call `WidgetCenter.shared.reloadAllTimelines()` from the main app when data changes
