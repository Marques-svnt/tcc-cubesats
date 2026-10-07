# CubeSat 1U: Otimização de Volume e Geometria para Maximização de Desempenho Estrutural e Funcional

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Standard: NASA GEVS](https://img.shields.io/badge/Norma-NASA%20GSFC--STD--7000A-red.svg)](https://standards.nasa.gov/)
[![Instituição: UESC](https://img.shields.io/badge/Institui%C3%A7%C3%A3o-UESC%202026-green.svg)](http://www.uesc.br/)
[![Tests: 67 Passing](https://img.shields.io/badge/Tests-67%20Passing-brightgreen.svg)]()

Repositório oficial de pesquisa, modelagem computacional, simulações mecânicas multifísicas e síntese da monografia do Trabalho de Conclusão de Curso (TCC) em Engenharia Mecânica da Universidade Estadual de Santa Cruz (UESC).

* **Autor:** Gabriel Marques de Andrade (`marques.svnt.002@gmail.com`)
* **Orientadora:** Prof.ª Dr.ª Nila Cecília de Faria Lopes Medeiros
* **Monografia Final Oficial (PDF):** [📄 monografia_tcc_final.pdf](monografia_tcc_final.pdf)

---

## 📌 Visão Geral do Projeto

Este projeto desenvolve uma metodologia preditiva de otimização topológica e geométrica para o chassi de um nanossatélite **CubeSat 1U**, substituindo o núcleo estrutural convencional por metamateriais celulares auxéticos de densidade funcionalmente graduada (*Functionally Graded Lattices* - FGL), preservando os quatro trilhos de contato monolíticos e maciços ($8.5 \times 8.5\text{ mm}$) para interface cinemática com o dispensador orbital **P-POD**.

O chassi é rigorosamente qualificado sob o espectro dinâmico da norma **NASA GSFC-STD-7000A (GEVS)**, com transição escalonada do modelo analógico de prototipagem em PLA (FDM) para a liga metálica aeroespacial de voo AlSi10Mg (LPBF).

```text
          +-------------------------------------------+
          |         CHASSI CUBESAT 1U (100x100x113.5 mm)        |
          +-------------------------------------------+
          |  Trilhos Maciços P-POD (8.5 x 8.5 mm)      |
          |  Núcleo Celular Auxético (Reentrante FGL) |
          |  Fixação Interna PC/104 para Payload      |
          +-------------------------------------------+
                                |
             +------------------+------------------+
             |                                     |
    [Prototipagem FDM PLA]             [Modelo de Voo LPBF AlSi10Mg]
    - Anisotropia (0°/45°/90°)         - Homogeneização Gibson-Ashby
    - Validação Geométrica DfAM        - Vibração Randômica 14.1 Grms
    - Ensaios de Bancada               - Fadiga de Steinberg (D <= 0.25)
```

---

## 🌿 Organização das Branches do Repositório (Etapas da Monografia)

Para garantir rastreabilidade acadêmica completa, cada estágio de evolução da monografia possui sua própria branch dedicada no repositório:

| Branch | Etapa / Escopo | Principais Artefatos |
| :--- | :--- | :--- |
| `main` | **Produção Oficial:** Código bruto unificado + versão final da monografia formatada no padrão UESC + PDF final compilado na raiz | `monografia_tcc_final.pdf`, `monografia/`, `src/`, `tests/` |
| [`monografia/etapa-05-uesc-final`](https://github.com/Marques-svnt/tcc-cubesats/tree/monografia/etapa-05-uesc-final) | **Etapa 5 (UESC Final):** Adequação integral ao template oficial da Pós-Graduação/TCC da UESC (`ppgmc-uesc.cls`) com elementos pré-textuais, textuais, pós-textuais e PDF oficial | `monografia_v5/Main.tex`, `monografia_v5/Main.pdf` |
| [`monografia/etapa-04-revisao-canonica`](https://github.com/Marques-svnt/tcc-cubesats/tree/monografia/etapa-04-revisao-canonica) | **Etapa 4 (Alinhamento Canônico):** Harmonização dos parâmetros físicos (512 Hz, 184 MPa), inserção de Ermurat et al. (2020), Pareto e Bloch-Floquet | `monografia_v4/main.tex`, `monografia_v4/main.pdf` |
| [`monografia/etapa-03-overleaf-modular`](https://github.com/Marques-svnt/tcc-cubesats/tree/monografia/etapa-03-overleaf-modular) | **Etapa 3 (Overleaf Modular):** Modularização do texto por capítulos e preâmbulo LaTeX de alta fidelidade | `monografia_v3/main.tex`, `monografia_v3/main.pdf` |
| [`monografia/etapa-02-markdown-expandido`](https://github.com/Marques-svnt/tcc-cubesats/tree/monografia/etapa-02-markdown-expandido) | **Etapa 2 (Markdown Analítico):** Versão hiperdetalhada com deduções analíticas completas, equações constitutivas e formulação de IA (~1 MB) | `TCC - Gabriel Marques de Andrade - v2.md` |
| [`monografia/etapa-01-latex-inicial`](https://github.com/Marques-svnt/tcc-cubesats/tree/monografia/etapa-01-latex-inicial) | **Etapa 1 (LaTeX Inicial):** Primeira versão compilada em documento LaTeX monolítico ao fim do Sprint 06 | `monografia_tcc.tex`, `monografia_tcc.pdf` |

*Branches de sprints técnicos (`sprint-01` a `sprint-06`) também estão preservadas no histórico para auditoria dos modelos neurais e formulações estruturais.*

---

## 📂 Arquitetura da Branch Principal (`main`)

```text
.
├── monografia_tcc_final.pdf  # PDF final compilado da monografia (Padrão UESC PPGMC)
├── monografia/               # Fonte LaTeX oficial completo no padrão UESC (v5)
│   ├── 01-elementos-pre-textuais/  # Capa, folha de aprovação, resumos, listas
│   ├── 02-elementos-textuais/      # Capítulos 1 a 6 (Introdução a Conclusão)
│   ├── 03-elementos-pos-textuais/  # Referências ABNT NBR 6023 e refbase.bib
│   ├── 04-figuras/                 # Figuras de alta resolução (300 DPI)
│   ├── pacotes/                    # Classe ppgmc-uesc.cls e macros-cubesat.tex
│   ├── Main.tex                    # Arquivo mestre de compilação
│   ├── Main.pdf                    # PDF compilado da monografia
│   └── template_overleaf/          # Template limpo original da UESC
├── src/                      # Código-fonte completo de simulação e IA
│   ├── agents/               # Orquestrador multiagente e nós especialistas
│   ├── analysis/             # Mecânica celular, Gibson-Ashby, Steinberg, Bloch-Floquet
│   ├── cad/                  # Modelagem paramétrica DfAM e exportação CAD (CadQuery)
│   ├── core/                 # Geometria auxética reentrante e física
│   ├── mesh/                 # Geração de malhas de elementos finitos (Gmsh)
│   ├── neural/               # Amostragem DoE (LHS) e Physics-Guided ResNet
│   ├── optimization/         # Algoritmo genético NSGA-II e seleção TOPSIS
│   └── pipeline/             # Pipeline aberta de simulação unificada
├── tests/                    # 67 testes automatizados com 100% de aprovação (pytest)
├── configs/                  # Especificações NASA GEVS e arquivos YAML de materiais
├── data/                     # Datasets DoE, pontos de Pareto e scripts de solver
├── models/                   # Pesos treinados (.pt), escalonadores (.json) e CAD (.step, .stl)
├── reports/                  # Apresentação da banca (.pptx, .pdf), visualizador 3D Three.js
├── scripts/                  # Scripts de exportação 3D, geração de gráficos e slides
├── mcp_servers/              # Conectores com servidores MCP (SolidWorks / Ansys)
├── AGENTS.md                 # Governança técnica multiagente e limites de qualificação
├── PARAMETROS_CANONICOS.md   # Tabela canônica de parâmetros físicos e de voo
├── pyproject.toml            # Configurações do projeto e do pytest
├── requirements.txt          # Dependências do ecossistema Python
└── README.md                 # Este documento
```

---

## 🚀 Requisitos e Critérios de Qualificação (NASA GEVS)

1. **Rigidez Fundamental do Lançador:** $f_1 \ge 100.0\text{ Hz}$ (Chassi nominal auxético otimizado atinge $512.4\text{ Hz}$).
2. **Perfil Espectral de Vibração Aleatória (PSD):** $14.1\text{ G}_{\text{rms}}$ aplicado sequencialmente nos 3 eixos ortogonais ($X, Y, Z$) por $120\text{ s/eixo}$ na faixa de $20\text{ a }2000\text{ Hz}$.
3. **Margem de Segurança Estocástica:** $MS_{\text{yield}} = (\sigma_{\text{adm}} / \sigma_{3\sigma}) - 1 > 0.0$ com tensão admissível corrigida $\sigma_{\text{adm}} = 184.0\text{ MPa}$ ($FS_{\text{yield}} = 1.25$).
4. **Dano Acumulado de Fadiga (Steinberg):** $D \le 0.25$ pela regra linear de Palmgren-Miner combinada ao método de 3 bandas gaussianas (fator de segurança de vida de $4\times$).

---

## 🛠️ Como Executar os Testes e Simulações

### 1. Configurar o Ambiente Virtual
```bash
# Criar e ativar o ambiente
python -m venv .venv

# No Windows PowerShell:
.venv\Scripts\Activate.ps1

# Instalar dependências completas
pip install -r requirements.txt
```

### 2. Executar a Suíte de Testes Automatizada (67 Testes)
```bash
python -m pytest tests/ -v
```

### 3. Executar o Pipeline Completo de Otimização e Síntese
```bash
python run_pipeline.py
```

### 4. Abrir o Visualizador 3D Interativo do CubeSat 1U
Abra diretamente no navegador o arquivo:
`reports/cad_viewer/cubesat_1u_cad_viewer.html`

---

## 📜 Licença e Citações

Este projeto está licenciado sob a Licença MIT. Para citações acadêmicas da monografia:

```bibtex
@monography{marques2026cubesat,
  author    = {Gabriel Marques de Andrade},
  title     = {Otimiza{\c{c}}{\~a}o de Volume e Geometria para Maximiza{\c{c}}{\~a}o de Desempenho Estrutural e Funcional de um CubeSat 1U em Baixa {\'O}rbita},
  school    = {Universidade Estadual de Santa Cruz (UESC)},
  year      = {2026},
  type      = {Trabalho de Conclus{\~a}o de Curso (Engenharia Mec{\^a}nica)},
  address   = {Ilh{\'e}us, BA, Brasil}
}
```
