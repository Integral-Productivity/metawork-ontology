"""SHACL shapes as fitness functions (CQ-10, CQ-11, CQ-12)."""
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import SH

import metawork_ontology as mo

EX = Namespace("https://example.integralproductivity.com/groups/")


def _report(root, ont, shapes, name):
    data = Graph().parse(root / "examples" / name, format="turtle")
    conforms, report, _ = mo.validate(data, ont, shapes)
    # Top-level results only; nested sh:detail results (focus = the bad value)
    # are explanatory and would double-count the group-level violation.
    results = [
        (r, report.value(r, SH.focusNode), report.value(r, SH.resultPath), str(report.value(r, SH.resultMessage)))
        for r in report.objects(None, SH.result)
    ]
    return conforms, results


def test_cq10_valid_examples_conform_and_nest(root, ont, shapes):
    """CQ-10: valid examples conform; the project-level group nests under the area-level one."""
    conforms, results = _report(root, ont, shapes, "valid-groups.ttl")
    assert conforms, results
    data = Graph().parse(root / "examples" / "valid-groups.ttl", format="turtle")
    assert (EX["metawork-ontology"], mo.MW.parent, EX["overview-vertical-development"]) in data


def test_cq10_self_parent_is_rejected(root, ont, shapes):
    """CQ-10: a group may not be its own parent."""
    _, results = _report(root, ont, shapes, "invalid-groups.ttl")
    assert any(fn == EX["bad-self-parent"] and "own parent" in msg for _, fn, _, msg in results)


def test_cq11_missing_axis_is_rejected(root, ont, shapes):
    """CQ-11: all three first-class axes are required."""
    _, results = _report(root, ont, shapes, "invalid-groups.ttl")
    assert any(fn == EX["bad-missing-axis"] and path == mo.MW.systemStrata for _, fn, path, _ in results)


def test_cq12_wrong_scheme_is_rejected(root, ont, shapes):
    """CQ-12: an axis rejects a value from another scheme."""
    _, results = _report(root, ont, shapes, "invalid-groups.ttl")
    assert any(fn == EX["bad-wrong-scheme"] and path == mo.MW.horizonsOfFocus for _, fn, path, _ in results)


def test_invalid_examples_break_exactly_one_rule_each(root, ont, shapes):
    """Guard: if a shape is loosened, the violation count drops and this fails."""
    conforms, results = _report(root, ont, shapes, "invalid-groups.ttl")
    assert not conforms
    focus_nodes = {fn for _, fn, _, _ in results}
    assert focus_nodes == {EX["bad-missing-axis"], EX["bad-wrong-scheme"], EX["bad-self-parent"]}


def test_lift_markdown_frontmatter(root, ont, shapes, tmp_path):
    """The bridge to the plugin: a markdown-backend file lifts to RDF and validates."""
    md = tmp_path / "Overview (Sleep).md"
    md.write_text(
        "---\n"
        "subject: Sleep\n"
        "life_domain: Wellness/Sleep\n"
        "horizons_of_focus: 20000ft-areas-focus-responsibility\n"
        "system_strata: 1-2yr\n"
        "vertical_development_stage: self-determining\n"
        "cynefin_domain: complicated\n"
        "perspective_checks: [reality, goals_and_objectives]\n"
        "---\n# Overview (Sleep)\n"
    )
    data = mo.frontmatter_to_rdf(md, ont)
    conforms, _, text = mo.validate(data, ont, shapes)
    assert conforms, text

    md.write_text(md.read_text().replace("system_strata: 1-2yr", "system_strata: someday"))
    data = mo.frontmatter_to_rdf(md, ont)
    conforms, _, _ = mo.validate(data, ont, shapes)
    assert not conforms, "an unknown enum value must fail validation"
