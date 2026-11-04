---
name: design-solution
description: Act as the project's senior tech lead and design how to build a Jira ticket or feature — the approach, which existing files need updating, which new files are needed and where, which file delivers each acceptance criterion, tests, risks and open questions. Uses the PROJECT_CONTEXT.md and SYSTEM_CONTEXT.md written by create-project-context as its project knowledge and learns the business rules from the code; still works from a code scan alone when no context file exists. Hands the work to the tech-lead subagent and shows the plan in the chat in short, plain English a junior developer or manager can follow. Use when the user says "design a solution", "how should we build this ticket", "which files need to change", "what files do I need to create", "plan this story", "tech lead review of this ticket", or pastes a ticket and asks how to implement it. Read-only — does not write code, edit files or change Jira.
---

# Design Solution

Take a ticket, read what the project already knows, scan the code, and show a plan for building it: which files change, which new files are needed, and what to watch out for. The `tech-lead` subagent does the code work; this skill gathers the input and shows the result.

## Ground rules

- **Read-only.** Don't write code, edit files, or change the Jira ticket. If the user asks to save the plan, do that only then (default path: `docs/design/<ticket key or short-name>.md`).
- **Ask only what the code can't answer.** Read the ticket and the code first. Ask the user only about gaps that change the design. Never invent requirements, numbers or names — put them under **Open questions**.
- **Every question uses AskUserQuestion**, never a plain-text question.
  - Give 1–3 suggested options built from the ticket, the context files and the code. Mark the best one "(Recommended)".
  - The user can type their own answer in the built-in **Other** textbox. Say so in the question text.
  - Group up to 4 related questions in one call.
  - Every question after the first has **Retry previous answer** as its last option. If picked, ask which answer to change, re-ask it, and continue.
- **No personal or secret data.** Never ask for, copy or repeat:
  - names tied to records, email addresses, phone numbers, home addresses, dates of birth
  - government IDs, bank or card numbers, tax, income, medical or case/application records
  - gender, race, religion or national origin of real people
  - passwords, API keys, tokens, connection strings, MFA codes or any other credential

  If the ticket or pasted notes contain any of this, stop, do not repeat it, tell the user it looks like personal or sensitive data that must not go into AI tools, and ask them to redact it or use made-up examples. Follow your organisation's data policy if it is stricter.

## Output style

Write every question, summary and file this skill produces so a junior developer or a manager can follow it:

1. **Short and point-wise.** Bullets or numbered steps, not paragraphs. One idea per bullet, under 20 words where possible.
2. **Simple, everyday English.** "Use" not "utilise", "fix" not "remediate", "show" not "render".
3. **Explain technical terms once**, in plain words in brackets — e.g. "cache (a saved copy kept for speed)". Spell out acronyms the first time.
4. **Precise, not vague.** Name the exact file, screen, number or step. "Takes 12 seconds to load", not "slow".
5. **Lead with the answer.** Give the result or decision first, then the reason.
6. **Neutral and plain.** No blame, slang, emojis or exclamation marks.

## Step 1 — Get the ticket

Use what came with the request first.

- **A Jira key (e.g. `ABC-123`) and a Jira connector is available:** fetch the summary, type, description, acceptance criteria and linked issues. Say in one line that you fetched it.
- **A key but no Jira connector:** ask with AskUserQuestion (the first question, so no **Retry previous answer**) — **Ticket details**: Paste the summary, description and acceptance criteria in Other (Recommended), Describe the feature in a few lines in Other.
- **Pasted text or a description:** use it as is.

Check the ticket for personal or secret data (see the ground rules) before going on.

## Step 2 — Find the project context

1. Find the repo root with `git rev-parse --show-toplevel` (the current folder if it isn't a git repo).
2. Look for `PROJECT_CONTEXT.md` in the repo root or `docs/`, and `SYSTEM_CONTEXT.md` in the parent folder or at the path its **System** section names.
3. **In a parent folder with several repos:** read `SYSTEM_CONTEXT.md` (or list the subfolders that are git repos) and work out which repos the ticket touches. If it isn't clear, ask — **Repos**: the likely repos (Recommended), All repos, Retry previous answer.
4. **No context file:** say in one line "No PROJECT_CONTEXT.md found — the plan will be based on a code scan only." and carry on. Don't stop to ask.

## Step 3 — Clear up what blocks the design

Skim the ticket against the code area it names. Ask only about gaps that would change which files are touched or how, for example:

- which screen or API the change belongs to, when there are several candidates
- whether existing data must keep working (backward compatibility)
- an acceptance criterion that can be read two ways

Offer the likely answers you found in the code as options. Skip this step if nothing blocks the design — small gaps go into **Open questions** instead.

## Step 4 — Hand off to the tech lead

Start the `tech-lead` subagent (`ai-sam:tech-lead`) in **design** mode. Give it:

- the full ticket text, and the user's answers from Step 3
- the repo root(s) to look in
- the context file paths found in Step 2, or "none found"

Wait for its plan.

## Step 5 — Check and show the plan

1. Spot-check the plan before showing it:
   - Every file under **Files to update** exists.
   - Every file under **New files** sits in a folder that exists or follows the codebase's layout.
   - Every acceptance criterion appears in **Acceptance criteria → where each is built**.

   Fix small slips yourself. If the plan misses something big, send it back to the subagent with what is wrong.
2. Show the plan in the chat as the subagent returned it.
3. Ask with AskUserQuestion — **Plan**: Looks good (Recommended), Retry, Retry with edits, Ask a follow-up.
   - **Retry** — ask the subagent for a fresh plan with a different approach, and say what to avoid from the last one.
   - **Retry with edits** — ask what to change (Simpler approach, Fewer files, More detail on one part, or **Other**). Send only that change to the subagent, keep the rest, and show the result.
   - **Ask a follow-up** — answer the user's question about the plan, reading the code again if needed.

   Repeat until the user picks **Looks good**.
4. Once the user picks **Looks good**, stop. In one line, mention what is available:
   - Save the plan to a file, if they want it.
   - Run `/ai-sam:create-project-context` if the plan's **Notes** list context file drift, or no context file was found.
