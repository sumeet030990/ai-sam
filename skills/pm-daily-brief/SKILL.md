---
name: pm-daily-brief
description: Build a project manager's daily brief for the active sprint (or a named sprint, board or team) from Jira or Azure DevOps, for the PM and leadership. Opens with a short leadership summary (no names). Gives a sprint verdict — On track, At risk or Off track — from work done against time used, scope added mid-sprint and the forecast finish. Shows progress and risk for each epic and release against its target date and code freeze, and the sprint's bugs — new, open by priority, reopened, and found after a story was done. A PM-only section shows one row per team member (load, progress, On track / Watch / Needs a check-in), PR (pull request) review load per reviewer, and every ticket the PM should ask about with the reason and a ready-to-ask, neutral question — stuck in one status too long, past due, over estimate, no update for days, blocked, sent back from QA or review, in progress with no code or PR, PR waiting for review, carried over, or unassigned. Compares with yesterday's saved snapshot to show what moved and what is still stuck. Uses the team's rules (members, capacity, days off, limits, done statuses) saved in PM_BRIEF_CONFIG.md, set up on the first run, and release dates from setup-release-process when present. Shows the brief for approval, then asks where to save or send it: chat only, a Markdown (.md) or Excel (.xlsx) file, SharePoint, OneDrive, Google Drive, Confluence, Microsoft Teams, Slack or email — with a leadership version that leaves out the PM-only section. Use when the user says "daily brief", "PM brief", "standup report", "is the sprint on track", "who is behind", "which tickets are delayed", "what should I ask the team today", "status for leadership", or runs /ai-sam:pm-daily-brief [sprint, board or team]. Read-only on tickets; never comments on, moves or reassigns a ticket, and never messages a team member.
---

# PM Daily Brief

Give the project manager (PM) one short report each morning. It has two parts:

**For the PM and leadership:**

1. **Leadership summary** — 3 to 5 bullets: the verdict, top risks and decisions needed. No names.
2. **Is the sprint on track?** — a verdict with the numbers behind it.
3. **Epics and releases** — percent done and risk against each target date and code freeze.
4. **Bugs** — new, open by priority, reopened, and found after a story was done.

**For the PM only:**

5. **Team status** — one row per team member: who is on track and who may need help.
6. **Ask today** — each ticket that needs a check-in, with the reason and a ready-to-ask question.
7. **PR review load** — pull requests (PRs, code changes waiting to merge) waiting on each reviewer.

Pick one input:

- **The active sprint** (default) — e.g. `/ai-sam:pm-daily-brief`.
- **A named sprint or iteration** — e.g. `/ai-sam:pm-daily-brief "Sprint 42"`.
- **A board, project or team** — e.g. `/ai-sam:pm-daily-brief board "Payments"`.

The team's rules live in `PM_BRIEF_CONFIG.md`. The first run sets them up; later runs use them without asking.

Where it fits:

1. `/ai-sam:setup-release-process` — release dates and code freeze rules, used here for release risk.
2. `/ai-sam:create-ticket` and `/ai-sam:analyze-ticket` — tickets are written and checked before the sprint.
3. `/ai-sam:pm-daily-brief` — every morning during the sprint. (This skill.)
4. `/ai-sam:smoke-regression-report` — at the end, what QA should retest.

## Ground rules

- **Read-only on tickets and PRs.** Never comment on, move, reassign, re-estimate or edit a ticket. Never review, comment on or change a PR. Never message, email or tag a team member about their tickets.
- **Sending the brief itself is the only outward step.** Post or send it only to the channels and lists the PM picks in Step 8, after they approve the exact text in Step 9.
- **Two audiences.** The **Leadership summary**, **Sprint health**, **Epics and releases** and **Bugs** sections name tickets, never people. **Team status**, **Ask today** and **PR review load** go in a **PM only** section. Shared copies leave the PM-only section out unless the PM says to include it for that place.
- **About the work, not the person.** Every flag names a ticket and a fact (e.g. "In Review for 4 working days"), never a judgement about a person. No ranking of people, no "slowest", "worst" or "lazy". Questions offer help, e.g. "Is anything blocking NCD-12?", never "Why haven't you finished?".
- **Grounded in evidence.** Every flag shows the number that caused it and where it came from (status history, due date, worklog, PR). If a field is missing (no estimate, no status history, no release date), say so instead of guessing.
- **Count working days only.** Skip weekends, the team's holidays and each member's days off from the config.
- **Show first, then save or send.** Never write a brief file, upload, post or send before the user approves the brief in Step 7 and picks where it goes in Step 8. The snapshot (Step 9a) is the one exception.
- **Running on a schedule with no one to answer:** build the brief, save the snapshot, and save files only to the places in **Save to** that are local folders. Don't upload, post or send anything. Say at the top of the brief that it is waiting for approval to share.
- **No new packages without asking.** If writing an `.xlsx` file needs a library that is missing, ask before installing it.
- **Every question uses AskUserQuestion**, never a plain-text question.
  - Give 1–3 suggested options built from the tickets and the config. Mark the best one "(Recommended)".
  - The user can type their own answer in the built-in **Other** textbox. Say so in the question text.
  - Group up to 4 related questions in one call.
  - Every question after the first has **Retry previous answer** as its last option. If picked, ask which answer to change, re-ask it, and continue.
- **No personal or secret data.** Use team members' display names only — never their email addresses, account IDs or leave reasons. Show ticket keys and titles only; never copy ticket descriptions, comments or PR text into the brief. Never open `.env` files, secrets, keys, database dumps or data files that may hold real people's records. Never ask for, copy or repeat:
  - names tied to resident or customer records, email addresses (except the delivery list in Step 8), phone numbers, home addresses, dates of birth
  - government IDs, bank or card numbers, tax, income, medical or case/application records
  - gender, race, religion or national origin of real people
  - passwords, API keys, tokens, webhook URLs, connection strings, MFA codes or any other credential

  If a ticket title, bug title, comment or worklog contains any of this, stop, do not repeat it, tell the user it looks like personal or sensitive data that must not go into AI tools, and ask them to redact it. Refer to that ticket by key only. Follow your organisation's data policy if it is stricter.

## Output style

Write every question, summary and file this skill produces so a junior developer or a manager can follow it:

1. **Short and point-wise.** Bullets or numbered steps, not paragraphs. One idea per bullet, under 20 words where possible.
2. **Simple, everyday English.** "Use" not "utilise", "fix" not "remediate", "show" not "render".
3. **Explain technical terms once**, in plain words in brackets — e.g. "cache (a saved copy kept for speed)". Spell out acronyms the first time.
4. **Precise, not vague.** Name the exact file, screen, number or step. "Takes 12 seconds to load", not "slow".
5. **Lead with the answer.** Give the result or decision first, then the reason.
6. **Neutral and plain.** No blame, slang, emojis or exclamation marks.

## Step 1 — Find the sprint and its tickets

### Check what is connected

| System | Connected when | Used for |
|---|---|---|
| Jira | A Jira or Atlassian connector is available | JQL (Jira Query Language) search, ticket history, worklogs, sprint dates, epics, fix versions |
| Azure DevOps | `az account show` succeeds and `az extension show --name azure-devops` works | `az boards query --wiql`, `az boards work-item show`, `az boards iteration`, `az repos pr list` |
| Neither | — | Stop. Say the brief needs Jira or Azure DevOps, and name the connector or CLI (command-line tool) to set up. |

For PRs, also check the code host: GitHub (`gh auth status`), Azure Repos (`az repos`), GitLab (`glab auth status`), or a Bitbucket connector. If none works, PR flags use only the PR links on the ticket, and **PR review load** is left out with a Data gaps line.

Remember what is connected — later steps use it.

### Pick the sprint

- **Nothing given** → the active sprint for the project in the config, `PROJECT_CONTEXT.md`, or the branch's ticket key.
  - Jira: `sprint in openSprints() AND project = <KEY>`. If several boards have an open sprint, ask which one.
  - Azure DevOps: `az boards iteration team list --team "<team>" --timeframe current`.
- **A sprint or iteration name** → that sprint. If not found, list open and recent sprints and ask.
- **A board, project or team** → the active sprint of that board or team.
- **No sprint at all** (a Kanban board) → use work in progress and work finished in the last 14 days. Say the sprint verdict is replaced by a flow summary (Step 4c).

Read the sprint name, goal, start date and end date.

### Read the tickets

For every ticket in the sprint (including sub-tasks), read:

- key, type, title, status, assignee, priority, story points, original estimate, time spent, remaining estimate, due date
- created date, last updated date, date added to the sprint, labels, flagged / impediment field
- status history (changelog) — every status change with its date
- parent epic and fix version (release)
- links: "is blocked by", "is caused by" / "relates to" (for bugs), parent, linked PRs and branches
- previous sprints the ticket was in (carry-over)
- the date of the last comment and last worklog — the dates only, not the text

Then read, for Steps 6a and 6c:

- **Bugs** — every bug in the project created on or after the sprint start, whether or not it is in the sprint: key, title, priority, status, created date, status history, links.
- **Epics and releases** — for each epic and fix version found on sprint tickets: all its tickets (not only this sprint's), their status and points, the epic's due date or target date, and the fix version's release date.

Check each title for personal or secret data before going on. If there are more than 150 tickets, say so and ask: Read all (slower) (Recommended), Leave out sub-tasks, Retry previous answer.

## Step 2 — Load the project and the rules

1. Read, if present:
   - `PROJECT_CONTEXT.md` in the repo root or `docs/`, and `CLAUDE.md`.
   - The **Delivery and release process** section from `/ai-sam:setup-release-process`, in `PROJECT_CONTEXT.md` or `SYSTEM_CONTEXT.md` — release dates, code freeze days before release, and the "all tickets tested by" deadline. Used in Step 6c.
   - `SYSTEM_CONTEXT.md` in the parent folder — the repos to check for PRs.
2. Load `PM_BRIEF_CONFIG.md`. Settings merge section by section; for each section the highest file that sets it wins:

   | Order | File | Who it is for |
   |---|---|---|
   | 1 (highest) | `PM_BRIEF_CONFIG.local.md` in the repo root | One person's overrides in one repo; gitignored |
   | 2 | `PM_BRIEF_CONFIG.md` in the repo root | The team's rules for this repo; shared once committed |
   | 3 | `~/.claude/ai-sam/PM_BRIEF_CONFIG.md` | One person's defaults in every repo |
   | 4 | Built-in rules (shown in Step 3) | Used when nothing else is set |

3. **No config file found** → run Step 3 (first-run setup). Otherwise say in one line which files were loaded, and skip to Step 4.
4. The user can type "change rules" at any point to run Step 3 again.

## Step 3 — First-run setup of the team's rules

Ask in two calls. Suggest values from the sprint: the assignees found, the board's statuses and the sprint length.

**Call 1:**

1. **Who is on the team?** (multi-select) — list the assignees found in the sprint, up to 4 per call (ask again for more). Picked people get a row in the brief; others are grouped as "Outside the team". Say the user can type a name in **Other**.
2. **How do you measure work?** Story points (Recommended when most tickets have points), Hours (original estimate), Ticket count, Retry previous answer.
3. **Which statuses mean "done"?** (multi-select) — list the board's final columns, e.g. **Done**, **Closed**, **Resolved**. Mark the last column (Recommended).
4. **When should a ticket be flagged for a check-in?** Standard limits (Recommended — see the config below), Stricter (half the days), Looser (double the days), Retry previous answer.

**Call 2:**

5. **How much can each person take in a sprint?** Same for everyone: average done in the last 3 sprints (Recommended — show the number), Set per person (follow-up asks), Retry previous answer.
6. **Any days off or holidays this sprint?** No (Recommended), Yes — I will type them in **Other** (name and dates, or holiday dates), Retry previous answer.
7. **Which bugs count as high priority?** Highest and High (Recommended), Highest only, Retry previous answer.
8. **Who should these rules apply to?**
   - **The team, this repo** — writes `PM_BRIEF_CONFIG.md` in the repo root (Recommended when none exists).
   - **Just me, this repo** — writes `PM_BRIEF_CONFIG.local.md` (Recommended when the team file exists). Offer only in a git repo.
   - **Just me, every repo** — writes `~/.claude/ai-sam/PM_BRIEF_CONFIG.md` (Recommended when not in a git repo).
   - **Retry previous answer**.

Split question 8 into a third call if Call 2 already has 4 questions.

Write the file in this format. Keep the **Save to** section empty for now — Step 8 fills it.

```markdown
# PM brief config

Used by /ai-sam:pm-daily-brief. Edit by hand, or type "change rules" during a run.

## Source
- System: Jira — project `NCD` — board `Payments board`
- Code host: GitHub — repos `org/payments-api`, `org/payments-ui`

## Team
- Alex Rivera — capacity 8 points
- Sam Lee — capacity 8 points
- Jordan Patel — capacity 5 points (part-time)

## Days off
- Sam Lee — 2026-11-12 to 2026-11-13
- Holiday — 2026-11-26

## Work unit
- Story points

## Done statuses
- Done, Closed

## Check-in limits (working days)
- Same status too long — In Progress: 3 — In Review / Code Review: 2 — QA / Testing: 2 — Blocked: 1
- No update (no status change, comment or worklog): 2
- Over estimate by: 30%
- PR waiting for review: 2
- Too much at once: more than 2 tickets In Progress per person
- Review load: more than 3 PRs waiting on one reviewer

## Bugs
- High priority: Highest, High
- Bug types: Bug, Defect

## Sprint verdict
- At risk when done is behind time used by: 15 percentage points
- Off track when behind by: 30 percentage points, or forecast finish is more than 1 working day after the sprint end

## Save to
- (set on first save)

## Change log
- <YYYY-MM-DD> — created
```

For the local file, check `git check-ignore -q PM_BRIEF_CONFIG.local.md`. If not ignored, add it on its own line at the end of the repo root `.gitignore`. Don't commit any file. Say in one line where the rules were saved.

## Step 4 — Sprint health

Use the work unit from the config (points, hours or ticket count). Count working days only.

### 4a — The numbers

| Measure | How |
|---|---|
| Time used | working days passed ÷ working days in the sprint, as a percent |
| Work done | done work ÷ total work in the sprint now, as a percent |
| Gap | work done % − time used % (negative means behind) |
| Scope added | work added after the sprint start date, and how many tickets |
| Scope removed | work taken out after the start date |
| Forecast finish | remaining work ÷ average done per working day so far, counted forward from today |
| Not estimated | tickets with no points or estimate (they can't be counted — list them) |
| Carry-over | tickets that were in an earlier sprint too |

If the sprint is in its first 2 working days, say the forecast is too early to trust and base the verdict on blockers only.

### 4b — The verdict

- **On track** — gap is better than the "At risk" limit, forecast finish is on or before the sprint end, and no blocked ticket is High priority.
- **At risk** — gap is past the "At risk" limit, **or** forecast finish is up to 1 working day late, **or** scope grew by more than 15%, **or** a High priority ticket is blocked, **or** a high-priority bug is open with 2 or fewer working days left.
- **Off track** — gap is past the "Off track" limit, **or** forecast finish is more than 1 working day late.

Give the verdict with its top 3 reasons, each with its number. If the sprint has a goal, say which goal tickets are done, in progress and not started.

### 4c — No sprint (Kanban)

Replace 4a and 4b with: tickets finished in the last 7 days, tickets in progress, average days from start to done, and the 3 oldest tickets in progress.

## Step 5 — Per-person status and check-in list

### 5a — Check each ticket

Flag a ticket when any of these is true. Use the limits from the config. A ticket can have several flags.

| Flag | When | Shown as |
|---|---|---|
| Stuck | In one status longer than its limit (from status history) | "In Review for 4 working days (limit 2)" |
| Past due | Due date is before today and the ticket is not done | "Due 2026-11-05, 2 working days late" |
| Due soon, not started | Due in 2 working days or less and still To Do | "Due 2026-11-10, not started" |
| Over estimate | Time spent is more than the estimate by the config's percent | "12h spent of 8h estimate (+50%)" |
| No update | No status change, comment or worklog for the limit | "No update for 3 working days" |
| Blocked | Flagged, in a Blocked status, or linked "is blocked by" an open ticket | "Blocked by NCD-88 (open)" |
| Sent back | Moved back from QA, Review or Done to an earlier status | "Moved back from QA twice" |
| No code yet | In Progress for 2+ working days with no linked branch, commit or PR | "In Progress 3 days, no branch or PR" |
| PR waiting | Linked PR open with no review for the limit | "PR #412 open 3 days, no review" |
| Carried over | Was in an earlier sprint and is not done | "3rd sprint" |
| Unassigned | In the sprint with no assignee | "No owner" |
| Not estimated | No points or estimate | "No estimate" |

Leave out done tickets, except "Sent back" from the last 2 working days.

### 5b — Status for each person

For each team member from the config:

| Field | How |
|---|---|
| Load | their work in the sprint ÷ their capacity, less days off |
| Done | their done work, and percent of their load |
| In progress | number of tickets In Progress or In Review |
| Flags | number of their flagged tickets |
| Status | see below |

- **On track** — their done % is not behind time used by more than the "At risk" limit, and they have no Stuck, Past due or Blocked ticket.
- **Watch** — one of: behind by more than the "At risk" limit, one Stuck or Over estimate ticket, load over 110% of capacity, or more tickets in progress than the limit.
- **Needs a check-in** — one of: a Past due or Blocked ticket, behind by more than the "Off track" limit, or 2 or more flagged tickets.

Add a one-line reason with the main number, e.g. "2 of 8 points done at 60% of the sprint; NCD-12 stuck in Review". If a person is on a day off today, say so and don't mark No update flags for those days.

### 5c — Write the check-in questions

For each flagged ticket, write one question for the PM to ask the owner. Rules:

- Name the ticket and the fact, then ask about blockers or help. Never ask "why" about a person's speed.
- One question per ticket, under 25 words. Join several flags into one question.
- Order tickets: Blocked, Past due, High priority Stuck, then the rest by days stuck.

Examples:

- "NCD-12 has been in Review for 4 days. Is it waiting on a reviewer, and should I find one?"
- "NCD-20 was due on 5 November. What is the new expected date, and what is it waiting on?"
- "NCD-31 is blocked by NCD-88. Who needs to unblock it, and do you need me to follow up?"
- "NCD-44 is at 12h of an 8h estimate. Has the scope grown, and should we re-estimate or split it?"
- "NCD-50 has no owner. Who should pick it up?"

## Step 6 — Bugs, reviews, epics and releases

### 6a — Bugs

Use the bug types and high-priority levels from the config.

| Measure | How |
|---|---|
| New this sprint | bugs created on or after the sprint start, by priority |
| New since last brief | bugs created since the last snapshot |
| Open high-priority | high-priority bugs not done, with days open and owner status (assigned or not) |
| Reopened | bugs moved back from Done, Resolved or QA to an earlier status this sprint |
| Found after done | bugs linked ("is caused by", "relates to") to a story done this sprint, or created against an epic in this sprint |
| Trend | bugs opened vs bugs closed this sprint |

Add every open high-priority bug and every reopened bug to the **Ask today** list (Step 5c), with a question such as "NCD-77 is a High bug open 3 days with no owner. Who should take it?".

### 6b — PR review load

Skip with a Data gaps line if no code host is connected.

1. List open PRs in the repos from the config or `SYSTEM_CONTEXT.md`, plus PRs linked to sprint tickets:
   - GitHub: `gh pr list --repo <repo> --state open --json number,title,author,reviewRequests,reviews,createdAt,isDraft`
   - Azure Repos: `az repos pr list --repository <repo> --status active`
   - GitLab: `glab mr list --repo <repo>`
2. Leave out draft PRs.
3. For each reviewer on the team: PRs waiting on them (review requested, no review given), and the oldest wait in working days.
4. Flag:
   - a reviewer with more PRs waiting than the config's review load limit — "Alex Rivera: 5 PRs waiting, oldest 4 days"
   - PRs open past the "PR waiting for review" limit with **no reviewer assigned**
5. Phrase it as a load to spread, not a fault: "May need help spreading reviews".

### 6c — Epics and releases

For each epic and each fix version (release) that has a ticket in this sprint:

| Field | How |
|---|---|
| Done | done work ÷ all work in the epic or release (not only this sprint), as a percent |
| In this sprint | its tickets in this sprint: done and not done |
| Target date | epic due date, or the fix version's release date. Releases: also the code freeze date, from the release process (release date minus freeze days) |
| Working days left | to the code freeze when known, else to the target date |
| Forecast | remaining work ÷ the team's average done per working day (from Step 4a) — the date it would finish |
| Blockers | its blocked tickets and open high-priority bugs |
| Status | On track, At risk or Off track (below) |

- **On track** — forecast finish is on or before the code freeze (or target date), and no open blocker.
- **At risk** — forecast finish is up to 2 working days after it, **or** it has a blocked ticket or open high-priority bug.
- **Off track** — forecast finish is more than 2 working days after it.
- **No date** — no target date or release date found. Show the percent done only and add a Data gaps line.

Order: Off track first, then At risk, then by nearest date. Show at most 8; group the rest as "<n> more, all On track".

### 6d — Compare with yesterday

Look for the latest snapshot before today in the snapshot folder (Step 9a). If one exists, add a **Since last brief** list:

- Tickets finished since then.
- New flags, and flags that cleared.
- Tickets still flagged for 2+ briefs in a row — mark them **Repeat** so the PM can raise them differently.
- Sprint verdict change (e.g. On track → At risk) and work done change.
- Epic or release status changes.
- New bugs, and bugs closed.
- Tickets added to or removed from the sprint.

If no snapshot exists, say this is the first brief for this sprint.

### 6e — Leadership summary

Write it last, from Steps 4–6. 3 to 5 bullets, no people's names:

1. The sprint verdict and the one main reason.
2. Any epic or release At risk or Off track, with its date.
3. Open high-priority bugs, if any.
4. The decision leadership may need to make (e.g. "Move NCD-7 to the next sprint, or add a reviewer"), if any.

## Step 7 — Show the brief

Show it in the chat:

````markdown
# PM daily brief: <sprint name> — <YYYY-MM-DD>

## Leadership summary
- Sprint is **At risk**: 38% done at 60% of the sprint.
- Release 2.4 is **At risk**: code freeze 2026-11-16, forecast 2026-11-17.
- 1 High bug open (NCD-77), no owner yet.
- Decision needed: keep NCD-7 (3rd sprint) or move it to the next sprint.

## Sprint health
**Verdict:** At risk
- Work done 38% at 60% of the sprint (12 points behind).
- Forecast finish 2026-11-20, 2 working days after the sprint end (2026-11-18).
- 8 points added after the sprint start (+15%).

**Sprint goal:** <goal> — 2 of 4 goal tickets done, 1 in progress, 1 not started.
**Days left:** 4 working days.

## Epics and releases
| Epic / release | Status | Done | Target | Days left | Forecast | Blockers |
|---|---|---|---|---|---|---|
| Release 2.4 | At risk | 72% | Freeze 2026-11-16 (release 11-20) | 5 | 2026-11-17 | NCD-31 blocked |
| NCD-5 Refunds rework | On track | 85% | 2026-11-25 | 12 | 2026-11-19 | — |

## Bugs
- New this sprint: 6 (1 High, 3 Medium, 2 Low) — 2 since last brief.
- Opened 6, closed 4.
- Open High: NCD-77 — open 3 days, no owner.
- Reopened: NCD-61 (moved back from QA).
- Found after done: NCD-80, linked to NCD-14 (done 2026-11-05).

## Since last brief (<date>)
- Done: NCD-14, NCD-18 (+6 points)
- New flags: NCD-31 blocked
- Cleared: NCD-9 (PR reviewed)
- Release 2.4: On track → At risk
- **Repeat:** NCD-12 stuck in Review for the 3rd brief in a row

---

## PM only

### Team status
| Person | Status | Load | Done | In progress | Reason |
|---|---|---|---|---|---|
| Alex Rivera | On track | 8 / 8 pts | 5 (63%) | 1 | — |
| Sam Lee | Watch | 9 / 6 pts (150%) | 3 (33%) | 2 | Over capacity after 2 days off; NCD-12 stuck in Review |
| Jordan Patel | Needs a check-in | 5 / 5 pts | 0 (0%) | 2 | NCD-20 past due; NCD-31 blocked |

**Days off:** Sam Lee 12–13 Nov.

### Ask today (<n>)
| # | Ticket | Owner | Flags | Question to ask |
|---|---|---|---|---|
| 1 | NCD-31 — Card refund retry | Jordan Patel | Blocked by NCD-88 (open) | NCD-31 is blocked by NCD-88. Who needs to unblock it, and should I follow up? |
| 2 | NCD-77 — Refund total wrong (bug) | — | High bug, open 3 days, no owner | NCD-77 is a High bug with no owner. Who should take it today? |
| 3 | NCD-20 — Export payments CSV | Jordan Patel | Past due 2 days | NCD-20 was due on 5 November. What is the new date, and what is it waiting on? |
| 4 | NCD-12 — Voucher list filter | Sam Lee | **Repeat**; In Review 4 days (limit 2); PR #412 no review | NCD-12's PR has waited 4 days. Should I find a reviewer? |

### PR review load
| Reviewer | PRs waiting | Oldest wait | Note |
|---|---|---|---|
| Alex Rivera | 5 | 4 days | May need help spreading reviews |
| Sam Lee | 1 | 1 day | — |
- No reviewer assigned: PR #418 (`payments-api`), open 3 days.

### Needs a decision
- Unassigned: NCD-50 (3 pts)
- Not estimated: NCD-52, NCD-53
- Carried over: NCD-7 (3rd sprint) — keep, split or move out?

## Data gaps
- <e.g. "4 tickets have no status history, so Stuck could not be checked.">
````

Leave out empty sections. Then ask — **Brief**: This looks right (Recommended), Change a limit, Retry with edits, Ask a follow-up.

- **Change a limit** — ask which limit and the new value. Re-run Steps 4–6 and show the brief again. Then ask — **Save this limit for future briefs?**: No, today only (Recommended), Yes — update the config, Retry previous answer. On yes, update the config file it belongs in, with a dated **Change log** line.
- **Retry with edits** — ask what to change (Hide a ticket from the list, Shorter brief: top 5 questions only, Edit the leadership summary, or **Other**). Change only that and show the brief again.
- **Ask a follow-up** — answer from the tickets, e.g. "show Sam's tickets" or "what changed on NCD-12 this week".

Repeat until the user picks **This looks right**.

## Step 8 — Ask where to save or send

### 8a — Check what is saved and connected

1. Read the **Save to** section of the loaded config.
2. Check which tools work:
   - Upload: a Microsoft 365, SharePoint, Google Drive or Atlassian connector; `m365 status` (the CLI for Microsoft 365).
   - Messages: a Microsoft Teams, Slack, Outlook or Gmail connector; `m365 status` for Teams and Outlook.

### 8b — First run (Save to is empty)

Ask — **Where should I save or send this brief?** (multi-select). Say the user can type another place in **Other**.

- **Show in the chat only** — nothing saved except the snapshot (Recommended for a quick daily check).
- **Save a file** — Markdown or Excel, in `docs/pm-brief/` in the repo, or `~/.claude/ai-sam/pm-brief/` outside a repo.
- **Upload or publish** — SharePoint, OneDrive, Google Drive or a dated Confluence page.
- **Send as a message** — a Microsoft Teams channel, a Slack channel, or an email.

Mark a place "(not connected — I'll prepare it for you to share by hand)" when no tool for it works.

Then ask the follow-ups, in one call, only for what was picked:

| Picked | Follow-up |
|---|---|
| Save a file | **Which file type?** (multi-select): Markdown (.md) (Recommended), Excel (.xlsx). And the folder: `docs/pm-brief/` (Recommended), or type another in **Other** |
| Upload or publish | **Where?** SharePoint, OneDrive, Google Drive, Confluence. Then: SharePoint — site URL, library (default `Documents`), folder (e.g. `PM/Daily briefs`); OneDrive — folder; Google Drive — folder link or path; Confluence — space key and parent page title |
| Send as a message | **Where?** (multi-select) Microsoft Teams, Slack, Email. Then: Teams — team and channel name; Slack — channel name; Email — the recipients (a team or distribution list address is best) and subject line (default `PM daily brief: <sprint> — <date>`) |

For every place except chat and a local file, also ask — **Which version goes to <place>?**:

- **Leadership version** — everything except the PM-only section (Recommended).
- **Full brief** — includes Team status, Ask today and PR review load. Best only for a private PM folder or channel.
- **Retry previous answer**.

Never ask for or save passwords, tokens, webhook URLs or any other credential — only where the brief goes.

**Save the answers** in the **Save to** section, one line per place, plus a dated **Change log** line:

```markdown
## Save to
- Markdown file — folder `docs/pm-brief/` — full brief
- Confluence — space `PAY` — parent `Daily briefs` — leadership version
- Teams — team `Payments` — channel `Leadership updates` — leadership version
```

Email recipients go only in the personal config (`PM_BRIEF_CONFIG.local.md` or `~/.claude/ai-sam/PM_BRIEF_CONFIG.md`), never the team file, so addresses are not committed. Create the personal file with just a **Save to** section if needed. Say in one line where each choice was saved.

### 8c — Later runs (Save to is set)

Ask — **Where should I save or send this brief?**: Same as last time — list the places and versions in one line (Recommended), Change where it goes, Only this time: somewhere else, Retry previous answer.

### Before saving

- If a file or page with the same name exists (a second run today), ask: Replace it (Recommended), Save as `<name>-2`, Retry previous answer.
- If a saved folder or channel no longer exists or access is denied, say so and offer **Change where it goes**.

## Step 9 — Save and send

File name: `<sprint name>-brief-<YYYY-MM-DD>`, with spaces and `/` changed to `-` (e.g. `Sprint-42-brief-2026-11-07.md`). Build each place's copy from its version (leadership or full).

Do the steps in this order, so messages can link to the uploaded brief: 9a, 9b–9d, 9e, 9f, then 9g.

### 9a — Snapshot (always)

Always save a snapshot so tomorrow's brief can compare (Step 6d), even when the brief is shown in the chat only.

1. Path: `~/.claude/ai-sam/pm-brief/<project or board>/snapshots/<YYYY-MM-DD>.json`. Outside the repo, so it is never committed.
2. Store only: sprint name and dates, verdict, work done and total, epic and release statuses, bug keys with priority and status, and per ticket — key, status, assignee display name, points, flags and days stuck. No titles, descriptions or comments.
3. Keep the last 30 snapshots; delete older ones in that folder only.

### 9b — Get the repo folder ready

Only when a repo file was picked:

1. Create the folder if missing (`mkdir -p docs/pm-brief/`).
2. Keep it out of git — the brief is about people's work, not code:
   - If `git check-ignore -q <folder>/x.md` says it is already ignored, do nothing.
   - Otherwise add the folder on its own line at the end of the repo root `.gitignore`, under `# PM daily briefs from ai-sam pm-daily-brief`. Create `.gitignore` if missing. Don't change any other line.
3. Say in one line what was created and added.

### 9c — Markdown file

Write the Step 7 brief for that version.

### 9d — Excel file

1. Use the `xlsx` skill if this session has one. Otherwise write a short Python script in a temporary folder outside the repo using `openpyxl`.
2. If `openpyxl` is missing, ask — **Excel needs the `openpyxl` Python library**: Install it with `pip install --user openpyxl` (Recommended), Save as CSV (a plain table file Excel opens) instead, Skip Excel, Retry previous answer.
3. Sheets: **Summary** (leadership summary, verdict, numbers, since last brief), **Epics and releases**, **Bugs**, **All tickets** (key, title, owner, status, points, days in status, due date, flags). Full version adds **Team**, **Ask today** and **PR review load**.
4. Add empty **Answer** and **Follow-up date** columns on **Ask today** for the PM's notes.
5. Bold header row, frozen top row, wrapped text, readable column widths. Colour Status cells: On track green, Watch / At risk amber, Needs a check-in / Off track red, with the word always shown too. Ticket keys link to the ticket when the URL is known.
6. Open the saved file once to check every row is in it, then delete the temporary script.

### 9e — Shared folder (SharePoint, OneDrive, Google Drive)

1. Build the file as in 9c or 9d. If no repo file was picked, build it in a temporary folder outside the repo and delete it after upload.
2. Upload, using the first that works:
   - A connector for that service in this session.
   - SharePoint or OneDrive: `m365 spo file add --webUrl <site URL> --folder "<library>/<folder path>" --path <file>`, if `m365 status` shows it is signed in.
   - Neither: say no upload tool is connected and which connector would make it work. Save the file in `docs/pm-brief/` as in 9b, and give the exact place to upload it by hand.
3. Show the file name, version and full destination. Ask — **Upload to <service>?**: Upload (Recommended), Change the folder for this file only, Retry previous answer. Upload only on yes.
4. Give the link. If the upload fails, show the error in one line, save the file in the repo folder instead, and say so.

### 9f — Confluence page

1. Build the page from the Step 7 brief for that version, titled `PM daily brief: <sprint> — <YYYY-MM-DD>`, as a child of the saved parent page.
2. Show the title, version, space and parent. Ask — **Create this page?**: Create it (Recommended), Change the parent page, Retry previous answer. Create only on yes, then give the link.

### 9g — Teams, Slack or email message

1. Build a short message, not the whole brief:
   - Title line: `PM daily brief: <sprint> — <date>`
   - The leadership summary bullets.
   - The **Epics and releases** status in one line each, Off track and At risk only.
   - A link to the full brief from 9e or 9f, when one was made.
   - Full version only: the **Ask today** count and the top 3 tickets.
   - Email: send the Markdown brief as the body when there is no link.
2. Show the exact message, the channel or recipients, and the version. Ask — **Send to <place>?**: Send (Recommended), Edit the message, Retry previous answer. Send only on yes.
3. Send, using the first that works:
   - **Teams** — a Microsoft Teams or Microsoft 365 connector; or `m365 teams message send --teamId <id> --channelId <id> --message "<html>"` when `m365 status` is signed in (look up the IDs with `m365 teams team list` and `m365 teams channel list`).
   - **Slack** — a Slack connector.
   - **Email** — an Outlook, Microsoft 365 or Gmail connector; or `m365 outlook mail send --to <list> --subject "<subject>" --bodyContents "<html>" --bodyContentType HTML`.
   - None works: say which connector would make it work, and show the message ready to copy and paste.
4. Never tag or mention a team member in the message. Give the link to the sent message when the tool returns one. If sending fails, show the error in one line and show the message ready to paste.

## Step 10 — Report back

Show a short report in the chat:

````markdown
## Brief done: <sprint> — <YYYY-MM-DD>

**Sprint:** At risk — 38% done at 60% of the sprint
**Releases:** 1 at risk (Release 2.4)
**Bugs:** 1 High open
**Team:** 1 on track, 1 watch, 1 needs a check-in
**Ask today:** 4 tickets
**Saved and sent:**
- `docs/pm-brief/Sprint-42-brief-2026-11-07.md` — full brief
- Confluence — <link> — leadership version
- Teams `Leadership updates` — sent
- Snapshot for tomorrow's comparison

**Tip:** to get this brief every weekday morning, run `/schedule` or `/loop` with `/ai-sam:pm-daily-brief`. Scheduled runs save files only; uploads and messages wait for your approval.
````

Leave out lines that don't apply. Add a line if `.gitignore` or a `PM_BRIEF_CONFIG` file was created or changed — those changes are uncommitted. Never commit or push anything.
