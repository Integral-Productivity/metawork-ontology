"""The site builds with this repository's hooks, and every minted IRI resolves.

The pages workflow runs the same build and check (ontology-tooling, ADR-0005).
This test catches a hook that breaks the build before a pull request reaches it.
``releases={}`` keeps the test independent of the git tags in the checkout.
"""
import pytest
from rdflib import Graph

from ontology_tooling import build, hub_rule_violations, missing_iris

import metawork_ontology as mo
import site_hooks


@pytest.fixture(scope="module")
def site_dir(tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    site = build(out, mo.ONTOLOGY, site_hooks.MetaworkSite, releases={})
    return out, site


def test_every_minted_iri_resolves(site_dir):
    out, _ = site_dir
    g = Graph().parse(mo.ONTOLOGY, format="turtle")
    assert missing_iris(g, out) == []


def test_hub_rules_hold(site_dir):
    out, site = site_dir
    assert site.name == "metawork"
    assert hub_rule_violations(out, site.name) == []


def test_untagged_current_version_has_no_snapshot(site_dir):
    """ontology-tooling v0.2.0: only a tagged version gets /metawork/v/<version>/."""
    out, _ = site_dir
    assert not (out / "metawork" / "v").exists()


def test_released_version_gets_a_snapshot(tmp_path):
    data = mo.ONTOLOGY.read_bytes()
    version = site_hooks.MetaworkSite(Graph().parse(data=data, format="turtle")).version
    site = build(tmp_path, mo.ONTOLOGY, site_hooks.MetaworkSite, releases={version: data})
    snap = tmp_path / "metawork" / "v" / site.version
    assert (snap / "metawork.ttl").read_bytes() == data
    assert f'<a href="/metawork/v/{site.version}/">' in (tmp_path / "metawork" / "index.html").read_text(encoding="utf-8")


def test_repository_specific_content(site_dir):
    out, _ = site_dir
    page = (out / "metawork" / "index.html").read_text(encoding="utf-8")
    assert "How to read this" in page
    assert "Provenance" in page
    assert "github.com/Integral-Productivity/metawork-ontology" in page
    assert page.count('<a href="/">ontologies</a>') == 1
    concept = next((out / "metawork" / "vocab").rglob("index.html")).read_text(encoding="utf-8")
    assert '<a href="/">ontologies</a> › <a href="/metawork/">' in concept
    assert "source and issues" in concept
