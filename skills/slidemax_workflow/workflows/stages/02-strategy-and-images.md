# Stage 4-5 Playbook

This playbook covers the planning stages that define the design contract and localize required image assets.

## Scope

- Stage 4: Strategist
- Stage 5: Image_Generator

## Stage 4: Strategist

This stage is mandatory for every PPT project.

Required reads:

- `skills/slidemax_workflow/roles/Strategist.md`
- `skills/slidemax_workflow/roles/guides/strategist-confirmations.md`
- `skills/slidemax_workflow/roles/guides/strategist-image-planning.md`
- `skills/slidemax_workflow/roles/guides/strategist-design-brief-contract.md`

Execution steps:

1. Confirm source, project path, template decision, and delivery format.
2. Complete the eight confirmations.
3. If the user provided local images, run:

   ```bash
   python3 skills/slidemax_workflow/scripts/slidemax.py analyze_images <project-path>/images
   ```

4. Write the project design brief into `<project-path>/design_specification.md`.
5. Route to `Image_Generator` or one Executor.

Checkpoint marker:

```markdown
## Strategist Stage Complete
- [x] Eight confirmations are complete
- [x] The design brief and content outline were generated
- [x] The design brief was saved into the project
- [ ] Next: Image_Generator or an Executor
```

## Stage 5: Image_Generator

Trigger this stage when the image strategy includes AI generation or stock assets.

Required reads:

- `skills/slidemax_workflow/roles/Image_Generator.md`
- `skills/slidemax_workflow/roles/guides/image-generator-prompt-pack.md`
- `skills/slidemax_workflow/references/docs/image_generation_providers.md`

Execution steps:

1. Extract all assets that require external acquisition from the design brief.
2. Create `<project-path>/images/image_prompts.md`.
3. If a live provider will be used, smoke test it first.
4. Generate, download, or register assets into project-local paths.
5. Confirm that required assets now exist under `images/` or `images/stock/`.

Provider smoke-test examples:

```bash
python3 skills/slidemax_workflow/scripts/slidemax.py smoke_test_image_provider --provider gemini --output <project-path>/images --aspect-ratio 16:9 --image-size 1K
python3 skills/slidemax_workflow/scripts/slidemax.py smoke_test_image_provider --provider doubao --model doubao-seedream-4.5 --output <project-path>/images --aspect-ratio 16:9 --image-size 1K
```

Checkpoint marker:

```markdown
## Image_Generator Stage Complete
- [x] The role file was read
- [x] `images/image_prompts.md` was created
- [x] Provider smoke testing completed when a live provider was used
- [x] Required images were saved under `images/` or `images/stock/`
- [x] Asset status was refreshed in the project
- [ ] Next: an Executor
```

## Exit Criteria

Do not enter Stage 6 until all of the following are true:

- The design brief exists on a project-local path.
- Image decisions are explicit.
- Required image files are local or intentionally marked as placeholders.
- The next role is one specific Executor.
