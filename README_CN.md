# SlideMax

[![Version](https://img.shields.io/badge/version-v1.2.0-blue.svg)](https://github.com/funenc-lab/slidemax/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/funenc-lab/slidemax.svg)](https://github.com/funenc-lab/slidemax/stargazers)

[English](./README.md) | 中文

SlideMax 是一个 AI 辅助的 SVG 演示文稿工作流仓库。

根目录 README 仅作为仓库入口页使用。
唯一权威的 PPT workflow 手册在：

- [`skills/slidemax_workflow/AGENTS.md`](./skills/slidemax_workflow/AGENTS.md)

## 快速开始

1. 克隆仓库。
2. 安装 Python 依赖。
3. 任何 PPT 任务开始前先阅读工作流手册。

```bash
git clone https://github.com/funenc-lab/slidemax.git
cd slidemax
pip install -r requirements.txt
```

## Canonical 入口

- 工作流手册：[`skills/slidemax_workflow/AGENTS.md`](./skills/slidemax_workflow/AGENTS.md)
- Skill 入口：[`skills/slidemax_workflow/SKILL.md`](./skills/slidemax_workflow/SKILL.md)
- 工具说明：[`skills/slidemax_workflow/commands/README_CN.md`](./skills/slidemax_workflow/commands/README_CN.md)
- 角色定义：[`skills/slidemax_workflow/roles/AGENTS.md`](./skills/slidemax_workflow/roles/AGENTS.md)
- 示例索引：[`skills/slidemax_workflow/examples/README.md`](./skills/slidemax_workflow/examples/README.md)

## 仓库结构

```text
slidemax/
├── skills/slidemax_workflow/  # Canonical workflow assets
├── workspace/                 # Runtime project outputs
├── README.md
└── README_CN.md
```

## 说明

- 不要把本 README 当作第二套 workflow 手册。
- 日常命令入口优先使用 `skills/slidemax_workflow/commands/`。
- 解释、执行或修改工作流时，统一以 `skills/slidemax_workflow/AGENTS.md` 为准。
