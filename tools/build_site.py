"""Render the Meta Work ontology to a static site for GitHub Pages.

The site is a project site (integral-productivity.github.io/metawork-ontology/)
with no custom domain. Files sit under the `metawork/` prefix registered in
Integral-Productivity/ontology-hub, whose Worker serves them at
ontology.integralproductivity.com. The hub, not this repo, owns the domain and
the root landing page.

Output layout (so that every minted IRI resolves):

  site/
  ├── index.html                    project-site root: link to metawork/ (not served on the domain)
  ├── metawork.ttl                  the machine-readable file
  ├── metawork/index.html           schema + all schemes, with #anchors for mw: terms
  └── metawork/vocab/<slug>/index.html   one page per SKOS concept / scheme

IRI → file mapping:
  https://ontology.integralproductivity.com/metawork#X        → /metawork/#X
  https://ontology.integralproductivity.com/metawork/vocab/Y  → /metawork/vocab/Y/
  https://ontology.integralproductivity.com/metawork.ttl      → /metawork.ttl

Usage: python tools/build_site.py [out_dir]
"""
from __future__ import annotations

import html
import shutil
import sys
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, PROV

ROOT = Path(__file__).resolve().parent.parent
TTL = ROOT / "ontology" / "metawork.ttl"
BASE = "https://ontology.integralproductivity.com"
MW = BASE + "/metawork#"
MWV = BASE + "/metawork/vocab/"
HOST = "ontology.integralproductivity.com"
REPO = "https://github.com/Integral-Productivity/metawork-ontology"

CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--muted:#5a5a5a;--line:#e3e3e3;--accent:#2a5d8f;--code:#f4f4f4}
@media(prefers-color-scheme:dark){:root{--bg:#121212;--fg:#e8e8e8;--muted:#a0a0a0;--line:#2c2c2c;--accent:#7fb3e6;--code:#1e1e1e}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:860px;margin:0 auto;padding:32px 16px 64px}a{color:var(--accent)}
h1{font-size:1.7rem;margin:.2em 0}h2{font-size:1.25rem;margin-top:2em;border-bottom:1px solid var(--line);padding-bottom:.25em}
h3{font-size:1.05rem;margin-top:1.6em}code{background:var(--code);padding:.1em .35em;border-radius:4px;font-size:.92em}
dl{display:grid;grid-template-columns:max-content 1fr;gap:.3em 1.2em}dt{color:var(--muted)}dd{margin:0}
.crumbs{color:var(--muted);font-size:.9em}.muted{color:var(--muted)}table{border-collapse:collapse;width:100%}
td,th{text-align:left;padding:.35em .5em;border-bottom:1px solid var(--line);vertical-align:top}
.term{scroll-margin-top:1em}footer{margin-top:3em;color:var(--muted);font-size:.85em;border-top:1px solid var(--line);padding-top:1em}
"""


def page(title: str, body: str, crumbs: str = "") -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<link rel="alternate" type="text/turtle" href="/metawork.ttl"><style>{CSS}</style></head>
<body><main><div class="crumbs">{crumbs}</div>{body}
<footer>Integral Productivity · <a href="{REPO}">source and issues</a> · content CC-BY-SA-4.0 ·
machine-readable: <a href="/metawork.ttl">metawork.ttl</a></footer></main></body></html>"""


def slug(iri: URIRef) -> str:
    return str(iri).replace(MWV, "")


def href(iri: URIRef) -> str:
    s = str(iri)
    if s.startswith(MWV):
        return f"/metawork/vocab/{s[len(MWV):]}/"
    if s.startswith(MW):
        return f"/metawork/#{s[len(MW):]}"
    return s


def lit(g: Graph, s: URIRef, p: URIRef) -> str:
    v = g.value(s, p)
    return str(v) if v is not None else ""


def link(g: Graph, iri: URIRef) -> str:
    label = lit(g, iri, SKOS.prefLabel) or lit(g, iri, RDFS.label) or slug(iri)
    return f'<a href="{href(iri)}">{html.escape(label)}</a>'


def concept_page(g: Graph, c: URIRef) -> str:
    label = lit(g, c, SKOS.prefLabel) or slug(c)
    rows = []

    def row(k, v):
        if v:
            rows.append(f"<dt>{k}</dt><dd>{v}</dd>")

    row("IRI", f"<code>{html.escape(str(c))}</code>")
    row("Definition", html.escape(lit(g, c, SKOS.definition)))
    row("Notation", " ".join(f"<code>{html.escape(str(n))}</code>" for n in g.objects(c, SKOS.notation)))
    row("Also called", ", ".join(html.escape(str(a)) for a in g.objects(c, SKOS.altLabel)))
    row("Scope note", html.escape(lit(g, c, SKOS.scopeNote)))
    row("Example", html.escape(lit(g, c, SKOS.example)))
    row("In scheme", ", ".join(link(g, s) for s in g.objects(c, SKOS.inScheme)))
    row("Broader", ", ".join(link(g, s) for s in g.objects(c, SKOS.broader)))
    row("Narrower", ", ".join(link(g, s) for s in g.objects(c, SKOS.narrower)))
    row("Related", ", ".join(link(g, s) for s in g.objects(c, SKOS.related)))
    members = sorted(g.subjects(SKOS.inScheme, c), key=lambda x: str(x))
    if members:
        row("Concepts in this scheme", "<br>".join(link(g, m) for m in members))
    row("Source", html.escape(lit(g, c, DCTERMS.source)))
    kinds = ", ".join(str(t).split("#")[-1] for t in g.objects(c, RDF.type))
    body = f'<h1>{html.escape(label)}</h1><p class="muted">{kinds} · Meta Work ontology</p><dl>{"".join(rows)}</dl>'
    return page(f"{label} — Meta Work ontology", body, '<a href="/">ontologies</a> › <a href="/metawork/">Meta Work</a> › vocab')


def ontology_page(g: Graph) -> str:
    onto = URIRef(BASE + "/metawork")
    title = lit(g, onto, DCTERMS.title) or "Meta Work ontology"
    desc = lit(g, onto, DCTERMS.description)
    version = lit(g, onto, OWL.versionInfo)
    derived = "".join(f'<li><a href="{d}">{html.escape(str(d))}</a></li>' for d in g.objects(onto, PROV.wasDerivedFrom))

    # schema terms (mw:)
    classes = sorted(c for c in g.subjects(RDF.type, OWL.Class) if str(c).startswith(MW))
    props = sorted({p for t in (OWL.ObjectProperty, OWL.DatatypeProperty) for p in g.subjects(RDF.type, t) if str(p).startswith(MW)})
    schema = ""
    for c in classes:
        schema += f'<h3 class="term" id="{slug(c).replace(MW, "")}"><code>mw:{str(c)[len(MW):]}</code> — {html.escape(lit(g, c, RDFS.label))}</h3><p>{html.escape(lit(g, c, RDFS.comment))}</p>'
    schema += "<table><tr><th>Property</th><th>Range</th><th>Vocabulary</th></tr>"
    for p in props:
        rng = g.value(p, RDFS.range)
        see = g.value(p, RDFS.seeAlso)
        schema += (f'<tr id="{str(p)[len(MW):]}" class="term"><td><code>mw:{str(p)[len(MW):]}</code><br><span class="muted">{html.escape(lit(g, p, RDFS.label))}</span></td>'
                   f'<td><code>{html.escape(str(rng).split("#")[-1].split("/")[-1]) if rng else ""}</code></td>'
                   f'<td>{link(g, see) if see else ""}</td></tr>')
    schema += "</table>"

    # schemes
    schemes = ""
    core = URIRef(MWV + "core")
    for scheme in [core] + sorted((s for s in g.subjects(RDF.type, SKOS.ConceptScheme) if s != core), key=lambda x: str(x)):
        members = sorted(g.subjects(SKOS.inScheme, scheme), key=lambda x: str(x))
        schemes += f'<h3>{link(g, scheme)} <span class="muted">({len(members)} concepts)</span></h3><p>{html.escape(lit(g, scheme, SKOS.definition))}</p><ul>'
        for m in members:
            d = lit(g, m, SKOS.definition)
            schemes += f"<li>{link(g, m)}" + (f' <span class="muted">— {html.escape(d[:140])}{"…" if len(d) > 140 else ""}</span>' if d else "") + "</li>"
        schemes += "</ul>"

    body = f"""<h1>{html.escape(title)}</h1><p class="muted">version {html.escape(version)} · namespace <code>{MW}</code> · vocabulary <code>{MWV}</code></p>
<p>{html.escape(desc)}</p>
<p>Download: <a href="/metawork.ttl">metawork.ttl</a> (Turtle). Conformance shapes, competency questions, and tests: <a href="{REPO}">{REPO.replace("https://", "")}</a>.</p>
<h2>How to read this</h2>
<p>The <b>vocabulary</b> is SKOS: every term has a definition, a source, and links to broader, narrower, and related terms. Each enumeration (Horizons of Focus, System Strata, …) is its own concept scheme. The <b>schema</b> is one OWL class, <code>mw:MetaWorkGroup</code>, and its properties, so that a Meta Work Group can be validated against the SHACL shapes in the repository.</p>
<h2>Schema (<code>mw:</code>)</h2>{schema}
<h2>Vocabulary (<code>mwv:</code>)</h2>{schemes}
<h2>Provenance</h2><p>Derived from:</p><ul>{derived}</ul>"""
    return page(title, body, '<a href="/">ontologies</a> › Meta Work')


def root_page() -> str:
    # Only reachable at the project-site URL; on the domain, "/" belongs to ontology-hub.
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Meta Work ontology</title>
<meta http-equiv="refresh" content="0; url=https://{HOST}/metawork/"><link rel="canonical" href="https://{HOST}/metawork/"></head>
<body><p>The Meta Work ontology is published at <a href="https://{HOST}/metawork/">https://{HOST}/metawork/</a>.</p></body></html>"""


def build(out: Path) -> int:
    g = Graph().parse(TTL, format="turtle")
    if out.exists():
        shutil.rmtree(out)
    (out / "metawork" / "vocab").mkdir(parents=True)
    (out / ".nojekyll").write_text("")
    (out / "index.html").write_text(root_page(), encoding="utf-8")
    shutil.copy(TTL, out / "metawork.ttl")
    (out / "metawork" / "index.html").write_text(ontology_page(g), encoding="utf-8")
    n = 0
    for c in set(g.subjects(RDF.type, SKOS.Concept)) | set(g.subjects(RDF.type, SKOS.ConceptScheme)):
        if not str(c).startswith(MWV):
            continue
        d = out / "metawork" / "vocab" / slug(c)
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(concept_page(g, c), encoding="utf-8")
        n += 1
    return n


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "site"
    n = build(out)
    print(f"built {out}: {n} vocabulary pages + ontology page + index")
