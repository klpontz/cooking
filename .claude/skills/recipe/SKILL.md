---
name: recipe
description: Publish the current recipe from conversation context as a self-contained HTML page, commit it to public/recipes/, push to main, deploy to kevinrocci.com/cooking/, and return the live URL. Invoke when Kevin says "publish the recipe", "finalize the recipe", "give me the final recipe", "save this recipe", or "drop the recipe".
---

# Recipe Publish Skill

Publish the current recipe from conversation context as a self-contained HTML page, push it to the repo, deploy it, and return the live URL.

## Live base URL

```
https://kevinrocci.com/cooking
```

The site is hosted on Bluehost. `./deploy.sh` uploads it over SFTP. Links must stay relative: the site lives under `/cooking/`, so a root-absolute link like `/public/...` breaks.

## Steps

1. Extract from conversation context:
   - `recipe_name` — e.g., "Pasta alla Gricia"
   - `date` — today's date as YYYY-MM-DD (e.g., "2026-06-08")
   - `slug` — lowercase hyphenated name (e.g., "pasta-alla-gricia")
   - `serves` — number of servings
   - `cuisine` — one of: italian, japanese, mexican, chinese, indian, thai, other
   - `type` — one or more of: pasta, braise, weeknight, weekend, bread, pizza, soup, salad, fermentation, other
   - `main_ingredient` — primary ingredient, lowercase (e.g., "guanciale")
   - `tags` — comma-separated: cuisine + type + main_ingredient combined

2. Construct the filename: `{date}-{slug}.html` (e.g., `2026-06-08-pasta-alla-gricia.html`)

3. Write the file to `public/recipes/{filename}` using the HTML template below. Fill every placeholder with real content — never leave `{recipe_name}` or any other `{variable}` in the output. Build the At a Glance table by following the **At a Glance Table** rules below.

4. Add a new `<li>` entry to the Recipes section of `index.html` at the repo root:
   ```html
   <li><a href="public/recipes/{filename}">{recipe_name}</a><span class="meta">{date}</span></li>
   ```
   Insert it at the top of the existing list (most recent first).

5. Shade and check the table, then commit and deploy. Fix any table error before going on:
   ```bash
   python3 .claude/skills/recipe/shade_table.py public/recipes/{filename}
   python3 .claude/skills/recipe/check_table.py public/recipes/{filename}
   git add public/recipes/{filename} index.html
   git commit -m "feat: add recipe {recipe_name}"
   git push
   ./deploy.sh
   ```

   If `./deploy.sh` fails, report the error. Do not claim the recipe is live.

6. Post the URL in the conversation:
   ```
   Recipe published:
   https://kevinrocci.com/cooking/public/recipes/{filename}
   ```

## HTML Template

```html
<!--
  recipe: {recipe_name}
  date: {date}
  serves: {serves}
  cuisine: {cuisine}
  type: {type}
  main-ingredient: {main_ingredient}
  tags: {tags}
-->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="recipe-tags" content="{tags}">
  <meta name="recipe-cuisine" content="{cuisine}">
  <meta name="recipe-type" content="{type}">
  <meta name="recipe-main-ingredient" content="{main_ingredient}">
  <title>{recipe_name}</title>
  <style>
    /* Palette from kevinrocci.com/work (yellow-billed magpie).
       c50–c950: one tinted scale on the hue of the wing blue (#1A5F92),
       near-white to near-black. Every neutral comes from it. */
    :root {
      --c50: #F5FAFE; --c100: #EDF2F7; --c200: #DDE4EA; --c300: #C6CFD7;
      --c400: #9FABB6; --c500: #768593; --c600: #576878; --c700: #404F5C;
      --c800: #2B3741; --c900: #192229; --c950: #0E151B;
      --accent: #1A5F92;  /* wing blue: links */
      --spark: #F0AD1B;   /* eye ring: one mark on the title rule */
    }
    body { font-family: Georgia, serif; max-width: 680px; margin: 40px auto; padding: 0 20px; color: var(--c900); background: var(--c50); line-height: 1.7; }
    h1 { font-size: 1.8rem; padding-bottom: 8px; margin-bottom: 0.3rem; background: linear-gradient(to right, var(--spark) 0 3rem, var(--c900) 3rem) left bottom / 100% 2px no-repeat; }
    .meta { font-size: 0.85rem; color: var(--c600); margin-bottom: 2rem; }
    h2 { font-size: 1.1rem; margin-top: 2rem; color: var(--c700); text-transform: uppercase; letter-spacing: 0.05em; }
    ul, ol { padding-left: 1.4rem; }
    li { margin-bottom: 0.4rem; }
    .note { border-left: 3px solid var(--c200); padding-left: 1rem; margin: 1.5rem 0; font-size: 0.95rem; color: var(--c700); }
    a { color: var(--accent); }
    nav { margin-top: 3rem; font-size: 0.85rem; }
    nav a { color: var(--c600); text-decoration: none; }
    nav a:hover { text-decoration: underline; }
    .recipe-table-wrap { overflow-x: auto; margin: 1rem 0 0; }
    .recipe-table { border-collapse: collapse; border: 2px solid var(--c900); font-size: 0.85rem; line-height: 1.35; width: 100%; }
    .recipe-table td { border: 1px solid var(--c400); padding: 6px; text-align: center; vertical-align: middle; }
    .recipe-table td.ing { text-align: left; min-width: 7.5rem; }
    .recipe-table td.ing, .recipe-table td.blank { border-top-color: var(--c200); border-bottom-color: var(--c200); }
    .recipe-table td.lane { border-left-style: hidden; }
    .recipe-table td.t1 { background: var(--c100); }
    .recipe-table td.t2 { background: var(--c200); }
    .recipe-table td.t3 { background: var(--c300); }
    .recipe-table td.setup { background: var(--c100); border-bottom: 2px solid var(--c900); }
    .recipe-table tr.group > td { border-top: 2px solid var(--c900); }
  </style>
</head>
<body>
  <h1>{recipe_name}</h1>
  <p class="meta">{date} &middot; Serves {serves}</p>

  <h2>Ingredients</h2>
  <ul>
    {ingredients_as_li_items}
  </ul>

  <h2>Method</h2>
  <ol>
    {method_as_li_items}
  </ol>

  <h2>At a Glance</h2>
  <div class="recipe-table-wrap">
  <table class="recipe-table">
    {table_rows}
  </table>
  </div>

  <h2>Notes</h2>
  <div class="note">
    {technique_notes}
  </div>

  <nav><a href="../../">← All recipes</a></nav>
</body>
</html>
```

## Rules

- Fill every section from conversation context. Never output `{variable}` placeholders in the final HTML — replace them all with real content.
- `{ingredients_as_li_items}`: each ingredient on its own `<li>` line, e.g. `<li>150g guanciale</li>`
- **Ingredient order is mandatory: list ingredients in the exact order they are first incorporated in the Method steps** — not by category, quantity, or importance. Walk the method top to bottom and record each ingredient the first time it's added; that sequence is the ingredient list order. Example: if garlic and ginger go into step 1, they come before the coconut milk added in step 2. Group items added together in the same step in the order the step names them. Finishing/garnish items (added off-heat or "to serve") go last.
- **Before writing the file, run this check:** for each ingredient, note the step number where it first appears, and confirm those step numbers are non-decreasing down the ingredient list. If any ingredient is out of order, reorder the list before generating HTML.
- `{method_as_li_items}`: each step on its own `<li>` line
- `{technique_notes}`: the "why it works" reasoning as prose, not a restatement of steps
- If serves is unknown, omit `&middot; Serves {serves}` from the `.meta` line
- No confirmation step — generate, write, commit, push, deploy, post URL
- `{table_rows}`: the `<tr>` rows of the At a Glance table. See the next section.

## At a Glance Table

The At a Glance table shows the whole recipe as one grid, in the tabular style from Cooking for Engineers. Ingredients run down the left. Steps run left to right. Merged cells show where ingredients come together. It goes after Method and before Notes. The Ingredients list and Method stay as they are.

**Structure:**
- Each ingredient gets one row. The first cell is `<td class="ing">` with the quantity and a short name (e.g. `2 Tbsp olive oil`). Leave the prep words out of the name when a step cell covers them.
- Split a divided ingredient into one row per use (e.g. `1 Tbsp olive oil` for the rub, `2 Tbsp olive oil` for the sear).
- Rows follow the order that ingredients enter the cooking. Ingredients that combine in one step must be on adjacent rows, so a single `rowspan` cell can join them.
- Each cell to the right is a short step in lowercase, about 2–8 words, with times and temperatures (e.g. `sear 6–8 min, all sides`). Doneness cues and warnings stay in Method.
- When ingredients combine, use one cell with `rowspan` over all of their rows. Each new merge column covers every row the previous merge covered, plus the new rows.
- An ingredient that waits for a later step gets an empty cell with `colspan` that reaches the column where it joins. Leave empty cells as plain `<td></td>`. The shading script classes them.
- The last column is usually one cell that spans every row: the final assemble-and-serve step.
- Setup that applies to the whole dish (oven heat, fire, a pan to heat) goes in an optional first row: `<tr><td class="setup" colspan="{total_columns}">Heat oven to 425°F</td></tr>`.

**Groups:**
- A group is a component prepared on its own track: a marinade, a sauce, a garnish, a side, or table condiments. Start each group after the first with `<tr class="group">`. This draws a heavy rule above it.
- A single pot or pan with no separate components needs no group rows.

**Size:**
- Keep the table to 9 columns or fewer, including the ingredient column, so it fits the 680px page on desktop. Merge adjacent short steps to stay under the limit. On phones the table scrolls inside its box.

**Shading:** do not write the `t1`, `t2`, `t3`, `blank`, or `lane` classes by hand. Write `class="ing"` and `class="setup"` only. `shade_table.py` sets the rest from each cell's column: step cells darken from left to right, the final column gets the darkest tint, and an empty cell right of an ingredient becomes a lane with no dividing line.

**Colors:** never use hex greys in a page. Every neutral comes from the `--c50`…`--c950` scale in the template, links use `--accent`, and `--spark` appears only on the title rule.

**Check:** run `python3 .claude/skills/recipe/check_table.py public/recipes/{filename}`. It fails when a row has a gap, cells overlap, a `rowspan` runs past the last row, or a row does not start with `td.ing`. Fix and rerun until it prints `OK`.
