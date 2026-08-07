# AGENTS.md

## Skill Discovery
- Skills live in `.agents/skills/`. Installed: `documentation-writer`, `find-skills`, `grill-me`, `ponytail`, `research`.
- If a task needs a capability none of these cover, use `find-skills` to search the registry (`npx skills find <query>`) before writing custom logic from scratch.
- Update installed skills periodically with `npx skills update`.

## Always-On Skill

### `ponytail` — default coding posture
Active on every coding task (write, add, refactor, fix, review, design) unless the user says "stop ponytail." Climb the ladder before writing code: skip speculative work (YAGNI) → reuse existing code in-repo → stdlib → native platform feature → already-installed dependency → one-liner → minimum custom code. Ship the lazy-but-correct version, name what was skipped and when to add it back. Never skip: validation at trust boundaries, error handling, security, accessibility, anything explicitly requested. Default intensity `full`; use `lite`/`ultra` if asked.

## Task-Triggered Skills

### `research`
Trigger: the user wants a topic investigated, docs/API facts gathered, or reading legwork delegated.
Spin up a background agent, chase claims to **primary sources only** (official docs, source, specs — not secondary write-ups), and write findings to a single cited Markdown file, saved wherever the repo already keeps such notes.

### `grill-me`
Trigger: only on explicit invocation (`disable-model-invocation: true` — never auto-triggers).
Runs a `/grilling` session: a relentless interview to pressure-test a plan or design before committing to it. Use before locking in architecture decisions, not as a general code review step.

### `documentation-writer`
Trigger: writing or restructuring docs (tutorials, how-tos, reference, explanation).
Follows the Diátaxis framework strictly. Workflow: (1) clarify doc type, audience, goal, and scope before writing anything, (2) propose an outline and wait for approval, (3) write full Markdown only after approval. Use existing repo Markdown as tone/terminology context, but never copy from it unless asked.

### `find-skills`
Trigger: the user asks "how do I do X," "is there a skill for X," or wants capabilities extended.
Check the skills.sh leaderboard first, then `npx skills find [query]`, verify install count (prefer 1K+) and source reputation before recommending, then offer `npx skills add <owner/repo@skill>` on request.

## Workflow
1. Identify task type → match to a trigger above.
2. `ponytail` applies underneath any coding task regardless of which other skill fires.
3. For investigation → `research`. For docs → `documentation-writer`. For plan/design pressure-testing → `grill-me` (explicit only). For "does a skill exist for this" → `find-skills`.
4. If nothing matches, do the task directly with general capabilities and suggest creating a new skill (`npx skills init`) if it's likely to recur.

<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
