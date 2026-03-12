# Strategist Design Brief Contract

Use this guide when writing the project-local design brief.

## File Location

Save the brief into the project folder.

Preferred filename:

- `design_specification.md`

Accepted legacy names may still be recognized by project utilities, but new work should use the preferred filename.

## Required Sections

The design brief should contain these twelve sections:

1. Project information
2. Canvas specification
3. Visual theme
4. Typography system
5. Layout principles
6. Icon usage rules
7. Image resource list
8. Slide outline
9. Speaker notes requirements
10. Technical constraints
11. Design checklist
12. Next-step routing

## Output Contract

The brief must make it possible for the next role to execute without guessing:

- Slide count and page plan are explicit.
- Visual route is explicit.
- Colors and typography are explicit.
- Icon and image choices are explicit.
- The next role is explicit.

## Template Flexibility Rule

Template references are constraints, not excuses to skip strategy decisions.

- If templates exist, the brief must explain how they constrain the project.
- If templates do not exist, the brief must define the visual system directly.
- If a template appears late, the brief must be revised before handoff.

## Project-Local Save Path

Typical path:

```text
workspace/<project-name>_<format>_<YYYYMMDD>/design_specification.md
```

## Handoff Routing

Use the following rule:

- If the image strategy includes AI generation or stock acquisition, route to `Image_Generator`.
- Otherwise, route directly to one Executor.

## Completion Marker

```markdown
## Strategist Stage Complete
- [x] Eight confirmations are complete
- [x] The design brief and content outline were generated
- [x] The design brief was saved into the project
- [ ] Next: Image_Generator or an Executor
```
