<div align="right">10.19.2026</div>

# Fix Batch Template

Fix findings three at a time. Small batches make it easy to see what changed, compare the result, and revert a change that did not help. A typical site needs four or five rounds.

## The fix request

```text
Fix findings 1 to 3 only. After each fix, show the lines that changed before and after. Do not touch anything I did not ask you to change. When done, re-review only these three aspects and tell me whether they now meet the check criteria.
```

Arabic original:

```text
أصلح الملاحظات من ١ إلى ٣ فقط. بعد كل إصلاح، اعرض الأسطر التي تغيّرت قبل التعديل وبعده. لا تلمس أي شيء لم أطلب تغييره. عند الانتهاء، أعد المراجعة لهذه الجوانب الثلاثة فقط، وأخبرني هل أصبحت تستوفي معايير الفحص.
```

## The brand preservation clause

Add this to any fix request when the result drifts toward a generic Apple look:

```text
Keep my current colors and identity. Apply the structural rules only: font sizes, spacing, visual hierarchy, contrast, and motion.
```

Arabic original:

```text
حافظ على ألواني وهويتي الحالية. طبّق القواعد البنيوية فقط: أحجام الخطوط، والمسافات، والتسلسل البصري، والتباين، والحركة.
```

## What a completed batch report looks like

```markdown
## Batch 1: findings 1 to 3

### Finding 1 (type scale) styles/hero.css:12
Before: `font-size: 32px;`
After:  `font-size: 44px;`
Re-check: hero title now sits on the 15 / 20 / 28 / 44 scale. PASS.

### Finding 2 (contrast) styles/base.css:40
Before: `color: #7A7A7A;`
After:  `color: #5C5C5C;`
Re-check: 6.69:1 on #FFFFFF (contrast.py). PASS for normal text.

### Finding 3 (motion) styles/buttons.css:8
Before: `transition: all 0.6s linear;`
After:  `transition: transform 0.15s cubic-bezier(0.4, 0, 0.2, 1);`
Re-check: 150ms, ease out curve, single property. PASS.

Nothing else was changed. Ready for findings 4 to 6 when you are.
```
