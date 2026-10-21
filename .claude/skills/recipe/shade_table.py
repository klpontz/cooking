#!/usr/bin/env python3
"""Add stage shading and lane classes to the At a Glance table.

Usage: python3 shade_table.py public/recipes/<file>.html [...]

The script reads the grid position of every cell and rewrites its class:
- Step cells get a tint that darkens from left to right: no class for the
  first third of the step columns, t1 for the middle third, t2 for the
  last third. A cell that reaches the last column gets t3.
- Empty cells get class "blank". An empty cell directly right of an
  ingredient also gets "lane", which hides the line between them, so the
  ingredient row reads as one lane up to the step where it joins.
- Ingredient (ing) and setup cells keep their class.
The script is idempotent. Run check_table.py after it.
"""
import re
import sys

TD = re.compile(r"<td([^>]*)>(.*?)</td>", re.S)
TR = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S)


def attr(attrs, name, default=None):
    m = re.search(rf'{name}="([^"]*)"', attrs)
    return m.group(1) if m else default


def shade(html):
    start = html.find('<table class="recipe-table">')
    if start < 0:
        return html
    end = html.find("</table>", start)
    body = html[start:end]

    rows = [TD.findall(m.group(1)) for m in TR.finditer(body)]
    n = len(rows)
    occupied = [set() for _ in range(n)]
    cells = []  # (row, start col, end col, attrs, text) in document order
    for r, tds in enumerate(rows):
        col = 0
        for attrs, text in tds:
            while col in occupied[r]:
                col += 1
            cs = int(attr(attrs, "colspan", 1))
            rs = int(attr(attrs, "rowspan", 1))
            for dr in range(min(rs, n - r)):
                occupied[r + dr].update(range(col, col + cs))
            cells.append((col, col + cs - 1, attrs, text))
            col += cs
    width = max(len(o) for o in occupied)

    new_cells = []
    for first, last, attrs, text in cells:
        classes = (attr(attrs, "class") or "").split()
        keep = [c for c in classes if c in ("ing", "setup")]
        if not keep:
            if not text.strip():
                keep = ["blank"] + (["lane"] if first == 1 else [])
            elif last == width - 1:
                keep = ["t3"]
            else:
                frac = (last - 1) / (width - 2)  # step columns run 1..width-1
                level = min(2, int(frac * 3))
                keep = [f"t{level}"] if level else []
        attrs = re.sub(r'\s*class="[^"]*"', "", attrs)
        if keep:
            attrs = f' class="{" ".join(keep)}"' + attrs
        new_cells.append(f"<td{attrs}>{text}</td>")

    it = iter(new_cells)
    body = TD.sub(lambda m: next(it), body)
    return html[:start] + body + html[end:]


if __name__ == "__main__":
    for path in sys.argv[1:]:
        s = open(path, encoding="utf-8").read()
        open(path, "w", encoding="utf-8").write(shade(s))
        print("shaded", path)
