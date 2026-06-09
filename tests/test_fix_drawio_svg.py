#!/usr/bin/env python3
"""Minimal tests for the draw.io SVG post-processor."""

from __future__ import annotations

import importlib.util
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "drawio-svg-docx" / "scripts" / "fix_drawio_svg.py"


def load_module():
    spec = importlib.util.spec_from_file_location("fix_drawio_svg", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_multiline_foreign_object_is_rewritten():
    module = load_module()
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="120px" height="80px">
<foreignObject><div xmlns="http://www.w3.org/1999/xhtml">line one<br/>line two</div></foreignObject><text x="60" y="40" font-size="10px">...</text>
</svg>"""

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sample.svg"
        path.write_text(svg, encoding="utf-8")
        changed, message = module.process(path, check=False, keep_foreign_object=False)
        updated = path.read_text(encoding="utf-8")

    ET.fromstring(updated)
    assert changed, message
    assert "foreignObject" not in updated
    assert "<tspan" not in updated
    assert updated.count("<text") == 2
    assert "line one" in updated
    assert "line two" in updated


def test_warning_is_removed():
    module = load_module()
    warning = (
        '<switch><g requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"/>'
        '<a transform="translate(0,-5)" xlink:href="https://www.drawio.com/doc/faq/svg-export-text-problems" target="_blank">'
        '<text text-anchor="middle" font-size="10px" x="50%" y="100%">Text is not SVG - cannot display</text>'
        "</a></switch>"
    )
    svg = f'<svg xmlns:xlink="http://www.w3.org/1999/xlink">{warning}<text x="1" y="2">ok</text></svg>'

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "warning.svg"
        path.write_text(svg, encoding="utf-8")
        changed, message = module.process(path, check=False, keep_foreign_object=False)
        updated = path.read_text(encoding="utf-8")

    ET.fromstring(updated)
    assert changed, message
    assert "Text is not SVG" not in updated
    assert "cannot display" not in updated


def main() -> int:
    test_multiline_foreign_object_is_rewritten()
    test_warning_is_removed()
    print("tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
