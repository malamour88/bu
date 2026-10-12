// Plan Filler Workflow
// Version 10.12.2026
//
// Runs on the Mac inside the Claude Code session, through the Workflow tool.
// One agent fills each batch file written by the organizer's batches subcommand,
// a second agent re reads every answer as a skeptic, then the session runs merge.
//
// Call:  Workflow({ scriptPath: "<this file>", args: { batches: [...paths], runbook: "<runbook path>", verify: true } })
// args.batches is the contents of "Batch List MM.DD.YYYY.json" written by batches.
// args.verify false skips the skeptic pass. Default is true.

export const meta = {
  name: 'fill-organizer-plan',
  description: 'Fill the Mac File Organizer plan from file content, one agent per batch, then verify every answer',
  phases: [
    { title: 'Fill', detail: 'one agent per batch file, answers written next to the batch' },
    { title: 'Verify', detail: 'a skeptic re reads each batch and fixes weak or unsafe answers' },
  ],
}

const batches = (args && Array.isArray(args.batches)) ? args.batches : []
if (!batches.length) throw new Error('args.batches must be the list of batch files written by the batches subcommand')
const runbook = (args && args.runbook) || '~/Organizer Kit/Mac File Organizer Runbook 10.12.2026.md'
const doVerify = !(args && args.verify === false)

const FILL = {
  type: 'object',
  properties: {
    batch: { type: 'string' },
    answersFile: { type: 'string' },
    answered: { type: 'integer' },
    inbox: { type: 'integer', description: 'rows sent to 001 Inbox because the content was unclear' },
    opened: { type: 'integer', description: 'files opened with Read or textutil because the snippet was empty' },
    unreadable: { type: 'array', items: { type: 'string' }, description: 'row ids whose file could not be read at all' },
    questions: { type: 'array', items: { type: 'string' }, description: 'row id and one line each, only where a human must decide' },
  },
  required: ['batch', 'answersFile', 'answered'],
}

const VERDICT = {
  type: 'object',
  properties: {
    batch: { type: 'string' },
    checked: { type: 'integer' },
    fixed: { type: 'integer' },
    fixes: { type: 'array', items: { type: 'string' }, description: 'row id and what changed, one line each' },
  },
  required: ['batch', 'checked', 'fixed'],
}

const shortName = p => p.split('/').pop().replace(/\.json$/, '')

const RULES = `
Rules that decide every row. The runbook sections 2, 3 and 4 and step 2 of section 6 hold the full text, read them first.
- action is move, trash, print, or skip. new folder is relative to the root, for example 002 Personal/001 Finance.
- new name is the description only. The script adds the code, the company, the date stamp and the extension.
- The description names the document type, the person or party, the last 4 digits of any account, policy, VIN or invoice number, and the period, for example "Chase Checking Statement Mohammad Alamour 4821 March 2026".
- No dashes and no underscores. Spaces and dots only. Never a full account number, never a street address or house number.
- CONFIDENTIAL goes at the start of the description on identity documents, passports, visas, medical records, credentials and check images.
- Work rows need a company folder from the fixed list. A Work file whose company is unclear goes to 003 Work/007 Other Work with the reason in notes. Loose Bukrah Foundation files go to 003 Work/001 Bukrah Foundation/001 Organizer Intake.
- Rows flagged moved whole take destination and description from the section 3 mapping. Project folders and bundles get one name for what they are.
- Rows with a prefilled action of trash (duplicate, installer, zero bytes, temp file, archive extracted, empty folder) stay trash unless the content clearly says otherwise. Screenshots are trash unless they show something worth keeping.
- Symlinks, .webloc shortcuts and Google stubs (.gdoc, .gsheet, .gslides) are skip, with a note.
- When the snippet is empty or the row is flagged needs read, open the file: the Read tool for PDFs and images, textutil -convert txt -stdout for docx, rtf and pages. Never guess a name. If the content stays unclear, action move, new folder 001 Inbox, and a short note.
- Every row id in the batch appears exactly once in the answers file.
`

function fillPrompt(batchFile) {
  return `You are filling one batch of the Mac File Organizer plan. Work only on the rows in this batch.

1. Read the runbook at "${runbook}": sections 2, 3 and 4, and step 2 of section 6.
2. Read the batch file "${batchFile}". It holds the rows, each with its current path, flags, a content snippet and Spotlight metadata, and the path of the answers file to write.
3. Decide every row by the rules below. Open files whose snippet is empty.
4. Write the answers file named in the batch as a JSON list, one object per row: {"id": "...", "action": "...", "new folder": "...", "new name": "...", "notes": "..."}. Overwrite it if it exists.
5. Return the structured result. Counts and row ids only, never file contents or account numbers.
${RULES}`
}

function verifyPrompt(batchFile, answersFile) {
  return `You are the skeptic for one batch of the Mac File Organizer plan. Another agent filled it. Assume some answers are wrong and prove it.

1. Read the runbook at "${runbook}": sections 2, 3 and 4.
2. Read the batch file "${batchFile}" and the answers file "${answersFile}".
3. For every row check: is the description supported by the snippet, or by the file itself when the snippet is empty? Open the file when in doubt. Does the answer break a rule: a dash or underscore, five or more consecutive digits that look like an account number, a street address, a missing CONFIDENTIAL on an identity, medical, credential or check document, a Work row without a company folder from the fixed list, a trash row outside 006 Trash, a print row outside 005 To Be Printed, a missing row, a guessed description?
4. Fix every wrong answer in the answers file in place and keep the file a valid JSON list with every row id exactly once. A row whose content you cannot confirm goes to action move, new folder 001 Inbox, with a note.
5. Return the structured result. Counts and row ids only, never file contents or account numbers.
${RULES}`
}

const results = await pipeline(
  batches,
  b => agent(fillPrompt(b), { label: `fill ${shortName(b)}`, phase: 'Fill', schema: FILL }),
  (filled, b) => {
    if (!filled) return { batch: shortName(b), fill: null, verify: null }
    if (!doVerify) return { batch: shortName(b), fill: filled, verify: null }
    return agent(verifyPrompt(b, filled.answersFile), { label: `verify ${shortName(b)}`, phase: 'Verify', schema: VERDICT })
      .then(v => ({ batch: shortName(b), fill: filled, verify: v }))
  },
)

const rows = results.filter(Boolean)
const sum = (list, f) => list.reduce((n, x) => n + (f(x) || 0), 0)
const totals = {
  batches: batches.length,
  filled: rows.filter(r => r.fill).length,
  failed: rows.filter(r => !r.fill).map(r => r.batch),
  answered: sum(rows, r => r.fill && r.fill.answered),
  inbox: sum(rows, r => r.fill && r.fill.inbox),
  opened: sum(rows, r => r.fill && r.fill.opened),
  verified: rows.filter(r => r.verify).length,
  fixed: sum(rows, r => r.verify && r.verify.fixed),
  unreadable: rows.flatMap(r => (r.fill && r.fill.unreadable) || []),
  questions: rows.flatMap(r => (r.fill && r.fill.questions) || []),
  fixes: rows.flatMap(r => (r.verify && r.verify.fixes) || []),
}
if (totals.failed.length) log(`Batches with no answers, run batches again after merge to redo them: ${totals.failed.join(', ')}`)
log(`Filled ${totals.filled} of ${totals.batches} batches, ${totals.answered} rows answered, ${totals.inbox} sent to Inbox, ${totals.fixed} answers fixed by the skeptics. Next: merge, then check.`)
return totals
