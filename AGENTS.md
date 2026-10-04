# AGENTS.md — Governança Técnica e Limites Normativos da Missão

## Projeto: CubeSat em Baixa Órbita (LEO)
**Título:** Otimização de Volume e Geometria para Maximização de Desempenho Estrutural e Funcional  
**Instituição:** Universidade Estadual de Santa Cruz (UESC 2026)  
**Autor:** Gabriel Marques de Andrade  
**Orientação / Contexto:** Trabalho de Conclusão de Curso (Engenharia Aeroespacial / Mecânica)

---

## 1. Escopo e Governança Multiagente

Este documento define os limites normativos, critérios de aceitação e papéis técnicos dos agentes autônomos e conectores operacionais que compõem o ecossistema de projeto, simulação e síntese estrutural do chassi CubeSat 1U.

### Papéis dos Agentes Técnicos
1. **Arquiteto de Sistemas CAD/DfAM (`CadAgent`):**
   - Parametrização da célula unitária auxética reentrante.
   - Verificação estrita das restrições de manufatura aditiva (DfAM - *Design for Additive Manufacturing*).
   - Reconstrução paramétrica e exportação neutral STEP AP214 / Parasolid via servidor MCP SolidWorks.

2. **Analista de Estruturas e Dinâmica FEA (`FeaAgent`):**
   - Orquestração de rotinas batch no Ansys MAPDL / PyAnsys.
   - Avaliação modal pré-tensionada e resposta espectral à vibração aleatória (PSD).
   - Extração da primeira frequência natural fundamental ($f_1$), pico de tensão $3\sigma$ e transmissibilidade da carga útil.

3. **Especialista em Metamateriais e Confiabilidade (`MaterialsReliabilityAgent`):**
   - Modelagem contínua via equações fenomenológicas de Gibson-Ashby para sólidos celulares sob flexão.
   - Cálculo do acúmulo de dano de fadiga em vibração aleatória via metodologia de 3 bandas de Steinberg (Palmgren-Miner).
   - Verificação das Margens de Segurança ($MS$) segundo requisitos de qualificação de voo.

4. **Orquestrador Autônomo de Skills (`OrchestratorAgent`):**
   - Roteamento autônomo e context-aware das skills do Antigravity (`aerospace-structures-dfam`, `operations-research-supply-chain`, `academic-paper-latex`, `python-pro`).
   - Orquestração dos ciclos de vida: DoE $\rightarrow$ DfAM Gate $\rightarrow$ Gibson-Ashby/FEA $\rightarrow$ Qualificação NASA GEVS $\rightarrow$ Síntese Técnica.
   - Manutenção de trilha de auditoria completa (`execution_audit_trail`) das skills e ferramentas acionadas.

### 1.1 Política de Ativação Autônoma do Orquestrador
- **Ativação Autônoma Padrão (Sem necessidade de comando explícito):**
  Sempre que qualquer solicitação envolver triagem geométrica, verificação de manufaturabilidade DfAM, análise modal/vibracional, conformidade NASA GEVS, amostragem DoE ou geração de relatórios técnicos/tabelas para o TCC, o assistente **automaticamente assume o papel do `OrchestratorAgent`** e ativa as skills pertinentes.
- **Chamada Explícita Opcional:**
  Caso você deseje forçar um ciclo específico de execução isolada, pode solicitar diretamente chamando o agente ou o script (ex.: *"Execute o ciclo de qualificação pelo OrchestratorAgent"* ou *"Rode o screening com o Orchestrator"*).

---

## 2. Requisitos Estruturais e Arquitetura do Chassi

### 2.1 Envelope e Geometria 1U
- **Formato Base:** CubeSat 1U conforme padrão California Polytechnic State University (CalPoly CubeSat Design Specification).
- **Dimensões Externas:** $100.0 \times 100.0 \times 113.5\text{ mm}$ (incluindo trilhos e guias de implantação).
- **Trilhos de Contato (Deployer Rails):**
  - Quatro trilhos longitudinais maciços de $8.5 \times 8.5\text{ mm}$ de seção transversal.
  - Rugosidade superficial $\le 1.6\ \mu\text{m}\ Ra$ e anodização dura para prevenir soldagem a frio (*cold welding*) no interior do dispensador P-POD (*Poly-Picosatellite Orbital Deployer*).
- **Núcleo Celular Auxético:**
  - Painéis de amortecimento estrutural e absorção de choque pirotécnico compostos por células reentrantes com coeficiente de Poisson negativo ($\nu_{\text{eff}} < 0$).
  - Gradação Funcional de Densidade (FGL - *Functionally Graded Lattice*) para atenuação direcionada de ondas elásticas nas interfaces de fixação da carga útil (*payload*).

### 2.2 Restrições de Manufatura Aditiva Metálica (DfAM - LPBF)
- **Ângulo de Sobraselha Autossuportado:** $\theta_{\text{overhang}} \ge 35^\circ$ em relação à mesa de impressão, eliminando suportes internos no núcleo auxético.
- **Espessura Mínima de Costela (*Strut*):** $t \ge 0.8\text{ mm}$ para garantir coalescência de poça de fusão e mitigar defeitos de falta de fusão (*lack of fusion*).
- **Evacuação de Pó Residual:** Todos os vazios celulares devem possuir orifícios de drenagem desobstruídos com diâmetro $d_{\text{drain}} \ge 2.0\text{ mm}$.

---

## 3. Requisitos Normativos e Critérios de Qualificação (NASA GEVS)

A qualificação estrutural é regida pela norma **NASA GSFC-STD-7000A** (*General Environmental Verification Standard - GEVS*) para cargas secundárias lançadas em lançadores comerciais/institucionais.

### 3.1 Perfil de Vibração Aleatória (Random Vibration PSD)
- **Nível Geral de Aceleração:** $14.1\text{ G}_{\text{rms}}$ aplicado sequencialmente nos 3 eixos ortogonais ($X, Y, Z$).
- **Faixa de Frequência:** $20\text{ Hz}$ a $2000\text{ Hz}$.
- **Duração do Teste de Qualificação:** $120.0\text{ segundos}$ por eixo.
- **Amortecimento Estrutural Crítico Adotado:** $\zeta = 2.0\%$ ($Q = 25$ ou conservador $Q = 10$ para resposta de banda larga).

| Faixa de Frequência (Hz) | Nível de Densidade Espectral de Potência (PSD) | Inclinação / Patamar |
| :--- | :--- | :--- |
| $20\text{ Hz}$ | $0.013\text{ g}^2/\text{Hz}$ | Rampa inicial $+3\text{ dB/oitava}$ |
| $50 - 800\text{ Hz}$ | $0.080\text{ g}^2/\text{Hz}$ | Patamar máximo de energia |
| $2000\text{ Hz}$ | $0.0053\text{ g}^2/\text{Hz}$ | Atenuação $-6\text{ dB/oitava}$ |

---

## 4. Critérios de Aceitação e *Quality Gates*

Para que qualquer topologia candidata seja aprovada pelos agentes na esteira de otimização, os seguintes critérios matemáticos devem ser rigorosamente satisfeitos:

### 4.1 Rigidez Fundamental do Veículo Lançador
Para evitar acoplamento dinâmico ressonante com os modos de baixa frequência do lançador (acelerações quase-estáticas e transientes pogo):
$$\mathbf{f_1 \ge 100.0\text{ Hz}}$$

### 4.2 Margens de Segurança Estrutural ($MS$)
A resposta estocástica de pico a $3\sigma$ (probabilidade de ocorrência de 99.73% em distribuição Gaussiana) não deve ultrapassar a tensão admissível do material corrigida pelos fatores de segurança da NASA ($FS_{\text{yield}} = 1.25$ e $FS_{\text{ultimate}} = 1.40$):
$$\sigma_{\text{adm}} = \frac{\sigma_{\text{yield}}}{FS_{\text{yield}}} = \frac{230.0\text{ MPa}}{1.25} = 184.0\text{ MPa}$$
$$MS_{\text{yield}} = \left( \frac{\sigma_{\text{adm}}}{\sigma_{3\sigma}} \right) - 1.0 > 0.0$$

### 4.3 Dano Cumulativo de Fadiga de Steinberg
Pela regra linear de Palmgren-Miner combinada à distribuição de três bandas de Steinberg para carregamentos aleatórios gaussianos:
$$D = \sum_{i=1}^{3} \frac{n_i}{N_i} = \frac{n_{1\sigma}}{N_{1\sigma}} + \frac{n_{2\sigma}}{N_{2\sigma}} + \frac{n_{3\sigma}}{N_{3\sigma}}$$
- **Critério Teórico de Falha:** $D < 1.0$.
- **Critério de Qualificação Espacial NASA (NASA-HDBK-7005):**
  $$\mathbf{D \le 0.25}$$
  *(Garante fator de segurança de vida de $4\times$ para ambientes vibratórios estocásticos de lançamento)*.

---

## 5. Transição de Materiais: Prototipagem vs. Voo Espacial

O desenvolvimento do CubeSat adota uma estratégia de transição escalonada em duas etapas:

### 5.1 Etapa Experimental / Validação Cinemática (Polímero FDM)
- **Material:** Ácido Polilático (PLA).
- **Processo:** Fused Deposition Modeling (FDM) com bico de $0.4\text{ mm}$ e orientação $0^\circ/90^\circ$.
- **Objetivo:** Validação dimensional, verificação de mecanismos de abertura de antena, encaixe de PCBs no padrão PC/104 e caracterização acústica em mesa vibratória de bancada.
- **Propriedades Base:**
  - Módulo Elástico Sólido: $E_s = 3.5\text{ GPa}$
  - Limite de Escoamento: $\sigma_y = 50.0\text{ MPa}$
  - Densidade: $\rho_s = 1250.0\text{ kg/m}^3$

### 5.2 Etapa Estrutural de Voo (Liga Metálica LPBF)
- **Material:** Liga de Alumínio Aeroespacial AlSi10Mg (com tratamento térmico de alívio de tensões $300^\circ\text{C} / 2\text{h}$).
- **Processo:** Laser Powder Bed Fusion (LPBF / SLM).
- **Objetivo:** Modelo de voo qualificado capaz de suportar cargas de vibração aleatória, descompressão rápida e ciclos termoelásticos em órbita baixa (LEO).
- **Propriedades Base:**
  - Módulo Elástico Sólido: $E_s = 68.0\text{ GPa}$
  - Limite de Escoamento: $\sigma_y = 230.0\text{ MPa}$
  - Limite de Resistência à Tração: $\sigma_{\text{uts}} = 340.0\text{ MPa}$
  - Densidade: $\rho_s = 2680.0\text{ kg/m}^3$
  - Coeficiente de Poisson: $\nu_s = 0.33$
  - Expoente de Basquin: $m = 6.8$
  - Coeficiente de Basquin: $C = 1.2 \times 10^{20}$

### 5.3 Modelo de Escala Gibson-Ashby e Mecânica da Fratura (LEFM)
A transição das propriedades mecânicas entre as geometrias auxéticas e os materiais é regida analiticamente pelo modelo clássico de Gibson-Ashby para sólidos celulares com deformação dominada por flexão das costelas:
$$E^* = E_s \cdot C_1 \cdot \left(\frac{\rho^*}{\rho_s}\right)^2$$
$$\sigma_y^* = \sigma_{ys} \cdot C_2 \cdot \left(\frac{\rho^*}{\rho_s}\right)^{1.5}$$
Onde $C_1 \approx 1.0$ e $C_2 \approx 0.3$.

Para a liga metálica manufaturada aditivamente (AlSi10Mg), os efeitos microestruturais de porosidades residuais induzidas pelo laser são quantificados via Mecânica da Fratura Elástica Linear (LEFM) segundo a lei de Paris-Erdogan:
$$\frac{da}{dN} = C_{\text{paris}} (\Delta K)^p = C_{\text{paris}} (Y \Delta \sigma \sqrt{\pi a})^p$$
assegurando que nenhum poro subsuperficial atinja o tamanho crítico de trinca $a_c = \frac{1}{\pi} \left(\frac{K_{Ic}}{Y \sigma_{3\sigma}}\right)^2$ durante os $120\text{ segundos}$ de excitação dinâmica do lançamento.

---

## 6. Governança Operacional do Servidor MCP (`cubesat_mcp.py`)
- O servidor MCP unifica os conectores `SolidWorksConnector` e `AnsysBatchConnector`, bem como o módulo analítico `auxetic_analytics`.
- O ambiente deve operar de forma resiliente: em servidores de CI/CD ou máquinas sem licença local ativa do SolidWorks COM ou Ansys MAPDL, as rotinas devem executar automaticamente os fallbacks seguros e instrumentados com telemetria via `logging`.
