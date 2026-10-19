<div align="right">10.19.2026</div>

# Worked Example

The source guide shows these findings from a landing page Claude generated without prior design rules. The numbers belong to that example. They are not an official Apple type scale and not a guaranteed result for every site. Use the example to calibrate how specific a finding should be.

## Findings as reported

1. Type scale. Seven font sizes in use: 14, 15, 16, 18, 20, 24, 32px. Proposed: collapse to four sizes, 15, 20, 28, 44px.
2. Spacing. Section padding alternates between 48px and 52px with no visible reason. Proposed: 48px everywhere.
3. Hierarchy. Hero title 32px with a 24px subtitle. The gap is too small to signal priority. Proposed: 44px title, 20px subtitle. The example also suggests 60% opacity on the subtitle. Measure contrast after applying opacity before accepting that part.
4. Contrast. Body text #7A7A7A on #FFFFFF. The source guide reported 4.1:1; the computed value is 4.29:1. Either way it fails the 4.5:1 normal text minimum. Proposed: #5C5C5C, which measures 6.69:1 on white.
5. Motion. Button transition `all 0.6s linear`. Proposed: a transform only transition of 0.15s with an ease out curve.

```css
/* Before */
transition: all 0.6s linear;
/* After */
transition: transform 0.15s cubic-bezier(0.4, 0, 0.2, 1);
```

## Verifying the contrast numbers

```bash
python3 scripts/contrast.py "#7A7A7A" "#FFFFFF"   # 4.29:1, fails normal text
python3 scripts/contrast.py "#5C5C5C" "#FFFFFF"   # 6.69:1, passes
python3 scripts/contrast.py "#000000" "#FFFFFF" --alpha 0.6 --size 20   # the 60% subtitle idea
```

The correction from 4.1:1 to 4.29:1 is the point of the "no unmeasured ratios" rule. A reviewer who estimates will be off by enough to matter at the threshold.

## What the author reported

Five fixes in about 15 minutes made a visible difference to the page. Treat that as one experience recorded in the source, not as a promise about time or conversion impact. Conversion effects need real measurement on the user's own site.
