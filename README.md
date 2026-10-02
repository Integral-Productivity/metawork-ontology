# metawork-ontology

> **Status:** v0.1.0 — vocabulary and conformance shapes for the Meta Work
> methodology. First consumer: `metawork-claude-plugin` (see ADR-0003).

A formal, inspectable, testable vocabulary for **Meta Work** — the intentional
practice of planning, monitoring, and maintaining perspective, instantiated
per `(scope, subject)` as a *Meta Work Group*.

The methodology's prose lives in
[`metawork-methodology`](https://github.com/Integral-Productivity/metawork-methodology).
The tooling lives in
[`metawork-claude-plugin`](https://github.com/Integral-Productivity/metawork-claude-plugin).
This repo is the contract between them.

## What's here

```
ontology/
├── metawork.ttl            # SKOS vocabulary + minimal RDFS/OWL schema
└── context.jsonld          # JSON-LD context for the plugin's YAML keys
shapes/
└── metawork-group.shacl.ttl  # SHACL shapes = fitness functions for instance data
competency-questions/       # Gherkin: the questions the ontology must answer
examples/                   # valid-groups.ttl (conforms) / invalid-groups.ttl (3 pinned violations)
fixtures/                   # copy of the plugin's JSON Schema, asserted in sync (CQ-15)
tools/metawork_ontology.py  # load / lift markdown frontmatter to RDF / validate
tests/                      # one test per @CQ-nn, plus shape guards
docs/adr/                   # modeling decisions
```

## The three layers, in one paragraph each

**SKOS** (`skos:Concept`, `skos:ConceptScheme`) is a glossary with links.
Each term has a preferred label, a definition, a `dcterms:source`, and
`broader` / `narrower` / `related` links to other terms. Each scope axis
(Horizons of Focus, System Strata, Vertical Development Stage) is its own
scheme, so a tool can ask "is `complex` a Horizons value?" and get *no*.

**RDFS/OWL** declares the one class that instance data needs —
`mw:MetaWorkGroup` — and its properties (`mw:subject`, `mw:horizonsOfFocus`,
`mw:parent`, …). That is deliberately all. No reasoner is assumed.

**SHACL** says what a *conforming* Meta Work Group looks like: three required
axes, each a concept in the right scheme; optional classifiers; a parent
that is itself a group and not the group itself. Run it and you get a report
naming the group, the property, and the rule it broke.

**Competency questions** are the acceptance tests for all three. See
[`competency-questions/README.md`](competency-questions/README.md).

## Try it

```bash
pip install -r requirements.txt
python -m pytest -q                                              # 19 checks
python tools/metawork_ontology.py validate examples/valid-groups.ttl
python tools/metawork_ontology.py validate examples/invalid-groups.ttl   # 3 violations, by design
python tools/metawork_ontology.py lift "~/MetaWork/Vocational/Praxis/Overview.md"   # markdown backend → RDF → validate
```

## Contributing a concern

Open an issue titled `concern: <term> — <what is wrong>`. Say which of these
it is, because they are fixed differently:

- **Definition is wrong** → PR against `ontology/metawork.ttl` plus the
  methodology prose, citing a source.
- **A distinction is missing** → add a competency question first, then the
  term that makes it pass.
- **A constraint is too tight / too loose** → add a case to
  `examples/invalid-groups.ttl` (or `valid-groups.ttl`), then change the shape.
- **A modeling choice is wrong** → argue against the specific ADR in
  `docs/adr/`.

## License

Ontology content CC-BY-SA-4.0; code MIT. See [`LICENSE.md`](LICENSE.md).
