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

3. Write the file to `public/recipes/{filename}` using the HTML template below. Fill every placeholder with real content — never leave `{recipe_name}` or any other `{variable}` in the output.

4. Add a new `<li>` entry to the Recipes section of `index.html` at the repo root:
   ```html
   <li><a href="public/recipes/{filename}">{recipe_name}</a><span class="meta">{date}</span></li>
   ```
   Insert it at the top of the existing list (most recent first).

5. Run:
   ```bash
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
    body { font-family: Georgia, serif; max-width: 680px; margin: 40px auto; padding: 0 20px; color: #1a1a1a; line-height: 1.7; }
    h1 { font-size: 1.8rem; border-bottom: 2px solid #1a1a1a; padding-bottom: 8px; margin-bottom: 0.3rem; }
    .meta { font-size: 0.85rem; color: #888; margin-bottom: 2rem; }
    h2 { font-size: 1.1rem; margin-top: 2rem; color: #444; text-transform: uppercase; letter-spacing: 0.05em; }
    ul, ol { padding-left: 1.4rem; }
    li { margin-bottom: 0.4rem; }
    .note { border-left: 3px solid #ddd; padding-left: 1rem; margin: 1.5rem 0; font-size: 0.95rem; color: #555; }
    nav { margin-top: 3rem; font-size: 0.85rem; }
    nav a { color: #555; text-decoration: none; }
    nav a:hover { text-decoration: underline; }
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
