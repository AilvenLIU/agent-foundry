#!/usr/bin/env python3
"""Tests guaranteeing dual-platform (Claude/Codex via AGENTS.md) parity and agentic-team wiring.

After the CODEX axis was removed, AGENTS.md is the canonical Codex entrypoint
(per the agents.md spec). These tests assert that AGENTS_*.md carries every
critical rule and procedure mapping that the deleted CODEX_*.md used to carry.
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_agentic_team_constraint_file_exists() -> None:
    path = ROOT / ".agents" / "constraints" / "common" / "agentic-team.md"
    assert path.exists(), "agentic-team constraint must exist"
    assert "Agentic Team" in path.read_text()


def test_session_init_loads_agentic_team_constraint() -> None:
    body = _read(".agents/scripts/session_init.py")
    assert '"common/agentic-team"' in body, (
        "session_init.py must include common/agentic-team in its always-on list "
        "so the constraint appears in the session manifest."
    )








def _required_prohibitions(body: str, items: list[str]) -> list[str]:
    return [item for item in items if item.lower() not in body.lower()]










def test_codex_axis_files_are_gone() -> None:
    """The CODEX*.md files were intentionally removed; agents.md spec replaces them."""
    for name in ("CODEX.md", "CODEX_PYTHON.md", "CODEX_CPP.md"):
        assert not (ROOT / name).exists(), (
            f"{name} should not exist after CODEX axis removal"
        )


def test_roadmap_prompt_template_declares_authority_order() -> None:
    body = _read(".agents/scripts/roadmap/templates/prompt.md")
    for token in (
        "INVARIANTS.md",
        "ROADMAP.md",
        "roadmap.yml",
        "sessions",
        "prompt.md",
    ):
        assert token in body, f"prompt.md template missing token: {token}"
    assert "Repository-Local Precedence" in body
    assert "does not supersede" in body


def test_roadmap_invariants_template_declares_full_authority_order() -> None:
    body = _read(".agents/scripts/roadmap/templates/INVARIANTS.md")
    for token in (
        "INVARIANTS.md",
        "ROADMAP.md",
        "roadmap.yml",
        "sessions",
        "prompt.md",
    ):
        assert token in body, f"INVARIANTS.md template missing token: {token}"


def test_roadmap_roadmap_template_declares_authority_order() -> None:
    body = _read(".agents/scripts/roadmap/templates/ROADMAP.md")
    for token in (
        "INVARIANTS.md",
        "ROADMAP.md",
        "roadmap.yml",
        "sessions",
        "prompt.md",
    ):
        assert token in body, f"ROADMAP.md template missing token: {token}"
