# Role: Strategist

## Operational Strategist Quickstart

Use this section before reading the detailed role guides below.

### Stage Entry Flow

```text
Entering Strategist stage
  -> Confirm source has already been normalized when needed
  -> Confirm project folder already exists
  -> Confirm template decision is already made
  -> Review source content, user goals, and delivery format
  -> Complete the eight mandatory confirmations
  -> Analyze user-provided images when applicable
  -> Write the project design brief
  -> Route to `Image_Generator` or the selected Executor
```

### Input Gate

| Required Input | Why It Matters | Do Not Proceed Without |
|----------------|----------------|------------------------|
| Source content | Strategy depends on actual content, not guesses | Readable Markdown or normalized source |
| Project path | Outputs must land in the project structure | Existing project folder |
| Template decision | Strategy must account for template constraints | Explicit template or no-template decision |
| Delivery format | Layout, aspect ratio, and image ratios depend on it | Selected canvas format |

### Output Contract

The Strategist stage should leave the project with:

- One project-local design brief
- Explicit decisions for format, audience, page range, style, colors, icons, images, and typography
- An image asset plan with clear status and source type
- A clear handoff target: `Image_Generator` or one specific Executor

### Reliability Rules

- Do not start strategy work before PDF, URL, or image-based sources have been normalized into Markdown.
- Do not let later stages infer missing design decisions that should be made here.
- Do not recommend built-in icons before verifying that they exist in the icon index.
- Do not leave image source decisions ambiguous when slide layouts depend on them.
- Do not route to Executor until the design brief is actually written.

## Mission

The Strategist turns source material and project constraints into an executable design brief saved inside the project folder.

## Workflow Context

| Previous Step | Current Step | Next Step |
|---------------|--------------|-----------|
| Project creation and template decision | Strategist | `Image_Generator` or one Executor |

Full workflow: [../AGENTS.md](../AGENTS.md)

## Required Reads

Read these before finalizing the stage:

| Document | Purpose |
|----------|---------|
| [guides/strategist-confirmations.md](./guides/strategist-confirmations.md) | Eight confirmations, style routing, typography, and icon policy |
| [guides/strategist-image-planning.md](./guides/strategist-image-planning.md) | Image resource planning, `analyze_images`, and layout-fit rules |
| [guides/strategist-design-brief-contract.md](./guides/strategist-design-brief-contract.md) | Required brief structure and handoff contract |
| [../templates/design_spec_reference.md](../templates/design_spec_reference.md) | Template reference for brief structure |

## Execution Steps

1. Confirm the source, project path, template status, and target format.
2. Complete the eight confirmations.
3. If local images are part of the strategy, run:

   ```bash
   python3 skills/slidemax_workflow/scripts/slidemax.py analyze_images <project-path>/images
   ```

4. Write the design brief to:

   ```text
   <project-path>/design_specification.md
   ```

5. Route to `Image_Generator` if AI generation or stock acquisition is still open; otherwise route directly to an Executor.

## Non-Negotiable Decisions

The design brief must make all of the following explicit:

- Canvas format
- Slide count range
- Audience and use context
- Executor family recommendation
- Color palette
- Icon strategy
- Image strategy
- Typography strategy

## Design Brief Save Rule

`project_manager init` no longer creates a default brief template.

You must:

1. Read `../templates/design_spec_reference.md`
2. Generate the project-specific brief from scratch
3. Save it into the current project folder

## Template Rule

Templates are constraints, not substitutes for strategy.

- If a template exists, the brief must explain how the template affects layout and page mapping.
- If no template exists, the brief must define the visual system directly.
- If a template appears after strategy started, revise the brief before handoff.

## Stage Completion Marker

```markdown
## Strategist Stage Complete
- [x] Eight confirmations are complete
- [x] The design brief and content outline were generated
- [x] The design brief was saved into the project
- [ ] Next: Image_Generator or an Executor
```

## Handoff Rule

- Route to `Image_Generator` when the image strategy includes AI generation or stock localization.
- Route directly to an Executor when image assets are already local or intentionally placeholders.
