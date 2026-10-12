---
title: Relatório Executivo de Quantificação de Incerteza (UQ) e Tolerâncias LPBF
domain: Aerospace Structural Optimization & Metamaterials
date_synced: 2026-10-12
author: Gabriel Marques de Andrade
institution: Universidade Estadual de Santa Cruz (UESC 2026)
project: CubeSat 1U Auxetic Chassis Optimization & NASA GEVS Qualification
tags:
  - uncertainty-quantification
  - monte-carlo
  - additive-manufacturing
  - lpbf-tolerances
  - nasa-gevs
  - flight-qualification
---

# Avaliação Estocástica de Incertezas de Manufatura Aditiva (LPBF AlSi10Mg)

Este relatório formaliza a verificação de conformidade segundo a norma **NASA-STD-7009B** e o padrão **ASME V&V 10**, avaliando como imperfeições dimensionais típicas do processo de fusão em leito de pó a laser (L-PBF) propagam-se na integridade estrutural do chassi CubeSat 1U.

---

## 1. Parâmetros de Tolerância Estocástica Modelados

* **Espessura da Costela ($t$):** $\Delta t \sim \mathcal{N}(0, (15\ \mu	ext{m})^2)$ (faixa de dispersão $\pm 45\ \mu	ext{m}$ a $3\sigma$)
* **Ângulo Reentrante ($	heta$):** $\Delta 	heta \sim \mathcal{N}(0, (0.50^\circ)^2)$
* **Comprimento da Costela ($l$):** $\Delta l \sim \mathcal{N}(0, (20\ \mu	ext{m})^2)$
* **Altura Vertical ($h$):** $\Delta h \sim \mathcal{N}(0, (20\ \mu	ext{m})^2)$
* **Amostras de Monte Carlo:** $N = 10,000$ realizações vetorizadas via rede neural *Physics-Guided ResNet*.
* **Tempo de Inferência:** 0.0082 s

---

## 2. Resultados Estatísticos no Ponto Ótimo de Voo (Solução TOPSIS)

| Resposta Estrutural | Média ($\mu$) | Desvio ($\sigma$) | Percentil 2.5% | Mediana (P50) | Percentil 97.5% | Margem / Limite NASA |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Frequência Fundamental ($f_1$)** | 576.44 Hz | 0.62 Hz | 575.32 Hz | 576.41 Hz | 577.74 Hz | $\ge 100.0	ext{ Hz}$ |
| **Tensão de Pico ($3\sigma$)** | 186.57 MPa | 2.89 MPa | 180.85 MPa | 186.58 MPa | 192.27 MPa | $\le 242.9	ext{ MPa}$ |
| **Margem Última ($MS_{\text{ult}}$)** | +0.302 | 0.020 | +0.263 | +0.302 | +0.343 | $> 0.00$ |
| **Aceleração RMS Payload** | 2.89 G$_{\text{rms}}$ | 0.028 G$_{\text{rms}}$ | 2.85 G$_{\text{rms}}$ | 2.89 G$_{\text{rms}}$ | 2.96 G$_{\text{rms}}$ | $< 14.1	ext{ G}_{\text{rms}}$ |
| **Transmissibilidade ($T$)** | 0.205 | 0.002 | 0.202 | 0.205 | 0.210 | $< 1.00$ ($-13.8	ext{ dB}$) |
| **Dano de Fadiga Steinberg ($D$)**| 0.098 | 0.010 | 0.079 | 0.097 | 0.119 | $\le 0.250$ |

---

## 3. Probabilidades de Qualificação de Voo (NASA GSFC-STD-7000A)

1. **Desacoplamento do Lançador:** $\mathbf{P(f_1 \ge 100.0	ext{ Hz}) = 100.0\%}$
2. **Integridade Estrutural Última:** $\mathbf{P(MS_{\text{ult}} > 0) = 100.0\%}$
3. **Resistência à Fadiga Aleatória:** $\mathbf{P(D \le 0.25) = 100.0\%}$

### Conclusão
Mesmo sob o pior cenário estocástico a 97.5% de confiança, a estrutura metamaterial auxética preserva atenuação de vibração de quase 80% e cumpre integralmente todos os requisitos de segurança de voo da NASA.
