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

## Amendments

### Amendment 1 (2026-10-02): a second ontology started; what that triggers

**What happened.** `Integral-Productivity/vertical-development-ontology` was
started on 2026-10-02 (v0.1.0, private repository). It is a vocabulary for the
stages of adult ego development and the lineage of their names.

**The rule in this ADR was met.** This ADR says: "Every further ontology …
must name its consumer and its 90-day decision in its first ADR before
modeling begins." The new repository's ADR-0001 names the
`vertical-development-scholarship` skill as first consumer, and the decision:
the skill's stage names are checked against the ontology, not maintained by
hand. Its ADR-0003 sets milestones and the same decision date as this ADR,
2027-01-02.

**Two other records said more than this ADR does.** The approach document
(section 6) and the GlassFrog project note for this repository both said: if
the plugin decision did not get better by 2027-01-02, stop and diagnose
*before starting a second ontology*. This ADR has no such rule. On 2026-10-02
the role-holder chose to run both tracks. This amendment records that choice
here, so that the three records agree.

**Decision.**

1. Both tracks run. On 2027-01-02 each is judged on its own consumer. The
   result of one does not excuse the other.
2. One question is added for that date: *did two tracks at the same time cost
   either of them its result?* If yes, the rule "one ontology at a time" goes
   into the approach document. If no, the rule becomes "a new track needs a
   first consumer as small as a skill".
3. The Vertical Development Stage axis in this ontology and the stage labels
   in the new one are the same eight names. The new repository checks this
   (its CQ-20) against a copy of this repository's scheme. A change to the
   axis here is a coordinated change there.

**Triggers this fires in other ADRs.** They are listed here and are not done
by this amendment.

- ADR-0002, trigger to revisit: "A second ontology … is started → extract the
  shared tooling into a template repo."
- ADR-0004, trigger to revisit: "Second ontology starts → create
  `Integral-Productivity/ontology-hub` …, move `infra/ontology-router/`
  there, and transfer the custom domain to the hub repo."
- ADR-0004, decision 1: the new ontology's IRIs use the path prefix
  `/vertical-development/`. That prefix is not in `registry.json`, as a
  prefix or as a reserved name. It must be registered before the new
  ontology publishes an IRI.
- ADR-0004, decision 4: the persistence decision (w3id) is due at "the second
  ontology's first public release". The new repository stays private until
  that decision is made.

**Risk named.** Two tracks on one day is the attractor that the Context of
this ADR describes. The countermeasure is the dated question in item 2, not a
prohibition.
