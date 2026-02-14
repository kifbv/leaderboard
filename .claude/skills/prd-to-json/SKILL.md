---
name: prd-to-json
description: "Convert PRDs to prd.json format for Ralph loop execution. Creates JSON task files with user stories, acceptance criteria, and dependencies. Triggers on: convert prd, create prd.json, ralph json, convert to json, json from prd."
user-invocable: true
---

# PRD to JSON Converter

Convert existing PRDs (markdown) to the `prd.json` format that Ralph uses for autonomous execution.

---

## The Job

Take a PRD (markdown file or text) and convert it to `prd.json`.

---

## Output Format

```json
{
  "name": "[Project Name]",
  "branchName": "ralph/[feature-name-kebab-case]",
  "description": "[Feature description]",
  "userStories": [
    {
      "id": "US-001",
      "title": "[Story title]",
      "description": "As a [user], I want [feature] so that [benefit]",
      "acceptanceCriteria": [
        "Criterion 1",
        "Criterion 2",
        "Typecheck passes"
      ],
      "category": "[feature-area]",
      "priority": 1,
      "passes": false,
      "dependsOn": [],
      "notes": ""
    }
  ]
}
```

---

## Story Sizing

**Each story must be completable in ONE Ralph iteration (one context window).**

**Right-sized:**
- Add a database column and migration
- Add a UI component to an existing page
- Update a server action with new logic
- Add a filter dropdown to a list

**Too big (split these):**
- "Build the entire dashboard" -> schema, queries, UI components, filters
- "Add authentication" -> schema, middleware, login UI, session handling

**Rule of thumb:** If you cannot describe the change in 2-3 sentences, it is too big.

---

## Story Ordering

Stories execute in priority order. Earlier stories must not depend on later ones.

1. Project setup / configuration
2. Schema / database changes
3. Server actions / backend logic
4. UI components that use the backend
5. Dashboard / summary views
6. Polish / edge cases

Use the `dependsOn` field to express dependencies between stories:
```json
{
  "id": "US-003",
  "dependsOn": ["US-001", "US-002"]
}
```

---

## Acceptance Criteria Rules

Must be verifiable:

**Good:** "Add status column with default 'pending'", "Filter dropdown has All | Active | Completed options"
**Bad:** "Works correctly", "Good UX", "Handles edge cases"

Always include as final criterion: `"Typecheck passes"`
For testable logic, add: `"Tests pass"`
For UI stories, add: `"Verify in browser"`

---

## Conversion Rules

1. Each user story from the PRD becomes one JSON entry
2. IDs: Sequential (US-001, US-002, etc.)
3. Priority: Based on dependency order, then document order
4. All stories: `passes: false` and empty `notes`
5. branchName: Derive from feature name, kebab-case, prefixed with `ralph/`
6. Always add "Typecheck passes" to every story's acceptance criteria
7. Use `category` field to group related stories logically

---

## Archive Check

Before writing a new prd.json, check if one exists with a different `branchName`. If so:
1. Create `archive/YYYY-MM-DD-feature-name/`
2. Copy current `prd.json` and `progress.txt` to archive
3. Reset `progress.txt` with fresh header

---

## Checklist

Before saving prd.json:
- [ ] Previous run archived (if prd.json exists with different branchName)
- [ ] Each story completable in one iteration
- [ ] Stories ordered by dependency
- [ ] Every story has "Typecheck passes"
- [ ] UI stories have "Verify in browser"
- [ ] Acceptance criteria are verifiable
- [ ] No story depends on a later story
- [ ] `dependsOn` fields correctly reference prerequisite story IDs
