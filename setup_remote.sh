#!/usr/bin/env bash
# ==============================================================================
# Script de Configuración de Entorno Conda para el Scraper en Servidor Remoto
# ==============================================================================
set -e

echo "🚀 [1/3] Detectando entorno Conda..."
if ! command -v conda &> /dev/null; then
    if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/anaconda3/etc/profile.d/conda.sh"
    elif [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
        source "/opt/conda/etc/profile.d/conda.sh"
    elif [ -f "$HOME/.bashrc" ]; then
        source "$HOME/.bashrc"
    fi
fi

if ! command -v conda &> /dev/null; then
    echo "❌ Error: 'conda' no fue encontrado. Asegúrate de ejecutar 'source ~/.bashrc' antes."
    exit 1
fi

echo "📦 [2/3] Creando / actualizando el entorno Conda 'gmaps-scraper'..."
if conda info --envs | grep -q "gmaps-scraper"; then
    echo "ℹ️  El entorno 'gmaps-scraper' ya existe. Actualizando paquetes según environment.yml..."
    conda env update -f environment.yml --prune
else
    echo "ℹ️  Creando entorno 'gmaps-scraper'..."
    conda env create -f environment.yml
fi

echo "🌐 [3/3] Activando entorno e instalando navegadores de Playwright..."
eval "$(conda shell.bash hook)"
conda activate gmaps-scraper

# Instalar binarios de Chromium para Playwright
playwright install chromium

echo ""
echo "=============================================================================="
echo "✅ ¡Configuración completada con éxito!"
echo "=============================================================================="
echo "Para activar el entorno ejecuta:"
echo "    conda activate gmaps-scraper"
echo ""
echo "Para correr el Bulk Perfume Scraper (ej. 5000 leads, 6 workers):"
echo "    python bulk_us_perfume_scraper.py 5000 6"
echo ""
echo "O para correrlo en segundo plano (nohup):"
echo "    bash run_bulk_scraper.sh 5000 6"
echo "=============================================================================="
