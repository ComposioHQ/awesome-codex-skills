#!/usr/bin/env python3
"""Validate the skill catalog: SKILL.md frontmatter and README index consistency.

Run from anywhere:

    python scripts/validate_skills.py

Exits non-zero and prints a grouped report when any skill is invalid.
Use --json for machine-readable output.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field

# Directories that live at the repo root but are not skills themselves.
NON_SKILL_DIRS = {"scripts", "tests"}

# Directories whose children are skills rather than the directory itself.
SKILL_COLLECTION_DIRS = {"composio-skills"}

# Descriptions are loaded eagerly into the agent's context for every session,
# so an oversized one is a cost paid on every request.
MAX_DESCRIPTION_LENGTH = 1024

SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)
README_LINK_RE = re.compile(r"\]\(\./([^)\s]+?)/?\)")


ERROR = "error"
WARNING = "warning"


@dataclass
class Problem:
    path: str
    message: str
    severity: str = ERROR

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclass
class Report:
    skills_checked: int = 0
    problems: list[Problem] = field(default_factory=list)

    @property
    def errors(self) -> list[Problem]:
        return [p for p in self.problems if p.severity == ERROR]

    @property
    def warnings(self) -> list[Problem]:
        return [p for p in self.problems if p.severity == WARNING]

    @property
    def ok(self) -> bool:
        return not self.errors

    def add(self, path: str, message: str, severity: str = ERROR) -> None:
        self.problems.append(Problem(path, message, severity))


def repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Return top-level scalar keys of the YAML frontmatter, or None if absent.

    Deliberately minimal (stdlib only): top-level ``key: value`` pairs plus
    ``|``/``>`` block scalars. Nested mappings and sequences are skipped, since
    validation only cares about ``name`` and ``description``.
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None

    fields: dict[str, str] = {}
    lines = match.group(1).split("\n")
    index = 0
    while index < len(lines):
        line = lines[index].rstrip("\r")
        index += 1
        if not line.strip() or line.startswith("#") or line[:1].isspace():
            continue
        key, sep, raw_value = line.partition(":")
        if not sep or not key.strip():
            continue
        key = key.strip()
        value = raw_value.strip()
        if value in ("|", ">", "|-", ">-", "|+", ">+"):
            block: list[str] = []
            while index < len(lines):
                candidate = lines[index].rstrip("\r")
                if candidate.strip() and not candidate[:1].isspace():
                    break
                block.append(candidate.strip())
                index += 1
            joiner = "\n" if value.startswith("|") else " "
            value = joiner.join(block).strip()
        fields[key] = _unquote(value)
    return fields


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def discover_skill_dirs(root: str) -> list[str]:
    """Return repo-relative paths of every skill directory, sorted."""
    skills: list[str] = []
    for name in sorted(os.listdir(root)):
        if name.startswith(".") or name in NON_SKILL_DIRS:
            continue
        path = os.path.join(root, name)
        if not os.path.isdir(path):
            continue
        if name in SKILL_COLLECTION_DIRS:
            for child in sorted(os.listdir(path)):
                if child.startswith("."):
                    continue
                if os.path.isdir(os.path.join(path, child)):
                    skills.append(f"{name}/{child}")
            continue
        skills.append(name)
    return skills


def validate_skill(root: str, rel_path: str, report: Report) -> None:
    report.skills_checked += 1
    skill_dir = os.path.join(root, *rel_path.split("/"))
    skill_md = os.path.join(skill_dir, "SKILL.md")
    rel_md = f"{rel_path}/SKILL.md"

    if not os.path.isfile(skill_md):
        report.add(rel_path, "missing SKILL.md")
        return

    with open(skill_md, encoding="utf-8") as handle:
        text = handle.read()

    fields = parse_frontmatter(text)
    if fields is None:
        report.add(rel_md, "missing YAML frontmatter block (file must start with '---')")
        return

    expected_name = rel_path.rsplit("/", 1)[-1]
    name = fields.get("name")
    if name is None:
        report.add(rel_md, "frontmatter is missing required field 'name'")
    elif not name.strip():
        report.add(rel_md, "frontmatter field 'name' is empty")
    elif name != expected_name:
        report.add(
            rel_md,
            f"name {name!r} does not match its directory name {expected_name!r} "
            "(the name must be the directory's lowercase hyphenated slug)",
        )
    elif not SLUG_RE.fullmatch(name):
        # The frontmatter agrees with the directory, so the directory itself is
        # the thing to rename. That is a breaking change for anyone who already
        # installed the skill, so report it without failing the build.
        report.add(
            rel_path,
            f"directory name {name!r} is not a lowercase hyphenated slug",
            WARNING,
        )

    description = fields.get("description")
    if description is None:
        report.add(rel_md, "frontmatter is missing required field 'description'")
    elif not description.strip():
        report.add(rel_md, "frontmatter field 'description' is empty")
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        report.add(
            rel_md,
            f"description is {len(description)} characters, "
            f"over the {MAX_DESCRIPTION_LENGTH} character limit",
        )


def validate_readme(root: str, skill_dirs: list[str], report: Report) -> None:
    readme = os.path.join(root, "README.md")
    if not os.path.isfile(readme):
        report.add("README.md", "missing README.md")
        return

    with open(readme, encoding="utf-8") as handle:
        text = handle.read()

    linked = {match.group(1) for match in README_LINK_RE.finditer(text)}
    top_level = {path for path in skill_dirs if "/" not in path} | (
        SKILL_COLLECTION_DIRS & set(os.listdir(root))
    )

    for name in sorted(top_level - linked):
        report.add("README.md", f"skill directory './{name}/' is not linked from the README index")

    for name in sorted(linked - top_level):
        target = os.path.join(root, *name.split("/"))
        if not os.path.exists(target):
            report.add("README.md", f"link './{name}' points at a path that does not exist")


def validate(root: str) -> Report:
    report = Report()
    skill_dirs = discover_skill_dirs(root)
    for rel_path in skill_dirs:
        validate_skill(root, rel_path, report)
    validate_readme(root, skill_dirs, report)
    return report


def _print_group(title: str, problems: list[Problem], stream) -> None:
    if not problems:
        return
    grouped: dict[str, list[Problem]] = {}
    for problem in problems:
        top = problem.path.split("/", 1)[0]
        grouped.setdefault(top, []).append(problem)

    print(f"{title} ({len(problems)}):", file=stream)
    for top in sorted(grouped):
        print(f"  {top}:", file=stream)
        for problem in grouped[top]:
            print(f"    - {problem}", file=stream)
    print(file=stream)


def _print_report(report: Report) -> None:
    _print_group("Warnings", report.warnings, sys.stdout)
    _print_group("Errors", report.errors, sys.stderr)

    if report.ok:
        print(
            f"OK: {report.skills_checked} skills validated, "
            f"{len(report.warnings)} warning(s), no errors."
        )
    else:
        print(
            f"FAILED: {len(report.errors)} error(s) across "
            f"{report.skills_checked} skills.",
            file=sys.stderr,
        )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=repo_root(), help="Repository root to validate")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output")
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    args = parser.parse_args(argv)

    report = validate(args.root)

    if args.json:
        print(
            json.dumps(
                {
                    "ok": report.ok,
                    "skills_checked": report.skills_checked,
                    "problems": [
                        {
                            "path": p.path,
                            "message": p.message,
                            "severity": p.severity,
                        }
                        for p in report.problems
                    ],
                },
                indent=2,
            )
        )
    else:
        _print_report(report)

    if not report.ok:
        return 1
    return 1 if args.strict and report.warnings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
