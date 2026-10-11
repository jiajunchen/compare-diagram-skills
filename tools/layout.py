"""Shared locations for presentation results, reusable inputs, and scratch files."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIGURES = REPO / "figures"
TOOLS = REPO / "figures/tools"
QWEN = REPO / ".runtime/qwen-tts"


def runtime(collection: str) -> Path:
    """Create a disposable render directory outside the finished results."""
    path = REPO / ".runtime/figures" / collection
    path.mkdir(parents=True, exist_ok=True)
    return path


def assets(collection: str) -> Path:
    """Locate reusable production inputs, including original simulator captures."""
    path = TOOLS / "assets" / collection
    path.mkdir(parents=True, exist_ok=True)
    return path
