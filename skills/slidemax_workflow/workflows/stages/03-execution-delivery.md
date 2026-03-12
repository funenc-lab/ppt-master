# Stage 6-8 Playbook

This playbook covers slide production, delivery, and optional post-draft optimization.

## Scope

- Stage 6: Executor
- Stage 7: Delivery chain
- Stage 8: Optimizer_CRAP

## Stage 6: Executor

Required reads:

- `skills/slidemax_workflow/roles/Executor_General.md`
- `skills/slidemax_workflow/roles/Executor_Consultant.md`
- `skills/slidemax_workflow/roles/Executor_Consultant_Top.md`

Execution contract:

- Visual construction phase writes SVG slides into `<project-path>/svg_output/`.
- Logic construction phase writes the notes manuscript into `<project-path>/notes/total.md`.
- Speaker notes are mandatory.

Checkpoint marker:

```markdown
## Executor Stage Complete
### Visual Construction
- [x] The matching Executor role file was read
- [x] All SVG slides were generated into `svg_output/`
- [x] Basic quality checks passed

### Logic Construction
- [x] `notes/total.md` was generated

### Delivery Chain
- [ ] Run `total_md_split`
- [ ] Run `finalize_svg`
- [ ] Run `svg_to_pptx -s final`
- [ ] Run `project_manager validate`
```

## Stage 7: Delivery Chain

Run the delivery path in order:

```text
total_md_split -> finalize_svg -> svg_to_pptx -s final -> project_manager validate
```

### Step 1: Split Speaker Notes

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py total_md_split <project-path>
```

### Step 2: Finalize SVG

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py finalize_svg <project-path>
```

`finalize_svg` is the canonical post-processing entry and should replace ad-hoc file copying.

### Step 3: Export PPTX

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py svg_to_pptx <project-path> -s final
```

### Step 4: Validate Delivery

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py project_manager validate <project-path>
```

Validation expectations:

- `svg_final/` contains the finalized slide set.
- Notes cover every slide through per-slide files or a complete `notes/total.md`.
- An exported `.pptx` exists in the project root.

Minimum spot check:

- The cover slide
- The agenda or section slide
- One representative content slide

## Stage 8: Optimizer_CRAP

This stage is optional.

- Preferred timing: after the first complete SVG draft and before final delivery.
- If optimization happens after export, re-run the full Stage 7 delivery chain.
- Read `skills/slidemax_workflow/roles/Optimizer_CRAP.md` before starting.

## Completion Checklist

- [ ] Source content was normalized into Markdown when required
- [ ] The project folder was created
- [ ] Template strategy was confirmed
- [ ] The eight Strategist confirmations were completed
- [ ] The design brief was saved
- [ ] Image assets are ready when required
- [ ] SVG slides exist in `svg_output/`
- [ ] `notes/total.md` exists
- [ ] `total_md_split` was run and per-slide notes were generated
- [ ] `finalize_svg` was run
- [ ] `svg_final/` exists
- [ ] PPTX was exported
- [ ] `project_manager validate` passed
- [ ] A minimum spot check was completed
