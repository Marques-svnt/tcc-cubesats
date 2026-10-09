#!/usr/bin/env bash
# ==============================================================================
# compile_monografia.sh
# Script de automação para compilação limpa da monografia de TCC em LaTeX
# Compatível com Linux (Pop!_OS / Ubuntu) e TeX Live
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MONO_DIR="${ROOT_DIR}/monografia"

echo "=== [1/3] Limpando arquivos auxiliares antigos em monografia/ ==="
cd "${MONO_DIR}"
rm -f *.aux *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk *.synctex.gz
find 01-elementos-pre-textuais 02-elementos-textuais 03-elementos-pos-textuais -name "*.aux" -delete 2>/dev/null || true

echo "=== [2/3] Executando compilação com pdflatex (3 passadas para referências cruzadas) ==="
pdflatex -interaction=nonstopmode Main.tex > pdflatex_pass1.log 2>&1 || {
    echo "ERRO: Falha na 1ª passada do pdflatex. Verifique pdflatex_pass1.log"
    tail -n 30 pdflatex_pass1.log
    exit 1
}

pdflatex -interaction=nonstopmode Main.tex > pdflatex_pass2.log 2>&1 || {
    echo "ERRO: Falha na 2ª passada do pdflatex. Verifique pdflatex_pass2.log"
    tail -n 30 pdflatex_pass2.log
    exit 1
}

pdflatex -interaction=nonstopmode Main.tex > pdflatex_pass3.log 2>&1 || {
    echo "ERRO: Falha na 3ª passada do pdflatex. Verifique pdflatex_pass3.log"
    tail -n 30 pdflatex_pass3.log
    exit 1
}

echo "=== [3/3] Atualizando PDF final na raiz do projeto ==="
if [ -f "Main.pdf" ]; then
    cp Main.pdf "${ROOT_DIR}/monografia_tcc_final.pdf"
    echo "SUCESSO: Monografia compilada com êxito!"
    echo "Arquivo gerado: ${ROOT_DIR}/monografia_tcc_final.pdf"
    ls -lh "${ROOT_DIR}/monografia_tcc_final.pdf"
else
    echo "ERRO: Main.pdf não foi gerado."
    exit 1
fi
