import json
from pathlib import Path

import pytest


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def parties_data():
    path = DATA_DIR / "25th-Knesset-2022" / "parties.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def poll_now14():
    path = DATA_DIR / "25th-Knesset-2022" / "polls" / "2022-10-27-now14.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)
