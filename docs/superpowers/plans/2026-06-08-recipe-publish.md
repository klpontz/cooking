# Recipe Publish Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When Kevin says "give me the final recipe" (or uses `/recipe`), Claude generates a tagged HTML recipe page, commits and pushes it, and Vercel auto-deploys it — URL posted in the thread.

**Architecture:** Project-local Claude Code skill generates self-contained HTML from conversation context, writes to `public/recipes/`, commits, pushes to main, and Vercel deploys via GitHub integration. Natural language triggers wired into CLAUDE.md. No build pipeline, no external dependencies.

**Tech Stack:** Claude Code skills, Vercel (static hosting via GitHub integration), Git, HTML/CSS

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `public/recipes/.gitkeep` | Create | Scaffold directory |
| `.claude/skills/recipe.md` | Create | Recipe publish skill — instructions + HTML template |
| `CLAUDE.md` | Modify | Add natural language triggers + recipe publishing section |

---

## Task 1: Create GitHub Repository and Push

> This is a manual step Kevin performs. No code to write.

**Files:** none

- [ ] **Step 1: Create repo on GitHub**

Go to https://github.com/new and create a new repository named `cooking`. Keep it private. Do not initialize with README or .gitignore.

- [ ] **Step 2: Add remote and push**

```bash
git remote add origin https://github.com/kevinrocci/cooking.git
git push -u origin main
```

Expected: all commits push cleanly, branch tracking set to `origin/main`.

- [ ] **Step 3: Verify**

```bash
git remote -v
```

Expected output:
```
origin  https://github.com/kevinrocci/cooking.git (fetch)
origin  https://github.com/kevinrocci/cooking.git (push)
```

---

## Task 2: Set Up Vercel Project

> This is a manual step Kevin performs via the Vercel web UI.

**Files:** none

- [ ] **Step 1: Create Vercel account**

Go to https://vercel.com and sign up with your GitHub account.

- [ ] **Step 2: Import the repo**

From the Vercel dashboard, click "Add New → Project". Select the `cooking` repo from GitHub. When prompted for framework, select "Other" (no build step needed). Leave all other settings as defaults. Click Deploy.

- [ ] **Step 3: Note the project URL**

After the first deploy completes, Vercel assigns a URL in the format `https://<project-name>.vercel.app`. Copy it — you'll need it in Task 4.

It will look like: `https://cooking-kevinrocci.vercel.app` (Vercel may append your username or a random suffix).

- [ ] **Step 4: Verify the deploy**

Open `https://<your-project>.vercel.app/overview.html` in a browser. The overview page should render — confirming the repo root is being served correctly.

---

## Task 3: Scaffold `public/recipes/` Directory

**Files:**
- Create: `public/recipes/.gitkeep`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p /Users/pontz/cooking/public/recipes
touch /Users/pontz/cooking/public/recipes/.gitkeep
```

- [ ] **Step 2: Commit and push**

```bash
git -C /Users/pontz/cooking add public/recipes/.gitkeep
git -C /Users/pontz/cooking commit -m "feat: scaffold public/recipes directory"
git -C /Users/pontz/cooking push
```

Expected: Vercel triggers a new deploy. The `public/recipes/` path now exists.

---

## Task 4: Write the `/recipe` Skill

**Files:**
- Create: `.claude/skills/recipe.md`

The skill instructs Claude exactly how to execute the publish flow: generate HTML from conversation context, write the file, commit, push, and post the URL.

- [ ] **Step 1: Create the skills directory if it doesn't exist**

```bash
mkdir -p /Users/pontz/cooking/.claude/skills
```

- [ ] **Step 2: Write the skill file**

Create `/Users/pontz/cooking/.claude/skills/recipe.md` with this content — replacing `YOUR_VERCEL_URL` with the actual URL from Task 2 Step 3:

````markdown
# Recipe Publish Skill

Publish the current recipe from conversation context as a self-contained HTML page, push it to the repo, and return the live Vercel URL.

## Your Vercel base URL

```
https://YOUR_VERCEL_URL.vercel.app
```

Replace `YOUR_VERCEL_URL` with your actual Vercel project name after setup.

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

3. Write the file to `public/recipes/{filename}` using the template below.

4. Run:
   ```bash
   git add public/recipes/{filename}
   git commit -m "feat: add recipe {recipe_name}"
   git push
   ```

5. Post the URL in the conversation:
   ```
   Recipe published — live in ~60s:
   https://YOUR_VERCEL_URL.vercel.app/public/recipes/{filename}
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
    <!-- ingredients here, one <li> per item -->
  </ul>

  <h2>Method</h2>
  <ol>
    <!-- numbered steps here, one <li> per step -->
  </ol>

  <h2>Notes</h2>
  <div class="note">
    <!-- technique notes / why it works -->
  </div>

  <nav><a href="/">← Home</a></nav>
</body>
</html>
```

## Rules

- Fill every section from conversation context. Never leave template placeholders in the output.
- Technique notes go in the `<div class="note">` — the "why it works" reasoning, not redundant restatement of steps.
- If serves is unknown, omit the serves line from `.meta`.
- No confirmation step. Generate, write, commit, push, post URL.
````

- [ ] **Step 3: Replace `YOUR_VERCEL_URL` in the skill file**

Open `.claude/skills/recipe.md` and replace both occurrences of `YOUR_VERCEL_URL` with the actual Vercel project subdomain from Task 2 Step 3 (e.g., `cooking-kevinrocci`).

- [ ] **Step 4: Commit the skill**

```bash
git -C /Users/pontz/cooking add .claude/skills/recipe.md
git -C /Users/pontz/cooking commit -m "feat: add /recipe publish skill"
git -C /Users/pontz/cooking push
```

---

## Task 5: Update CLAUDE.md with Natural Language Triggers

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add Recipe Publishing section to CLAUDE.md**

After the `## Wiki Maintenance` section and before `## Advisory Rules`, insert:

```markdown
## Recipe Publishing

When Kevin says any of the following, invoke the `/recipe` skill immediately — no confirmation:
- "give me the final recipe"
- "finalize the recipe"
- "publish the recipe"
- "save this recipe"
- "drop the recipe"

The skill generates a tagged HTML page, commits it to `public/recipes/`, pushes to main, and posts the Vercel URL in the thread.
```

- [ ] **Step 2: Update the Repo Files section**

In the `## Repo Files` section, add:

```markdown
- `public/recipes/` — published recipe HTML pages, deployed via Vercel
```

- [ ] **Step 3: Commit**

```bash
git -C /Users/pontz/cooking add CLAUDE.md
git -C /Users/pontz/cooking commit -m "feat: add recipe publish triggers to CLAUDE.md"
git -C /Users/pontz/cooking push
```

---

## Task 6: Smoke Test — Publish Pasta alla Gricia

**Files:**
- Creates: `public/recipes/2026-06-08-pasta-alla-gricia.html`

> Run this in a live Claude Code session with the cooking repo open, using the recipe discussed on 2026-06-08.

- [ ] **Step 1: Trigger the recipe skill**

Type: `give me the final recipe`

Claude should invoke the `/recipe` skill, generate the HTML for pasta alla gricia (serves 3, italian, pasta, weeknight, guanciale), write `public/recipes/2026-06-08-pasta-alla-gricia.html`, commit, push, and post the URL.

- [ ] **Step 2: Verify the file was created**

```bash
ls /Users/pontz/cooking/public/recipes/
```

Expected: `2026-06-08-pasta-alla-gricia.html`

- [ ] **Step 3: Inspect the HTML**

```bash
head -20 /Users/pontz/cooking/public/recipes/2026-06-08-pasta-alla-gricia.html
```

Expected: comment block at top with recipe metadata, then `<!DOCTYPE html>` with correct meta tags.

- [ ] **Step 4: Verify on Vercel**

Wait ~60s after push, then open the URL Claude posted. Confirm:
- Page renders correctly
- Recipe name, date, serves visible
- Ingredients and method present
- Technique notes populated
- No template placeholders remain (`{recipe_name}`, etc.)

- [ ] **Step 5: Check git log**

```bash
git -C /Users/pontz/cooking log --oneline -3
```

Expected: commit for pasta alla gricia at top.
