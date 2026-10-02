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


# ── CQ-16: scope-axis mismatch (metawork-diagnose pattern, ADR-0003 item 3) ──

EXD = Namespace("https://example.integralproductivity.com/decisions/")


def _findings(root, ont, shapes, *names):
    data = Graph()
    for n in names:
        data.parse(root / "examples" / n, format="turtle")
    conforms, report, _ = mo.validate(data, ont, shapes)
    return conforms, mo.findings(report)


def test_cq16_matching_altitudes_conform(root, ont, shapes):
    """CQ-16: decisions made at their group's horizons_of_focus conform."""
    conforms, results = _findings(root, ont, shapes, "valid-groups.ttl", "valid-decisions.ttl")
    assert conforms, results


def test_cq16_mismatch_is_a_warning_naming_both_altitudes(root, ont, shapes):
    """CQ-16: a 20,000 ft question in a 10,000 ft group (and vice versa) is a scope-axis mismatch warning."""
    conforms, results = _findings(root, ont, shapes, "valid-groups.ttl", "invalid-decisions.ttl")
    assert not conforms, "a warning must still surface as non-conformance"
    by_focus = {fn: (sev, path, msg) for sev, fn, path, msg in results}

    sev, path, msg = by_focus[EXD["area-question-in-project-group"]]
    assert sev == SH.Warning and path == mo.MW.decisionAltitude
    assert "Scope-axis mismatch" in msg
    assert "'20000ft-areas-focus-responsibility'" in msg and "'10000ft-projects'" in msg

    sev, _, msg = by_focus[EXD["project-question-in-area-group"]]
    assert sev == SH.Warning
    assert msg.index("10000ft-projects") < msg.index("20000ft-areas-focus-responsibility")


def test_cq16_invalid_decisions_pinned(root, ont, shapes):
    """Guard: exactly two mismatch warnings and one malformed-decision violation."""
    _, results = _findings(root, ont, shapes, "valid-groups.ttl", "invalid-decisions.ttl")
    assert sorted((str(fn), str(sev)) for sev, fn, _, _ in results) == sorted([
        (str(EXD["area-question-in-project-group"]), str(SH.Warning)),
        (str(EXD["project-question-in-area-group"]), str(SH.Warning)),
        (str(EXD["no-altitude"]), str(SH.Violation)),
    ])


def test_load_reads_every_shapes_file(shapes):
    """validate must apply the mismatch shape, not only the group shapes."""
    from rdflib import URIRef
    mws = "https://ontology.integralproductivity.com/metawork/shapes#"
    for name in ("MetaWorkGroupShape", "NoSelfParentShape", "DecisionShape", "ScopeAxisMismatchShape"):
        assert (URIRef(mws + name), None, None) in shapes, name


def test_cq16_cli_on_markdown_group(root, tmp_path):
    """The plugin's path: lift a markdown group, state the decision altitude, read the warning."""
    import subprocess
    import sys
    md = tmp_path / "Metawork Ontology.md"
    md.write_text(
        "---\n"
        "subject: Meta Work ontology\n"
        "life_domain: Vocational/Integral Productivity\n"
        "horizons_of_focus: 10000ft-projects\n"
        "system_strata: 1-2yr\n"
        "vertical_development_stage: self-questioning\n"
        "---\n# Meta Work ontology\n"
    )
    tool = str(root / "tools" / "metawork_ontology.py")

    def run(*args):
        return subprocess.run([sys.executable, tool, "validate", str(md), *args], capture_output=True, text=True)

    same = run("--at", "10000ft-projects")
    assert same.returncode == 0, same.stdout

    up = run("--at", "20000ft-areas-focus-responsibility", "--statement", "Is this an area?")
    assert up.returncode == 1
    assert "Severity: sh:Warning" in up.stdout
    assert ("Scope-axis mismatch: this decision is being made at horizons_of_focus "
            "'20000ft-areas-focus-responsibility'") in up.stdout
    assert "<urn:metawork:group:metawork-ontology> is scoped at '10000ft-projects'" in up.stdout

    bad = run("--at", "someday")
    assert bad.returncode == 1 and "Severity: sh:Violation" in bad.stdout
