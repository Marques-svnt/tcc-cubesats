# ADR 0005: Integração do Pipeline CAD B-Rep (build123d/OpenCASCADE), Malhador Gmsh Tet10 e Qualificação Espectral NASA GEVS

**Status:** Aprovado / Implementado  
**Data:** 2026-10-10  
**Contexto:** Trabalho de Conclusão de Curso (TCC) - Engenharia Mecânica / Aeroespacial (UESC 2026)  
**Autor:** Gabriel Marques de Andrade  

---

## 1. Contexto e Motivação

Durante a avaliação de repositórios técnicos abertos (conversa `Avaliação de Repositórios para Pesquisa`), identificou-se a necessidade de superar as limitações dos scripts simplificados de CAD e da ausência de modelagem B-Rep determinística no ambiente Linux (sem dependência de SolidWorks GUI ou FreeCAD interativo).

O motor legado (`cadquery_engine.py`) dependia da biblioteca `cadquery`, que não estava instalada no ambiente nativo Linux, forçando a esteira a recorrer a arquivos STEP analíticos sintéticos. Além disso, a geração de malha no Gmsh não consumia geometrias B-Rep tridimensionais completas com trilhos de deployer CalPoly e restrições de manufatura aditiva (DfAM LPBF em AlSi10Mg).

## 2. Decisão Arquitetural

Adotou-se formalmente a pilha técnica moderna de código aberto para a esteira do TCC (`cubesat-tcc-opt`):

1. **Modelagem B-Rep e CAD Paramétrico (`build123d` + OpenCASCADE):**
   - Substituição do CadQuery clássico por `build123d==0.7.0` sobre `cadquery-ocp==7.8.1.post1`.
   - Implementação da geração paramétrica do **Chassi CubeSat 1U Canônico de Voo** (`Build123dEngine.generate_1u_flight_chassis`):
     - Envelope CalPoly $100.0 \times 100.0 \times 113.5\text{ mm}$.
     - 4 trilhos longitudinais maciços de deployer ($8.5 \times 8.5\text{ mm}$) ao longo do eixo Z.
     - Janelas de corte lateral autossuportadas com ângulo $\theta \ge 35^\circ$.
     - Orifícios de despoeiramento e evacuação de pó residual AlSi10Mg ($d_{\text{drain}} \ge 2.0\text{ mm}$, adotado $3.5\text{ mm}$).
     - Extração exata de propriedades físicas ($V, M, \text{CoG}, \rho_{\text{rel}}$) via kernel OpenCASCADE.
     - Exportação determinística para STEP AP214 e malhas trianguladas STL.

2. **Discretização em Elementos Finitos Tet10 (`Gmsh 4.12.1`):**
   - Implementação do método `mesh_step_model` no `GmshMeshGenerator`, invocando diretamente o binário `/usr/bin/gmsh` no Linux.
   - Geração de malhas volumétricas 3D de 2ª ordem compostas por tetraedros quadráticos de 10 nós (tipo 11 na especificação Gmsh 2.2 / C3D10).
   - Extração automática de métricas de convergência de malha e verificação de distorção de elementos.

3. **Metamateriais Celulares e Leis de Escala de Gibson-Ashby (`tpms_lattice.py`):**
   - Avaliação contínua de superfícies mínimas periódicas triplas (TPMS: Gyroid, Schwarz Primitive, Diamond).
   - Equações de homogeneização mecânica efetiva para sólidos celulares sob flexão de costelas:
     $$E^* = E_s \cdot C_1 \cdot \left(\frac{\rho^*}{\rho_s}\right)^{n_1}, \quad \sigma_y^* = \sigma_{ys} \cdot C_2 \cdot \left(\frac{\rho^*}{\rho_s}\right)^{n_2}$$
   - Formulação de campos de densidade funcionalmente gradada (FGL - *Functionally Graded Lattice*) ao longo do eixo Z para atenuação de choque e vibração nas interfaces do payload.

4. **Qualificação Espectral NASA GEVS e Formato Aeroespacial pyNastran (`nasa_gevs_utils.py`):**
   - Implementação analítica da curva de Densidade Espectral de Potência (PSD) da norma **NASA GSFC-STD-7000A / GEVS** ($20\text{ Hz}$ a $2000\text{ Hz}$, $14.1\text{ G}_{\text{rms}}$) com interpolação log-log exata entre *breakpoints*.
   - Estimativa da resposta estocástica em ressonância via Equação de Miles:
     $$G_{\text{rms}} = \sqrt{\frac{\pi}{2} f_n Q \cdot \text{PSD}(f_n)}$$
   - Módulo de exportação de cartões de dados volumétricos da NASA em formato Nastran BDF (`GRID`, `CTETRA`, `MAT1`, `PSOLID`, `SPC1`) com compatibilidade retroativa para NumPy 2.0+.

## 3. Consequências e Resultados

- **Autonomia Total em Linux:** Elimina dependências de licenças proprietárias do SolidWorks COM para geração de geometrias B-Rep complexas de voo.
- **Convergência Numérica Comprovada:** O Gmsh gera malhas Tet10 de 2ª ordem a partir dos arquivos STEP exportados em menos de $0.15\text{ s}$, sem elementos degenerados ou com jacobiano não-positivo.
- **Suíte de Testes 100% Aprovada:** 94 testes unitários e de integração aprovados no TCC, 59 aprovados no IC, e sincronização contínua com o Obsidian Vault.

---
*Referências: NASA GSFC-STD-7000A, NASA-STD-5020, CalPoly CubeSat Design Spec Rev. 14, Gibson & Ashby (1997).*
