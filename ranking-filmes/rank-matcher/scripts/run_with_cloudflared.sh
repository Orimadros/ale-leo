#!/bin/bash

# Script para executar o app com cloudflared

echo "🚀 Iniciando Comparador de Rankings com cloudflared..."
echo ""

# Verificar se cloudflared está instalado
if ! command -v cloudflared &> /dev/null
then
    echo "❌ cloudflared não encontrado!"
    echo "Por favor, instale o cloudflared:"
    echo "  Mac: brew install cloudflared"
    echo "  Linux: https://github.com/cloudflare/cloudflared/releases"
    exit 1
fi

# Verificar se Streamlit está instalado
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit não encontrado!"
    echo "Instalando Streamlit..."
    pip install streamlit
fi

# Iniciar Streamlit em background
echo "📱 Iniciando Streamlit na porta 8501..."
streamlit run app.py &
STREAMLIT_PID=$!

# Aguardar Streamlit iniciar
sleep 3

# Iniciar cloudflared
echo "🌐 Iniciando túnel Cloudflare..."
cloudflared tunnel --url http://localhost:8501

# Cleanup ao sair
kill $STREAMLIT_PID
