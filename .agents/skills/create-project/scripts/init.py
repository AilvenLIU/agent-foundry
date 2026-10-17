#!/usr/bin/env python3
"""Create a new project from Agent Foundry.

Usage: init.py <target-directory> [--type python|cpp|hybrid]

Copies the relevant skills, composes AGENTS.md from the common section plus the
language fragments, writes a minimal build scaffold for native and hybrid types,
and makes one initial commit on `main`.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_TYPES = ("python", "cpp", "hybrid")

# templates/<type>/AGENTS.md fragments appended after templates/common/AGENTS.md.
_FRAGMENTS = {
    "python": ["python"],
    "cpp": ["cpp"],
    "hybrid": ["cpp", "python", "hybrid"],
}

# Skills that only apply to some project types; every other skill goes to all.
_SKILL_TYPES = {
    "create-project": set(),
    "python-env": {"python", "hybrid"},
    "cuda": {"cpp", "hybrid"},
    "gpu-ci": {"cpp", "hybrid"},
    "python-bindings": {"hybrid"},
}

_CMAKE_ROOT = """cmake_minimum_required(VERSION 3.24)
project(myproject VERSION 0.1.0 LANGUAGES CXX CUDA)

option(PROJECT_ENABLE_TESTS "Build native tests" ON)
option(PROJECT_ENABLE_BENCHMARKS "Build benchmarks" OFF)
option(PROJECT_ENABLE_PYTHON "Build Python bindings" OFF)

add_subdirectory(cpp)

if(PROJECT_ENABLE_TESTS)
  enable_testing()
  add_subdirectory({tests})
endif()
{python}"""

_CMAKE_CORE = """add_library(myproject_core INTERFACE)
target_compile_features(myproject_core INTERFACE cxx_std_17)
target_include_directories(myproject_core INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
"""

_PYPROJECT = """[build-system]
requires = ["scikit-build-core", "nanobind", "ninja", "cmake"]
build-backend = "scikit_build_core.build"

[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.10"

[tool.scikit-build]
cmake.build-type = "RelWithDebInfo"
build-dir = "build/{wheel_tag}"
wheel.packages = ["python/myproject"]
"""

_BINDINGS_CMAKE = """find_package(Python 3.10 REQUIRED COMPONENTS Interpreter Development.Module)
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE
  OUTPUT_VARIABLE nanobind_ROOT)
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(_core_ext STABLE_ABI bindings.cpp)
target_link_libraries(_core_ext PRIVATE myproject_core)
install(TARGETS _core_ext DESTINATION myproject)
"""

_BINDINGS_CPP = """#include <nanobind/nanobind.h>

NB_MODULE(_core_ext, module) {
  module.doc() = "myproject native bindings";
}
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _scaffold(target: Path, project_type: str) -> None:
    if project_type == "python":
        return
    hybrid = project_type == "hybrid"
    python_block = (
        "\nif(PROJECT_ENABLE_PYTHON)\n  add_subdirectory(bindings/python)\nendif()\n" if hybrid else ""
    )
    _write(
        target / "CMakeLists.txt",
        _CMAKE_ROOT.format(tests="tests/cpp" if hybrid else "tests", python=python_block),
    )
    _write(target / "cpp" / "CMakeLists.txt", _CMAKE_CORE)
    _write(target / ("tests/cpp" if hybrid else "tests") / "CMakeLists.txt", "")
    if hybrid:
        _write(target / "pyproject.toml", _PYPROJECT)
        _write(target / "bindings" / "python" / "CMakeLists.txt", _BINDINGS_CMAKE)
        _write(target / "bindings" / "python" / "bindings.cpp", _BINDINGS_CPP)
        _write(target / "python" / "myproject" / "__init__.py", "from ._core_ext import *  # noqa: F403\n")
        _write(target / "tests" / "python" / ".gitkeep", "")


def _copy_skills(template_root: Path, target: Path, project_type: str) -> None:
    skills = target / ".agents" / "skills"
    skills.mkdir(parents=True)
    for skill in sorted((template_root / ".agents" / "skills").iterdir()):
        if skill.is_dir() and project_type in _SKILL_TYPES.get(skill.name, set(PROJECT_TYPES)):
            shutil.copytree(skill, skills / skill.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    # Claude Code discovers skills under .claude/skills; point it at the shared copy.
    (target / ".claude").mkdir()
    (target / ".claude" / "skills").symlink_to("../.agents/skills")


def _init_git(target: Path) -> None:
    for args in (
        ("init", "-b", "main"),
        ("add", "."),
        ("commit", "-m", "chore: initialise project from agent-foundry"),
    ):
        subprocess.run(["git", *args], cwd=target, capture_output=True, check=True)


def create_project(template_root: Path, target_dir: Path, project_type: str) -> None:
    templates = template_root / "templates"
    target_dir.mkdir(parents=True, exist_ok=True)

    fragments = [templates / "common" / "AGENTS.md"]
    fragments += [templates / name / "AGENTS.md" for name in _FRAGMENTS[project_type]]
    _write(target_dir / "AGENTS.md", "\n".join(f.read_text() for f in fragments))
    shutil.copy2(templates / "common" / "CLAUDE.md", target_dir / "CLAUDE.md")

    language = templates / project_type
    for name in (".gitignore", "poetry.toml"):
        if (language / name).exists():
            shutil.copy2(language / name, target_dir / name)
    if project_type == "hybrid":
        shutil.copy2(templates / "python" / "poetry.toml", target_dir / "poetry.toml")

    _copy_skills(template_root, target_dir, project_type)
    _scaffold(target_dir, project_type)
    _write(target_dir / "README.md", "# Project Name\n")

    try:
        _init_git(target_dir)
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        print(f"Warning: git bootstrap failed: {error}", file=sys.stderr)

    print(f"Created {project_type} project at {target_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("target", type=Path)
    parser.add_argument("--type", choices=PROJECT_TYPES, dest="project_type")
    args = parser.parse_args()

    target = args.target.resolve()
    if target.exists() and any(target.iterdir()):
        parser.error(f"{target} exists and is not empty")

    project_type = args.project_type
    while project_type is None:
        choice = input("Project type (python / cpp / hybrid): ").strip()
        project_type = choice if choice in PROJECT_TYPES else None

    create_project(Path(__file__).resolve().parents[4], target, project_type)


if __name__ == "__main__":
    main()
