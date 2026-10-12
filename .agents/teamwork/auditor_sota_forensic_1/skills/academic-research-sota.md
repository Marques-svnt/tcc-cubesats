---
name: academic-research-sota
description: Pesquisa acadêmica estruturada e avaliação de originalidade. Executa busca sistemática de literatura (arXiv, Crossref, Semantic Scholar, OpenAlex, Google Scholar), snowballing bidirecional, mapeamento do Estado da Arte (SOTA), síntese de matriz taxonômica comparativa e avaliação formal do Grau de Inovação (Delta de Novidade, Taxonomia de Nickerson e TRL).
---

# Academic Research & State-of-the-Art (SOTA) Mapping Runbook

Diretrizes metodológicas para condução de pesquisa bibliográfica sistemática, mapeamento exaustivo do Estado da Arte (SOTA), identificação de artigos correlatos/baselines e mensuração formal do Grau de Inovação científica.

---

## 1. Princípios e Persona

Esta skill opera sob a ótica de um **Diretor de Pesquisa Acadêmica & Especialista em Cienciometria (Padrão Qualis A1 / Q1)**. 

### Objetivos Centrais
1. **Mapear a Fronteira do Conhecimento**: Localizar os marcos seminais históricos e os artigos mais recentes da fronteira de pesquisa.
2. **Evitar Vieses de Confirmação e Baselines Frágeis**: Garantir que o trabalho seja comparado contra os competidores mais fortes da literatura, e não contra baselines simplórios (*straw-man baselines*).
3. **Quantificar o Delta de Novidade ($\Delta_{\text{nov}}$)**: Isolar com clareza matemática e metodológica exatamente o que a pesquisa proposta acrescenta em relação a tudo o que já foi publicado.

---

## 2. Quando Usar

- Início ou estruturação de projetos de pesquisa (TCC, Dissertação de Mestrado, Tese de Doutorado, Projetos FAPESP/CNPq).
- Escrita ou revisão da Seção de Trabalhos Relacionados (*Related Work* / *State of the Art*) de um artigo para periódicos Q1.
- Identificação dos 3 a 5 baselines que devem compor a seção experimental de um paper.
- Avaliação crítica do potencial de inovação e patenteabilidade de um método antes do desenvolvimento prático.

### Quando NÃO Usar
- Para auditar o código implementado ou a redação final de um artigo pronto $\rightarrow$ use `academic-peer-reviewer` ou `doctoral-auditor`.
- Para formatar tabelas e referências em BibTeX $\rightarrow$ use `academic-paper-latex`.
- Para geração de figuras e gráficos $\rightarrow$ use `academic-figures-plots`.

---

## 3. Protocolo de Pesquisa em 4 Fases

```mermaid
flowchart TD
    P1["Fase 1: Engenharia de Busca & Descoberta Multi-Base"] --> P2["Fase 2: Snowballing Bidirecional (Backward & Forward)"]
    P2 --> P3["Fase 3: Mapeamento do Estado da Arte (Matriz Taxonômica)"]
    P3 --> P4["Fase 4: Avaliação Formal do Grau de Inovação (Delta de Novidade & TRL)"]
    P4 --> Output["Relatório Consolidado (SOTA + Novelty Assessment)"]
```

---

### Fase 1: Engenharia de Busca & Descoberta Multi-Base

1. **Formulação Booleana Estruturada**:
   - Decompor o problema em facetas: `[Domínio de Aplicação] AND [Técnica/Método Central] AND [Métrica de Desempenho ou Restrição]`.
   - Exemplo: `("process control" OR "CSTR") AND ("model predictive control" OR "PINN" OR "physics-informed") AND ("disturbance rejection" OR "stability guarantees")`.
2. **Consulta a Múltiplas Fontes Primárias**:
   - Ferramentas web e APIs acadêmicas: arXiv, Semantic Scholar, Crossref, OpenAlex, DBLP e Google Scholar.
   - Extrair: Título, Autores, Ano, Venue (Periódico/Conferência), DOI, Citações e Resumo.

---

### Fase 2: Snowballing Bidirecional

Nenhum levantamento bibliográfico é completo apenas com palavras-chave. Deve-se aplicar **Snowballing** (Wohlin, 2014):

1. **Backward Snowballing**:
   - A partir dos 3 artigos mais citados e influentes encontrados, inspecionar exaustivamente a lista de referências bibliográficas desses artigos para identificar os fundamentos teóricos originais.
2. **Forward Snowballing**:
   - Utilizar as ferramentas de busca para identificar **quem citou** os artigos seminais nos últimos 24 a 36 meses.
   - Isso garante a captura das variantes mais recentes, melhorias incrementais e contrapontos da literatura contemporânea.

---

### Fase 3: Mapeamento do Estado da Arte (Matriz Taxonômica)

Organizar os artigos encontrados em uma **Matriz Comparativa de SOTA**. Os trabalhos devem ser julgados sob critérios objetivos:

| Dimensão de Análise | O que Avaliar |
|---|---|
| **Premissas e Hipóteses** | O método assume linearidade? Conhecimento exato de parâmetros? Dados estacionários? |
| **Abordagem Algorítmica** | Analítica, Baseada em Otimização (MILP/NLP), Heurística, Deep Learning puro ou Híbrida? |
| **Garantias Teóricas** | Há prova formal de convergência, estabilidade de Lyapunov ou limitantes de erro? |
| **Complexidade Computacional** | Complexidade assintótica $\mathcal{O}(n)$ em treino e inferência/execução em tempo real. |
| **Datasets e Benchmarks** | Usou datasets sintéticos simplificados ou dados industriais/públicos consolidados? |
| **Limitações Declaradas** | Onde o método falha ou exige relaxamento de restrições? |

A partir da matriz, selecionar obrigatoriamente os **3 a 5 baselines competitivos** que representam as melhores soluções atuais para o problema.

---

### Fase 4: Avaliação Formal do Grau de Inovação

A inovação deve ser decomposta em 3 vetores ortogonais:

$$
\Delta_{\text{nov}} = \left\{ \Delta_{\text{metodológico}}, \, \Delta_{\text{teórico}}, \, \Delta_{\text{empírico}} \right\}
$$

1. **Delta Metodológico / Algorítmico ($\Delta_{\text{metodológico}}$)**:
   - Proposta de nova formulação matemática, novo operador, nova função de perda, nova combinação híbrida de paradigmas (ex: fusão de equações diferenciais com redes neurais).
2. **Delta Teórico ($\Delta_{\text{teórico}}$)**:
   - Demonstração de novas propriedades matemáticas, relaxamento de premissas restritivas anteriores ou novas cotas de erro assintótico.
3. **Delta Empírico / Aplicação ($\Delta_{\text{empírico}}$)**:
   - Resolução de problema prático em escala inédita, superação de baselines consolidados em métricas chave (IAE, TV, MASE, etc.) com testes de significância estatística.

### Enquadramento na Taxonomia de Inovação
- **Incremental**: Ajuste de hiperparâmetros ou aplicação direta de método existente em novo caso sem alteração estrutural. *(Risco alto de rejeição em periódicos Q1 se não houver ganho extraordinário).*
- **Modular / Adaptativa**: Substituição de um módulo específico por uma técnica moderna mantendo a arquitetura geral. *(Aceitável em bons periódicos se o ganho for substancial).*
- **Arquitetural / Sistêmica**: Reconfiguração da forma como os módulos interagem (ex: união de controle preditivo com aprendizado por reforço seguro). *(Excelente recepção em Q1/A1).*
- **Radical / Disruptiva**: Introdução de novo paradigma teórico que invalida ou substitui as abordagens anteriores.

### Nível de Maturidade Tecnológica (TRL)
Avaliar a pesquisa na escala TRL (1 a 9):
- **TRL 1-2**: Princípios básicos observados / Formulação de conceito.
- **TRL 3-4**: Prova de conceito analítica e experimental em bancada/simulação.
- **TRL 5-6**: Validação em ambiente simulado industrial ou planta piloto.
- **TRL 7-9**: Sistema demonstrado e operacional em ambiente real.

---

## 4. Estrutura dos Relatórios Emitidos

Ao executar a skill, gerar relatórios formais baseados nos templates:
1. **Relatório de Mapeamento do Estado da Arte**: [`templates/sota_mapping_report.md`](file:///home/marques/.gemini/config/plugins/engineering-suite/skills/academic-research-sota/templates/sota_mapping_report.md)
2. **Relatório de Avaliação do Grau de Inovação**: [`templates/novelty_assessment_report.md`](file:///home/marques/.gemini/config/plugins/engineering-suite/skills/academic-research-sota/templates/novelty_assessment_report.md)

Sincronizar os relatórios gerados com o Obsidian Vault através da skill [`obsidian-sync`](file:///home/marques/.gemini/config/plugins/engineering-suite/skills/obsidian-sync/SKILL.md).
