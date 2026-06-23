# CLAUDE.md - Token Efficient Rules

1. Think before acting. Read existing files before writing code.
2. Be concise in output but thorough in reasoning.
3. Prefer editing over rewriting whole files.
4. Do not re-read files you have already read unless the file may have changed.
5. Test your code before declaring done.
6. No sycophantic openers or closing fluff.
7. Keep solutions simple and direct.
8. User instructions always override this file.

## gstack

Use the `/browse` skill from gstack for all web browsing. Never use `mcp__claude-in-chrome__*` tools.

Available gstack skills:

- **Planning & review**: `/office-hours`, `/autoplan`, `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review`, `/plan-devex-review`
- **Design**: `/design-consultation`, `/design-shotgun`, `/design-html`, `/design-review`
- **Code review & ship**: `/review`, `/codex`, `/ship`, `/land-and-deploy`, `/canary`, `/benchmark`
- **QA & browsing**: `/qa`, `/qa-only`, `/browse`, `/connect-chrome`, `/setup-browser-cookies`
- **Safety**: `/careful`, `/freeze`, `/guard`, `/unfreeze`, `/investigate`
- **Docs & release**: `/document-release`, `/document-generate`, `/retro`
- **Setup & maintenance**: `/setup-deploy`, `/setup-gbrain`, `/gstack-upgrade`, `/learn`
- **Security**: `/cso`
- **DevEx**: `/devex-review`

### PEIRS-specific usage

For the five-agent pipeline (A1-A5), prefer:

- `/office-hours` before adding a new agent or modifying the pipeline
- `/plan-eng-review` before architectural changes (LangGraph, FastAPI, traceability framework)
- `/review` after edits to any agent in `D:\DemocracIA\`
- `/qa` for the React/Vite frontend (port 5173) — use real browser tests
- `/cso` before exposing any endpoint that handles V-Dem, Freedom House, PEI, or RSF data
- `/freeze` when debugging a single agent to prevent cross-module edits
- `/ship` for releases to `github.com/lachmanmariana8-sudo/democracia-peirs`
