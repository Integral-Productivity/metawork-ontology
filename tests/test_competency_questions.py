"""Executable competency questions.

Each test carries the @CQ-nn id from competency-questions/*.feature. The
docstring quotes the scenario so a failure reads as a modeling bug, not a
code bug. test_every_cq_has_a_test enforces that no scenario is orphaned.
"""
import re
from pathlib import Path

import yaml
from rdflib import Literal, URIRef
from rdflib.namespace import DCTERMS, SKOS

import metawork_ontology as mo

MWV = mo.MWV


def by_label(ont, label):
    hits = list(ont.subjects(SKOS.prefLabel, Literal(label, lang="en")))
    assert len(hits) == 1, f"expected exactly one concept labelled {label!r}, got {hits}"
    return hits[0]


def in_scheme(ont, scheme):
    return set(ont.subjects(SKOS.inScheme, scheme))


# ── distinctions.feature ─────────────────────────────────────────────────

def test_cq01_metawork_vs_metawork(ont):
    """CQ-01: Meta Work and meta-work are distinct, related, and not synonyms."""
    mw = by_label(ont, "Meta Work")
    esc = by_label(ont, "meta-work (escapist)")
    assert mw != esc
    assert (mw, SKOS.related, esc) in ont and (esc, SKOS.related, mw) in ont
    for p in (SKOS.broader, SKOS.narrower):
        assert (mw, p, esc) not in ont and (esc, p, mw) not in ont


def test_cq02_metatask_is_outside(ont):
    """CQ-02: Meta-Task is recorded but is not part of the methodology."""
    mt = by_label(ont, "Meta-Task")
    mw = by_label(ont, "Meta Work")
    assert (mt, SKOS.inScheme, MWV.core) in ont
    assert (mt, SKOS.broader, mw) not in ont
    assert "Unrelated to Meta Work" in str(ont.value(mt, SKOS.definition))


# ── scope.feature ────────────────────────────────────────────────────────

def test_cq03_first_class_axes(ont):
    """CQ-03: The three first-class axes are narrower than Scope."""
    scope = by_label(ont, "Scope (multi-axial)")
    narrower = set(ont.objects(scope, SKOS.narrower))
    assert {MWV.HorizonsOfFocus, MWV.SystemStrata, MWV.VerticalDevelopmentStage} <= narrower


def test_cq04_optional_classifiers(ont):
    """CQ-04: The two optional classifiers are narrower than Scope."""
    scope = by_label(ont, "Scope (multi-axial)")
    assert {MWV.CynefinDomain, MWV.NeurologicalLevel} <= set(ont.objects(scope, SKOS.narrower))


def test_cq05_horizons_values_and_source(ont):
    """CQ-05: Horizons of Focus has six values with a cited source."""
    assert mo.notations_in_scheme(ont, MWV.HorizonsOfFocus) == {
        "50000ft-purpose-principles", "40000ft-vision", "30000ft-goals-objectives",
        "20000ft-areas-focus-responsibility", "10000ft-projects", "runway",
    }
    assert "David Allen" in str(ont.value(MWV.HorizonsOfFocus, DCTERMS.source))


def test_cq06_vds_eight_values(ont):
    """CQ-06: Vertical Development Stage has eight values, Self-Centric..Unitive."""
    tops = list(ont.objects(MWV.VerticalDevelopmentStage, SKOS.hasTopConcept))
    assert len(tops) == 8
    labels = {str(ont.value(c, SKOS.prefLabel)) for c in tops}
    assert {"Self-Centric", "Unitive"} <= labels


def test_cq07_life_domain_not_an_axis(ont):
    """CQ-07: Life Domain is related to Scope but not narrower than it."""
    ld = by_label(ont, "Life domain")
    scope = by_label(ont, "Scope (multi-axial)")
    assert (ld, SKOS.broader, scope) not in ont and (scope, SKOS.narrower, ld) not in ont
    assert (ld, SKOS.related, scope) in ont


# ── pillars.feature ──────────────────────────────────────────────────────

def test_cq08_eight_pillars_with_provenance(ont):
    """CQ-08: Eight pillars; at least seven cite a source."""
    pillars = in_scheme(ont, MWV.Pillar)
    assert len(pillars) == 8
    sourced = [p for p in pillars if ont.value(p, DCTERMS.source) is not None]
    assert len(sourced) >= 7


def test_cq09_perspective_checks_under_living_forward(ont):
    """CQ-09: Perspective checks belong to the Living Forward pillar and number four."""
    pc = by_label(ont, "Perspective check")
    assert (pc, SKOS.broader, by_label(ont, "Living Forward Life Plan")) in ont
    assert len(in_scheme(ont, MWV.PerspectiveCheck)) == 4


# ── groups.feature → see test_shapes.py (CQ-10..12) ──────────────────────

def test_cq13_backends(ont):
    """CQ-13: Backends are enumerated."""
    b = by_label(ont, "Backend")
    labels = {str(ont.value(c, SKOS.prefLabel)) for c in ont.objects(b, SKOS.narrower)}
    assert labels == {"OmniFocus backend", "Markdown directory backend"}


# ── provenance.feature ───────────────────────────────────────────────────

def test_cq14_ontology_header(ont):
    """CQ-14: The ontology declares derivation sources and a license."""
    from rdflib.namespace import PROV
    o = URIRef("https://ontology.integralproductivity.com/metawork")
    derived = {str(x) for x in ont.objects(o, PROV.wasDerivedFrom)}
    assert any("metawork-claude-plugin" in d and "CONTEXT.md" in d for d in derived)
    assert any("metawork-methodology" in d for d in derived)
    assert ont.value(o, DCTERMS.license) is not None


def test_cq15_plugin_schema_in_sync(ont, root):
    """CQ-15: The plugin's YAML schema enums equal the ontology's notations."""
    schema = yaml.safe_load((root / "fixtures" / "metawork-group.schema.yaml").read_text())
    props = schema["properties"]
    pairs = {
        "horizons_of_focus": MWV.HorizonsOfFocus,
        "system_strata": MWV.SystemStrata,
        "vertical_development_stage": MWV.VerticalDevelopmentStage,
        "cynefin_domain": MWV.CynefinDomain,
        "neurological_level": MWV.NeurologicalLevel,
    }
    for key, scheme in pairs.items():
        enum = {v for v in props[key]["enum"] if v is not None}
        assert enum == mo.notations_in_scheme(ont, scheme), f"{key} drifted"
    pc = set(props["perspective_checks"]["items"]["enum"])
    assert pc == mo.notations_in_scheme(ont, MWV.PerspectiveCheck), "perspective_checks drifted"


# ── meta: every @CQ in the feature files has a test ──────────────────────

def test_every_cq_has_a_test(root):
    feature_ids = set()
    for f in (root / "competency-questions").glob("*.feature"):
        feature_ids |= set(re.findall(r"@(CQ-\d+)", f.read_text()))
    test_ids = set()
    for f in (root / "tests").glob("test_*.py"):
        test_ids |= set(re.findall(r"(CQ-\d+)", f.read_text()))
    missing = feature_ids - test_ids
    assert not missing, f"competency questions without an executable test: {sorted(missing)}"
