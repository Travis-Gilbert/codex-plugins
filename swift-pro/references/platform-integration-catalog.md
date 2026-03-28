# Apple Platform Integration Catalog

## Spotlight (Core Spotlight)

Index app content so it appears in system Spotlight search:

```swift
import CoreSpotlight
import MobileCoreServices

class SpotlightIndexer {
    static func indexItem(_ item: Article) {
        let attributeSet = CSSearchableItemAttributeSet(contentType: .text)
        attributeSet.title = item.title
        attributeSet.contentDescription = item.summary
        attributeSet.thumbnailData = item.thumbnailData
        attributeSet.keywords = item.tags
        attributeSet.lastUsedDate = item.lastModified
        attributeSet.contentCreationDate = item.createdAt

        let searchableItem = CSSearchableItem(
            uniqueIdentifier: item.id.uuidString,
            domainIdentifier: "com.app.articles",
            attributeSet: attributeSet
        )
        searchableItem.expirationDate = .distantFuture

        CSSearchableIndex.default().indexSearchableItems([searchableItem]) { error in
            if let error { print("Indexing failed: \(error)") }
        }
    }

    static func removeItem(id: UUID) {
        CSSearchableIndex.default().deleteSearchableItems(
            withIdentifiers: [id.uuidString]
        ) { error in
            if let error { print("Removal failed: \(error)") }
        }
    }

    static func removeAll() {
        CSSearchableIndex.default().deleteAllSearchableItems { error in
            if let error { print("Clear failed: \(error)") }
        }
    }
}

// Handle Spotlight taps — in App
.onContinueUserActivity(CSSearchableItemActionType) { activity in
    if let id = activity.userInfo?[CSSearchableItemActivityIdentifier] as? String {
        router.navigate(to: .article(id: UUID(uuidString: id)!))
    }
}

// NSUserActivity for Spotlight (handoff-compatible)
func registerActivity(for article: Article) -> NSUserActivity {
    let activity = NSUserActivity(activityType: "com.app.viewArticle")
    activity.title = article.title
    activity.isEligibleForSearch = true
    activity.isEligibleForHandoff = true
    activity.contentAttributeSet = buildAttributeSet(for: article)
    activity.userInfo = ["articleID": article.id.uuidString]
    return activity
}
```

---

## WidgetKit

### TimelineProvider

```swift
import WidgetKit
import SwiftUI

struct TaskWidget: Widget {
    let kind = "TaskWidget"

    var body: some WidgetConfiguration {
        AppIntentConfiguration(
            kind: kind,
            intent: TaskWidgetIntent.self,
            provider: TaskTimelineProvider()
        ) { entry in
            TaskWidgetView(entry: entry)
                .containerBackground(.fill.tertiary, for: .widget)
        }
        .configurationDisplayName("Tasks")
        .description("View your upcoming tasks")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge, .accessoryRectangular])
    }
}

struct TaskEntry: TimelineEntry {
    let date: Date
    let tasks: [TaskItem]
    let configuration: TaskWidgetIntent
}

struct TaskTimelineProvider: AppIntentTimelineProvider {
    func placeholder(in context: Context) -> TaskEntry {
        TaskEntry(date: .now, tasks: TaskItem.samples, configuration: TaskWidgetIntent())
    }

    func snapshot(for configuration: TaskWidgetIntent, in context: Context) async -> TaskEntry {
        let tasks = await fetchTasks(filter: configuration.filter)
        return TaskEntry(date: .now, tasks: tasks, configuration: configuration)
    }

    func timeline(for configuration: TaskWidgetIntent, in context: Context) async -> Timeline<TaskEntry> {
        let tasks = await fetchTasks(filter: configuration.filter)
        let entry = TaskEntry(date: .now, tasks: tasks, configuration: configuration)
        // Refresh every 30 minutes
        let nextUpdate = Calendar.current.date(byAdding: .minute, value: 30, to: .now)!
        return Timeline(entries: [entry], policy: .after(nextUpdate))
    }

    private func fetchTasks(filter: TaskFilter) async -> [TaskItem] {
        // Read from App Group shared container
        let store = SharedDataStore(groupID: "group.com.app.tasks")
        return store.tasks(matching: filter)
    }
}
```

### App Groups Data Sharing

```swift
// Shared UserDefaults
let sharedDefaults = UserDefaults(suiteName: "group.com.app.tasks")
sharedDefaults?.set(encodedTasks, forKey: "widgetTasks")

// Shared file container
let containerURL = FileManager.default.containerURL(
    forSecurityApplicationGroupIdentifier: "group.com.app.tasks"
)!
let dataURL = containerURL.appendingPathComponent("shared_data.json")

// Notify widget to reload
WidgetCenter.shared.reloadTimelines(ofKind: "TaskWidget")
// Or reload all widgets
WidgetCenter.shared.reloadAllTimelines()
```

### Widget Families

| Family | Size | Platform |
|--------|------|----------|
| `.systemSmall` | 2x2 grid | iOS, iPadOS |
| `.systemMedium` | 4x2 grid | iOS, iPadOS |
| `.systemLarge` | 4x4 grid | iOS, iPadOS |
| `.systemExtraLarge` | 8x4 (iPad only) | iPadOS |
| `.accessoryCircular` | Watch complication | watchOS, iOS Lock Screen |
| `.accessoryRectangular` | Watch rectangular | watchOS, iOS Lock Screen |
| `.accessoryInline` | Single line | watchOS, iOS Lock Screen |

---

## Share Extensions

```swift
// ShareViewController.swift
import UIKit
import UniformTypeIdentifiers

class ShareViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        guard let extensionItems = extensionContext?.inputItems as? [NSExtensionItem] else {
            close()
            return
        }

        for item in extensionItems {
            guard let attachments = item.attachments else { continue }
            for attachment in attachments {
                if attachment.hasItemConformingToTypeIdentifier(UTType.url.identifier) {
                    attachment.loadItem(forTypeIdentifier: UTType.url.identifier) { [weak self] item, error in
                        if let url = item as? URL {
                            DispatchQueue.main.async {
                                self?.handleSharedURL(url)
                            }
                        }
                    }
                } else if attachment.hasItemConformingToTypeIdentifier(UTType.plainText.identifier) {
                    attachment.loadItem(forTypeIdentifier: UTType.plainText.identifier) { [weak self] item, error in
                        if let text = item as? String {
                            DispatchQueue.main.async {
                                self?.handleSharedText(text)
                            }
                        }
                    }
                }
            }
        }
    }

    private func handleSharedURL(_ url: URL) {
        // Save to App Group shared storage
        let store = SharedDataStore(groupID: "group.com.app")
        store.addSharedItem(url: url)
        close()
    }

    private func close() {
        extensionContext?.completeRequest(returningItems: nil)
    }
}
```

---

## App Intents / Shortcuts

```swift
import AppIntents

struct AddTaskIntent: AppIntent {
    static var title: LocalizedStringResource = "Add Task"
    static var description = IntentDescription("Add a new task to your list")
    static var openAppWhenRun: Bool = false

    @Parameter(title: "Task Name")
    var name: String

    @Parameter(title: "Priority", default: .medium)
    var priority: TaskPriority

    @Parameter(title: "Due Date", optionsProvider: DateOptionsProvider())
    var dueDate: Date?

    func perform() async throws -> some IntentResult & ProvidesDialog & ReturnsValue<TaskItem> {
        let task = TaskItem(name: name, priority: priority, dueDate: dueDate)
        let store = TaskStore.shared
        try await store.add(task)

        return .result(
            value: task,
            dialog: "Added '\(name)' to your tasks"
        )
    }
}

// Make types work with App Intents
enum TaskPriority: String, AppEnum {
    case low, medium, high

    static var typeDisplayRepresentation = TypeDisplayRepresentation(name: "Priority")
    static var caseDisplayRepresentations: [TaskPriority: DisplayRepresentation] = [
        .low: "Low",
        .medium: "Medium",
        .high: "High",
    ]
}

// Register shortcuts
struct AppShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: AddTaskIntent(),
            phrases: [
                "Add a task in \(.applicationName)",
                "Create a new \(.applicationName) task",
            ],
            shortTitle: "Add Task",
            systemImageName: "plus.circle"
        )
    }
}
```

---

## CloudKit

```swift
import CloudKit

actor CloudKitService {
    private let container: CKContainer
    private let privateDB: CKDatabase
    private let sharedDB: CKDatabase

    init(containerID: String = "iCloud.com.app.myapp") {
        container = CKContainer(identifier: containerID)
        privateDB = container.privateCloudDatabase
        sharedDB = container.sharedCloudDatabase
    }

    // Save
    func save(_ item: Item) async throws {
        let record = CKRecord(recordType: "Item")
        record["title"] = item.title
        record["content"] = item.content
        record["createdAt"] = item.createdAt
        record["tags"] = item.tags as CKRecordValue

        try await privateDB.save(record)
    }

    // Fetch
    func fetchItems() async throws -> [Item] {
        let query = CKQuery(recordType: "Item", predicate: NSPredicate(value: true))
        query.sortDescriptors = [NSSortDescriptor(key: "createdAt", ascending: false)]

        let (results, _) = try await privateDB.records(matching: query, resultsLimit: 100)
        return results.compactMap { _, result in
            guard case .success(let record) = result else { return nil }
            return Item(
                title: record["title"] as? String ?? "",
                content: record["content"] as? String ?? "",
                createdAt: record["createdAt"] as? Date ?? .now
            )
        }
    }

    // Subscriptions for change notifications
    func subscribeToChanges() async throws {
        let subscription = CKQuerySubscription(
            recordType: "Item",
            predicate: NSPredicate(value: true),
            options: [.firesOnRecordCreation, .firesOnRecordUpdate, .firesOnRecordDeletion]
        )

        let notificationInfo = CKSubscription.NotificationInfo()
        notificationInfo.shouldSendContentAvailable = true  // Silent push
        subscription.notificationInfo = notificationInfo

        try await privateDB.save(subscription)
    }

    // Sharing
    func share(_ record: CKRecord) async throws -> CKShare {
        let share = CKShare(rootRecord: record)
        share[CKShare.SystemFieldKey.title] = "Shared Item"
        share.publicPermission = .readOnly

        let (savedShare, _) = try await privateDB.modifyRecords(saving: [record, share], deleting: [])
        return savedShare.first { $0 is CKShare } as! CKShare
    }
}
```

---

## Push Notifications

```swift
import UserNotifications

class NotificationManager: NSObject, UNUserNotificationCenterDelegate {
    static let shared = NotificationManager()

    func requestPermission() async -> Bool {
        do {
            let granted = try await UNUserNotificationCenter.current()
                .requestAuthorization(options: [.alert, .badge, .sound, .provisional])
            if granted {
                await MainActor.run {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
            return granted
        } catch {
            return false
        }
    }

    // Schedule local notification
    func scheduleReminder(for task: TaskItem) async throws {
        let content = UNMutableNotificationContent()
        content.title = "Task Reminder"
        content.body = task.name
        content.sound = .default
        content.categoryIdentifier = "TASK_REMINDER"
        content.userInfo = ["taskID": task.id.uuidString]

        let trigger = UNTimeIntervalNotificationTrigger(
            timeInterval: task.dueDate!.timeIntervalSinceNow,
            repeats: false
        )

        let request = UNNotificationRequest(
            identifier: task.id.uuidString,
            content: content,
            trigger: trigger
        )
        try await UNUserNotificationCenter.current().add(request)
    }

    // Notification categories with actions
    func registerCategories() {
        let completeAction = UNNotificationAction(
            identifier: "COMPLETE",
            title: "Mark Complete",
            options: [.authenticationRequired]
        )
        let snoozeAction = UNNotificationAction(
            identifier: "SNOOZE",
            title: "Snooze 1 Hour",
            options: []
        )

        let taskCategory = UNNotificationCategory(
            identifier: "TASK_REMINDER",
            actions: [completeAction, snoozeAction],
            intentIdentifiers: [],
            options: [.customDismissAction]
        )

        UNUserNotificationCenter.current().setNotificationCategories([taskCategory])
    }

    // Handle action responses
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse
    ) async {
        let taskID = response.notification.request.content.userInfo["taskID"] as? String

        switch response.actionIdentifier {
        case "COMPLETE":
            if let taskID { await TaskStore.shared.complete(id: taskID) }
        case "SNOOZE":
            // Reschedule
            break
        default:
            // Tapped notification — navigate to task
            if let taskID { await Router.shared.navigate(to: .task(id: taskID)) }
        }
    }
}

// APNs token registration (AppDelegate)
func application(_ app: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken token: Data) {
    let tokenString = token.map { String(format: "%02.2hhx", $0) }.joined()
    Task { try await APIClient.shared.registerPushToken(tokenString) }
}
```

---

## Handoff (NSUserActivity)

```swift
struct ArticleView: View {
    let article: Article

    var body: some View {
        ScrollView {
            ArticleContent(article: article)
        }
        .userActivity("com.app.viewArticle") { activity in
            activity.title = article.title
            activity.isEligibleForHandoff = true
            activity.isEligibleForSearch = true
            activity.userInfo = ["articleID": article.id.uuidString]
            activity.webpageURL = URL(string: "https://app.com/articles/\(article.id)")
        }
    }
}

// Receive handoff
.onContinueUserActivity("com.app.viewArticle") { activity in
    if let id = activity.userInfo?["articleID"] as? String {
        router.navigate(to: .article(id: UUID(uuidString: id)!))
    }
}
```

---

## StoreKit 2

```swift
import StoreKit

@Observable
class StoreManager {
    var products: [Product] = []
    var purchasedProductIDs: Set<String> = []

    private var transactionListener: Task<Void, Error>?

    init() {
        transactionListener = listenForTransactions()
    }

    deinit { transactionListener?.cancel() }

    // Load products
    func loadProducts() async throws {
        products = try await Product.products(for: [
            "com.app.premium.monthly",
            "com.app.premium.yearly",
            "com.app.feature.unlock",
        ])
    }

    // Purchase
    func purchase(_ product: Product) async throws -> Transaction? {
        let result = try await product.purchase()

        switch result {
        case .success(let verification):
            let transaction = try checkVerification(verification)
            await transaction.finish()
            purchasedProductIDs.insert(product.id)
            return transaction
        case .userCancelled:
            return nil
        case .pending:
            return nil
        @unknown default:
            return nil
        }
    }

    // Restore
    func restorePurchases() async {
        for await result in Transaction.currentEntitlements {
            if case .verified(let transaction) = result {
                purchasedProductIDs.insert(transaction.productID)
            }
        }
    }

    // Subscription status
    func subscriptionStatus() async -> Product.SubscriptionInfo.Status? {
        guard let product = products.first(where: { $0.type == .autoRenewable }) else { return nil }
        return try? await product.subscription?.status.first
    }

    // Transaction listener
    private func listenForTransactions() -> Task<Void, Error> {
        Task.detached {
            for await result in Transaction.updates {
                if case .verified(let transaction) = result {
                    await self.purchasedProductIDs.insert(transaction.productID)
                    await transaction.finish()
                }
            }
        }
    }

    private func checkVerification<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified(_, let error): throw error
        case .verified(let safe): return safe
        }
    }
}

// Subscription view
struct SubscriptionView: View {
    @Environment(StoreManager.self) private var store

    var body: some View {
        SubscriptionStoreView(
            groupID: "ABCDEF1234",
            visibleRelationships: .current
        )
        .subscriptionStoreControlStyle(.prominentPicker)
        .storeButton(.visible, for: .restorePurchases)
    }
}
```
