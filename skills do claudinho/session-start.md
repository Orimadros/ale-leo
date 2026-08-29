---
description: Standardized session startup — checks git/repo state, loads project instructions/rules/memory and the previous session's handoff, identifies unfinished work, asks for a session type (STUDY/RESEARCH/ADMIN/ARCHITECTURE), and produces a status report. Use at the start of a session, or when asked to start/orient a session.
---

Start the session:

1. **Git/repo status.** Run `git status`, confirm the current branch (`main` expected), and note ahead/behind `origin/main`. Flag anything unexpected — uncommitted changes left over from last time, wrong branch — rather than proceeding silently.
2. **Load context via `context-status`.** Invoke the `context-status` skill rather than re-deriving its output here: it lists the most recent `logs/plans/`/`logs/sessions/` entries, summarizes `.claude/memory/MEMORY.md`, and notes the current phase plus anything flagged "next." Treat its most recent `logs/sessions/` entry as the previous session's handoff — per repo convention, that log entry *is* the handoff; there is no separate handoff file. On top of what `context-status` returns, skim `CLAUDE.md` (mission, phase, principles) and `.claude/rules/` if not already in context.
3. **Identify unfinished work.** From `context-status`'s output, pull forward anything flagged as open/unresolved/next in the last session log, and any `logs/plans/` entry still marked as a pending design item or not yet implemented.
4. **Ask for the session type.** Ask the user which kind of session this is:
   - `STUDY` — pre-MSc/MSc coursework and study
   - `RESEARCH` — literature, research questions, thesis-track work
   - `ADMIN` — logistics, deadlines, and career items (applications, offers, admin planning)
   - `ARCHITECTURE` — building/editing this repo's own agents/skills/hooks/rules, or infra/tooling/dev-environment design (VM/remote access, dev environment setup, general system design work)
   Treat this as the current list, not a hard limit — it's expected to grow. Note in the report if the session doesn't cleanly fit any of them.
5. **Adapt context to the type:**
   - `STUDY` → prioritize `prep/` (progress, weekly-plans, pre-reading) and study materials.
   - `RESEARCH` → prioritize `research/`, `literature/`, and thesis-track threads.
   - `ADMIN` → prioritize `admin/` and `career/`, including applications and deadlines.
   - `ARCHITECTURE` → prioritize `.claude/` (agents, skills, hooks, rules) and `logs/plans/` (design decisions, including infra/tooling plans like the VM migration).
6. **Report.** Give a concise startup/status report combining the git check, `context-status`'s orientation summary, and the type-adapted highlights. Point to files rather than reproducing their content in full.
7. **Wait.** Do not begin work or modify any files after the report — this skill is read-only/reporting by design. Wait for the user's explicit next instruction.

`session-start` invokes `context-status` as part of its own procedure (step 2) rather than duplicating its logic — the two skills aren't meant to coexist as parallel, uncoordinated ways of doing the same scan. `context-status` remains independently invocable on its own for a quick on-demand orientation check mid-session, outside the `session-start` flow.
