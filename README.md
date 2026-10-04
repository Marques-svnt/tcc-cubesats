# CubeSat 1U: Otimização de Volume e Geometria para Maximização de Desempenho Estrutural e Funcional

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Standard: NASA GEVS](https://img.shields.io/badge/Norma-NASA%20GSFC--STD--7000A-red.svg)](https://standards.nasa.gov/)
[![Instituição: UESC](https://img.shields.io/badge/Institui%C3%A7%C3%A3o-UESC%202026%2F2027-green.svg)](http://www.uesc.br/)

Repositório oficial de pesquisa, modelagem computacional e síntese estrutural do Trabalho de Conclusão de Curso (TCC) em Engenharia Mecânica da Universidade Estadual de Santa Cruz (UESC).

* **Autor:** Gabriel Marques de Andrade (`marques.svnt.002@gmail.com`)
* **Orientadora:** Prof.ª Dr.ª Nila Cecília de Faria Lopes Medeiros
* **Janela do Projeto:** Outubro de 2026 a Maio de 2027

---

## 📌 Visão Geral do Projeto

Este projeto desenvolve uma metodologia preditiva de otimização topológica e geométrica para o chassi de um nanossatélite **CubeSat 1U**, substituindo o núcleo estrutural convencional por metamateriais celulares auxéticos de densidade funcionalmente graduada (*Functionally Graded Lattices* - FGL), preservando os trilhos de contato monolíticos e maciços ($8.5 \times 8.5\text{ mm}$) para interface cinemática com o dispensador **P-POD**.

O chassi é qualificado sob o espectro dinâmico da norma **NASA GSFC-STD-7000A (GEVS)**, com transição escalonada do modelo analógico de prototipagem em PLA (FDM) para a liga metálica aeroespacial de voo AlSi10Mg (LPBF).

```
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
    - Anisotropia (0°/45°/90°)         - Homogeneização RVE
    - Ensaios ASTM D638/D695           - Vibração Randômica 14.1 Grms
    - Validação de Bancada             - Fadiga de Steinberg (D <= 0.25)
```

---

## 🚀 Requisitos e Critérios de Qualificação (NASA GEVS)

1. **Rigidez Fundamental:** Primeira frequência natural $f_1 \ge 100.0\text{ Hz}$ para evitar acoplamento dinâmico com o lançador.
2. **Perfil Espectral de Vibração Aleatória (PSD):** $14.1\text{ G}_{\text{rms}}$ aplicado sequencialmente nos 3 eixos ortogonais ($X, Y, Z$) por $120\text{ s/eixo}$ na faixa de $20\text{ a }2000\text{ Hz}$.
3. **Margem de Segurança Estocástica:** $MS_{\text{yield}} = (\sigma_{\text{adm}} / \sigma_{3\sigma}) - 1 > 0.0$ com fator de segurança da NASA $FS_{\text{yield}} = 1.25$.
4. **Dano Acumulado de Fadiga (Steinberg):** $D \le 0.25$ pela regra linear de Palmgren-Miner combinada ao método de 3 bandas gaussianas (fator de vida $4\times$).

---

## 📂 Arquitetura do Repositório

```text
.
├── configs/                  # Especificações técnicas e parâmetros de projeto
│   ├── gevs_specs.yaml       # Espectro PSD NASA GSFC-STD-7000A e limites dinâmicos
│   ├── material_alsi10mg.yaml# Propriedades da liga metálica de voo LPBF
│   ├── material_pla.yaml     # Propriedades analógicas do PLA FDM (0°/45°/90°)
│   └── optimization_bounds.yaml # Espaço de projeto da célula reentrante e DfAM
├── mcp_servers/              # Conectores com solvers e CAD (SolidWorks/Ansys MAPDL)
│   ├── ansys_mcp.py          # Automação batch de elementos finitos
│   ├── cubesat_mcp.py        # Servidor unificado MCP com telemetria e fallback
│   └── solidworks_mcp.py     # Geração paramétrica de geometrias
├── src/                      # Código-fonte principal do ecossistema
│   ├── analysis/             # Mecânica celular, Gibson-Ashby e fadiga de Steinberg
│   ├── core/                 # Geometria reentrante, física e controle de estado
│   └── neural/               # Amostragem DoE (LHS) e modelos de resposta substituta
├── tests/                    # Suíte de testes automatizados com pytest
├── AGENTS.md                 # Governança técnica multiagente e limites normativos
├── .gitignore                # Proteção contra artefatos CAD, CAE e arquivos volumosos
├── .gitattributes           # Normalização de line endings e formatos binários
└── README.md                 # Este documento
```

---

## 🛠️ Como Executar os Testes e Simulações

### 1. Clonar e Configurar o Ambiente
```bash
# Criar e ativar ambiente virtual
python -m venv .venv
# No Windows PowerShell:
.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt  # ou instalar pytest, pyyaml, numpy, scipy
```

### 2. Rodar a Suíte de Testes Automatizada
```bash
python -m pytest tests/ -v
```

---

## 📅 Cronograma de Sprints Revisado (10/2026 - 05/2027)

* **Sprint 1 (Out/26):** Engenharia de Sistemas, Espaço de Projeto DfAM & Pipeline DoE Paramétrico (LHS).
* **Sprint 2 (Nov/26):** Automação FEA de Alta Fidelidade (Ansys MAPDL) & Geração do Dataset Base.
* **Sprint 3 (Dez/26):** Desenvolvimento do Modelo Substituto Neural Guiado por Física (Physics-Guided ResNet em PyTorch).
* **Sprint 4 (Jan/27):** Arquitetura Multi-Agente com LangGraph & Orquestração de Engenharia Concorrente.
* **Sprint 5 (Fev/27):** Otimização Multiobjetivo (NSGA-II) & Síntese da Frente de Pareto do Chassi 1U.
* **Sprint 6 (Mar/27):** Auditoria em Alta Fidelidade no Ansys, Análise de Fadiga de Steinberg & Benchmark Estrutural.
* **Sprint 7 (Abr/27):** Redação Integral da Monografia do TCC e Revisão Crítica com a Orientadora.
* **Sprint 8 (Mai/27):** Fechamento Textual ABNT/UESC, Slides Técnicos, Ensaio Pré-Banca e Defesa Oficial.
