# Cooking → kevinrocci.com/cooking/ migration

Date: 2026-10-08. Status: approved, executed.

## Goal

Serve the cooking site at `kevinrocci.com/cooking/`, the professional site at
`kevinrocci.com/work/`, and a landing page at `kevinrocci.com/` that links to
both. Retire the Vercel deployment.

## Decisions

- **Host:** Bluehost, for one host and one bill. Vercel is retired.
- **Repos:** two repos, one host. The `kevinrocci.com` repo owns `/` and
  `/work/`. The `cooking` repo owns `/cooking/`. Neither repo contains the
  other's folder. SFTP never deletes on the server, so neither deploy can erase
  the other's files.
- **Pro URL:** `/work/`. The existing `/work/hiring-automation/` nests under it.
- **Landing style:** pure cooking style. Georgia, `#1a1a1a` on white, a 680px
  column. No palette borrowing.
- **Links:** all cooking links are relative, so the site works under any base
  path.
- **Payload allowlist:** cooking uploads only `index.html`, `public/`, and
  `wiki/`. Private notes (`CLAUDE.md`, `pantry/`, `log/`, `meta/`, `tools/`,
  `overview.html`) stay local. Vercel served all of them before.

## Changes

Cooking repo:
- `index.html`, `public/recipes/*.html`: relative links.
- `.claude/skills/recipe/SKILL.md`: relative link template, runs `./deploy.sh`
  after push, returns the kevinrocci.com URL.
- `deploy.sh`: SFTP batch upload of the allowlist. Refuses any `REMOTE_DIR`
  that does not end in `/cooking`.
- `vercel.json`: permanent redirect of every path to
  `https://kevinrocci.com/cooking/<path>`.

kevinrocci.com repo:
- `index.html` → `work/index.html`, with asset paths prefixed `../`.
- New root `index.html`: the landing page.
- `work/hiring-automation/index.html`: back links point to `../` (Work).
- `deploy.sh`: SFTP batch uploads `work/index.html`.

## Rollout

1. Deploy cooking to `/cooking/`. Nothing links there yet.
2. Deploy the pro restructure. `/` becomes the landing page.
3. Push the Vercel redirect.

## Verification

- Local: assemble the production tree, crawl every link, check in a browser at
  desktop and mobile widths.
- Live: crawl from `https://kevinrocci.com/`, expect no non-200s.
  `/cooking/CLAUDE.md`, `/cooking/pantry/staples.md`, and
  `/cooking/overview.html` return 404. The old Vercel URL redirects.

## Follow-ups

- Delete the Vercel project after about a month.
- Old deep links such as `/#experience` land on the landing page without the
  anchor. Accepted.
