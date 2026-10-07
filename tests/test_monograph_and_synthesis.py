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
    """Verifies that all chapters 1 to 6 and bibliography exist in monografia_v3 if present."""
    latex_dir = project_root / "monografia_v3"
    if not latex_dir.exists():
        pytest.skip("monografia_v3 is tracked on branch monografia/etapa-03-overleaf-modular")

    assert (latex_dir / "main.tex").exists(), "main.tex not found in monografia_v3"

    expected_chapters = [
        ("01_introducao.tex", "Introdução"),
        ("02_objetivos.tex", "Objetivos"),
        ("03_revisao_literatura.tex", "Revisão de literatura"),
        ("04_metodologia.tex", "Metodologia"),
        ("05_resultados_discussao.tex", "Resultados e discussão"),
        ("06_conclusao.tex", "Conclusão e trabalhos futuros"),
    ]

    for filename, chapter_title in expected_chapters:
        chap_path = latex_dir / "capitulos" / filename
        assert chap_path.exists(), f"Chapter file missing: {chap_path}"
        content = chap_path.read_text(encoding="utf-8")
        assert f"\\chapter{{{chapter_title}}}" in content, f"Missing \\chapter{{{chapter_title}}} in {filename}"

    ref_path = latex_dir / "postextual" / "referencias.tex"
    assert ref_path.exists(), f"References file missing: {ref_path}"
    assert "\\begin{thebibliography}" in ref_path.read_text(encoding="utf-8")


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


def test_monograph_v4_structure_and_compilation(project_root: Path) -> None:
    """Verifies that the enhanced monografia_v4 exists, is compiled to PDF, and contains all fixes if present."""
    v4_dir = project_root / "monografia_v4"
    if not v4_dir.exists():
        pytest.skip("monografia_v4 is tracked on branch monografia/etapa-04-revisao-canonica")

    assert (v4_dir / "main.tex").exists(), "main.tex not found in monografia_v4"
    
    pdf_path = v4_dir / "main.pdf"
    assert pdf_path.exists(), "Compiled main.pdf not found in monografia_v4"
    assert pdf_path.stat().st_size > 1_000_000, "main.pdf size is abnormally small"

    # Verify literature fix [m1]
    rev_lit = (v4_dir / "capitulos" / "03_revisao_literatura.tex").read_text(encoding="utf-8")
    assert "Ermurat" in rev_lit, "Ermurat citation missing from 03_revisao_literatura.tex"

    # Verify mechanics fix [M1]
    metodologia = (v4_dir / "capitulos" / "04_metodologia.tex").read_text(encoding="utf-8")
    assert "\\SI{230.0}{\\mega\\pascal}" in metodologia, "Yield strength 230 MPa missing from 04_metodologia.tex"
    assert "\\SI{184.0}{\\mega\\pascal}" in metodologia, "Allowable stress 184 MPa missing from 04_metodologia.tex"

    # Verify Pareto table fix [m4]
    resultados = (v4_dir / "capitulos" / "05_resultados_discussao.tex").read_text(encoding="utf-8")
    assert "tab:pareto-pontos" in resultados, "Pareto table missing from 05_resultados_discussao.tex"
    assert "Bloch-Floquet" in resultados

    # Verify canonical parameters alignment [M2]
    params = (v4_dir / "PARAMETROS_CANONICOS.md").read_text(encoding="utf-8")
    assert "512" in params, "Baseline frequency 512 Hz missing from PARAMETROS_CANONICOS.md"
    assert "184" in params, "Allowable stress 184 MPa missing from PARAMETROS_CANONICOS.md"


def test_monograph_v5_structure_and_compilation(project_root: Path) -> None:
    """Verifies that final monograph (monografia_v5 or monografia) adheres to the UESC template and compiles to PDF."""
    v5_dir = project_root / "monografia_v5"
    if not v5_dir.exists():
        v5_dir = project_root / "monografia"

    assert (v5_dir / "Main.tex").exists(), f"Main.tex not found in {v5_dir}"

    pdf_path = v5_dir / "Main.pdf"
    if not pdf_path.exists():
        pdf_path = v5_dir / "monografia_tcc_final.pdf"
    assert pdf_path.exists(), f"Compiled PDF not found in {v5_dir}"
    assert pdf_path.stat().st_size > 1_000_000, "Compiled PDF size is abnormally small"

    expected_chapters = [
        "cap1-introducao.tex",
        "cap2-objetivos.tex",
        "cap3-revisao_literatura.tex",
        "cap4-metodologia.tex",
        "cap5-resultados_discussao.tex",
        "cap6-conclusao.tex",
    ]
    textual_dir = v5_dir / "02-elementos-textuais"
    for chap in expected_chapters:
        assert (textual_dir / chap).exists(), f"Chapter {chap} missing from {v5_dir}"

    assert (v5_dir / "pacotes" / "ppgmc-uesc.cls").exists(), "ppgmc-uesc.cls missing"
    assert (v5_dir / "pacotes" / "macros-cubesat.tex").exists(), "macros-cubesat.tex missing"
    assert (v5_dir / "03-elementos-pos-textuais" / "refbase.bib").exists(), "refbase.bib missing"
    assert (v5_dir / "03-elementos-pos-textuais" / "referencias.tex").exists(), "referencias.tex missing"



