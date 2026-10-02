# 3. The first consumer is the plugin; value is measured by a decision that changes

Date: 2026-10-02

## Status

Accepted

## Context

An ontology with no consumer is a glossary with extra steps. The founder's
own thinking style (high Ideation / Input / Intellection) makes "define
ontologies for every concept I have ever used" an attractor with no natural
stopping point. The methodology's own vocabulary names this risk: intentional
Meta Work versus escapist meta-work.

Candidate first consumers were: AI skills and plugins; coaching clients
(shared vocabulary in contracting and assessment); the Praxis data model; and
the Institute / community (a public good to critique and extend).

## Decision

The first consumer is **`metawork-claude-plugin` and its skills**. The
decision that must get better within 90 days: *when a skill reads or writes
a Meta Work Group, it validates the group against the ontology instead of
trusting the enum strings*, and *the plugin's JSON Schema is generated from,
or asserted equal to, the ontology's notations*.

Concretely, within 90 days of this ADR:

1. CQ-15 runs in the plugin's CI as well as here (schema ↔ ontology sync).
2. `metawork-set-up` and `metawork-diagnose` call `tools/metawork_ontology.py
   lift` + `validate` (or an equivalent) on the markdown backend before
   reporting success.
3. One `metawork-diagnose` pattern ("scope-axis mismatch") is expressed as a
   SHACL shape rather than prose.

Every further ontology (Holacracy, TPD, mappings) must name its consumer and
its 90-day decision in its first ADR before modeling begins.

## Consequences

- Clients, Praxis, and the Institute are explicitly *not* first; they are
  sequenced after the plugin proves the loop closes.
- The ontology's scope is bounded by what the plugin needs plus the
  distinctions the methodology insists on. Pillar *interactions* (the heart
  of the methodology per `methodology.md`) are out of scope for v0.1.
- If item 2 above is not done by 2027-01-02, this ADR is the trigger to ask
  whether the ontology is Meta Work or meta-work.
