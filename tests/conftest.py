import shutil
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.repository_fake import FakeRepository


@pytest.fixture
def repo(tmp_path):
    seed = ROOT / "mock_data/seed_state.json"
    state = tmp_path / "state.json"
    shutil.copyfile(seed, state)
    return FakeRepository(state_path=state, seed_path=seed)


@pytest.fixture
def c0():
    return {"eligibility": "KEEP", "remove_reason": None, "C_label": "C0", "S_label": "S0", "A_label": "A0", "uncertain": False}


@pytest.fixture
def c1():
    return {"eligibility": "KEEP", "remove_reason": None, "C_label": "C1", "S_label": "S2", "A_label": "A3", "uncertain": False}
