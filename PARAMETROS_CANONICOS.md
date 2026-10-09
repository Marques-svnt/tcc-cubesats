# Matriz Canônica de Parâmetros de Engenharia (TCC CubeSat 1U)
**Projeto:** CubeSat em Baixa Órbita: Otimização de Volume e Geometria para Maximização de Desempenho Estrutural e Funcional  
**Autor:** Gabriel Marques de Andrade | **Orientadora:** Prof.ª Dr.ª Nila Cecília de Faria Lopes Medeiros  
**Instituição:** Universidade Estadual de Santa Cruz (UESC) — Colegiado de Engenharia Mecânica  

---

## 1. Geometria e Envelope Estrutural
- **Padrão:** CubeSat Design Specification (Cal Poly, Rev. 14 / P-POD).
- **Fator de forma:** 1U.
- **Dimensões externas nominais:** $100{,}0 \times 100{,}0 \times 113{,}5\text{ mm}$ ($\pm 0{,}1\text{ mm}$).
- **Trilhos guia (Rails):** $8{,}5 \times 8{,}5\text{ mm}$ sólidos monolíticos contínuos nas 4 arestas longitudinais.
  - Raios de concordância: $R \ge 1{,}0\text{ mm}$.
  - Rugosidade superficial: $Ra \le 1{,}6\text{ \mu m}$ (atrito e deslizamento contra o deployer P-POD).
  - Tratamento superficial: Anodização dura tipo III (PTFE impregnado) nos trilhos.

---

## 2. Orçamento de Massa e Desempenho Comparativo
| Parâmetro | Chassi Monolítico Convencional (Al 6061-T6) | Chassi Auxético Ótimo Proposto (AlSi10Mg) | Variação / Ganho |
| :--- | :---: | :---: | :---: |
| **Massa Estrutural** | $0{,}308\text{ kg}$ ($308\text{ g}$) | $0{,}116\text{ kg}$ ($116\text{ g}$) | **$-62{,}49\%$** |
| **Frequência Fundamental ($f_1$)** | $412{,}10\text{ Hz}$ | $579{,}62\text{ Hz}$ | **$+40{,}65\%$** (GEVS $\ge 100\text{ Hz}$) |
| **Transmissibilidade ($T$)** | $1{,}66$ | $0{,}39$ | **$-76{,}50\%$** ($-12{,}6\text{ dB}$) |
| **Aceleração RMS Payload** | $23{,}4\text{ G}_{\text{rms}}$ | $5{,}5\text{ G}_{\text{rms}}$ | **$-76{,}50\%$** |
| **Tensão de Pico ($3\sigma$)** | $112{,}4\text{ MPa}$ | $68{,}8\text{ MPa}$ | **$-38{,}79\%$** |
| **Margem de Segurança ($MS_{\text{yield}}$)**| $+0{,}56$ | $+1{,}56$ | Aprovado ($MS > 0$) |
| **Dano de Fadiga Steinberg ($D$)** | $0{,}182$ | $0{,}046$ | Aprovado ($D \ll 0{,}25$) |

---

## 3. Propriedades do Material (AlSi10Mg — Manufatura Aditiva LPBF)
Tratamento térmico de alívio de tensões: 2 horas a $300^\circ\text{C}$.
- **Massa específica ($\rho_s$):** $2670\text{ kg/m}^3$ ($2{,}67\text{ g/cm}^3$)
- **Módulo de elasticidade ($E_s$):** $68{,}0\text{ GPa}$
- **Coeficiente de Poisson ($\nu_s$):** $0{,}33$
- **Limite de escoamento ($\sigma_y$):** $220{,}0\text{ MPa}$
- **Limite de resistência à tração ($\sigma_{uts}$):** $345{,}0\text{ MPa}$
- **Fator de intensidade de tensão limiar ($\Delta K_{th}$):** $2{,}5\text{ MPa}\sqrt{\text{m}}$

---

## 4. Requisitos Ambientais e Dinâmicos (NASA GSFC-STD-7000A / GEVS)
- **Rigidez mínima:** Frequência fundamental $f_1 \ge 100{,}0\text{ Hz}$.
- **Assinatura global de vibração aleatória na base:** $G_{\text{rms, base}} = 14{,}1\text{ G}_{\text{rms}}$ ($20\text{ a }2000\text{ Hz}$).
- **Espectro PSD de Qualificação (NASA GEVS):**
  - $20\text{ Hz}$ a $0{,}013\text{ g}^2/\text{Hz}$ ($+3\text{ dB/oitava}$)
  - $50\text{ a }800\text{ Hz}$ (patamar constante): $0{,}080\text{ g}^2/\text{Hz}$
  - $800\text{ a }2000\text{ Hz}$ (rampa descendente): $-6\text{ dB/oitava}$, atingindo $0{,}0053\text{ g}^2/\text{Hz}$ em $2000\text{ Hz}$.
- **Critério de Fadiga Aleatória de Steinberg (3 bandas gaussianas):**
  - Dano acumulado $D = D_{1\sigma} + D_{2\sigma} + D_{3\sigma} \le 0{,}25$ para qualificação de voo.

---

## 5. Regras de Design for Additive Manufacturing (DfAM — LPBF)
- **Ângulo mínimo de inclinação sem suportes ($\theta_{\text{overhang}}$):**
  - Limite inferior admissível no espaço de busca: $\theta_{\text{overhang}} \ge 35{,}0^\circ$.
  - Diretriz conservadora recomendada: $\ge 45{,}0^\circ$ (sem necessidade de estruturas de ancoragem sacrificial).
- **Espessura de parede das costelas ($t$):**
  - Limite inferior do processo: $t_{\text{min}} = 0{,}50\text{ mm}$ (para resolução do feixe de laser de $\sim 100\text{ \mu m}$).
  - Faixa de variação paramétrica na otimização: $0{,}50\text{ mm} \le t \le 1{,}80\text{ mm}$.
- **Canais de drenagem de pó não sinterizado:**
  - Vão livre intercelular: $\ge 1{,}50\text{ mm}$.
  - Furos de evacuação nos painéis fechados: $\phi \ge 2{,}0\text{ mm}$.

---

## 6. Parâmetros da Célula Auxética Reentrante e Otimização
- **Vetor de variáveis:** $\mathbf{x} = [\theta, t, l, h]^\top$
  - Ângulo reentrante $\theta$: $50{,}0^\circ \le \theta \le 85{,}0^\circ$
  - Espessura $t$: $0{,}50\text{ mm} \le t \le 1{,}80\text{ mm}$
  - Comprimento da costela inclinada $l$: $6{,}00\text{ mm} \le l \le 15{,}00\text{ mm}$
  - Altura da costela vertical $h$: $8{,}00\text{ mm} \le h \le 20{,}00\text{ mm}$
- **Ponto Ótimo de Voo (Solução TOPSIS na Fronteira de Pareto NSGA-II):**
  - $\theta^* = 65{,}75^\circ$
  - $t^* = 0{,}613\text{ mm}$
  - $l^* = 10{,}42\text{ mm}$
  - $h^* = 14{,}85\text{ mm}$
  - Coeficiente de Poisson efetivo: $\nu_{\text{eff}} = -13{,}81$

---

## 7. Modelo Substituto Neural (*Physics-Guided ResNet*)
- **Arquitetura:** Rede residual com blocos skip connection e regularização física baseada nas equações de escala de Gibson-Ashby.
- **Dataset:** 250 simulações de alta ordem (Code\_Aster e Gmsh Tet10 em Linux/WSL) orquestradas via LangGraph determinístico.
- **Métricas:** $\overline{R^2} = 0{,}9874$, RMSE $= 0{,}0182$.
- **Tempo de inferência:** $0{,}405\text{ ms}$ (aceleração $> 200.000\times$ em relação ao ciclo FEA completo de $\sim 92\text{ s}$).
