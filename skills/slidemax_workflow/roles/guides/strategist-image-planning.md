# Strategist Image Planning Guide

Use this guide when the design brief includes any image-related decision.

## Image Strategy Options

| Strategy | Meaning | Typical Next Step |
|----------|---------|-------------------|
| None | No image dependency | Route directly to Executor |
| Local | User or team already has image assets | Analyze and localize under `images/` |
| AI | Images will be generated after strategy | Route to Image_Generator |
| Placeholder | Layout reserves image space only | Route directly to Executor |
| Stock | Commercial stock asset will be localized | Route to Image_Generator or stock registration flow |

Combined strategies are allowed.

## Required Image Resource List

When any image strategy other than `None` is selected, add an image resource table to the design brief.

Suggested columns:

| Filename | Size | Ratio | Layout Hint | Usage | Type | Status | Source | Prompt or Source Note |
|----------|------|-------|-------------|-------|------|--------|--------|-----------------------|

Status values:

- `to-generate`
- `ready`
- `placeholder`

Source values:

- `ai`
- `local`
- `stock(<provider>)`
- `placeholder`

## When `analyze_images` Is Mandatory

Run this command after the eight confirmations and before finalizing the design brief when local images are part of the plan:

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py analyze_images <project-path>/images
```

The scan output should be copied into the image resource list so later stages do not guess aspect ratios or layout fit.

## Layout-Fit Rules

The layout container should match the image ratio closely enough to avoid unusable whitespace.

| Image Ratio | Preferred Layout |
|-------------|------------------|
| `> 1.5` | Top-and-bottom or wide image zone |
| `1.2` to `1.5` | Standard left-right split |
| `0.8` to `1.2` | Balanced two-column or card layout |
| `< 0.8` | Vertical image zone or sidebar layout |

Avoid:

- Forcing a wide image into a square box
- Forcing a portrait image into a narrow horizontal strip
- Letting image whitespace dominate the slide

For complex diagrams, prioritize readable area over decorative balance.

## Stock Asset Rules

If stock assets are planned:

- Keep them on project-local paths under `images/stock/`
- Register provenance into `images/stock/manifest.json`
- Keep the design brief source label explicit

## Handoff Rule

Do not send a project to Executor while image-dependent layouts still rely on an ambiguous image source.
