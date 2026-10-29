"""``split_pages: true`` writes one reference file per scraped page instead of one per category."""

from pathlib import Path

import pytest

from skill_seekers.cli.doc_scraper import DocToSkillConverter

BASE = "https://example.com/proj/latest/"
PAGES = [
    {"title": "proj", "url": BASE, "content": "Home page about proj.", "headings": []},
    {
        "title": "Matchers - proj",
        "url": f"{BASE}features/matchers/",
        "content": "Matchers.",
        "headings": [],
    },
    {
        "title": "Argument captors - proj",
        "url": f"{BASE}features/captors/",
        "content": "Captors.",
        "headings": [],
    },
]


def _build(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, pages: list[dict] = PAGES, **extra: object
) -> Path:
    monkeypatch.chdir(tmp_path)
    config = {"name": "proj", "base_url": BASE, **extra}
    converter = DocToSkillConverter(config)
    monkeypatch.setattr(converter, "load_scraped_data", lambda: pages)
    assert converter.build_skill()
    return Path(converter.skill_dir) / "references"


def test_split_pages_writes_one_file_per_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    refs = _build(tmp_path, monkeypatch, split_pages=True)
    assert sorted(p.name for p in refs.glob("*.md")) == [
        "captors.md",
        "home.md",
        "index.md",
        "matchers.md",
    ]
    assert "Matchers." in (refs / "matchers.md").read_text(encoding="utf-8")
    index = (refs / "index.md").read_text(encoding="utf-8")
    assert "`matchers.md`" in index
    assert "`home.md`" in index


def test_split_pages_skill_md_lists_the_page_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    refs = _build(tmp_path, monkeypatch, split_pages=True)
    skill_md = (refs.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "matchers.md" in skill_md


def test_split_pages_disambiguates_colliding_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pages = [
        {"title": "A", "url": f"{BASE}a/setup/", "content": "First.", "headings": []},
        {"title": "B", "url": f"{BASE}b/setup/", "content": "Second.", "headings": []},
    ]
    refs = _build(tmp_path, monkeypatch, pages, split_pages=True)
    assert (refs / "setup.md").is_file()
    assert (refs / "setup-2.md").is_file()


def test_default_keeps_category_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    refs = _build(tmp_path, monkeypatch)
    assert not (refs / "matchers.md").exists()
    assert not (refs / "home.md").exists()
