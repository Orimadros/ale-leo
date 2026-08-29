---
description: Closes out a session — writes a dated session-log entry, runs the standing git-state checklist, accounts for what agents/skills/hooks did this session, and prompts saving durable lessons to MEMORY.md. Supersedes the former session-checkpoint skill. Use at the end of a meaningful session, or when asked to end/checkpoint/save progress.
argument-hint: "[optional short label]"
---

Close out the current session:

1. **Summarize.** In a few short paragraphs, summarize what happened this session and *why* — decisions made, problems solved, work produced, and open threads. Write for a future session (and the next `/session-start`) that has no memory of this one. If a session type was set via `/session-start`, frame next-session recommendations against it.
2. **Git-state checklist** (standing checklist, per `logs/plans/0002-phase-2-session-lifecycle-skills.md`):
   - `git status` — flag uncommitted/unstaged changes rather than let the session end silently on a dirty tree.
   - Confirm the current branch is `main`; flag if not.
   - Check ahead/behind `origin/main`; flag unpushed commits.
   - Confirm `CLAUDE.local.md` is still excluded (`git check-ignore -v CLAUDE.local.md`).
   - Cross-check that nothing matching the heavy-file patterns (`.claude/hooks/heavy-file-guard.sh`) is staged.
   - Note any `git-guardrail` denials that occurred this session and whether they're resolved or still pending.
3. **Agent/skill/hook accounting:**
   - Skills invoked this session, and any unacted prompts they raised.
   - Agents invoked (`verifier`, `claim-verifier`, and any domain agents) and their verdicts — surface unresolved findings rather than letting them drop.
   - Hooks that fired, and whether any block was resolved, deferred, or overridden.
   - If this session revealed the need for new agent/skill/hook/rule infrastructure, prompt logging it as a new plan item in `logs/plans/`, consistent with the phased-adoption policy in `CLAUDE.md`.
4. **Save the log.** Write the summary plus checklist results to `logs/sessions/YYYY-MM-DD-<short-slug>.md` (today's date; slug from `$ARGUMENTS` if given, otherwise from the session's main topic).
5. **Durable lessons.** Review the session for anything durable — a correction, a convention, a recurring lesson — not already captured. Propose it and ask whether it belongs in repo memory (`/learn` → `.claude/memory/MEMORY.md`) or is really a personal working-style preference for the user's harness-level memory instead (see `CLAUDE.md`'s memory section for the distinction).
6. **Commit the log.** Once the log is written (and any `/learn` entries saved), invoke the `commit` skill to stage and commit the session-log file — as its own commit if nothing else is pending, or bundled with other pending work — so it doesn't sit uncommitted as "next session's problem." Do not hand-roll `git add`/`git commit` here; go through `commit` so its review/approval step still applies.
7. **Offer to push.** After the log commit lands, check the commit count ahead of `origin/main`. If there are unpushed commits, explicitly ask whether to push now — state how many commits are ahead. Only run `git push` after an explicit yes for *this* session; a prior session's approval doesn't carry over, and routine/log-only commits don't get a pass either. If declined, or no clear answer is given, leave it unpushed and note that in the summary rather than defaulting to push.
8. **Scope.** Do not duplicate the research journal (`journal/`) — this is Claude's operational record of the session, not Alessandra's own intellectual journal.

Keep the entry factual and concise. This is a log, not a narrative.
