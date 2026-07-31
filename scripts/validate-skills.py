#!/usr/bin/env python3
"""Automated validator for Codex Skills in awesome-codex-skills repository.

Validates that each skill directory contains a SKILL.md with valid YAML frontmatter,
matching directory name, and context-friendly description length.
"""

from __future__ import annotations

import os
import sys
import re

def validate_skill_file(skill_path: str, expected_name: str) -> list[str]:
    errors = []
    if not os.path.exists(skill_path):
        return [f"Missing SKILL.md in directory: {expected_name}"]

    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for YAML frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        errors.append(f"Invalid or missing YAML frontmatter in {skill_path}")
        return errors

    frontmatter = frontmatter_match.group(1)
    
    # Check for required 'name' field
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if not name_match:
        errors.append(f"Missing 'name' field in frontmatter: {skill_path}")
    else:
        skill_name = name_match.group(1).strip().strip("'\"")
        if skill_name != expected_name:
            errors.append(f"Skill name '{skill_name}' does not match folder name '{expected_name}'")

    # Check for required 'description' field
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if not desc_match:
        errors.append(f"Missing 'description' field in frontmatter: {skill_path}")
    else:
        description = desc_match.group(1).strip()
        if len(description) > 500:
            errors.append(f"Description in {skill_path} exceeds 500 characters ({len(description)} chars)")

    return errors

def main() -> int:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ignored_dirs = {".git", ".github", "skill-installer", "scripts", "i18n", "composio-skills"}

    passed = 0
    failed = 0
    total_errors = []

    for item in sorted(os.listdir(repo_root)):
        item_path = os.path.join(repo_root, item)
        if os.path.isdir(item_path) and item not in ignored_dirs:
            skill_md = os.path.join(item_path, "SKILL.md")
            errors = validate_skill_file(skill_md, item)
            if errors:
                failed += 1
                total_errors.extend(errors)
            else:
                passed += 1

    print(f"--- Codex Skills Validation Summary ---")
    print(f"Passed: {passed} skills")
    print(f"Failed: {failed} skills")

    if total_errors:
        print("\nValidation Errors:")
        for err in total_errors:
            print(f"  [ERROR] {err}")
        return 1

    print("\n[SUCCESS] All skills passed validation successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
