# Server Actions

> Implementation rules and patterns for Server Actions.
>
> **Source files**: action-handler.ts (50K), encryption.ts,
> is-serializable-props.ts

## Processing Pipeline

1. Parse — extract action ID and arguments from request
2. Validate — verify action ID, check encryption
3. Execute — run the action function
4. Revalidate — process any revalidation calls made during execution
5. Respond — serialize return value back to client

<!-- TODO: Populate from refs/next-server/app-render/action-handler.ts -->

## Serialization Rules

Actions accept and return only serializable values:
- Primitives, plain objects, arrays, Date, FormData
- NOT: functions, classes, Symbols, streams

## Action ID Encryption

Action IDs are encrypted to prevent enumeration attacks.

<!-- TODO: Populate from refs/next-server/app-render/encryption.ts -->

## Error Handling

Server Actions throw errors, they don't return error objects.
Use try/catch on the client or error boundaries.

## Progressive Enhancement

Forms with Server Actions work without JavaScript via standard
HTML form submission.

## Patterns

- Form actions with `useActionState`
- Optimistic updates with `useOptimistic`
- Inline "use server" for component-scoped actions
- File-level "use server" for action modules
