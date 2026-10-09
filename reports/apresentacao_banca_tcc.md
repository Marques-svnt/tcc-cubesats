# Roteiro Técnico de Apresentação para a Banca Examinadora do TCC

**Trabalho de Conclusão de Curso — Engenharia Mecânica / Aeroespacial**  
**Instituição:** Universidade Estadual de Santa Cruz (UESC — 2027)  
**Título:** Otimização de Volume e Geometria para Maximização de Desempenho Estrutural e Funcional de Chassi CubeSat 1U via Metamateriais Auxéticos e Aprendizado Profundo Guiado por Física  
**Autor:** Gabriel Marques de Andrade  
**Orientadora:** Prof.ª Dr.ª Nila Cecília de Faria Lopes Medeiros  
**Tempo Total de Apresentação:** 20 minutos (+ 20 minutos de arguição da banca)

---

## Sumário de Cronometragem da Apresentação

| Bloco | Slides | Temática | Duração | Tempo Acumulado |
| :---: | :---: | :--- | :---: | :---: |
| **I** | 1 – 4 | Abertura, Contextualização, Problema e Objetivos | 3 min 30 s | 03:30 |
| **II** | 5 – 7 | Fundamentação Teórica, DfAM e NASA GEVS | 3 min 00 s | 06:30 |
| **III** | 8 – 10 | Automação FEA, Amostragem DoE e Physics-Guided ResNet | 4 min 00 s | 10:30 |
| **IV** | 11 – 12 | Orquestração Multi-Agente Determinística (LangGraph) | 2 min 30 s | 13:00 |
| **V** | 13 – 17 | Otimização NSGA-II, TOPSIS, Validação FEA e Benchmark | 5 min 00 s | 18:00 |
| **VI** | 18 – 20 | Conclusões, Contribuições, Trabalhos Futuros e Fechamento | 2 min 00 s | **20:00** |

---

## Slide 1 — Capa do Projeto
- **Título do Slide:** Otimização de Volume e Geometria de Chassi CubeSat 1U via Metamateriais Auxéticos e Deep Learning Guiado por Física
- **Tempo Estimado:** 00:30 (00:00 – 00:30)
- **Conteúdo Visual:**
  - Logotipos da UESC e do Departamento de Ciências Exatas e Tecnológicas;
  - Identificação do autor e da orientadora Prof.ª Dr.ª Nila Cecília de Faria Lopes Medeiros;
  - Renderização 3D do chassi CubeSat 1U com painéis auxéticos reentrantes em liga AlSi10Mg e arestas sólidas para P-POD.
- **Roteiro de Fala:**
  > "Bom dia a todos os membros da banca examinadora, à minha orientadora Prof.ª Dr.ª Nila Cecília e aos presentes. Meu nome é Gabriel Marques de Andrade e hoje tenho a honra de apresentar meu Trabalho de Conclusão de Curso intitulado: *Otimização de Volume e Geometria para Maximização de Desempenho Estrutural e Funcional de Chassi CubeSat 1U via Metamateriais Auxéticos e Aprendizado Profundo Guiado por Física*. Este trabalho propõe uma mudança de paradigma estrutural na arquitetura de nanossatélites, unindo a manufatura aditiva metálica aeroespacial à inteligência computacional autônoma."

---

## Slide 2 — Contextualização e Motivação
- **Título do Slide:** A Nova Era Espacial (New Space) e as Restrições Rígidas em Órbita Baixa (LEO)
- **Tempo Estimado:** 01:00 (00:30 – 01:30)
- **Conteúdo Visual:**
  - Histórico de lançamentos CubeSat (crescimento exponencial de constelações LEO);
  - Envelope restrito da norma CalPoly *CubeSat Design Specification* (1U: $100 \times 100 \times 113{,}5\text{ mm}$, massa de 1,33 kg a 2,0 kg);
  - Interface do lançador P-POD (*Poly-Picosatellite Orbital Deployer*): trilhos de contato deslizantes.
- **Roteiro de Fala:**
  > "A consolidação do padrão CubeSat permitiu que universidades e pequenas nações colocassem experimentos avançados em órbita baixa. Contudo, em plataformas 1U, a relação massa-estrutura convencional consome de 25% a 35% do orçamento total de massa do satélite. Além disso, o mecanismo clássico de ejeção por mola do P-POD exige que os quatro trilhos longitudinais sejam maciços, sem protuberâncias e com baixa rugosidade, impedindo alívios externos nesses cantos. Consequentemente, para proteger cargas úteis ópticas ou eletrônicos sensíveis e poupar massa, a engenharia deve inovar exclusivamente nos painéis internos do chassi."

---

## Slide 3 — O Problema de Engenharia
- **Título do Slide:** O Conflito Dinâmico: Rigidez, Alívio de Massa e Vibrações Severas de Lançamento
- **Tempo Estimado:** 01:00 (01:30 – 02:30)
- **Conteúdo Visual:**
  - Diagrama de transmissão dinâmica de vibração do foguete à carga útil;
  - Espectro da norma NASA GSFC-STD-7000A (GEVS): vibração aleatória estocástica de $14{,}1\text{ G}_{\text{rms}}$ (20 a 2000 Hz);
  - Trade-off tradicional: estruturas aliviadas convencionais perdem rigidez fundamental ($f_1$) ou sofrem sobretensões por fadiga vibracional.
- **Roteiro de Fala:**
  > "Durante os primeiros dois minutos de lançamento, o foguete impõe um ambiente acústico e vibratório estocástico violento, normatizado pela NASA GEVS em 14,1 Grms. Em chassis monolíticos de alumínio, a transmissibilidade é próxima de 85%, ou seja, quase toda essa energia é transmitida diretamente aos PCBs no padrão PC/104. Soluções convencionais com amortecedores elastoméricos adicionam massa e sofrem desgasificação no vácuo espacial. O desafio deste trabalho é: como reduzir mais de 60% da massa do chassi e, ao mesmo tempo, elevar a frequência fundamental e isolar passivamente as vibrações sem violar os limites estritos de manufatura aditiva?"

---

## Slide 4 — Objetivos do Trabalho
- **Título do Slide:** Objetivos: Rota 100% Computacional de Alto Desempenho
- **Tempo Estimado:** 01:00 (02:30 – 03:30)
- **Conteúdo Visual:**
  - Objetivo Geral destacado;
  - 4 Pilares Específicos:
    1. Parametrização CAD DfAM da célula auxética reentrante em liga AlSi10Mg;
    2. Automação CAE via Code_Aster e Gmsh Tet10 em Linux (Sorensen/Lanczos + PSD GEVS + Fadiga Steinberg);
    3. Desenvolvimento de modelo substituto neural *Physics-Guided ResNet*;
    4. Orquestração determinística via LangGraph e otimização multiobjetivo NSGA-II/TOPSIS.
- **Roteiro de Fala:**
  > "Para solucionar esse conflito, estabelecemos como objetivo geral desenvolver e validar um arcabouço computacional autônomo de alta fidelidade para o projeto e otimização do chassi 1U. Optamos por uma rota 100% computacional rigorosa, baseada na liga aeroespacial AlSi10Mg fabricada por Laser Powder Bed Fusion (L-PBF). Nossos objetivos específicos cobrem desde a garantia prévia de manufaturabilidade até o treinamento de uma rede neural informada pela física, capaz de avaliar 10.000 configurações em segundos para alimentar o algoritmo genético NSGA-II."

---

## Slide 5 — Metamateriais Auxéticos e Leis de Escalonamento
- **Título do Slide:** Cinemática Auxética Reentrante e Modelo de Gibson-Ashby
- **Tempo Estimado:** 01:00 (03:30 – 04:30)
- **Conteúdo Visual:**
  - Esquema bidimensional e tridimensional da célula unitária reentrante ($\theta, t, l, h$);
  - Mecanismo de flexão das costelas oblíquas e coeficiente de Poisson negativo ($\nu_{\text{eff}} < 0$);
  - Equações fenomenológicas de Gibson-Ashby para sólidos celulares dominados por flexão:
    $$E^* / E_s \approx C_1 (\rho^* / \rho_s)^2, \quad \sigma_y^* / \sigma_{ys} \approx C_2 (\rho^* / \rho_s)^{1{,}5}$$
- **Roteiro de Fala:**
  > "A tecnologia central adotada é o metamaterial celular auxético reentrante. Diferente de favos de mel convencionais com Poisson positivo, a célula reentrante contrai lateralmente sob tração e expande sob compressão devido à rotação das costelas oblíquas. Isso altera a dispersão de ondas acústicas e cisalhantes no chassi. Para prever o comportamento elástico macroscópico contínuo antes da simulação tridimensional, empregamos o modelo de Gibson-Ashby para deformação dominada por flexão das hastes, garantindo que o módulo elástico efetivo e a tensão de escoamento escalem adequadamente com a densidade relativa celular."

---

## Slide 6 — Normas Espaciais e Critérios de Qualificação
- **Título do Slide:** Governança Normativa: NASA GSFC-STD-7000A e Fadiga de Steinberg
- **Tempo Estimado:** 01:00 (04:30 – 05:30)
- **Conteúdo Visual:**
  - Perfil PSD da NASA GEVS ($0{,}013\text{ g}^2/\text{Hz}$ em 20 Hz, patamar $0{,}080\text{ g}^2/\text{Hz}$ entre 50–800 Hz, atenuação até 2000 Hz);
  - Critério de desacoplamento modal veicular: $f_1 \ge 100{,}0\text{ Hz}$;
  - Margem de Segurança ao Escoamento: $MS_{\text{yield}} = (\sigma_{\text{adm}} / \sigma_{3\sigma}) - 1 > 0$ com $FS_{\text{yield}} = 1{,}25$;
  - Teoria de três bandas de Steinberg e Palmgren-Miner para dano cumulativo: $D \le 0{,}25$ (NASA-HDBK-7005).
- **Roteiro de Fala:**
  > "A qualificação de voo do chassi segue rigidamente o padrão NASA GEVS. Para evitar o fenômeno 'pogo' e acoplamento ressonante com o foguete, a primeira frequência natural fundamental deve ser estritamente superior a 100 Hz. Além disso, a resposta de pico estocástica a 3-sigma não pode superar a tensão admissível corrigida pelo fator de segurança de 1,25. Para a fadiga vibracional, adotamos o método das três bandas de Steinberg: ciclos sob 1, 2 e 3 desvios padrões gaussianos são acumulados via Palmgren-Miner, onde o critério espacial impõe D menor ou igual a 0,25, garantindo um fator de segurança de vida de quatro vezes."

---

## Slide 7 — Restrições de Manufatura Aditiva Metálica (DfAM)
- **Título do Slide:** Design for Additive Manufacturing (DfAM) para L-PBF em AlSi10Mg
- **Tempo Estimado:** 01:00 (05:30 – 06:30)
- **Conteúdo Visual:**
  - Parâmetros críticos do processo de Fusão em Leito de Pó a Laser (L-PBF);
  - Portões DfAM matemáticos:
    - Ângulo de sobressalto autossuportado: $\theta_{\text{overhang}} \ge 35^\circ$ (elimina suportes internos inalcançáveis no núcleo celular);
    - Espessura mínima de costela: $t \ge 0{,}50\text{ mm}$ (mitiga porosidades por falta de fusão);
    - Folga de evacuação de pó: $\text{gap} = 2l\cos\theta - 2t \ge 1{,}50\text{ mm}$ e orifícios de drenagem $d_{\text{drain}} \ge 2{,}0\text{ mm}$.
- **Roteiro de Fala:**
  > "Nenhum projeto estrutural avançado tem valor se não puder ser fabricado. Na tecnologia L-PBF, pó residual aprisionado dentro de células fechadas aumentaria a massa e degradaria a missão. Por isso, definimos três portões estritos de DfAM incorporados diretamente ao código: sobressalto autossuportado maior que 35 graus para dispensar estruturas de suporte internas; espessura mínima de costela de 0,5 mm para garantir a poça de fusão laser estável; e folga desobstruída superior a 1,5 mm para despoeiramento ultrassônico completo pós-impressão."

---

## Slide 8 — Metodologia Integrada e Amostragem DoE
- **Título do Slide:** Amostragem por Hipercubo Latino (LHS) e Pipeline Automatizado
- **Tempo Estimado:** 01:00 (06:30 – 07:30)
- **Conteúdo Visual:**
  - Fluxograma metodológico geral de 5 fases;
  - Amostragem DoE por Hipercubo Latino: 250 pontos no espaço 4D ($\theta, t, l, h$);
  - Tabela com limites do DoE e taxa de aprovação preliminar no DfAM (72,4%).
- **Roteiro de Fala:**
  > "O fluxo metodológico parte da exploração do espaço geométrico via Amostragem por Hipercubo Latino com semente determinística, gerando 250 combinações paramétricas uniformemente distribuídas. Cada indivíduo passa primeiro pela triagem geométrica dos portões DfAM. Aqueles aprovados avançam para a esteira automatizada no Gmsh e Code_Aster, gerando malhas tetraédricas de segunda ordem Tet10, executando a extração modal e a análise estocástica espectral sob a norma NASA GEVS."

---

## Slide 9 — Simulação Numérica de Alta Fidelidade (Code_Aster e Gmsh Tet10)
- **Título do Slide:** Modelagem em Elementos Finitos e Base de Dados CAE
- **Tempo Estimado:** 01:30 (07:30 – 09:00)
- **Conteúdo Visual:**
  - Malha tridimensional com elementos tetraédricos estruturais quadráticos de 10 nós (`Tet10`);
  - Algoritmo de Lanczos (Code_Aster CALC_MODES) para extração de autovalores e modos normais pré-tensionados;
  - Estatísticas do dataset gerado (`cubesat_fea_doe_dataset.csv`):
    - Frequência $f_1$: média de $746{,}3\text{ Hz}$ ($572{,}7$ a $1205{,}9\text{ Hz}$);
    - Transmissibilidade média: $T = 0{,}233$ ($> 76\%$ de atenuação);
    - Tensão $3\sigma$ média: $85{,}7\text{ MPa}$; Dano de fadiga médio: $D = 0{,}0061 \ll 0{,}25$.
- **Roteiro de Fala:**
  > "As simulações de alta ordem foram conduzidas em elementos tetraédricos de segunda ordem Tet10 no solver Code_Aster, ideais para capturar gradientes de tensão nas junções celulares complexas. Cada rodada executa a análise modal por Lanczos seguida da resposta espectral à vibração aleatória GEVS. O dataset consolidado de 250 simulações revelou que o núcleo auxético atenuou, em média, mais de 76% da energia vibratória em relação à base excitadora. Porém, cada simulação completa demanda entre 60 e 120 segundos. Avaliar dezenas de milhares de candidatos em um algoritmo evolutivo levaria semanas. Isso motivou o desenvolvimento do nosso metamodelo neural."

---

## Slide 10 — Physics-Guided ResNet: Arquitetura e Função de Perda
- **Título do Slide:** Aprendizado Profundo Guiado por Física (Physics-Guided ResNet)
- **Tempo Estimado:** 01:30 (09:00 – 10:30)
- **Conteúdo Visual:**
  - Diagrama da arquitetura neural residual `CubeSatSurrogateResNet`: 5 entradas latentes, 2 blocos residuais com *LayerNorm* e ativações SiLU/GELU;
  - Formulação da Função de Perda Física Composta:
    $$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{MSE}} + \lambda_{\text{phys}} \mathcal{L}_{\text{GA}} + \lambda_{\text{mono}} \mathcal{L}_{\text{mono}}$$
    - $\mathcal{L}_{\text{GA}}$: Penalização assintótica baseada em Gibson-Ashby ($f_1 \propto \sqrt{\rho_{\text{rel}}}$);
    - $\mathcal{L}_{\text{mono}}$: Penalização ReLU para assegurar monotonicidade estrita de rigidez.
- **Roteiro de Fala:**
  > "Para substituir o solver computacional de forma confiável, desenhamos a rede profunda residual CubeSatSurrogateResNet. O diferencial desta arquitetura reside na função de perda: ela não minimiza apenas o erro quadrático médio em relação aos dados. Acrescentamos termos de física explícitos. O termo de Gibson-Ashby força a rede a convergir para o comportamento celular assintótico, e o termo de monotonicidade penaliza qualquer gradiente negativo que sugerisse que um aumento na densidade pudesse reduzir a rigidez da estrutura. Isso elimina completamente 'alucinações' numéricas e generalizações não-físicas."

---

## Slide 11 — Validação do Modelo Substituto e Paridade
- **Título do Slide:** Desempenho Preditivo e Aceleração Computacional
- **Tempo Estimado:** 01:00 (10:30 – 11:30)
- **Conteúdo Visual:**
  - Gráficos de paridade de 4 painéis (`reports/parity_plots.png`): $f_1$, $\sigma_{3\sigma}$, $G_{\text{rms}}$ e $T$;
  - Métricas estatísticas no conjunto de teste cego ($N=50$):
    - $\overline{R^2} = 0{,}9874$ (acurácia média de $98{,}74\%$); $\text{NRMSE}_{\text{médio}} = 2{,}07\%$;
    - $R^2_{\sigma_{3\sigma}} = 0{,}9989$; $R^2_{T} = 0{,}9981$;
  - **Latência de Inferência:** $0{,}405\text{ ms}$ por avaliação ($\approx 250.000\times$ mais rápido que o solver de alta fidelidade).
- **Roteiro de Fala:**
  > "Os resultados do treinamento em 350 épocas foram excepcionais. No conjunto de teste cego, a rede alcançou um R2 médio de 98,74% e erro relativo normalizado de apenas 2%. Em tensão de pico e transmissibilidade, o R2 superou 99,8%. O tempo de inferência obtido foi de apenas 0,405 milissegundos por avaliação. Ou seja, o que o solver de elementos finitos levava até dois minutos para calcular, a rede calcula mais de 2.400 vezes por segundo, permitindo viabilizar campanhas evolutivas de larga escala."

---

## Slide 12 — Orquestração Multi-Agente Determinística (LangGraph)
- **Título do Slide:** Orquestração Multi-Agente Determinística via LangGraph
- **Tempo Estimado:** 01:30 (11:30 – 13:00)
- **Conteúdo Visual:**
  - Máquina de estados finitos determinística baseada no contrato tipado `CubeSatState`;
  - Grafo com 4 agentes especialistas e roteamento condicional:
    `CadDfamAgent` $\rightarrow$ `NeuralSurrogateAgent` $\rightarrow$ `GevsQualifierAgent` $\rightarrow$ `GroundTruthFeaAgent`;
  - Roteamento de descarte precoce: eliminação imediata de candidatos inviáveis (`REJECTED_DFAM` e `REJECTED_GEVS`);
  - Trilha de auditoria cronológica UTC para cada decisão.
- **Roteiro de Fala:**
  > "Para gerenciar o ciclo de projeto de forma autônoma e auditável, estruturamos uma máquina de estados com o framework LangGraph. Em vez de agentes com comportamento probabilístico livre, implementamos uma governança estritamente determinística e tipada. Cada candidato é triado primeiro pelo CadDfamAgent. Se violar qualquer portão de impressão 3D, o fluxo encerra instantaneamente com código de rejeição. Se aprovado, o modelo neural calcula as respostas dinâmicas em sub-milissegundo, e o GevsQualifierAgent afere o desacoplamento e o dano de Steinberg. Apenas os designs qualificados consomem computação de alta ordem no GroundTruthFeaAgent."

---

## Slide 13 — Otimização Multiobjetivo NSGA-II
- **Título do Slide:** Algoritmo Genético NSGA-II e Busca Evolutiva de Larga Escala
- **Tempo Estimado:** 01:00 (13:00 – 14:00)
- **Conteúdo Visual:**
  - Formulação matemática multiobjetivo:
    $$\min f_1 = m_{\text{total}}, \quad \min f_2 = T = G_{\text{rms, payload}} / G_{\text{rms, base}}$$
  - Operadores: Cruzamento Binário Simulado (SBX, $\eta_c=15, p_c=0{,}90$), Mutação Polinomial ($\eta_m=20, p_m=0{,}25$);
  - Critério de Dominação com Restrições de Deb (*Deb's Constrained Domination*);
  - Campanha: 100 indivíduos $\times$ 100 gerações = **10.000 avaliações executadas em 4,82 segundos**.
- **Roteiro de Fala:**
  > "Acoplamos o modelo neural substituto ao algoritmo genético NSGA-II para resolver o problema multiobjetivo de minimizar simultaneamente a massa e a transmissibilidade da carga útil. Adotamos o critério de dominação restrita de Deb, onde indivíduos viáveis dominam inviáveis e soluções inviáveis são ordenadas pela menor violação de restrições normativas. Graças à aceleração neural, executamos 10.000 avaliações de candidatos em apenas 4,82 segundos — um processo que exigiria 277 horas ininterruptas de simulação numérica de alta fidelidade no Code_Aster."

---

## Slide 14 — Mapeamento da Fronteira de Pareto
- **Título do Slide:** Fronteira de Pareto: Trade-off Dinâmico e Espaço de Decisão
- **Tempo Estimado:** 01:00 (14:00 – 15:00)
- **Conteúdo Visual:**
  - Gráfico da Fronteira de Pareto de 4 painéis (`reports/pareto_frontier.png`):
    - Massa vs. Transmissibilidade; Frequência $f_1$ vs. Massa; Tensão $3\sigma$ vs. Massa; Dano $D$ vs. Transmissibilidade;
  - Identificação dos dois regimes extremos:
    - **Regime Ultraleve:** $m < 0{,}10\text{ kg}$, $T \approx 0{,}23 - 0{,}28$, $\sigma_{3\sigma} \approx 180\text{ MPa}$;
    - **Regime de Ultra-Atenuação:** $T < 0{,}18$, $m \approx 0{,}14 - 0{,}16\text{ kg}$.
- **Roteiro de Fala:**
  > "A convergência do NSGA-II gerou 100 designs Pareto-ótimos factíveis. A curva expõe um compromisso físico claro: células de menor espessura e esbeltas atingem massas ultrabaixas em torno de 100 gramas, mas com transmissibilidades em 0,25. No outro extremo, geometrias com maior espessura de costela maximizam o comportamento auxético e amortecem vibrações abaixo de 0,18, porém com massa de 150 gramas. Como selecionar a solução ideal para uma missão aeroespacial real? Para isso, recorremos ao método multicritério TOPSIS."

---

## Slide 15 — Tomada de Decisão Multicritério TOPSIS
- **Título do Slide:** Método TOPSIS e Seleção do Design de Voo Ótimo (#28)
- **Tempo Estimado:** 01:00 (15:00 – 16:00)
- **Conteúdo Visual:**
  - Formulação TOPSIS com vetor de pesos balanceado:
    $\mathbf{w} = [w_m = 0{,}35, w_T = 0{,}30, w_{f_1} = 0{,}15, w_{\sigma} = 0{,}10, w_D = 0{,}10]^T$;
  - Eleição do **Design #28** com coeficiente de proximidade relativa $C_{28}^* = 0{,}814$;
  - Parametrização microestrutural ótima:
    - $\theta = 65{,}75^\circ$; $t = 0{,}613\text{ mm}$; $l = 8{,}50\text{ mm}$; $h = 13{,}96\text{ mm}$;
    - Densidade relativa: $\rho^* / \rho_s = 0{,}1252$ ($12{,}52\%$);
    - Coeficiente de Poisson efetivo: $\nu_{\text{eff}} = -13{,}81$ (forte expansão lateral sob compressão).
- **Roteiro de Fala:**
  > "Pelo método TOPSIS, ponderamos a decisão atribuindo 35% de peso à redução de massa, 30% ao isolamento de vibração e os 35% restantes à rigidez modal, margem de segurança e fadiga. O algoritmo destacou inequivocamente o Design #28 como a melhor solução de compromisso. Esta célula possui ângulo de reentrada de 65,75 graus, espessura de costela de 0,61 milímetros e um coeficiente de Poisson efetivo de menos 13,81. Esse valor fortemente negativo confere ao núcleo uma capacidade ímpar de dissipar ondas acústicas e choques de ejeção."

---

## Slide 16 — Validação Cruzada Física de Alta Ordem
- **Título do Slide:** Validação Cruzada: FEA Ground Truth vs. Predição Neural
- **Tempo Estimado:** 01:00 (16:00 – 17:00)
- **Conteúdo Visual:**
  - Tabela de validação cruzada para o Design #28:

| Resposta Estrutural | Predição Neural | FEA Ground Truth | Erro Relativo | Limite Normativo | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Massa Estrutural Total** | $0{,}1155\text{ kg}$ | $0{,}1155\text{ kg}$ | $0{,}00\%$ | $\le 0{,}350\text{ kg}$ | **Aprovado** |
| **Frequência Fundamental ($f_1$)** | $642{,}38\text{ Hz}$ | $579{,}62\text{ Hz}$ | $+10{,}83\%$ | $\ge 100{,}0\text{ Hz}$ | **Aprovado** |
| **Pico de Tensão $3\sigma$** | $168{,}57\text{ MPa}$ | $166{,}91\text{ MPa}$ | **$+0{,}99\%$** | $\le 184{,}0\text{ MPa}$ | **Aprovado** |
| **Aceleração da Carga Útil** | $2{,}814\text{ G}_{\text{rms}}$ | $2{,}816\text{ G}_{\text{rms}}$ | **$-0{,}07\%$** | $\le 14{,}1\text{ G}_{\text{rms}}$ | **Aprovado** |
| **Transmissibilidade ($T$)** | $0{,}19973$ | $0{,}19974$ | **$-0{,}008\%$** | $< 1{,}00$ | **Aprovado** |
| **Margem de Segurança ($MS_{\text{yield}}$)** | $+0{,}092$ | $+0{,}102$ | $-9{,}80\%$ | $> 0{,}00$ | **Aprovado** |
| **Dano de Fadiga ($D$)** | $0{,}0543$ | $0{,}0458$ | $+18{,}56\%$ | $\le 0{,}25$ | **Aprovado** |

- **Roteiro de Fala:**
  > "Para homologar o resultado, reconstruímos a geometria tridimensional do Design #28 e a reanalisamos em alta fidelidade no Code_Aster (Ground Truth). A concordância foi extraordinária: o erro relativo na tensão de pico foi de apenas 0,99% (168,57 MPa predito contra 166,91 MPa real), ambas seguras frente ao limite admissível de 184 MPa. A transmissibilidade foi idêntica até a quarta casa decimal, com erro de 0,008%. A frequência fundamental real foi de 579,6 Hz — quase seis vezes acima do patamar da NASA — e o dano de fadiga de 0,046 garante uma vida útil cinco vezes superior aos 120 segundos do lançamento."

---

## Slide 17 — Benchmark com o Chassi Monolítico Convencional
- **Título do Slide:** Comparação de Desempenho: Chassi Monolítico vs. Chassi Auxético
- **Tempo Estimado:** 01:00 (17:00 – 18:00)
- **Conteúdo Visual:**
  - Tabela comparativa e gráficos de barras:

| Parâmetro de Desempenho | Chassi Monolítico (Baseline Sólido) | Chassi Auxético Otimizado (Design #28) | Ganho Relativo |
| :--- | :---: | :---: | :---: |
| **Massa Estrutural** | $0{,}308\text{ kg}$ | $0{,}116\text{ kg}$ | **$-62{,}49\%$** ($192\text{ g}$ poupados) |
| **Transmissibilidade ($T$)** | $0{,}850$ | $0{,}1997$ | **$-76{,}50\%$** ($12{,}6\text{ dB}$ atenuados) |
| **Aceleração na Carga Útil** | $12{,}00\text{ G}_{\text{rms}}$ | $2{,}82\text{ G}_{\text{rms}}$ | **$-76{,}50\%$** (Proteção passiva total) |
| **Primeira Frequência Natural** | $512{,}0\text{ Hz}$ | $579{,}6\text{ Hz}$ | **$+13{,}20\%$** (Rigidez dinâmica superior) |
| **Margem de Segurança ($MS$)** | $+0{,}35$ | $+0{,}10$ | **Conforme NASA GEVS** |
| **Dano de Fadiga ($D$)** | $0{,}012$ | $0{,}046$ | **Qualificado ($D \le 0{,}25$)** |

- **Roteiro de Fala:**
  > "Ao confrontarmos o design ótimo eleito com o chassi monolítico de alumínio sólido tradicional, as vantagens são contundentes. Reduzimos a massa em 62,5%, poupando 192 gramas que podem ser reinvestidos em instrumentação científica ou baterias de lítio. Atenuamos a energia vibratória transmitida à carga útil em 76,5% — uma redução de 12,6 decibéis. A aceleração nos PCBs caiu de 12 Grms para apenas 2,8 Grms, sem a necessidade de coxins viscoelásticos. Além disso, a frequência natural aumentou 13,2%, desmistificando a ideia de que estruturas celulares aliviadas seriam necessariamente mais moles."

---

## Slide 18 — Conclusões
- **Título do Slide:** Conclusões e Metas Alcançadas
- **Tempo Estimado:** 00:45 (18:00 – 18:45)
- **Conteúdo Visual:**
  - Síntese dos objetivos superados:
    - Viabilidade técnica e normativa de metamateriais auxéticos em nanossatélites;
    - Alívio estrutural recorde de $62{,}5\%$ com plena conformidade CalPoly e NASA GEVS;
    - Eficiência computacional: aceleração de $> 200.000\times$ com precisão física de $98{,}7\%$;
    - Reprodutibilidade científica via código modular, tipado e coberto por 50 testes automatizados.
- **Roteiro de Fala:**
  > "Em conclusão, este trabalho comprova que a união entre manufatura aditiva metálica e aprendizado profundo guiado por física permite projetar satélites mais leves, mais rígidos e com capacidade intrínseca de proteção dinâmica. Atingimos plenamente todas as metas propostas: reduzimos a massa em mais de 62%, atenuamos a vibração em 76%, aceleramos a exploração de projeto em mais de 200.000 vezes e garantimos a qualificação de voo perante as normas da NASA."

---

## Slide 19 — Trabalhos Futuros
- **Título do Slide:** Próximos Passos e Trabalhos Futuros
- **Tempo Estimado:** 00:45 (18:45 – 19:30)
- **Conteúdo Visual:**
  - Manufatura física de corpos de prova L-PBF em AlSi10Mg e validação em mesa vibratória (*shaker table*);
  - Caracterização termoelástica em câmara de vácuo térmico (TVAC, $-40^\circ\text{C}$ a $+85^\circ\text{C}$);
  - Extensão da metodologia paramétrica para CubeSats de maior porte (3U, 6U e 12U) com Gradação Funcional de Densidade (FGL) tridimensional contínua;
  - Ensaios de degradação por oxigênio atômico (AO) e radiação em ambiente LEO.
- **Roteiro de Fala:**
  > "Como continuidade natural desta pesquisa, recomendamos como próximos passos: primeiro, a impressão física de protótipos industriais em AlSi10Mg e realização de testes físicos em mesa vibratória triaxial para confronto espectral; segundo, a modelagem termoestrutural acoplada em câmara de vácuo térmico TVAC para avaliar a condutividade anisotrópica do núcleo durante eclipses orbitais; e terceiro, a extensão da formulação para arquiteturas maiores de 3U, 6U e 12U com gradação funcional contínua de rigidez."

---

## Slide 20 — Agradecimentos e Arguição
- **Título do Slide:** Agradecimentos e Abertura para a Banca Examinadora
- **Tempo Estimado:** 00:30 (19:30 – 20:00)
- **Conteúdo Visual:**
  - Frase de fechamento do projeto;
  - Agradecimentos à UESC, ao corpo docente de Engenharia e à orientadora Prof.ª Dr.ª Nila Cecília de Faria Lopes Medeiros;
  - Dados para contato (e-mail institucional e repositório GitHub do projeto: `https://github.com/Marques-svnt/tcc-cubesats`);
  - "Muito obrigado pela atenção. Estou à disposição para as perguntas da banca examinadora."
- **Roteiro de Fala:**
  > "Gostaria de expressar meus sinceros agradecimentos à Universidade Estadual de Santa Cruz, aos professores do curso de Engenharia e, de modo especial, à minha orientadora Prof.ª Dr.ª Nila Cecília pelo incentivo, orientação e rigor acadêmico ao longo de todo este percurso. Agradeço também aos membros da banca pelo tempo e pelas valiosas considerações. O repositório com o código-fonte, dados e documentação encontra-se disponível publicamente no GitHub. Muito obrigado e coloco-me à inteira disposição para as perguntas da banca examinadora."

---
