---
name: analyze-jira-ticket
description: Check whether a Jira ticket (story, bug, task, epic or spike) is ready for development before someone picks it up — is it clear, are the acceptance criteria testable, what is missing, which questions to ask the product owner, which areas of the code it touches, how big it is, and the risks. Uses the tech-lead subagent and the PROJECT_CONTEXT.md / SYSTEM_CONTEXT.md from create-project-context for the code impact (falls back to a code scan when no context file exists), and checks the ticket against the team's JIRA_CONFIG.md when one exists. Gives a Ready / Needs small fixes / Not ready verdict in short, plain English a junior developer or manager can follow. Use when the user says "analyze this ticket", "is this ticket ready", "review this story", "refine this ticket", "what's missing in this ticket", "grooming" or "sprint planning check", or pastes a ticket and asks what's wrong with it. Read-only — does not change the ticket in Jira.
---

# Analyze Jira Ticket

Read a ticket, check it is clear and complete, and look at the code it will touch. Tell the user whether it is ready to start, what to fix first, and what to ask.

For the full build plan (every file to change or create), use `/ai-sam:design-solution`. This skill is the quicker readiness check that comes before it.

## Ground rules

- **Read-only.** Don't edit the ticket, comment on it, or change its status. Don't edit any file.
- **Judge the ticket, don't rewrite it.** Point out gaps and suggest the fix in one line each. To rewrite the ticket, point the user to `/ai-sam:create-jira-ticket`.
- **Don't guess.** If you can't tell whether something is a gap (for example, a rule that may be documented elsewhere), list it as a question, not a gap.
- **Every question uses AskUserQuestion**, never a plain-text question.
  - Give 1–3 suggested options built from what you already know. Mark the best one "(Recommended)".
  - The user can type their own answer in the built-in **Other** textbox. Say so in the question text.
  - Every question after the first has **Retry previous answer** as its last option.
- **No personal or secret data.** Never ask for, copy or repeat:
  - names tied to records, email addresses, phone numbers, home addresses, dates of birth
  - government IDs, bank or card numbers, tax, income, medical or case/application records
  - gender, race, religion or national origin of real people
  - passwords, API keys, tokens, connection strings, MFA codes or any other credential

  If the ticket contains any of this (in the description, logs, screenshots or comments), stop, do not repeat it, tell the user it looks like personal or sensitive data that must not go into AI tools, and ask them to redact it. Also list it as a gap: the ticket itself should not hold that data. Follow your organisation's data policy if it is stricter.

## Output style

Write every question, summary and file this skill produces so a junior developer or a manager can follow it:

1. **Short and point-wise.** Bullets or numbered steps, not paragraphs. One idea per bullet, under 20 words where possible.
2. **Simple, everyday English.** "Use" not "utilise", "fix" not "remediate", "show" not "render".
3. **Explain technical terms once**, in plain words in brackets — e.g. "cache (a saved copy kept for speed)". Spell out acronyms the first time.
4. **Precise, not vague.** Name the exact file, screen, number or step. "Takes 12 seconds to load", not "slow".
5. **Lead with the answer.** Give the result or decision first, then the reason.
6. **Neutral and plain.** No blame, slang, emojis or exclamation marks.

## Step 1 — Get the ticket

- **A Jira key (e.g. `ABC-123`) and a Jira connector is available:** fetch the summary, type, description, acceptance criteria, linked issues and sub-tasks. Say in one line that you fetched it.
- **A key but no Jira connector:** ask with AskUserQuestion (the first question, so no **Retry previous answer**) — **Ticket details**: Paste the summary, description and acceptance criteria in Other (Recommended), Describe the ticket in a few lines in Other.
- **Pasted text:** use it as is.

Check the ticket for personal or secret data (see the ground rules) before going on.

## Step 2 — Load the team's ticket rules

Look for the team config written by `/ai-sam:setup-jira-config`, in this order, and merge it section by section (the first file that sets a section wins):

1. `JIRA_CONFIG.local.md` in the repo root
2. `JIRA_CONFIG.md` in the repo root
3. `~/.claude/ai-sam/JIRA_CONFIG.md`

If one exists, check the ticket against its summary format, acceptance criteria style and the template for its type. If none exists, check against the standard sections for the ticket type (Step 3). Say in one line which you used.

## Step 3 — Check the ticket itself

Check every ticket for:

- **Clear goal** — what is changing, and why it matters.
- **Testable acceptance criteria** — each one is a single yes/no check. Flag vague words like "fast", "user-friendly" or "handle errors" with no detail.
- **Edge cases** — empty states, errors, permissions (who can and can't), large amounts of data.
- **Scope** — what is in and out. Flag a ticket that does several unrelated things.
- **Dependencies** — other tickets, teams, designs or APIs it waits on.
- **Conflicts** — parts of the ticket that contradict each other.

Then check what its type needs:

| Type | Must have |
|---|---|
| Story | Who it is for and why; acceptance criteria; design or screen reference if there is UI |
| Bug | Steps to reproduce; what happens vs what should happen; where (environment, browser, screen); how many users are hit |
| Task | What needs doing; how we know it is done |
| Epic | Goal; what is in and out; the stories it splits into, or a plan to split it |
| Spike | The question to answer; a time limit; what the output is (doc, demo, decision) |

## Step 4 — Check the code impact

Start the `tech-lead` subagent (`ai-sam:tech-lead`) in **impact** mode. Give it:

- the full ticket text
- the repo root (`git rev-parse --show-toplevel`, or the current folder), or several repos when run in a parent folder
- the `PROJECT_CONTEXT.md` / `SYSTEM_CONTEXT.md` paths you find, or "none found"

If no context file exists, carry on — the subagent scans the code. Use its areas, likely files, size and risks in the report. A gap the code reveals (for example, the ticket names a screen that doesn't exist) goes under **Gaps to fix**.

## Step 5 — Report

Pick the verdict:

- **Ready** — no gaps that block starting work.
- **Needs small fixes** — a developer could start, but some gaps should be fixed first.
- **Not ready** — missing acceptance criteria, an unclear goal, a blocking dependency, or too big for one ticket.

Show the report in the chat:

````markdown
## Ticket analysis: <ticket key or short title>

**Verdict:** Ready / Needs small fixes / Not ready — <one-line reason>
**Size:** Small / Medium / Large — <one-line reason>
**Based on:** <context files read> | Code scan only

### What's clear
- <point>

### Gaps to fix before starting
| Gap | Why it matters | Suggested fix |
|---|---|---|
| <gap> | <effect if left> | <one-line fix> |

### Questions to ask
- <question> — <who: product owner, designer, another team>

### Areas of the code it touches
- <area> — `<main file or folder>`

### Risks
- **<risk>** — <what could go wrong> → <what to do>

### Team format check
- <only if a JIRA_CONFIG file was found: what doesn't match>
````

Leave out sections that are empty, except **Gaps to fix** (write "None").

Then ask with AskUserQuestion — **Next step**: Done (Recommended), Retry with edits, Design the solution, Rewrite the ticket.

- **Retry with edits** — ask what to change (Shorter, Less technical, More detail on one part, or **Other**). Apply only that change and show it again.
- **Design the solution** — run `/ai-sam:design-solution` with this ticket.
- **Rewrite the ticket** — run `/ai-sam:create-jira-ticket` with the ticket and this report's gaps as the notes.
