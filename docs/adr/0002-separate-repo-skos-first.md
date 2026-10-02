# 2. The ontology lives in its own repo and is SKOS-first

Date: 2026-10-02

## Status

Accepted

## Context

Meta Work now exists in three forms:

1. **Prose** — `metawork-methodology` (CC-BY-SA-4.0, intentionally code-free;
   ADR-0003 there).
2. **Tooling** — `metawork-claude-plugin`, which carries a glossary
   (`CONTEXT.md`) and a JSON Schema (`lib/schema/metawork-group.schema.yaml`).
3. **Practice** — Meta Work Groups in users' OmniFocus databases and markdown
   directories.

None of these is machine-checkable against the others. The glossary is prose;
the JSON Schema can enforce enum membership but cannot say *which scheme* a
value belongs to, that a parent must be a group, or where a term's definition
came from. Two consumers need that: (a) the plugin's skills and any MCP server,
which should validate what they read and write rather than trust it; and
(b) anyone outside Integral Productivity who wants to inspect, test, or build
on the methodology.

Three questions had to be settled.

**Where does the ontology live?** Options: inside `metawork-methodology`
(violates its code-free rule and couples a CI pipeline to a prose repo);
inside the plugin (couples the public vocabulary to one tool's release
cadence, and the vocabulary is meant to outlive any one tool); or a third
repo that both consume.

**How formal?** The W3C stack offers SKOS (concepts, labels, definitions,
broader/narrower/related, provenance), RDFS/OWL (classes, properties,
inference), and SHACL (constraints on instance data). Full OWL would let a
reasoner infer things; it also makes every term harder to read and invites
modeling for its own sake — the escapist meta-work the methodology warns
against.

**What is the test of done?** Without a test, an ontology grows until its
author tires. Grüninger & Fox (1995) answer this with *competency questions*:
the questions the ontology must be able to answer, written before modeling.

## Decision

1. **Sibling repo.** `Integral-Productivity/metawork-ontology` holds the
   ontology, shapes, competency questions, and tests. `metawork-methodology`
   stays prose; the plugin consumes the ontology (initially by copying the
   JSON Schema here as a fixture and asserting it matches — CQ-15 — and later
   by importing the vocabulary directly).

2. **SKOS first; RDFS/OWL only for what instance data needs; SHACL for
   constraints.** Every term is a `skos:Concept` with `prefLabel`,
   `definition`, and `dcterms:source`. Each scope axis is its own
   `skos:ConceptScheme`. The only OWL is one class (`mw:MetaWorkGroup`) and
   its properties, so that a Meta Work Group can be an RDF node and SHACL can
   validate it. No reasoner is assumed (`inference="none"`).

3. **Competency questions are the acceptance tests.** Written as Gherkin in
   `competency-questions/*.feature`, each tagged `@CQ-nn`, each with an
   executable counterpart in `tests/`. A scenario with no test fails the
   build (`test_every_cq_has_a_test`). SHACL shapes are the fitness functions
   for instance data; `examples/invalid-groups.ttl` pins the expected
   violations so a loosened shape is caught.

4. **Licensing follows the methodology.** Ontology and shapes: CC-BY-SA-4.0,
   matching `metawork-methodology`. Code under `tools/` and `tests/`: MIT.

## Consequences

**Positive**

- The plugin's vocabulary and the public vocabulary cannot drift silently
  (CQ-15 runs in CI).
- A newcomer can read `metawork.ttl` top to bottom; SKOS reads like a
  glossary with links.
- Adding a term requires a definition and a source, which is the discipline
  the methodology's "distinctions to keep sharp" section asks for.
- The same pattern (SKOS + SHACL + CQs + ADRs) can be reused for Holacracy,
  TPD, or a Kaizen-Kata ↔ Panarchy mapping without re-deciding anything.

**Negative**

- Three repos to keep coherent. A renamed axis is a coordinated change
  across the plugin schema, this ontology, and the methodology prose.
- No inference means some questions (transitive nesting cycles, pillar
  interactions) need SPARQL constraints written by hand.
- RDF tooling is unfamiliar to most practitioners; the `.feature` files and
  `README` carry the explanation burden.

**Trigger to revisit**

- A competency question that cannot be answered without OWL reasoning
  (e.g., "which groups are transitively under X at altitude Y?") → introduce
  an inference layer in a new ADR.
- The plugin wants to read the vocabulary at runtime rather than compare a
  fixture → publish the ontology as a versioned artifact (npm or a static
  URL under `ontology.integralproductivity.com`).
- A second ontology (Holacracy, TPD) is started → extract the shared
  tooling into a template repo.
