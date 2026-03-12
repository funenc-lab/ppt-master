# Stage 0-3 Playbook

This playbook covers the entry stages that must be completed before strategy work begins.

## Scope

- Stage 0: Mandatory preflight
- Stage 1: Source normalization
- Stage 2: Project creation
- Stage 3: Template strategy

## Stage 0: Mandatory Preflight

Do not skip this stage.

Confirm all of the following before touching project outputs:

- The role switching protocol is understood.
- The SVG and PowerPoint compatibility rules are understood.
- The source normalization rules for PDF, URL, and image-based inputs are understood.

Checkpoint marker:

```markdown
## Stage 0 Check Complete
- [x] AGENTS.md has been read
- [x] Core rules are understood
- [ ] Stage 1 will start next
```

## Stage 1: Normalize Source Content

Convert input into Markdown as soon as the source type is known.

| Source Type | Required Tool | Command |
|-------------|---------------|---------|
| PDF file | `pdf_to_md` | `python3 skills/slidemax_workflow/scripts/slidemax.py pdf_to_md <file>` |
| Standard web page | `web_to_md` | `python3 skills/slidemax_workflow/scripts/slidemax.py web_to_md <url>` |
| WeChat or protected site | `web_to_md_cjs` | `python3 skills/slidemax_workflow/scripts/slidemax.py web_to_md_cjs <url>` |
| Screenshot, scan, or image document | OCR skill | Read `.agent/skills/ocr_image_to_markdown/SKILL.md` and transcribe first |
| Markdown or plain text | None | Use directly |

Required behavior:

- Convert PDF or URL input before strategy work starts.
- Treat OCR as mandatory when native extraction cannot produce readable Markdown.
- Preserve a project-local copy of the normalized source when practical.

## Stage 2: Create the Project Folder

Create the project as soon as the source is ready for direct use.

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py project_manager init <project-name> --format <format>
```

Supported formats include `ppt169`, `ppt43`, `xhs`, `story`, and the formats defined in shared config.

Expected result:

- A project directory exists under `workspace/`.
- The project has a valid destination for `images/`, `notes/`, `svg_output/`, and export artifacts.

## Stage 3: Confirm Template Strategy

Resolve template usage before Strategist starts.

### Option A: Use an Existing Template

If the template exists inside the repository, copy files by type:

```bash
cp skills/slidemax_workflow/templates/layouts/<layout-name>/*.svg <project-path>/templates/
cp skills/slidemax_workflow/templates/layouts/<layout-name>/design_spec.md <project-path>/templates/
cp skills/slidemax_workflow/templates/layouts/<layout-name>/*.png <project-path>/images/ 2>/dev/null || true
cp skills/slidemax_workflow/templates/layouts/<layout-name>/*.jpg <project-path>/images/ 2>/dev/null || true
cp skills/slidemax_workflow/templates/layouts/<layout-name>/*.jpeg <project-path>/images/ 2>/dev/null || true
```

If the template is external to the repository, copy:

- SVG template files into `<project-path>/templates/`
- The template design brief into `<project-path>/templates/`
- Template image assets into `<project-path>/images/`

Expected project shape:

```text
<project-path>/
├── templates/
│   ├── design_spec.md
│   ├── 01_cover.svg
│   ├── 02_toc.svg
│   ├── 02_chapter.svg
│   ├── 03_content.svg
│   └── 04_ending.svg
└── images/
    ├── cover_bg.png
    └── ...
```

### Option B: No Template

Proceed with a free-design workflow.

## Exit Criteria

Do not enter Stage 4 until all of the following are true:

- Source content is readable and normalized when required.
- The project directory exists.
- Template usage has been explicitly resolved.
- The destination format is known.
