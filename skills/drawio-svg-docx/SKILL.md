---
name: drawio-svg-docx
description: Export draw.io/.drawio diagrams to SVG and make the SVGs safe for Word/WPS/docx insertion. Use when converting .drawio/.io files, removing "Text is not SVG - cannot display", fixing draw.io SVG text line breaks that collapse in Word/WPS, checking abnormal SVG dimensions/viewBox, or post-processing SVG fallback text/foreignObject compatibility.
---

# Draw.io SVG Docx Compatibility

Use this skill for draw.io diagrams that must be inserted into Word/WPS/docx or other non-browser renderers.

## Workflow

1. Inspect the input directory:
   - List `.drawio`, `.io`, and `.svg` files.
   - Search sources and SVGs for `Text is not SVG`, `cannot display`, `foreignObject`, `<br`, `&#xa;`, and abnormal SVG `width`/`height` or `viewBox`.

2. Export `.drawio`/`.io` to SVG with draw.io CLI when needed:
   ```bash
   drawio --no-sandbox --export --format svg --embed-svg-fonts false path/to/file-or-folder
   ```
   If Electron sandboxing fails, rerun with required escalation. Do not use `--width` or `--height` to hide a bad aspect ratio; fix the source geometry or SVG viewBox problem first.

3. If an exported SVG is extremely wide and short, inspect the source `.drawio`:
   - Look for edge label geometries with suspicious `x`, `y`, `width`, or `height` on `mxGeometry relative="1"`.
   - Prefer fixing the `.drawio` source and re-exporting.
   - Typical symptom: a label was placed far away, making the exported SVG thousands of pixels wide.

4. Post-process the SVGs using `scripts/fix_drawio_svg.py`:
   ```bash
   python3 skills/drawio-svg-docx/scripts/fix_drawio_svg.py path/to/svg-or-directory
   ```
   The script:
   - removes draw.io's fallback warning `Text is not SVG - cannot display`;
   - rewrites multi-line fallback text into separate sibling `<text>` nodes so Word/WPS can preserve line breaks when it ignores `foreignObject`;
   - restores fallback text from draw.io `foreignObject` content when draw.io wrote `...`;
   - strips `foreignObject` by default for Word/WPS/docx compatibility;
   - validates XML after writing.

5. Verify after processing:
   ```bash
   rg -n "Text is not SVG|cannot display|can not display|not SVG" path/to/*.svg
   python3 skills/drawio-svg-docx/scripts/fix_drawio_svg.py --check path/to/svg-or-directory
   ```

## Notes

- Browser display is not enough. Browsers support `foreignObject`; Word/WPS often ignore it and use fallback `<text>`.
- Formatting SVG XML onto multiple physical lines does not fix Word/WPS line wrapping. The fallback text must use separate SVG text elements.
- Re-exporting from draw.io regenerates the raw SVG, so run the post-processing step again after every export.
- Existing `.docx` files do not automatically refresh embedded images. Delete the old inserted figure and insert the processed SVG again, or replace the media inside the `.docx`.
- If Word/WPS still renders poorly after this, use PNG for final document stability, or use PDF/EMF if a reliable converter exists locally.
