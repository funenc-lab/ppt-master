# Workflow References

This directory stores workflow entry and redirect documents for the `slidemax-workflow` skill.

## How This Directory Fits

- [`../AGENTS.md`](../AGENTS.md) is the authoritative workflow and rules handbook.
- This `workflows/` directory stores workflow entry pages and redirects referenced by that handbook.
- Update `../AGENTS.md` first when stage order or gate rules change, then keep workflow entry pages aligned.

## Workflow Entries

- `generate-ppt.md` - redirect entry to `../AGENTS.md` for PPT workflow tasks
- `create-template.md` - template creation workflow entry
- `stages/README.md` - detailed stage playbooks grouped by workflow phase

## Maintenance Rules

- Treat `skills/slidemax_workflow/` as the only workflow source of truth.
- Read the relevant workflow entry before executing a workflow stage.
- Keep redirect pages thin; do not duplicate the authoritative stage logic from `../AGENTS.md`.
- Keep detailed stage execution rules in `stages/`.
- If a workflow rule affects role switching, stage gates, or command ordering, update `../AGENTS.md` in the same change and then reconcile the related entry pages.
