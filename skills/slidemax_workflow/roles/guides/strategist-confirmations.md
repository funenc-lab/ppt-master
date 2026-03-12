# Strategist Confirmations Guide

Use this guide when completing the mandatory confirmation block for the Strategist stage.

## The Eight Confirmations

1. Canvas format
2. Slide count range
3. Audience and presentation context
4. Visual route and style recommendation
5. Color palette
6. Icon strategy
7. Image strategy
8. Typography strategy

Do not move into design-brief writing until all eight are explicit.

## 1. Canvas Format

Pick the output format according to delivery context.

| Format | Size | Typical Use |
|--------|------|-------------|
| PPT 16:9 | `1280x720` | Business presentation, meeting deck |
| PPT 4:3 | `1024x768` | Legacy projector environments |
| Xiaohongshu | `1242x1660` | Social graphic post |
| WeChat Moments | `1080x1080` | Square social card |
| Story | `1080x1920` | Vertical short-form story |

Reference: `../../references/docs/canvas_formats.md`

## 2. Slide Count Range

Estimate the page range from source density.

- Use a tight range instead of a single number when the source is still fluid.
- Prefer explicit trade-offs such as “short version vs full version”.

## 3. Audience and Presentation Context

Capture:

- Who will read or watch the deck
- What decision or outcome the deck should support
- Whether the deck is live-presented, self-read, or distributed asynchronously

## 4. Visual Route and Style Recommendation

Route to one of the three executor families.

| Route | Executor | Best Fit |
|-------|----------|----------|
| General | `Executor_General.md` | Promotion, training, mixed storytelling, visual-first decks |
| Consultant | `Executor_Consultant.md` | Work reports, structured business updates, data-heavy slides |
| Consultant Top | `Executor_Consultant_Top.md` | Executive persuasion, strategic review, board-grade decks |

Recommendation rule:

- Choose General when image impact and flexible composition matter most.
- Choose Consultant when clear data communication matters most.
- Choose Consultant Top when argument structure and executive persuasion matter most.

## 5. Color Palette

Provide a primary, secondary, and accent color set in HEX.

Palette rules:

- Follow a `60/30/10` balance.
- Keep text contrast readable.
- Avoid more than four dominant colors on one slide.

Typical references:

| Context | Suggested Primary |
|---------|-------------------|
| Finance or business | `#003366` |
| Technology | `#1565C0` |
| Healthcare | `#00796B` |
| Public sector | `#C41E3A` |

Full reference: `../../slidemax/config.py`

## 6. Icon Strategy

Choose one of the following:

- Emoji
- AI-generated icon-style illustration
- Built-in icon library
- Custom icons

If the built-in icon library is selected, verify every icon name before writing the design brief.

Required verification path:

1. Read `../../templates/icons/icons_index.json`
2. Confirm that the chosen icon name exists
3. Record the final approved icon list in the design brief

Do not invent path-like icon names.

## 7. Image Strategy

Choose one or more of the following:

- No images
- User-provided local images
- AI-generated images
- Placeholder frames
- Commercial stock assets

If user-provided images are selected, run `analyze_images` before finalizing the brief.

Detailed policy: [strategist-image-planning.md](./strategist-image-planning.md)

## 8. Typography Strategy

Set:

- Title font family
- Body font family
- Emphasis font family
- Base body size

Density rule:

| Density | Body Size | Typical Use |
|---------|-----------|-------------|
| Low density | `24px` | Presentation-style decks, training, sparse pages |
| High density | `18px` | Reports, consulting analysis, dense content |

Suggested scale:

| Role | Ratio | 24px Base | 18px Base |
|------|-------|-----------|-----------|
| Cover title | `2.5x` to `3x` | `60px` to `72px` | `45px` to `54px` |
| Content title | `1.5x` to `2x` | `36px` to `48px` | `27px` to `36px` |
| Body | `1x` | `24px` | `18px` |
| Annotation | `0.75x` | `18px` | `14px` |

## Speaker Notes Defaults

Record the note expectations in the design brief.

- Notes should align with SVG filenames when possible.
- `notes/total.md` is the aggregate manuscript.
- Split note files should not contain heading markers.
