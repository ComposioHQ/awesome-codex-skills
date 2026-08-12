"""Tests for scripts/validate_skills.py."""

from __future__ import annotations

import os
import sys
import textwrap

import pytest

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
)

import validate_skills  # noqa: E402


VALID_SKILL_MD = textwrap.dedent(
    """\
    ---
    name: demo-skill
    description: Does a demo thing, and says when Codex should trigger it.
    ---

    # Demo Skill

    Steps.
    """
)


def write_skill(root, name, contents=VALID_SKILL_MD):
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    if contents is not None:
        (skill_dir / "SKILL.md").write_text(contents, encoding="utf-8")
    return skill_dir


def write_readme(root, names):
    links = "\n".join(f"- [{n}/](./{n}/) - A skill." for n in names)
    (root / "README.md").write_text(f"## Skills\n\n{links}\n", encoding="utf-8")


@pytest.fixture
def repo(tmp_path):
    """A minimal repo containing one valid skill and a README that links it."""
    write_skill(tmp_path, "demo-skill")
    write_readme(tmp_path, ["demo-skill"])
    return tmp_path


def messages(report):
    return [str(problem) for problem in report.problems]


def test_valid_repo_passes(repo):
    report = validate_skills.validate(str(repo))
    assert report.problems == []
    assert report.ok
    assert report.skills_checked == 1


def test_missing_skill_md_is_an_error(repo):
    write_skill(repo, "no-metadata", contents=None)
    write_readme(repo, ["demo-skill", "no-metadata"])

    report = validate_skills.validate(str(repo))

    assert not report.ok
    assert any("no-metadata: missing SKILL.md" in m for m in messages(report))


def test_missing_frontmatter_is_an_error(repo):
    write_skill(repo, "bare-skill", contents="# Bare Skill\n\nNo frontmatter here.\n")
    write_readme(repo, ["demo-skill", "bare-skill"])

    report = validate_skills.validate(str(repo))

    assert not report.ok
    assert any("missing YAML frontmatter" in m for m in messages(report))


@pytest.mark.parametrize(
    "frontmatter, expected",
    [
        ("description: Only a description.", "missing required field 'name'"),
        ("name: gapped-skill", "missing required field 'description'"),
        ("name: \ndescription: Empty name.", "field 'name' is empty"),
        ("name: gapped-skill\ndescription: \"\"", "field 'description' is empty"),
    ],
)
def test_required_fields(repo, frontmatter, expected):
    write_skill(repo, "gapped-skill", contents=f"---\n{frontmatter}\n---\n\n# Gapped\n")
    write_readme(repo, ["demo-skill", "gapped-skill"])

    report = validate_skills.validate(str(repo))

    assert not report.ok
    assert any(expected in m for m in messages(report))


def test_name_must_match_directory(repo):
    write_skill(
        repo,
        "video-downloader",
        contents="---\nname: youtube-downloader\ndescription: Downloads videos.\n---\n",
    )
    write_readme(repo, ["demo-skill", "video-downloader"])

    report = validate_skills.validate(str(repo))

    assert not report.ok
    assert any(
        "name 'youtube-downloader' does not match its directory name 'video-downloader'" in m
        for m in messages(report)
    )


def test_title_case_name_is_an_error(repo):
    write_skill(
        repo,
        "ahrefs-automation",
        contents="---\nname: Ahrefs Automation\ndescription: Automates Ahrefs.\n---\n",
    )
    write_readme(repo, ["demo-skill", "ahrefs-automation"])

    report = validate_skills.validate(str(repo))

    assert not report.ok
    assert any("name 'Ahrefs Automation' does not match" in m for m in messages(report))


def test_non_slug_directory_is_a_warning_not_an_error(repo):
    write_skill(
        repo,
        "zoho_mail-automation",
        contents="---\nname: zoho_mail-automation\ndescription: Automates Zoho Mail.\n---\n",
    )
    write_readme(repo, ["demo-skill", "zoho_mail-automation"])

    report = validate_skills.validate(str(repo))

    assert report.ok
    assert len(report.warnings) == 1
    assert "is not a lowercase hyphenated slug" in str(report.warnings[0])


def test_oversized_description_is_an_error(repo):
    long_description = "x" * (validate_skills.MAX_DESCRIPTION_LENGTH + 1)
    write_skill(
        repo,
        "wordy-skill",
        contents=f"---\nname: wordy-skill\ndescription: {long_description}\n---\n",
    )
    write_readme(repo, ["demo-skill", "wordy-skill"])

    report = validate_skills.validate(str(repo))

    assert not report.ok
    assert any("over the" in m and "character limit" in m for m in messages(report))


def test_description_at_the_limit_passes(repo):
    at_limit = "x" * validate_skills.MAX_DESCRIPTION_LENGTH
    write_skill(
        repo,
        "exact-skill",
        contents=f"---\nname: exact-skill\ndescription: {at_limit}\n---\n",
    )
    write_readme(repo, ["demo-skill", "exact-skill"])

    assert validate_skills.validate(str(repo)).ok


def test_skill_missing_from_readme_index_is_an_error(repo):
    write_skill(repo, "unlisted-skill", contents=VALID_SKILL_MD.replace("demo-skill", "unlisted-skill"))

    report = validate_skills.validate(str(repo))

    assert not report.ok
    assert any(
        "'./unlisted-skill/' is not linked from the README index" in m
        for m in messages(report)
    )


def test_readme_link_to_missing_path_is_an_error(repo):
    write_readme(repo, ["demo-skill", "deleted-skill"])

    report = validate_skills.validate(str(repo))

    assert not report.ok
    assert any(
        "'./deleted-skill' points at a path that does not exist" in m
        for m in messages(report)
    )


def test_collection_children_are_validated(repo):
    collection = repo / "composio-skills"
    write_skill(
        collection,
        "algolia-automation",
        contents="---\nname: algolia-automation\ndescription: Automates Algolia.\n---\n",
    )
    write_skill(
        collection,
        "attio-automation",
        contents="---\nname: Attio Automation\ndescription: Automates Attio.\n---\n",
    )
    write_readme(repo, ["demo-skill", "composio-skills"])

    report = validate_skills.validate(str(repo))

    assert report.skills_checked == 3
    assert [str(p) for p in report.errors] == [
        "composio-skills/attio-automation/SKILL.md: name 'Attio Automation' does not "
        "match its directory name 'attio-automation' (the name must be the directory's "
        "lowercase hyphenated slug)"
    ]


def test_scripts_and_tests_directories_are_not_skills(repo):
    (repo / "scripts").mkdir()
    (repo / "tests").mkdir()

    report = validate_skills.validate(str(repo))

    assert report.ok
    assert report.skills_checked == 1


def test_parse_frontmatter_handles_quotes_nesting_and_block_scalars():
    fields = validate_skills.parse_frontmatter(
        textwrap.dedent(
            """\
            ---
            name: "quoted-skill"
            description: >
              A folded description
              across two lines.
            requires:
              mcp:
                - rube
            ---

            body
            """
        )
    )

    assert fields["name"] == "quoted-skill"
    assert fields["description"] == "A folded description across two lines."
    assert "mcp" not in fields


def test_parse_frontmatter_returns_none_without_a_block():
    assert validate_skills.parse_frontmatter("# No frontmatter\n") is None


def test_main_reports_exit_codes(repo, capsys):
    assert validate_skills.main(["--root", str(repo)]) == 0

    write_skill(
        repo,
        "zoho_mail-automation",
        contents="---\nname: zoho_mail-automation\ndescription: Automates Zoho Mail.\n---\n",
    )
    write_readme(repo, ["demo-skill", "zoho_mail-automation"])
    capsys.readouterr()

    assert validate_skills.main(["--root", str(repo)]) == 0
    assert validate_skills.main(["--root", str(repo), "--strict"]) == 1

    write_skill(repo, "broken-skill", contents="no frontmatter\n")
    write_readme(repo, ["demo-skill", "zoho_mail-automation", "broken-skill"])

    assert validate_skills.main(["--root", str(repo)]) == 1


def test_main_json_output(repo, capsys):
    import json

    write_skill(
        repo,
        "video-downloader",
        contents="---\nname: youtube-downloader\ndescription: Downloads videos.\n---\n",
    )
    write_readme(repo, ["demo-skill", "video-downloader"])

    exit_code = validate_skills.main(["--root", str(repo), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["ok"] is False
    assert payload["skills_checked"] == 2
    assert payload["problems"][0]["severity"] == "error"


def test_real_repository_is_valid():
    """The catalog in this repository must satisfy its own rules."""
    report = validate_skills.validate(validate_skills.repo_root())

    assert [str(p) for p in report.errors] == []
