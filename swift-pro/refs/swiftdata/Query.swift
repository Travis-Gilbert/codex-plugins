// REFERENCE: @Query Property Wrapper and #Predicate (SwiftData)
// Declarative data fetching in SwiftUI views

import SwiftUI
import SwiftData

// ─── Basic @Query ────────────────────────────────────────────────────
// @Query fetches data from the model context and keeps the view updated.

struct ArticleListView: View {
    // Fetch all articles, no filtering
    @Query private var articles: [Article]

    var body: some View {
        List(articles) { article in
            Text(article.title)
        }
    }
}

// ─── @Query with Sort ────────────────────────────────────────────────

struct SortedListView: View {
    // Single sort descriptor
    @Query(sort: \Article.publishedAt, order: .reverse)
    private var articles: [Article]

    // Multiple sort descriptors
    @Query(sort: [
        SortDescriptor(\Article.viewCount, order: .reverse),
        SortDescriptor(\Article.title)
    ])
    private var rankedArticles: [Article]

    var body: some View {
        List(articles) { article in
            Text(article.title)
        }
    }
}

// ─── @Query with Filter (#Predicate) ────────────────────────────────

struct FilteredListView: View {
    @Query(
        filter: #Predicate<Article> { $0.viewCount > 100 },
        sort: \Article.publishedAt,
        order: .reverse
    )
    private var popularArticles: [Article]

    var body: some View {
        List(popularArticles) { article in
            Text("\(article.title) (\(article.viewCount) views)")
        }
    }
}

// ─── #Predicate Syntax ───────────────────────────────────────────────
// Type-safe predicates using Swift expressions.

// String operations:
let titleSearch = #Predicate<Article> {
    $0.title.localizedStandardContains("Swift")
}

let startsWithA = #Predicate<Article> {
    $0.title.starts(with: "A")
}

// Comparison operators:
let recentArticles = #Predicate<Article> {
    $0.publishedAt > Date.now.addingTimeInterval(-86400 * 7)
}

// Logical operators:
let popularRecent = #Predicate<Article> {
    $0.viewCount > 100 && $0.publishedAt > Date.now.addingTimeInterval(-86400 * 30)
}

// Optional handling:
let rated = #Predicate<Article> {
    $0.rating != nil
}

let highRated = #Predicate<Article> {
    if let rating = $0.rating {
        return rating > 4.0
    }
    return false
}

// Collection predicates:
let hasTag = #Predicate<Article> {
    $0.tags.contains("swift")
}

// Negation:
let notArchived = #Predicate<Article> {
    $0.viewCount > 0  // Example — negate with !
}

// ─── Dynamic @Query with Init ────────────────────────────────────────
// Change the query based on parameters by configuring in init.

struct DynamicFilterList: View {
    @Query private var articles: [Article]

    init(minViews: Int, searchText: String) {
        let predicate: Predicate<Article>
        if searchText.isEmpty {
            predicate = #Predicate { $0.viewCount >= minViews }
        } else {
            predicate = #Predicate {
                $0.viewCount >= minViews &&
                $0.title.localizedStandardContains(searchText)
            }
        }
        _articles = Query(
            filter: predicate,
            sort: [SortDescriptor(\Article.publishedAt, order: .reverse)]
        )
    }

    var body: some View {
        List(articles) { article in
            Text(article.title)
        }
    }
}

// Parent view drives the parameters:
struct ParentView: View {
    @State private var searchText = ""

    var body: some View {
        DynamicFilterList(minViews: 10, searchText: searchText)
            .searchable(text: $searchText)
    }
}

// ─── @Query with Animation ───────────────────────────────────────────
// Animate changes to query results.

struct AnimatedListView: View {
    @Query(sort: \Article.title, animation: .default)
    private var articles: [Article]

    var body: some View {
        List(articles) { article in
            Text(article.title)
        }
    }
}

// ─── @Query with FetchDescriptor ─────────────────────────────────────
// Use FetchDescriptor for full control.

struct PaginatedView: View {
    @Query private var articles: [Article]

    init(page: Int, pageSize: Int = 20) {
        var descriptor = FetchDescriptor<Article>(
            sortBy: [SortDescriptor(\.publishedAt, order: .reverse)]
        )
        descriptor.fetchLimit = pageSize
        descriptor.fetchOffset = page * pageSize
        _articles = Query(descriptor)
    }

    var body: some View {
        List(articles) { article in
            Text(article.title)
        }
    }
}

// ─── Predicate Variable Capture ──────────────────────────────────────
// Predicates can capture local variables (must be value types).

func makePredicate(authorName: String, minViews: Int) -> Predicate<Article> {
    #Predicate<Article> {
        $0.title.localizedStandardContains(authorName) &&
        $0.viewCount >= minViews
    }
}

// ─── Predicate Limitations ───────────────────────────────────────────
// #Predicate supports a SUBSET of Swift expressions:
//   Supported: ==, !=, <, >, <=, >=, &&, ||, !
//   Supported: .contains, .starts(with:), .localizedStandardContains
//   Supported: Optional chaining, if-let
//   NOT supported: Custom functions, closures, switch, complex expressions
//   NOT supported: Regex, string interpolation
//   NOT supported: Cross-model joins (use relationships instead)
