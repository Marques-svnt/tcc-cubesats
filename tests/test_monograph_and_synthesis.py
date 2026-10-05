"""Unit and regression tests for monograph integrity, final synthesis, and presentation artifacts.

Ensures that all chapters (1 through 6), references, Pareto data, comparison
metrics, and defense presentation scripts conform to project specifications.
"""

from pathlib import Path
import csv
import json
import pytest


@pytest.fixture
def project_root() -> Path:
    """Returns the project root directory."""
    return Path(__file__).resolve().parent.parent


def test_monograph_structure_and_chapters(project_root: Path) -> None:
    """Verifies that all chapters 1 to 6 and bibliography exist in the monograph."""
    monograph_path = project_root / "TCC - Gabriel Marques de Andrade - v2.md"
    assert monograph_path.exists(), f"Monograph not found at {monograph_path}"

    content = monograph_path.read_text(encoding="utf-8")

    expected_sections = [
        "# **1 INTRODUÇÃO**",
        "# **2 OBJETIVOS**",
        "# **3 REVISÃO DE LITERATURA**",
        "# **4 METODOLOGIA**",
        "# **5 RESULTADOS E DISCUSSÃO**",
        "# **6 CONCLUSÃO E TRABALHOS FUTUROS**",
        "# **REFERÊNCIAS BIBLIOGRÁFICAS**",
    ]

    for section in expected_sections:
        assert section in content, f"Missing section '{section}' in monograph."


def test_flight_comparison_and_pareto_artifacts(project_root: Path) -> None:
    """Validates the integrity of the flight design comparison JSON and Pareto CSV."""
    json_path = project_root / "reports" / "flight_design_comparison.json"
    csv_path = project_root / "data" / "pareto_optimal_designs.csv"
    png_path = project_root / "reports" / "pareto_frontier.png"

    assert json_path.exists(), f"Flight comparison JSON missing at {json_path}"
    assert csv_path.exists(), f"Pareto CSV missing at {csv_path}"
    assert png_path.exists(), f"Pareto PNG plot missing at {png_path}"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "optimal_flight_design" in data
    assert "surrogate_predicted_responses" in data
    assert "fea_ground_truth_responses" in data
    assert "conventional_baseline_comparison" in data

    baseline = data["conventional_baseline_comparison"]
    assert baseline["mass_reduction_percent"] > 60.0
    assert baseline["vibration_attenuation_gain_percent"] > 75.0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 100
    assert "theta_deg" in rows[0]
    assert "total_mass_kg" in rows[0]
    assert "transmissibility_ratio" in rows[0]


def test_defense_presentation_script(project_root: Path) -> None:
    """Verifies that the 20-minute defense presentation script is complete."""
    presentation_path = project_root / "reports" / "apresentacao_banca_tcc.md"
    assert presentation_path.exists(), f"Presentation script missing at {presentation_path}"

    content = presentation_path.read_text(encoding="utf-8")

    assert "## Slide 1 — Capa do Projeto" in content
    assert "## Slide 20 — Agradecimentos e Arguição" in content
    assert "20 minutos" in content
    assert "Prof.ª Dr.ª Nila Cecília de Faria Lopes Medeiros" in content
