# Image Prompt Guidance

This guide helps operators and agents turn a Strategist design brief into a project-ready `images/image_prompts.md` file before any live image acquisition starts.

## Document Boundary

Use this file for prompt-pack structure and asset classification only.

- Local setup and doctor checks belong in `./image_generation_setup.md`
- Provider and model reference belongs in `./image_generation_providers.md`
- Stock provenance rules belong in `./image_stock_sources.md`
- Copy-paste AI assistant prompts belong in `./ai_setup_prompts.md`

Do not duplicate credential setup or full provider matrices here.

## When to Use

Use this guide when:

- Stage 5 (`Image_Generator`) has started
- the design brief already contains an image asset list
- you need to decide whether each asset should be local, AI-generated, stock, or placeholder
- you want a compact prompt-authoring checklist instead of reading the full role document first

## Required Inputs

Prepare the following before drafting prompts:

- project path, including the target `images/` directory
- the latest design brief from Strategist
- the image asset list with filenames and intended slide usage
- the canvas format and preferred aspect ratio
- the visual style, palette, and typography context
- any explicit restrictions such as "must use stock", "must keep the user's photo", or "placeholder only"

## Output Contract

The prompt file should be saved to:

```text
<project-path>/images/image_prompts.md
```

The file should leave no ambiguity for the next operator or agent. At minimum it should contain:

- a short project header
- an asset overview table
- one section per asset
- the selected source type for each asset
- the target local path for the delivered image
- the aspect ratio or image size required for the asset
- a prompt or acquisition brief for the selected source type
- a negative prompt when the asset is AI-generated
- alt text for downstream handoff and accessibility
- acquisition notes that match the selected source type

## Recommended Authoring Workflow

1. Read the image asset list from the design brief.
2. Classify every asset as `local`, `ai`, `stock`, or `placeholder`.
3. Map the canvas format to a supported aspect ratio and image size.
4. Draft `images/image_prompts.md` before any live generation or download.
5. If a live provider will be used, run a smoke test before batch generation.
6. Acquire assets serially and confirm that each required file lands on a project-local path.
7. Record provenance for stock or user-provided assets when the workflow requires it.

## Source-Type Decision Matrix

| Source type | Use when | Expected output | Notes |
|-------------|----------|-----------------|-------|
| `local` | The user already provided the exact asset or the template already includes it | `<project>/images/...` | Capture crop, focus, and reuse notes instead of writing a fake generation prompt |
| `ai` | The asset is abstract, illustrative, conceptual, or highly customized to the deck style | `<project>/images/...` | Prefer `image_generate` and provider smoke tests |
| `stock` | The asset should be photorealistic and a stock source is acceptable | `<project>/images/stock/...` | Use `download_stock_image` or `register_stock_image`; do not bypass the manifest flow |
| `placeholder` | The slide layout needs reserved space but the final asset is pending approval or deferred | no live asset yet | Mark the asset explicitly so Executor does not guess |

## Canvas Mapping

Use an aspect ratio that matches both the canvas and the active provider constraints.

| Canvas format | Suggested aspect ratio | Common size target |
|---------------|------------------------|--------------------|
| `ppt169` | `16:9` | `1K`, `2K`, or `4K` depending on provider and reuse needs |
| `ppt43` | `4:3` | `1K` or `2K` |
| `xiaohongshu` | `3:4` | `2K` |
| `moments` | `1:1` | `1K` or `2K` |
| `story` | `9:16` | `2K` or `4K` |

Supported provider-neutral aspect ratios are defined by the workflow tooling. Prefer:

```text
1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
```

## Recommended File Structure

Use a structure close to the following:

````markdown
# Image Prompt Pack

- Project: <project-name>
- Canvas: <canvas-format>
- Style: <style summary>
- Palette: <primary / secondary / accent>

## Asset Overview

| # | Filename | Use | Source Type | Aspect Ratio | Image Size | Status | Target Path |
|---|----------|-----|-------------|--------------|------------|--------|-------------|
| 1 | cover_bg.png | Cover background | ai | 16:9 | 2K | pending | images/cover_bg.png |

## Asset 1: cover_bg.png

- Use: Cover background
- Source type: ai
- Target path: images/cover_bg.png
- Visual role: full-bleed background with safe text area

**Prompt**
```text
<final positive prompt>
```

**Negative Prompt**
```text
<final negative prompt>
```

**Alt Text**
> <short descriptive alt text>

**Acquisition**
- Provider: gemini
- Suggested model: gemini-3.1-flash-image-preview
- Command target: `python3 skills/slidemax_workflow/scripts/slidemax.py image_generate ...`
````

## Prompt Writing Rules

For AI-generated assets, each section should include:

- subject description
- style guidance
- color guidance
- composition guidance
- quality guidance
- negative prompt
- alt text
- provider or command recommendation when helpful

For stock assets, replace the generation prompt with:

- preferred provider
- search brief
- acceptable subject variants
- required framing or crop notes
- expected local filename
- manifest registration reminder

For local assets, replace the generation prompt with:

- confirmed source filename
- target project-local path
- crop or focus notes
- any rotation or cleanup tasks

For placeholders, write:

- why the placeholder exists
- what final asset is still missing
- whether Executor should leave the area empty, use a neutral block, or reserve a labeled slot

## Reusable Prompt Patterns

### Background Image

Use when the asset sits behind slide text or title blocks.

```text
Abstract <theme> background, <style> style, <palette guidance>, subtle detail, clean negative space for text overlay, <aspect ratio> aspect ratio, high resolution
```

### Illustration

Use when the deck needs a conceptual or brand-aligned visual rather than a photo.

```text
<subject>, <illustration style>, clean lines, simplified forms, palette matching <brand colors>, white or transparent background, presentation-ready composition
```

### Photorealistic Scene

Use only when AI is still preferred over stock.

```text
<subject>, professional photography, natural lighting, realistic materials, clean composition, color grading aligned with <palette>, high detail
```

### Negative Prompt Baseline

Start with the following and then tighten it for the asset type:

```text
text, watermark, signature, logo, blurry details, low resolution, distorted anatomy, clipped subject
```

## Quality Checklist

Before leaving Stage 5, verify that:

- every required asset has a source type
- every AI asset has a positive prompt, negative prompt, and alt text
- every stock asset has a provider and registration path
- every local asset has a confirmed path and any required cleanup notes
- aspect ratio and size match the canvas and provider constraints
- the prompt file points only to project-local output paths

## Provenance and Risk Routing

Use the following commands when provenance or watermark risk should be explicit:

- `register_image_source` for user-provided or manually obtained local images that need sidecar provenance metadata
- `download_stock_image` or `register_stock_image` for stock assets that must land in `images/stock/manifest.json`
- `audit_image_asset` when watermark risk or asset provenance is unclear before delivery

Do not rely on chat history as the only source record for a delivered image.
