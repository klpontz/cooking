#!/usr/bin/env python3
"""Check the At a Glance table on recipe pages.

Usage: python3 check_table.py public/recipes/*.html

For each table.recipe-table, the script lays out every cell with its
rowspan and colspan. It fails if a row has a gap, if two cells overlap,
if a rowspan runs past the last row, or if a data row does not start
with an ingredient cell (td.ing). Exit code is 1 on any failure.
"""
import sys
from html.parser import HTMLParser


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.rows = []  # each row: list of (colspan, rowspan, classes)
        self.found = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table" and "recipe-table" in (a.get("class") or "").split():
            self.in_table = True
            self.found = True
        elif self.in_table and tag == "tr":
            self.rows.append([])
        elif self.in_table and tag == "td":
            self.rows[-1].append((
                int(a.get("colspan", 1)),
                int(a.get("rowspan", 1)),
                (a.get("class") or "").split(),
            ))

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False


def check(path):
    p = TableParser()
    p.feed(open(path, encoding="utf-8").read())
    if not p.found:
        return ["no table.recipe-table found"]
    errors = []
    n_rows = len(p.rows)
    occupied = [dict() for _ in range(n_rows)]  # row -> {col: True}
    width = None
    for r, cells in enumerate(p.rows):
        col = 0
        for i, (cs, rs, classes) in enumerate(cells):
            while col in occupied[r]:
                col += 1
            if i == 0 and col == 0 and "setup" not in classes and "ing" not in classes:
                errors.append(f"row {r + 1}: first cell is not td.ing")
            if r + rs > n_rows:
                errors.append(f"row {r + 1}: rowspan {rs} runs past the last row")
            for dr in range(min(rs, n_rows - r)):
                for dc in range(cs):
                    if col + dc in occupied[r + dr]:
                        errors.append(f"row {r + dr + 1}: cells overlap at column {col + dc + 1}")
                    occupied[r + dr][col + dc] = True
            col += cs
    for r in range(n_rows):
        w = len(occupied[r])
        full = set(range(w)) == set(occupied[r])
        if width is None:
            width = w
        if w != width or not full:
            errors.append(f"row {r + 1}: fills {w} columns with gaps={not full}, expected {width}")
    return errors


def main(paths):
    failed = False
    for path in paths:
        errors = check(path)
        status = "OK" if not errors else "FAIL"
        print(f"{status}  {path}")
        for e in errors:
            print(f"      {e}")
        failed = failed or bool(errors)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
