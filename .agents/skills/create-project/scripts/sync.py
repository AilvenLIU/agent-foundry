#!/usr/bin/env python3
"""Three-way sync of agent tooling from a generated reference project into an existing repo.

usage: sync.py <repo> <reference-project> [--base <foundry-commit>]

base   = the foundry commit the repo was last synced from (auto-detected when omitted:
         the recent commit whose tooling files differ least from the repo's)
ours   = tracked files of <repo> under .agents .claude .codex .githooks
theirs = <reference-project>, generated with init.py for the same project type

For each path: untouched by the repo -> take the template; unchanged by the template -> keep the
repo's file; changed by both -> `git merge-file`, reported as CONFLICT when markers remain.
Template files deleted upstream are removed only if the repo never changed them. The repo's own
.agents/project.yml is never touched. Review the report and `git diff` afterwards.
"""
import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

FOUNDRY = Path(__file__).resolve().parents[4]
SCOPE = (".agents", ".claude", ".codex", ".githooks")


def skipped(path: str) -> bool:
    return path == ".agents/project.yml" or "__pycache__" in path or path.endswith((".pyc", "session_state.json", "settings.local.json"))


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True)


def tracked(cwd: Path, rev: str | None = None) -> set[str]:
    out = git(cwd, "ls-tree", "-r", "--name-only", rev, "--", *SCOPE) if rev else git(cwd, "ls-files", "--", *SCOPE)
    return {p for p in out.stdout.decode().splitlines() if p and not skipped(p)}


def reference_files(ref: Path) -> set[str]:
    found = set()
    for scope in SCOPE:
        for root, _, files in os.walk(ref / scope):
            found |= {str((Path(root) / f).relative_to(ref)) for f in files}
    return {p for p in found if not skipped(p)}


def at_rev(rev: str, path: str) -> bytes | None:
    out = git(FOUNDRY, "show", f"{rev}:{path}")
    return out.stdout if out.returncode == 0 else None


def read(root: Path, path: str) -> bytes | None:
    file = root / path
    return file.read_bytes() if file.is_file() else None


def detect_base(repo: Path, candidates: int = 60) -> str:
    ours = tracked(repo)
    revs = git(FOUNDRY, "log", "--format=%h", f"-n{candidates}").stdout.decode().split()
    def distance(rev: str) -> int:
        return sum(1 for p in ours if at_rev(rev, p) is not None and at_rev(rev, p) != read(repo, p))
    return min(revs, key=distance)


def sync(repo: Path, ref: Path, base: str) -> dict[str, list[str]]:
    report: dict[str, list[str]] = {}
    old, mine, new = tracked(FOUNDRY, base), tracked(repo), reference_files(ref)

    def note(kind: str, path: str) -> None:
        report.setdefault(kind, []).append(path)

    for path in sorted(old | mine | new):
        b, o, t = at_rev(base, path) if path in old else None, read(repo, path), read(ref, path)
        dest = repo / path
        if t is None:  # gone from the template
            if o is None:
                continue
            if b is None:
                note("kept (repo-owned)", path)
            elif o == b:
                dest.unlink()
                note("removed (template dropped it)", path)
            else:
                note("kept (customised, template dropped it)", path)
        elif o is None:
            if b is None:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ref / path, dest)
                note("added", path)
            else:
                note("skipped (repo deleted it)", path)
        elif o == t:
            continue
        elif b is None:
            note("CONFLICT (repo file at a template path)", path)
        elif o == b:
            shutil.copy2(ref / path, dest)
            note("updated", path)
        elif t == b:
            note("kept (customised)", path)
        else:
            with tempfile.TemporaryDirectory() as tmp:
                (Path(tmp) / "base").write_bytes(b)
                (Path(tmp) / "theirs").write_bytes(t)
                merged = subprocess.run(["git", "merge-file", "-p", "-L", "repo", "-L", "base", "-L", "template", str(dest), str(Path(tmp) / "base"), str(Path(tmp) / "theirs")], capture_output=True)
            dest.write_bytes(merged.stdout)
            note("CONFLICT (markers left)" if merged.returncode else "merged", path)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("--base")
    args = parser.parse_args()
    repo = args.repo.resolve()
    base = args.base or detect_base(repo)
    print(f"base: foundry {base}")
    for kind, paths in sync(repo, args.reference.resolve(), base).items():
        print(f"\n## {kind} ({len(paths)})")
        print("\n".join(f"  {p}" for p in paths))


if __name__ == "__main__":
    main()
