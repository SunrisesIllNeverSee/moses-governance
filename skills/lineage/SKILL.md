---
name: lineage
description: "MO§ES™ lineage custody — cryptographic origin verification. Proves the governance chain traces to the patent filing anchor. Use when verifying sovereign custody, checking chain integrity, generating lineage badges, or attesting provenance."
allowed-tools: [Bash, Read]
---

# MO§ES™ Lineage Custody

Cryptographic origin verification for the governance chain. Every sovereign
MO§ES™ implementation traces its audit chain back to the MOSES_ANCHOR — a
SHA-256 hash derived from the patent filing components. Chains not rooted
here fail verification as a cryptographic fact, not a policy.

## Commands

| Command | What it does |
|---------|-------------|
| `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lineage.py" init` | Anchor genesis to origin filing |
| `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lineage.py" verify` | Confirm three-layer chain: archival -> anchor -> live ledger |
| `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lineage.py" status` | Human-readable custody summary |
| `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lineage.py" badge` | Shareable proof block |
| `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lineage.py" attest` | Machine-verifiable signed attestation JSON |
| `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lineage.py" check` | Exit 0/1 for CI integration |

## Three-Layer Custody

```
Layer -1 (archival)  — pre-filing provenance chain
         |
Layer  0 (anchor)    — MOSES_ANCHOR from patent serial + DOI
         |
Layer  1 (live)      — running audit chain, every entry linked
```

All three layers must verify for SOVEREIGN CUSTODY CONFIRMED.

## When to Use

- On first session with a new installation — run `init` to anchor
- Before any high-stakes operation — run `verify` to confirm chain
- When sharing provenance proof — run `badge` or `attest`
- In CI pipelines — run `check` for automated gating

Patent pending: Serial No. 63/877,177 | DOI: https://zenodo.org/records/18792459
