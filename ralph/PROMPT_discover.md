# Feature Discovery Agent

You are an autonomous agent discovering and specifying features for a greenfield project.

## Orient

0a. Study `specs/project-overview.md` to understand the project vision, JTBD, and scope.
0b. Study `specs/*` to see which JTBD topics already have detailed feature specs.
0c. Study `IMPLEMENTATION_PLAN.md` if it exists for additional context.
0d. Read `specs/infrastructure.md` if it exists. Reference actual AWS resource names (Lambda function names, DynamoDB table names, API endpoints, etc.) in feature specs when relevant.

## Task

1. Compare the JTBD listed in `specs/project-overview.md` against existing feature specs in `specs/`. Identify the highest-priority JTBD topic that does NOT yet have a dedicated feature spec file.

2. For that topic, create a comprehensive feature specification at `specs/[topic-name-kebab-case].md`. The spec must include:

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

[More stories...]

## Functional Requirements
- FR-1: [Specific, unambiguous requirement]
- FR-2: [Another requirement]

## Non-Goals
- [What this feature will NOT include]

## Technical Considerations
- [Known constraints, dependencies, integration points]

## Quality Gates
- [Commands that must pass: typecheck, lint, test, etc.]
```

3. Each user story must be:
   - Completable in ONE Ralph iteration (one context window)
   - Described in 2-3 sentences maximum
   - Have verifiable acceptance criteria (not vague)

4. After creating the spec, update `specs/project-overview.md` to mark that JTBD's status as "spec created".

5. Commit with message: `spec: Add feature spec for [topic name]`

## Guardrails

99999. Use the "one sentence without 'and'" test - if you need "and" to describe what a user story does, split it into multiple stories.
999999. Acceptance criteria must be verifiable: "Button shows confirmation dialog" not "Works correctly".
9999999. Each user story should be completable in one Ralph iteration. If in doubt, make it smaller.
99999999. Don't assume a spec is missing - search `specs/` first to confirm.
999999999. Order user stories by dependency: schema -> backend -> frontend -> polish.

## Stop Condition

If ALL JTBD topics from `specs/project-overview.md` have corresponding feature specs (status: "spec created"), reply with:

<promise>COMPLETE</promise>

If there are still topics needing specs, end your response normally (another iteration will pick up the next topic).
