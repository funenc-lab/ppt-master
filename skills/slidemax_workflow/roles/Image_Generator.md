# Role: Image_Generator

## Operational Image Quickstart

Use this section before reading the detailed prompt-pack guide below.

### Stage Entry Flow

```text
Entering Image_Generator stage
  -> Read the strategy output and the image asset list
  -> Classify each asset as local, AI-generated, stock, or placeholder
  -> Write `images/image_prompts.md` first
  -> If live AI generation is needed, smoke test the provider configuration
  -> Generate, download, or register assets into project-local paths
  -> Confirm every required image now exists under `images/` or `images/stock/`
  -> Hand off to Executor with concrete local asset paths
```

### Source Decision Matrix

| Asset Type | Preferred Path | Canonical Tooling |
|------------|----------------|-------------------|
| AI image | Generate into `images/` | `image_generate`, `smoke_test_image_provider` |
| Commercial stock image | Normalize into `images/stock/` | `download_stock_image`, `register_stock_image` |
| User-provided image | Keep on a project-local path | `analyze_images` when inspection is needed |
| Placeholder | Record explicitly in the asset list | No generation tool |

### Output Contract

The Image_Generator stage should leave the project with:

- `images/image_prompts.md` written before generation starts
- Concrete image files stored on project-local paths
- Stock provenance recorded when stock assets are used
- Updated asset status that Executor can consume without guessing

### Reliability Rules

- Do not generate or download assets before the prompt file exists.
- Do not rely on remote image links inside slide delivery assets.
- Do not treat a provider as stable before a smoke test succeeds.
- Do not hand off to Executor while required image files are still missing.
- Do not mix provider experiments with delivery output paths unless the result is intentionally accepted.

## Mission

The Image_Generator stage turns the Strategist image plan into a project-local prompt pack and a localized asset set.

## Workflow Context

| Previous Step | Current Step | Next Step |
|---------------|--------------|-----------|
| Strategist | Image_Generator | Executor |

Full workflow: [../AGENTS.md](../AGENTS.md)

## Required Reads

| Document | Purpose |
|----------|---------|
| [guides/image-generator-prompt-pack.md](./guides/image-generator-prompt-pack.md) | Prompt-file structure, asset typing, acquisition paths, and completion rules |
| [../references/docs/image_generation_providers.md](../references/docs/image_generation_providers.md) | Provider selection and configuration guidance |
| [../references/docs/image_generation_setup.md](../references/docs/image_generation_setup.md) | Environment setup and smoke-test preparation |

## Execution Steps

1. Read the project design brief and extract all assets that still need acquisition.
2. Create:

   ```text
   <project-path>/images/image_prompts.md
   ```

3. Record one section per asset with source type, target local path, aspect ratio or size, prompt or acquisition brief, alt text, and acquisition notes.
4. If a live provider will be used, smoke test it first.
5. Acquire assets through generation, download, registration, or a documented placeholder path.
6. Confirm the asset set is ready for Executor consumption.

## Canonical Acquisition Paths

### AI Generation

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py image_generate "prompt" --provider gemini --aspect-ratio 16:9 --image-size 4K --output <project-path>/images --filename cover_bg
```

### Provider Smoke Test

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py smoke_test_image_provider --provider gemini --output <project-path>/images
python3 skills/slidemax_workflow/scripts/slidemax.py smoke_test_image_provider --provider doubao --model doubao-seedream-4.5 --output <project-path>/images
```

### Stock Localization

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py download_stock_image <project-path> --provider <provider> --source-url <url> --download-url <url> --filename <filename>
python3 skills/slidemax_workflow/scripts/slidemax.py register_stock_image <project-path> --provider <provider> --source-url <url> --local-file <path> --filename <filename>
```

## Handoff Rule

Do not hand off to Executor until one of the following is true for every required asset:

- The file exists under `images/` or `images/stock/`
- The brief explicitly marks it as a placeholder
- The user has been instructed to generate it manually from `image_prompts.md`

## Stage Completion Marker

```markdown
## Image_Generator Stage Complete
- [x] The role file was read
- [x] `images/image_prompts.md` was created
- [x] Provider smoke testing completed when a live provider was used
- [x] Required images were saved under `images/` or `images/stock/`
- [x] Asset status was refreshed in the project
- [ ] Next: an Executor
```
