#!/usr/bin/env python3
"""Post-process draw.io SVGs for Word/WPS/docx compatibility."""

from __future__ import annotations

import argparse
import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


WARNING_RE = re.compile(
    r'<switch><g requiredFeatures="http://www\.w3\.org/TR/SVG11/feature#Extensibility"/>'
    r'<a transform="translate\(0,-5\)" xlink:href="https://www\.(?:drawio\.com|diagrams\.net)/doc/faq/svg-export-text-problems" target="_blank">'
    r'<text text-anchor="middle" font-size="10px" x="50%" y="100%">Text is not SVG - cannot display</text>'
    r'</a></switch>'
)
PAIR_RE = re.compile(
    r'(<foreignObject\b.*?</foreignObject>)(<text\b([^>]*)>)(.*?)(</text>)',
    re.S,
)
TEXT_WITH_TSPANS_RE = re.compile(
    r'<text\b([^>]*)>\s*((?:<tspan\b[^>]*>.*?</tspan>\s*)+)</text>',
    re.S,
)
TSPAN_RE = re.compile(r'<tspan\b([^>]*)>(.*?)</tspan>', re.S)
BR_RE = re.compile(r'<br\b[^>]*/?>', re.I)
TAG_RE = re.compile(r'<[^>]+>')


def attr(attrs: str, name: str) -> str | None:
    match = re.search(rf'\b{re.escape(name)}="([^"]*)"', attrs)
    return match.group(1) if match else None


def set_attr(attrs: str, name: str, value: str) -> str:
    replacement = f'{name}="{html.escape(value, quote=True)}"'
    if re.search(rf'\b{re.escape(name)}="[^"]*"', attrs):
        return re.sub(rf'\b{re.escape(name)}="[^"]*"', replacement, attrs, count=1)
    return attrs.rstrip() + ' ' + replacement


def number(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.match(r'\s*(-?\d+(?:\.\d+)?)', value)
    return float(match.group(1)) if match else None


def fmt(value: float) -> str:
    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))
    return f'{value:.2f}'.rstrip('0').rstrip('.')


def lines_from_foreign_object(foreign_object: str) -> list[str]:
    marked = BR_RE.sub('\n', foreign_object)
    text = TAG_RE.sub('', marked)
    text = html.unescape(text)
    return clean_lines(text)


def lines_from_text(text: str) -> list[str]:
    return clean_lines(html.unescape(text))


def clean_lines(text: str) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        line = ' '.join(line.split())
        if line:
            lines.append(line)
    return lines


def text_elements(attrs: str, lines: list[str]) -> str:
    x = attr(attrs, 'x') or '0'
    y_value = number(attr(attrs, 'y'))
    font_size = number(attr(attrs, 'font-size')) or 15.0
    line_gap = font_size * 1.2

    if y_value is None:
        y_value = 0.0

    start_y = y_value - line_gap * (len(lines) - 1) / 2
    parts = []
    for index, line in enumerate(lines):
        line_attrs = set_attr(set_attr(attrs, 'x', x), 'y', fmt(start_y + index * line_gap))
        parts.append(f'<text{line_attrs}>{html.escape(line, quote=False)}</text>')
    return ''.join(parts)


def rewrite_fallback(match: re.Match[str], keep_foreign_object: bool) -> str:
    foreign_object, open_text, attrs, content, close_text = match.groups()
    foreign_lines = lines_from_foreign_object(foreign_object)
    fallback_lines = lines_from_text(content)
    fallback_plain = ''.join(fallback_lines)

    lines = foreign_lines if (len(foreign_lines) > 1 or '...' in fallback_plain) else fallback_lines
    if len(lines) <= 1:
        fallback = open_text + content + close_text
    else:
        fallback = text_elements(attrs, lines)

    return foreign_object + fallback if keep_foreign_object else fallback


def convert_tspan_text(match: re.Match[str]) -> str:
    attrs, tspan_block = match.groups()
    parts = []
    for tspan_match in TSPAN_RE.finditer(tspan_block):
        tspan_attrs, content = tspan_match.groups()
        line = ' '.join(html.unescape(TAG_RE.sub('', content)).split())
        if not line:
            continue
        line_attrs = attrs
        for name in ('x', 'y'):
            value = attr(tspan_attrs, name)
            if value is not None:
                line_attrs = set_attr(line_attrs, name, value)
        parts.append(f'<text{line_attrs}>{html.escape(line, quote=False)}</text>')
    return ''.join(parts) if parts else match.group(0)


def convert_tspans(svg: str) -> str:
    """Convert nested tspan text into sibling text nodes for Word/WPS."""

    return TEXT_WITH_TSPANS_RE.sub(convert_tspan_text, svg)


def collect_paths(inputs: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        if item.is_dir():
            paths.extend(sorted(item.glob('*.svg')))
        elif item.suffix.lower() == '.svg':
            paths.append(item)
    return paths


def process(path: Path, check: bool, keep_foreign_object: bool) -> tuple[bool, str]:
    original = path.read_text(encoding='utf-8')
    warning_count = len(WARNING_RE.findall(original))
    updated = WARNING_RE.sub('', original)
    foreign_object_count = updated.count('<foreignObject')
    updated, pair_count = PAIR_RE.subn(
        lambda match: rewrite_fallback(match, keep_foreign_object), updated
    )
    tspan_count = updated.count('<tspan')
    updated = convert_tspans(updated)

    if check:
        text = updated
    else:
        if updated != original:
            path.write_text(updated, encoding='utf-8')
        text = updated

    ET.fromstring(text)
    changed = updated != original
    return changed, (
        f'{path}: warning={warning_count}, text_fallbacks={pair_count}, '
        f'foreign_objects={foreign_object_count}, tspans={tspan_count}, changed={changed}'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', type=Path, help='SVG files or directories containing SVG files')
    parser.add_argument('--check', action='store_true', help='validate and report without writing')
    parser.add_argument(
        '--keep-foreign-object',
        action='store_true',
        help='keep draw.io foreignObject HTML text; default strips it for Word/WPS/docx compatibility',
    )
    args = parser.parse_args()

    svg_paths = collect_paths(args.paths)
    if not svg_paths:
        print('No SVG files found.', file=sys.stderr)
        return 1

    for path in svg_paths:
        _changed, message = process(path, args.check, args.keep_foreign_object)
        print(message)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
