"""The workflows call ontology-tooling at one pinned version, and a release tag rebuilds main.

ontology-tooling owns the build, the checks, the deploy gate and the release trigger
(ADR-0005). These checks keep this repository's four pins together and keep the
pieces the release trigger depends on in place (ontology-tooling#12).
"""
import re

import pytest
import yaml

TOOLING = "Integral-Productivity/ontology-tooling/.github/workflows/"


def workflow(root, name):
    doc = yaml.safe_load((root / ".github" / "workflows" / name).read_text(encoding="utf-8"))
    return doc, doc.get(True, doc.get("on"))  # PyYAML reads the key `on` as True


def pinned_tag(root):
    m = re.search(r"^ontology-tooling @ git\+https://github\.com/Integral-Productivity/ontology-tooling@(v\d+\.\d+\.\d+)$",
                  (root / "requirements.txt").read_text(encoding="utf-8"), re.M)
    assert m, "requirements.txt does not pin ontology-tooling at a vX.Y.Z tag"
    return m.group(1)


@pytest.mark.parametrize("name", ["pages.yml", "validate.yml", "release-pages.yml"])
def test_workflow_calls_ontology_tooling_at_the_pinned_version(root, name):
    raw = (root / ".github" / "workflows" / name).read_text(encoding="utf-8")
    uses = re.findall(rf"^    uses: {re.escape(TOOLING)}{re.escape(name)}@([0-9a-f]{{40}}) # (v\S+)$", raw, re.M)
    assert [tag for _, tag in uses] == [pinned_tag(root)], f"{name} is not pinned with requirements.txt"


def test_release_tag_push_starts_pages_on_main(root):
    _, on = workflow(root, "release-pages.yml")
    assert on == {"push": {"tags": ["v*.*.*"]}}
    _, pages_on = workflow(root, "pages.yml")
    assert "workflow_dispatch" in pages_on, "release-pages.yml can start pages.yml only through workflow_dispatch"
