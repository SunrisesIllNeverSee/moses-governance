---
name: doc-numbering
description: "Applies sequential document numbering, timestamps, topic tags, and cross-references to every document created in a session. Auto-activates whenever a new document, file, report, or artifact is created. Maintains a session TOC and enables traceability across all outputs."
origin: MO§E§™
---

# Document Numbering — Session Traceability

Every document created under MO§E§™ governance receives a sequential identifier, timestamp, and topic tag. This creates a traceable index of everything produced in a session.

## Format

```
[SEQ]_[descriptive-name].[ext]
```

Examples: `001_session-header.md`, `002_governance-audit.json`, `002a_governance-audit-addendum.md`

## Numbering Rules

- Sequential 3-digit prefix: `001_`, `002_`, `003_` — never skip, never reuse
- Cross-references (new doc referencing a parent): parent number + alpha suffix (`001a_`, `001b_`) — does NOT consume the next sequential number
- Versions (same doc revised): append `v2`, `v3` before the extension (`002_report-v2.md`)

## Document Header (Required on Every Doc)

```
──────────────────────────────────────
DOC [SEQ] | [TOPIC/THEME TAG]
[YYYY-MM-DD HH:MM] | Session: [description]
──────────────────────────────────────
```

Cross-references add: `Refs: DOC [parent]`
Pivots add: `Pivot: [from → to]`

## Session Header (DOC 001)

The first document of every session is the Session Header:
- Operator: Luthen / Ello Cello LLC
- Timestamp and session theme
- TOC table with columns: Doc | Name | Topic | Time
- TOC updates as new docs are created — never recreated

## After Action Review (Final Doc)

The last document of every session is the After Action Review:
- What was accomplished
- Complete document index
- Pivots tracked
- What carries forward
- Key decisions

## Enforcement Instructions

When creating any document:

1. Determine the next sequential number (check existing docs in session)
2. Apply the `[SEQ]_` prefix to the filename
3. Add the standard header block at the top of the document
4. Update the session TOC (DOC 001) with the new entry
5. If this is the first doc of the session, create the Session Header first
