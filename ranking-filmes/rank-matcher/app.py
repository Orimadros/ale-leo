import streamlit as st
from typing import Dict, List, Tuple, Optional

# ============================================================================
# CONSTANTES - Conjuntos de dados de filmes
# ============================================================================

HP_TITLES = {
    "HP1": "HP1: A Pedra Filosofal",
    "HP2": "HP2: A Câmara Secreta",
    "HP3": "HP3: O Prisioneiro de Azkaban",
    "HP4": "HP4: O Cálice de Fogo",
    "HP5": "HP5: A Ordem da Fênix",
    "HP6": "HP6: O Enigma do Príncipe",
    "HP7": "HP7: As Relíquias da Morte Parte 1",
    "HP8": "HP8: As Relíquias da Morte Parte 2"
}

SW_TITLES = {
    "SW1": "SW1: A Ameaça Fantasma",
    "SW2": "SW2: Ataque dos Clones",
    "SW3": "SW3: A Vingança dos Sith",
    "SW4": "SW4: Uma Nova Esperança",
    "SW5": "SW5: O Império Contra-Ataca",
    "SW6": "SW6: O Retorno de Jedi",
    "SW7": "SW7: O Despertar da Força",
    "SW8": "SW8: Os Últimos Jedi",
    "SW9": "SW9: A Ascensão Skywalker",
    "SWX": "Rogue One: Uma História Star Wars"
}

# Perfis padrão
DEFAULT_RANKINGS = {
    "hp": {
        "Ale": ["HP2", "HP4", "HP1", "HP3", "HP5", "HP7", "HP8", "HP6"],
        "Leo": ["HP6", "HP4", "HP5", "HP3", "HP1", "HP7", "HP8", "HP2"]
    },
    "sw": {
        "Ale": ["SW5", "SW6", "SW7", "SW4", "SW1", "SW8", "SWX", "SW3", "SW9", "SW2"],
        "Leo": ["SW5", "SW6", "SW3", "SWX", "SW4", "SW1", "SW2", "SW7", "SW8", "SW9"]
    }
}

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================


def get_titles(saga: str) -> Dict[str, str]:
    """Obter dicionário de títulos para uma saga."""
    return HP_TITLES if saga == "hp" else SW_TITLES


def get_defaults(saga: str) -> Dict[str, List[str]]:
    """Obter classificações padrão para uma saga."""
    return DEFAULT_RANKINGS[saga]


def to_codes(seq: List[str], saga: str) -> List[str]:
    """Converter títulos para códigos, filtrando desconhecidos."""
    titles = get_titles(saga)
    code_set = set(titles.keys())
    return [item for item in seq if item in code_set]


def ranks_map(seq: List[str]) -> Dict[str, int]:
    """Converter sequência para {código: classificação baseada em 1} mapeamento."""
    return {code: idx + 1 for idx, code in enumerate(seq)}


def levenshtein_seq(a: List[str], b: List[str]) -> int:
    """
    Computar distância de Levenshtein entre duas sequências usando programação dinâmica.
    Inserir/excluir/substituir custam 1.
    """
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # exclusão
                    dp[i][j-1],    # inserção
                    dp[i-1][j-1]   # substituição
                )
    return dp[m][n]


def wmape_on_ranks(ref_seq: List[str], cmp_seq: List[str]) -> float:
    """
    Computar WMAPE nas classificações sobre a interseção de itens.
    Retorna NaN se não houver itens comuns.
    """
    r1 = ranks_map(ref_seq)
    r2 = ranks_map(cmp_seq)
    common = set(r1.keys()) & set(r2.keys())
    if not common:
        return float('nan')
    abs_err = sum(abs(r1[it] - r2[it]) for it in common)
    denominator = sum(r1[it] for it in common)
    if denominator == 0:
        return float('nan')
    return abs_err / denominator


def similarity_from_wmape(w: float) -> float:
    """Converter WMAPE para pontuação de similaridade (1 - w), limitada a [0,1]."""
    if w != w:  # NaN
        return float('nan')
    return max(0.0, min(1.0, 1.0 - w))


def compare_one(input_codes: List[str], ref_codes: List[str], saga: str) -> Dict:
    """
    Comparar classificação do usuário contra um perfil de referência.
    Retorna dict com pontuação, métricas de Levenshtein e métricas de WMAPE.
    """
    titles = get_titles(saga)
    n_total = len(titles)

    lev_dist = levenshtein_seq(input_codes, ref_codes)
    lev_norm = lev_dist / n_total if n_total > 0 else 0.0
    lev_sim = 1.0 - lev_norm

    wmape = wmape_on_ranks(ref_codes, input_codes)
    wmape_sim = similarity_from_wmape(wmape)

    if wmape_sim != wmape_sim:  # wmape_sim é NaN
        score = lev_sim
    elif lev_sim != lev_sim:  # improvável
        score = wmape_sim
    else:
        score = (lev_sim + wmape_sim) / 2.0

    return {
        "score": score,
        "levenshtein_distance": lev_dist,
        "levenshtein_normalized": lev_norm,
        "levenshtein_similarity": lev_sim,
        "wmape": wmape,
        "wmape_similarity": wmape_sim
    }

# =======================
# Helpers de apresentação
# =======================


def margin_text(m: int) -> str:
    if m < 5:
        return "diferença pequena"
    if m < 15:
        return "diferença considerável"
    return "diferença grande"


def topk_overlap(user: List[str], ref: List[str], k: int = 3):
    u_top = set(user[:k])
    r_top = set(ref[:k])
    u_bottom = set(user[-k:])
    r_bottom = set(ref[-k:])
    strong_agree = list(u_top & r_top)
    strong_disagree = []
    for x in user[:k]:
        if x in r_bottom:
            strong_disagree.append((x, "top_vs_bottom"))
    for x in user[-k:]:
        if x in r_top:
            strong_disagree.append((x, "bottom_vs_top"))
    return strong_agree, strong_disagree

# ---------------------------------
# Helper visual "tenebroso" (Leo)
# ---------------------------------


def spooky_banner(texto: str = "💀 Algo estranho aconteceu…"):
    st.markdown(
        """
        <style>
        @keyframes spookyPulse {
            0%   { background: #0f0f0f; color: #ff4d4f; box-shadow: 0 0 0px #000; }
            50%  { background: #1a0000; color: #ffffff; box-shadow: 0 0 16px #7a0000; }
            100% { background: #0f0f0f; color: #ff4d4f; box-shadow: 0 0 0px #000; }
        }
        .spooky {
            border: 1px solid #ff4d4f;
            border-radius: 12px;
            padding: 14px 16px;
            text-align: center;
            font-weight: 700;
            letter-spacing: .2px;
            animation: spookyPulse 1.2s ease-in-out infinite;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(f'<div class="spooky">{texto}</div>', unsafe_allow_html=True)


# ============================================================================
# INICIALIZAÇÃO DO ESTADO DA SESSÃO
# ============================================================================


def init_session_state():
    """Inicializar variáveis do estado da sessão."""
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'
    if 'saga' not in st.session_state:
        st.session_state['saga'] = None
    if 'user_ranking' not in st.session_state:
        st.session_state['user_ranking'] = None

# ============================================================================
# VISUALIZAÇÃO 1: INÍCIO
# ============================================================================


def show_home():
    """Exibe a página inicial com seleção de saga."""
    st.title("🎬 Comparador de Rankings")
    st.markdown("### Compare seus rankings de filmes com Ale e Leo!")
    st.markdown(
        "Escolha uma saga para classificar e veja o quanto seu gosto combina.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ Rankear Harry Potter", use_container_width=True, type="primary"):
            st.session_state['saga'] = 'hp'
            st.session_state['page'] = 'ranking'
            st.rerun()
    with col2:
        if st.button("🌟 Rankear Star Wars", use_container_width=True, type="primary"):
            st.session_state['saga'] = 'sw'
            st.session_state['page'] = 'ranking'
            st.rerun()

# ============================================================================
# VISUALIZAÇÃO 2: CLASSIFICAÇÃO
# ============================================================================


def show_ranking():
    """Exibe a interface de classificação com tabela interativa."""
    saga = st.session_state['saga']
    titles = get_titles(saga)
    codes = sorted(titles.keys())

    saga_name = "Harry Potter" if saga == "hp" else "Star Wars"
    st.title(f"📊 Classifique os Filmes de {saga_name}")
    st.markdown(
        f"Atribua uma classificação única (1-{len(codes)}) para cada filme. (1 = seu favorito!)")

    if 'ranking_data' not in st.session_state or st.session_state.get('last_saga') != saga:
        st.session_state['ranking_data'] = {code: None for code in codes}
        st.session_state['last_saga'] = saga

    st.markdown("---")
    st.markdown("### Suas Classificações")

    for code in codes:
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            st.markdown(f"**{code}**")
        with col2:
            rank = st.number_input(
                "Posição",
                min_value=1,
                max_value=len(codes),
                value=st.session_state['ranking_data'][code],
                key=f"rank_{code}",
                label_visibility="collapsed"
            )
            st.session_state['ranking_data'][code] = rank
        with col3:
            st.markdown(titles[code])

    st.markdown("---")

    ranks = [st.session_state['ranking_data'][code] for code in codes]
    all_filled = all(r is not None for r in ranks)
    unique_ranks = len(ranks) == len(set(ranks)) if all_filled else True

    if not all_filled:
        st.warning("⚠️ Por favor, preencha todas as posições antes de enviar.")
    elif not unique_ranks:
        st.error(
            "❌ Cada posição deve ser única! Por favor, corrija as posições duplicadas.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🏠 Voltar ao Início", use_container_width=True):
            st.session_state['page'] = 'home'
            st.rerun()
    with col2:
        if st.button("✅ Enviar Classificações", use_container_width=True, type="primary", disabled=not (all_filled and unique_ranks)):
            sorted_codes = sorted(
                codes, key=lambda c: st.session_state['ranking_data'][c])
            st.session_state['user_ranking'] = sorted_codes
            st.session_state['page'] = 'results'
            st.rerun()

# =======================
# VISUALIZAÇÃO 3: RESULTADOS
# =======================


def show_results():
    """Exibe resultados em formato amigável (%), narrativa e detalhes técnicos opcionais."""
    import pandas as pd

    saga = st.session_state['saga']
    user_ranking = st.session_state['user_ranking']
    defaults = get_defaults(saga)
    titles = get_titles(saga)
    saga_name = "Harry Potter" if saga == "hp" else "Star Wars"

    # --- Cálculo (mantém a lógica original) ---
    ale_result = compare_one(user_ranking, defaults['Ale'], saga)
    leo_result = compare_one(user_ranking, defaults['Leo'], saga)

    compat_ale = int(round(ale_result['score'] * 100))
    compat_leo = int(round(leo_result['score'] * 100))

    if compat_ale > compat_leo:
        winner = "Ale"
        lead, lag = compat_ale, compat_leo
    elif compat_leo > compat_ale:
        winner = "Leo"
        lead, lag = compat_leo, compat_ale
    else:
        winner = "Empate"
        lead, lag = compat_ale, compat_leo

    margin = abs(compat_ale - compat_leo)

    # --- Animação / efeito condicional ---
    if winner == "Ale":
        st.balloons()  # celebração feliz
    elif winner == "Leo":
        spooky_banner("Match maior com Leo… que gosto questionável...")

    # --- Cabeçalho ---
    st.title(f"Compatibilidade de Preferências — {saga_name}")

    if winner == "Empate":
        st.subheader(f"🤝 Empate técnico ({compat_ale}% vs {compat_leo}%)")
    else:
        st.subheader(
            f"🎉 Você combina mais com **{winner}**"
            if winner == "Ale" else
            f"Você combina mais com **{winner}**"
        )

    # --- Painel rápido (limpo) ---
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Ale", f"{compat_ale}%")
    with c2:
        st.metric("Leo", f"{compat_leo}%")

    diff = abs(compat_ale - compat_leo)
    emoji = "🔥" if diff > 20 else "✨" if diff > 10 else "🤝"
    st.caption(f"{emoji} Diferença de {diff} pontos percentuais")

    st.markdown("---")

    # --- Narrativa de acordos/desacordos ---
    st.markdown("### 📚 Resumo qualitativo")

    def narrativa(user_ranking, ref_ranking, ref_name):
        agree, disagree = topk_overlap(user_ranking, ref_ranking, k=3)
        if agree:
            st.write(f"🎯 **Acordos fortes com {ref_name}:** " +
                     ", ".join(titles[x] for x in agree))
        if disagree:
            itens = [titles[x] for x, _ in disagree[:3]]
            st.write(f"⚖️ **Diferenças marcantes com {ref_name}:** " +
                     ", ".join(itens))
        if not agree and not disagree:
            st.write(
                "ℹ️ Preferências equilibradas — sem acordos ou diferenças fortes no Top/Bottom-3.")

    narrativa(user_ranking, defaults['Ale'], "Ale")
    narrativa(user_ranking, defaults['Leo'], "Leo")

    st.markdown("---")

    # --- Gráfico simples em % ---
    st.markdown("### 📊 Comparação de Compatibilidade (%)")
    st.bar_chart({"Ale": compat_ale, "Leo": compat_leo})

    st.markdown("---")

    # --- Detalhes técnicos (expander) ---
    with st.expander("🔎 Como calculamos (detalhes técnicos)"):
        st.write(
            "A compatibilidade é a **média** de duas medidas normalizadas (0–1): "
            "**similaridade de Levenshtein** entre sequências e **similaridade derivada do WMAPE** de posições. "
            "Convertida para % para facilitar a leitura."
        )
        st.write(
            "- **Levenshtein**: quantas operações (inserir/remover/substituir) para transformar um ranking no outro, "
            "normalizado pelo total de filmes.\n"
            "- **WMAPE**: quão diferentes são as posições dos itens em comum, ponderado pelas posições de referência."
        )

        df = pd.DataFrame({
            "Métrica": ["Score (0–1)", "Levenshtein Similarity", "Levenshtein Distance",
                        "Levenshtein Normalized", "WMAPE", "WMAPE Similarity"],
            "Ale": [
                f"{ale_result['score']:.3f}",
                f"{ale_result['levenshtein_similarity']:.3f}",
                ale_result['levenshtein_distance'],
                f"{ale_result['levenshtein_normalized']:.3f}",
                f"{ale_result['wmape']:.3f}",
                f"{ale_result['wmape_similarity']:.3f}"
            ],
            "Leo": [
                f"{leo_result['score']:.3f}",
                f"{leo_result['levenshtein_similarity']:.3f}",
                leo_result['levenshtein_distance'],
                f"{leo_result['levenshtein_normalized']:.3f}",
                f"{leo_result['wmape']:.3f}",
                f"{leo_result['wmape_similarity']:.3f}"
            ]
        })
        st.dataframe(df, use_container_width=True)

    st.markdown("---")

    if st.button("🏠 Voltar ao Início", use_container_width=True, type="primary"):
        st.session_state['page'] = 'home'
        st.session_state['ranking_data'] = None
        st.rerun()


# ============================================================================
# APLICATIVO PRINCIPAL
# ============================================================================


def main():
    """Ponto de entrada principal do aplicativo."""
    st.set_page_config(
        page_title="Comparador de Rankings",
        page_icon="🎬",
        layout="centered"
    )
    init_session_state()
    page = st.session_state['page']
    if page == 'home':
        show_home()
    elif page == 'ranking':
        show_ranking()
    elif page == 'results':
        show_results()


if __name__ == "__main__":
    main()
