import importlib.util
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / ".agents" / "skills" / "create-project" / "scripts" / "sync.py"
spec = importlib.util.spec_from_file_location("sync", SCRIPT)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

LINES = "".join(f"line {i}\n" for i in range(1, 11))


def commit(root: Path, files: dict[str, str]) -> str:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(root)]
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "x"], check=True)
    return subprocess.run([*git, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def test_three_way_decisions(tmp_path: Path) -> None:
    base = {f".agents/{n}": LINES for n in ("update", "custom", "merge", "gone", "conflict")}
    foundry, repo, ref = tmp_path / "foundry", tmp_path / "repo", tmp_path / "ref"
    for d in (foundry, repo, ref):
        d.mkdir()
    sha = commit(foundry, base)
    commit(repo, {
        **base,
        ".agents/custom": LINES + "repo only\n",                  # repo changed, template did not
        ".agents/merge": "repo top\n" + LINES,                    # both changed, different places
        ".agents/conflict": LINES.replace("line 5", "repo 5"),    # both changed the same line
        ".agents/own": "project-owned\n",
    })
    for name, text in {
        ".agents/update": LINES + "template\n",
        ".agents/custom": LINES,
        ".agents/merge": LINES + "template bottom\n",
        ".agents/conflict": LINES.replace("line 5", "template 5"),
        ".agents/new": "new\n",
    }.items():
        (ref / name).parent.mkdir(parents=True, exist_ok=True)
        (ref / name).write_text(text)

    sync.FOUNDRY = foundry
    report = sync.sync(repo, ref, sha)

    assert (repo / ".agents/update").read_text() == LINES + "template\n"
    assert (repo / ".agents/custom").read_text() == LINES + "repo only\n"
    assert (repo / ".agents/merge").read_text() == "repo top\n" + LINES + "template bottom\n"
    assert not (repo / ".agents/gone").exists()
    assert (repo / ".agents/new").read_text() == "new\n"
    assert (repo / ".agents/own").read_text() == "project-owned\n"
    assert "<<<<<<<" in (repo / ".agents/conflict").read_text()
    assert report["CONFLICT (markers left)"] == [".agents/conflict"]
