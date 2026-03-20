---
name: coverify
description: "CoVerify — commitment conservation verifier for MO§ES™. Extract commitment kernels, measure Jaccard similarity, detect ghost tokens, and classify commitment leakage. Use when verifying governance held across transformations, checking if meaning survived compression, or testing signal integrity between agents."
allowed-tools: [Bash, Read]
---

# CoVerify — Commitment Conservation Verifier

Verifies whether semantic commitment is conserved across transformations.
The Commitment Conservation Law: `C(T(S)) = C(S)` — commitment survives
transformation when enforcement is active. It leaks when enforcement is absent.

## Commands

| Command | What it does |
|---------|-------------|
| `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/commitment_verify.py" extract "<text>"` | Extract commitment kernel + input hash |
| `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/commitment_verify.py" compare "<a>" "<b>"` | Jaccard score + CONSERVED/VARIANCE/DIVERGED verdict |
| `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/commitment_verify.py" ghost "<original>" "<transformed>"` | Ghost token leakage report + cascade risk |

## When to Use

- After governance mode changes — verify constraints weren't softened
- When comparing outputs from two different AI systems on the same input
- When auditing whether a document transformation preserved its commitments
- When ghost token cascade risk needs quantification

## Verdicts

| Verdict | Meaning |
|---------|---------|
| CONSERVED | Jaccard >= 0.8 — commitment kernel survived |
| VARIANCE | Same input hash, low Jaccard — model extraction differs, not a leak |
| DIVERGED | Different inputs, low Jaccard — commitment leaked |

## Ghost Tokens

Ghost tokens are commitment tokens present in the original but absent after transformation.
Cascade risk is HIGH when modal/enforcement anchors (must, shall, never, always) leak —
downstream reasoning inherits the softening without visible symptoms.

Patent pending: Serial No. 63/877,177
