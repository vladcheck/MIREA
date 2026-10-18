# Plan: opencode.jsonc → .omp migration (+ validation)

## Context

Repo `PEPiS` currently configures OpenCode via `opencode.jsonc` (2 skill paths + 2 MCP servers `kicad`, `kicad-copilot`) plus one project skill at `opencode/skills/review-pr-or-lab/SKILL.md`. OMP already auto-discovers `opencode.jsonc` through its `opencode` provider (priority 55), but the ask is an explicit native `.omp` copy so config is owned by OMP (priority 100), editor-validated, and independent of OpenCode discovery. End state: `.omp/mcp.json` with both servers, native skill coverage for `review-pr-or-lab`, documented handling of the two user-home skill dirs, and proof via `/mcp list`, `/mcp test`, and skill resolution.

## Approach

1. **Create `.omp/mcp.json` translating both servers verbatim (no behavior change).**
   - Add `$schema: https://raw.githubusercontent.com/can1357/oh-my-pi/main/packages/coding-agent/src/config/mcp-schema.json` + `mcpServers` map.
   - `kicad`: `{"type":"stdio","command":"node","args":["${HOME}/KiCAD-MCP-Server/dist/index.js"],"timeout":30000,"env":{"NODE_ENV":"production","LOG_LEVEL":"info","KICAD_AUTO_LAUNCH":"false","KICAD_MCP_DEV":"0","KICAD_BACKEND":"auto","KICAD_PYTHON":"/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3","PYTHONPATH":"/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/lib/python3.9/site-packages"}}`.
   - Rationale / mapping: opencode `type:local` → OMP `type:stdio`; opencode `command:[...]` split into OMP `command` (first element) + `args` (rest); opencode `environment` → OMP `env`; opencode `enabled:true` → omit (default enabled); opencode `timeout` in ms kept as-is.
   - `kicad-copilot`: `{"type":"stdio","command":"npx","args":["-y","kicad-copilot-mcp"],"timeout":120000}` with no `env`.
   - Keep names exactly `kicad`, `kicad-copilot`; do not merge, rename, or add `disabledServers`/`enabledServers`. Do not set `cwd`, `auth`, `oauth`, `headers`, `instructions`, or `requestIdFormat`.
   - If `${HOME}` expansion is unverified in this OMP build, fallback (pre-decided): replace with literal `/Users/valdemar_check` — unverified, confirm first (see Assumptions). Prefer `${HOME}` form; it is the documented discovery-time `${VAR}` expansion for OMP-native files.
2. **Give `review-pr-or-lab` a native skill slot without forking content.**
   - Preferred (no duplication): create `.omp/config.yml` with `skills: { customDirectories: ["./opencode/skills"] }` — unverified key shape, confirm first. Rationale: provider scanner is non-recursive `*/SKILL.md`, so pointing the scanner parent at existing `opencode/skills` exposes `review-pr-or-lab` with zero copy; native file wins over `opencode`-provider copy on name collision (custom-directory outranks provider).
   - Fallback if key shape differs or scanner rejects relative path (pre-decided): copy `opencode/skills/review-pr-or-lab/SKILL.md` → `.omp/skills/review-pr-or-lab/SKILL.md` byte-for-byte (frontmatter `name`, `description` required by native provider with `requireDescription:true`), keep opencode original in place; identical-body dedup is not relied upon across different paths.
   - Never rename the skill, never edit frontmatter/body, never nest deeper than `<root>/skills/<name>/SKILL.md`.
3. **Leave the two `{env:HOME}`-based user skill dirs out of project `.omp`.**
   - `~/github/agentic/kicad-happy/skills` and `~/github/zxkmm/kicad-harness` are user-home absolutes, not project content; do not commit them under `.omp/` and do not hardcode them in `.omp/config.yml`. They belong in user scope (`~/.omp/agent/config.yml` `skills.customDirectories` or `~/.omp/agent/skills/` symlinks) — document as manual follow-up only, do not create user files in this change. Project sessions still see them only if the user config opts in; that is intended.
   - Do not disable/set `enabledProviders` and do not add `disabledProviders`/`disabledExtensions`; default project roots stay enabled so nothing else stops loading.
4. **Validate shape offline before launching OMP.**
   - JSON-parse `.omp/mcp.json` and `.omp/config.yml` (if created); validate `mcp.json` against `packages/coding-agent/src/config/mcp-schema.json` (editor schema or `ajv`/`bun --eval` JSON-schema check). Failures: fix fields per `validateServerConfig` rules (`stdio` requires `command`, no `command`+`url` mix, known `type` only) — do not work around by switching transport.
   - Confirm no other `.omp/mcp.json`, `.omp/.mcp.json`, root `mcp.json`/`.mcp.json`, or `.opencode/mcp` shadows the new names (`grep -r kicad-copilot --include=*.json .` from repo root, read-only).

## Critical files & anchors

- `opencode.jsonc:1-32` — source of truth: skill paths + both MCP server stanzas and env values; every translated field traces here.
- `opencode/skills/review-pr-or-lab/SKILL.md:1-9` — only project skill; frontmatter `name`/`description` must survive migration verbatim.
- `.omp/mcp.json` (new) — native MCP target; OMP reads project `.omp/mcp.json` before user `mcp.json`.
- `.omp/config.yml` (new, only if customDirectories path chosen) — project settings layer; verify key name against `omp config list` schema before writing.
- `AGENTS.md` (repo root) — existing project context via `agents-md` provider; untouched, but confirms project-root scope for the new `.omp/` dir.

## Verification

- `jq . .omp/mcp.json` (or `bun -e "JSON.parse(await Bun.file('.omp/mcp.json').text())"`): must exit 0, both servers present.
- Schema check: open `.omp/mcp.json` in editor with `$schema` — zero diagnostics; or `npx -y ajv-cli validate -s <mcp-schema.json> -d .omp/mcp.json` must pass. This is the new-behavior proof for transport/field mapping.
- Interactive: `omp` → `/mcp list` shows `kicad` and `kicad-copilot` sourced from `.omp/mcp.json` (not `opencode.jsonc`); then `/mcp test kicad` and `/mcp test kicad-copilot` — kicad passes only if KiCad MCP node target + `KICAD_PYTHON` exist on this Mac, copilot passes if `npx` can fetch/run; record actual output, do not fake success.
- Skill: `omp` → `/skill:review-pr-or-lab` (or skill list) resolves once; if duplicated, bare name must be the native/custom-directory copy with the opencode copy namespaced, per collision rules.
- Regression: session starts with no discovery warnings about malformed MCP JSON or missing skill description.

## Assumptions & contingencies

- Assumption: OMP `${HOME}` expansion works in native `mcp.json` `args` (per MCP docs discovery-time `${VAR}` expansion). If `/mcp test kicad` shows literal `${HOME}` in spawn path: use absolute `/Users/valdemar_check/KiCAD-MCP-Server/dist/index.js` instead.
- Assumption: project skills key is `skills.customDirectories` accepting relative `./opencode/skills` resolved from cwd — unverified, confirm first via `omp config list --json | jq '.["skills.customDirectories"]'`. If key absent/wrong: use byte-copy fallback in Approach step 2, no new decision needed.
- Scope edge: user-home skill dirs intentionally not migrated; if user wants them project-pinned later, add them as submodules under `.omp/skills/`, never as absolute paths in committed config.
