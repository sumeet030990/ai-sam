# ai-sam

End to end workflow skills for any projects you work on, packaged as a Claude Code plugin.

## Skills

- `/ai-sam:create-project-context` — interviews you about a repo (goals, stack, dependency manifests, commands) and writes a `PROJECT_CONTEXT.md` that later coding sessions read before writing code. In a parent folder it writes a `SYSTEM_CONTEXT.md` that maps the repos and how they connect.
- `/ai-sam:create-jira-ticket` — asks the questions a story, bug, task, epic or spike needs, then writes the ticket in plain, point-wise English using the standard format for that type. Shows the finished ticket in the chat as Markdown, ready to paste into Jira or any rich text editor, with Retry and Retry with edits options before it is final. Follows the team's `JIRA_CONFIG.md` when one exists.
- `/ai-sam:setup-jira-config` — asks once how your team writes tickets (summary format such as `[FE]` tags or a custom pattern, checklist or Gherkin acceptance criteria, and custom templates that fully replace the standard Story, Bug, Task, Epic or Spike formats) and saves it in a `JIRA_CONFIG.md`. Save it for the team per repo (`JIRA_CONFIG.md` in the repo root, shareable by committing it), for yourself across all repos (`~/.claude/ai-sam/JIRA_CONFIG.md`), or for yourself in one repo (`JIRA_CONFIG.local.md` in the repo root, gitignored) to override the team's rules without changing them for anyone else.

### How Jira configs combine

Settings are merged section by section (summary format, acceptance criteria style, and each ticket type's template). For each section the highest file that sets it wins:

1. `JIRA_CONFIG.local.md` — your overrides for this repo
2. `JIRA_CONFIG.md` — the team's rules for this repo
3. `~/.claude/ai-sam/JIRA_CONFIG.md` — your defaults everywhere
4. The built-in standard format

So a local file with only `Acceptance criteria style: Gherkin` gives you Gherkin while you keep the team's summary tags and templates, and future team changes to those still apply to you.

### Project context for multi-repo projects

For a project made of several repos (backend + frontend, microservices, micro-frontends, or a monorepo):

1. Run `/ai-sam:create-project-context` in **each repo**. Each one gets its own `PROJECT_CONTEXT.md` with its stack, versions and manifests.
2. Run it again in the **parent folder** (or monorepo root). It writes a `SYSTEM_CONTEXT.md` that only references each repo's context file and records how the repos connect.
3. Re-run it in the parent whenever a repo is added or removed, or a repo's context changes.

## Testing locally

Validate the manifests after any structural change:

```bash
claude plugin validate .
```

Start a Claude Code session with the plugin loaded from this folder:

```bash
claude --plugin-dir /path/to/ai-sam
```

This loads the plugin for that session only. It doesn't install anything or change your settings, and plain `claude` runs without it. The plugin is read at startup, so restart the session after editing a `SKILL.md`.


## Installing

```bash
claude plugin marketplace add /path/to/ai-sam
claude plugin install ai-sam@ai-sam
```

After changing the plugin, run `claude plugin update ai-sam` and restart Claude Code.
