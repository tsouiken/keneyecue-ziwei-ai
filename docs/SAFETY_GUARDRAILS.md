# Safety guardrails — scope

`safety/` implements one slice of a much larger ethics/safety design for a
system that processes birth data, chat content, and AI inference about
personality traits (referred to internally as "§21"). This document says
plainly what is built and what is not, so nobody mistakes this module for
full compliance.

## What `safety/` does

| Module | Covers |
|---|---|
| `banned_inference.py` | Scans AI-drafted output for the ten forbidden-inference categories (medical/psych diagnosis, orientation/identity, protected identity, criminal/violence labeling, unverifiable moral judgment, creditworthiness/capability, major life-decision conclusions, minor sexualization, weakness-as-manipulation-entry framing, absolute-language conclusions) plus this repo's pre-existing brand-level bans on promise-style astrology language (AGENTS.md §2). |
| `risk_classifier.py` | Tags a user request LOW / MEDIUM / HIGH per the spec's own example situations, and separately flags manipulation requests (e.g. "help me make him afraid of losing me") for refusal + redirect. |
| `minor_protection.py` | Flags the specific combination the spec targets — a minor is identified *and* the request carries pursuit/control/isolation/private-content intent — without blocking ordinary mentions of minors. |
| `disclaimers.py` | The fixed disclaimer strings (general / third-party-data / high-risk) plus this repo's existing symbolic-astrology disclaimer, composed by context. |
| `__init__.py` (`assess()`) | Single entry point tying the above together into one decision object a caller can act on before and after generation. |

All of it is a keyword net over the spec's own example phrasing, deliberately
biased toward false positives, pure-stdlib, and covered by
`tests/test_safety.py`. It is meant to be called from wherever this app
generates AI output — it doesn't call anything itself yet, since `app.py` is
still a stub with no generation logic to hook into.

## What it explicitly does not do

Everything below requires product/backend work this slice doesn't attempt.
Building it is a separate, much larger effort:

- **Consent management** — no consent-type tracking (service / object-profile
  storage / chat storage / model-improvement / marketing / third-party
  sharing), no opt-out flow, no "user-stated, not platform-verified" labeling
  for third-party consent claims.
- **Data minimization enforcement** — no schema, so nothing here makes any
  field actually optional or supports a "no birth data" / "one-shot analysis"
  mode.
- **Retention, encryption, access control, audit logging** — no database, no
  encryption-at-rest, no staff RBAC, no audit trail for reads/exports/deletes.
- **Deletion / export / correction rights** — no APIs for deleting a profile,
  a conversation, or an account; no data-portability export; no "reset object
  model" function.
- **Minor age verification** — `minor_protection.py` detects mentions of a
  minor in text, which is not the same as an age-gate or guardian-consent flow
  at signup.
- **Risk classifier is not a moderation system** — it is a keyword net, not a
  trained classifier, has no human-review escalation path, and is not wired
  to any incident-response process.
- **UI copy and consent prompts** — the §21.12/21.10 fixed prompts exist as
  strings in `disclaimers.py`; nothing renders them anywhere yet.
- **Pre-launch/post-launch testing & monitoring program** — no red-team test
  set beyond `tests/test_safety.py`'s unit coverage, no refusal-rate
  tracking, no periodic-review process.

Building any of the above should start from the specific bullet, not from
"finish the rest of §21" — each is its own scoped task with its own design
decisions (storage choice, auth model, admin surface, etc.) that need to be
made deliberately rather than inferred from this doc.
