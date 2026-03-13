"""Layout quality checks for finalized SlideMax SVG slides."""

from __future__ import annotations

import argparse
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence
from xml.etree import ElementTree as ET

from .config import EXTRA_EXAMPLE_PATHS_ENV, get_example_dirs
from .project_utils import CANVAS_FORMATS, find_all_projects

SVG_NS = "http://www.w3.org/2000/svg"
TRANSLATE_RE = re.compile(r"translate\(\s*([-+]?\d*\.?\d+)(?:[\s,]+([-+]?\d*\.?\d+))?\s*\)")
NUMBER_RE = re.compile(r"[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][-+]?\d+)?")


@dataclass(frozen=True)
class BBox:
    """Axis-aligned bounding box in SVG canvas coordinates."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @property
    def width(self) -> float:
        return max(0.0, self.x_max - self.x_min)

    @property
    def height(self) -> float:
        return max(0.0, self.y_max - self.y_min)

    @property
    def area(self) -> float:
        return self.width * self.height

    def intersects(self, other: "BBox") -> bool:
        return not (
            self.x_max <= other.x_min
            or self.x_min >= other.x_max
            or self.y_max <= other.y_min
            or self.y_min >= other.y_max
        )

    def intersection_area(self, other: "BBox") -> float:
        if not self.intersects(other):
            return 0.0
        x_min = max(self.x_min, other.x_min)
        y_min = max(self.y_min, other.y_min)
        x_max = min(self.x_max, other.x_max)
        y_max = min(self.y_max, other.y_max)
        return max(0.0, x_max - x_min) * max(0.0, y_max - y_min)

    def translated(self, dx: float, dy: float) -> "BBox":
        return BBox(
            x_min=self.x_min + dx,
            y_min=self.y_min + dy,
            x_max=self.x_max + dx,
            y_max=self.y_max + dy,
        )


@dataclass(frozen=True)
class LayoutNode:
    """Extracted layout primitive used for overlap checks."""

    kind: str
    tag: str
    bbox: BBox
    order: int
    label: str
    opaque: bool
    opacity: float
    font_size: float
    fill: str


@dataclass(frozen=True)
class LayoutTargetSummary:
    """Aggregated layout summary for a checked target."""

    target_path: str
    checked_path: str
    stage_name: str
    total: int
    clean: int
    errors: int

    @property
    def is_compatible(self) -> bool:
        return self.total > 0 and self.errors == 0


def _local_name(tag: str) -> str:
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _parse_float(value: Optional[str], default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _has_visible_fill(element: ET.Element) -> bool:
    tag = _local_name(element.tag)
    fill = (element.attrib.get("fill") or "").strip().lower()
    if fill == "none":
        return False
    if tag == "text":
        return True
    return fill != ""


def _has_visible_stroke(element: ET.Element) -> bool:
    stroke = (element.attrib.get("stroke") or "").strip().lower()
    return stroke not in {"", "none"}


def _parse_opacity(element: ET.Element, parent_opacity: float = 1.0) -> float:
    opacity = _parse_float(element.attrib.get("opacity"), 1.0)
    fill_opacity = _parse_float(element.attrib.get("fill-opacity"), 1.0)
    stroke_opacity = _parse_float(element.attrib.get("stroke-opacity"), 1.0)

    paint_alpha = 0.0
    if _has_visible_fill(element):
        paint_alpha = max(paint_alpha, fill_opacity)
    if _has_visible_stroke(element):
        paint_alpha = max(paint_alpha, stroke_opacity)

    if paint_alpha <= 0.0:
        paint_alpha = fill_opacity

    return parent_opacity * opacity * paint_alpha


def _is_opaque_shape(element: ET.Element, effective_opacity: float) -> bool:
    fill = (element.attrib.get("fill") or "").strip().lower()
    if fill in {"", "none"}:
        return False
    return effective_opacity > 0.05


def _allows_decorative_bleed(node: LayoutNode) -> bool:
    """Return whether a node is a low-visibility decorative shape allowed to bleed."""

    if node.kind == "text":
        label = node.label.strip()
        if node.opacity <= 0.18 and node.font_size >= 100:
            return True
        if node.opacity <= 0.30 and re.fullmatch(r"[\W_/<>{}\[\];:=+*#|\\-]{1,6}", label):
            return True
        return False
    if node.kind != "shape":
        return False
    if node.tag not in {"circle", "ellipse"}:
        return False
    fill = node.fill.strip().lower()
    if fill.startswith("url(") and (node.bbox.width >= 300 or node.bbox.height >= 200):
        return True
    return node.opacity <= 0.12


def _is_low_visibility_shape(node: LayoutNode) -> bool:
    """Return whether a shape is too faint to count as content coverage."""

    return node.kind == "shape" and node.opacity <= 0.25


def _looks_numeric_label(label: str) -> bool:
    compact = "".join(label.split())
    return bool(re.fullmatch(r"[\d,]+(?:\.\d+)?", compact))


def _looks_unit_suffix(label: str) -> bool:
    compact = "".join(label.split())
    return bool(re.fullmatch(r"(?:%|‰|bp|x|倍|亿|万|元|人|亿元|万元|元/人)", compact))


def _is_compact_numeric_suffix_pair(current: LayoutNode, other: LayoutNode) -> bool:
    larger, smaller = (current, other) if current.font_size >= other.font_size else (other, current)
    if larger.font_size <= 0 or smaller.font_size <= 0:
        return False
    if smaller.font_size > larger.font_size * 0.5:
        return False
    if not _looks_numeric_label(larger.label):
        return False
    if not _looks_unit_suffix(smaller.label):
        return False
    return abs(current.bbox.y_max - other.bbox.y_max) <= max(6.0, larger.font_size * 0.3)


def _axis_overlap_ratio(start_a: float, end_a: float, start_b: float, end_b: float) -> float:
    overlap = max(0.0, min(end_a, end_b) - max(start_a, start_b))
    span = min(max(0.0, end_a - start_a), max(0.0, end_b - start_b))
    if span <= 0:
        return 0.0
    return overlap / span


def _measure_text_width(text: str, font_size: float) -> float:
    width = 0.0
    for char in text:
        if char.isspace():
            width += font_size * 0.32
            continue
        category = unicodedata.category(char)
        east_width = unicodedata.east_asian_width(char)
        if east_width in {"W", "F"}:
            width += font_size * 1.0
        elif category.startswith("P"):
            width += font_size * 0.38
        elif ord(char) > 0xFFFF:
            width += font_size * 1.0
        else:
            width += font_size * 0.56
    return width


def _parse_translate(transform: Optional[str]) -> tuple[float, float]:
    if not transform:
        return 0.0, 0.0
    dx = 0.0
    dy = 0.0
    for match in TRANSLATE_RE.finditer(transform):
        dx += _parse_float(match.group(1))
        dy += _parse_float(match.group(2))
    return dx, dy


def _resolve_canvas_size(root: ET.Element, expected_format: Optional[str]) -> tuple[float, float]:
    viewbox = root.attrib.get("viewBox")
    if viewbox:
        parts = viewbox.split()
        if len(parts) == 4:
            return _parse_float(parts[2], 1280.0), _parse_float(parts[3], 720.0)
    if expected_format and expected_format in CANVAS_FORMATS:
        parts = CANVAS_FORMATS[expected_format]["viewbox"].split()
        return _parse_float(parts[2], 1280.0), _parse_float(parts[3], 720.0)
    return _parse_float(root.attrib.get("width"), 1280.0), _parse_float(root.attrib.get("height"), 720.0)


def _iter_text_lines(element: ET.Element) -> List[str]:
    tspans = [child for child in list(element) if _local_name(child.tag) == "tspan"]
    if tspans:
        lines: List[List[str]] = []
        current_line: List[str] = []
        previous_x: Optional[float] = None
        previous_y: Optional[float] = None

        for child in tspans:
            text = " ".join("".join(child.itertext()).split())
            if not text:
                continue

            child_x_attr = child.attrib.get("x")
            child_y_attr = child.attrib.get("y")
            child_dy_attr = child.attrib.get("dy")
            child_x = _parse_float(child_x_attr) if child_x_attr is not None else None
            child_y = _parse_float(child_y_attr) if child_y_attr is not None else None
            child_dy = _parse_float(child_dy_attr) if child_dy_attr is not None else 0.0

            starts_new_line = False
            if current_line:
                if child_y is not None and previous_y is not None and abs(child_y - previous_y) > 0.5:
                    starts_new_line = True
                elif child_dy_attr is not None and abs(child_dy) > 0.5:
                    starts_new_line = True
                elif child_x is not None and previous_x is not None and child_x < previous_x - 1.0:
                    starts_new_line = True

            if starts_new_line:
                lines.append(current_line)
                current_line = []

            current_line.append(text)
            if child_x is not None:
                previous_x = child_x
            if child_y is not None:
                previous_y = child_y

        if current_line:
            lines.append(current_line)

        return [" ".join(parts) for parts in lines if parts]
    text = " ".join("".join(element.itertext()).split())
    return [text] if text else []


def _text_bbox(element: ET.Element, dx: float, dy: float) -> Optional[BBox]:
    lines = _iter_text_lines(element)
    if not lines:
        return None

    font_size = _parse_float(element.attrib.get("font-size"), 16.0)
    line_height = font_size * 1.2
    anchor = (element.attrib.get("text-anchor") or "start").strip().lower()
    base_x = _parse_float(element.attrib.get("x"), 0.0)
    base_y = _parse_float(element.attrib.get("y"), 0.0)
    line_width = max(_measure_text_width(line, font_size) for line in lines)
    total_height = font_size + line_height * max(0, len(lines) - 1)

    x_min = base_x
    if anchor == "middle":
        x_min = base_x - line_width / 2
    elif anchor == "end":
        x_min = base_x - line_width

    y_min = base_y - font_size * 0.8
    bbox = BBox(
        x_min=x_min,
        y_min=y_min,
        x_max=x_min + line_width,
        y_max=y_min + total_height,
    )
    return bbox.translated(dx, dy)


def _rect_like_bbox(element: ET.Element, dx: float, dy: float) -> Optional[BBox]:
    tag = _local_name(element.tag)
    if tag in {"rect", "image"}:
        x = _parse_float(element.attrib.get("x"))
        y = _parse_float(element.attrib.get("y"))
        width = _parse_float(element.attrib.get("width"))
        height = _parse_float(element.attrib.get("height"))
        return BBox(x, y, x + width, y + height).translated(dx, dy)
    if tag == "circle":
        cx = _parse_float(element.attrib.get("cx"))
        cy = _parse_float(element.attrib.get("cy"))
        radius = _parse_float(element.attrib.get("r"))
        return BBox(cx - radius, cy - radius, cx + radius, cy + radius).translated(dx, dy)
    if tag == "ellipse":
        cx = _parse_float(element.attrib.get("cx"))
        cy = _parse_float(element.attrib.get("cy"))
        rx = _parse_float(element.attrib.get("rx"))
        ry = _parse_float(element.attrib.get("ry"))
        return BBox(cx - rx, cy - ry, cx + rx, cy + ry).translated(dx, dy)
    return None


def _points_bbox(points: str, dx: float, dy: float) -> Optional[BBox]:
    numbers = [float(token) for token in NUMBER_RE.findall(points)]
    if len(numbers) < 4:
        return None
    xs = numbers[0::2]
    ys = numbers[1::2]
    return BBox(min(xs), min(ys), max(xs), max(ys)).translated(dx, dy)


def _path_bbox(path_data: str, dx: float, dy: float) -> Optional[BBox]:
    tokens = re.findall(r"[A-Za-z]|[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][-+]?\d+)?", path_data)
    if not tokens:
        return None

    x = 0.0
    y = 0.0
    start_x = 0.0
    start_y = 0.0
    xs: List[float] = []
    ys: List[float] = []
    command = ""
    index = 0

    def add_point(px: float, py: float) -> None:
        xs.append(px)
        ys.append(py)

    while index < len(tokens):
        token = tokens[index]
        if re.fullmatch(r"[A-Za-z]", token):
            command = token
            index += 1
            if command in {"Z", "z"}:
                x = start_x
                y = start_y
                add_point(x, y)
            continue

        lower = command.lower()
        relative = command.islower()

        def read_number() -> float:
            nonlocal index
            value = float(tokens[index])
            index += 1
            return value

        if lower == "m":
            nx = read_number()
            ny = read_number()
            if relative:
                x += nx
                y += ny
            else:
                x, y = nx, ny
            start_x, start_y = x, y
            add_point(x, y)
            command = "l" if relative else "L"
        elif lower in {"l", "t"}:
            nx = read_number()
            ny = read_number()
            if relative:
                x += nx
                y += ny
            else:
                x, y = nx, ny
            add_point(x, y)
        elif lower == "h":
            nx = read_number()
            x = x + nx if relative else nx
            add_point(x, y)
        elif lower == "v":
            ny = read_number()
            y = y + ny if relative else ny
            add_point(x, y)
        elif lower in {"c"}:
            values = [read_number() for _ in range(6)]
            points = list(zip(values[0::2], values[1::2]))
            for px, py in points:
                abs_x = x + px if relative else px
                abs_y = y + py if relative else py
                add_point(abs_x, abs_y)
            end_x, end_y = points[-1]
            x = x + end_x if relative else end_x
            y = y + end_y if relative else end_y
        elif lower in {"s", "q"}:
            values = [read_number() for _ in range(4)]
            points = list(zip(values[0::2], values[1::2]))
            for px, py in points:
                abs_x = x + px if relative else px
                abs_y = y + py if relative else py
                add_point(abs_x, abs_y)
            end_x, end_y = points[-1]
            x = x + end_x if relative else end_x
            y = y + end_y if relative else end_y
        elif lower == "a":
            values = [read_number() for _ in range(7)]
            end_x = values[5]
            end_y = values[6]
            x = x + end_x if relative else end_x
            y = y + end_y if relative else end_y
            add_point(x, y)
        else:
            index += 1

    if not xs or not ys:
        return None
    return BBox(min(xs), min(ys), max(xs), max(ys)).translated(dx, dy)


def _extract_nodes(root: ET.Element) -> List[LayoutNode]:
    nodes: List[LayoutNode] = []
    order = 0

    def visit(element: ET.Element, parent_dx: float, parent_dy: float, parent_opacity: float) -> None:
        nonlocal order
        if not isinstance(element.tag, str):
            return
        tag = _local_name(element.tag)
        dx, dy = _parse_translate(element.attrib.get("transform"))
        total_dx = parent_dx + dx
        total_dy = parent_dy + dy
        opacity = _parse_opacity(element, parent_opacity)

        bbox: Optional[BBox] = None
        kind: Optional[str] = None
        label = tag
        opaque = False
        font_size = 0.0
        fill = element.attrib.get("fill", "")

        if tag == "text":
            bbox = _text_bbox(element, total_dx, total_dy)
            kind = "text"
            label = " ".join(_iter_text_lines(element))[:80] or "text"
            font_size = _parse_float(element.attrib.get("font-size"), 16.0)
        elif tag in {"rect", "image", "circle", "ellipse"}:
            bbox = _rect_like_bbox(element, total_dx, total_dy)
            kind = "shape"
            opaque = _is_opaque_shape(element, opacity)
        elif tag in {"polygon", "polyline"}:
            bbox = _points_bbox(element.attrib.get("points", ""), total_dx, total_dy)
            kind = "shape"
            opaque = _is_opaque_shape(element, opacity)
        elif tag == "path":
            bbox = _path_bbox(element.attrib.get("d", ""), total_dx, total_dy)
            kind = "shape"
            opaque = _is_opaque_shape(element, opacity)

        if kind and bbox and bbox.area > 0:
            nodes.append(
                LayoutNode(
                    kind=kind,
                    tag=tag,
                    bbox=bbox,
                    order=order,
                    label=label,
                    opaque=opaque,
                    opacity=opacity,
                    font_size=font_size,
                    fill=fill,
                )
            )
            order += 1

        for child in list(element):
            visit(child, total_dx, total_dy, opacity)

    visit(root, 0.0, 0.0, 1.0)
    return nodes


class LayoutQualityChecker:
    """Detect obvious layout collisions in finalized SlideMax SVG slides."""

    def __init__(self) -> None:
        self.results: List[Dict[str, object]] = []
        self.summary = {"total": 0, "passed": 0, "errors": 0}

    def check_file(self, svg_file: str | Path, expected_format: Optional[str] = None) -> Dict[str, object]:
        svg_path = Path(svg_file)
        result: Dict[str, object] = {
            "file": svg_path.name,
            "path": str(svg_path),
            "exists": svg_path.exists(),
            "errors": [],
            "passed": True,
        }

        if not svg_path.exists():
            result["errors"].append("File does not exist.")
            result["passed"] = False
            self._record_result(result)
            return result

        try:
            root = ET.fromstring(svg_path.read_text(encoding="utf-8"))
            canvas_width, canvas_height = _resolve_canvas_size(root, expected_format)
            nodes = _extract_nodes(root)
            result["errors"].extend(self._collect_canvas_overflow_errors(nodes, canvas_width, canvas_height))
            result["errors"].extend(self._collect_text_overlap_errors(nodes))
            result["errors"].extend(self._collect_text_covered_errors(nodes))
            result["passed"] = len(result["errors"]) == 0
        except Exception as exc:
            result["errors"].append(f"Failed to inspect layout: {exc}")
            result["passed"] = False

        self._record_result(result)
        return result

    def check_directory(self, target: str | Path, expected_format: Optional[str] = None) -> None:
        _, _, svg_files = _resolve_layout_target(target, prefer_finalized=True)
        for svg_file in svg_files:
            self.check_file(svg_file, expected_format)

    def _record_result(self, result: Dict[str, object]) -> None:
        self.summary["total"] += 1
        if result["passed"]:
            self.summary["passed"] += 1
        else:
            self.summary["errors"] += 1
        self.results.append(result)

    def _collect_canvas_overflow_errors(
        self,
        nodes: Iterable[LayoutNode],
        canvas_width: float,
        canvas_height: float,
    ) -> List[str]:
        errors: List[str] = []
        tolerance = 2.0
        for node in nodes:
            bbox = node.bbox
            if _allows_decorative_bleed(node):
                continue
            if (
                bbox.x_min < -tolerance
                or bbox.y_min < -tolerance
                or bbox.x_max > canvas_width + tolerance
                or bbox.y_max > canvas_height + tolerance
            ):
                errors.append(
                    f"Detected {node.kind} element outside the canvas bounds: {node.label}"
                )
                break
        return errors

    def _collect_text_overlap_errors(self, nodes: Iterable[LayoutNode]) -> List[str]:
        text_nodes = [node for node in nodes if node.kind == "text"]
        errors: List[str] = []
        for index, current in enumerate(text_nodes):
            if _allows_decorative_bleed(current):
                continue
            for other in text_nodes[index + 1 :]:
                if _allows_decorative_bleed(other):
                    continue
                if _is_compact_numeric_suffix_pair(current, other):
                    continue
                intersection = current.bbox.intersection_area(other.bbox)
                if intersection <= 0:
                    continue
                overlap_ratio = intersection / min(current.bbox.area, other.bbox.area)
                horizontal_overlap = _axis_overlap_ratio(
                    current.bbox.x_min,
                    current.bbox.x_max,
                    other.bbox.x_min,
                    other.bbox.x_max,
                )
                vertical_overlap = _axis_overlap_ratio(
                    current.bbox.y_min,
                    current.bbox.y_max,
                    other.bbox.y_min,
                    other.bbox.y_max,
                )
                if overlap_ratio >= 0.35 and horizontal_overlap >= 0.35 and vertical_overlap >= 0.45:
                    errors.append(
                        f"Detected overlapping text blocks: '{current.label}' and '{other.label}'"
                    )
                    return errors
        return errors

    def _collect_text_covered_errors(self, nodes: Iterable[LayoutNode]) -> List[str]:
        ordered_nodes = list(nodes)
        errors: List[str] = []
        for current in ordered_nodes:
            if current.kind != "text" or _allows_decorative_bleed(current):
                continue
            for other in ordered_nodes:
                if other.order <= current.order or other.kind != "shape" or not other.opaque:
                    continue
                if _is_low_visibility_shape(other):
                    continue
                intersection = current.bbox.intersection_area(other.bbox)
                if intersection <= 0:
                    continue
                cover_ratio = intersection / current.bbox.area
                if cover_ratio >= 0.55:
                    errors.append(
                        f"Detected text likely covered by a later shape: '{current.label}'"
                    )
                    return errors
        return errors

    def print_summary(self) -> None:
        print("\nLayout quality summary")
        print("=" * 60)
        print(f"Files checked: {self.summary['total']}")
        print(f"Clean files: {self.summary['passed']}")
        print(f"Files with errors: {self.summary['errors']}")

    def print_results(self) -> None:
        for result in self.results:
            token = "OK" if result["passed"] else "ERROR"
            print(f"[{token}] {result['file']}")
            for error in result["errors"]:
                print(f"  - {error}")


def _resolve_layout_target(
    target: str | Path,
    *,
    prefer_finalized: bool = True,
) -> tuple[Path, str, List[Path]]:
    target_path = Path(target)
    if target_path.is_file():
        return target_path, "file", [target_path]
    if not target_path.exists() or not target_path.is_dir():
        return target_path, "missing", []

    direct_svg_files = sorted(target_path.glob("*.svg"))
    if direct_svg_files:
        stage_name = target_path.name if target_path.name in {"svg_output", "svg_final"} else "directory"
        return target_path, stage_name, direct_svg_files

    if prefer_finalized:
        svg_final_dir = target_path / "svg_final"
        if svg_final_dir.exists():
            return svg_final_dir, "svg_final", sorted(svg_final_dir.glob("*.svg"))
        return svg_final_dir, "svg_final", []

    svg_output_dir = target_path / "svg_output"
    if svg_output_dir.exists():
        return svg_output_dir, "svg_output", sorted(svg_output_dir.glob("*.svg"))
    return target_path, "directory", []


def summarize_layout_target(
    target: str | Path,
    expected_format: Optional[str] = None,
    *,
    prefer_finalized: bool = True,
) -> LayoutTargetSummary:
    resolved_path, stage_name, svg_files = _resolve_layout_target(target, prefer_finalized=prefer_finalized)
    checker = LayoutQualityChecker()
    for svg_file in svg_files:
        checker.check_file(svg_file, expected_format)
    return LayoutTargetSummary(
        target_path=str(Path(target)),
        checked_path=str(resolved_path),
        stage_name=stage_name,
        total=checker.summary["total"],
        clean=checker.summary["passed"],
        errors=checker.summary["errors"],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 skills/slidemax_workflow/scripts/slidemax.py layout_quality_checker",
        description="Check finalized PPT layout quality for overlap, coverage, and canvas overflow issues.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
When to use:
  - Run this before export when slide composition looks suspicious
  - Use this to detect text overlap, text coverage, and canvas overflow in svg_final/

Examples:
  %(prog)s workspace/demo_ppt169_20260313
  %(prog)s workspace/demo_ppt169_20260313/svg_final --expected-format ppt169
""",
    )
    parser.add_argument("target", nargs="?", help="Project path, svg_final directory, or a single SVG file.")
    parser.add_argument("--expected-format", default=None, help="Optional canvas format hint such as ppt169.")
    parser.add_argument("--all", action="store_true", help="Check all bundled example projects.")
    return parser


def _run_all_projects(checker: LayoutQualityChecker, target: Optional[str], expected_format: Optional[str]) -> None:
    if target:
        base_dirs = [Path(target)]
    else:
        base_dirs = get_example_dirs()
        extra_example_dirs = get_example_dirs(include_default=False)
        if extra_example_dirs:
            print(f"[INFO] Extra example roots from {EXTRA_EXAMPLE_PATHS_ENV}:")
            for path in extra_example_dirs:
                print(f"  - {path}")
            print()

    for base_dir in base_dirs:
        projects = find_all_projects(str(base_dir))
        for project in projects:
            print(f"\n{'=' * 80}")
            print(f"Checking project layout: {project.name}")
            print("=" * 80)
            checker.check_directory(project, expected_format)


def run_cli(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.all and not args.target:
        parser.print_help()
        return 0

    checker = LayoutQualityChecker()
    if args.all:
        _run_all_projects(checker, args.target if args.target else None, args.expected_format)
    else:
        checker.check_directory(args.target, args.expected_format)

    checker.print_results()
    checker.print_summary()
    return 1 if checker.summary["errors"] > 0 else 0


def main() -> None:
    raise SystemExit(run_cli())


__all__ = [
    "BBox",
    "LayoutNode",
    "LayoutQualityChecker",
    "LayoutTargetSummary",
    "build_parser",
    "main",
    "run_cli",
    "summarize_layout_target",
]
