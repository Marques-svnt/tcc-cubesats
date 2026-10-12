# 05: Uncertainty Quantification Synthesis and Monograph Reporting

**What to build:** Automated pipeline runner executing Monte Carlo uncertainty quantification on the canonical flight candidate and Pareto frontier, generating JSON telemetry, Markdown executive report, and LaTeX table (booktabs/siunitx) for Chapter 5 of the monograph.

**Blocked by:** 04: CI/CD Pipeline Automation and Monograph Verification

**Status:** completed

- [x] Implement `scripts/run_uncertainty_analysis.py` executing 10,000 Monte Carlo draws
- [x] Export structured JSON telemetry to `reports/uncertainty_quantification_flight_report.json`
- [x] Generate Markdown synthesis in `reports/uncertainty_quantification_flight_report.md`
- [x] Generate publication-grade LaTeX table in `monografia/04-figuras/tab_uncertainty_quantification.tex`
- [x] Add unit test verifying artifact generation and data integrity
