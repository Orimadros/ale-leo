#!/bin/bash

# Script para instalar dependências do Comparador de Rankings

echo "🎬 Instalando dependências do Comparador de Rankings..."

# Instalar Streamlit
pip install streamlit

echo "✅ Instalação concluída!"
echo ""
echo "Para executar o aplicativo:"
echo "  streamlit run app.py"
echo ""
echo "Para tornar acessível externamente:"
echo "  Opção 1 - ngrok: ngrok http 8501"
echo "  Opção 2 - cloudflared: cloudflared tunnel --url http://localhost:8501"
