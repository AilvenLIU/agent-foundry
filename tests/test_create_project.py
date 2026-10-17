import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / ".agents" / "skills" / "create-project" / "scripts"))

from init import create_project  # noqa: E402


@pytest.mark.parametrize("kind", ["python", "cpp", "hybrid"])
def test_generated_project(tmp_path: Path, kind: str) -> None:
    create_project(ROOT, tmp_path, kind)

    agents = (tmp_path / "AGENTS.md").read_text()
    assert agents.startswith("# Project instructions")
    assert ("## Python" in agents) == (kind in ("python", "hybrid"))
    assert ("## C++/CUDA" in agents) == (kind in ("cpp", "hybrid"))
    assert (tmp_path / "CLAUDE.md").read_text().strip() == "@AGENTS.md"

    skills = {p.name for p in (tmp_path / ".claude" / "skills").iterdir()}
    assert "create-project" not in skills
    assert ("python-env" in skills) == (kind != "cpp")
    assert ("cuda" in skills) == (kind != "python")

    branch = subprocess.run(
        ["git", "branch", "--show-current"], cwd=tmp_path, capture_output=True, text=True, check=True
    ).stdout.strip()
    assert branch == "main"
    assert not (tmp_path / ".github").exists() and not (tmp_path / "LICENSE").exists()
    if kind == "hybrid":
        assert "nanobind" in (tmp_path / "pyproject.toml").read_text()
