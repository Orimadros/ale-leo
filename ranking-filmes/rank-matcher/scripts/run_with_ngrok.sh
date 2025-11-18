#!/bin/bash

# Script para executar o app com ngrok

echo "🚀 Iniciando Comparador de Rankings com ngrok..."
echo ""

# Verificar se ngrok está instalado
if ! command -v ngrok &> /dev/null
then
    echo "❌ ngrok não encontrado!"
    echo "Por favor, instale o ngrok em: https://ngrok.com/download"
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

# Iniciar ngrok
echo "🌐 Iniciando túnel ngrok..."
ngrok http 8501

# Cleanup ao sair
kill $STREAMLIT_PID
