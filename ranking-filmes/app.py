import streamlit as st
from typing import Dict, List, Tuple, Optional

# ============================================================================
# CONSTANTS - Film datasets
# ============================================================================

HP_TITLES = {
    "HP1": "HP1: Philosopher's Stone",
    "HP2": "HP2: Chamber of Secrets",
    "HP3": "HP3: Prisoner of Azkaban",
    "HP4": "HP4: Goblet of Fire",
    "HP5": "HP5: Order of the Phoenix",
    "HP6": "HP6: Half-Blood Prince",
    "HP7": "HP7: Deathly Hallows Part 1",
    "HP8": "HP8: Deathly Hallows Part 2"
}

SW_TITLES = {
    "SW1": "SW1: The Phantom Menace",
    "SW2": "SW2: Attack of the Clones",
    "SW3": "SW3: Revenge of the Sith",
    "SW4": "SW4: A New Hope",
    "SW5": "SW5: The Empire Strikes Back",
    "SW6": "SW6: Return of the Jedi",
    "SW7": "SW7: The Force Awakens",
    "SW8": "SW8: The Last Jedi",
    "SW9": "SW9: The Rise of Skywalker",
    "SWX": "Rogue One"
}

# Default profiles
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
# HELPER FUNCTIONS
# ============================================================================

def get_titles(saga: str) -> Dict[str, str]:
    """Get title dictionary for a saga."""
    return HP_TITLES if saga == "hp" else SW_TITLES

def get_defaults(saga: str) -> Dict[str, List[str]]:
    """Get default rankings for a saga."""
    return DEFAULT_RANKINGS[saga]

def to_codes(seq: List[str], saga: str) -> List[str]:
    """Convert titles to codes, filtering out unknowns."""
    titles = get_titles(saga)
    code_set = set(titles.keys())
    return [item for item in seq if item in code_set]

def ranks_map(seq: List[str]) -> Dict[str, int]:
    """Convert sequence to {code: 1-based-rank} mapping."""
    return {code: idx + 1 for idx, code in enumerate(seq)}

def levenshtein_seq(a: List[str], b: List[str]) -> int:
    """
    Compute Levenshtein distance between two sequences using dynamic programming.
    Insert/delete/substitute all cost 1.
    """
    m, n = len(a), len(b)
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # deletion
                    dp[i][j-1],    # insertion
                    dp[i-1][j-1]   # substitution
                )
    
    return dp[m][n]

def wmape_on_ranks(ref_seq: List[str], cmp_seq: List[str]) -> float:
    """
    Compute WMAPE on ranks over the intersection of items.
    Returns NaN if no common items.
    """
    r1 = ranks_map(ref_seq)
    r2 = ranks_map(cmp_seq)
    
    # Find intersection
    common = set(r1.keys()) & set(r2.keys())
    if not common:
        return float('nan')
    
    abs_err = sum(abs(r1[it] - r2[it]) for it in common)
    denominator = sum(r1[it] for it in common)
    
    if denominator == 0:
        return float('nan')
    
    return abs_err / denominator

def similarity_from_wmape(w: float) -> float:
    """Convert WMAPE to similarity score (1 - w), clamped to [0,1]."""
    if w != w:  # NaN check
        return float('nan')
    return max(0.0, min(1.0, 1.0 - w))

def compare_one(input_codes: List[str], ref_codes: List[str], saga: str) -> Dict:
    """
    Compare user ranking against a reference profile.
    Returns dict with score, levenshtein metrics, and wmape metrics.
    """
    titles = get_titles(saga)
    n_total = len(titles)
    
    # Levenshtein distance and similarity
    lev_dist = levenshtein_seq(input_codes, ref_codes)
    lev_norm = lev_dist / n_total if n_total > 0 else 0.0
    lev_sim = 1.0 - lev_norm
    
    # WMAPE and similarity
    wmape = wmape_on_ranks(ref_codes, input_codes)
    wmape_sim = similarity_from_wmape(wmape)
    
    # Final score (mean of similarities, handling NaN)
    if wmape_sim != wmape_sim:  # wmape_sim is NaN
        score = lev_sim
    elif lev_sim != lev_sim:  # lev_sim is NaN (shouldn't happen)
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

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'
    if 'saga' not in st.session_state:
        st.session_state['saga'] = None
    if 'user_ranking' not in st.session_state:
        st.session_state['user_ranking'] = None

# ============================================================================
# VIEW 1: HOME
# ============================================================================

def show_home():
    """Display the home page with saga selection."""
    st.title("🎬 Rank Matcher")
    st.markdown("### Compare your film rankings with Ale and Leo!")
    st.markdown("Choose a saga to rank and see how your taste matches up.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚡ Harry Potter")
        st.markdown("Rank all 8 films from the wizarding world")
        if st.button("Choose Harry Potter", use_container_width=True, type="primary"):
            st.session_state['saga'] = 'hp'
            st.session_state['page'] = 'ranking'
            st.rerun()
    
    with col2:
        st.markdown("### 🌟 Star Wars")
        st.markdown("Rank 10 films from a galaxy far, far away")
        if st.button("Choose Star Wars", use_container_width=True, type="primary"):
            st.session_state['saga'] = 'sw'
            st.session_state['page'] = 'ranking'
            st.rerun()

# ============================================================================
# VIEW 2: RANKING
# ============================================================================

def show_ranking():
    """Display the ranking interface with interactive table."""
    saga = st.session_state['saga']
    titles = get_titles(saga)
    codes = sorted(titles.keys())
    
    saga_name = "Harry Potter" if saga == "hp" else "Star Wars"
    st.title(f"📊 Rank {saga_name} Films")
    st.markdown(f"Assign a unique rank (1-{len(codes)}) to each film. 1 = your favorite!")
    
    # Prefill option
    prefill = st.checkbox("Prefill with alphabetical order (for testing)")
    
    # Initialize ranking data in session state
    if 'ranking_data' not in st.session_state or st.session_state.get('last_saga') != saga:
        if prefill:
            st.session_state['ranking_data'] = {code: idx + 1 for idx, code in enumerate(codes)}
        else:
            st.session_state['ranking_data'] = {code: None for code in codes}
        st.session_state['last_saga'] = saga
    
    st.markdown("---")
    
    # Create interactive table
    st.markdown("### Your Rankings")
    
    # Display table with number inputs
    for code in codes:
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            st.markdown(f"**{code}**")
        with col2:
            rank = st.number_input(
                "Rank",
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
    
    # Validation
    ranks = [st.session_state['ranking_data'][code] for code in codes]
    all_filled = all(r is not None for r in ranks)
    unique_ranks = len(ranks) == len(set(ranks)) if all_filled else True
    
    if not all_filled:
        st.warning("⚠️ Please fill in all ranks before submitting.")
    elif not unique_ranks:
        st.error("❌ Each rank must be unique! Please fix duplicate ranks.")
    
    # Sort by rank button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 Sort by Rank", use_container_width=True):
            # Sort codes by their ranks for preview
            sorted_codes = sorted(codes, key=lambda c: st.session_state['ranking_data'][c] or 999)
            st.markdown("#### Preview (sorted by rank):")
            for code in sorted_codes:
                rank = st.session_state['ranking_data'][code]
                st.markdown(f"{rank}. **{code}** - {titles[code]}")
    
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state['page'] = 'home'
            st.rerun()
    
    with col3:
        if st.button("✅ Submit Rankings", use_container_width=True, type="primary", disabled=not (all_filled and unique_ranks)):
            # Create final ranking list sorted by rank
            sorted_codes = sorted(codes, key=lambda c: st.session_state['ranking_data'][c])
            st.session_state['user_ranking'] = sorted_codes
            st.session_state['page'] = 'results'
            st.rerun()

# ============================================================================
# VIEW 3: RESULTS
# ============================================================================

def show_results():
    """Display comparison results with scores and winner."""
    saga = st.session_state['saga']
    user_ranking = st.session_state['user_ranking']
    defaults = get_defaults(saga)
    
    saga_name = "Harry Potter" if saga == "hp" else "Star Wars"
    
    # Compute scores
    ale_result = compare_one(user_ranking, defaults['Ale'], saga)
    leo_result = compare_one(user_ranking, defaults['Leo'], saga)
    
    # Determine winner
    ale_score = ale_result['score']
    leo_score = leo_result['score']
    
    if ale_score > leo_score:
        winner = "Ale"
    elif leo_score > ale_score:
        winner = "Leo"
    else:
        winner = "Tie"
    
    # Show celebration animation
    st.balloons()
    
    # Display results
    st.title(f"🏆 Results: {saga_name}")
    
    if winner == "Tie":
        st.markdown("## 🤝 It's a Tie!")
        st.markdown("Your rankings match Ale and Leo equally!")
    else:
        st.markdown(f"## 🎉 Winner: {winner}!")
        st.markdown(f"Your {saga_name} rankings are most similar to {winner}'s taste!")
    
    # Progress animation
    progress_bar = st.progress(0)
    for i in range(100):
        progress_bar.progress(i + 1)
    progress_bar.empty()
    
    st.markdown("---")
    
    # Metrics panel
    st.markdown("### 📈 Similarity Scores")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Ale")
        st.metric("Overall Score", f"{ale_score:.3f}")
        st.metric("Levenshtein Similarity", f"{ale_result['levenshtein_similarity']:.3f}")
        st.caption(f"Distance: {ale_result['levenshtein_distance']}, Normalized: {ale_result['levenshtein_normalized']:.3f}")
        st.metric("WMAPE Similarity", f"{ale_result['wmape_similarity']:.3f}")
        st.caption(f"WMAPE: {ale_result['wmape']:.3f}")
    
    with col2:
        st.markdown("#### Leo")
        st.metric("Overall Score", f"{leo_score:.3f}")
        st.metric("Levenshtein Similarity", f"{leo_result['levenshtein_similarity']:.3f}")
        st.caption(f"Distance: {leo_result['levenshtein_distance']}, Normalized: {leo_result['levenshtein_normalized']:.3f}")
        st.metric("WMAPE Similarity", f"{leo_result['wmape_similarity']:.3f}")
        st.caption(f"WMAPE: {leo_result['wmape']:.3f}")
    
    st.markdown("---")
    
    # Bar chart comparison
    st.markdown("### 📊 Score Comparison")
    st.bar_chart({"Ale": ale_score, "Leo": leo_score})
    
    st.markdown("---")
    
    # Raw numbers table
    st.markdown("### 📋 Detailed Metrics")
    import pandas as pd
    
    df = pd.DataFrame({
        "Metric": ["Overall Score", "Levenshtein Similarity", "Levenshtein Distance", "Levenshtein Normalized", "WMAPE", "WMAPE Similarity"],
        "Ale": [
            f"{ale_score:.3f}",
            f"{ale_result['levenshtein_similarity']:.3f}",
            ale_result['levenshtein_distance'],
            f"{ale_result['levenshtein_normalized']:.3f}",
            f"{ale_result['wmape']:.3f}",
            f"{ale_result['wmape_similarity']:.3f}"
        ],
        "Leo": [
            f"{leo_score:.3f}",
            f"{leo_result['levenshtein_similarity']:.3f}",
            leo_result['levenshtein_distance'],
            f"{leo_result['levenshtein_normalized']:.3f}",
            f"{leo_result['wmape']:.3f}",
            f"{leo_result['wmape_similarity']:.3f}"
        ]
    })
    
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    
    # Back to home button
    if st.button("🏠 Back to Home", use_container_width=True, type="primary"):
        st.session_state['page'] = 'home'
        st.session_state['ranking_data'] = None
        st.rerun()

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Rank Matcher",
        page_icon="🎬",
        layout="centered"
    )
    
    init_session_state()
    
    # Route to appropriate view
    page = st.session_state['page']
    
    if page == 'home':
        show_home()
    elif page == 'ranking':
        show_ranking()
    elif page == 'results':
        show_results()

if __name__ == "__main__":
    main()
