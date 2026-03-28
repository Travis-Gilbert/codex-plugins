---
description: Create a Product Requirements Document from discussion
allowed-tools: Read, Write
---

# Create PRD

Generate a structured Product Requirements Document through guided discussion with the user.

## Step 1: Gather Information

Ask the user the following questions. Batch them into 2-3 groups to avoid overwhelming.

**Batch 1: The Problem**

1. **What problem are you solving?** Describe the pain point or unmet need in 2-3 sentences.
2. **Who are the users?** List the primary and secondary user personas. Include their goals and frustrations.
3. **What exists today?** How do users currently handle this? What is the workaround or competing solution?

**Batch 2: The Solution**

4. **What are the goals?** What should the feature achieve? Be specific and measurable.
5. **What are the non-goals?** What is explicitly out of scope for this iteration?
6. **What are the constraints?** Technical limitations, timeline, platform requirements, dependencies.

**Batch 3: Success Criteria**

7. **How will you measure success?** Specific metrics or outcomes.
8. **What are the key user stories?** The 3-5 most important things a user should be able to do.

## Step 2: Generate the PRD

Write a structured document with the following sections:

```markdown
# PRD: <Feature Name>

## Problem Statement

<2-3 sentences describing the problem.>

## Users

### Primary: <Persona Name>
- **Role:** <who they are>
- **Goal:** <what they want to achieve>
- **Frustration:** <current pain point>

### Secondary: <Persona Name> (if applicable)
- ...

## Goals

1. <Measurable goal>
2. <Measurable goal>
3. <Measurable goal>

## Non-Goals

- <Explicitly out of scope>
- <Explicitly out of scope>

## Constraints

- **Platform:** <iOS version, device support>
- **Technical:** <dependencies, API limitations>
- **Timeline:** <if specified>

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| <metric> | <target> | <measurement method> |

## User Stories

### US-1: <Title>
**As a** <persona>, **I want to** <action>, **so that** <benefit>.

**Acceptance Criteria:**
- Given <precondition>, when <action>, then <result>
- Given <precondition>, when <action>, then <result>

### US-2: <Title>
...

## Open Questions

- <Any unresolved decisions>
- <Areas needing further research>
```

## Step 3: Save the PRD

Derive the feature name from the discussion (kebab-case, lowercase).

Save to: `docs/prd-<feature-name>.md`

```bash
mkdir -p docs
```

If a `docs/` directory does not exist, create it.

## Step 4: Present Summary

Tell the user:
- Where the file was saved
- A one-line summary of the feature
- The number of user stories defined
- Any open questions that need resolution before moving to spec
- Suggest running `/generate-spec docs/prd-<feature-name>.md` as the next step
