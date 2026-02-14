---
name: prd
description: "Generate a Product Requirements Document (PRD) for a feature. Use when planning a feature or when asked to create a PRD. Triggers on: create a prd, write prd for, plan this feature, requirements for, spec out."
user-invocable: true
---

# PRD Generator

Create detailed Product Requirements Documents that are clear, actionable, and suitable for Ralph loop implementation.

---

## The Job

1. Receive a feature description from the user
2. Ask 3-5 essential clarifying questions (with lettered options)
3. Generate a structured PRD based on answers
4. Save to `specs/prd-[feature-name].md`

**Important:** Do NOT start implementing. Just create the PRD.

---

## Step 1: Clarifying Questions

Ask only critical questions where the initial prompt is ambiguous. Focus on:

- **Problem/Goal:** What problem does this solve?
- **Core Functionality:** What are the key actions?
- **Scope/Boundaries:** What should it NOT do?
- **Success Criteria:** How do we know it's done?

Format questions with lettered options for quick answers:

```
1. What is the primary goal?
   A. Improve user onboarding
   B. Increase retention
   C. Reduce support burden
   D. Other: [please specify]
```

Users can respond with "1A, 2C, 3B" for quick iteration.

---

## Step 2: PRD Structure

### 1. Introduction/Overview
Brief description of the feature and the problem it solves.

### 2. Goals
Specific, measurable objectives (bullet list).

### 3. User Stories
Each story needs:
- **Title:** Short descriptive name
- **Description:** "As a [user], I want [feature] so that [benefit]"
- **Acceptance Criteria:** Verifiable checklist

Format:
```markdown
### US-001: [Title]
**Description:** As a [user], I want [feature] so that [benefit].

**Acceptance Criteria:**
- [ ] Specific verifiable criterion
- [ ] Another criterion
- [ ] Typecheck passes
- [ ] **[UI stories]** Verify in browser
```

**Important:**
- Acceptance criteria must be verifiable. "Works correctly" is bad. "Button shows confirmation dialog before deleting" is good.
- Each story must be completable in one Ralph iteration (one context window).

### 4. Functional Requirements
Numbered list: "FR-1: The system must..."

### 5. Non-Goals (Out of Scope)
What this feature will NOT include.

### 6. Technical Considerations (Optional)
Constraints, dependencies, integration points.

### 7. Success Metrics
How will success be measured?

### 8. Open Questions
Remaining areas needing clarification.

---

## Output

- **Format:** Markdown
- **Location:** `specs/`
- **Filename:** `prd-[feature-name].md` (kebab-case)

---

## Checklist

Before saving:
- [ ] Asked clarifying questions with lettered options
- [ ] User stories are small (one Ralph iteration each)
- [ ] Acceptance criteria are verifiable
- [ ] Functional requirements are numbered and unambiguous
- [ ] Non-goals define clear boundaries
