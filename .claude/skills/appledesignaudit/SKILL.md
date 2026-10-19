---
name: appledesignaudit
description: Audit a website or web app's visual design against Apple Human Interface Guidelines (HIG) principles and fix the findings in small batches while keeping the site's own brand. Produces a numbered, measurable findings list across six checks (type scale, spacing, hierarchy, contrast, motion, density) with exact current and replacement values, then applies fixes three at a time with before and after diffs. Use this skill whenever the user asks to review, audit, critique, polish, tighten, or "clean up" a site's design, says a page "looks off", "amateurish", or "not premium", mentions Apple style or HIG for a website or landing page, asks about font size consistency, spacing systems, contrast ratios, or transition timing, or wants design fixes applied step by step. Also use it when building a fresh site and the user wants Apple grade visual discipline from the start.
---

# Apple Design Audit

Review a web page the way a disciplined design reviewer would: measure, do not opine. The useful output of a design review is a list of numbers the developer can change. Font sizes in px, spacing values, contrast ratios, transition durations. "Make it cleaner" is not a finding.

This skill adapts Apple HIG principles to the web. It is not affiliated with Apple. The goal is never to make the site look like apple.com. The goal is to apply Apple's structural rules (type scale, spacing rhythm, one clear focal point, measured contrast, short purposeful motion, breathing room) while keeping the site's colors, voice, and personality intact.

## Two modes

1. **Audit mode** (default). Read only. Produce the numbered findings list. Change no code.
2. **Fix batch mode**. Fix exactly the findings the user names, usually three at a time. Show before and after for every changed line. Re-audit only those three aspects and report whether each now meets its threshold.

Never slide from audit into fixing on your own. The user decides which batch comes next, because small batches are how they see what changed, compare results, and revert a bad call.

## Before you audit

- **Get the source if you can.** Findings should cite file and line. With only a URL you can still measure rendered values (computed styles, screenshots), but say plainly that you cannot cite source lines rather than inventing them.
- **Confirm the skill is loaded.** Users often ask "did you read the skill?" Answer with one line naming the six checks so they know the review will not be generic.
- **Inventory the stylesheet first.** Run the inventory script before forming opinions. It extracts every font size, spacing value, transition, and color literal with file and line so the audit rests on data:

  ```bash
  python3 .claude/skills/appledesignaudit/scripts/cssinventory.py <path or paths>
  ```

  For Tailwind or utility class projects, also read the Tailwind config and grep the class names (text-*, p-*, gap-*, duration-*, ease-*). The script catches arbitrary values like `text-[15px]` but not theme tokens.
- **Capture a before screenshot** at a fixed viewport (for example 1440 wide) if a browser is available. The user will compare before and after side by side, and the comparison only works when both shots share the same size.

## The six checks, in order

Run them in this order. Each check lists what to measure, the threshold, and why it matters.

### 1. Type scale

Measure every font size actually in use. A page with seven sizes (14, 15, 16, 18, 20, 24, 32) reads as noisy even when nothing is "wrong", because the eye cannot tell which differences carry meaning. Flag any size that does not sit on a consistent progression and propose a scale of four to five steps. State the current value in px and the exact replacement. Apple's platform minimums are a useful sanity floor (17pt default and 11pt minimum on iOS, 13pt default on macOS); on the web treat anything under 12px as suspect and 16px body as the common baseline.

### 2. Spacing

Look for a base unit. Most clean layouts resolve to multiples of 4px or 8px. List every margin, padding, and gap value that breaks the unit, with its location. Alternating section padding like 48px and 52px with no reason is the classic symptom. The 4px and 8px units are a review heuristic from this workflow, not an Apple mandate, so say so if the user asks.

### 3. Hierarchy

For each screen, name the single element the eye should land on first. Then test whether it actually wins: size, weight, contrast, and whitespace all vote. A 32px hero title next to a 24px subtitle loses because the ratio is too small to signal priority. Say what the focal point is, whether it wins, and if not, which lever (size, weight, color, space) fixes it with an exact value.

### 4. Contrast

Report the measured contrast ratio for every text and background pair you can compute. Thresholds come from WCAG 2.2 and match HIG accessibility guidance:

| Text | Minimum ratio |
|---|---|
| Normal text | 4.5:1 |
| Large text (24px and up, or 18.66px and up when bold) | 3:1 |
| UI components and graphical objects | 3:1 |

Never state a ratio you did not compute. Use the bundled calculator:

```bash
python3 .claude/skills/appledesignaudit/scripts/contrast.py "#7A7A7A" "#FFFFFF"
python3 .claude/skills/appledesignaudit/scripts/contrast.py "#000000" "#FFFFFF" --alpha 0.6
```

Opacity matters: text at 60% opacity must be blended onto its background before measuring, which is what `--alpha` does. For text over gradients or images, report "not measurable from source" and recommend a manual check rather than guessing.

### 5. Motion

List every transition and animation with its duration and easing. Flag anything over 300ms or using `linear`, and say whether the context justifies it (a page level reveal can be longer; a button hover cannot). Flag `transition: all` because it animates properties nobody intended. The 300ms line is a review heuristic, not an Apple rule. Prefer short transform based motion with an ease out curve, for example `transform 0.15s cubic-bezier(0.4, 0, 0.2, 1)`.

### 6. Density

Where is the page crowded, and where is there space that serves nothing? HIG layout guidance is direct about this: give essential information room, and keep unrelated controls far enough apart to tell them apart. Point at specific regions and propose spacing or grouping changes with values. Interactive targets under 44px on touch layouts belong here too.

## Audit output format

Use this exact structure. Order findings by visual impact, highest first, not by check number. Lead with the top five, then the rest.

```markdown
# Design audit: <page or site>

Scope: <files or URL reviewed, viewport, what could not be measured>
Skill checks run: type scale, spacing, hierarchy, contrast, motion, density

## Top five findings
1. [<check>] <file:line or "rendered, no source line"> — <problem in one sentence>. Current: <value>. Replace with: <exact value>.
2. ...

## Remaining findings
6. ...

## Measured contrast pairs
| Foreground | Background | Ratio | Text size | Result |
|---|---|---|---|---|

## Not measurable
<pairs or regions you could not compute, and why>
```

Every finding carries four things: location, the problem in one sentence, the current value, the exact replacement. No general praise. If a check comes back clean, say "no findings" for it in one line.

## Fix batch workflow

When the user says "fix 1 to 3":

1. Restate the three findings you are about to change and nothing else.
2. Make the smallest edit that resolves each one. Do not reformat files, rename classes, or touch neighbors. The user will diff this, and unrelated changes bury the ones that matter.
3. After each edit, show the changed lines before and after.
4. Re-run only the checks those three findings belong to (for example rerun the contrast script on the changed pair) and state pass or fail against the threshold.
5. Stop. Do not start finding 4. Ask which batch comes next.

Expect four or five rounds on a typical site. That pace is the point.

## Guardrails that keep the brand intact

- Keep the brand's palette. Adjust lightness to meet contrast; do not swap hues.
- Apply structural rules only: type scale, spacing, hierarchy, contrast, motion. Do not change copy, layout concept, imagery, or component choices unless a finding requires it.
- If the result starts to resemble a generic Apple page, you have gone past the brief. Pull back.
- Do not promise conversion lifts. The source guide reports one author's 15 minute, five fix improvement; treat that as anecdote, not a forecast.

## Optional: the upstream HIG mirror

The NutshellEngineering `apple-design-skill` plugin bundles a local mirror of Apple's HIG articles. When it is installed (`/plugin marketplace add https://github.com/NutshellEngineering/apple-design-skill` then `/plugin install apple-design-skill@apple-design-skill-marketplace`), consult `references/foundations/typography.md`, `color.md`, `motion.md`, `layout.md`, and `accessibility.md` for the exact wording behind these checks. This skill works without it; the thresholds above already carry the values that matter for the web.

## References in this skill

Read them when the situation calls for it, not up front.

- `references/Review Template 10.19.2026.md`: the copy and paste prompt the user may send you, in English and Arabic, so you recognize it and can hand it to them.
- `references/Fix Batch Template 10.19.2026.md`: the fix request wording, plus the brand preservation clause.
- `references/Worked Example 10.19.2026.md`: a real findings list from a landing page, with corrected contrast math. Read it when you want to calibrate how specific a finding should be.
- `references/Troubleshooting 10.19.2026.md`: what to do when the user says the review is generic, the fixes rewrote the file, the site now looks like Apple's, or nothing visibly changed.

## Scripts

- `scripts/contrast.py`: WCAG contrast ratio for a foreground and background, with optional alpha blending and text size classification. Run `--help` for options.
- `scripts/cssinventory.py`: scans CSS, SCSS, HTML, and component files for font sizes, spacing, transitions, and colors; reports each unique value with counts and locations, and flags off unit spacing and slow or linear transitions.

Source: this skill was built from the Arabic guide "Apple Design Audit, review your site's design with Apple principles" by AI Automation Academy Plus, and from the Apple HIG foundations articles mirrored in the apple-design-skill repository.
