# 🎬 Comparador de Rankings - Rank Matcher

Aplicativo Streamlit para comparar suas classificações de filmes de Harry Potter ou Star Wars com os perfis de Ale e Leo.

## 📋 Requisitos

- Python 3.7+
- Streamlit

## 🚀 Instalação

1. Instale as dependências:
\`\`\`bash
pip install streamlit
\`\`\`

2. Execute o aplicativo:
\`\`\`bash
streamlit run app.py
\`\`\`

## 🌐 Tornar o App Acessível Externamente

Para compartilhar seu aplicativo Streamlit rodando em localhost com usuários externos, você pode usar **ngrok** ou **cloudflared**.

### Opção 1: Usando ngrok

#### Instalação do ngrok

**Windows/Mac/Linux:**
1. Baixe o ngrok em: https://ngrok.com/download
2. Extraia o arquivo e adicione ao PATH do sistema
3. Crie uma conta gratuita em https://ngrok.com/signup
4. Autentique com seu token:
\`\`\`bash
ngrok config add-authtoken SEU_TOKEN_AQUI
\`\`\`

#### Uso do ngrok

1. Execute seu aplicativo Streamlit (geralmente na porta 8501):
\`\`\`bash
streamlit run app.py
\`\`\`

2. Em outro terminal, execute o ngrok:
\`\`\`bash
ngrok http 8501
\`\`\`

3. O ngrok fornecerá uma URL pública (ex: `https://abc123.ngrok.io`)
4. Compartilhe esta URL com usuários externos!

**Nota:** A versão gratuita do ngrok gera URLs aleatórias que mudam a cada execução.

---

### Opção 2: Usando Cloudflare Tunnel (cloudflared)

#### Instalação do cloudflared

**Windows:**
\`\`\`bash
# Usando winget
winget install --id Cloudflare.cloudflared
\`\`\`

**Mac:**
\`\`\`bash
brew install cloudflared
\`\`\`

**Linux:**
\`\`\`bash
# Debian/Ubuntu
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
\`\`\`

#### Uso do cloudflared

1. Execute seu aplicativo Streamlit:
\`\`\`bash
streamlit run app.py
\`\`\`

2. Em outro terminal, crie um túnel:
\`\`\`bash
cloudflared tunnel --url http://localhost:8501
\`\`\`

3. O cloudflared fornecerá uma URL pública (ex: `https://xyz.trycloudflare.com`)
4. Compartilhe esta URL com usuários externos!

**Vantagens do cloudflared:**
- Não requer cadastro ou autenticação
- Gratuito e sem limites
- URLs mais estáveis

---

## 🎮 Como Usar o App

1. **Página Inicial:** Escolha entre Harry Potter ou Star Wars
2. **Classificação:** Atribua posições únicas (1 = favorito) para cada filme
3. **Resultados:** Veja suas pontuações de similaridade com Ale e Leo!

## 📊 Métricas Utilizadas

- **Distância de Levenshtein:** Mede diferenças na ordem das sequências
- **WMAPE (Weighted Mean Absolute Percentage Error):** Mede diferenças nas posições dos rankings
- **Pontuação Final:** Média das similaridades de ambas as métricas

## 🔧 Solução de Problemas

### Porta já em uso
Se a porta 8501 estiver ocupada, especifique outra porta:
\`\`\`bash
streamlit run app.py --server.port 8502
\`\`\`

E ajuste o comando do túnel:
\`\`\`bash
# ngrok
ngrok http 8502

# cloudflared
cloudflared tunnel --url http://localhost:8502
\`\`\`

### Firewall bloqueando conexões
Certifique-se de que seu firewall permite conexões de saída nas portas usadas pelo Streamlit e pelos túneis.

## 📝 Licença

Este projeto é de código aberto e está disponível para uso pessoal e educacional.
