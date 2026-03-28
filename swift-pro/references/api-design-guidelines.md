# Swift API Design Guidelines (Condensed)

Based on Apple's official Swift API Design Guidelines. These rules apply to all Swift code: app code, frameworks, and packages.

---

## Fundamentals

**Clarity at the point of use** is the most important goal. Code is read far more often than written. Optimize for the reader.

**Clarity over brevity.** Shortest code is not the goal. Minimize unnecessary words, but include all words needed for comprehension.

**Write a documentation comment** for every declaration. If you cannot describe its purpose simply, you may have designed the wrong API.

---

## Naming Conventions

### Methods Read as English Phrases

Call sites should form grammatical English phrases:

```swift
// GOOD: reads as "insert y at z"
array.insert(element, at: index)

// GOOD: reads as "remove element at index"
array.remove(at: index)

// BAD: unclear what x is relative to
array.insert(element, position: index)

// BAD: reads awkwardly
array.remove(index)
```

### Naming Mutating vs Non-Mutating Pairs

| Pattern | Mutating (verb) | Non-mutating (noun/participle) |
|---------|-----------------|-------------------------------|
| -ed suffix | `sort()` | `sorted()` |
| -ing suffix | `strip()` | `stripping()` |
| form- prefix | `formUnion(other)` | `union(other)` |

```swift
// Mutating: verb
var numbers = [3, 1, 2]
numbers.sort()                    // Modifies in place
numbers.append(4)                 // Modifies in place
numbers.reverse()                 // Modifies in place

// Non-mutating: -ed or -ing
let sorted = numbers.sorted()    // Returns new value
let reversed = numbers.reversed() // Returns new value
let filtered = numbers.filter { $0 > 2 }  // Returns new value
```

### Boolean Assertions

Booleans read as assertions about the receiver:

```swift
// GOOD: reads as "line1 intersects line2"
line1.intersects(line2)

// GOOD: reads as "set isEmpty"
set.isEmpty

// GOOD: reads as "view isHidden"
view.isHidden

// BAD: reads as "line1 intersect line2" (verb, not assertion)
line1.intersect(line2)

// BAD: ambiguous -- "is the set empty?" vs "empty the set"
set.empty
```

Boolean properties and methods: use `is`, `has`, `can`, `should`, `will` prefixes.

```swift
var isEnabled: Bool
var hasContent: Bool
var canUndo: Bool
var shouldAutorotate: Bool
func isEqual(to other: Self) -> Bool
```

### Protocols

**Protocols describing capabilities** use `-able`, `-ible`, or `-ing`:

```swift
protocol Equatable { }      // "can be equated"
protocol Hashable { }       // "can be hashed"
protocol Sendable { }       // "can be sent"
protocol Comparable { }     // "can be compared"
protocol Identifiable { }   // "has an identity"
protocol Encoding { }       // "performs encoding"
```

**Protocols describing what something is** use nouns:

```swift
protocol Collection { }     // "is a collection"
protocol Sequence { }       // "is a sequence"
protocol View { }           // "is a view"
```

### Factory Methods

Use `make` prefix for factory methods that return a new instance:

```swift
// GOOD
func makeIterator() -> Iterator
func makeBody(configuration: Configuration) -> some View
func makeUIViewController(context: Context) -> UIViewController

// BAD: unclear that it creates a new object
func iterator() -> Iterator
func body(configuration: Configuration) -> some View
```

### Type Names

| Type | Convention | Examples |
|------|-----------|----------|
| Protocols (capability) | `-able`, `-ible`, `-ing` | `Sendable`, `Codable`, `Loading` |
| Protocols (identity) | Noun | `Collection`, `View`, `Error` |
| Structs | Noun | `Point`, `Color`, `UserProfile` |
| Classes | Noun | `ViewController`, `NetworkManager` |
| Enums | Singular noun | `Direction`, `HTTPMethod`, `Theme` |
| Enum cases | lowerCamelCase | `.north`, `.get`, `.dark` |
| Generic params | Single uppercase or descriptive | `T`, `Element`, `Key`, `Value` |

---

## Parameter Labels

### First Argument Reads as Part of the Method Name

```swift
// GOOD: "send message to recipient"
func send(_ message: Message, to recipient: User)

// GOOD: "remove item at index"
func remove(at index: Int) -> Element

// GOOD: "move item from source to destination"
func move(from source: Int, to destination: Int)

// BAD: "send message message recipient"
func send(message: Message, recipient: User)
```

### Omit the First Label When...

The first argument completes a grammatical phrase with the method name:

```swift
// "append element" -- element is obvious from context
func append(_ element: Element)

// "contains element"
func contains(_ element: Element) -> Bool

// "distance to point"
func distance(to point: Point) -> Double
```

### Always Label When...

Arguments are peers with no natural ordering or the role is ambiguous:

```swift
// GOOD: all arguments labeled for clarity
func move(from source: Index, to destination: Index)

// GOOD: peer arguments
func clamp(min: Int, max: Int) -> Int

// BAD: which is min, which is max?
func clamp(_ min: Int, _ max: Int) -> Int
```

### Weak Type Information Needs Labels

When the type does not convey the parameter's role:

```swift
// BAD: what does the String mean?
func add(_ text: String)

// GOOD: label clarifies the role
func add(name text: String)

// BAD: two Ints with unclear roles
func draw(_ width: Int, _ height: Int)

// GOOD
func draw(width: Int, height: Int)
```

---

## Type Conventions

### Protocols for Capabilities

Define what a type can do:

```swift
protocol DataLoading {
    func loadData() async throws -> Data
}

protocol Cacheable {
    var cacheKey: String { get }
    var cacheExpiry: Date { get }
}
```

### Structs for Values

Use structs for types that represent values with no identity:

```swift
struct Coordinate: Hashable {
    let latitude: Double
    let longitude: Double
}

struct Money: Equatable {
    let amount: Decimal
    let currency: Currency
}

// Value types are preferred in Swift
// Use structs unless you need identity or inheritance
```

### Classes for Identity

Use classes when instances have identity (two instances with the same data are NOT the same):

```swift
class DatabaseConnection {
    let id = UUID()
    private var handle: OpaquePointer
    // Two connections to the same DB are different objects
}

class FileHandle {
    // Wraps a system resource with identity
}
```

### Actors for Shared Mutable State

```swift
actor ImageCache {
    private var cache: [URL: UIImage] = [:]
    // Protects mutable state from data races
}
```

---

## Common Patterns

### Result Type

```swift
// Use throws for synchronous code (preferred in Swift)
func parse(_ input: String) throws -> Document

// Use Result when you need to store or pass errors
func validate(_ form: Form) -> Result<ValidatedForm, ValidationError>

// Async code uses throws naturally
func fetchUser() async throws -> User
```

### Throws vs Optionals

```swift
// Use throws when the caller needs to know WHY it failed
func loadDocument(at path: String) throws -> Document

// Use optionals when failure is a normal, expected case
func find(_ element: Element) -> Index?

// Never use both (optional + throws) unless truly needed
// BAD:
func parse(_ data: Data) throws -> User?
// GOOD (pick one):
func parse(_ data: Data) throws -> User
func parse(_ data: Data) -> User?
```

### Default Arguments

Provide defaults for common cases:

```swift
// GOOD: most callers want default animation
func dismiss(animated: Bool = true)

// GOOD: sensible defaults reduce call-site noise
func fetch(page: Int = 1, perPage: Int = 20, sortBy: SortKey = .date) async throws -> [Item]
```

---

## Documentation Comments

### Format

```swift
/// Returns the element at the specified position.
///
/// The index must be a valid index of the collection that is not equal to
/// `endIndex`. Passing an invalid index triggers a runtime error.
///
/// - Parameter position: The position of the element to access.
/// - Returns: The element at the specified position.
/// - Throws: `CollectionError.outOfBounds` if position is invalid.
/// - Complexity: O(1)
func element(at position: Index) throws -> Element
```

### Summary Line

- First line is the summary. It is the most important line.
- Use a single sentence fragment (no period) or a full sentence (with period).
- Begin with a verb phrase: "Returns...", "Creates...", "Removes...".

```swift
/// Returns the distance between two points.
func distance(from a: Point, to b: Point) -> Double

/// A Boolean value indicating whether the collection is empty.
var isEmpty: Bool { get }

/// A view that displays a person's profile photo.
struct ProfilePhotoView: View { }
```

### When to Document

| Always Document | Skip Documentation |
|----------------|-------------------|
| Public API | Obvious overrides (`viewDidLoad`) |
| Protocol requirements | Single-line computed properties with obvious names |
| Complex algorithms | Private helpers called from one place |
| Non-obvious behavior | Conformances to standard protocols |
| Side effects | |

---

## Good vs Bad Naming

| Bad | Good | Why |
|-----|------|-----|
| `data.process()` | `data.compressed()` | Vague verb vs specific result |
| `list.add(item)` | `list.append(item)` | `add` is ambiguous (where?) |
| `manager.handle(event)` | `handler.dispatch(event)` | `manager`/`handle` are non-specific |
| `str.equals(other)` | `str == other` or `str.isEqual(to: other)` | Use operators for equality |
| `view.updateUI()` | `view.refresh()` | `UI` is noise in a view context |
| `fetchAllUsers()` | `users()` or `listUsers()` | `All` is usually implied |
| `UserModel` | `User` | Don't suffix domain types with `Model` |
| `IUserService` | `UserService` (protocol) | No `I` prefix (that is C#/Java convention) |
| `getUserName()` | `var name: String` | Use properties for O(1) attribute access |
| `setHidden(true)` | `isHidden = true` | Use property setters, not setter methods |
| `kMaxRetries` | `maxRetries` | No Hungarian/k-prefix (that is Obj-C convention) |
| `enumType.None` | `enumType.none` | Cases are lowerCamelCase |

---

## Abbreviations and Acronyms

- Spell out words unless the abbreviation is universally known
- Universally known: `URL`, `HTTP`, `ID`, `JSON`, `XML`, `HTML`, `API`, `UI`
- Case rules for acronyms: all-upper when standalone (`URL`), all-lower when part of a longer name start (`urlString`), all-upper when not at start (`baseURL`)

```swift
// GOOD
var userID: UUID
var urlString: String
var baseURL: URL
var htmlContent: String
func fetchJSON() async throws -> Data

// BAD
var uId: UUID        // Inconsistent casing
var URLString: String // Should be urlString at start
var userId: UUID     // ID should be all-caps
```

---

## Overloading

Overload on return type or generic constraints, not on subtle parameter differences:

```swift
// GOOD: overload by return type
func decode<T: Decodable>(_ type: T.Type, from data: Data) throws -> T

// GOOD: overload by constraint
func sorted() -> [Element] where Element: Comparable
func sorted(by areInIncreasingOrder: (Element, Element) -> Bool) -> [Element]

// BAD: overloads that differ only by label
func process(input: String) -> Result
func process(data: String) -> Result  // Confusing -- which to use?
```
