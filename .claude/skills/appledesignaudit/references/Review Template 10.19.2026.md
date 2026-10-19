<div align="right">10.19.2026</div>

# Review Template

Hand this to the user when they want the audit prompt, or recognize it when they paste it. Send it only after the site's code or URL is available. With a URL alone, file and line citations are not possible; say so instead of inventing them.

## English

```text
Use the appledesignaudit skill for this task.
Review this site against Apple design principles. Do not edit any code now.
Check the elements in this order and give me a numbered list of findings:
1. TYPE SCALE: which font sizes are actually in use? Identify any size that does not follow a consistent scale. State the current value in px and the exact proposed replacement.
2. SPACING: is there a base unit such as 4px or 8px? List the values that break the pattern and where they are.
3. HIERARCHY: on each screen, what is the one element the eye should see first? Does it actually stand out? If not, why not?
4. CONTRAST: give me the measured contrast ratio for every text and background pair. Flag anything under 4.5:1 for normal text and under 3:1 for large text. Do not give a measurement you could not compute.
5. MOTION: list every transition, its duration, and its easing curve. Flag anything over 300ms or using linear, and say whether the context justifies it.
6. DENSITY: where is the page crowded? Where is there space that does not serve the content?
For each finding: the file and line if available, the problem in one sentence, and the exact replacement value. Order the list by the impact of the fix on the site's visual quality. No general praise.
```

## Arabic (original wording from the source guide)

```text
استخدم مهارة appledesignaudit لهذه المهمة.
راجع هذا الموقع وفق مبادئ Apple في التصميم. لا تعدّل أي كود الآن.
افحص العناصر بالترتيب التالي، وأعطني قائمة مرقّمة بالملاحظات:
١. أحجام الخطوط TYPE SCALE: ما الأحجام المستخدمة فعليًا؟ حدّد أي حجم لا يتبع تدرّجًا متّسقًا. اذكر القيمة الحالية بوحدة px والقيمة البديلة المقترحة بدقة.
٢. المسافات SPACING: هل توجد وحدة أساسية مثل 4px أو 8px؟ اذكر القيم الخارجة عن النسق ومواقعها.
٣. التسلسل البصري HIERARCHY: في كل شاشة، ما العنصر الوحيد الذي ينبغي أن تراه العين أولًا؟ هل يبرز فعلًا؟ وإن لم يبرز، فما السبب؟
٤. التباين CONTRAST: أعطني نسبة التباين المقاسة لكل زوج من لون النص والخلفية. حدّد ما يقل عن 4.5:1 للنص العادي، وعن 3:1 للنص الكبير. لا تقدّم قياسًا لم تتمكن من حسابه.
٥. الحركة MOTION: اذكر كل انتقال، ومدته، ومنحنى التسارع easing المستخدم. ضع للمراجعة ما يتجاوز 300ms أو يستخدم منحنى linear، مع توضيح ما إذا كان السياق يبرّره.
٦. كثافة المحتوى DENSITY: أين يوجد ازدحام؟ وأين توجد مساحة لا تخدم المحتوى؟
لكل ملاحظة: اذكر الملف والسطر إذا كانا متاحين، والمشكلة في جملة واحدة، والقيمة البديلة الدقيقة. رتّب القائمة بحسب أثر الإصلاح في جودة الموقع البصرية. لا تكتفِ بمدح عام.
```

## Notes on the thresholds

- The contrast limits are WCAG 2.2 (Web Content Accessibility Guidelines) values and match Apple HIG accessibility guidance. Large text starts at 18pt (24px), or 14pt (about 18.66px) when bold.
- The 4px and 8px spacing units and the 300ms motion ceiling are review heuristics proposed by this workflow. They are not universal Apple rules. Say that if the user asks.
- Start with the top five findings. A site rarely needs all of them fixed at once.
