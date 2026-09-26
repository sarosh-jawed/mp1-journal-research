from pathlib import Path

from mp1.config import load_config

TEXT_SUFFIXES = {".py", ".md", ".yml", ".yaml", ".toml"}


def test_analysis_config_loads() -> None:
    config = load_config()
    assert config["project"]["random_seed"] == 42
    assert config["clustering"]["k_values"] == [2, 3, 4, 5, 6]


def test_project_text_contains_no_em_dash() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    excluded_parts = {".git", ".venv", "data", "outputs"}
    prohibited_character = chr(0x2014)

    violations = []
    for path in repository_root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if any(part in excluded_parts for part in path.parts):
            continue

        content = path.read_text(encoding="utf-8")
        if prohibited_character in content:
            violations.append(str(path.relative_to(repository_root)))

    assert not violations, f"Prohibited punctuation found in: {violations}"
