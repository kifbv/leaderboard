---
name: interview
description: "Conduct a structured interview to define a greenfield project. Guides the user through vision, JTBD, scope, technical context, and success criteria. Produces specs/project-overview.md. Triggers on: interview, start a project, new project, define project, project discovery."
user-invocable: true
---

# Project Discovery Interview

Conduct a structured interview to help define a greenfield project from scratch.

---

## The Job

1. Interview the user about their project idea
2. Identify Jobs to Be Done (JTBD)
3. Define v1 scope and boundaries
4. Capture technical context and constraints
5. Write `specs/project-overview.md`

**Important:** Do NOT implement anything. Just create the specification.

---

## Interview Steps

### Step 1: Vision (2-3 questions)

Ask the user to describe their project idea, then explore:
- What problem does this solve? Who has this problem?
- Who is the target user?
- What is the core experience?

### Step 2: Jobs to Be Done (1-2 questions)

From the vision, propose 3-7 JTBD as a numbered list. Ask:
- Are these the right jobs? Missing any?
- Which are most important for v1?

### Step 3: Scope (2-3 questions per JTBD)

For each JTBD, define:
- Minimum viable version
- Explicitly out of scope for v1
- Non-negotiables vs nice-to-haves

Use lettered options:
```
1. For the "manage watchlist" job, what's v1 scope?
   A. Basic add/remove only
   B. Add/remove with rating and notes
   C. Full tracking with tags, categories, search
   D. Other: [please specify]
```

### Step 4: Technical Context (1-2 questions)

Ask about: platform, tech stack, existing constraints, quality requirements.

### Step 5: Success Criteria (1 question)

What does "done" look like for v1?

---

## Output

Create `specs/project-overview.md` with:
- Project name and problem statement
- Target users
- JTBD (numbered, each with "Status: needs spec")
- v1 scope (in/out, non-negotiables)
- Technical constraints
- Quality gates
- Success criteria

Then print a summary and suggest: "Run `./ralph/ralph.sh discover` to generate feature specs."

---

## Style

- 2-4 questions at a time
- Lettered options for quick answers
- Reflect back understanding after each answer
- Be opinionated when user is unsure
- "One sentence without 'and'" test for JTBD scoping
