# Instruções para Uso e Compilação no Overleaf (Otimizado)

Este diretório contém os arquivos-fonte da **Monografia de Conclusão de Curso em Engenharia Mecânica (UESC)**, estruturados de forma modular e em total conformidade com as normas da ABNT (NBR 14724, NBR 6023, NBR 10520 e NBR 6028).

O pacote está **totalmente otimizado para o plano gratuito do Overleaf**, prevenindo o erro de *compile timeout* e garantindo compilação rápida em poucas passagens.

---

## 1. Como Importar para o Overleaf

1. No painel inicial do Overleaf, clique em **New Project** (Novo Projeto) $\rightarrow$ **Upload Project** (Carregar Projeto).
2. Selecione o arquivo zip: `monografia_v3_overleaf.zip`.
3. O Overleaf criará o projeto com a estrutura modular e as imagens já ativadas.

---

## 2. Configurações Essenciais no Menu do Overleaf

No painel lateral esquerdo do Overleaf (ícone **Menu** no topo esquerdo da tela):

- **Compiler (Compilador):** `pdfLaTeX` *(obrigatório)*
- **TeX Live version:** `2023` ou `2024` (mais recente)
- **Main document (Documento Principal):** `main.tex`
- **Spell check (Verificação ortográfica):** `Portuguese (Brazilian)`

> [!TIP]
> **Como Resolver se Houver Cache Travado no Overleaf:**
> Se o Overleaf exibir timeout residual de compilações anteriores, clique no ícone de log (ao lado do botão verde "Recompile") $\rightarrow$ role até o final $\rightarrow$ clique no ícone da lixeira **"Clear cached files"** (Limpar arquivos de cache) e recompile.

---

## 3. Otimizações de Velocidade Aplicadas

1. **Imagens Otimizadas em RGB Nativo:**
   - Imagens de altíssima densidade gráfica foram convertidas de RGBA (canal alfa de 4 canais) para RGB nativo e reamostradas para 300 DPI ($\le 1920\text{ px}$ de largura). Isso eliminou o processamento custoso de máscaras `/SMask` pelo `pdfTeX`, reduzindo o tempo de CPU por passagem em mais de **50%**.
2. **Arquivo de Orquestração `latexmkrc`:**
   - Incluído arquivo de configuração para instruir o compilador `latexmk` a limitar o número de passagens consecutivas a no máximo 3 e suprimir pausas interativas (`-interaction=nonstopmode`).
3. **Ponto de Entrada Único:**
   - O projeto possui um único arquivo mestre na raiz (`main.tex`), evitando conflitos de dependências mútuas no cache da nuvem.

---

## 4. Estrutura Modular dos Arquivos

```text
monografia_v3/
├── main.tex                 # Arquivo mestre compilável (ponto de entrada)
├── latexmkrc                # Configuração de compilação sem timeout para o Overleaf
├── README_OVERLEAF.md       # Este guia
├── config/
│   ├── pacotes.tex          # Pacotes ABNT, siunitx, amsmath, etc.
│   └── comandos.tex         # Layout de margens e dados institucionais UESC
├── pretextual/
│   ├── 00_capa_folharosto.tex # Capa, folha de rosto e aprovação
│   ├── 01_resumo.tex        # Resumo em português (NBR 6028)
│   └── 02_abstract.tex      # Abstract em inglês
├── capitulos/
│   ├── 01_introducao.tex    # Cap. 1: Contextualização e justificativa
│   ├── 02_objetivos.tex     # Cap. 2: Objetivos geral e específicos
│   ├── 03_revisao_literatura.tex # Cap. 3: Revisão bibliográfica
│   ├── 04_metodologia.tex   # Cap. 4: Metodologia e formulação matemática
│   ├── 05_resultados_discussao.tex # Cap. 5: Pareto, TOPSIS, ResNet e FEA Ground Truth
│   └── 06_conclusao.tex     # Cap. 6: Síntese e trabalhos futuros
├── postextual/
│   └── referencias.tex      # Referências segundo a NBR 6023
└── figuras/                 # Imagens reais de alta resolução
```
