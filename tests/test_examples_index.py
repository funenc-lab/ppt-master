import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PROJECT_ROOT / "skills" / "slidemax_workflow"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from slidemax.examples_index import CANONICAL_CLI, build_render_context


class ExamplesIndexTestCase(unittest.TestCase):
    def test_build_render_context_uses_unified_cli_inside_repo(self):
        context = build_render_context(SKILL_ROOT / "examples")

        self.assertIn("scripts/slidemax.py", context.command_reference)
        self.assertIn("scripts/slidemax.py", context.project_manager_command)
        self.assertIn("project_manager init", context.project_manager_command)
        self.assertIn("generate_examples_index", context.update_command)
        self.assertNotIn("commands/project_manager.py", context.project_manager_command)
        self.assertNotIn("commands/generate_examples_index.py", context.update_command)

    def test_build_render_context_uses_unified_cli_for_external_examples_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            context = build_render_context(Path(tmp))

        self.assertEqual(context.command_reference, str(CANONICAL_CLI))
        self.assertIn("project_manager validate", context.validate_command)
        self.assertIn("generate_examples_index", context.update_command)


if __name__ == "__main__":
    unittest.main()
