# ai-sam — authoring rules

Rules for writing or changing skills in this plugin.

## Every skill has an Output style section

Each `skills/<name>/SKILL.md` must include this section, word for word, right after its **Ground rules**. Skills load on their own, so each one carries its own copy. `create-ticket` covers the same rules in its **Writing style** section.

```markdown
## Output style

Write every question, summary and file this skill produces so a junior developer or a manager can follow it:

1. **Short and point-wise.** Bullets or numbered steps, not paragraphs. One idea per bullet, under 20 words where possible.
2. **Simple, everyday English.** "Use" not "utilise", "fix" not "remediate", "show" not "render".
3. **Explain technical terms once**, in plain words in brackets — e.g. "cache (a saved copy kept for speed)". Spell out acronyms the first time.
4. **Precise, not vague.** Name the exact file, screen, number or step. "Takes 12 seconds to load", not "slow".
5. **Lead with the answer.** Give the result or decision first, then the reason.
6. **Neutral and plain.** No blame, slang, emojis or exclamation marks.
```

Subagents in `agents/` carry the same rules, with the first line reading "Write everything you return so a junior developer or a manager can follow it:".

If you change these rules, update the copy in every `SKILL.md` and agent file too.
