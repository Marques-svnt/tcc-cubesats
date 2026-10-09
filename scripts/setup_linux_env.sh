#!/usr/bin/env bash
# ==============================================================================
# setup_linux_env.sh
# Script para instalação automatizada de dependências do TCC no Linux (Pop!_OS / Ubuntu)
# Configura: Python venv, pacotes APT (LaTeX TeX Live, Gmsh, CalculiX) e pip requirements
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=================================================================="
echo " Setup Oficial da Stack Open Source e Ambiente de Pesquisa (Linux)"
echo " Projeto: CubeSat 1U - Otimização Estrutural com Metamateriais"
echo "=================================================================="

# 1. Instalação de pacotes do sistema operacional via APT
echo ""
echo ">>> [Passo 1/4] Instalando dependências de sistema via APT..."
echo "Será solicitada sua senha de sudo para a instalação dos pacotes:"

sudo apt-get update
sudo apt-get install -y \
    python3.12-venv \
    python3-pip \
    build-essential \
    gmsh \
    calculix-ccx \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-science \
    texlive-publishers \
    texlive-lang-portuguese \
    texlive-fonts-recommended \
    cm-super

# 2. Configuração do ambiente virtual Python
echo ""
echo ">>> [Passo 2/4] Criando e configurando ambiente virtual Python (.venv)..."
cd "${ROOT_DIR}"
if [ -d ".venv" ]; then
    echo "Ambiente .venv já existente. Atualizando..."
else
    python3 -m venv .venv
    echo "Ambiente .venv criado com sucesso."
fi

# 3. Instalação das dependências Python
echo ""
echo ">>> [Passo 3/4] Instalando pacotes Python científicos em .venv..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Concessão de permissões de execução aos scripts
echo ""
echo ">>> [Passo 4/4] Ajustando permissões de execução nos scripts..."
chmod +x scripts/*.sh 2>/dev/null || true

echo ""
echo "=================================================================="
echo " Instalação concluída com sucesso!"
echo " Para ativar o ambiente virtual: source .venv/bin/activate"
echo " Para compilar a monografia:     ./scripts/compile_monografia.sh"
echo "=================================================================="
