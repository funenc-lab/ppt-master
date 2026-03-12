from __future__ import annotations

import argparse
from typing import Optional, Sequence

from .. import video_generation as core
from ..video_generation import (
    add_common_generation_arguments,
    execute_parsed_command,
    print_result,
    print_status,
    request_from_args,
    str_to_bool,
)

CLI_PROG = "python3 skills/slidemax_workflow/scripts/slidemax.py doubao_i2v_task"


def build_parser() -> argparse.ArgumentParser:
    return core.build_parser(
        prog=CLI_PROG,
        epilog='''
When to use:
  - Create or run ARK image-to-video tasks from a prepared still image
  - Use `create` when you only need the task id, `run` when you want the full wait-and-download flow

Examples:
  %(prog)s create "Fast drone flight" --image-url https://example.com/demo.png
  %(prog)s run "Fast drone flight" --image-url https://example.com/demo.png --output workspace/demo/videos/flight.mp4
  %(prog)s status task-001
  %(prog)s download --video-url https://cdn.example/video.mp4 --output workspace/demo/videos/final.mp4
''',
    )


def run_cli(argv: Optional[Sequence[str]] = None, *, executor=execute_parsed_command) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return executor(args)


def main(argv: Optional[Sequence[str]] = None) -> None:
    raise SystemExit(run_cli(argv))


__all__ = [
    "add_common_generation_arguments",
    "build_parser",
    "execute_parsed_command",
    "main",
    "print_result",
    "print_status",
    "request_from_args",
    "run_cli",
    "str_to_bool",
]
