# Draw.io SVG Docx

[English](README.md) | [简体中文](README.zh-CN.md)

Standalone Python tool and optional agent skill for post-processing draw.io SVG files so they behave better when inserted into Word, WPS, or `.docx` documents.

It focuses on common draw.io SVG issues:

- removes `Text is not SVG - cannot display`;
- strips `foreignObject` fallback HTML by default;
- restores multiline text from draw.io HTML text blocks;
- converts multiline fallback text into separate SVG `<text>` nodes for Word/WPS compatibility;
- checks SVG XML validity after processing.

## Repository Layout

```text
drawio-svg-docx/
├── README.md
├── README.zh-CN.md
├── LICENSE
├── skills/
│   └── drawio-svg-docx/
│       ├── SKILL.md
│       └── scripts/
│           └── fix_drawio_svg.py
└── tests/
    └── test_fix_drawio_svg.py
```

## Usage

Run the post-processor on one SVG file or a directory containing SVG files:

```bash
python3 skills/drawio-svg-docx/scripts/fix_drawio_svg.py path/to/svg-or-directory
```

Check without modifying files:

```bash
python3 skills/drawio-svg-docx/scripts/fix_drawio_svg.py --check path/to/svg-or-directory
```

If you re-export from draw.io, run the post-processing step again because draw.io regenerates raw SVG output.

## Optional Skill Install

If your AI coding agent supports local skills, copy the skill directory into that agent's skills directory. For Codex, this is commonly:

```bash
mkdir -p ~/.codex/skills
cp -a skills/drawio-svg-docx ~/.codex/skills/
```

Workspace-local skill directories such as `.agents/skills/` may also be supported depending on your environment.

## Requirements

- Python 3.10 or newer.
- Optional: draw.io CLI if you also want Codex to export `.drawio` or `.io` files to SVG.

The SVG cleanup script uses only the Python standard library.

## Testing

```bash
python3 tests/test_fix_drawio_svg.py
```

## Notes

Existing `.docx` files do not automatically refresh embedded images. Delete the old inserted figure and insert the processed SVG again, or replace the media inside the `.docx`.
