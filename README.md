# SlideMax

[![Version](https://img.shields.io/badge/version-v1.2.0-blue.svg)](https://github.com/funenc-lab/slidemax/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/funenc-lab/slidemax.svg)](https://github.com/funenc-lab/slidemax/stargazers)

English | [中文](./README_CN.md)

SlideMax is an AI-assisted SVG presentation workflow repository.

This root README is a repository landing page only.
The canonical PPT workflow handbook is:

- [`skills/slidemax_workflow/AGENTS.md`](./skills/slidemax_workflow/AGENTS.md)

## Quick Start

1. Clone the repository.
2. Install Python dependencies.
3. Read the workflow handbook before running any PPT task.

```bash
git clone https://github.com/funenc-lab/slidemax.git
cd slidemax
pip install -r requirements.txt
```

## Canonical Entry Points

- Workflow handbook: [`skills/slidemax_workflow/AGENTS.md`](./skills/slidemax_workflow/AGENTS.md)
- Skill entry: [`skills/slidemax_workflow/SKILL.md`](./skills/slidemax_workflow/SKILL.md)
- Commands reference: [`skills/slidemax_workflow/commands/README.md`](./skills/slidemax_workflow/commands/README.md)
- Role definitions: [`skills/slidemax_workflow/roles/AGENTS.md`](./skills/slidemax_workflow/roles/AGENTS.md)
- Examples index: [`skills/slidemax_workflow/examples/README.md`](./skills/slidemax_workflow/examples/README.md)

## Repository Layout

```text
slidemax/
├── skills/slidemax_workflow/  # Canonical workflow assets
├── workspace/                 # Runtime project outputs
├── README.md
└── README_CN.md
```

## Notes

- Do not treat this README as a second workflow manual.
- Prefer `skills/slidemax_workflow/commands/` as the command entry surface.
- Use `skills/slidemax_workflow/AGENTS.md` when explaining, running, or editing the workflow.
