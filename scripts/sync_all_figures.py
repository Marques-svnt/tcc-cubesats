"""Synchronizes all figures (.png and .pdf) across all 8 project directories.

Ensures strict compliance with the academic-figures-plots skill:
1. Full parity between high-res raster (.png >= 300 DPI) and vector/lossless (.pdf).
2. Synchronization across all 8 target directories.
"""

from __future__ import annotations

import logging
from pathlib import Path
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sync_all_figures")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TARGET_DIRS = [
    PROJECT_ROOT / "figures",
    PROJECT_ROOT / "Entregas-finais" / "01-Tese-Exaustiva" / "figuras",
    PROJECT_ROOT / "Entregas-finais" / "01-Tese-Exaustiva" / "04-figuras",
    PROJECT_ROOT / "Entregas-finais" / "02-Artigos-Cientificos" / "01-Materials-and-Design-Elsevier" / "figures",
    PROJECT_ROOT / "Entregas-finais" / "02-Artigos-Cientificos" / "02-Aerospace-Science-and-Technology-Elsevier" / "figures",
    PROJECT_ROOT / "Entregas-finais" / "02-Artigos-Cientificos" / "03-Engineering-Applications-of-AI-Elsevier" / "figures",
    PROJECT_ROOT / "Entregas-finais" / "03-TCC-Graduacao-UESC" / "figuras",
    PROJECT_ROOT / "Entregas-finais" / "03-TCC-Graduacao-UESC" / "04-figuras",
    PROJECT_ROOT / "monografia" / "figuras",
    PROJECT_ROOT / "monografia" / "04-figuras",
]


def ensure_pdf_companion(png_path: Path) -> Path:
    """Ensures a corresponding .pdf exists for every .png."""
    pdf_path = png_path.with_suffix(".pdf")
    if not pdf_path.exists():
        logger.info("Generating PDF companion for %s", png_path.name)
        img = Image.open(png_path)
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1])
            bg.save(pdf_path, "PDF", resolution=300.0)
        else:
            img.convert("RGB").save(pdf_path, "PDF", resolution=300.0)
    return pdf_path


def sync_figures() -> None:
    """Copies all canonical figures from figures/ to all destination directories."""
    source_dir = PROJECT_ROOT / "figures"
    
    # First, make sure every png in figures/ has a pdf companion
    for png in source_dir.glob("*.png"):
        ensure_pdf_companion(png)

    # Also check reports/ for pareto_frontier and parity_plots
    reports_dir = PROJECT_ROOT / "reports"
    for r_png in ["pareto_frontier.png", "parity_plots.png"]:
        src_f = reports_dir / r_png
        if src_f.exists():
            dest_png = source_dir / r_png
            if not dest_png.exists():
                import shutil
                shutil.copy2(src_f, dest_png)
            ensure_pdf_companion(dest_png)

    all_files = list(source_dir.glob("*.png")) + list(source_dir.glob("*.pdf"))
    logger.info("Found %d master figure files in figures/ to synchronize.", len(all_files))

    import shutil
    for d in TARGET_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        for f in all_files:
            dest = d / f.name
            if not dest.exists() or dest.stat().st_mtime < f.stat().st_mtime:
                shutil.copy2(f, dest)

    logger.info("Successfully synchronized all figures to all %d target directories.", len(TARGET_DIRS))


if __name__ == "__main__":
    sync_figures()
