---
name: discover
description: "Discover and specify features from a project overview. Takes a JTBD from specs/project-overview.md and creates a detailed feature spec. Triggers on: discover features, create feature spec, spec out feature, feature discovery."
user-invocable: true
---

# Feature Discovery

Create detailed feature specifications from project JTBD topics.

---

## The Job

1. Read `specs/project-overview.md` for JTBD list
2. Identify the next JTBD needing a spec
3. Ask 2-3 clarifying questions about the feature
4. Generate a detailed feature spec at `specs/[topic].md`
5. Update project-overview.md to mark the JTBD as "spec created"

**Important:** Do NOT implement anything. Just create the specification.

---

## Feature Spec Structure

```markdown
# [Feature Name]

## Overview
[What this feature does and the problem it solves]

## User Stories

### US-001: [Title]
**Description:** As a [user], I want [feature] so that [benefit].

**Acceptance Criteria:**
- [ ] Specific verifiable criterion
- [ ] Another criterion
- [ ] Typecheck passes

## Functional Requirements
- FR-1: [Requirement]

## Non-Goals
- [What this feature will NOT include]

## Technical Considerations
- [Constraints, dependencies]

## Quality Gates
- [Commands that must pass]
```

---

## Story Sizing

Each story must be completable in ONE Ralph iteration:

**Right-sized:** Add a database column, add a UI component, update a server action
**Too big:** "Build the dashboard", "Add authentication", "Refactor the API"

**Rule of thumb:** If you can't describe it in 2-3 sentences, split it.

---

## Clarifying Questions

Before writing the spec, ask 2-3 essential questions:
- What are the key user interactions?
- What data needs to be stored/displayed?
- Any specific UI requirements or constraints?

Use lettered options for quick answers.
