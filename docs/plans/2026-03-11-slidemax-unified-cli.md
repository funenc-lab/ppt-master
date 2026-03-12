# SlideMax Unified CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Introduce a single SlideMax command tool that dispatches the full workflow command surface through one stable entrypoint and removes Python command files from `commands/`.

**Architecture:** Add a shared CLI registry under `skills/slidemax_workflow/slidemax/cli.py` and expose it through `skills/slidemax_workflow/scripts/slidemax.py`. Move the canonical Python command surface into `scripts/`, keep reusable logic in `slidemax/`, and leave `commands/` for documentation plus non-Python fallback resources only.

**Tech Stack:** Python 3, `argparse`, `importlib`, `subprocess`, `unittest`

---

### Task 1: Add failing tests for the unified CLI

**Files:**
- Create: `tests/test_slidemax_cli.py`

**Step 1: Write the failing test**

Add tests for:
- default help output when no command is provided
- alias resolution for a registered command
- `help <command>` dispatch
- unknown command handling

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_slidemax_cli.py -q`
Expected: FAIL because `slidemax.cli` does not exist yet.

### Task 2: Implement the shared registry-driven CLI

**Files:**
- Create: `skills/slidemax_workflow/slidemax/cli.py`
- Create: `skills/slidemax_workflow/scripts/slidemax.py`

**Step 1: Add a registry-backed dispatcher**

Implement:
- a `CommandSpec` model with name, summary, category, aliases, and runner
- registry construction for canonical Python command bridges
- a special handler for the Node-based `web_to_md_cjs`
- `run_cli(argv, registry, output_fn)` for testable dispatch

**Step 2: Remove duplicated Python entrypoints**

Delete `commands/*.py` after the registry covers the full command surface and the documentation has been updated.

### Task 3: Update command documentation

**Files:**
- Modify: `skills/slidemax_workflow/commands/README.md`
- Modify: `skills/slidemax_workflow/commands/README_CN.md`

**Step 1: Document the new canonical entrypoint**

Add:
- `python3 skills/slidemax_workflow/scripts/slidemax.py list`
- `python3 skills/slidemax_workflow/scripts/slidemax.py <command> ...`
- note that `commands/` no longer stores Python entrypoints

### Task 4: Verify the change

**Files:**
- Test: `tests/test_slidemax_cli.py`
- Test: `tests/test_command_bridge.py`
- Test: `tests/test_skill_metadata.py`

**Step 1: Run targeted tests**

Run:
- `pytest tests/test_slidemax_cli.py tests/test_command_bridge.py tests/test_skill_metadata.py -q`

**Step 2: Review output**

Confirm:
- all new CLI tests pass
- shared bridge behavior remains green
- `commands/` contains no `.py` files
