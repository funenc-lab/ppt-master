import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PROJECT_ROOT / "skills" / "slidemax_workflow"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from slidemax.layout_quality import LayoutQualityChecker, summarize_layout_target


class LayoutQualityCheckerTestCase(unittest.TestCase):
    def test_checker_allows_low_opacity_decorative_bleed_text(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#1F2937" />
  <text x="1100" y="500" font-size="400" font-weight="700" text-anchor="middle" fill="#FFFFFF" fill-opacity="0.05">01</text>
  <text x="280" y="350" font-size="48" fill="#FFFFFF">Section Title</text>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "section.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertTrue(result["passed"], result)

    def test_checker_allows_low_opacity_decorative_bleed_circle(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#1F2937" />
  <circle cx="150" cy="150" r="220" fill="#FFFFFF" opacity="0.05" />
  <text x="640" y="140" font-size="42" text-anchor="middle" fill="#FFFFFF">CTA</text>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "slide_10_cta.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertTrue(result["passed"], result)

    def test_checker_allows_low_opacity_decorative_overlay_on_footer(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#1F2937" />
  <text x="1240" y="690" text-anchor="end" font-size="14" fill="#FFFFFF">17 / 17</text>
  <path d="M1280 720 L1280 600 Q1220 600 1220 660 L1220 720 Z" fill="#C41E3A" opacity="0.2" />
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "footer.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertTrue(result["passed"], result)

    def test_checker_allows_inherited_low_opacity_decorative_bleed_circle(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#1F2937" />
  <g opacity="0.1">
    <circle cx="80" cy="80" r="120" fill="none" stroke="#FFFFFF" stroke-width="1" />
  </g>
  <text x="640" y="140" font-size="42" text-anchor="middle" fill="#FFFFFF">CTA</text>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "inherited_circle.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertTrue(result["passed"], result)

    def test_checker_allows_inherited_low_opacity_footer_overlay(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#1F2937" />
  <text x="1240" y="690" text-anchor="end" font-size="14" fill="#FFFFFF" opacity="0.5">17 / 17</text>
  <g opacity="0.2">
    <rect x="1160" y="660" width="120" height="60" fill="#C41E3A" />
  </g>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "footer_group.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertTrue(result["passed"], result)

    def test_checker_allows_inline_tspans_without_false_overlap(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#F8FAFC" />
  <text x="600" y="75" text-anchor="middle" font-size="15" fill="#0F172A">
    <tspan>Alpha</tspan>
    <tspan fill="#16A34A" font-weight="600">Beta</tspan>
    <tspan>Gamma</tspan>
  </text>
  <text x="600" y="95" text-anchor="middle" font-size="15" fill="#334155">
    <tspan>Delta content stays on a separate line.</tspan>
  </text>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "inline_tspans.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertTrue(result["passed"], result)

    def test_checker_allows_low_opacity_background_section_number(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#1E293B" />
  <text x="640" y="360" text-anchor="middle" font-size="16" fill="#FFFFFF" fill-opacity="0.24">Body Self</text>
  <text x="640" y="430" text-anchor="middle" font-size="120" font-weight="700" fill="#FFFFFF" fill-opacity="0.15">03</text>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "section_number.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertTrue(result["passed"], result)

    def test_checker_allows_low_opacity_decorative_code_symbol(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#0D1117" />
  <text x="1000" y="520" font-size="100" opacity="0.25" fill="#8B949E">/*</text>
  <text x="980" y="520" font-size="16" fill="#8B949E">06 Test Log</text>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "code_symbol.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertTrue(result["passed"], result)

    def test_checker_allows_compact_numeric_value_with_unit(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#F8FAFC" />
  <text x="685" y="225" font-size="42" font-weight="700" fill="#0F172A">44.81</text>
  <text x="790" y="225" font-size="14" fill="#475569">%</text>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "numeric_unit.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertTrue(result["passed"], result)

    def test_checker_allows_low_opacity_circle_bleed_at_twelve_percent(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <rect width="1280" height="720" fill="#F8FAFC" />
  <circle cx="80" cy="80" r="120" fill="#1A5F9E" opacity="0.12" />
  <text x="640" y="360" text-anchor="middle" font-size="40" fill="#0F172A">Cover Title</text>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "decorative_circle.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertTrue(result["passed"], result)

    def test_checker_allows_gradient_glow_ellipse_bleed(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#C2410C;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#C2410C;stop-opacity:0" />
    </radialGradient>
  </defs>
  <rect width="1280" height="720" fill="#0F172A" />
  <ellipse cx="1100" cy="150" rx="300" ry="200" fill="url(#glow)" opacity="0.4" />
  <text x="640" y="360" text-anchor="middle" font-size="40" fill="#FFFFFF">Cover Title</text>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "glow_ellipse.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertTrue(result["passed"], result)

    def test_checker_detects_overlapping_text_blocks(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <text x="120" y="120" font-size="40">Alpha headline</text>
  <text x="125" y="128" font-size="40">Beta headline</text>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "slide_01_cover.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertFalse(result["passed"], result)
        self.assertTrue(any("overlap" in error.lower() for error in result["errors"]), result)

    def test_checker_detects_text_covered_by_later_shape(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <text x="120" y="120" font-size="36">Covered text</text>
  <rect x="90" y="80" width="260" height="70" fill="#FFFFFF" />
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "slide_01_cover.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertFalse(result["passed"], result)
        self.assertTrue(any("covered" in error.lower() for error in result["errors"]), result)

    def test_checker_detects_text_overflowing_canvas(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <text x="1180" y="120" font-size="40">Overflowing title block</text>
</svg>
"""

        with tempfile.TemporaryDirectory() as tmp:
            svg_file = Path(tmp) / "slide_01_cover.svg"
            svg_file.write_text(svg, encoding="utf-8")

            result = LayoutQualityChecker().check_file(svg_file)

        self.assertFalse(result["passed"], result)
        self.assertTrue(any("outside" in error.lower() for error in result["errors"]), result)

    def test_summarize_layout_target_checks_svg_final_directory(self):
        clean_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" '
            'width="1280" height="720"><text x="120" y="120" font-size="32">OK</text></svg>'
        )
        bad_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" '
            'width="1280" height="720"><text x="120" y="120" font-size="40">Alpha</text>'
            '<text x="122" y="126" font-size="40">Beta</text></svg>'
        )

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "demo_ppt169_20260313"
            (project / "svg_output").mkdir(parents=True)
            (project / "svg_final").mkdir()
            (project / "svg_output" / "slide_01_cover.svg").write_text(clean_svg, encoding="utf-8")
            (project / "svg_final" / "slide_01_cover.svg").write_text(bad_svg, encoding="utf-8")

            summary = summarize_layout_target(project, expected_format="ppt169", prefer_finalized=True)

        self.assertEqual(summary.stage_name, "svg_final")
        self.assertEqual(summary.total, 1)
        self.assertEqual(summary.errors, 1)
        self.assertFalse(summary.is_compatible)


if __name__ == "__main__":
    unittest.main()
