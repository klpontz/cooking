# Cooking Repo Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap the /cooking repo — file structure, CLAUDE.md advisor role, epicure-mcp wired in as a live MCP server, and all context files populated from the approved cooking profile.

**Architecture:** File-based advisor (no custom code) modeled on /fin. Markdown for data you write into; HTML for compiled synthesis. Epicure-mcp runs as a local HTTP server; Claude Code connects to it via URL in `.claude/settings.json`. Everything committed to git.

**Tech Stack:** Markdown, HTML, Python 3.12+ (epicure-mcp), uvicorn, git, macOS launchd (optional auto-start).

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `.gitignore` | Create | Ignore venv, pyc, DS_Store |
| `.claude/settings.json` | Create | Wire epicure-mcp HTTP endpoint |
| `CLAUDE.md` | Create | Advisor role + behavioral rules |
| `meta/preferences.md` | Create | Full cooking profile |
| `meta/sources.md` | Create | Trusted references |
| `pantry/staples.md` | Create | Reliable pantry inventory |
| `pantry/garden.md` | Create | Fresh herbs and homegrown |
| `recipes/.keep` | Create | Scaffold empty dir |
| `techniques/.keep` | Create | Scaffold empty dir |
| `log/2026/.keep` | Create | Scaffold log dir |
| `tools/epicure-mcp/` | Clone | MCP server source |
| `bin/epicure` | Create | Shell script to start server |
| `wiki/index.html` | Create | Wiki navigation |
| `wiki/flavor-patterns.html` | Create | Compiled flavor patterns |
| `wiki/seasonal.html` | Create | Seasonal ingredient notes |
| `overview.html` | Create | Blueprint doc |

---

### Task 1: Git init and .gitignore

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Initialize git repo**

```bash
cd /Users/pontz/cooking
git init
```

Expected: `Initialized empty Git repository in /Users/pontz/cooking/.git/`

- [ ] **Step 2: Create .gitignore**

Create `/Users/pontz/cooking/.gitignore`:

```
# Python
tools/epicure-mcp/.venv/
tools/epicure-mcp/__pycache__/
tools/epicure-mcp/src/**/__pycache__/
*.pyc
*.pyo

# macOS
.DS_Store

# Editor
.idea/
.vscode/
```

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: init repo with gitignore"
```

---

### Task 2: Clone and install epicure-mcp

**Files:**
- Create: `tools/epicure-mcp/` (cloned repo)
- Create: `bin/epicure`

- [ ] **Step 1: Create tools dir and clone**

```bash
mkdir -p /Users/pontz/cooking/tools
cd /Users/pontz/cooking/tools
git clone https://github.com/KAIKAKU-AI/epicure-mcp.git
```

Expected: repo cloned to `tools/epicure-mcp/`

- [ ] **Step 2: Set up Python venv**

```bash
cd /Users/pontz/cooking/tools/epicure-mcp
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e "."
```

Expected: installs mcp, starlette, uvicorn, numpy, pandas, etc. No errors.

- [ ] **Step 3: Verify server starts**

```bash
cd /Users/pontz/cooking/tools/epicure-mcp
source .venv/bin/activate
python -m epicure_mcp.server &
sleep 2
curl -s http://localhost:8080/healthz
kill %1
```

Expected: `{"status":"ok"}` (or similar). If you see a connection error, check that port 8080 is free: `lsof -i :8080`.

- [ ] **Step 4: Create bin/epicure start script**

Create `/Users/pontz/cooking/bin/epicure`:

```bash
#!/usr/bin/env bash
# Starts the epicure-mcp server on localhost:8080.
# Run this before a Claude Code cooking session.
set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$REPO_ROOT/tools/epicure-mcp/.venv"
cd "$REPO_ROOT/tools/epicure-mcp"
source "$VENV/bin/activate"
exec python -m epicure_mcp.server
```

```bash
chmod +x /Users/pontz/cooking/bin/epicure
```

- [ ] **Step 5: Verify script works**

```bash
/Users/pontz/cooking/bin/epicure &
sleep 2
curl -s http://localhost:8080/healthz
kill %1
```

Expected: health check returns ok.

- [ ] **Step 6: Commit**

```bash
cd /Users/pontz/cooking
git add tools/ bin/
git commit -m "feat: add epicure-mcp server and start script"
```

---

### Task 3: Configure Claude Code MCP settings

**Files:**
- Create: `.claude/settings.json`

The epicure-mcp server runs at `http://localhost:8080/mcp` (Streamable HTTP transport). Claude Code connects to it via URL. The server must be running before starting a cooking session — run `bin/epicure` in a separate terminal, or set up launchd (see optional step).

- [ ] **Step 1: Create .claude directory**

```bash
mkdir -p /Users/pontz/cooking/.claude
```

- [ ] **Step 2: Create settings.json**

Create `/Users/pontz/cooking/.claude/settings.json`:

```json
{
  "mcpServers": {
    "epicure": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

- [ ] **Step 3: (Optional) Create launchd plist for auto-start**

If you want epicure-mcp to start automatically at login, create `~/Library/LaunchAgents/com.pontz.epicure-mcp.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.pontz.epicure-mcp</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/pontz/cooking/bin/epicure</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/epicure-mcp.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/epicure-mcp.err</string>
</dict>
</plist>
```

Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.pontz.epicure-mcp.plist
```

Verify: `curl -s http://localhost:8080/healthz`

- [ ] **Step 4: Commit**

```bash
cd /Users/pontz/cooking
git add .claude/
git commit -m "feat: configure epicure-mcp as Claude Code MCP server"
```

---

### Task 4: Create CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Create CLAUDE.md**

Create `/Users/pontz/cooking/CLAUDE.md`:

```markdown
# Cooking Advisor

## Role

You are a personal cooking advisor for Kevin and his family.
Advisory style: direct, technique-grounded, flavor-driven.

When Kevin asks a question, give a specific recommendation — not "it depends."
Show the reasoning when technique matters. Flag assumptions when you make them.

## Household

- **Kevin** — primary cook, adapts rather than follows recipes, asks about technique and flavor balance
- **Partner** — Kevin's partner
- **Kid** — their child
- Most recipes should work for the whole family unless Kevin notes otherwise

## Cooking Style

The goal is few ingredients that sing. Deep flavor and simple flavor are not opposites.
Strong technique over complexity. Not fussy.

**Cadence:**
- Weeknights: fast, no sacrifice on quality. 30–45 min max.
- Weekends: longer projects are welcome — braises, bread, pizza, fermentation, fire.

**Family staples (reliable hits for everyone):** pork tonkatsu, sesame tofu rice bowls, tacos, quick miso ramen.

## Flavor Profile

**Cuisines:** Italian (primary), Japanese, Chinese, Mexican, Indian, Thai.
Cross-tradition borrowing is welcome. Fusion for its own sake is not.

**Techniques Kevin uses:** spice-forward preparations, quick pickling, fermentation, breadmaking, pizza dough, long braises, open-flame/fire cooking (Mallmann influence), crispy breadcrumb toppings, garlic in all forms (fresh, fried, crispy, freeze-dried).

**Ingredients Kevin reaches for:** guanciale, Parmesan, cured meats, bitter greens, fresh herbs, vinegar-driven flavors, umami-rich bases.

**Garden (fresh, currently growing):** rosemary, oregano, sage, thyme, onions/onion sets.

**Dislikes:** overly sweet dishes, mustard-forward preparations, anything that reads as "too French."

## Trusted Sources

When technique questions arise, default to these sources. Cite them when relevant.

- **J. Kenji López-Alt** — The Food Lab, The Wok; technique-first, evidence-based
- **America's Test Kitchen / Cook's Illustrated** — reliable, tested, explains why
- **Marcella Hazan** — Essentials of Classic Italian Cooking; Italian fundamentals
- **Joshua McFadden** — Six Seasons; vegetable-forward, seasonal
- **Francis Mallmann** — Seven Fires, Mallmann on Fire; open-flame, live-fire, rustic Argentine technique

## Ingredient Intelligence (epicure-mcp)

You have access to the Epicure ingredient embedding model via MCP tools. Use these automatically — do not ask Kevin to invoke them.

**When to use:**
- Substitution questions → `neighbors` (top-k flavor neighbors) + `pairing_score`
- "What goes with X?" → `find_pairings`
- Cultural fit of an ingredient → `cultural_profile`
- Flavor axis comparisons → `compare_on_axis`
- Exploring a flavor direction → `morph`

Ingredient names must be lowercase and canonical (e.g., "guanciale", "parmesan", "fresh thyme"). Use `neighbors` to verify a name resolves before using other tools.

## Repo Files

- `meta/preferences.md` — full cooking profile (read for context on any session)
- `meta/sources.md` — annotated reference list
- `pantry/staples.md` — pantry inventory
- `pantry/garden.md` — fresh herbs and homegrown ingredients
- `recipes/` — recipes worth keeping, markdown, YYYY-MM-DD-name.md format
- `techniques/` — technique notes
- `log/YYYY/` — session notes, experiments, outcomes
- `wiki/` — HTML synthesis articles you maintain (see below)

## Wiki Maintenance

The `wiki/` directory holds HTML articles you compile and maintain. Update them during sessions when new patterns emerge — a flavor combination that keeps working, a technique that generalizes, a seasonal observation.

Articles:
- `wiki/flavor-patterns.html` — ingredient combos and techniques that keep working
- `wiki/seasonal.html` — seasonal and garden ingredient notes
- `wiki/index.html` — catalog and navigation

Keep articles tight. Update rather than append. The wiki is for synthesis, not raw notes — those go in `log/`.

## Advisory Rules

- Give specific recommendations, not "it depends"
- Weeknight vs. weekend context matters — always ask if it's unclear
- If Kevin mentions what's in the pantry or garden, use it
- When using epicure tools, show interesting findings inline (e.g., "guanciale's closest flavor neighbors are pancetta, lardo, and nduja")
- Don't volunteer unrelated cooking advice — answer what's asked
- When uncertain, state confidence level (high / moderate / low)
```

- [ ] **Step 2: Verify file looks right**

```bash
wc -l /Users/pontz/cooking/CLAUDE.md
```

Expected: ~90 lines. Open in a browser or editor and scan for formatting issues.

- [ ] **Step 3: Commit**

```bash
cd /Users/pontz/cooking
git add CLAUDE.md
git commit -m "feat: add CLAUDE.md cooking advisor role"
```

---

### Task 5: Create meta/ files

**Files:**
- Create: `meta/preferences.md`
- Create: `meta/sources.md`

- [ ] **Step 1: Create meta directory**

```bash
mkdir -p /Users/pontz/cooking/meta
```

- [ ] **Step 2: Create preferences.md**

Create `/Users/pontz/cooking/meta/preferences.md`:

```markdown
# Cooking Preferences

## Household

Kevin (primary cook), his partner, and their child. Most meals are for all three.
Kevin cooks; the family eats. Flag if a recipe skews too spicy or unfamiliar for a family meal.

## Style

Few ingredients that sing. Deep flavor and simple flavor are not opposites.
Technique over complexity. Not fussy. No unnecessary steps.

## Cadence

- **Weeknights:** 30–45 min max. Fast, no sacrifice on quality.
- **Weekends:** Longer projects welcome — braises, bread, dough, fermentation, fire.

## Family Staples

Reliable hits that work for everyone:

- Pork tonkatsu
- Sesame tofu rice bowls
- Tacos
- Quick miso ramen

## Cuisines

**Primary:** Italian
**Also:** Japanese, Chinese, Mexican, Indian, Thai

Cross-tradition technique borrowing is welcome. Fusion for its own sake is not.
The strongest single theme: rustic, savory, balanced — a few ingredients doing heavy work.

## Techniques

- Spice-forward preparations
- Quick pickling
- Fermentation
- Breadmaking and pizza dough (homemade)
- Long braises and slow roasting
- Open-flame / fire cooking (Mallmann influence)
- Crispy breadcrumb toppings
- Garlic in all forms: fresh, fried, crispy, freeze-dried

## Ingredients Kevin Reaches For

- Guanciale, pancetta, cured meats
- Parmesan, aged hard cheeses
- Bitter greens (radicchio, escarole, dandelion)
- Fresh herbs (rosemary, oregano, sage, thyme — all currently growing)
- Vinegar-driven flavors
- Umami bases: fish sauce, soy, miso, anchovies, Parmesan rind

## Garden (Currently Growing)

- Rosemary
- Oregano
- Sage
- Thyme
- Onions / onion sets

## Dislikes

- Overly sweet preparations
- Mustard-forward dishes
- Dijon-heavy sauces
- Anything that reads as "too French" — one previous vinegar chicken recipe was too sweet, too mustardy, too refined
- Fusion for its own sake

## Cooking Personality

Adapts rather than follows. Starts with what's on hand. Turns components and leftovers into something new.
Asks about technique, timing, and flavor balance — not how to boil water.
Understands why techniques work; sources matter.
```

- [ ] **Step 3: Create sources.md**

Create `/Users/pontz/cooking/meta/sources.md`:

```markdown
# Trusted Sources

These are the references Kevin returns to. When technique questions come up, default to these.
Cite the source and the reasoning — not just the answer.

## Authors and Books

**J. Kenji López-Alt**
- *The Food Lab* (2015) — technique-first, evidence-based American and European cooking
- *The Wok* (2022) — stir-fry technique, Chinese-American cooking, high heat
- Why: Explains the science behind technique. Replaces "that's how it's done" with "here's why."

**America's Test Kitchen / Cook's Illustrated**
- Continuous publication; online at cooksillustrated.com
- Why: Extensively tested recipes that explain every decision. Reliable for unfamiliar territory.

**Marcella Hazan**
- *Essentials of Classic Italian Cooking* (1992) — the Italian fundamentals reference
- Why: Rustic, simple, technique-grounded. Few ingredients, maximum flavor. Kevin's Italian north star.

**Joshua McFadden**
- *Six Seasons: A New Way with Vegetables* (2017)
- *Six Seasons of Pasta* — pasta and vegetable-forward
- Why: Seasonal, produce-driven, teaches you to see vegetables as the main event.

**Francis Mallmann**
- *Seven Fires: Grilling the Argentine Way* (2009)
- *Mallmann on Fire* (2014)
- Why: Open-flame, live-fire, rustic Argentine technique. Ember cooking, whole animals, fire as a flavor ingredient. Influences Kevin's approach to weekend fire cooking.

## Technique Hierarchy

For technique disputes, prioritize in this order:
1. Kenji (science-based explanation)
2. ATK/Cook's Illustrated (tested, reliable)
3. Hazan (Italian tradition)
4. McFadden (seasonal vegetables)
5. Mallmann (fire technique)

For general technique that none of them cover, state confidence level explicitly.
```

- [ ] **Step 4: Commit**

```bash
cd /Users/pontz/cooking
git add meta/
git commit -m "feat: add meta preferences and sources"
```

---

### Task 6: Create pantry/ files

**Files:**
- Create: `pantry/staples.md`
- Create: `pantry/garden.md`

- [ ] **Step 1: Create pantry directory**

```bash
mkdir -p /Users/pontz/cooking/pantry
```

- [ ] **Step 2: Create staples.md**

Create `/Users/pontz/cooking/pantry/staples.md`:

```markdown
# Pantry Staples

Last updated: 2026-06-06

These are reliable on-hand ingredients. Update this file when something runs out or a new staple gets added.

## Cured Meats and Umami

- Guanciale
- Parmesan (wedge, not pre-grated)
- Anchovies (oil-packed)
- Miso (white and/or red)
- Fish sauce
- Soy sauce / tamari

## Pantry

- Dried pasta (various shapes)
- Arborio rice
- Japanese short-grain rice
- Panko breadcrumbs
- Canned whole San Marzano tomatoes
- Dried chiles (various)
- Chickpeas (dried and canned)

## Acids

- Red wine vinegar
- Sherry vinegar
- Rice wine vinegar
- Lemons

## Oils and Fats

- Extra-virgin olive oil
- Neutral oil (grapeseed or avocado)
- Toasted sesame oil

## Spices

- Black pepper (whole and ground)
- Cumin (whole and ground)
- Coriander (whole and ground)
- Smoked paprika
- Dried chili flakes
- Fennel seeds
- Dried oregano

## Notes

Kevin adapts based on what's on hand. If an ingredient below is missing, check with Claude about substitutions rather than making a special trip.
```

- [ ] **Step 3: Create garden.md**

Create `/Users/pontz/cooking/pantry/garden.md`:

```markdown
# Garden

Last updated: 2026-06-06

Fresh herbs and homegrown ingredients currently available.
Update this file seasonally or when something comes or goes.

## Fresh Herbs (Currently Growing)

- Rosemary
- Oregano
- Sage
- Thyme

## Vegetables

- Onions / onion sets (currently growing)

## Notes

Fresh herbs from the garden are preferred over dried when available.
The epicure-mcp `neighbors` tool can suggest pairings for whatever's abundant.
When something is in season or heavy, log it in `log/YYYY/` for the wiki.
```

- [ ] **Step 4: Commit**

```bash
cd /Users/pontz/cooking
git add pantry/
git commit -m "feat: add pantry and garden files"
```

---

### Task 7: Scaffold recipes/, techniques/, log/

**Files:**
- Create: `recipes/.keep`
- Create: `techniques/.keep`
- Create: `log/2026/.keep`

- [ ] **Step 1: Create directories and placeholders**

```bash
mkdir -p /Users/pontz/cooking/recipes
mkdir -p /Users/pontz/cooking/techniques
mkdir -p /Users/pontz/cooking/log/2026
touch /Users/pontz/cooking/recipes/.keep
touch /Users/pontz/cooking/techniques/.keep
touch /Users/pontz/cooking/log/2026/.keep
```

- [ ] **Step 2: Commit**

```bash
cd /Users/pontz/cooking
git add recipes/ techniques/ log/
git commit -m "chore: scaffold recipes, techniques, and log directories"
```

---

### Task 8: Create wiki/ HTML files

**Files:**
- Create: `wiki/index.html`
- Create: `wiki/flavor-patterns.html`
- Create: `wiki/seasonal.html`

- [ ] **Step 1: Create wiki directory**

```bash
mkdir -p /Users/pontz/cooking/wiki
```

- [ ] **Step 2: Create shared CSS (inline in each file — no separate stylesheet needed)**

The wiki uses a consistent minimal style: dark background optional, readable body width, good typography. Inline CSS per file keeps files self-contained for Vercel.

- [ ] **Step 3: Create wiki/flavor-patterns.html**

Create `/Users/pontz/cooking/wiki/flavor-patterns.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Flavor Patterns — Cooking Wiki</title>
  <style>
    body { font-family: Georgia, serif; max-width: 720px; margin: 40px auto; padding: 0 20px; color: #1a1a1a; line-height: 1.7; }
    h1 { font-size: 1.8rem; border-bottom: 2px solid #1a1a1a; padding-bottom: 8px; }
    h2 { font-size: 1.2rem; margin-top: 2rem; color: #444; }
    nav { margin-bottom: 2rem; font-size: 0.9rem; }
    nav a { color: #555; text-decoration: none; margin-right: 1rem; }
    nav a:hover { text-decoration: underline; }
    .entry { border-left: 3px solid #ddd; padding-left: 1rem; margin: 1.5rem 0; }
    .meta { font-size: 0.8rem; color: #888; margin-bottom: 0.5rem; }
    .empty { color: #aaa; font-style: italic; }
  </style>
</head>
<body>
  <nav><a href="index.html">← Index</a></nav>
  <h1>Flavor Patterns</h1>
  <p>Ingredient combinations and techniques that keep working. Updated by Claude during cooking sessions.</p>

  <h2>Combinations</h2>
  <p class="empty">No entries yet. After your first few sessions, Claude will populate this with combinations worth remembering.</p>

  <h2>Techniques</h2>
  <p class="empty">No entries yet.</p>

  <h2>Cross-Cuisine Moves</h2>
  <p class="empty">No entries yet.</p>
</body>
</html>
```

- [ ] **Step 4: Create wiki/seasonal.html**

Create `/Users/pontz/cooking/wiki/seasonal.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Seasonal Notes — Cooking Wiki</title>
  <style>
    body { font-family: Georgia, serif; max-width: 720px; margin: 40px auto; padding: 0 20px; color: #1a1a1a; line-height: 1.7; }
    h1 { font-size: 1.8rem; border-bottom: 2px solid #1a1a1a; padding-bottom: 8px; }
    h2 { font-size: 1.2rem; margin-top: 2rem; color: #444; }
    nav { margin-bottom: 2rem; font-size: 0.9rem; }
    nav a { color: #555; text-decoration: none; margin-right: 1rem; }
    nav a:hover { text-decoration: underline; }
    .season { border-left: 3px solid #ddd; padding-left: 1rem; margin: 1.5rem 0; }
    .empty { color: #aaa; font-style: italic; }
  </style>
</head>
<body>
  <nav><a href="index.html">← Index</a></nav>
  <h1>Seasonal Notes</h1>
  <p>Seasonal patterns, what's in the garden, and how to use it. Updated by Claude as sessions accumulate.</p>

  <h2>Garden — Current (June 2026)</h2>
  <div class="season">
    <p><strong>Fresh herbs:</strong> Rosemary, oregano, sage, thyme</p>
    <p><strong>Vegetables:</strong> Onions / onion sets</p>
  </div>

  <h2>Seasonal Observations</h2>
  <p class="empty">No entries yet. Claude will add observations here when seasonal patterns emerge across sessions.</p>
</body>
</html>
```

- [ ] **Step 5: Create wiki/index.html**

Create `/Users/pontz/cooking/wiki/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cooking Wiki</title>
  <style>
    body { font-family: Georgia, serif; max-width: 720px; margin: 40px auto; padding: 0 20px; color: #1a1a1a; line-height: 1.7; }
    h1 { font-size: 1.8rem; border-bottom: 2px solid #1a1a1a; padding-bottom: 8px; }
    h2 { font-size: 1.2rem; margin-top: 2rem; color: #444; }
    ul { padding-left: 1.2rem; }
    li { margin: 0.5rem 0; }
    a { color: #1a1a1a; }
    a:hover { color: #555; }
    .desc { font-size: 0.9rem; color: #666; margin-left: 0.5rem; }
    footer { margin-top: 3rem; font-size: 0.8rem; color: #aaa; border-top: 1px solid #eee; padding-top: 1rem; }
  </style>
</head>
<body>
  <h1>Cooking Wiki</h1>
  <p>LLM-compiled synthesis across sessions. Claude maintains these articles; you don't edit them directly. Raw notes go in <code>log/</code>.</p>

  <h2>Articles</h2>
  <ul>
    <li>
      <a href="flavor-patterns.html">Flavor Patterns</a>
      <span class="desc">— Ingredient combos and techniques that keep working</span>
    </li>
    <li>
      <a href="seasonal.html">Seasonal Notes</a>
      <span class="desc">— What's in the garden, seasonal patterns</span>
    </li>
  </ul>

  <h2>Repo Map</h2>
  <ul>
    <li><code>CLAUDE.md</code> — Advisor role and rules</li>
    <li><code>meta/preferences.md</code> — Full cooking profile</li>
    <li><code>meta/sources.md</code> — Trusted references</li>
    <li><code>pantry/staples.md</code> — Pantry inventory</li>
    <li><code>pantry/garden.md</code> — Fresh herbs and homegrown</li>
    <li><code>recipes/</code> — Recipes worth keeping (YYYY-MM-DD-name.md)</li>
    <li><code>techniques/</code> — Technique notes</li>
    <li><code>log/YYYY/</code> — Session notes and experiments</li>
  </ul>

  <footer>Updated by Claude during cooking sessions.</footer>
</body>
</html>
```

- [ ] **Step 6: Verify all three files open correctly in browser**

```bash
open /Users/pontz/cooking/wiki/index.html
```

Check: navigation links work, typography is readable, no broken elements.

- [ ] **Step 7: Commit**

```bash
cd /Users/pontz/cooking
git add wiki/
git commit -m "feat: add wiki HTML files (index, flavor-patterns, seasonal)"
```

---

### Task 9: Create overview.html

**Files:**
- Create: `overview.html`

- [ ] **Step 1: Create overview.html**

Create `/Users/pontz/cooking/overview.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cooking — Personal Advisor System</title>
  <style>
    body { font-family: Georgia, serif; max-width: 760px; margin: 40px auto; padding: 0 24px; color: #1a1a1a; line-height: 1.75; }
    h1 { font-size: 2rem; border-bottom: 2px solid #1a1a1a; padding-bottom: 10px; margin-bottom: 0.5rem; }
    .subtitle { color: #666; margin-top: 0; margin-bottom: 2rem; }
    h2 { font-size: 1.25rem; margin-top: 2.5rem; border-left: 4px solid #1a1a1a; padding-left: 12px; }
    h3 { font-size: 1rem; color: #444; margin-top: 1.5rem; }
    code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
    pre { background: #f4f4f4; padding: 1rem; border-radius: 4px; overflow-x: auto; font-size: 0.85em; line-height: 1.5; }
    table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
    th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #ddd; }
    th { font-size: 0.85rem; color: #666; font-weight: normal; text-transform: uppercase; letter-spacing: 0.05em; }
    ul { padding-left: 1.2rem; }
    li { margin: 0.4rem 0; }
    a { color: #1a1a1a; }
    .note { background: #fffbea; border-left: 4px solid #f0c040; padding: 0.75rem 1rem; margin: 1.5rem 0; font-size: 0.95rem; }
  </style>
</head>
<body>

  <h1>Cooking</h1>
  <p class="subtitle">A personal cooking advisor and recipe library. Persistent context, ingredient intelligence, and a structured place for everything worth keeping.</p>

  <h2>Why This Exists</h2>

  <p>Most recipe apps are optimized for discovery, not memory. They don't know you already make a great tonkatsu, that you have rosemary in the garden right now, that you hate anything that reads as "too French," or that it's Tuesday night and you have 40 minutes.</p>

  <p>This system does. It holds your full cooking profile — preferences, pantry, trusted sources, past experiments — and reasons from it. The goal is an advisor that knows your kitchen as well as you do.</p>

  <h2>What This Is</h2>

  <p>Claude Code loads <code>CLAUDE.md</code> at session start. Combined with structured context files and the Epicure ingredient embedding model (wired in as a live MCP server), each session has:</p>

  <ul>
    <li>Your full cooking profile — household, style, cuisines, techniques, dislikes</li>
    <li>Current pantry and garden state</li>
    <li>Trusted technique sources (Kenji, Hazan, ATK, McFadden, Mallmann)</li>
    <li>Ingredient intelligence — flavor neighbors, pairing scores, cultural affinities</li>
    <li>A growing recipe library and log of past sessions</li>
  </ul>

  <h2>Repo Structure</h2>

  <pre>cooking/
├── CLAUDE.md                  # Advisor role + behavioral rules
├── overview.html              # This file
├── .claude/
│   └── settings.json          # Epicure-mcp wired in as MCP server
├── recipes/                   # Recipes worth keeping (YYYY-MM-DD-name.md)
├── techniques/                # Technique notes — the "why it works" layer
├── pantry/
│   ├── staples.md             # Reliable pantry inventory
│   └── garden.md             # Fresh herbs and homegrown
├── log/YYYY/                  # Session notes, experiments, outcomes
├── wiki/                      # HTML — LLM-compiled synthesis
│   ├── index.html
│   ├── flavor-patterns.html
│   └── seasonal.html
├── meta/
│   ├── preferences.md        # Full cooking profile
│   └── sources.md            # Trusted references
└── tools/
    └── epicure-mcp/           # Ingredient embedding MCP server</pre>

  <table>
    <tr><th>Directory</th><th>Format</th><th>Purpose</th></tr>
    <tr><td><code>recipes/</code></td><td>Markdown</td><td>Storage you write into — captured after cooking</td></tr>
    <tr><td><code>techniques/</code></td><td>Markdown</td><td>Technique notes from trusted sources</td></tr>
    <tr><td><code>pantry/</code></td><td>Markdown</td><td>Current pantry and garden — informs substitution advice</td></tr>
    <tr><td><code>log/</code></td><td>Markdown</td><td>Session notes and experiments — raw, quick to capture</td></tr>
    <tr><td><code>wiki/</code></td><td>HTML</td><td>Compiled synthesis — meant for reading, not editing</td></tr>
    <tr><td><code>meta/</code></td><td>Markdown</td><td>Advisor calibration — preferences and sources</td></tr>
  </table>

  <h2>Epicure Ingredient Intelligence</h2>

  <p>The Epicure model embeds 1,790 ingredients as 300-dimensional vectors trained on 4.14M recipes. Claude has access to it as a live MCP server and uses it automatically — you don't invoke it manually.</p>

  <table>
    <tr><th>Tool</th><th>When Claude uses it</th></tr>
    <tr><td><code>neighbors</code></td><td>Substitution questions — finds closest flavor neighbors</td></tr>
    <tr><td><code>find_pairings</code></td><td>"What goes with X?" — cluster and bridge graph</td></tr>
    <tr><td><code>pairing_score</code></td><td>Checking affinity between two specific ingredients</td></tr>
    <tr><td><code>cultural_profile</code></td><td>Which cuisine an ingredient fits best</td></tr>
    <tr><td><code>compare_on_axis</code></td><td>Comparing two ingredients on a named flavor axis</td></tr>
    <tr><td><code>morph</code></td><td>Exploring a flavor direction from a starting ingredient</td></tr>
  </table>

  <div class="note">The epicure-mcp server must be running before a session. Run <code>bin/epicure</code> in a terminal, or install the launchd plist to auto-start it at login.</div>

  <h2>How to Use It</h2>

  <h3>Weeknight question</h3>
  <p>Open a Claude Code session in <code>/cooking</code>. Ask something. The advisor knows your profile, your pantry, and your time constraints. It will give a specific recommendation — not "it depends."</p>

  <h3>Saving a recipe</h3>
  <p>Tell Claude to save it: "save this as a recipe." It creates <code>recipes/YYYY-MM-DD-name.md</code> with what you made, the source, and any notes.</p>

  <h3>Logging a session</h3>
  <p>After an experiment, log what happened: "log tonight — I made X, changed Y, result was Z." Claude writes it to <code>log/YYYY/MM-DD.md</code> and updates the wiki if there's a pattern worth noting.</p>

  <h2>The Wiki Layer</h2>

  <p>The <code>wiki/</code> directory is compiled synthesis — Claude maintains it, you don't write to it directly. Raw notes go in <code>log/</code>. The wiki is where patterns become visible: flavor combinations that keep working, seasonal observations, cross-cuisine moves that generalize.</p>

  <p>It starts sparse and fills in over time. That's correct.</p>

  <h2>Future: Public Docs</h2>

  <p><code>overview.html</code> and <code>wiki/</code> are structured for static hosting. When ready: connect to Vercel, point at the root, done. No restructuring needed.</p>

</body>
</html>
```

- [ ] **Step 2: Verify in browser**

```bash
open /Users/pontz/cooking/overview.html
```

Check: table formatting, code blocks, note callout, all links intact.

- [ ] **Step 3: Commit**

```bash
cd /Users/pontz/cooking
git add overview.html
git commit -m "feat: add overview.html blueprint doc"
```

---

### Task 10: Final verification

- [ ] **Step 1: Verify full repo structure**

```bash
find /Users/pontz/cooking -not -path '*/\.git/*' -not -path '*/tools/epicure-mcp/.venv/*' -not -path '*/tools/epicure-mcp/data/*' | sort
```

Expected output should include all files from the file map above.

- [ ] **Step 2: Verify epicure-mcp connects to Claude Code**

Start the server:

```bash
/Users/pontz/cooking/bin/epicure &
sleep 2
curl -s http://localhost:8080/healthz
```

Open a Claude Code session in `/Users/pontz/cooking` and run:

```
what are the closest flavor neighbors to guanciale?
```

Claude should call the `neighbors` tool automatically and return results with ingredient names and similarity scores. If it doesn't call the tool, check that `.claude/settings.json` has the correct URL and that the server is running.

- [ ] **Step 3: Final commit — tag it**

```bash
cd /Users/pontz/cooking
git log --oneline
git tag v0.1.0 -m "Initial cooking repo setup"
```

---

## Self-Review Notes

**Spec coverage check:**

| Spec requirement | Task |
|-----------------|------|
| CLAUDE.md with advisor role | Task 4 |
| overview.html (HTML from day one) | Task 9 |
| .claude/settings.json with epicure-mcp | Task 3 |
| recipes/, techniques/, log/ directories | Task 7 |
| pantry/staples.md and garden.md | Task 6 |
| wiki/ HTML files (index, flavor-patterns, seasonal) | Task 8 |
| meta/preferences.md with full profile | Task 5 |
| meta/sources.md with Mallmann | Task 5 |
| git init | Task 1 |
| epicure-mcp cloned and installed | Task 2 |

All spec requirements covered. No placeholders in any task.
