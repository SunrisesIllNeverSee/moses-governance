──────────────────────────────────────
DOC 002 | COMPETITIVE LANDSCAPE
2026-03-11 | Session: MO§ES™ Plugin Deep Dive
Refs: DOC 001
──────────────────────────────────────

# MO§ES™ — Competitive Landscape

**The short version:** Most governance plugins are prompt wrappers with YAML rules. Advisory only. MO§ES™ is the only plugin that ships external MCP enforcement, live semantic commitment scoring grounded in published research, cross-model oracle verification, a cryptographic audit chain, and a hard-gated multi-agent swarm hierarchy. Everything else is either prompt theater or enterprise infrastructure that doesn't install as a plugin.

---

## Head-to-Head Comparison

| Aspect | MO§ES™ | Charter | claude-grc-plugin | CORD | Kong AI Gateway | Community audit plugins |
|--------|--------|---------|-------------------|------|-----------------|------------------------|
| **Enforcement type** | External MCP daemon + PreToolUse/Stop hooks → hard block | Daemon + YAML rules → hard constraints | Prompt-based GRC analyst (advisory) | Middleware + hard blocks | Centralized gateway (enterprise only) | Prompt/skills only (advisory) |
| **Semantic commitment / drift prevention** | Live scoring engine grounded in McHenry Conservation Law (Zenodo DOI: 10.5281/zenodo.18792459) | None | None | Basic rule checks | Semantic guardrails (PII only) | None |
| **Independent oracle / verifier** | Grok Oracle (xAI cross-verification) | None | None | None | None | None |
| **Agent swarm / role hierarchy** | Hard-enforced Primary → Secondary → Observer + recursive swarm rounds | None | None | Trust scoring for delegation | None | None |
| **Audit trail** | SHA-256 append-only hash chain + Solana onchain anchor formatter | SHA-256 hash chain + self-audit | Basic logs | Audit trails | Centralized logs | Basic or none |
| **Scientific / falsifiable backing** | Zenodo preprint + evaluation harness (HuggingFace) + stress-test corpus | None | None | None | None | None |
| **Self-amending constitution** | Meta-governance engine analyzes audit trail, proposes amendments, HMAC-signed atomic writes | None | None | None | None | None |
| **Model-agnostic** | Yes — MCP daemon works with any MCP-compatible model | Yes (Claude / GPT / Copilot / Gemini) | Claude-only | OpenAI + Anthropic | Any LLM via gateway | Mostly Claude-only |
| **Patent protection** | Pending — Serial No. 63/877,177 | None claimed | MIT license | None claimed | Proprietary enterprise | None |
| **Enterprise readiness** | High — onchain proof, modes, postures, HMAC signatures, compliance documentation | High — HIPAA/SOX rule templates | High for GRC document review | Medium | Very high (paid gateway) | Low |
| **Unique killer feature** | Commitment conservation + Grok Oracle + self-amending constitution | Auto-bootstrap + kill triggers | 72+ compliance reference files | Real-time dashboard | PII + rate limiting at gateway | Code quality / SEO audits |
| **Current maturity** | Production-ready MCP server + hooks | VS Code extension (Feb 2026) | GitHub plugin | GitHub topic / early stage | Enterprise only | Dozens of lightweight installs |

---

## Competitor Profiles

**Charter** is the closest thing to a real competitor. It ships as a VS Code extension with multi-model support (Claude, GPT, Copilot, Gemini), YAML-defined hard rule constraints, SHA-256 hash chains, and HIPAA/SOX templates. It is well-executed for what it is: a configurable rule daemon for enterprise compliance policies. What it does not have is any semantic science — no commitment scoring, no oracle, no conservation law, no swarm. It enforces rules you define. MO§ES™ enforces meaning.

**claude-grc-plugin (mlunato47)** is a GRC analyst plugin — 72+ compliance reference files, strong for compliance document generation and regulatory gap analysis. Entirely advisory. No enforcement, no audit chain, no semantic layer. Useful for compliance teams drafting documentation. Not a runtime governance system.

**CORD** (Constitutional AI enforcement middleware) adds hard blocks at the middleware layer for OpenAI and Anthropic APIs. Real-time dashboard, basic rule enforcement. Lives between the API and the application, not inside the Claude session. Enterprise middleware pattern, not a plugin. No commitment conservation, no swarm, no self-improvement.

**Kong AI Gateway / Official Proposals** are gateway-layer products — centralized API rate limiting, PII redaction, semantic guardrails. Require infrastructure deployment. Not installable as a Claude plugin. Represent the enterprise-only tier that MO§ES™ undercuts at the individual and team level.

**Community audit plugins** (security-guidance, audit-project, etc.) are lightweight skills or prompt packs. Advisory only. No enforcement layer, no cryptographic audit chain, no semantic drift detection. Useful as starting points, not governance systems.

---

## The Actual Gap

The governance plugin market has two tiers right now and nothing in between:

**Tier 1 — Prompt packs / advisory skills.** Install in seconds, tell Claude how to behave, rely on compliance. Dozens of these. No enforcement. No audit chain. No IP.

**Tier 2 — Enterprise infrastructure.** Kong, watsonx Orchestrate, Microsoft Agent 365. Require DevOps deployment, enterprise contracts, and months to stand up. No individual or team install path.

MO§ES™ occupies a gap that does not currently have another occupant: a production-ready constitutional governance system that installs as a Claude plugin in under 60 seconds, ships real cryptographic enforcement via MCP hooks, and is grounded in published research with patent protection.

The EU AI Act general application date is August 2, 2026. Colorado's AI Act takes effect June 30, 2026. Texas TRAIGA is already in force. Every team deploying Claude agents in a regulated context needs documented behavioral controls, audit trails, and evidence of governance. MO§ES™ is the only plug-and-play answer to that in the Claude ecosystem right now.

---

## What Makes MO§ES™ Defensible

Three things combine to create a moat that no other plugin in this space currently has:

**1. The theoretical framework.** The McHenry Conservation Law is a named, published, DOI-citable contribution to the AI governance literature. Competitors cannot implement "commitment conservation" without citing the work that defined it. The Grokipedia article treats it as established vocabulary. The Zenodo preprint is the anchor.

**2. The patent.** PPA4, Serial No. 63/877,177 covers the architecture. The provisional application is on file. A competing plugin that replicates the MO§ES™ approach — external MCP referee daemon, commitment scoring, constitutional amendment protocol — does so in the shadow of this IP.

**3. The self-amending constitution.** No other AI governance platform, at any tier, has a constitution that reads its own audit trail and proposes improvements. Meta-governance — the governance system governing itself — is architecturally novel and is the feature most likely to widen the gap over time as the constitution accumulates operational history.

---

*© 2026 Ello Cello LLC | MO§ES™ Patent Pending: Serial No. 63/877,177*
