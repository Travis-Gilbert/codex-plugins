// REFERENCE: @Model Macro (SwiftData)
// Persistent models, stored/transient properties, unique constraints

import SwiftData
import Foundation

// ─── @Model Declaration ──────────────────────────────────────────────
// @Model makes a class a persistent SwiftData model.
// All stored properties are persisted by default.

@Model
final class Article {
    // Persistent stored properties
    var title: String
    var body: String
    var publishedAt: Date
    var viewCount: Int
    var rating: Double?            // Optional properties supported
    var tags: [String]             // Arrays of value types supported
    var metadata: [String: String] // Dictionaries of value types supported

    // Supported property types:
    //   Bool, Int, Int8...Int64, UInt...UInt64, Float, Double, Decimal
    //   String, Date, Data, URL, UUID
    //   Optional<T> where T is supported
    //   Array<T> where T is supported
    //   Dictionary<String, T> where T is supported
    //   Enums conforming to Codable (backed by raw value)
    //   Other @Model types (relationships)

    init(title: String, body: String) {
        self.title = title
        self.body = body
        self.publishedAt = .now
        self.viewCount = 0
        self.rating = nil
        self.tags = []
        self.metadata = [:]
    }
}

// ─── Transient Properties ────────────────────────────────────────────
// @Transient excludes a property from persistence.

@Model
final class Player {
    var name: String
    var highScore: Int

    @Transient
    var currentSessionScore: Int = 0   // Not saved to disk

    @Transient
    var isOnline: Bool = false          // Not saved to disk

    // Computed properties are inherently transient
    var displayName: String {
        "\(name) (\(highScore) pts)"
    }

    init(name: String, highScore: Int = 0) {
        self.name = name
        self.highScore = highScore
    }
}

// ─── Unique Constraints ──────────────────────────────────────────────
// #Unique enforces uniqueness across one or more properties.
// On conflict, SwiftData updates the existing record (upsert).

@Model
final class User {
    #Unique([\.email])
    #Unique([\.username])

    var email: String
    var username: String
    var displayName: String

    init(email: String, username: String, displayName: String) {
        self.email = email
        self.username = username
        self.displayName = displayName
    }
}

// Compound unique constraint:
@Model
final class Enrollment {
    #Unique([\.studentID, \.courseID])

    var studentID: String
    var courseID: String
    var enrolledAt: Date

    init(studentID: String, courseID: String) {
        self.studentID = studentID
        self.courseID = courseID
        self.enrolledAt = .now
    }
}

// ─── Relationships ───────────────────────────────────────────────────
// Use @Relationship to define how models connect.

@Model
final class Author {
    var name: String

    // One-to-many: author has many books
    @Relationship(deleteRule: .cascade, inverse: \Book.author)
    var books: [Book]

    init(name: String) {
        self.name = name
        self.books = []
    }
}

@Model
final class Book {
    var title: String
    var author: Author?           // Many-to-one (inverse side)

    // Many-to-many
    @Relationship(inverse: \Category.books)
    var categories: [Category]

    init(title: String, author: Author? = nil) {
        self.title = title
        self.author = author
        self.categories = []
    }
}

@Model
final class Category {
    var name: String
    var books: [Book]

    init(name: String) {
        self.name = name
        self.books = []
    }
}

// Delete rules:
//   .nullify  — Set the inverse to nil (default)
//   .cascade  — Delete related objects
//   .deny     — Prevent deletion if related objects exist
//   .noAction — Do nothing (manual cleanup)

// ─── Enum Properties ─────────────────────────────────────────────────
// Enums must conform to Codable to be persisted.

@Model
final class Task {
    var title: String
    var status: Status
    var priority: Priority

    enum Status: String, Codable {
        case todo, inProgress, done
    }

    enum Priority: Int, Codable, Comparable {
        case low = 0, medium = 1, high = 2

        static func < (lhs: Priority, rhs: Priority) -> Bool {
            lhs.rawValue < rhs.rawValue
        }
    }

    init(title: String, status: Status = .todo, priority: Priority = .medium) {
        self.title = title
        self.status = status
        self.priority = priority
    }
}

// ─── Custom Codable Properties ───────────────────────────────────────
// Complex value types work if they conform to Codable.

struct Address: Codable {
    var street: String
    var city: String
    var zip: String
}

@Model
final class Contact {
    var name: String
    var address: Address    // Persisted as encoded data

    init(name: String, address: Address) {
        self.name = name
        self.address = address
    }
}

// ─── Index Attributes ────────────────────────────────────────────────
// Use #Index for query performance on frequently filtered/sorted properties.

@Model
final class LogEntry {
    #Index([\.timestamp])
    #Index([\.level, \.timestamp])

    var message: String
    var level: String
    var timestamp: Date

    init(message: String, level: String) {
        self.message = message
        self.level = level
        self.timestamp = .now
    }
}
