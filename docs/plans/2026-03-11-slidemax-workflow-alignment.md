# SlideMax Workflow Alignment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Align the SlideMax workflow docs, role prompts, validation behavior, and prompt-pack contract so the repository exposes one canonical workflow instead of multiple drifting variants.

**Architecture:** Treat `skills/slidemax_workflow/AGENTS.md` as the single canonical workflow contract, then make the runtime enforce the same delivery gates the docs promise. Keep command bridges thin, push reusable checks into `slidemax/`, and reduce prompt/document duplication by defining one canonical `image_prompts.md` schema that all role and reference docs reuse.

**Tech Stack:** Python, unittest, Markdown workflow docs, thin CLI bridges under `skills/slidemax_workflow/commands/`

---

### Task 1: Define the canonical delivery validation contract

**Files:**
- Modify: `skills/slidemax_workflow/AGENTS.md`
- Modify: `skills/slidemax_workflow/commands/README.md`
- Modify: `skills/slidemax_workflow/commands/README_CN.md`
- Modify: `skills/slidemax_workflow/roles/AGENTS.md`
- Test: `tests/test_project_management.py`

**Step 1: Write the failing tests for missing delivery artifacts**

Add tests covering:
- `validate` should fail or at minimum return an error status when `svg_final/` is missing finalized SVG after Stage 7 is claimed complete.
- `validate` should fail when no `.pptx` exists in the project root after export is expected.
- `validate` should fail when notes are missing for one or more slides.

Suggested test names:
- `test_run_cli_validate_fails_when_finalized_svg_missing`
- `test_run_cli_validate_fails_when_exported_pptx_missing`
- `test_run_cli_validate_fails_when_slide_notes_are_incomplete`

**Step 2: Run the project-management test file and confirm failure**

Run:
```bash
python3 -m unittest tests.test_project_management -v
```

Expected:
- New validation tests fail because current `validate` only checks project structure and raw SVG.

**Step 3: Extend the shared validation model in `slidemax.project_management`**

Add canonical delivery checks for:
- finalized SVG presence under `svg_final/`
- exported PPTX presence in the project root
- note coverage for all SVG slides

Implementation direction:
- Keep `validate_project()` as the canonical delivery validator.
- Add helper functions similar to `_collect_notes_check()` for:
  - finalized SVG coverage
  - exported PPTX existence
- Promote missing delivery artifacts from warnings to errors inside `validate`.

**Step 4: Keep `doctor` as preflight and `validate` as delivery gate**

Ensure behavior separation:
- `doctor`: permissive readiness/preflight checks with warnings
- `validate`: strict delivery completion checks

Do not silently reuse permissive `doctor` semantics for release validation.

**Step 5: Update docs to match the enforced contract**

Update wording so every workflow-facing doc says:
- `project_manager.py validate` is the delivery gate
- it verifies finalized SVG, notes coverage, and exported PPTX
- `doctor` is the non-blocking preflight path

**Step 6: Run tests again**

Run:
```bash
python3 -m unittest tests.test_project_management -v
```

Expected:
- All project-management tests pass.

**Step 7: Commit**

```bash
git add tests/test_project_management.py skills/slidemax_workflow/AGENTS.md skills/slidemax_workflow/commands/README.md skills/slidemax_workflow/commands/README_CN.md skills/slidemax_workflow/roles/AGENTS.md skills/slidemax_workflow/slidemax/project_management.py skills/slidemax_workflow/slidemax/project_utils.py
git commit -m "fix(slidemax-workflow): align delivery validation with workflow contract"
```

### Task 2: Collapse `image_prompts.md` into one canonical schema

**Files:**
- Modify: `skills/slidemax_workflow/AGENTS.md`
- Modify: `skills/slidemax_workflow/roles/Image_Generator.md`
- Modify: `skills/slidemax_workflow/references/docs/image_prompt_guidance.md`
- Test: `tests/test_pptx_export.py`

**Step 1: Define the canonical prompt-pack fields**

Use one minimum schema for each asset entry:
- asset id / filename
- use
- source type: `local | ai | stock | placeholder`
- target local path
- aspect ratio / image size
- prompt
- negative prompt
- alt text
- acquisition notes

Stock and local assets may replace prompt text with acquisition metadata, but the schema should stay stable.

**Step 2: Rewrite the failing docs first**

Update all three docs so they describe the same structure:
- `AGENTS.md` Stage 5 output contract
- `roles/Image_Generator.md` section 2 and section 5 template
- `references/docs/image_prompt_guidance.md`

Important:
- Remove the conflicting simplified template from `Image_Generator.md`
- Keep one example that includes `source type`, `target path`, and `negative prompt`

**Step 3: Add or update an export-side regression test if prompt-pack assumptions leak into runtime**

If no runtime depends on prompt-pack shape today, add a documentation-only test note in the plan and skip code.

If runtime reads prompt-pack metadata later, add tests before implementation.

**Step 4: Verify prompt-pack terminology consistency**

Search for these strings and reconcile them:
- `Updated asset status`
- `image_prompts.md`
- `Negative Prompt`
- `Alt Text`
- `local`, `ai`, `stock`, `placeholder`

Run:
```bash
rg -n "image_prompts.md|Negative Prompt|Alt Text|source type|local|stock|placeholder|asset status" skills/slidemax_workflow
```

Expected:
- No contradictory field definitions remain.

**Step 5: Commit**

```bash
git add skills/slidemax_workflow/AGENTS.md skills/slidemax_workflow/roles/Image_Generator.md skills/slidemax_workflow/references/docs/image_prompt_guidance.md
git commit -m "docs(slidemax-workflow): unify image prompt pack schema"
```

### Task 3: Remove workflow drift from command and role docs

**Files:**
- Modify: `skills/slidemax_workflow/commands/README_CN.md`
- Modify: `skills/slidemax_workflow/roles/Strategist.md`
- Modify: `skills/slidemax_workflow/roles/Executor_General.md`
- Modify: `skills/slidemax_workflow/roles/Executor_Consultant.md`
- Modify: `skills/slidemax_workflow/roles/Executor_Consultant_Top.md`
- Modify: `skills/slidemax_workflow/AGENTS.md`

**Step 1: Remove the stale workflow section from `README_CN.md`**

Delete or rewrite the section that still says:
- `Strategist -> Executor -> Optimizer`
- validate is optional
- the design spec file is generated by `init`

Replace it with the canonical chain:
- Stage 4 Strategist
- Stage 5 Image_Generator when needed
- Stage 6 Executor
- Stage 7 `total_md_split.py -> finalize_svg.py -> svg_to_pptx.py -s final -> project_manager.py validate`

**Step 2: Fix Strategist responsibility boundaries**

Update `roles/Strategist.md` so it no longer says Strategist creates project folders.

Canonical rule:
- project folder creation belongs only to Stage 2 via `project_manager.py init`
- Strategist consumes an existing project path

**Step 3: Fix note-file compatibility wording**

Adjust Strategist and Executor docs so they say:
- `total_md_split` writes note files using SVG stems
- export reading also accepts legacy `slide01.md` naming

Do not claim the splitter emits `slide01.md`.

**Step 4: Fix design spec naming language**

Pick one recommended filename:
- preferably `design_specification.md` if that is the future-facing standard

Then update:
- workflow docs
- warning messages in validation helpers
- any examples that still prefer `设计规范与内容大纲.md`

Keep legacy names accepted for compatibility, but stop recommending multiple primary names.

**Step 5: Run targeted grep verification**

Run:
```bash
rg -n "Strategist → Executor → Optimizer|可选）验证项目|create content folders|slide01.md|设计规范与内容大纲.md|design_specification.md" skills/slidemax_workflow
```

Expected:
- only intended compatibility mentions remain
- no stale workflow sequence remains

**Step 6: Commit**

```bash
git add skills/slidemax_workflow/commands/README_CN.md skills/slidemax_workflow/roles/Strategist.md skills/slidemax_workflow/roles/Executor_General.md skills/slidemax_workflow/roles/Executor_Consultant.md skills/slidemax_workflow/roles/Executor_Consultant_Top.md skills/slidemax_workflow/AGENTS.md skills/slidemax_workflow/slidemax/project_utils.py
git commit -m "docs(slidemax-workflow): remove workflow and naming drift"
```

### Task 4: Add final regression coverage for delivery and note hydration

**Files:**
- Modify: `tests/test_project_management.py`
- Modify: `tests/test_pptx_export.py`
- Modify: `skills/slidemax_workflow/slidemax/exporters/pptx_assets.py`
- Modify: `skills/slidemax_workflow/slidemax/pptx_export.py`

**Step 1: Add regression tests for legacy note naming**

Add tests proving:
- export can still read legacy `slide01.md`
- splitter still emits SVG-stem filenames

Suggested test names:
- `test_find_notes_files_reads_legacy_slide_number_files`
- `test_total_md_split_writes_svg_stem_note_files`

**Step 2: Add regression tests for strict delivery validation**

Add tests proving:
- `validate` rejects projects missing `.pptx`
- `validate` rejects projects missing `svg_final` outputs for current slides

**Step 3: Run the focused test suite**

Run:
```bash
python3 -m unittest tests.test_project_management tests.test_pptx_export -v
```

Expected:
- All workflow-alignment regressions pass.

**Step 4: Commit**

```bash
git add tests/test_project_management.py tests/test_pptx_export.py skills/slidemax_workflow/slidemax/exporters/pptx_assets.py skills/slidemax_workflow/slidemax/pptx_export.py
git commit -m "test(slidemax-workflow): cover aligned delivery and note semantics"
```

### Task 5: Run repository-level verification for the workflow slice

**Files:**
- No new source files

**Step 1: Run unit tests for the touched workflow modules**

Run:
```bash
python3 -m unittest tests.test_project_management tests.test_pptx_export -v
```

Expected:
- PASS

**Step 2: Run grep-based consistency checks**

Run:
```bash
rg -n "Image_Generator|total_md_split.py|project_manager.py validate|design_specification.md|slide01.md|svg_final|pptx" skills/slidemax_workflow
```

Expected:
- wording is consistent with the intended compatibility story

**Step 3: Run one manual smoke check**

Create a temporary project and verify:
- `doctor` warns on incomplete delivery artifacts
- `validate` fails until notes, finalized SVG, and PPTX all exist

**Step 4: Final commit**

```bash
git status --short
git commit -m "chore(slidemax-workflow): complete workflow contract alignment"
```

## Extension Points

- If delivery validation becomes too strict for in-progress decks, add an explicit `project_manager.py verify-delivery` subcommand instead of weakening `validate`.
- If prompt-pack metadata will later drive automation, introduce a machine-readable sidecar such as `images/image_prompts.json` while keeping `image_prompts.md` human-readable.
- If doc drift remains a recurring problem, add snapshot-style tests that assert key workflow strings across canonical docs.

## Assumptions

- `AGENTS.md` remains the single authoritative workflow handbook.
- Backward compatibility for legacy spec names and legacy note filenames should remain supported during read-time, but no longer be recommended as the primary path.
- It is acceptable to tighten `validate` semantics even if that changes existing operator expectations, because the current docs already promise stricter behavior than the code delivers.
