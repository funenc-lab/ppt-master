import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PROJECT_ROOT / "skills" / "slidemax_workflow"
COMMANDS_DIR = SKILL_ROOT / "commands"
SLIDEMAX_DIR = SKILL_ROOT / "slidemax"
SUBCOMMANDS_DIR = SLIDEMAX_DIR / "subcommands"
UNIFIED_CLI = SKILL_ROOT / "scripts" / "slidemax.py"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from slidemax.cli import CommandSpec, build_registry, run_cli


class SlideMaxCliTestCase(unittest.TestCase):
    def _run_help(self, command_name: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(UNIFIED_CLI), "help", command_name],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_registry_covers_historical_command_surface(self):
        registry_names = set(build_registry().keys())
        expected = {
            "analyze_images",
            "audit_image_asset",
            "batch_validate",
            "config",
            "crop_images",
            "doubao_i2v_task",
            "download_stock_image",
            "embed_icons",
            "embed_images",
            "error_helper",
            "finalize_svg",
            "fix_image_aspect",
            "flatten_tspan",
            "gemini_watermark_remover",
            "generate_examples_index",
            "image_generate",
            "layout_quality_checker",
            "nano_banana_gen",
            "pdf_to_md",
            "project_manager",
            "project_utils",
            "register_image_source",
            "register_stock_image",
            "rotate_images",
            "setup_export_env",
            "smoke_test_image_provider",
            "svg_position_calculator",
            "svg_quality_checker",
            "svg_rect_to_path",
            "svg_to_pptx",
            "total_md_split",
            "web_to_md",
            "web_to_md_cjs",
        }

        self.assertSetEqual(registry_names, expected)

    def test_commands_directory_has_no_python_entrypoints(self):
        python_entrypoints = sorted(path.name for path in COMMANDS_DIR.glob("*.py"))
        self.assertEqual(python_entrypoints, [])

    def test_cli_adapter_modules_live_under_subcommands_only(self):
        legacy_cli_modules = sorted(
            path.name
            for path in SLIDEMAX_DIR.glob("*_cli.py")
            if path.name in {
                "flatten_text_cli.py",
                "rounded_rect_cli.py",
                "svg_asset_cli.py",
                "svg_position_cli.py",
                "video_generation_cli.py",
            }
        )
        self.assertEqual(legacy_cli_modules, [])

        expected_subcommands = {
            "flatten_text.py",
            "rounded_rect.py",
            "svg_asset.py",
            "svg_position.py",
            "video_generation.py",
        }
        actual_subcommands = {
            path.name
            for path in SUBCOMMANDS_DIR.glob("*.py")
            if path.name != "__init__.py"
        }
        self.assertTrue(expected_subcommands.issubset(actual_subcommands))

    def test_run_cli_prints_help_when_no_command_is_given(self):
        outputs = []
        registry = {
            "demo": CommandSpec(
                name="demo",
                summary="Demo command",
                category="Examples",
                runner=lambda argv: 0,
            )
        }

        exit_code = run_cli([], registry=registry, output_fn=outputs.append)

        self.assertEqual(exit_code, 0)
        rendered = "\n".join(outputs)
        self.assertIn("Usage:", rendered)
        self.assertIn("demo", rendered)

    def test_run_cli_dispatches_registered_alias(self):
        calls = []
        registry = {
            "demo": CommandSpec(
                name="demo",
                summary="Demo command",
                category="Examples",
                aliases=("demo-command",),
                runner=lambda argv: calls.append(list(argv)) or 0,
            )
        }

        exit_code = run_cli(["demo-command", "--flag"], registry=registry)

        self.assertEqual(exit_code, 0)
        self.assertEqual(calls, [["--flag"]])

    def test_run_cli_supports_help_subcommand(self):
        calls = []
        registry = {
            "demo": CommandSpec(
                name="demo",
                summary="Demo command",
                category="Examples",
                runner=lambda argv: calls.append(list(argv)) or 0,
            )
        }

        exit_code = run_cli(["help", "demo"], registry=registry)

        self.assertEqual(exit_code, 0)
        self.assertEqual(calls, [["--help"]])

    def test_run_cli_supports_custom_help_arguments(self):
        calls = []
        registry = {
            "demo": CommandSpec(
                name="demo",
                summary="Demo command",
                category="Examples",
                runner=lambda argv: calls.append(list(argv)) or 0,
                help_args=(),
            )
        }

        exit_code = run_cli(["help", "demo"], registry=registry)

        self.assertEqual(exit_code, 0)
        self.assertEqual(calls, [[]])

    def test_run_cli_reports_unknown_command(self):
        outputs = []

        exit_code = run_cli(["missing"], registry={}, output_fn=outputs.append)

        self.assertEqual(exit_code, 2)
        self.assertIn("Unknown command", "\n".join(outputs))

    def test_unified_cli_help_works_for_web_to_md_cjs(self):
        completed = self._run_help("web_to_md_cjs")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("Usage:", completed.stdout)
        self.assertIn("web_to_md_cjs", completed.stdout)
        self.assertNotIn("Maximum call stack size exceeded", completed.stderr)

    def test_unified_cli_help_for_project_manager_uses_canonical_examples(self):
        completed = self._run_help("project_manager")

        self.assertEqual(completed.returncode, 0)
        self.assertIn(
            "python3 skills/slidemax_workflow/scripts/slidemax.py project_manager init",
            completed.stdout,
        )
        self.assertIn("When to use:", completed.stdout)

    def test_unified_cli_help_for_finalize_svg_uses_canonical_examples(self):
        completed = self._run_help("finalize_svg")

        self.assertEqual(completed.returncode, 0)
        self.assertIn(
            "python3 skills/slidemax_workflow/scripts/slidemax.py finalize_svg",
            completed.stdout,
        )
        self.assertIn("When to use:", completed.stdout)

    def test_unified_cli_help_for_svg_to_pptx_uses_canonical_examples(self):
        completed = self._run_help("svg_to_pptx")

        self.assertEqual(completed.returncode, 0)
        self.assertIn(
            "python3 skills/slidemax_workflow/scripts/slidemax.py svg_to_pptx",
            completed.stdout,
        )
        self.assertIn("When to use:", completed.stdout)

    def test_unified_cli_help_for_image_generate_includes_examples_and_provider_guidance(self):
        completed = self._run_help("image_generate")

        self.assertEqual(completed.returncode, 0)
        self.assertIn(
            "python3 skills/slidemax_workflow/scripts/slidemax.py image_generate",
            completed.stdout,
        )
        self.assertIn("When to use:", completed.stdout)
        self.assertIn("--list-providers", completed.stdout)

    def test_all_command_help_outputs_use_canonical_entry_and_minimum_guidance(self):
        registry_names = sorted(build_registry().keys())
        guidance_tokens = ("When to use:", "Usage:", "用法:", "Examples:")

        for command_name in registry_names:
            with self.subTest(command=command_name):
                completed = self._run_help(command_name)
                self.assertEqual(completed.returncode, 0)
                self.assertIn(
                    "python3 skills/slidemax_workflow/scripts/slidemax.py",
                    completed.stdout,
                )
                self.assertTrue(
                    any(token in completed.stdout for token in guidance_tokens),
                    msg=f"missing guidance tokens for {command_name}",
                )


if __name__ == "__main__":
    unittest.main()
