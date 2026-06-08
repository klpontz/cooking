# Cooking Repo Design

**Date:** 2026-06-06
**Status:** Approved

## What This Is

A persistent cooking advisor and recipe library built on the /fin pattern: `CLAUDE.md` defines the advisor role, structured markdown directories hold context, and Claude provides reasoning across sessions. The epicure-mcp MCP server is wired in to give Claude live ingredient intelligence — pairing scores, flavor neighbors, cultural affinity — available in every session without manual invocation.

## Architecture

File-based advisor with MCP integration. No custom code. Everything is either markdown (data you write into) or HTML (compiled synthesis Claude maintains and serves for reading).

```
cooking/
├── CLAUDE.md                  # Advisor role + full cooking profile
├── overview.html              # Blueprint doc (HTML from day one, Vercel-ready)
├── .claude/
│   └── settings.json          # Epicure-mcp wired in as MCP server
├── recipes/                   # Recipes worth keeping, freeform markdown
│   └── YYYY-MM-DD-name.md
├── techniques/                # Technique notes — the "why it works" layer
├── pantry/
│   ├── staples.md             # Reliable pantry (guanciale, Parmesan, spices, etc.)
│   └── garden.md             # Homegrown ingredients, seasonal availability
├── log/                       # Cooking session notes, experiments, outcomes
│   └── YYYY/
├── wiki/                      # HTML — LLM-compiled synthesis, Vercel-ready
│   ├── index.html             # Catalog and navigation
│   ├── flavor-patterns.html   # Ingredient combos and techniques that keep working
│   └── seasonal.html          # Seasonal patterns and homegrown ingredient notes
└── meta/
    ├── sources.md             # Trusted references (Kenji, ATK, Hazan, McFadden, Mallmann)
    └── preferences.md        # Full flavor profile — cuisines, techniques, dislikes
```

## Directory Rationale

| Directory | Format | Purpose |
|-----------|--------|---------|
| `recipes/` | Markdown | Storage you write into — freeform, captured after cooking |
| `techniques/` | Markdown | The "why it works" layer — technique notes from trusted sources |
| `pantry/` | Markdown | Current pantry and garden state — informs substitution advice |
| `log/` | Markdown | Session notes and experiments — raw, quick to capture |
| `wiki/` | HTML | LLM-compiled synthesis — meant for reading, not editing |
| `meta/` | Markdown | Advisor calibration — preferences and sources |

Recipes, techniques, pantry, and log stay markdown because they're data you're actively writing. The wiki is HTML because it's compiled output meant to be read — the same reason the article on HTML effectiveness advocates for it. `overview.html` is HTML from day one so it's Vercel-ready when that work happens.

## Epicure-MCP Integration

Wired in via `.claude/settings.json` as an MCP server. Available tools:

- `pairing_score` — cosine affinity between two ingredients
- `find_pairings` — cluster and bridge graph for an ingredient
- `neighbors` — top-k flavor neighbors
- `cultural_profile` — cosine to each cuisine direction (Italian, Japanese, etc.)
- `compare_on_axis` — project two ingredients onto a flavor axis
- `morph` — SLERP toward a flavor direction or ingredient

Claude calls these automatically when relevant — substitution questions, pairing suggestions, "what cuisines does this ingredient lean toward?" — without the user invoking them manually.

## CLAUDE.md Role

Defines the advisor as a cooking assistant that:

- Knows the household's full flavor profile and who's at the table (see preferences.md)
- Defaults to trusted sources (Kenji, ATK, Hazan, McFadden, Mallmann) for technique questions
- Distinguishes between weeknight and weekend cooking contexts
- Uses epicure tools automatically for ingredient reasoning
- Captures recipes and technique notes on request
- Maintains the wiki layer by updating HTML articles when new patterns emerge

## Cooking Profile (compiled from prior conversations)

Baked into `meta/preferences.md` and referenced in `CLAUDE.md`:

- **Household:** Kevin, his partner, and their child. Recipes should work for the whole family unless noted.
- **Style:** Deep flavor and simple flavor are not opposites — the goal is few ingredients that sing. Strong technique over complexity. Not fussy.
- **Cadence:** Weekend for longer projects (braises, bread, pizza, fermentation). Weeknights need speed without sacrificing quality.
- **Family staples:** Pork tonkatsu, sesame tofu rice bowls, tacos, quick miso ramen — reliable, whole-family hits.
- **Cuisines:** Italian (primary), Japanese, Chinese, Mexican, Indian, Thai — cross-tradition borrowing welcome, fusion for its own sake not.
- **Techniques:** Spice-forward, quick pickling, fermentation, breadmaking, pizza, long braises, fire and open-flame cooking (Mallmann influence), crispy breadcrumb toppings, garlic in all forms.
- **Ingredients:** Guanciale, Parmesan, cured meats, bitter greens, fresh herbs, vinegar-driven flavors, umami-rich bases.
- **Garden herbs (fresh):** Rosemary, oregano, sage, thyme. Also grows onions/onion sets.
- **Dislikes:** Overly sweet dishes, mustard-forward preparations, anything that reads as "too French."
- **Cooking personality:** Adapts rather than follows. Starts with what's on hand. Turns components into something new. Asks about technique and flavor balance, not basic recipes.

## Future: Vercel / HTML Docs

`overview.html` and `wiki/` are structured for static hosting from day one. When ready: connect the repo to Vercel, point it at the root, done. No restructuring needed.

## What This Doesn't Do

- No live pantry sync or inventory management — pantry is manual markdown
- No recipe search or database — recipes are flat markdown files
- No custom tooling or scripts — everything is conversational
