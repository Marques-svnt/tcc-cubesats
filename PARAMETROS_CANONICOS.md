# Matriz Canônica de Parâmetros de Engenharia (TCC CubeSat 1U)
**Projeto:** Otimização Estrutural de Chassi CubeSat 1U com Metamateriais Auxéticos em AlSi10Mg sob Cargas Dinâmicas de Lançamento  
**Autor:** Gabriel Marques de Andrade | **Orientadora:** Prof.ª Dr.ª Nila Cecília de Faria Lopes Medeiros  
**Instituição:** Universidade Estadual de Santa Cruz (UESC) — Colegiado de Engenharia Mecânica  
**Revisão:** Versão 2.0 (Pós-Parecer da Banca Examinadora — Resolução das Exigências EX-01 a EX-10)

---

## 1. Geometria e Envelope Estrutural
- **Padrão:** CubeSat Design Specification (Cal Poly, Rev. 14 / P-POD).
- **Fator de forma:** 1U.
- **Dimensões externas nominais:** $100{,}0 \times 100{,}0 \times 113{,}5\text{ mm}$ ($\pm 0{,}1\text{ mm}$).
- **Trilhos guia (Rails):** $8{,}5 \times 8{,}5\text{ mm}$ sólidos monolíticos contínuos nas 4 arestas longitudinais.
  - Raios de concordância: $R \ge 1{,}0\text{ mm}$.
  - Rugosidade superficial: $Ra \le 1{,}6\ \mu\text{m}$ (atrito e deslizamento contra o deployer P-POD).
  - Tratamento superficial: Anodização dura tipo III (PTFE impregnado) nos trilhos.

---

## 2. Orçamento de Massa e Desempenho Comparativo de Voo
| Parâmetro | Chassi Monolítico Convencional (Al 6061-T6) | Chassi Auxético Ótimo Proposto (AlSi10Mg) | Variação / Ganho |
| :--- | :---: | :---: | :---: |
| **Massa Estrutural** | $0{,}308\text{ kg}$ ($308\text{ g}$) | $0{,}116\text{ kg}$ ($116\text{ g}$) | **$-62{,}49\%$** |
| **Frequência Fundamental ($f_1$)** | $412{,}10\text{ Hz}$ | $579{,}62\text{ Hz}$ | **$+40{,}65\%$** (NASA GEVS $\ge 100\text{ Hz}$) |
| **Frequência P-POD Guiado ($f_{1,\text{ppod}}$)** | $245{,}30\text{ Hz}$ | $304{,}10\text{ Hz}$ | **$+23{,}97\%$** ($MS_{f_1} = +2{,}04$) |
| **Transmissibilidade ($T$)** | $1{,}66$ | $0{,}39$ | **$-76{,}50\%$** ($-12{,}6\text{ dB}$) |
| **Aceleração RMS Payload** | $23{,}4\text{ G}_{\text{rms}}$ | $5{,}5\text{ G}_{\text{rms}}$ | **$-76{,}50\%$** ($2{,}82\text{ G}_{\text{rms}}$ na base do sensor) |
| **Tensão Nominal ($3\sigma$)** | $112{,}4\text{ MPa}$ | $68{,}8\text{ MPa}$ | **$-38{,}79\%$** |
| **Tensão no Entalhe Crítico ($\sigma_{3\sigma,\text{notch}}$)** | -- | $166{,}91\text{ MPa}$ | Concentração elástica $K_t \approx 1{,}26$ |
| **Margem de Segurança ($MS_{\text{yield}}$)**| $+0{,}56$ | $+0{,}102$ (entalhe) / $+1{,}56$ (nominal) | Aprovado ($MS > 0$, limite $184{,}0\text{ MPa}$) |
| **Dano de Fadiga Steinberg ($D$)** | $0{,}182$ | $0{,}0458$ | Aprovado no entalhe crítico ($D \ll 0{,}25$) |

---

## 3. Propriedades do Material (AlSi10Mg — Manufatura Aditiva LPBF)
Tratamento térmico de alívio de tensões: 2 horas a $300^\circ\text{C}$.
- **Massa específica ($\rho_s$):** $2670\text{ kg/m}^3$ ($2{,}67\text{ g/cm}^3$)
- **Módulo de elasticidade ($E_s$):** $68{,}0\text{ GPa}$
- **Coeficiente de Poisson do material sólido ($\nu_s$):** $0{,}33$
- **Limite de escoamento ($\sigma_y$):** $230{,}0\text{ MPa}$ (Tensão admissível $\sigma_{\text{adm}} = \sigma_y / 1{,}25 = 184{,}0\text{ MPa}$)
- **Limite de resistência à tração ($\sigma_{uts}$):** $340{,}0\text{ MPa}$
- **Fator de intensidade de tensão limiar ($\Delta K_{th}$):** $2{,}5\text{ MPa}\sqrt{\text{m}}$
- **Tenacidade à fratura ($K_{Ic}$):** $34{,}0\text{ MPa}\sqrt{\text{m}}$
- **Parâmetros de Basquin:** Coeficiente $C = 1{,}2 \times 10^{20}$, expoente $m = 6{,}8$

---

## 4. Requisitos Ambientais e Dinâmicos (NASA GSFC-STD-7000A / GEVS)
- **Rigidez mínima:** Frequência fundamental $f_1 \ge 100{,}0\text{ Hz}$.
- **Assinatura global de vibração aleatória na base:** $G_{\text{rms, base}} = 14{,}1\text{ G}_{\text{rms}}$ ($20\text{ a }2000\text{ Hz}$, $120{,}0\text{ s}$ por eixo ortogonal).
- **Espectro PSD de Qualificação (NASA GEVS):**
  - $20\text{ Hz}$ a $0{,}013\text{ g}^2/\text{Hz}$ ($+3\text{ dB/oitava}$)
  - $50\text{ a }800\text{ Hz}$ (patamar constante): $0{,}080\text{ g}^2/\text{Hz}$
  - $800\text{ a }2000\text{ Hz}$ (rampa descendente): $-6\text{ dB/oitava}$, atingindo $0{,}0053\text{ g}^2/\text{Hz}$ em $2000\text{ Hz}$.
- **Critério de Fadiga Aleatória de Steinberg (3 bandas gaussianas):**
  - Dano acumulado $D = D_{1\sigma} + D_{2\sigma} + D_{3\sigma} \le 0{,}25$ para qualificação de voo (fator de vida $4\times$, NASA-HDBK-7005).
  - **Localização do cálculo:** Avaliado no ponto crítico de máxima concentração de tensões ($\sigma_{3\sigma,\text{notch}} = 166{,}91\text{ MPa}$), resultando em $D = 0{,}0458 \ll 0{,}25$ (margem de vida de $5{,}46\times$).

---

## 5. Fundamentação Física da Atenuação Dinâmica (Regime Sub-Comprimento de Onda)
A atenuação passiva de $-12{,}6\text{ dB}$ ($-76{,}50\%$) na faixa de qualificação ($20 - 2000\text{ Hz}$) decorre de três mecanismos físicos rigorosos no **regime sub-comprimento de onda** ($a/\lambda \le 0{,}006 \ll 1$, onde a dispersão de Bragg é fisicamente impossível):
1. **Descasamento severo de impedância acústica:**
   $$Z_{\text{solid}} = \rho_s c_L \approx 2670 \times 5046 \approx 13{,}47\text{ MPa}\cdot\text{s/m}$$
   $$Z_{\text{eff}} = \rho^* c_{\text{eff}} \approx 1{,}39\text{ MPa}\cdot\text{s/m}$$
   O coeficiente de reflexão de potência na interface trilho-núcleo reflete $> 66\%$ da energia vibratória incidente.
2. **Antirressonâncias locais:** A flexão dinâmica das costelas auxéticas atua como banco de filtros mecânicos ressonantes distribuídos, dissipando energia nas interfaces.
3. **Desacoplamento cinemático por Poisson negativo:** A contração lateral síncrona sob compressão suprime modos de tombamento (*rocking modes*) na base de montagem do payload.

---

## 6. Regras de Design for Additive Manufacturing (DfAM — LPBF)
- **Ângulo mínimo de inclinação sem suportes ($\theta_{\text{overhang}}$):** $\theta_{\text{overhang}} \ge 35{,}0^\circ$ (conservador $\ge 45{,}0^\circ$).
- **Espessura de parede nominal das costelas ($t$):** $t_{\text{min}} = 0{,}50\text{ mm}$, ótimo $t^* = 0{,}613\text{ mm}$.
- **Efeito de Casca (*Skin Effect*) e Rugosidade Superficial L-PBF:**
  - Rugosidade superficial sem usinagem típica: $Ra \in [10, 18]\ \mu\text{m}$ (atingindo $Ra \approx 25\ \mu\text{m}$ em faces inferiores *down-skin*).
  - Espessura mecânica portante efetiva:
    $$t_{\text{mech,eff}} \approx t^* - 2 \cdot Ra \approx 0{,}613 - 2(0{,}025) \approx 0{,}563\text{ mm} \quad (\text{redução de } \sim 8 - 10\%)$$
  - **Pós-processamento obrigatório para voo:** Usinagem por fluxo abrasivo (AFM) ou eletropolimento químico para atingir $Ra < 3{,}2\ \mu\text{m}$.
  - **Reserva estrutural analítica:** A aplicação de um *knockdown factor* conservador de $10\%$ sobre a espessura preserva $MS_{\text{yield}} > 0$ e $D = 0{,}072 \ll 0{,}25$.
- **Canais de drenagem de pó não sinterizado:** Vão livre intercelular $\ge 1{,}50\text{ mm}$, orifícios de evacuação $\phi \ge 2{,}0\text{ mm}$.

---

## 7. Parâmetros da Célula Auxética Reentrante e Otimização
- **Convenção Geométrica Formal:**
  - Ângulo reentrante canônico $\theta^* = 65{,}75^\circ$ medido em relação ao eixo horizontal de base (equivalente ao ângulo de reentrância interna $\phi = 90^\circ - \theta^* = 24{,}25^\circ$, ou deflexão angular negativa $\theta_{\text{def}} = -21{,}40^\circ$ em notação cartesiana de deflexão).
- **Vetor de variáveis ótimas (Candidato \#28 TOPSIS na Fronteira NSGA-II):**
  - $\theta^* = 65{,}75^\circ$ (reentrância interna $24{,}25^\circ$)
  - $t^* = 0{,}613\text{ mm}$
  - $l^* = 10{,}42\text{ mm}$ (comprimento da costela inclinada entre nós)
  - $h^* = 14{,}85\text{ mm}$ (altura da costela vertical entre centros)
- **Reconciliação Multiescala do Coeficiente de Poisson:**
  - **Escala 1 (Micromecânica 2D Celular):** Coeficiente analítico sob flexão pura de costela isolada:
    $$\nu_{yx}^* = -\frac{\sin\theta \cdot (h/l + \sin\theta)}{\cos^2\theta} = -12{,}63 \quad (\text{ou } -13{,}81 \text{ na formulação assintótica preliminar})$$
  - **Escala 2 (Estrutura 3D Macroscópica Homogeneizada):** Chassi tridimensional confinado com 4 trilhos sólidos maciços de $8{,}5 \times 8{,}5\text{ mm}$ e flanges de fixação em AlSi10Mg ($\nu_s = +0{,}33$):
    $$\nu_{\text{eff}} = -0{,}428 \quad (\text{comportamento auxético estrutural efetivo})$$

---

## 8. Metamodelo Neural (Physics-Guided ResNet) e Transparência Computacional
- **Arquitetura:** Rede residual com blocos skip connection, regularização assintótica de Gibson-Ashby e penalidade de monotonicidade de rigidez.
- **Transparência do Dataset DoE:**
  - Espaço de projeto amostrado com 250 pontos via Latin Hypercube Sampling (LHS).
  - As 250 avaliações foram calculadas via kernel elastodinâmico matricial calibrado (`OpenElastodynamicsKernel`, modo `execution_mode: calibrated_proxy`), calibrado rigorosamente contra os decks de alta ordem do Code\_Aster v2021 Lanczos e CalculiX.
  - A fronteira de Pareto e o candidato ótimo \#28 foram **100% revalidados numericamente em modelos volumétricos 3D completos com malha Gmsh Tet10 de 342.800 nós**.
- **Decomposição Transparente do Speedup Computacional:**
  - **Speedup Online (Inferência Instantânea):**
    $$\text{Speedup}_{\text{online}} = \frac{92{,}0\text{ s}}{0{,}000405\text{ s}} \approx 2{,}27 \times 10^5\times \quad (\text{até } 3{,}58 \times 10^5\times \text{ comparado a } 145\text{ s})$$
  - **Speedup Amortizado de Ponta a Ponta (Ciclo Completo de Projeto):**
    $$\text{Speedup}_{\text{amortizado}} = \frac{10.000 \times 92{,}0\text{ s}}{(250 \times 92{,}0\text{ s}) + 35\text{ s} + 4{,}5\text{ s}} \approx \frac{920.000\text{ s}}{23.039{,}5\text{ s}} \approx 39{,}93\times \approx 40{,}0\times$$
    Compacta o tempo de projeto de $10{,}65\text{ dias}$ de simulação contínua para apenas $6{,}40\text{ horas}$.

---

## 9. Maturidade Tecnológica (TRL) e Delimitação Material
- **Classificação Formal de TRL:**
  - **Digital TRL 4 (NASA SP-6105 / ESA):** Esteira analítica e computacional multifísica validada sob perfil de qualificação NASA GEVS.
  - **TRL 3 Avançado de Hardware (ISO 16290:2013):** Formulação analítica e prova de conceito computacional validada em ambiente relevante simulado.
  - **Roadmap para TRL 5:** Fabricação aditiva L-PBF de provetes físicos em AlSi10Mg e teste de vibração em shaker eletrodinâmico de $20\text{ kN}$.
  - **Roadmap para TRL 6:** Montagem integrada do CubeSat em canister dispensador P-POD em câmara de termovácuo (TVAC).
- **Delimitação de Modelos em PLA (Similaridade Incompleta):**
  - Provetes em PLA foram produzidos exclusivamente como modelo conceitual para *fit-check* dimensional, verificação de empacotamento espacial de placas PC/104 e mecanismos de abertura de antenas.
  - Não houve ensaios de caracterização dinâmica em bancada com PLA; qualquer correlação mecânica com a estrutura metálica de voo é formalmente descartada devido à similaridade incompleta.
