from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mock_seed import build_mock_store
from src.repository_fake import FakeRepository

path = ROOT / ".local" / "mock_state.json"
FakeRepository(path, build_mock_store).reset()
print(f"Mock data reset: {path}")

