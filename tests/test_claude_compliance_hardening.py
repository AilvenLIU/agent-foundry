#!/usr/bin/env python3
"""Regression tests for Claude/Codex instruction parity hardening."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / ".agents" / "scripts"))

from constraints_check import check_constraints  # type: ignore[import-not-found]  # noqa: E402
from project_profile import (  # type: ignore[import-not-found]  # noqa: E402
    BuildSystem,
    Language,
    ProjectProfile,
)


ROOT = Path(__file__).parent.parent


def _text(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")








def test_template_project_yml_contains_project_profile_metadata() -> None:
    expectations = {
        "templates/python/project.yml": ["project_type: python", "language: [python]"],
        "templates/cpp/project.yml": ["project_type: cpp", "language: [cpp]"],
        "templates/hybrid/project.yml": [
            "project_type: hybrid",
            "language: [python, cpp]",
            "build_system: scikit-build-core",
        ],
    }
    for rel_path, needles in expectations.items():
        content = _text(rel_path)
        assert "project_profile:" in content
        for needle in needles:
            assert needle in content




def test_native_build_ownership_detects_setup_py_extension(tmp_path: Path) -> None:
    (tmp_path / "CMakeLists.txt").write_text(
        "cmake_minimum_required(VERSION 3.24)\n",
        encoding="utf-8",
    )
    (tmp_path / "cmake").mkdir()
    (tmp_path / "cmake" / "CPM.cmake").write_text("", encoding="utf-8")
    (tmp_path / "cmake" / "Dependencies.cmake").write_text("", encoding="utf-8")
    (tmp_path / "cmake" / "Options.cmake").write_text("", encoding="utf-8")
    (tmp_path / "3rdparty" / "cpm-cache").mkdir(parents=True)
    (tmp_path / "3rdparty" / "cpm-cache" / ".gitkeep").write_text("", encoding="utf-8")
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup, Extension\n"
        "setup(ext_modules=[Extension('pkg._core', ['src/core.cpp'])])\n",
        encoding="utf-8",
    )

    profile = ProjectProfile(
        language=[Language.PYTHON, Language.CPP],
        build_system=BuildSystem.SCIKIT_BUILD_CORE,
    )
    violations = check_constraints(tmp_path, profile)

    assert any(
        v.category == "Native Build Ownership"
        and "setup.py" in v.message
        and v.severity == "CRITICAL"
        for v in violations
    )
