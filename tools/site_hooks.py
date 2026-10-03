"""Renderer hooks for the Meta Work ontology's site (ADR-0005, decision 2).

The page frame, addressing, hub rules, snapshots and default SKOS renderers come
from ontology-tooling. This module adds only what is specific to this repository:

- a link to the source repository in every footer (``footer_extra``);
- the "How to read this" and Provenance sections on the ontology page
  (``ontology_sections``);
- a leading "ontologies" breadcrumb back to the hub's landing page at "/".

Built by the reusable pages workflow with ``site-class: site_hooks:MetaworkSite``,
or locally: ``ontology-tooling build --out site --site-class site_hooks:MetaworkSite``.
"""
from __future__ import annotations

from html import escape as e

from rdflib.namespace import PROV

from ontology_tooling import Site

REPO = "https://github.com/Integral-Productivity/metawork-ontology"


class MetaworkSite(Site):
    def footer_extra(self) -> str:
        return f' · <a href="{REPO}">source and issues</a>'

    def page(self, title: str, body: str, crumbs: str) -> str:
        # The hub owns "/" on the domain. The ontology page builds its crumbs
        # without crumbs(), so the leading link is added here, once, for every page.
        return super().page(title, body, f'<a href="/">ontologies</a> › {crumbs}')

    def ontology_sections(self) -> str:
        derived = "".join(
            f"<li>{self.link(d, str(d))}</li>" for d in sorted(self.g.objects(self.onto, PROV.wasDerivedFrom))
        )
        return f"""
<p>Conformance shapes, competency questions, and tests: <a href="{REPO}">{e(REPO.replace("https://", ""))}</a>.</p>
<h2>How to read this</h2>
<p>The <b>vocabulary</b> is SKOS: every term has a definition, a source, and links to broader, narrower, and
related terms. Each enumeration (Horizons of Focus, System Strata, …) is its own concept scheme. The
<b>schema</b> is the OWL classes <code>mw:MetaWorkGroup</code> and <code>mw:Decision</code> and their
properties, so that Meta Work data can be validated against the SHACL shapes in the repository.</p>
<h2>Provenance</h2><p>Derived from:</p><ul>{derived}</ul>"""
