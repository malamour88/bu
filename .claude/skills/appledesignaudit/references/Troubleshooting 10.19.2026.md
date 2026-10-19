<div align="right">10.19.2026</div>

# Troubleshooting

Problems users hit with this workflow, and what to do.

## "Claude cannot find the skill"

For this skill: the folder must contain `SKILL.md` at its top level, at `.claude/skills/appledesignaudit/SKILL.md` in the project, or `~/.claude/skills/appledesignaudit/SKILL.md` for a personal install. Restart Claude Code after adding it, then type `/` and look for `appledesignaudit`.

For the optional upstream HIG mirror: cloning the whole NutshellEngineering repository into `~/.claude/skills` puts `SKILL.md` one level too deep. The real skill folder inside that repository is `skills/apple-design-skill`. Copy that folder, with its `references`, to `~/.claude/skills/apple-design-skill`. The documented install uses the plugin marketplace instead:

```text
/plugin marketplace add https://github.com/NutshellEngineering/apple-design-skill
/plugin install apple-design-skill@apple-design-skill-marketplace
```

## "The review is generic and ignores the rules"

Start every request with "Use the appledesignaudit skill for this task" and ask for confirmation that it was read before the review starts. When you are the reviewer: confirm in one line by naming the six checks, run the inventory script, and make every finding carry a file, a current value, and a replacement value. A finding without a number is the symptom to fix.

## "It rewrote the whole file"

Add "Do not touch anything I did not ask you to change" to every fix request and name the finding numbers. When you are the fixer: edit the specific declarations, keep formatting, show before and after lines, and stop at the end of the batch.

## "The result looks like Apple's site, not my brand"

Add the brand preservation clause: keep the current colors and identity, apply only the structural rules (type scale, spacing, hierarchy, contrast, motion). When fixing contrast, move lightness, not hue. If a fix changes the layout concept or the imagery, it has overreached.

## "I do not see a difference after the fixes"

Check the priority order. The first batch should hold the three highest impact findings, which are usually hierarchy and type scale, not a 2px padding nudge. Compare before and after screenshots at the same viewport size; differences in priority, spacing, and readability are easy to miss when the two shots differ in size.

## "You gave a contrast ratio for text over a photo"

Do not. Report it as not measurable from source and recommend a manual check with a browser contrast tool on the rendered page, or propose an overlay or solid backing that makes the pair measurable.
