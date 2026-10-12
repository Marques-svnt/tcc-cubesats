# Mapeamento Oficial de Templates e Diretrizes dos Entregáveis

Este documento consolida o mapeamento de todos os templates, normas e formatações adotadas para os entregáveis finais da pesquisa:
**Projeto:** Otimização Estrutural de Chassi CubeSat 1U com Metamateriais Auxéticos em AlSi10Mg sob Cargas Dinâmicas de Lançamento  
**Instituição:** Universidade Estadual de Santa Cruz (UESC 2026)  
**Autor:** Gabriel Marques de Andrade  

---

## 1. Matriz de Entregáveis e Templates Oficiais

| Entregável | Objetivo & Público-Alvo | Template Oficial | Localização no Projeto | Status de Compilação |
| :--- | :--- | :--- | :--- | :---: |
| **Linha 1: Tese Exaustiva** | Registro enciclopédico de toda a esteira científica (114 páginas). | `ppgmc-uesc.cls` (v5.0, UESC) + `macros-cubesat.tex` | `Entregas-finais/01-Tese-Exaustiva/` | **Compilado (114 pp.)** |
| **Linha 2: TCC Graduação UESC** | Monografia concisa e pedagógica de graduação (52 páginas). | `ppgmc-uesc.cls` (Colegiado Eng. Mecânica UESC) | `Entregas-finais/03-TCC-Graduacao-UESC/` | **Compilado (52 pp.)** |
| **Linha 3.1: Artigo M&D** | Manuscrito internacional (DfAM & Otimização de Metamateriais). | `elsarticle.cls` (*Materials & Design*, Elsevier Q1/A1) | `Entregas-finais/02-Artigos-Cientificos/01-Materials-and-Design-Elsevier/` | **Compilado com BibTeX** |
| **Linha 3.2: Artigo AST** | Manuscrito internacional (Dinâmica de Lançamento & NASA GEVS). | `elsarticle.cls` (*Aerospace Science & Tech*, Elsevier Q1/A1) | `Entregas-finais/02-Artigos-Cientificos/02-Aerospace-Science-and-Technology-Elsevier/` | **Compilado com BibTeX** |
| **Linha 3.3: Artigo EAAI** | Manuscrito internacional (Physics-Guided ResNet & IA). | `elsarticle.cls` (*Eng. Appl. of AI*, Elsevier Q1/A1) | `Entregas-finais/02-Artigos-Cientificos/03-Engineering-Applications-of-AI-Elsevier/` | **Compilado com BibTeX** |
| **Linha 4: SpringerBriefs** | Monografia internacional de alto impacto (Springer Nature). | `SNmono.cls` (v6.00 / `svmono.cls`) + `spphys.bst` | `Entregas-finais/04-Monografia-SpringerBriefs/` | **Compilado (142 pp.) & Auditado (94.4/100 A1)** |

---

## 2. Detalhamento dos Templates por Eixo

### Eixo A: Monografias Acadêmicas (UESC / ABNT)
- **Classe:** `ppgmc-uesc.cls` (baseada no pacote `abntex2`).
- **Normas ABNT Atendidas:**
  - NBR 14724 (Trabalhos acadêmicos e estrutura);
  - NBR 6023 (Referências bibliográficas);
  - NBR 6028 (Resumo e Abstract);
  - NBR 6024 (Numeração progressiva das seções).
- **Tipografia e Pacotes:**
  - Fonte: Times New Roman (`ptm`) em corpo 12 pt com entrelinha 1,5;
  - Tabelas: `booktabs` (sem linhas verticais, com réguas de topo, meio e fundo);
  - Unidades: `siunitx` com formatação rigorosa (`\SI{...}{...}`);
  - Matemática: `amsmath`, `amssymb`, `mathtools`.

### Eixo B: Periódicos Científicos Internacionais (Elsevier / Qualis A1)
- **Classe:** `elsarticle.cls` (versão 3.3 oficial da Elsevier).
- **Opções de Layout:** `\documentclass[preprint,12pt,3p]{elsarticle}` (padrão de submissão para revisão por pares).
- **Estilo Bibliográfico:** `elsarticle-num.bst` (citações numéricas em ordem de aparição no texto).
- **Seções Mandatórias da Elsevier:**
  - `frontmatter` estruturado com filiações, autor correspondente e e-mails;
  - `graphicalabstract`: figura de alto impacto em destaque;
  - `highlights`: 3 a 5 tópicos de no máximo 85 caracteres resumindo a inovação;
  - `Declaration of Competing Interest` e `CRediT authorship contribution statement`.

### Eixo C: Monografia Internacional (Springer Nature / SpringerBriefs)
- **Classe:** `SNmono.cls` (versão 6.00 unificada oficial da Springer Nature, com retrocompatibilidade `svmono.cls`).
- **Série Alvo:** *SpringerBriefs in Applied Sciences and Technology (Aerospace Technology)*.
- **Opções de Layout:** `\documentclass[graybox,envcountchap,sectrefs]{SNmono}`.
- **Dimensões e Mancha Gráfica:** Trim size $155 \times 235\text{ mm}$, largura útil de $118\text{ mm}$ (proibido o uso de `geometry`).
- **Tipografia e Pacotes:**
  - Fontes: `newtxtext` e `newtxmath` (com fallback robusto para `mathptmx`);
  - Tabelas: `booktabs` e `siunitx` com formatação rigorosa;
  - Destaques: ambiente nativo `svgraybox`;
  - Acessibilidade: comando `\Description{...}` para alt-text obrigatório em todas as figuras;
  - Estilo Bibliográfico: `spphys.bst` (Springer Physics & Engineering, citações numéricas com DOI).

---

## 3. Diretrizes de Adequação do Orientador Incorporadas

O documento [`Considerações-TCC-Gabriel.pdf`](file:///home/marques/Downloads/Considerações-TCC-Gabriel.pdf) forneceu direcionamentos pedagógicos essenciais, incorporados no TCC da UESC:
1. **Problema de Engenharia Direto:** Substituição de perguntas longas e multifacetadas por uma formulação clara sobre a redução de massa e mitigação de vibração da carga útil;
2. **Dimensionamento Realista de Graduação:** Delimitação do escopo para 12 meses de dedicação, organizando o texto em seis partes sequenciais e compreensíveis;
3. **Padronização Linguística:** Apresentação prévia dos termos técnicos em português antes das siglas consagradas em inglês (ex.: *Projeto para Manufatura Aditiva — DfAM*, *Fusão em Leito de Pó por Laser — L-PBF*);
4. **Demonstração do Caminho Computacional:** Valorização dos procedimentos operacionais (geometria 3D, elementos finitos Tet10, condições de contorno e parâmetros no Code_Aster e CalculiX) em vez de apenas exibir números finais;
5. **Legibilidade das Figuras:** Diagramas com fontes nítidas, eixos legíveis e legendas autoexplicativas.
