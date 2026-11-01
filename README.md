# ai-sam

End to end workflow skills for any projects you work on, packaged as a Claude Code plugin.

## Skills

- `/ai-sam:create-project-context` — interviews you about a repo (goals, stack, dependency manifests, commands) and writes a `PROJECT_CONTEXT.md` that later coding sessions read before writing code. In a parent folder it writes a `SYSTEM_CONTEXT.md` that maps the repos and how they connect.
- `/ai-sam:create-jira-ticket` — asks the questions a story, bug, task, epic or spike needs, then writes the ticket in plain, point-wise English using the standard format for that type. Shows the finished ticket in the chat as Markdown, ready to paste into Jira or any rich text editor, with Retry and Retry with edits options before it is final.

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
