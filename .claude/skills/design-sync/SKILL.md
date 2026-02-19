---
name: design-sync
description: "Import UI designs from Stitch into project specs. Connects to a Stitch design project, maps screens to JTBD, generates feature specs with design references, synthesizes a design system (DESIGN.md), fills design gaps with Stitch-optimized prompts, and saves HTML locally for the build loop. Triggers on: import designs, sync designs, design to spec, stitch import, mockup to spec, design sync."
user-invocable: true
---

# Design Sync

Import UI mockups from a Stitch design project into the specs and designs that drive the Ralph loop.

---

## The Job

1. Connect to a Stitch project and inventory its screens
2. Map screens to JTBD from `specs/project-overview.md`
3. Generate feature specs with design references
4. Save screen HTML locally to `designs/`
5. Synthesize a design system into `designs/DESIGN.md`
6. Identify uncovered JTBD and generate Stitch-optimized prompts for missing screens
7. Offer to generate missing screens in Stitch and import them
8. Update project-overview.md to mark JTBD coverage status

**Important:** Do NOT implement anything. Just create specs, design references, and design system documentation.

---

## Steps

### Step 1: Connect to Stitch

1. Call `mcp__stitch__list_projects` to show available design projects.
2. Present the list and ask the user to select one (or accept the default if only one exists).
3. Call `mcp__stitch__list_screens` for the selected project.
4. Call `mcp__stitch__get_project` to retrieve project-level design settings (color mode, fonts, roundness, custom colors). Hold this data for Step 6.

### Step 2: Screen Inventory

5. For each **visible** screen (skip hidden ones), call `mcp__stitch__get_screen` to get full details.
6. Present a summary table:

```
Screen                  | Device   | Size
----------------------- | -------- | ----------
Global Leaderboard      | Mobile   | 390x967
Player Statistics       | Mobile   | 390x908
Log Match Result        | Mobile   | 390x884
```

7. Ask the user to confirm which screens to import. All visible screens are selected by default.

### Step 3: Map Screens to JTBD

8. Read `specs/project-overview.md` if it exists.
9. Propose a mapping of screens to JTBD topics. Group related screens under the same topic.
   - If project-overview exists: map screens to existing JTBD.
   - If no project-overview: infer JTBD from the screen set and propose them.
10. Ask the user to confirm or adjust the mapping.

### Step 4: Generate Feature Specs

11. For each JTBD group, create `specs/[topic-name-kebab-case].md` with this structure:

```markdown
# [Feature Name]

## Overview
[Derived from screen analysis - what this feature does and the problem it solves]

## Design Reference
- **Stitch Project:** [project name] (`projects/[project-id]`)
- **Screens:**
  - [Screen Title] (`[screen-id]`, [device], [width]x[height])
- **Local HTML:** `designs/[screen-name].html`
- **Design System:** `designs/DESIGN.md` (colors, typography, spacing, component patterns)

## User Stories

### US-001: [Title]
**Description:** As a [user], I want [feature visible in mockup] so that [benefit].

**Acceptance Criteria:**
- [ ] [Specific criterion derived from mockup UI elements]
- [ ] UI matches design reference in `designs/[screen-name].html`
- [ ] Typecheck passes
- [ ] Verify in browser

## Functional Requirements
- FR-1: [Derived from visible UI elements and interactions]

## Non-Goals
- [What this feature will NOT include, inferred from what the mockup omits]

## Technical Considerations
- Design HTML in `designs/` is a layout/styling reference, not production code
- Adapt to the project's tech stack and component patterns

## Quality Gates
- Typecheck passes
- Verify in browser against design reference
```

**Story sizing:** Each user story must be completable in ONE Ralph iteration. If a screen is complex, split it into multiple stories (e.g., layout/structure, data display, interactions, polish).

### Step 5: Save Design HTML

12. Download the HTML code from each imported Stitch screen.
13. Save to `designs/[screen-title-kebab-case].html`.
14. These files serve as layout and styling references for the Build agent. They are NOT production code to copy verbatim.

### Step 6: Generate DESIGN.md

15. Parse each downloaded HTML file in `designs/` for:
    - Tailwind utility classes (colors, spacing, typography, borders, shadows)
    - CSS custom properties and variables
    - Recurring component patterns (cards, buttons, navs, forms, modals)

16. Use the project metadata from Step 1 (color mode, fonts, roundness, custom colors) to fill in project-level design tokens.

17. Analyze the designs using this methodology:

    **a. Define the Atmosphere:** Evaluate the screenshots and HTML structure to capture the overall "vibe." Use evocative adjectives to describe the mood (e.g., "Airy," "Dense," "Minimalist," "Utilitarian," "Gallery-like," "Sophisticated"). Describe the density, aesthetic philosophy, and emotional impression — don't just list tokens.

    **b. Map the Color Palette:** For each color found, provide all three elements:
    - A **descriptive natural-language name** that conveys its character (e.g., "Deep Muted Teal-Navy")
    - The **hex code** in parentheses for precision (e.g., `#294056`)
    - Its **functional role** (e.g., "Used for primary actions and CTAs")

    **c. Translate Geometry to Language:** Convert technical border-radius values into physical descriptions:

    | Tailwind Class | Natural Language |
    |----------------|------------------|
    | `rounded-none` | Sharp, squared-off edges |
    | `rounded-sm` | Slightly softened corners |
    | `rounded-md` | Gently rounded corners |
    | `rounded-lg` | Generously rounded corners |
    | `rounded-xl` | Very rounded, pillow-like |
    | `rounded-full` | Pill-shaped, circular |

    **d. Describe Depth & Elevation:** Explain how the UI handles layers. Describe the presence and quality of shadows:
    - "Flat" — no shadows, relies on color contrast for separation
    - "Whisper-soft diffused shadows" — subtle, barely-there elevation
    - "Heavy, high-contrast drop shadows" — bold depth and layering

    **e. Reference:** Consult the Stitch Effective Prompting Guide for language patterns: https://stitch.withgoogle.com/docs/learn/prompting/

18. Synthesize findings into `designs/DESIGN.md` with these sections:

    ```markdown
    # Design System: [Project Title]
    **Project ID:** [project-id]

    ## 1. Visual Theme & Atmosphere
    (Evocative description of the mood, density, and aesthetic philosophy.
    E.g., "Airy Scandinavian minimal with warm cream tones and generous
    whitespace. The overall mood is spacious and tranquil, prioritizing
    breathing room and visual clarity.")

    ## 2. Color Palette & Roles
    (Each color as: Descriptive Name (#hexcode) — functional role.
    E.g., "Deep Muted Teal-Navy (#294056) — primary actions and CTAs."
    Group by: Foundation, Accent/Interactive, Typography, Functional States.)

    ## 3. Typography Rules
    (Font families, weight usage for headings vs body, letter-spacing
    character. E.g., "Manrope for all text. Semi-bold 600 for headings,
    Regular 400 for body. Slightly expanded letter-spacing on headers
    for refined elegance.")

    ## 4. Component Patterns
    * **Buttons:** (Shape description, color assignment, hover behavior.
      E.g., "Subtly rounded corners, Deep Teal-Navy fill, white text,
      subtle hover darkening.")
    * **Cards:** (Corner roundness description, background color, shadow
      depth. E.g., "Gently rounded corners, white surface, whisper-soft
      diffused shadow on hover.")
    * **Inputs:** (Stroke style, background, focus state.)
    * **Navigation:** (Layout, typography weight, active state styling.)

    ## 5. Layout Principles
    (Whitespace strategy, spacing scale, grid patterns, responsive
    breakpoints observed. E.g., "Generous breathing room between sections.
    8px base unit. 4-column grid on desktop, single column on mobile.")
    ```

    **Best practices for DESIGN.md writing:**
    - **Be Descriptive:** Avoid generic terms like "blue" or "rounded." Use "Ocean-deep Cerulean (#0077B6)" or "Gently curved edges"
    - **Be Functional:** Always explain what each design element is used for
    - **Be Consistent:** Use the same terminology throughout the document
    - **Be Visual:** Help readers visualize the design through your descriptions
    - **Be Precise:** Include exact values (hex codes, pixel values) in parentheses after natural language descriptions

    **Common pitfalls to avoid:**
    - Using technical jargon without translation (e.g., "rounded-xl" instead of "generously rounded corners")
    - Omitting hex codes or using only descriptive names without values
    - Forgetting to explain functional roles of design elements
    - Being too vague in atmosphere descriptions
    - Ignoring subtle design details like shadows or spacing patterns

19. Present a summary of the extracted design system to the user:
    - Number of unique colors found
    - Font families detected
    - Number of component patterns identified
    - Overall vibe in one sentence

20. Ask: "Does this design system look right? Any adjustments before I save it?"

21. Save to `designs/DESIGN.md`.

### Step 7: Fill Gaps

22. Compare the JTBD list from `specs/project-overview.md` against the screens imported in Steps 1-5. Identify JTBD with no matching Stitch screen.

23. If no gaps exist, tell the user "All JTBD have design coverage" and skip to Step 8.

24. Present a table of uncovered JTBD:

    ```
    Uncovered JTBD              | Reason
    --------------------------- | ------
    User authentication         | No matching screen in Stitch
    Settings & preferences      | No matching screen in Stitch
    ```

25. For each uncovered JTBD, generate a Stitch-optimized prompt using this pipeline:

    **a. Assess what's needed:** Evaluate the JTBD description from `specs/project-overview.md` against this checklist:

    | Element | Check for | If missing... |
    |---------|-----------|---------------|
    | **Platform** | "web", "mobile", "desktop" | Infer from existing screens' device types |
    | **Page type** | "landing page", "dashboard", "form" | Infer from JTBD description |
    | **Structure** | Numbered sections/components | Create logical page structure |
    | **Visual style** | Adjectives, mood, vibe | Pull from `designs/DESIGN.md` atmosphere |
    | **Colors** | Specific values or roles | Pull from `designs/DESIGN.md` palette |
    | **Components** | UI-specific terms | Translate to proper keywords (see below) |

    **b. Enhance with UI/UX keywords:** Replace vague terms with specific component names:

    | Vague | Enhanced |
    |-------|----------|
    | "menu at the top" | "navigation bar with logo and menu items" |
    | "button" | "primary call-to-action button" |
    | "list of items" | "card grid layout" or "vertical list with thumbnails" |
    | "form" | "form with labeled input fields and submit button" |
    | "picture area" | "hero section with full-width image" |

    **c. Amplify the vibe:** Translate generic adjectives into descriptive language:

    | Basic | Enhanced |
    |-------|----------|
    | "modern" | "clean, minimal, with generous whitespace" |
    | "professional" | "sophisticated, trustworthy, with subtle shadows" |
    | "fun" | "vibrant, playful, with rounded corners and bold colors" |
    | "dark mode" | "dark theme with high-contrast accents on deep backgrounds" |

    **d. Structure the page:** Organize content into numbered sections:

    ```markdown
    **Page Structure:**
    1. **Header:** Navigation with logo and menu items
    2. **Hero Section:** Headline, subtext, and primary CTA
    3. **Content Area:** [Describe the main content for this JTBD]
    4. **Footer:** Links, social icons, copyright
    ```

    **e. Format colors properly:** When referencing colors from `designs/DESIGN.md`, always use:
    ```
    Descriptive Name (#hexcode) for functional role
    ```
    E.g., "Deep Ocean Blue (#1a365d) for primary buttons and links"

    **f. Assemble the prompt** using this template:

    ```markdown
    [One-line description of the page purpose and vibe]

    **DESIGN SYSTEM (REQUIRED):**
    - Platform: [Web/Mobile], [Desktop/Mobile]-first
    - Theme: [Light/Dark], [style descriptors from DESIGN.md atmosphere]
    - Background: [Color description] (#hex)
    - Primary Accent: [Color description] (#hex) for [role]
    - Text Primary: [Color description] (#hex)
    - Typography: [Font family], [weight usage]
    - Buttons: [Shape description], [color]
    - Cards: [Corner style], [shadow description]
    - [Additional design tokens from DESIGN.md...]

    **Page Structure:**
    1. **[Section]:** [Description with specific UI component keywords]
    2. **[Section]:** [Description with specific UI component keywords]
    ...
    ```

    **g. Save** to `designs/prompts/[jtbd-name-kebab-case].md`.

    **Reference:** Consult the Stitch Effective Prompting Guide for latest best practices: https://stitch.withgoogle.com/docs/learn/prompting/

26. Present the generated prompts to the user for review.

27. Ask: "Would you like me to generate these screens in Stitch now?"
    - **a) Yes, all** — generate screens for all uncovered JTBD
    - **b) Pick which ones** — let the user select specific JTBD to generate
    - **c) No, skip** — leave prompts saved in `designs/prompts/` for manual use later

28. If the user chooses (a) or (b):
    a. Infer the device type from existing imported screens. If all are the same type, use that. If mixed, ask the user.
    b. For each selected JTBD, call `mcp__stitch__generate_screen_from_text` with the prompt content and inferred device type. Note: this can take ~1 minute per screen.
    c. For each newly generated screen:
       - Call `mcp__stitch__get_screen` for metadata
       - Download HTML to `designs/[screen-title-kebab-case].html`
       - Generate a feature spec in `specs/[topic-name-kebab-case].md` using the same template as Step 4
    d. Present the newly imported screens alongside the originals in the summary table.

### Step 8: Update Project Overview

29. If `specs/project-overview.md` exists, update each JTBD's status based on how it was handled:
    - **"Status: spec created (from design)"** — JTBD had matching Stitch screens imported in Steps 1-5
    - **"Status: spec created (from generated design)"** — screen was generated in Step 7 and imported
    - **"Status: prompt saved (no spec)"** — prompt saved to `designs/prompts/`, user declined generation; Discover phase will create a text-only spec

30. The Discover phase will skip JTBD marked "spec created" and handle the rest.

### Step 9: Review

31. Present a summary of everything created:

    ```
    Created:
      specs/            N feature specs (N from design, N from generated design)
      designs/          N HTML files
      designs/DESIGN.md
      designs/prompts/  N gap prompts

    Updated:
      specs/project-overview.md   N/N JTBD covered
    ```

32. Ask the user if any specs need adjustment.
33. Commit all files with message: `spec: Add design-synced specs from Stitch`

---

## Output

| Artifact | Location | Purpose |
|----------|----------|---------|
| Feature specs | `specs/[topic].md` | Same format as Discover output, drives Plan and Build |
| Design HTML | `designs/[screen].html` | Layout/styling reference for Build agent |
| Design system | `designs/DESIGN.md` | Design tokens (colors, typography, spacing, components) for consistent UI |
| Gap prompts | `designs/prompts/[jtbd].md` | Stitch-optimized prompts for screens that don't exist yet |
| Updated overview | `specs/project-overview.md` | Marks JTBD as covered so Discover skips them |

---

## After Design Sync

Suggest next steps based on project state:

- If JTBD remain without specs: "Run `./ralph/ralph.sh discover` to spec remaining features."
- If all JTBD have specs: "Run `./ralph/ralph.sh plan` to create the implementation plan."
- To convert designs to React components: "Run `/react-components` on individual screens."

---

## Style

- Let the user confirm screen selection and JTBD mapping before generating specs
- Use lettered options for quick answers
- Be opinionated about screen-to-JTBD grouping
- Flag screens that seem to span multiple features and ask how to handle them
