#!/usr/bin/env bash
# ==============================================================================
# Script para correr Bulk US Perfume Scraper en segundo plano (nohup)
# Uso: bash run_bulk_scraper.sh [CANTIDAD_LEADS] [NUM_WORKERS]
# Ejemplo: bash run_bulk_scraper.sh 5000 6
# ==============================================================================

LEADS=${1:-30000}
WORKERS=${2:-128}





# Encontrar el binario exacto de Python en Conda
PYTHON_BIN="python"
if [ -f "/opt/miniconda/envs/gmaps-scraper/bin/python" ]; then
    PYTHON_BIN="/opt/miniconda/envs/gmaps-scraper/bin/python"
elif [ -f "$HOME/miniconda3/envs/gmaps-scraper/bin/python" ]; then
    PYTHON_BIN="$HOME/miniconda3/envs/gmaps-scraper/bin/python"
elif [ -f "$HOME/anaconda3/envs/gmaps-scraper/bin/python" ]; then
    PYTHON_BIN="$HOME/anaconda3/envs/gmaps-scraper/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="$(command -v python3)"
fi

echo "=============================================================================="
echo "🚀 Iniciando Bulk Scraper en segundo plano..."
echo "📊 Objetivo: $LEADS leads | ⚡ Procesos Paralelos: $WORKERS workers"
echo "🐍 Python: $PYTHON_BIN"
echo "📄 Logs en tiempo real guardándose en: scraper.log"
echo "=============================================================================="

nohup "$PYTHON_BIN" -u bulk_us_perfume_scraper.py "$LEADS" "$WORKERS" > scraper.log 2>&1 &
SCRAPER_PID=$!


echo "✅ Scraper ejecutándose con PID: $SCRAPER_PID"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs en vivo:        tail -f scraper.log"
echo "  - Ver progreso de leads:   grep '✅' scraper.log"
echo "  - Detener scraper:         kill $SCRAPER_PID"
echo "=============================================================================="
