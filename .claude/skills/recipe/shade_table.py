#!/usr/bin/env python3
"""Add lane and final-step classes to the At a Glance table.

Usage: python3 shade_table.py public/recipes/<file>.html [...]

The script reads every cell and rewrites its class:
- Empty cells get "blank".
- A single-row cell whose first word is knife work or measuring (chop,
  slice, juice, weigh, and so on) gets "prep", if nothing but the
  ingredient and other lane cells sit to its left. Prep text is
  left-aligned. A merged knife cell (one step written once for several
  rows) is drawn as a step, so it reads as one box.
- A step cell that reaches the last column gets "t3", the one tint.
- Ingredient (ing) and setup cells keep their class.
- Lane cells (ing, blank, prep) lose the line between them, and the line
  into a multi-row step, with classes "ol" (open left) and "or" (open
  right). A row reads as one open lane until it joins a step. Single-row
  steps keep all four lines.
The script is idempotent. Run check_table.py after it.
"""
import re
import sys

TD = re.compile(r"<td([^>]*)>(.*?)</td>", re.S)
TR = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S)

# First words that mark a cell as prep, not cooking.
PREP = {
    "chop", "mince", "slice", "dice", "cut", "halve", "quarter", "julienne",
    "juice", "zest", "grate", "peel", "trim", "strip", "stem", "seed",
    "core", "pit", "crush", "smash", "crumble", "tear", "pick", "shred",
    "rinse", "wash", "sort", "soak", "drain", "pat", "dry", "separate",
    "measure", "weigh", "sift", "remove", "butterfly", "pound",
}


def attr(attrs, name, default=None):
    m = re.search(rf'{name}="([^"]*)"', attrs)
    return m.group(1) if m else default


def prep_word(text):
    words = re.findall(r"[a-z]+", text.lower())
    return bool(words) and words[0] in PREP and "together" not in words


def shade(html):
    start = html.find('<table class="recipe-table">')
    if start < 0:
        return html
    end = html.find("</table>", start)
    body = html[start:end]

    rows = [TD.findall(m.group(1)) for m in TR.finditer(body)]
    n = len(rows)
    occupied = [set() for _ in range(n)]
    cells = []  # (start col, end col, attrs, text) in document order
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

    # owner[r][c] = index of the cell that covers grid position (r, c)
    owner = [dict() for _ in range(n)]
    rows_of = []
    i = 0
    for r, tds in enumerate(rows):
        for _ in tds:
            first, last, attrs, _t = cells[i]
            rs = min(int(attr(attrs, "rowspan", 1)), n - r)
            rows_of.append(range(r, r + rs))
            for rr in rows_of[i]:
                for c in range(first, last + 1):
                    owner[rr][c] = i
            i += 1

    kind = []
    for first, last, attrs, text in cells:
        classes = (attr(attrs, "class") or "").split()
        if "ing" in classes or "setup" in classes:
            kind.append("ing" if "ing" in classes else "setup")
        elif not text.strip():
            kind.append("blank")
        elif prep_word(text):
            kind.append("prep?")
        elif last == width - 1:
            kind.append("t3")
        else:
            kind.append("step")
    # Prep only when the lane runs straight into it in every row.
    for i, (first, last, attrs, text) in enumerate(cells):
        if kind[i] == "prep?" and len(rows_of[i]) > 1:
            kind[i] = "t3" if last == width - 1 else "step"
        if kind[i] == "prep?":
            left = {owner[r].get(c) for r in rows_of[i] for c in range(first)}
            ok = all(j is not None and j != i and kind[j] in ("ing", "blank", "prep?") for j in left)
            kind[i] = "prep" if ok else ("t3" if last == width - 1 else "step")
    lane = ("ing", "blank", "prep")

    def neighbors(i, c):
        return {owner[r].get(c) for r in rows_of[i]}

    new_cells = []
    for i, (first, last, attrs, text) in enumerate(cells):
        keep = [] if kind[i] == "step" else [kind[i]]
        if kind[i] in lane:
            left = neighbors(i, first - 1)
            if first > 0 and None not in left and all(kind[j] in lane for j in left):
                keep.append("ol")
            right = neighbors(i, last + 1)
            if None not in right and all(
                kind[j] in lane or (kind[j] in ("step", "t3") and len(rows_of[j]) > 1) for j in right
            ):
                keep.append("or")
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
