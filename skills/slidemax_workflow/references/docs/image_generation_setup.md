# Image Generation Credentials and Tooling Setup

This guide explains how to configure credentials, environment variables, and command examples for the SlideMax image workflow.

## Document Boundary

Use this document for operator setup and first-run validation only.

- Provider registry, model defaults, and SDK surface: `./image_generation_providers.md`
- Prompt file structure and asset classification: `./image_prompt_guidance.md`
- Copy-paste prompts for AI-assisted setup: `./ai_setup_prompts.md`
- Stock source provenance and manifest flow: `./image_stock_sources.md`
- ARK image-to-video setup: `./ark_video_generation.md`

## Files Delivered

- Environment template: `../../examples/config/slidemax_image.env.example`
- Command template: `../../examples/config/image_generate_commands.sh.example`
- Provider reference: `./image_generation_providers.md`
- Prompt authoring guide: `./image_prompt_guidance.md`
- AI setup prompts: `./ai_setup_prompts.md`
- Stock image setup: `./image_stock_sources.md`
- Stock env template: `../../examples/config/slidemax_stock.env.example`
- Stock command template: `../../examples/config/register_stock_image.sh.example`
- ARK video setup: `./ark_video_generation.md`

## Recommended Setup Flow

1. Copy the environment template to an untracked local file.
2. Fill in only the provider block you intend to use.
3. Load the file with `source` in the current shell.
4. Install the SDK package for the provider you plan to use.
5. Draft `images/image_prompts.md` with the project asset list before the first live request.
6. Run `image_generate` using the matching provider.

## Dependency-Aware Installation

Install only the packages required by the workflow you plan to use:

```bash
# Shared bundle
pip install -r requirements.txt

# Gemini image generation
pip install google-genai

# OpenAI-compatible image generation
pip install openai

# Doubao / ARK image generation
pip install "volcengine-python-sdk[ark]"

# Optional local diagnostics
pip install Pillow
```

`image_generate` and `nano_banana_gen` now print provider-specific dependency and configuration hints automatically when setup is incomplete.

If you want an AI assistant to guide the setup step-by-step, use the ready-made prompts in `./ai_setup_prompts.md`.

## Prompt Authoring Before Live Generation

Before the first live generation request in a project:

1. Read the design brief and image asset list.
2. Draft `<project>/images/image_prompts.md`.
3. Decide whether each asset is `local`, `ai`, `stock`, or `placeholder`.
4. Run a provider smoke test only after the prompt file exists.

Use `./image_prompt_guidance.md` as the compact checklist for structuring the prompt file and selecting the correct acquisition path per asset.

## Recommended Validation Commands

Use the doctor command before the first live request or after switching providers:

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py project_manager doctor --provider gemini
python3 skills/slidemax_workflow/scripts/slidemax.py project_manager doctor --provider openai-compatible
python3 skills/slidemax_workflow/scripts/slidemax.py project_manager doctor --provider doubao --model doubao-seedream-5
```

The doctor output now checks:

- shared Python packages such as `requests`
- optional local diagnostics such as `Pillow`
- provider SDK availability for the selected provider
- provider credential and base URL configuration

## Example: Create a local config file

```bash
cp skills/slidemax_workflow/examples/config/slidemax_image.env.example .env.slidemax-image
```

Then edit `.env.slidemax-image` and load it:

```bash
source .env.slidemax-image
```

## Image Acquisition Modes

SlideMax supports three stable acquisition paths:

1. project-local images under `<project>/images/`
2. commercial stock images under `<project>/images/stock/`
3. AI-generated images written to `<project>/images/`

Use `./image_generation_providers.md` as the provider-side reference for the normalized acquisition surface.
Use `./image_stock_sources.md` when the asset must go through the stock manifest flow.
Use `./ark_video_generation.md` for Seedance-based image-to-video tasks instead of `image_generate`.

## SDK Dependencies

The installation commands earlier in this document are the operator checklist for first-run setup.
Keep `./image_generation_providers.md` as the reference for provider-specific SDK ownership and model defaults.

## Shared Variables

These variables apply across providers and are the preferred place for workflow defaults:

- `SLIDEMAX_IMAGE_PROVIDER`
- `SLIDEMAX_IMAGE_OUTPUT_DIR`
- `SLIDEMAX_IMAGE_TIMEOUT`
- `SLIDEMAX_IMAGE_API_KEY`
- `SLIDEMAX_IMAGE_BASE_URL`
- `SLIDEMAX_IMAGE_ENDPOINT`
- `SLIDEMAX_IMAGE_MODEL`

Use shared variables when your environment switches providers frequently and you want one common override surface.

## Provider-Specific Variables

### Gemini

- `GEMINI_API_KEY`
- `GEMINI_BASE_URL`
- `GEMINI_IMAGE_MODEL`

### OpenAI-compatible

- `OPENAI_IMAGE_API_KEY`
- `OPENAI_IMAGE_BASE_URL`
- `OPENAI_IMAGE_ENDPOINT`
- `OPENAI_IMAGE_MODEL`

### Doubao

- `ARK_API_KEY` or `DOUBAO_API_KEY`
- `ARK_BASE_URL` or `DOUBAO_BASE_URL`
- `DOUBAO_IMAGE_ENDPOINT`
- `DOUBAO_IMAGE_MODEL`

## Provider Examples

### Gemini

```bash
export SLIDEMAX_IMAGE_PROVIDER=gemini
export GEMINI_API_KEY="your-key"
export SLIDEMAX_IMAGE_OUTPUT_DIR="workspace/demo/images"
```

### Doubao Seedream

Use Seedream as the default model for static image generation.
Use `doubao_i2v_task` when you need Seedance-based image-to-video generation.

```bash
export SLIDEMAX_IMAGE_PROVIDER=doubao
export ARK_API_KEY="your-key"
export ARK_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
export DOUBAO_IMAGE_MODEL="doubao-seedream-4.5"
export SLIDEMAX_IMAGE_OUTPUT_DIR="workspace/demo/images"
```

The workflow also accepts `DOUBAO_API_KEY` and `DOUBAO_BASE_URL` as aliases for the same provider configuration.

The workflow also accepts the alias `doubao-seedream-5` and automatically normalizes it to the concrete model id `doubao-seedream-5-0-260128`.

For `doubao-seedream-5-0-260128`, the workflow now enforces a local minimum canvas size of `3686400` pixels before the SDK request is sent.
For example, `16:9` with `1K` is rejected locally, while `16:9` with `4K` is valid.

Recommended smoke test for Seedream 5 widescreen output:

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py smoke_test_image_provider \
  --provider doubao \
  --model doubao-seedream-5-0-260128 \
  --prompt "Minimal business presentation background" \
  --aspect-ratio 16:9 \
  --image-size 4K \
  --output workspace/demo/images \
  --filename seedream5_smoke
```

## Tool Invocation Examples

Use the bundled shell example directly or copy the commands into your own scripts:

```bash
bash skills/slidemax_workflow/examples/config/image_generate_commands.sh.example
```

For commercial stock images, use the dedicated examples and commands:

```bash
bash skills/slidemax_workflow/examples/config/register_stock_image.sh.example
python3 skills/slidemax_workflow/scripts/slidemax.py download_stock_image workspace/demo \
  --provider pexels \
  --source-url "https://www.pexels.com/photo/example-id/" \
  --download-url "https://images.pexels.com/photos/example.jpeg" \
  --filename stock_cover.jpg
```

You can inspect provider metadata and the smoke-test CLI shape without credentials:

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py image_generate --list-providers
python3 skills/slidemax_workflow/scripts/slidemax.py smoke_test_image_provider --help
```

## Safety Notes

- Do not commit filled credential files.
- Keep real keys in a local file outside git or in your shell profile.
- Prefer `SLIDEMAX_IMAGE_OUTPUT_DIR` for stable project-local output routing.
- If a provider requires a non-standard gateway, set `*_IMAGE_ENDPOINT` explicitly.
