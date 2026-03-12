# AI Setup Prompts

Use this document when you want an AI assistant to help configure SlideMax environment variables without guessing the workflow structure.

## Document Boundary

This file only stores copy-paste prompts for AI-assisted setup or drafting.

- Normative setup rules live in `./image_generation_setup.md`
- Provider and model reference lives in `./image_generation_providers.md`
- Prompt-pack structure lives in `./image_prompt_guidance.md`
- Stock provenance workflow lives in `./image_stock_sources.md`
- ARK video setup lives in `./ark_video_generation.md`

Keep the prompts short and reusable. Do not move the operational rules into this file.

## Image Generation Prompt

Paste the following into your AI assistant after you copy `skills/slidemax_workflow/examples/config/slidemax_image.env.example` to a local untracked file:

```text
I am setting up SlideMax image generation.
Please help me choose the correct provider block, tell me which required environment variables I must fill in, which optional variables I can leave empty, and how to verify the setup.
Use these files as the canonical references:
- skills/slidemax_workflow/examples/config/slidemax_image.env.example
- skills/slidemax_workflow/references/docs/image_generation_setup.md
- skills/slidemax_workflow/references/docs/image_generation_providers.md
After the file is filled, tell me which doctor command to run next.
```

## Image Prompt Authoring Prompt

Paste the following into your AI assistant after Strategist has produced the design brief and image asset list:

```text
I am in the SlideMax Image_Generator stage.
Please help me draft <project-path>/images/image_prompts.md from my design brief and image asset list.

Requirements:
- classify each asset as local, ai, stock, or placeholder
- preserve project-local output paths only
- for ai assets include prompt, negative prompt, alt text, aspect ratio, image size, and a suggested provider
- for stock assets include provider preference, search brief, target filename, and manifest registration notes
- for local assets include confirmed source path and any crop or cleanup notes
- for placeholders explain what is still missing and how Executor should reserve the layout

Use these files as the canonical references:
- skills/slidemax_workflow/roles/Image_Generator.md
- skills/slidemax_workflow/references/docs/image_prompt_guidance.md
- skills/slidemax_workflow/references/docs/image_generation_providers.md
- skills/slidemax_workflow/references/docs/image_stock_sources.md

Do not skip the prompt file and do not point Executor to remote image URLs.
```

## Stock Image Registration Prompt

Paste the following into your AI assistant after you copy `skills/slidemax_workflow/examples/config/slidemax_stock.env.example` to a local untracked file:

```text
I am setting up SlideMax stock image registration.
Please explain each variable in my stock env file, tell me which values are safe defaults, and tell me whether I need to change the provider allowlist for my team.
Use these files as the canonical references:
- skills/slidemax_workflow/examples/config/slidemax_stock.env.example
- skills/slidemax_workflow/references/docs/image_stock_sources.md
Then tell me which registration command or download command I should run first.
```

## ARK Video Prompt

Paste the following into your AI assistant after you copy `skills/slidemax_workflow/examples/config/slidemax_ark.env.example` to a local untracked file:

```text
I am setting up SlideMax ARK video generation.
Please tell me which variables are required, which defaults are safe to keep, and how to verify the setup before I create a live task.
Use these files as the canonical references:
- skills/slidemax_workflow/examples/config/slidemax_ark.env.example
- skills/slidemax_workflow/references/docs/ark_video_generation.md
Then give me the safest first command to run.
```

## Safety Rules

- Keep real secrets in local untracked files only.
- Do not paste real API keys into versioned files.
- Prefer `project_manager doctor` before the first live provider request.
- Ask the AI assistant to explain why each variable is needed instead of blindly filling every optional field.
