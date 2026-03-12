---
name: stamp
description: >
  Embeds a MO§ES™ governance stamp into every document produced this session. The stamp carries the active mode, posture, role, session ID, action sequence number, and integrity hash — making the output itself the audit record. Use when you want governed documents, when producing outputs that need to be traceable, or when you say 'stamp documents', 'governed output', 'embed governance', or 'stamp on'.
---
Embed a governance stamp at the bottom of every qualifying document. Stamp includes: mode, posture, role, session ID (first 8 chars of SHA-256 of timestamp + first message), action sequence number, integrity hash (SHA-256 of title+mode+posture+action#), runtime, and copyright. If SHA-256 unavailable use structured placeholder: sha256:[title-slug]:[mode]:[action#]. When both /docs and /stamp are active: doc header at top, stamp at bottom.
