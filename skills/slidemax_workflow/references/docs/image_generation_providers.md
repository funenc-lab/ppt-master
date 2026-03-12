# Image Generation Providers

This document defines the provider-neutral image generation surface for SlideMax.

## Document Boundary

Use this file as the provider and model reference layer.

- Step-by-step local setup and doctor flow belong in `./image_generation_setup.md`
- Prompt-pack authoring rules belong in `./image_prompt_guidance.md`
- Stock provenance and manifest workflow belong in `./image_stock_sources.md`
- AI-assistant prompt templates belong in `./ai_setup_prompts.md`
- ARK image-to-video setup belongs in `./ark_video_generation.md`

## Goals

- Keep the workflow independent from a single image vendor.
- Allow image output paths to be configured through environment variables.
- Allow new models and gateways to be added without rewriting the role workflow.
- Use the official SDK for each supported provider.

## Canonical Command

Use `scripts/slidemax.py image_generate` as the primary CLI.

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py image_generate "Abstract tech background" \
  --provider gemini \
  --aspect-ratio 16:9 \
  --image-size 4K \
  --output workspace/demo/images \
  --filename cover_bg
```

The legacy `scripts/slidemax.py nano_banana_gen` command remains available as a Gemini-only compatibility wrapper.

## Image Acquisition Modes

SlideMax accepts image assets through the following normalized paths:

- Local or template assets copied into `<project>/images/`
- Commercial stock assets downloaded or registered into `<project>/images/stock/`
- AI-generated assets written into `<project>/images/` by `image_generate`

The workflow keeps Executor on project-local paths and avoids third-party hotlinks inside slide SVG files.

## Example Files

- Environment template: `../../examples/config/slidemax_image.env.example`
- Command template: `../../examples/config/image_generate_commands.sh.example`
- Setup guide: `./image_generation_setup.md`

## Supported Providers

### 1. `gemini`

- Default model: `gemini-3.1-flash-image-preview`
- Environment variables:
  - `GEMINI_API_KEY` or `SLIDEMAX_IMAGE_API_KEY`
  - `GEMINI_BASE_URL` or `SLIDEMAX_IMAGE_BASE_URL`
  - `GEMINI_IMAGE_MODEL` or `SLIDEMAX_IMAGE_MODEL`
  - Official SDK: `google-genai`

### 2. `openai-compatible`

- Default model: `gpt-image-1`
- Intended for providers exposing an OpenAI-compatible API through the official `openai` SDK.
- Environment variables:
  - `OPENAI_IMAGE_API_KEY` / `OPENAI_API_KEY` / `SLIDEMAX_IMAGE_API_KEY`
  - `OPENAI_IMAGE_BASE_URL` / `OPENAI_BASE_URL` / `SLIDEMAX_IMAGE_BASE_URL`
  - `OPENAI_IMAGE_ENDPOINT` / `SLIDEMAX_IMAGE_ENDPOINT`
  - `OPENAI_IMAGE_MODEL` / `SLIDEMAX_IMAGE_MODEL`
  - Official SDK: `openai`

### 3. `doubao`

- Default model: `doubao-seedream-4.5`
- Static image generation defaults to the Seedream series.
- `image_generate` is wired to the official ARK SDK for static image generation.
- ARK image-to-video tasks should use `scripts/slidemax.py doubao_i2v_task` with Seedance models instead of `image_generate`.
- Seedream 5 models can be selected through `--model` or `DOUBAO_IMAGE_MODEL`.
- The workflow validates known model constraints locally before the request is sent.
  - Current built-in rule: `doubao-seedream-5*` requires at least `3686400` pixels.
- Environment variables:
  - `ARK_API_KEY` / `DOUBAO_API_KEY` / `SLIDEMAX_IMAGE_API_KEY`
  - `ARK_BASE_URL` / `DOUBAO_BASE_URL` / `SLIDEMAX_IMAGE_BASE_URL`
  - `DOUBAO_IMAGE_ENDPOINT` / `SLIDEMAX_IMAGE_ENDPOINT`
  - `DOUBAO_IMAGE_MODEL` / `SLIDEMAX_IMAGE_MODEL`
  - Official SDK: `volcengine-python-sdk[ark]`

## Dependency Commands

Use the commands below as the provider matrix reference.
For the recommended first-run order, local env file flow, and doctor validation sequence, follow `./image_generation_setup.md`.

Install the packages according to the provider you intend to use:

```bash
# Shared bundle
pip install -r requirements.txt

# Gemini
pip install google-genai

# OpenAI-compatible
pip install openai

# Doubao / ARK
pip install "volcengine-python-sdk[ark]"

# Optional local diagnostics
pip install Pillow
```

If the active provider is misconfigured, `image_generate`, `nano_banana_gen`, and `project_manager doctor` now print setup hints that point back to the env template and setup guide.

## Shared Environment Variables

- `SLIDEMAX_IMAGE_PROVIDER`: default provider when `--provider` is omitted.
- `SLIDEMAX_IMAGE_MODEL`: default model override for the active provider.
- `SLIDEMAX_IMAGE_OUTPUT_DIR`: default output directory for generated assets.
- `SLIDEMAX_IMAGE_BASE_URL`: shared provider base URL override.
- `SLIDEMAX_IMAGE_ENDPOINT`: shared provider endpoint override.
- `SLIDEMAX_IMAGE_API_KEY`: shared provider API key override.
- `SLIDEMAX_IMAGE_TIMEOUT`: request timeout in seconds.

## Recommended Configuration Examples

### Gemini

```bash
export SLIDEMAX_IMAGE_PROVIDER=gemini
export GEMINI_API_KEY="your-key"
export SLIDEMAX_IMAGE_OUTPUT_DIR="workspace/demo/images"
```

### Doubao Seedream

```bash
export SLIDEMAX_IMAGE_PROVIDER=doubao
export ARK_API_KEY="your-key"
export ARK_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
export DOUBAO_IMAGE_MODEL="doubao-seedream-4.5"
export SLIDEMAX_IMAGE_OUTPUT_DIR="workspace/demo/images"
```

The workflow also accepts `DOUBAO_API_KEY` and `DOUBAO_BASE_URL` as aliases for the same provider configuration.

## Doubao ARK Note

The `doubao` entry in `image_generate` now prefers the official ARK SDK for image generation.
If you need the official ARK image-to-video task flow, use `scripts/slidemax.py doubao_i2v_task` and `references/docs/ark_video_generation.md`.

## Workflow Guidance

- `Strategist` decides whether the image source is template, user-provided, AI-generated, or placeholder.
- `Image_Generator` always writes prompts to `images/image_prompts.md` first.
- When AI generation is required, the role should prefer `image_generate` over provider-specific commands.
- Store all final assets in the project `images/` directory before entering `Executor`.
- Use `./image_prompt_guidance.md` for the prompt-pack contract instead of re-describing the file shape here.
