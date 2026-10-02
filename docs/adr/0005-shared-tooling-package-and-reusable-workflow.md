# 5. Share the ontology tooling as a package and a reusable workflow; the scaffold skill owns the layout

Date: 2026-10-02

## Status

Accepted

Supersedes the third "trigger to revisit" of [ADR-0002](0002-separate-repo-skos-first.md)
("a second ontology is started → extract the shared tooling into a template
repo"). The trigger fired; this ADR answers it with a different mechanism.
ADR-0002 itself is not edited.

Issue: [#10](https://github.com/Integral-Productivity/metawork-ontology/issues/10).

## Context

`vertical-development-ontology` (VDO) started on 2026-10-02 (ADR-0003
Amendment 1). On the same day its issue #3 was done by copying this repo's
`tools/build_site.py` and the "every minted IRI maps to a file" step of
`pages.yml`. By the time this ADR was written the two copies had already
diverged:

| Part | metawork-ontology | vertical-development-ontology |
|---|---|---|
| `tools/build_site.py` | 189 lines; base IRI, prefix and Turtle path hard-coded | 408 lines; a `Site` class reads the base IRI, prefix and version from the one `owl:Ontology` in the file |
| Concept and ontology renderers | SKOS concepts and schemes | SKOS-XL labels, cited sources, tier placements |
| Dated snapshot `/<prefix>/v/<version>/` (ADR-0004 decision 3) | **not built** | built for the current version only; earlier versions are lost on the next deploy (VDO#6, open) |
| Page frame and CSS | same | same |
| IRI-to-file check | inline Python in `pages.yml` | the same, copied, prefix changed |
| Hub rules: Turtle at `/<name>.ttl`, no `site/CNAME`, `.nojekyll` ([ontology-hub ADR-0002](https://github.com/Integral-Productivity/ontology-hub/blob/main/docs/adr/0002-turtle-at-root-and-unlisted-entries.md)) | implemented | implemented again |
| No deploy while the repository is private (VDO ADR-0006) | n/a (public) | in `pages.yml` |
| Site tests | none | `tests/test_site.py` |

Two observations decide the question:

1. **The parts that must not drift are code, and they are already drifting.**
   The snapshot rule of ADR-0004 is missing here and half-built in VDO. A fix
   to it (VDO#6) would have to be made again in every copy. The Holacracy and
   TPD prefixes are reserved in the hub registry; they would be the third and
   fourth copies.
2. **The layout already has a source.** The `ontology-scaffold` skill describes
   the repository layout step by step: competency-question files, ADRs
   0001–0004, `LICENSE.md` (content CC-BY-SA-4.0, code MIT), README sections,
   `tools/` and `tests/`. It does not mention the site or Pages. A template
   repository would be a second source for the same layout.

Options compared (from #10):

| Option | Fixes reach existing repos | Sources for the layout | Fit |
|---|---|---|---|
| 1. Template repository | no (one copy at creation) | two (template and skill) | Poor: the drift above is in code a template copies once |
| 2. Package plus reusable workflow | yes, on a version bump | one (skill) | **Chosen** |
| 3. Template for layout plus package for code | yes, for the code | two (template and skill) | The package half fits; the template half duplicates the skill |
| 4. Keep copies plus a drift test | no | one (skill) | Poor: the renderers differ by design, so the test could compare only fragments |

## Decision

1. **A new public repository, `Integral-Productivity/ontology-tooling`
   (MIT), holds the shared code.** It is a Python package
   (`ontology_tooling`), installed from a git tag
   (`ontology-tooling @ git+https://github.com/Integral-Productivity/ontology-tooling@vX.Y.Z`
   in `requirements.txt`). It starts from VDO's `Site` class, which already
   reads the base IRI, prefix and version from the ontology file. It owns:
   - the page frame and CSS;
   - the IRI-to-site-path mapping;
   - the hub rules: the Turtle file at `/<name>.ttl` at the root, no
     `site/CNAME`, a `.nojekyll` file. The rules are enforced in this one
     place, and the build fails if they are broken;
   - the dated snapshots of ADR-0004 decision 3, including the rule that a
     released version's snapshot is never removed or overwritten (the VDO#6
     behavior);
   - the IRI-to-file check, as a function and a CLI command, not as inline
     Python in each workflow;
   - `load()` and `validate()` (pyshacl, ontology merged into the data graph,
     `inference="none"`).

2. **Renderers: a default plus hooks.** The package ships a default renderer
   for SKOS concepts, concept schemes and the ontology page. A repository
   overrides it for what is specific to its model (VDO: SKOS-XL labels,
   sources, tier placements). Domain functions (`frontmatter_to_rdf` here;
   the label lookups in VDO) stay in each repository.

3. **A reusable workflow (`workflow_call`) builds, checks and deploys the
   site.** It runs the build and the IRI-to-file check on pull requests and on
   `main`, and deploys only from `main`. It skips the deploy while the calling
   repository is private (VDO ADR-0006, generalized). A validate workflow is
   offered the same way, with the list of example files as an input. Each
   repository pins the same tag in `requirements.txt` and in `uses:`, and bumps
   both together.

4. **No template repository. The `ontology-scaffold` skill stays the only
   source for the layout**: the files each repository edits (README, ADRs,
   competency questions, shapes, `LICENSE.md`). Its tooling step changes to:
   depend on `ontology-tooling`, call the reusable workflow, and supply
   renderer hooks only where the model needs them (#12).

5. **The package stays in Python.** rdflib and pyshacl are what both
   repositories use today. Both repositories' shapes use SHACL-SPARQL
   constraints (`sh:sparql`), which pyshacl runs; the common TypeScript
   validator (`rdf-validate-shacl`) covers SHACL Core only. The org technology radar places Python on
   Hold, "reserved for ML-specific tooling only"; this ADR asks for an
   exception for RDF tooling in the radar rather than leaving the use
   unrecorded
   ([software-architecture-excellence#101](https://github.com/Integral-Productivity/software-architecture-excellence/issues/101)).

6. **Migration order.** This repository migrates first, in #10. That also
   gives it the dated snapshots it lacks today. The live checks of ontology-hub
   `smoke.yml` must still pass afterwards. VDO migrates after VDO#6 is merged,
   so the snapshot fix is ported into the package once rather than changed
   twice in flight
   ([vertical-development-ontology#9](https://github.com/Integral-Productivity/vertical-development-ontology/issues/9),
   blocked by VDO#6 and by #10).

## Consequences

**Positive**

- A fix to the frame, the hub rules, the snapshots or the IRI-to-file check
  reaches every ontology on a version bump.
- A third ontology writes only its domain code and, if needed, renderer
  hooks.
- One source for the layout (the skill), one source for the shared code (the
  package).

**Negative**

- One more repository to version, and two pins (`requirements.txt` and
  `uses:`) per ontology that must move together.
- A change to the shared code needs a release before an ontology can use it.
  Work that touches both is two pull requests.
- The renderer hook interface is a public API between repositories. Changing
  it is a breaking release.
- Python is used further while the radar still lists it on Hold, until the
  exception is recorded.

**Trigger to revisit**

- An ontology whose pages cannot be expressed through the renderer hooks →
  widen the API, or let that repository own its renderers, in a new ADR.
- The radar exception for Python RDF tooling is refused → choose the language
  again before a third ontology uses the package.
- Pin bumps fall behind (an ontology more than one minor version behind for a
  month) → automate the bump.
