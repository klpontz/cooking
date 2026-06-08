# Recipe Publish Feature Design

**Date:** 2026-06-08
**Status:** Approved

## What This Is

A publishing flow that takes a recipe from conversation context, generates a self-contained HTML page, commits and pushes it to the repo, and Vercel auto-deploys it. The URL is posted in the conversation thread.

## Flow

1. Trigger fires (skill or natural language)
2. Claude generates `public/recipes/YYYY-MM-DD-<slug>.html` from conversation context
3. `git add` → `git commit` → `git push` to main
4. Vercel detects push, deploys in ~30–60s
5. Claude posts URL in thread: `https://<project>.vercel.app/recipes/YYYY-MM-DD-<slug>.html`

## Directory Structure

```
cooking/
├── public/
│   └── recipes/
│       └── YYYY-MM-DD-<slug>.html   # One file per recipe
```

Vercel serves the repo root as the static site. `public/recipes/` holds all published recipe pages.

## Triggers

**Skill:** `/recipe` — explicit invocation

**Natural language** (recognized via CLAUDE.md instruction):
- "give me the final recipe"
- "finalize the recipe"
- "publish the recipe"
- "save this recipe"
- "drop the recipe"

Both paths invoke the same flow. No confirmation step — just run it.

The skill lives at `.claude/skills/recipe.md` (project-local, travels with the cooking context).

## Recipe HTML Page

Self-contained HTML, no external dependencies. Inline `<style>` block, consistent with existing wiki aesthetic.

Contents:
- Recipe name + date
- Yield / serves
- Ingredients list
- Method (numbered steps)
- Technique notes ("why it works")
- "Back to index" link

Slug: lowercase, hyphenated, date-prefixed — e.g., `2026-06-08-pasta-alla-gricia.html`.

HTML is generated from conversation context; no template file required.

## Tagging System

Each recipe page includes a metadata block for future indexing. Two forms — both written at publish time:

**HTML meta tag** (machine-readable, in `<head>`):
```html
<meta name="recipe-tags" content="italian, pasta, weeknight">
<meta name="recipe-cuisine" content="italian">
<meta name="recipe-type" content="pasta, weeknight">
<meta name="recipe-main-ingredient" content="guanciale">
```

**Comment block** (human-readable, top of file):
```html
<!--
  recipe: Pasta alla Gricia
  date: 2026-06-08
  serves: 3
  cuisine: italian
  type: pasta, weeknight
  main-ingredient: guanciale
  tags: italian, pasta, weeknight, guanciale
-->
```

**Tag categories:**
- `cuisine` — italian, japanese, mexican, chinese, indian, thai
- `type` — pasta, braise, weeknight, weekend, bread, pizza, soup, salad, fermentation
- `main-ingredient` — free-form, one primary ingredient

No UI or index built now. The metadata is there when indexing becomes useful.

## Template Iteration

The HTML structure is intentionally minimal for v1. Template design is flagged for future iteration — easy to update since it's just HTML.

## Setup Required

- Vercel project connected to this GitHub repo (new — Kevin has not used Vercel before)
- `vercel.json` if any configuration is needed (likely not for a static repo)
- Vercel auto-deploy on push to main enabled (default behavior)

## What Is Not In Scope

- Recipe index page (future work)
- Build pipeline or static site generator (not needed)
- Template system (future iteration)
