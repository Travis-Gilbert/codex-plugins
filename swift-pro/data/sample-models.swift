// sample-models.swift
// Example SwiftData models for testing and reference.
// These models demonstrate @Model, relationships, and @Query patterns.

import Foundation
import SwiftData

// MARK: - Content Object

@Model
final class ContentObject {
    var title: String
    var content: String
    var objectType: String
    var slug: String
    var createdAt: Date
    var updatedAt: Date
    var isDeleted: Bool

    @Relationship(deleteRule: .cascade, inverse: \Edge.fromObject)
    var outgoingEdges: [Edge]

    @Relationship(deleteRule: .cascade, inverse: \Edge.toObject)
    var incomingEdges: [Edge]

    @Relationship(inverse: \Notebook.objects)
    var notebooks: [Notebook]

    init(title: String, content: String, objectType: String) {
        self.title = title
        self.content = content
        self.objectType = objectType
        self.slug = title.lowercased().replacingOccurrences(of: " ", with: "-")
        self.createdAt = .now
        self.updatedAt = .now
        self.isDeleted = false
        self.outgoingEdges = []
        self.incomingEdges = []
        self.notebooks = []
    }
}

// MARK: - Edge (Connection)

@Model
final class Edge {
    var edgeType: String
    var strength: Double
    var createdAt: Date

    var fromObject: ContentObject?
    var toObject: ContentObject?

    init(edgeType: String, strength: Double = 0.5) {
        self.edgeType = edgeType
        self.strength = strength
        self.createdAt = .now
    }
}

// MARK: - Notebook

@Model
final class Notebook {
    var title: String
    var notebookDescription: String
    var createdAt: Date
    var updatedAt: Date

    var objects: [ContentObject]

    init(title: String, description: String = "") {
        self.title = title
        self.notebookDescription = description
        self.createdAt = .now
        self.updatedAt = .now
        self.objects = []
    }
}

// MARK: - Model Container Setup

extension ModelContainer {
    static func makeDefault() throws -> ModelContainer {
        let schema = Schema([
            ContentObject.self,
            Edge.self,
            Notebook.self,
        ])
        let configuration = ModelConfiguration(
            schema: schema,
            isStoredInMemoryOnly: false
        )
        return try ModelContainer(for: schema, configurations: [configuration])
    }

    static func makeInMemory() throws -> ModelContainer {
        let schema = Schema([
            ContentObject.self,
            Edge.self,
            Notebook.self,
        ])
        let configuration = ModelConfiguration(
            schema: schema,
            isStoredInMemoryOnly: true
        )
        return try ModelContainer(for: schema, configurations: [configuration])
    }
}
