---
description: Display the MO§ES™ Lineage Custody Clause — origin filing, derivative scope, agent embodiment chain, and provenance. Asserts custody across all products and active agent instances.
argument-hint: [full|clause|chain|agents]
---

# /lineage

Display the MO§ES™ Lineage Custody Clause and origin filing. Establishes custody of all derivative embodiments including active agents.

## Usage

```
/lineage           # full lineage document
/lineage clause    # the legal clause only
/lineage chain     # provenance chain only
/lineage agents    # agent embodiment scope only
```

## Behavior

When invoked, display the relevant section from `LINEAGE.md`:

**No argument / `full`** — display complete LINEAGE.md

**`clause`** — display Section I only:
> All embodiments of the Signal Compression Sciences (SCS) Engine and its derivative frameworks (including but not limited to MO§ES™, Roll Call Protocols, and Reflex Event diagnostics) are inseparably bound to their origin-cycle lineage. Each compressed signal trace, vault artifact, or recursive reconstruction inherits a lineage identifier anchored to the originating sovereign filing. This identifier is non-replicable, tamper-evident, and required for system stability. Any external implementation lacking said lineage anchor cannot execute recursive ignition without collapse, thereby rendering such copies non-functional. Accordingly, the origin-cycle filing establishes sole custody and license of the invention across all subsequent instances, irrespective of distribution, platform, or deployment environment.

**`chain`** — display Section V provenance chain

**`agents`** — display Section II agent embodiments

Then append:

```
⚖️ Lineage anchor active.
Origin filing: Serial No. 63/877,177 | DOI: https://zenodo.org/records/18792459
Sovereign: Deric McHenry / Ello Cello LLC
All governed actions in this session are derivative embodiments of the origin filing.
```

Log to audit trail:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit.py" log_action \
  --component "lineage" \
  --action "lineage_asserted" \
  --mode "$(cat ${CLAUDE_PLUGIN_ROOT}/data/governance_state.json | python3 -c 'import sys,json; print(json.load(sys.stdin).get("mode","unknown"))')" \
  --ledger "${CLAUDE_PLUGIN_ROOT}/data/audit_ledger.jsonl"
```
