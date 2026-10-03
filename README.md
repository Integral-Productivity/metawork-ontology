# metawork-ontology

> **Status:** v0.1.0 — vocabulary and conformance shapes for the Meta Work
> methodology. First consumer: `metawork-claude-plugin` (see ADR-0003).
>
> **Published at <https://ontology.integralproductivity.com/metawork/>** — every
> IRI in the ontology resolves to a page there; `metawork.ttl` is served alongside.
> This repo publishes a GitHub Pages project site; the domain, path registry and
> router live in [`ontology-hub`](https://github.com/Integral-Productivity/ontology-hub).

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
├── metawork-group.shacl.ttl    # SHACL shapes = fitness functions for instance data
└── scope-axis-mismatch.shacl.ttl  # metawork-diagnose pattern as a shape (sh:Warning)
competency-questions/       # Gherkin: the questions the ontology must answer
examples/                   # valid-/invalid-groups.ttl, valid-/invalid-decisions.ttl (pinned results)
fixtures/                   # copy of the plugin's JSON Schema, asserted in sync (CQ-15)
tools/metawork_ontology.py  # load / lift markdown frontmatter to RDF / validate
tools/site_hooks.py         # this repo's page hooks for ontology-tooling's site builder (ADR-0005)
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
python -m pytest -q                                              # 28 checks
python tools/metawork_ontology.py validate examples/valid-groups.ttl
python tools/metawork_ontology.py validate examples/invalid-groups.ttl   # 3 violations, by design
python tools/metawork_ontology.py lift "~/MetaWork/Vocational/Praxis/Overview.md"   # markdown backend → RDF → validate
python tools/metawork_ontology.py validate examples/valid-groups.ttl examples/invalid-decisions.ttl  # 2 mismatch warnings + 1 violation
python tools/metawork_ontology.py validate group.md --at 20000ft-areas-focus-responsibility   # scope-axis mismatch check
ontology-tooling build --out site --site-class site_hooks:MetaworkSite && ontology-tooling check-iris --site site
```

The site builder, the IRI-to-file check, the hub rules and the dated snapshots
(`/metawork/v/<version>/`) come from
[ontology-tooling](https://github.com/Integral-Productivity/ontology-tooling), pinned
in `requirements.txt` and in both workflows' `uses:` lines (ADR-0005). Bump the three
pins together.

## Scope-axis mismatch (diagnostic shape)

`shapes/scope-axis-mismatch.shacl.ttl` expresses the `metawork-diagnose`
pattern *scope-axis mismatch*: a group scoped at one `horizons_of_focus` is
being used to make decisions at another. A group's frontmatter records its
scope, not its use, so the check needs one more input: an `mw:Decision`.

Input contract, as triples (the ontology must be loaded alongside, which
`validate` does):

```turtle
<decision>  a mw:Decision ;
    mw:inGroup          <group> ;            # exactly one; must be an mw:MetaWorkGroup
    mw:decisionAltitude mwv:hof-20000ft ;    # exactly one Horizons of Focus concept
    mw:statement        "optional free text" .
<group>     mw:horizonsOfFocus mwv:hof-10000ft .   # from the group itself
```

From the markdown backend there is no new frontmatter field: `lift` the
group file as before and pass the decision altitude on the command line as
a `horizons_of_focus` notation (`--at`, plus optional `--statement`). In
Python, `decision_to_rdf(group_iri(path), notation, ont)` builds the same
triples.

A mismatch is reported as `sh:Warning`, not `sh:Violation`: neither the
group nor the decision is malformed, and one deliberate zoom-out is not a
breakdown. A malformed decision (no altitude, unknown notation, no group)
is a `sh:Violation`. `validate` exits 1 for either; read the severity
(`Severity: sh:Warning` in the text report, or `mo.findings()`) to tell
them apart.

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
