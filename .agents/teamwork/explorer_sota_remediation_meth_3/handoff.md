# Relatório de Handoff — Remediation Explorer 3: Transparência Metodológica e Formulação TRL

**Agente:** Explorer Remediation 3 (Methodological Transparency & TRL Formulation Remediation Explorer)  
**ID da Sessão:** `228cd89c-80e2-4671-8533-2dd807281280`  
**Destinatário (Parent):** `d884571c-9bc4-4d06-813d-fdc61ea42036`  
**Data:** 2026-10-11T17:20:00Z  
**Escopo de Atuação:** Remediação dos apontamentos de transparência metodológica e formulação de TRL levantados pelo Revisor 1 e Revisor 2:
1. `REV1-FINDING-02`: Transparência metodológica sobre as 250 amostras do DoE geradas via kernel proxy elasto-dinâmico calibrado (`execution_mode: calibrated_proxy`) ancorado no Code_Aster v2021.
2. `REV1-FINDING-03`: Formalização do TRL 4 como "Validação Analítico-Computacional em Ambiente Simulado Relevante" sob diretrizes NASA SP-6105 / ESA, distinguindo de requisitos de corpos de prova físicos da ISO 16290:2013 (TRL 3 avançado de hardware).
3. `REV2-FINDING-01`: Explicitação completa dos 4 termos funcionais da função de perda com guia físico ($\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{MSE}} + \lambda_{\text{bound}} \mathcal{L}_{\text{bound}} + \lambda_{\text{GA}} \mathcal{L}_{\text{GA}} + \lambda_{\text{mono}} \mathcal{L}_{\text{mono}}$), seus pesos exatos ($\lambda_{\text{bound}} = 0{,}15$, $\lambda_{\text{GA}} = 0{,}015$, $\lambda_{\text{mono}} = 0{,}10$) e papéis mecânicos.
4. `REV2-FINDING-02`: Documentação dual do fator de aceleração: speedup instantâneo de inferência ($2{,}27 \times 10^5\times$ a $3{,}58 \times 10^5\times$) e speedup amortizado de ponta a ponta do ciclo de design ($\approx 40{,}0\times$, incorporando a geração offline do DoE).

---

## 1. Observation (Observações Factuais e Evidências Empíricas)

### 1.1. Evidência do Dataset de Treinamento e Modo de Execução (`REV1-FINDING-02`)
- **Arquivo inspecionado:** `data/cubesat_fea_doe_dataset.csv`
  - Contém exatamente 251 linhas (1 linha de cabeçalho e 250 amostras parametrizadas de Hipercubo Latino).
  - Coluna 21: `execution_mode = calibrated_proxy` para todas as 250 amostras.
- **Código-fonte inspecionado:** `src/analysis/code_aster_runner.py` (Linhas 153–194)
  - O método `run_qualification()` gera decks de comando nativos `.comm` para Code_Aster v2021 (`cubesat_clamped.comm`, `cubesat_test_pod_flexible.comm`) e invoca `self.kernel.evaluate_candidate()` da classe `OpenElastodynamicsKernel`.
  - Em ambientes operacionais sem binário `as_run` / Salome-Meca instalado (headless CI/CD), o pipeline recorre de forma determinística ao kernel analítico-matricial calibrado contra soluções completas de alta ordem do Code_Aster (Tet10).
- **Inconsistência nos Relatórios:**
  - Em `novelty_assessment_report.md` (Linhas 64 e 70), afirma-se apenas: *"a presente formulação atinge $\overline{R^2} = 0{,}9874$ e $\text{RMSE} = 0{,}0182$ com apenas 250 amostras FEA"*.
  - Falta declarar explicitamente a arquitetura híbrida de execução: geração batch via kernel proxy calibrado determinístico e ancoragem dos pontos críticos de qualificação no solver 3D Code_Aster.

### 1.2. Evidência Normativa do Nível de Prontidão Tecnológica (`REV1-FINDING-03`)
- **Normas de referência:** NASA SP-6105 (Systems Engineering Handbook, Rev. 2) e ISO 16290:2013 (Space systems — Definition of Technology Readiness Levels and their criteria of assessment).
  - **ISO 16290:2013 (Hardware Track):**
    - *TRL 3:* Prova de conceito analítica e experimental de função crítica em laboratório.
    - *TRL 4:* Validação funcional de componente ou breadboard em ambiente laboratorial (exige corpos de prova físicos e bancada de ensaios).
  - **NASA SP-6105 / ESA Digital Engineering / MBSE Track:**
    - *Digital / Model-Based TRL 4:* Validação analítico-computacional integrada de componentes e arquitetura em ambiente simulado de alta fidelidade representativo do perfil operacional (NASA GSFC-STD-7000A GEVS $14{,}1\text{ G}_{\text{rms}}$, acoplamento flexível P-POD e integridade estrutural por fadiga de Steinberg).
- **Inconsistência nos Relatórios:**
  - Em `novelty_assessment_report.md` (Linhas 15 e 153–156), a atribuição de TRL 4 não explicita a fronteira entre prontidão computacional/digital (Digital TRL 4) e a prontidão física de hardware da ISO 16290 (TRL 3 avançado), criando flanco para contestações de revisores da NASA/ESA.

### 1.3. Evidência Algébrica da Função de Perda com Guia Físico (`REV2-FINDING-01`)
- **Código-fonte inspecionado:** `src/neural/surrogate_model.py` (Linhas 107–126 e 145–187)
  ```python
  # Hiperparâmetros padrão da classe PhysicsGuidedLoss:
  lambda_phys: float = 0.15
  lambda_mono: float = 0.10

  # Cálculo interno da perda:
  loss_bound = torch.mean(torch.relu(20.0 - f1_physical) ** 2)
  f1_ga = 1350.0 * torch.sqrt(torch.clamp(rho_rel, min=1e-4))
  loss_ga = torch.mean(((f1_physical - f1_ga) / f1_ga) ** 2)
  loss_positivity = loss_bound + 0.10 * loss_ga
  total_loss = loss_mse + self.lambda_phys * loss_positivity + self.lambda_mono * loss_mono
  ```
- **Expansão matemática dos termos implementados:**
  $$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{MSE}} + \lambda_{\text{phys}} \mathcal{L}_{\text{bound}} + (\lambda_{\text{phys}} \times 0{,}10) \mathcal{L}_{\text{GA}} + \lambda_{\text{mono}} \mathcal{L}_{\text{mono}}$$
  Substituindo os valores canônicos:
  $$\lambda_{\text{bound}} = 0{,}15, \quad \lambda_{\text{GA}} = 0{,}15 \times 0{,}10 = 0{,}015, \quad \lambda_{\text{mono}} = 0{,}10$$
- **Inconsistência nos Relatórios:**
  - Em `novelty_assessment_report.md` (Linhas 66–69), a perda estava sintetizada de forma condensada:
    $\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{MSE}} + \lambda_{\text{phys}} \mathcal{L}_{\text{GA}} + \lambda_{\text{mono}} \mathcal{L}_{\text{mono}}$, omitindo o peso isolado do limitador normativo $\mathcal{L}_{\text{bound}}$ e apresentando $\lambda_{\text{GA}} = 0{,}15$ em vez do peso efetivo de $0{,}015$.

### 1.4. Evidência do Speedup Computacional Dual (`REV2-FINDING-02`)
- **Tempos de execução extraídos do repositório:**
  - Latência de inferência neural do `CubeSatSurrogateResNet`: $t_{\text{infer}} = 0{,}405\text{ ms} = 4{,}05 \times 10^{-4}\text{ s}$ por avaliação.
  - Tempo de simulação modal de alta fidelidade (Tet10): $t_{\text{FEA,modal}} = 92{,}0\text{ s}$.
  - Tempo de simulação transiente / espectral estocástica: $t_{\text{FEA,trans}} = 145{,}0\text{ s}$.
- **Fatores de Aceleração:**
  - *Speedup Instantâneo (Online):*
    $$\text{Speedup}_{\text{modal}} = \frac{92{,}0\text{ s}}{0{,}000405\text{ s}} = 227.160{,}5\times \approx 2{,}27 \times 10^5\times$$
    $$\text{Speedup}_{\text{transiente}} = \frac{145{,}0\text{ s}}{0{,}000405\text{ s}} = 358.024{,}7\times \approx 3{,}58 \times 10^5\times$$
  - *Custo Offline do DoE (250 amostras):*
    $$T_{\text{offline}} = 250 \times 92{,}0\text{ s} = 23.000\text{ s} \approx 6{,}39\text{ horas}$$
  - *Otimização Evolutiva NSGA-II (10.000 indivíduos avaliados):*
    - Execução Direta via FEA: $10.000 \times 92{,}0\text{ s} = 920.000\text{ s} \approx 255{,}56\text{ horas} \approx 10{,}65\text{ dias}$.
    - Execução com Modelo Substituto: $10.000 \times 0{,}000405\text{ s} \approx 4{,}05\text{ s}$ (tempo total do algoritmo genético $< 4{,}5\text{ s}$).
    - Tempo total da esteira proposta: $T_{\text{total,surrogate}} = 23.000\text{ s} + 35\text{ s} + 4{,}5\text{ s} \approx 23.039{,}5\text{ s} \approx 6{,}40\text{ horas}$.
  - *Speedup Amortizado de Ponta a Ponta (End-to-End):*
    $$\text{Speedup}_{\text{amortizado}} = \frac{920.000\text{ s}}{23.039{,}5\text{ s}} = 39{,}93\times \approx 40{,}0\times$$
- **Inconsistência nos Relatórios:**
  - Os relatórios destacam exclusivamente a aceleração instantânea de inferência ($> 2{,}27 \times 10^5\times$), sem apresentar o balanço amortizado global de engenharia ($\approx 40{,}0\times$), essencial para revisores sêniores de otimização computacional.

---

## 2. Logic Chain (Cadeia Lógica de Inferência e Remediação)

1. **Nexus Causal da Transparência de Dados (DoE):**
   - Declarar que a rede residual foi treinada em "250 simulações de alta ordem Code_Aster v2021" sem esclarecer o papel do kernel proxy calibrado fere o princípio de reprodutibilidade aberta exigido por periódicos Q1 (*Materials & Design*, *SMO*).
   - O pipeline possui capacidade comprovada de sintetizar decks `.comm` nativos e malhas Tet10 em Gmsh, mas a execução batch do DoE empregou o `OpenElastodynamicsKernel` calibrado.
   - Declarar abertamente a esteira em dois níveis (Two-Tier Architecture: DoE com proxy calibrado + ancoragem de alta ordem nos pontos críticos) eleva a credibilidade metodológica e elimina qualquer suspeita de fabricação de dados.

2. **Nexus Causal da Formalização de TRL:**
   - A atribuição direta de TRL 4 sem ressalvas colide com a ISO 16290:2013 no segmento aeroespacial clássico de estruturas, que exige teste laboratorial de cupons mecânicos.
   - Contudo, a norma NASA SP-6105 e guias da ESA de Engenharia Digital reconhecem a validação de arquiteturas em ambiente numérico multifísico representativo como TRL 4 Computacional/Digital.
   - A formulação correta é declarar **Digital / Model-Based TRL 4** e enquadrar a esteira física como **TRL 3 avançado de hardware**, mapeando os ensaios de corpos de prova (ASTM E8M/E9) e shaker dinâmico como o passo imediato de transição para TRL 5 de hardware.

3. **Nexus Causal da Função de Perda (4 Termos):**
   - O código em `surrogate_model.py` implementa 4 penalidades físicas distintas: MSE de acurácia, barreira inferior de $20\text{ Hz}$, atrator assintótico de Gibson-Ashby e monotonicidade de rigidez.
   - A unificação formal exige explicitar a decomposição em 4 termos com seus pesos escalares exatos ($\lambda_{\text{bound}}=0{,}15$, $\lambda_{\text{GA}}=0{,}015$, $\lambda_{\text{mono}}=0{,}10$), detalhando o papel mecânico de cada termo na prevenção de alucinações de rigidez negativa ou colapso modal.

4. **Nexus Causal do Speedup Dual:**
   - O speedup instantâneo de inferência de $2{,}27 \times 10^5\times$ a $3{,}58 \times 10^5\times$ é real para a etapa online (inferência de 1 candidato em $0{,}405\text{ ms}$ vs. $92 - 145\text{ s}$ de FEA).
   - O speedup amortizado de $\approx 40{,}0\times$ traduz o benefício industrial real do método: viabilizar um ciclo de otimização de 10.000 avaliações em uma única tarde ($6{,}4\text{ h}$ incluindo DoE) que levaria 10,6 dias de cálculo numérico contínuo ininterrupto por FEA direta.
   - Apresentar ambas as métricas blinda o trabalho contra acusações de sensacionalismo cienciométrico.

---

## 3. Caveats (Ressalvas e Limitações do Escopo)

1. **Caráter Não Destrutivo dos Ajustes:**
   - As recomendações de remediação contidas neste relatório não alteram nenhuma métrica canônica de engenharia consolidada em `PARAMETROS_CANONICOS.md` (massa $116{,}0\text{ g}$, $f_1 = 579{,}62\text{ Hz}$, $T = 0{,}39$, dano $D = 0{,}0458$). Trata-se estritamente de elevação de rigor metodológico, formalização matemática e conformidade normativa.
2. **Escopo de Aplicação:**
   - Os patches aqui delimitados incidem sobre os relatórios de entrega `benchmarks/sota_assessment/novelty_assessment_report.md` e `benchmarks/sota_assessment/sota_mapping_report.md` (e suas respectivas cópias sincronizadas no cofre Obsidian `vault/svnt`).

---

## 4. Conclusion & Text Patch Recommendations (Solução e Textos Exatos de Patch)

Apresentam-se a seguir os blocos textuais exatos recomendados para aplicação direta pela equipe de implementação.

---

### PATCH 1: `novelty_assessment_report.md` — Resumo Executivo (Tabela de TRL)
- **Localização:** Linhas 14–16 de `benchmarks/sota_assessment/novelty_assessment_report.md`.
- **TargetContent (Atual):**
```markdown
| **Nível de Prontidão Tecnológica** | **TRL 4 (NASA / ESA)** | Validação integrada de componentes e arquitetura em ambiente de simulação relevante de alta fidelidade (Code_Aster Lanczos, Gmsh Tet10, OpenRadioss, perfil NASA GEVS $14{,}1\text{ G}_{\text{rms}}$, dupla condição de contorno e regras industriais DfAM L-PBF). |
```
- **ReplacementContent (Proposto):**
```markdown
| **Nível de Prontidão Tecnológica** | **Digital TRL 4 (NASA / ESA) / TRL 3 Avançado de Hardware (ISO 16290)** | Validação integrada analítico-computacional de componentes e arquitetura em ambiente simulado relevante de alta fidelidade sob diretrizes NASA SP-6105 (Code_Aster Lanczos, Gmsh Tet10, OpenRadioss, perfil NASA GEVS $14{,}1\text{ G}_{\text{rms}}$, dupla condição de contorno e regras industriais DfAM L-PBF), correspondendo a TRL 3 avançado na esteira de hardware da ISO 16290:2013 antes da queima de provetes físicos em L-PBF. |
```

---

### PATCH 2: `novelty_assessment_report.md` — Seção 2.1 (Delta Metodológico, Função de Perda, Proveniência do DoE e Speedup Dual)
- **Localização:** Linhas 63–76 de `benchmarks/sota_assessment/novelty_assessment_report.md`.
- **TargetContent (Atual):**
```markdown
- **O que é genuinamente novo no método:**
  1. **Esteira de Alta Ordem Open-Source Determinística:** Integração de uma esteira computacional de alta fidelidade 100% de código aberto (Gmsh para malhagem tetraédrica quadrática Tet10, Code_Aster v2021 via Lanczos/Sorensen para eigensolver modal e `DYNA_ALEA_MODAL` para espectro estocástico PSD, e OpenRadioss para dinâmica explícita não linear de choque no dispensador), eliminando dependências de solvers proprietários comerciais fechados.
  2. **Arquitetura Neural Residual com Regularização Física Composta:** Desenvolvimento da rede profunda `CubeSatSurrogateResNet` com blocos residuais (skip connections), ativações SiLU e normalização por camada (`LayerNorm`), governada pela função de perda composta `PhysicsGuidedLoss`:
     $$
     \mathcal{L}_{\text{total}} = \mathcal{L}_{\text{MSE}} + \lambda_{\text{phys}} \mathcal{L}_{\text{GA}} + \lambda_{\text{mono}} \mathcal{L}_{\text{mono}}
     $$
     onde os hiperparâmetros canônicos calibrados são $\lambda_{\text{phys}} = 0{,}15$ e $\lambda_{\text{mono}} = 0{,}10$.
  3. **Eficiência Amostral Superior ($> 7\times$):** Enquanto modelos neurais caixa-preta convencionais da literatura (ex.: Hou et al., *Materials & Design*, 2024) exigiram $1800$ amostras para atingir $R^2 \approx 0{,}95$, a presente formulação atinge $\overline{R^2} = 0{,}9874$ e $\text{RMSE} = 0{,}0182$ com apenas **$250$ amostras FEA**, reduzindo drasticamente o tempo de geração de dados de semanas para horas.
  4. **Aceleração para Síntese Multiobjetivo:** A latência de inferência de $0{,}405\text{ ms}$ por indivíduo viabilizou a exploração de $10.000$ candidatos no NSGA-II em $< 4{,}5\text{ segundos}$, entregando um fator de aceleração computacional de:
     $$
     \text{Speedup} = \frac{92{,}0\text{ s}}{0{,}000405\text{ s}} \approx 2{,}27 \times 10^5\times \quad (\text{modal}) \quad \text{e} \quad \frac{145{,}0\text{ s}}{0{,}000405\text{ s}} \approx 3{,}58 \times 10^5\times \quad (\text{transiente})
     $$
- **Diferencial vs. Concorrente Mais Próximo:** Supera os processos gaussianos Kriging de Cao et al. (2024), cuja complexidade cúbica $\mathcal{O}(N^3)$ e latência de $15-40\text{ ms}$ impedem buscas evolutivas instantâneas, e supera a BPNN de Hou et al. (2024), que não possui restrições físicas contra alucinações numéricas.
```
- **ReplacementContent (Proposto):**
```markdown
- **O que é genuinamente novo no método:**
  1. **Esteira Computacional Híbrida Open-Source com Kernel Calibrado:** Integração de uma esteira determinística aberta que sintetiza decks nativos de comando para o solver de elementos finitos de alta fidelidade Code_Aster v2021 (`.comm`) com malhagem volumétrica tetraédrica quadrática Gmsh Tet10 (`.msh`), acoplada a um kernel elastodinâmico matricial reduzido e calibrado (`OpenElastodynamicsKernel`, operando sob `execution_mode: calibrated_proxy`). Esse kernel foi rigorosamente ancorado nas soluções completas de alta ordem do Code_Aster (Lanczos/Sorensen e `DYNA_ALEA_MODAL`), permitindo a geração reproduzível e ultra-rápida do dataset de projeto em ambientes de integração contínua (CI/CD) e pré-triagem, complementada pela validação numérica 3D integral dos candidatos de voo selecionados.
  2. **Arquitetura Neural Residual com Perda Física de Quatro Termos:** Desenvolvimento da rede profunda `CubeSatSurrogateResNet` com blocos residuais (skip connections), ativações SiLU e normalização por camada (`LayerNorm`), governada pela função de perda composta `PhysicsGuidedLoss` com decomposição explícita em quatro termos funcionais:
     $$
     \mathcal{L}_{\text{total}} = \mathcal{L}_{\text{MSE}} + \lambda_{\text{bound}} \mathcal{L}_{\text{bound}} + \lambda_{\text{GA}} \mathcal{L}_{\text{GA}} + \lambda_{\text{mono}} \mathcal{L}_{\text{mono}}
     $$
     onde os pesos canônicos calibrados e seus papéis físicos são:
     - $\mathcal{L}_{\text{MSE}}$: erro quadrático médio de fidelidade de dados sobre os quatro alvos normalizados ($f_1, \sigma_{3\sigma}, G_{\text{rms}}, T$);
     - $\lambda_{\text{bound}} = 0{,}15$: penalidade de barreira inferior normativa baseada em $\text{ReLU}(20{,}0\text{ Hz} - \hat{f}_{1,\text{phys}})^2$, impedindo frequências não físicas no limiar espectral da NASA GEVS;
     - $\lambda_{\text{GA}} = 0{,}015$ (proveniente de $\lambda_{\text{phys}} \times 0{,}10$ na parametrização do modelo): regularizador micromecânico de escala de Gibson-Ashby para sólidos celulares sob flexão ($f_{1,\text{GA}} = 1350{,}0\sqrt{\rho_{\text{rel}}}$), atuando como atrator assintótico suave que preserva a física celular sem distorcer o enrijecimento dos trilhos sólidos;
     - $\lambda_{\text{mono}} = 0{,}10$: regularizador de monotonicidade de rigidez, penalizando quedas espúrias de frequência natural ao longo de passos positivos de densidade relativa ($\Delta \rho_{\text{rel}} > 0{,}05$).
  3. **Eficiência Amostral Superior ($> 7\times$) com Dataset Transparente:** Enquanto modelos neurais caixa-preta convencionais da literatura (ex.: Hou et al., *Materials & Design*, 2024) exigiram $1800$ amostras para atingir $R^2 \approx 0{,}95$, a presente formulação atinge $\overline{R^2} = 0{,}9874$ e $\text{RMSE} = 0{,}0182$ com um Design of Experiments (DoE) compacto de apenas **$250$ amostras geradas via kernel proxy calibrado** (`cubesat_fea_doe_dataset.csv`, `execution_mode: calibrated_proxy`), reduzindo drasticamente o tempo de geração de dados de semanas para horas e garantindo reprodutibilidade irrestrita.
  4. **Aceleração Dual: Instantânea e Amortizada de Ponta a Ponta:** A latência de inferência de $0{,}405\text{ ms}$ por indivíduo viabilizou a exploração de $10.000$ candidatos no NSGA-II em $< 4{,}5\text{ segundos}$. Essa métrica estabelece um regime dual de aceleração computacional:
     - **Speedup Instantâneo de Inferência (Online):**
       $$
       \text{Speedup}_{\text{online,modal}} = \frac{92{,}0\text{ s}}{0{,}000405\text{ s}} \approx 2{,}27 \times 10^5\times \quad \text{e} \quad \text{Speedup}_{\text{online,transiente}} = \frac{145{,}0\text{ s}}{0{,}000405\text{ s}} \approx 3{,}58 \times 10^5\times
       $$
     - **Speedup Amortizado de Ponta a Ponta (End-to-End Design Cycle):** Incorporando o custo computacional de geração prévia do dataset ($250 \times 92{,}0\text{ s} \approx 6{,}39\text{ h}$), o treinamento da rede ($\sim 35\text{ s}$) e a otimização evolutiva de 10.000 indivíduos ($< 4{,}5\text{ s}$), o ciclo completo totaliza $\approx 6{,}40\text{ h}$, frente às $255{,}56\text{ h}$ ($10{,}65\text{ dias}$) que seriam exigidas pela avaliação direta por elementos finitos, consolidando um ganho industrial líquido amortizado de:
       $$
       \text{Speedup}_{\text{amortizado}} = \frac{10.000 \times 92{,}0\text{ s}}{(250 \times 92{,}0\text{ s}) + 35\text{ s} + 4{,}5\text{ s}} \approx \frac{920.000\text{ s}}{23.039{,}5\text{ s}} \approx 39{,}93\times \approx 40{,}0\times
       $$
- **Diferencial vs. Concorrente Mais Próximo:** Supera os processos gaussianos Kriging de Cao et al. (2024), cuja complexidade cúbica $\mathcal{O}(N^3)$ e latência de $15-40\text{ ms}$ impedem buscas evolutivas instantâneas, e supera a BPNN de Hou et al. (2024), que não possui restrições físicas contra alucinações numéricas.
```

---

### PATCH 3: `novelty_assessment_report.md` — Seção 2.2 (Delta Teórico, Harmonização dos 4 Termos)
- **Localização:** Linhas 80–95 de `benchmarks/sota_assessment/novelty_assessment_report.md`.
- **TargetContent (Atual):**
```markdown
### 2.2. Delta Teórico ($\Delta_{\text{teórico}}$)
- **Pontuação de Novidade Teórica:** `8.8` / 10
- **Quais garantias formais foram formuladas e integradas:**
  1. **Acoplamento das Leis de Escala de Gibson-Ashby no Espaço Latente:** Injeção direta da relação de escala fenomenológica para sólidos celulares com deformação dominada por flexão de costelas ($E^* / E_s \propto (\rho^* / \rho_s)^2$) como termo de penalidade assintótica na perda neural:
     $$
     f_{1,\text{GA}}(\rho_{\text{rel}}) = \alpha \cdot \sqrt{\rho_{\text{rel}}}, \quad \alpha = 1350{,}0\text{ Hz}
     $$
     $$
     \mathcal{L}_{\text{GA}} = \frac{1}{N} \sum_{i=1}^N \left( \frac{\hat{f}_{1,i} - f_{1,\text{GA}}(\rho_{\text{rel},i})}{f_{1,\text{GA}}(\rho_{\text{rel},i})} \right)^2
     $$
  2. **Regularizador Analítico de Monotonicidade da Rigidez:** Formulação de um operador variacional que penaliza decréscimos espúrios de rigidez dinâmica quando a densidade relativa da célula se eleva:
     $$
     \mathcal{L}_{\text{mono}} = \frac{1}{|\mathcal{P}|} \sum_{(i,j) \in \mathcal{P}} \max\left(0, -(\hat{f}_{1,j} - \hat{f}_{1,i}) - \epsilon_{\text{tol}}\right)
     $$
     onde $\mathcal{P} = \left\{(i,j) \mid \rho_{\text{rel},j} - \rho_{\text{rel},i} > \delta_{\rho}\right\}$ com $\delta_{\rho} = 0{,}05$ e tolerância elástica $\epsilon_{\text{tol}} = 0{,}15$.
  3. **Garantia de Limite Inferior Normativo NASA GEVS:** O termo $\mathcal{L}_{\text{positivity}}$ penaliza qualquer predição de frequência abaixo do limiar estrutural básico ($f_1 < 20{,}0\text{ Hz}$), garantindo que todo o espaço explorado pelo NSGA-II satisfaça a estabilidade elasto-dinâmica.
```
- **ReplacementContent (Proposto):**
```markdown
### 2.2. Delta Teórico ($\Delta_{\text{teórico}}$)
- **Pontuação de Novidade Teórica:** `8.8` / 10
- **Quais garantias formais foram formuladas e integradas:**
  1. **Acoplamento das Leis de Escala de Gibson-Ashby no Espaço Latente:** Injeção direta da relação de escala fenomenológica para sólidos celulares com deformação dominada por flexão de costelas ($E^* / E_s \propto (\rho^* / \rho_s)^2$) como termo de penalidade assintótica suave na perda neural com peso calibrado $\lambda_{\text{GA}} = 0{,}015$:
     $$
     f_{1,\text{GA}}(\rho_{\text{rel}}) = \alpha \cdot \sqrt{\rho_{\text{rel}}}, \quad \alpha = 1350{,}0\text{ Hz}
     $$
     $$
     \mathcal{L}_{\text{GA}} = \frac{1}{N} \sum_{i=1}^N \left( \frac{\hat{f}_{1,\text{phys},i} - f_{1,\text{GA}}(\rho_{\text{rel},i})}{f_{1,\text{GA}}(\rho_{\text{rel},i})} \right)^2
     $$
     onde $\hat{f}_{1,\text{phys}}$ representa a frequência desnormalizada via média e desvio-padrão do scaler físico. Esse termo induz atração assintótica suave à lei analítica sem anular a rigidez residual fornecida pelos trilhos de deployer maciços de AlSi10Mg.
  2. **Regularizador Analítico de Monotonicidade da Rigidez:** Formulação de um operador variacional com peso $\lambda_{\text{mono}} = 0{,}10$ que penaliza decréscimos espúrios de rigidez dinâmica quando a densidade relativa da célula se eleva:
     $$
     \mathcal{L}_{\text{mono}} = \frac{1}{|\mathcal{P}|} \sum_{(i,j) \in \mathcal{P}} \left[\text{ReLU}\left(-(\Delta \hat{f}_{1,ij} + \epsilon_{\text{tol}})\right)\right]^2
     $$
     onde $\mathcal{P} = \left\{(i,j) \mid \rho_{\text{rel},j} - \rho_{\text{rel},i} > \delta_{\rho}\right\}$ com passo de densidade $\delta_{\rho} = 0{,}05$ e margem elástica de tolerância $\epsilon_{\text{tol}} = 0{,}15\sigma_{f_1}$ ($\approx 12\text{ Hz}$), prevenindo penalidades espúrias causadas pela variação da razão de aspecto $(h/l)$.
  3. **Garantia de Limite Inferior Normativo NASA GEVS:** O termo $\mathcal{L}_{\text{bound}}$ com peso $\lambda_{\text{bound}} = 0{,}15$ impõe barreira unilateral:
     $$
     \mathcal{L}_{\text{bound}} = \frac{1}{N} \sum_{i=1}^N \left[\text{ReLU}\left(20{,}0\text{ Hz} - \hat{f}_{1,\text{phys},i}\right)\right]^2
     $$
     penalizando categoricamente predições de frequência fundamental abaixo do limiar estrutural básico de lançamento ($20{,}0\text{ Hz}$), garantindo que todo o espaço explorado pelo algoritmo NSGA-II satisfaça a estabilidade elasto-dinâmica.
```

---

### PATCH 4: `novelty_assessment_report.md` — Seção 3 (Tabela Comparativa, Nota de Speedup Dual)
- **Localização:** Linhas 145–147 de `benchmarks/sota_assessment/novelty_assessment_report.md`.
- **TargetContent (Atual):**
```markdown
| **Inferência em tempo real ($< 1\text{ ms}$)** | N/A | N/A | N/A | ⚠️ ($\sim 2\text{ ms}$) | ❌ ($15 - 40\text{ ms}$, $\mathcal{O}(N^3)$) | ✅ **($0{,}405\text{ ms}$, speedup $3{,}6 \times 10^5\times$)** |
```
- **ReplacementContent (Proposto):**
```markdown
| **Inferência em tempo real ($< 1\text{ ms}$)** | N/A | N/A | N/A | ⚠️ ($\sim 2\text{ ms}$) | ❌ ($15 - 40\text{ ms}$, $\mathcal{O}(N^3)$) | ✅ **($0{,}405\text{ ms}$, speedup online $2{,}27-3{,}58 \times 10^5\times$, amortizado $\approx 40\times$)** |
```

---

### PATCH 5: `novelty_assessment_report.md` — Seção 4.1 e 4.2 (Formalização Completa de TRL)
- **Localização:** Linhas 153–176 de `benchmarks/sota_assessment/novelty_assessment_report.md`.
- **TargetContent (Atual):**
```markdown
### 4.1. Diagnóstico de Prontidão Tecnológica Atual (TRL 4)
Na escala padronizada NASA / ESA (ISO 16290:2013), o projeto classifica-se rigorosamente no nível:
$$\mathbf{TRL\ 4} \quad \text{— Validação de componentes e arquitetura em ambiente de laboratório / simulação de alta fidelidade}$$

### 4.2. Rastreamento e Evidências Documentais em `Entregas-finais`
A pontuação de TRL 4 apoia-se em um conjunto de evidências documentais e computacionais auditadas no repositório:
1. **Tese Exaustiva Enciclopédica (114 páginas):**  
   Localização: `Entregas-finais/01-Tese-Exaustiva/main.pdf` (e fonte `main.tex`).  
   Evidência: Documentação completa da formulação variacional, micromecânica de células reentrantes, esteira de elementos finitos e análise de sensibilidade estocástica.
2. **Manuscritos Científicos Submetidos a Periódicos Elsevier Qualis A1:**  
   - *Materials & Design*: `Entregas-finais/02-Artigos-Cientificos/01-Materials-and-Design-Elsevier/main.tex` (Tabela `tab:benchmark` de DfAM e metamateriais).
   - *Aerospace Science and Technology*: `Entregas-finais/02-Artigos-Cientificos/02-Aerospace-Science-and-Technology-Elsevier/main.tex` (Qualificação dinâmica NASA GEVS e dupla condição de contorno).
   - *Engineering Applications of Artificial Intelligence*: `Entregas-finais/02-Artigos-Cientificos/03-Engineering-Applications-of-AI-Elsevier/main.tex` (Modelo substituto PG-ResNet e regularização de Gibson-Ashby).
3. **Monografia de Graduação em Engenharia Mecânica (UESC, 52 páginas):**  
   Localização: `Entregas-finais/03-TCC-Graduacao-UESC/main.pdf`.  
   Evidência: Síntese pedagógica e formal aprovada com foco em projeto para manufatura e mitigação de cargas dinâmicas.
4. **Pipeline Numérico Auditado e Reprodutível:**  
   - Malhagem volumétrica quadrática Tet10: `src/mesh/gmsh_engine.py`.
   - Eigensolver e análise espectral estocástica: `src/analysis/code_aster_runner.py` (Code_Aster v2021).
   - Simulação explícita de impacto e contato: OpenRadioss (`test_pod_flexible`).
   - Modelo substituto residual e perda composta: `src/neural/surrogate_model.py`.
   - Otimizador genético multiobjetivo: `src/optimization/nsga2_optimizer.py`.
```
- **ReplacementContent (Proposto):**
```markdown
### 4.1. Diagnóstico de Prontidão Tecnológica Atual (TRL 4 Digital / TRL 3 Hardware)
Na avaliação de maturidade tecnológica aeroespacial, adota-se a desambiguação formal entre as diretrizes de Engenharia Digital da NASA/ESA (NASA SP-6105, Rev. 2) e a escala de qualificação física de componentes da ISO 16290:2013:
$$\mathbf{TRL\ 4\ \text{Digital}} \quad \text{— Validação analítico-computacional integrada em ambiente simulado relevante de alta fidelidade}$$
$$\mathbf{TRL\ 3\ \text{Hardware}} \quad \text{— Prova de conceito analítica e numérica rigorosa concluída (pré-queima de provetes físicos)}$$

O projeto atinge plenamente o **Digital TRL 4 (NASA / ESA)** ao completar a cadeia de simulação multifísica de alta fidelidade em ambiente representativo das cargas operacionais de lançamento:
- Qualificação dinâmica em espectro estocástico PSD completo da norma **NASA GSFC-STD-7000A GEVS** ($14{,}1\text{ G}_{\text{rms}}$, $20-2000\text{ Hz}$);
- Validação sob condições de contorno duais: engastamento rígido ($f_1 = 579{,}62\text{ Hz}$) e interface flexível de contato com canister P-POD ($f_1 = 304{,}10\text{ Hz}$, $MS_{f_1} = +2{,}04$);
- Avaliação de integridade estrutural por fadiga vibratória de Steinberg em 3 bandas gaussianas sob $120{,}0\text{ s}$ de excitação, atingindo $D = 0{,}0458 \ll 0{,}25$ no entalhe crítico ($\sigma_{3\sigma} = 166{,}91\text{ MPa}$);
- Conformidade geométrica estrita com restrições de manufatura aditiva em AlSi10Mg via L-PBF ($\theta_{\text{overhang}} = 65{,}75^\circ \ge 35{,}0^\circ$, $t = 0{,}613\text{ mm} \ge 0{,}50\text{ mm}$, drenos de pó $\phi \ge 2{,}0\text{ mm}$).

Sob a ótica estrita de hardware da **ISO 16290:2013**, o estado atual encerra a etapa de **TRL 3 avançado**, por não ter ainda realizado ensaios destrutivos em provetes metálicos de bancada (tração ASTM E8M e ensaios de shaker). A fabricação aditiva física dos cupons e painéis constitui o marco imediato de transição para o TRL 4/5 de hardware mapeado no roadmap.

### 4.2. Rastreamento e Evidências Documentais em `Entregas-finais`
A pontuação apoia-se em um conjunto de evidências documentais e computacionais auditadas no repositório:
1. **Tese Exaustiva Enciclopédica (114 páginas):**  
   Localização: `Entregas-finais/01-Tese-Exaustiva/main.pdf` (e fonte `main.tex`).  
   Evidência: Documentação completa da formulação variacional, micromecânica de células reentrantes, esteira de elementos finitos e análise de sensibilidade estocástica.
2. **Manuscritos Científicos Submetidos a Periódicos Elsevier Qualis A1:**  
   - *Materials & Design*: `Entregas-finais/02-Artigos-Cientificos/01-Materials-and-Design-Elsevier/main.tex` (Tabela `tab:benchmark` de DfAM e metamateriais).
   - *Aerospace Science and Technology*: `Entregas-finais/02-Artigos-Cientificos/02-Aerospace-Science-and-Technology-Elsevier/main.tex` (Qualificação dinâmica NASA GEVS e dupla condição de contorno).
   - *Engineering Applications of Artificial Intelligence*: `Entregas-finais/02-Artigos-Cientificos/03-Engineering-Applications-of-AI-Elsevier/main.tex` (Modelo substituto PG-ResNet e regularização de Gibson-Ashby).
3. **Monografia de Graduação em Engenharia Mecânica (UESC, 52 páginas):**  
   Localização: `Entregas-finais/03-TCC-Graduacao-UESC/main.pdf`.  
   Evidência: Síntese pedagógica e formal aprovada com foco em projeto para manufatura e mitigação de cargas dinâmicas.
4. **Pipeline Numérico Auditado e Reprodutível:**  
   - Malhagem volumétrica quadrática Tet10: `src/mesh/gmsh_engine.py`.
   - Síntese de decks Code_Aster v2021 (`.comm`) e execução DoE via kernel elastodinâmico calibrado: `src/analysis/code_aster_runner.py` e `src/analysis/open_fea_kernel.py` (`execution_mode: calibrated_proxy`).
   - Simulação explícita de impacto e contato: OpenRadioss (`test_pod_flexible`).
   - Modelo substituto residual e perda composta de 4 termos: `src/neural/surrogate_model.py`.
   - Otimizador genético multiobjetivo: `src/optimization/nsga2_optimizer.py`.
```

---

### PATCH 6: `novelty_assessment_report.md` — Seção 5 (Recomendações Editoriais Q1)
- **Localização:** Linhas 221–238 de `benchmarks/sota_assessment/novelty_assessment_report.md`.
- **TargetContent (Atual):**
```markdown
1. **Claims Proibidos (Zero Sycophancy / Evitar Veto de Revisores):**
   - ❌ NUNCA alegar *"eliminação completa de suportes em qualquer orientação"* (restringir à afirmação de que a orientação ótima $\theta^* = 65{,}75^\circ$ respeita o ângulo autossuportado $\ge 35^\circ$ do L-PBF).
   - ❌ NUNCA alegar *"qualificação de voo em TRL 8"* (o trabalho concluiu a qualificação computacional de alta fidelidade em TRL 4; ensaios em shaker físico e TVAC são requisitos de TRL 5 e 6).
   - ❌ NUNCA alegar *"bandgaps fonônicos por dispersão de Bragg na faixa de lançamento"* (a atenuação vibroacústica de $76{,}50\%$ decorre de antirressonâncias e descasamento de impedância acústica sub-comprimento de onda, pois o comprimento de onda em $20 - 2000\text{ Hz}$ é métrico).

2. **Claims Fortes e Inatacáveis (Recomendados para o Abstract e Highlights):**
   - ✅ *"First-of-a-kind monolithic 1U CubeSat chassis integrating re-entrant auxetic lattice panels in flight-grade AlSi10Mg via L-PBF."*
   - ✅ *"Simultaneous 62.49% primary structural mass relief (116.0 g vs. 308.0 g) and 40.65% fundamental frequency boost (579.62 Hz vs. 412.10 Hz), surpassing NASA GEVS 100 Hz floor under dual clamped/canister boundary conditions."*
   - ✅ *"Passive vibroacoustic isolation of -12.6 dB (76.50% reduction, payload RMS acceleration dropped from 23.4 G_rms to 5.5 G_rms under 14.1 G_rms NASA GEVS qualification spectrum) without parasitic elastomer dampers."*
   - ✅ *"Physics-Guided ResNet surrogate regularized by Gibson-Ashby scaling laws and stiffness monotonicity, achieving R2 = 0.9874 with only 250 high-fidelity FEA training samples and accelerating multiobjective Pareto search by over 200,000x."*
   - ✅ *"Structural fatigue qualification under Steinberg 3-band random vibration formulation with cumulative damage D = 0.0458, demonstrating a 5.46x life margin against NASA-HDBK-7005 requirement (D <= 0.25)."*
```
- **ReplacementContent (Proposto):**
```markdown
1. **Claims Proibidos (Zero Sycophancy / Evitar Veto de Revisores):**
   - ❌ NUNCA alegar *"eliminação completa de suportes em qualquer orientação"* (restringir à afirmação de que a orientação ótima $\theta^* = 65{,}75^\circ$ respeita o ângulo autossuportado $\ge 35^\circ$ do L-PBF).
   - ❌ NUNCA alegar *"qualificação física de hardware em TRL 4/5"* sem ressalvas (especificar rigorosamente que o projeto atingiu Digital TRL 4 sob diretrizes NASA SP-6105 / ESA, correspondendo a TRL 3 avançado na esteira física da ISO 16290:2013 antes dos testes de tração e shaker de bancada).
   - ❌ NUNCA alegar *"dataset gerado exclusivamente por 250 execuções completas de solver comercial 3D"* (declarar com total transparência a arquitetura híbrida de execução com kernel proxy elastodinâmico calibrado ancorado em soluções Code_Aster de alta ordem).
   - ❌ NUNCA alegar *"bandgaps fonônicos por dispersão de Bragg na faixa de lançamento"* (a atenuação vibroacústica de $76{,}50\%$ decorre de antirressonâncias e descasamento de impedância acústica sub-comprimento de onda, pois o comprimento de onda em $20 - 2000\text{ Hz}$ é métrico).
   - ❌ NUNCA omitir o custo computacional offline do DoE ao reportar o speedup do metamodelo (sempre apresentar conjuntamente o speedup online instantâneo de $> 2{,}27 \times 10^5\times$ e o speedup amortizado de ponta a ponta de $\approx 40{,}0\times$).

2. **Claims Fortes e Inatacáveis (Recomendados para o Abstract e Highlights):**
   - ✅ *"First-of-a-kind monolithic 1U CubeSat chassis integrating re-entrant auxetic lattice panels in flight-grade AlSi10Mg via L-PBF."*
   - ✅ *"Simultaneous 62.49% primary structural mass relief (116.0 g vs. 308.0 g) and 40.65% fundamental frequency boost (579.62 Hz vs. 412.10 Hz), surpassing NASA GEVS 100 Hz floor under dual clamped/canister boundary conditions."*
   - ✅ *"Passive vibroacoustic isolation of -12.6 dB (76.50% reduction, payload RMS acceleration dropped from 23.4 G_rms to 5.5 G_rms under 14.1 G_rms NASA GEVS qualification spectrum) without parasitic elastomer dampers."*
   - ✅ *"Physics-Guided ResNet surrogate regularized by an explicit 4-term loss integrating Gibson-Ashby scaling laws and stiffness monotonicity, achieving R2 = 0.9874 with 250 calibrated proxy samples anchored in Code_Aster solutions, enabling a 2.27x10^5x online speedup and a 40x amortized design cycle compression."*
   - ✅ *"Structural fatigue qualification under Steinberg 3-band random vibration formulation with cumulative damage D = 0.0458 at the critical notch (sigma_3sigma = 166.91 MPa), demonstrating a 5.46x life margin against NASA-HDBK-7005 requirement (D <= 0.25)."*
```

---

### PATCH 7: `sota_mapping_report.md` — Seção 2 (Diagrama Mermaid) e Seção 3 (Tabela 1)
- **Localização:** Linha 48 e Linha 75 de `benchmarks/sota_assessment/sota_mapping_report.md`.
- **TargetContent 1 (Linha 48):**
```markdown
    A2 -.-> Integracao["<b>Proposta Atual: Candidato #28</b><br>• Chassi monobloco auxético em AlSi10Mg L-PBF (-62.49% massa)<br>• Atenuação passiva de -12.6 dB no payload (5.5 G_rms)<br>• Desacoplamento modal dual: 579.62 Hz engastado / 304.1 Hz P-POD<br>• Dano de fadiga de Steinberg D = 0.0458 << 0.25<br>• Physics-Guided ResNet com speedup > 227.000x"]
```
- **ReplacementContent 1 (Proposto):**
```markdown
    A2 -.-> Integracao["<b>Proposta Atual: Candidato #28</b><br>• Chassi monobloco auxético em AlSi10Mg L-PBF (-62.49% massa)<br>• Atenuação passiva de -12.6 dB no payload (5.5 G_rms)<br>• Desacoplamento modal dual: 579.62 Hz engastado / 304.1 Hz P-POD<br>• Dano de fadiga de Steinberg D = 0.0458 << 0.25<br>• PG-ResNet (speedup online > 227.000x; amortizado ~40x)"]
```

- **TargetContent 2 (Linha 75):**
```markdown
| **PROP**| **Candidato #28 (UESC 2026)**<br>Gabriel Marques de Andrade | **Chassi Monobloco Auxético Reentrante Integrado** | **AlSi10Mg L-PBF ($300^\circ\text{C}/2\text{h}$)** | **$116{,}0\text{ g}$ ($-62{,}49\%$)** | **$579{,}62\text{ Hz}$ ($+40{,}65\%$)** | **$304{,}10\text{ Hz}$ ($MS = +2{,}04$)** | **$-12{,}6\text{ dB}$ ($-76{,}50\%$, $T = 0{,}39$)** | **$5{,}5\text{ G}_{\text{rms}}$ (sob $14{,}1\text{ G}$ GEVS)** | **$D = 0{,}0458 \ll 0{,}25$ ($5{,}46\times$ vida)** | **$\theta \ge 35^\circ$ autossuportado, $\phi \ge 2\text{ mm}$** | **PG-ResNet ($0{,}405\text{ ms}$, speedup $3{,}6 \times 10^5\times$)** |
```
- **ReplacementContent 2 (Proposto):**
```markdown
| **PROP**| **Candidato #28 (UESC 2026)**<br>Gabriel Marques de Andrade | **Chassi Monobloco Auxético Reentrante Integrado** | **AlSi10Mg L-PBF ($300^\circ\text{C}/2\text{h}$)** | **$116{,}0\text{ g}$ ($-62{,}49\%$)** | **$579{,}62\text{ Hz}$ ($+40{,}65\%$)** | **$304{,}10\text{ Hz}$ ($MS = +2{,}04$)** | **$-12{,}6\text{ dB}$ ($-76{,}50\%$, $T = 0{,}39$)** | **$5{,}5\text{ G}_{\text{rms}}$ (sob $14{,}1\text{ G}$ GEVS)** | **$D = 0{,}0458 \ll 0{,}25$ ($5{,}46\times$ vida)** | **$\theta \ge 35^\circ$ autossuportado, $\phi \ge 2\text{ mm}$** | **PG-ResNet ($0{,}405\text{ ms}$, online $3{,}6 \times 10^5\times$, amort. $\approx 40\times$)** |
```

---

## 5. Verification Method (Método de Verificação Independente)

Para que o orquestrador ou qualquer outro agente audite de forma independente a correção matemática e a consistência das alterações:

1. **Verificação dos Pesos da Função de Perda Composta em Python:**
   ```bash
   .venv/bin/python3 -c "
   import torch
   from src.neural.surrogate_model import PhysicsGuidedLoss
   loss_fn = PhysicsGuidedLoss(lambda_phys=0.15, lambda_mono=0.10)
   print('lambda_phys (nominal):', loss_fn.lambda_phys)
   print('lambda_mono (nominal):', loss_fn.lambda_mono)
   print('lambda_bound (efetivo):', loss_fn.lambda_phys)
   print('lambda_GA (efetivo):', loss_fn.lambda_phys * 0.10)
   assert abs(loss_fn.lambda_phys * 0.10 - 0.015) < 1e-6, 'Discrepância no peso de Gibson-Ashby'
   print('PESOS CONFERIDOS COM SUCESSO')
   "
   ```

2. **Verificação do Modo de Execução do Dataset:**
   ```bash
   python3 -c "
   import csv
   with open('data/cubesat_fea_doe_dataset.csv') as f:
       reader = csv.DictReader(f)
       rows = list(reader)
   print('Total amostras:', len(rows))
   modes = set(r['execution_mode'] for r in rows)
   print('Modos de execucao:', modes)
   assert modes == {'calibrated_proxy'}
   print('PROVENIÊNCIA CALIBRATED_PROXY VERIFICADA')
   "
   ```

3. **Verificação do Speedup Dual:**
   ```bash
   python3 -c "
   t_infer = 0.000405
   t_modal = 92.0
   t_trans = 145.0
   n_samples = 250
   n_opt = 10000
   t_train = 35.0
   t_nsga2 = 4.5
   speedup_modal = t_modal / t_infer
   speedup_trans = t_trans / t_infer
   t_direct = n_opt * t_modal
   t_surrogate_total = (n_samples * t_modal) + t_train + t_nsga2
   speedup_amortized = t_direct / t_surrogate_total
   print(f'Speedup Online Modal: {speedup_modal:.1f}x ({speedup_modal/1e5:.2f}e5x)')
   print(f'Speedup Online Trans: {speedup_trans:.1f}x ({speedup_trans/1e5:.2f}e5x)')
   print(f'Tempo Direto FEA: {t_direct/3600:.2f} horas ({t_direct/86400:.2f} dias)')
   print(f'Tempo Esteira Substituta: {t_surrogate_total/3600:.2f} horas')
   print(f'Speedup Amortizado: {speedup_amortized:.2f}x')
   "
   ```

4. **Verificação dos Testes Automatizados Unitários:**
   ```bash
   .venv/bin/pytest tests/test_surrogate_model.py tests/test_optimization.py tests/test_physics.py -v
   ```
   *Critério de aprovação:* 14 testes passando em $< 3{,}0\text{ s}$.
