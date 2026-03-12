"""Unified SlideMax command registry and dispatcher."""

from __future__ import annotations

import importlib
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"

CommandRunner = Callable[[Sequence[str]], int]


@dataclass(frozen=True)
class CommandSpec:
    """Command registry entry for the unified CLI."""

    name: str
    summary: str
    category: str
    runner: CommandRunner
    aliases: Sequence[str] = field(default_factory=tuple)
    help_args: Sequence[str] = field(default_factory=lambda: ("--help",))


@contextmanager
def _temporary_argv(argv: Sequence[str]) -> Iterable[None]:
    original = sys.argv[:]
    sys.argv = list(argv)
    try:
        yield
    finally:
        sys.argv = original


def _coerce_exit_code(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, bool):
        return int(value)
    return 1


def _normalize_command_name(name: str) -> str:
    return name.strip().replace("-", "_")


def _run_imported_callable(
    module_name: str,
    attr_name: str,
    argv: Sequence[str],
    *,
    pass_argv: bool,
    program_name: str,
) -> int:
    module = importlib.import_module(module_name)
    target = getattr(module, attr_name)

    try:
        if pass_argv:
            result = target(list(argv))
        else:
            with _temporary_argv([program_name, *argv]):
                result = target()
    except SystemExit as error:
        return _coerce_exit_code(error.code)

    return _coerce_exit_code(result)


def _build_main_runner(module_name: str, attr_name: str = "main") -> CommandRunner:
    def runner(argv: Sequence[str]) -> int:
        return _run_imported_callable(
            module_name,
            attr_name,
            argv,
            pass_argv=False,
            program_name=module_name.rsplit(".", 1)[-1],
        )

    return runner


def _build_run_cli_runner(module_name: str, attr_name: str = "run_cli") -> CommandRunner:
    def runner(argv: Sequence[str]) -> int:
        return _run_imported_callable(
            module_name,
            attr_name,
            argv,
            pass_argv=True,
            program_name=module_name.rsplit(".", 1)[-1],
        )

    return runner


def _run_image_generate(argv: Sequence[str]) -> int:
    module = importlib.import_module("slidemax.image_generation")
    parser = module.build_parser(
        description="Generate images using the configured SlideMax provider.",
        default_provider="gemini",
        default_prompt="Generate image",
        include_provider_argument=True,
        prog="python3 skills/slidemax_workflow/scripts/slidemax.py image_generate",
        epilog="""
When to use:
  - Use this as the default AI image generation entrypoint
  - Use `--list-providers` to inspect supported providers before choosing one
  - Use `--output` to keep generated images inside the current project

Provider guidance:
  - gemini: default general-purpose path
  - doubao: use when ARK or Seedream models are configured
  - openai-compatible: use for OpenAI-style image APIs

Examples:
  %(prog)s "Minimal geometric business background" --provider gemini --aspect-ratio 16:9 --output workspace/demo/images
  %(prog)s "Product hero shot" --provider doubao --model doubao-seedream-5 --image-size 2K --output workspace/demo/images
  %(prog)s --list-providers
""",
    )
    args = parser.parse_args(list(argv))
    return _coerce_exit_code(module.run_cli(args))


def _run_smoke_test_image_provider(argv: Sequence[str]) -> int:
    module = importlib.import_module("slidemax.image_generation")
    parser = module.build_smoke_test_parser(
        prog="python3 skills/slidemax_workflow/scripts/slidemax.py smoke_test_image_provider"
    )
    args = parser.parse_args(list(argv))
    return _coerce_exit_code(module.run_smoke_test_cli(args))


def _build_external_runner(executable: str, script_path: Path) -> CommandRunner:
    def runner(argv: Sequence[str]) -> int:
        completed = subprocess.run([executable, str(script_path), *argv], check=False)
        return completed.returncode

    return runner


def build_registry() -> Dict[str, CommandSpec]:
    """Return the default command registry."""

    commands = [
        CommandSpec(
            name="pdf_to_md",
            summary="Convert PDF documents to Markdown.",
            category="Source Conversion",
            runner=_build_run_cli_runner("slidemax.pdf_markdown"),
        ),
        CommandSpec(
            name="web_to_md",
            summary="Convert standard web pages to Markdown.",
            category="Source Conversion",
            runner=_build_run_cli_runner("slidemax.web_markdown"),
        ),
        CommandSpec(
            name="web_to_md_cjs",
            summary="Run the Node fallback for protected web pages.",
            category="Source Conversion",
            runner=_build_external_runner("node", SKILL_ROOT / "commands" / "web_to_md.cjs"),
            aliases=("web_to_md_js",),
        ),
        CommandSpec(
            name="project_manager",
            summary="Create, inspect, and validate SlideMax projects.",
            category="Project Management",
            runner=_build_run_cli_runner("slidemax.project_management"),
        ),
        CommandSpec(
            name="project_utils",
            summary="Inspect shared project utility helpers.",
            category="Project Management",
            runner=_build_main_runner("slidemax.project_utils"),
            help_args=(),
        ),
        CommandSpec(
            name="generate_examples_index",
            summary="Regenerate the examples index.",
            category="Project Management",
            runner=_build_run_cli_runner("slidemax.examples_index"),
        ),
        CommandSpec(
            name="analyze_images",
            summary="Analyze local image assets and export an inventory.",
            category="Image and Media",
            runner=_build_main_runner("slidemax.image_analysis"),
        ),
        CommandSpec(
            name="image_generate",
            summary="Generate images through the configured provider.",
            category="Image and Media",
            runner=_run_image_generate,
        ),
        CommandSpec(
            name="nano_banana_gen",
            summary="Run the legacy Gemini-compatible image generator.",
            category="Image and Media",
            runner=_build_run_cli_runner("slidemax.image_generation", "run_legacy_gemini_cli"),
        ),
        CommandSpec(
            name="smoke_test_image_provider",
            summary="Smoke test a live image provider configuration.",
            category="Image and Media",
            runner=_run_smoke_test_image_provider,
        ),
        CommandSpec(
            name="register_image_source",
            summary="Write provenance sidecars for local images.",
            category="Image and Media",
            runner=_build_run_cli_runner("slidemax.image_source_metadata"),
        ),
        CommandSpec(
            name="audit_image_asset",
            summary="Audit watermark and provenance risk before delivery.",
            category="Image and Media",
            runner=_build_main_runner("slidemax.asset_policy"),
        ),
        CommandSpec(
            name="register_stock_image",
            summary="Register an existing stock asset in the project manifest.",
            category="Image and Media",
            runner=_build_run_cli_runner("slidemax.stock_sources", "run_register_cli"),
        ),
        CommandSpec(
            name="download_stock_image",
            summary="Download and register a stock asset in the project manifest.",
            category="Image and Media",
            runner=_build_run_cli_runner("slidemax.stock_sources", "run_download_cli"),
        ),
        CommandSpec(
            name="rotate_images",
            summary="Rotate image assets and apply recorded fixes.",
            category="Image and Media",
            runner=_build_run_cli_runner("slidemax.image_rotation"),
        ),
        CommandSpec(
            name="doubao_i2v_task",
            summary="Create, run, and download ARK image-to-video tasks.",
            category="Image and Media",
            runner=_build_run_cli_runner("slidemax.subcommands.video_generation"),
        ),
        CommandSpec(
            name="gemini_watermark_remover",
            summary="Remove Gemini watermark assets.",
            category="Image and Media",
            runner=_build_run_cli_runner("slidemax.watermark_removal"),
        ),
        CommandSpec(
            name="finalize_svg",
            summary="Run the canonical SVG finalization workflow.",
            category="SVG Finalization and Helpers",
            runner=_build_main_runner("slidemax.finalize"),
        ),
        CommandSpec(
            name="crop_images",
            summary="Crop slice-mode image references into prepared assets.",
            category="SVG Finalization and Helpers",
            runner=_build_run_cli_runner("slidemax.subcommands.svg_asset", "run_crop_cli"),
        ),
        CommandSpec(
            name="embed_icons",
            summary="Replace icon placeholders with embedded SVG paths.",
            category="SVG Finalization and Helpers",
            runner=_build_run_cli_runner("slidemax.subcommands.svg_asset", "run_embed_icons_cli"),
        ),
        CommandSpec(
            name="fix_image_aspect",
            summary="Fix image aspect ratios for PowerPoint export.",
            category="SVG Finalization and Helpers",
            runner=_build_run_cli_runner("slidemax.subcommands.svg_asset", "run_fix_aspect_cli"),
        ),
        CommandSpec(
            name="embed_images",
            summary="Embed raster images into SVG files.",
            category="SVG Finalization and Helpers",
            runner=_build_run_cli_runner("slidemax.subcommands.svg_asset", "run_embed_images_cli"),
        ),
        CommandSpec(
            name="flatten_tspan",
            summary="Flatten tspan-based SVG text nodes.",
            category="SVG Finalization and Helpers",
            runner=_build_run_cli_runner("slidemax.subcommands.flatten_text"),
        ),
        CommandSpec(
            name="svg_rect_to_path",
            summary="Convert rounded rectangles into path geometry.",
            category="SVG Finalization and Helpers",
            runner=_build_run_cli_runner("slidemax.subcommands.rounded_rect"),
        ),
        CommandSpec(
            name="svg_position_calculator",
            summary="Calculate and validate chart-safe SVG positions.",
            category="SVG Finalization and Helpers",
            runner=_build_run_cli_runner("slidemax.subcommands.svg_position"),
        ),
        CommandSpec(
            name="svg_to_pptx",
            summary="Export SVG slides to PPTX.",
            category="Export and Validation",
            runner=_build_run_cli_runner("slidemax.pptx_export"),
        ),
        CommandSpec(
            name="svg_quality_checker",
            summary="Validate SVG compliance and compatibility.",
            category="Export and Validation",
            runner=_build_run_cli_runner("slidemax.svg_quality"),
        ),
        CommandSpec(
            name="batch_validate",
            summary="Validate multiple SlideMax outputs in one pass.",
            category="Export and Validation",
            runner=_build_run_cli_runner("slidemax.batch_validation"),
        ),
        CommandSpec(
            name="error_helper",
            summary="Explain common workflow and export errors.",
            category="Export and Validation",
            runner=_build_main_runner("slidemax.error_helper"),
        ),
        CommandSpec(
            name="setup_export_env",
            summary="Install or inspect the export environment.",
            category="Export and Validation",
            runner=_build_run_cli_runner("slidemax.export_setup"),
        ),
        CommandSpec(
            name="config",
            summary="Inspect shared configuration and canvas definitions.",
            category="Export and Validation",
            runner=_build_main_runner("slidemax.config"),
            help_args=(),
        ),
        CommandSpec(
            name="total_md_split",
            summary="Split total speaker notes into per-slide files.",
            category="Export and Validation",
            runner=_build_run_cli_runner("slidemax.notes_splitter"),
        ),
    ]

    registry: Dict[str, CommandSpec] = {}
    for command in commands:
        registry[command.name] = command
    return registry


def _aliases_for_command(command: CommandSpec) -> List[str]:
    aliases = list(command.aliases)
    hyphen_alias = command.name.replace("_", "-")
    if hyphen_alias != command.name:
        aliases.append(hyphen_alias)
    return sorted(dict.fromkeys(aliases))


def _resolve_command(
    name: str,
    registry: Mapping[str, CommandSpec],
) -> Optional[CommandSpec]:
    normalized = _normalize_command_name(name)
    if normalized in registry:
        return registry[normalized]

    for command in registry.values():
        alias_names = [command.name, *_aliases_for_command(command)]
        normalized_aliases = {_normalize_command_name(alias) for alias in alias_names}
        if normalized in normalized_aliases:
            return command
    return None


def _iter_grouped_commands(registry: Mapping[str, CommandSpec]) -> List[tuple[str, List[CommandSpec]]]:
    grouped: Dict[str, List[CommandSpec]] = {}
    for command in registry.values():
        grouped.setdefault(command.category, []).append(command)

    return [
        (category, sorted(commands, key=lambda item: item.name))
        for category, commands in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _print_help(registry: Mapping[str, CommandSpec], output_fn=print) -> None:
    output_fn("Usage:")
    output_fn("  python3 skills/slidemax_workflow/scripts/slidemax.py <command> [args...]")
    output_fn("  python3 skills/slidemax_workflow/scripts/slidemax.py list")
    output_fn("  python3 skills/slidemax_workflow/scripts/slidemax.py help <command>")
    output_fn("")
    output_fn("Commands:")
    for category, commands in _iter_grouped_commands(registry):
        output_fn(f"  {category}:")
        for command in commands:
            alias_text = ""
            aliases = _aliases_for_command(command)
            if aliases:
                alias_text = f" (aliases: {', '.join(aliases)})"
            output_fn(f"    {command.name:<26} {command.summary}{alias_text}")


def _execute_command(command: CommandSpec, argv: Sequence[str], output_fn=print) -> int:
    try:
        return command.runner(argv)
    except FileNotFoundError as error:
        output_fn(f"Missing executable: {error}")
        return 1
    except KeyboardInterrupt:
        output_fn("Interrupted.")
        return 130
    except Exception as error:  # pragma: no cover - defensive boundary
        output_fn(f"Error while executing '{command.name}': {error}")
        return 1


def run_cli(
    argv: Optional[Sequence[str]] = None,
    *,
    registry: Optional[Mapping[str, CommandSpec]] = None,
    output_fn=print,
) -> int:
    """Execute the unified CLI with the provided arguments."""

    args = list(argv) if argv is not None else sys.argv[1:]
    command_registry = dict(build_registry() if registry is None else registry)

    if not args or args[0] in {"-h", "--help"}:
        _print_help(command_registry, output_fn=output_fn)
        return 0

    if args[0] == "list":
        _print_help(command_registry, output_fn=output_fn)
        return 0

    if args[0] == "help":
        if len(args) < 2:
            _print_help(command_registry, output_fn=output_fn)
            return 0
        command = _resolve_command(args[1], command_registry)
        if command is None:
            output_fn(f"Unknown command: {args[1]}")
            return 2
        return _execute_command(command, list(command.help_args), output_fn=output_fn)

    command = _resolve_command(args[0], command_registry)
    if command is None:
        output_fn(f"Unknown command: {args[0]}")
        output_fn("")
        _print_help(command_registry, output_fn=output_fn)
        return 2

    return _execute_command(command, args[1:], output_fn=output_fn)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Console entrypoint for the unified CLI."""

    return run_cli(argv)


__all__ = [
    "CommandSpec",
    "SCRIPTS_DIR",
    "build_registry",
    "main",
    "run_cli",
]
