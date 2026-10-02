import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import metawork_ontology as mo  # noqa: E402


@pytest.fixture(scope="session")
def ont():
    return mo.load()[0]


@pytest.fixture(scope="session")
def shapes():
    return mo.load()[1]


@pytest.fixture(scope="session")
def root():
    return ROOT
