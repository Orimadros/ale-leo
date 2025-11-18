import argparse
import json
import sys
import re
from typing import List, Dict, Tuple
import Levenshtein

# =========================
# Canonical film sets (codes and title map)
# =========================
HP_TITLES = {
    "HP1": "HP1: Philosopher's Stone",
    "HP2": "HP2: Chamber of Secrets",
    "HP3": "HP3: Prisoner of Azkaban",
    "HP4": "HP4: Goblet of Fire",
    "HP5": "HP5: Order of the Phoenix",
    "HP6": "HP6: Half-Blood Prince",
    "HP7": "HP7: Deathly Hallows Part 1",
    "HP8": "HP8: Deathly Hallows Part 2",
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
    "SWX": "Rogue One",
}

HP_ALL = list(HP_TITLES.keys())
SW_ALL = list(SW_TITLES.keys())

# =========================
# Default profiles (can be overridden via --profiles)
# =========================

# ALE
DEFAULT_HP_ALE = [
    "HP2",
    "HP4",
    "HP1",
    "HP3",
    "HP5",
    "HP7",
    "HP8",
    "HP6",
]

DEFAULT_SW_ALE = [
    "SW5",
    "SW6",
    "SW7",
    "SW4",
    "SW1",
    "SW8",
    "SWX",
    "SW3",
    "SW9",
    "SW2",
]

# LEO
DEFAULT_HP_LEO = [
    "HP6",
    "HP4",
    "HP5",
    "HP3",
    "HP1",
    "HP7",
    "HP8",
    "HP2",
]


DEFAULT_SW_LEO = [
    "SW5",
    "SW6",
    "SW3",
    "SWX",
    "SW4",
    "SW1",
    "SW2",
    "SW7",
    "SW8",
    "SW9",
]


def load_profiles(path: str):
    data = {}
    if path:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    hp_ale = data.get("hp_Ale", DEFAULT_HP_ALE)
    hp_leo = data.get("hp_Leo", DEFAULT_HP_LEO)
    sw_ale = data.get("sw_Ale", DEFAULT_SW_ALE)
    sw_leo = data.get("sw_Leo", DEFAULT_SW_LEO)
    return hp_ale, hp_leo, sw_ale, sw_leo

# =========================
# Utils
# =========================


def to_codes(seq: List[str], saga: str) -> List[str]:
    """Accepts codes or titles and converts to codes; ignores unknowns."""
    if saga == "hp":
        code_map = {v.lower(): k for k, v in HP_TITLES.items()}
        valid = set(HP_TITLES.keys())
    else:
        code_map = {v.lower(): k for k, v in SW_TITLES.items()}
        valid = set(SW_TITLES.keys())
    out = []
    for s in seq:
        s = s.strip()
        if s in valid:
            out.append(s)
        else:
            # try by title (case-insensitive)
            k = code_map.get(s.lower())
            if k:
                out.append(k)
            else:
                # also accept bare codes like 'HP2' within titles 'HP2:' etc.
                m = re.match(r'^(HP\d+|SW\d+|SWX)', s, flags=re.I)
                if m and m.group(1).upper() in valid:
                    out.append(m.group(1).upper())
                else:
                    # ignore unknown
                    pass
    return out


def ranks_map(seq: List[str]) -> Dict[str, int]:
    return {item: i+1 for i, item in enumerate(seq)}


def wmape_on_ranks(ref_seq: List[str], cmp_seq: List[str]) -> float:
    """WMAPE aplicado em ranks; considera apenas interseção."""
    r1 = ranks_map(ref_seq)
    r2 = ranks_map(cmp_seq)
    common = [it for it in r1 if it in r2]
    if not common:
        return float("nan")
    abs_err = sum(abs(r1[it]-r2[it]) for it in common)
    denom = sum(r1[it] for it in common)
    return abs_err / denom if denom != 0 else float("nan")


def levenshtein_distance_items(a: List[str], b: List[str]) -> int:
    s1 = "\n".join(a)
    s2 = "\n".join(b)
    return Levenshtein.distance(s1, s2)


def levenshtein_norm_by_saga(dist: int, saga: str) -> float:
    N = len(HP_ALL) if saga == "hp" else len(SW_ALL)
    val = dist / N if N > 0 else float("nan")
    # clamp 0..1 (pode exceder se houver muitos extras fora da saga)
    return max(0.0, min(1.0, val))


def similarity_from_wmape(w: float) -> float:
    if w != w:  # NaN
        return float("nan")
    return max(0.0, min(1.0, 1.0 - w))


def compare_one(input_codes: List[str], ref_codes: List[str], saga: str) -> dict:
    d = levenshtein_distance_items(ref_codes, input_codes)
    d_norm = levenshtein_norm_by_saga(d, saga)
    s_lev = 1.0 - d_norm
    w = wmape_on_ranks(ref_codes, input_codes)
    s_w = similarity_from_wmape(w)
    score = (s_lev + s_w) / 2.0 if (s_lev == s_lev and s_w ==
                                    s_w) else s_lev if s_w != s_w else s_w
    return {
        "levenshtein": d,
        "levenshtein_norm": d_norm,
        "levenshtein_similarity": s_lev,
        "wmape": w,
        "wmape_similarity": s_w,
        "score": score,
    }


def main():
    ap = argparse.ArgumentParser(
        description="Compara um ranking (HP ou SW) com Ale e Leo usando Levenshtein norm e WMAPE.")
    ap.add_argument("--saga", required=True,
                    choices=["hp", "sw"], help="Saga do ranking de entrada (hp ou sw).")
    ap.add_argument("--ranking", required=True,
                    help="Ranking como string separada por vírgulas (códigos ou títulos). Ex.: 'HP2,HP4,HP1,...'")
    ap.add_argument("--profiles", default=None,
                    help="Arquivo JSON com hp_Ale, hp_Leo, sw_Ale, sw_Leo (opcional).")
    args = ap.parse_args()

    hp_ale, hp_leo, sw_ale, sw_leo = load_profiles(
        args.profiles if args.profiles else None)

    # valida perfis
    if args.saga == "hp":
        if hp_ale is None or hp_leo is None:
            print("Erro: perfis hp_Ale e hp_Leo necessários. Passe --profiles com JSON contendo 'hp_Ale' e 'hp_Leo'.", file=sys.stderr)
            sys.exit(2)
    else:
        if sw_ale is None or sw_leo is None:
            print("Erro: perfis sw_Ale e sw_Leo necessários. Passe --profiles com JSON contendo 'sw_Ale' e 'sw_Leo'.", file=sys.stderr)
            sys.exit(2)

    raw = [s.strip() for s in args.ranking.split(",") if s.strip()]
    input_codes = to_codes(raw, args.saga)
    if not input_codes:
        print("Nenhum item reconhecido no ranking de entrada.", file=sys.stderr)
        sys.exit(3)

    if args.saga == "hp":
        ale_codes = to_codes(hp_ale, "hp")
        leo_codes = to_codes(hp_leo, "hp")
    else:
        ale_codes = to_codes(sw_ale, "sw")
        leo_codes = to_codes(sw_leo, "sw")

    res_ale = compare_one(input_codes, ale_codes, args.saga)
    res_leo = compare_one(input_codes, leo_codes, args.saga)

    winner = "Ale" if res_ale["score"] > res_leo["score"] else "Leo" if res_leo["score"] > res_ale["score"] else "Empate"

    def fmt_res(name, r):
        return (f"{name}: score={r['score']:.3f} | "
                f"LevSim={r['levenshtein_similarity']:.3f} (dist={r['levenshtein']}, norm={r['levenshtein_norm']:.3f}) | "
                f"WMAPE_sim={r['wmape_similarity']:.3f} (wmape={r['wmape']:.3f})")

    print("Entrada:", raw)
    print("Entrada (codes):", input_codes)
    print(fmt_res("Ale", res_ale))
    print(fmt_res("Leo", res_leo))
    print("Vencedor:", winner)


def load_profiles(path: str):
    data = {}
    if path:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    hp_ale = data.get("hp_Ale", DEFAULT_HP_ALE)
    hp_leo = data.get("hp_Leo", DEFAULT_HP_LEO)
    sw_ale = data.get("sw_Ale", DEFAULT_SW_ALE)
    sw_leo = data.get("sw_Leo", DEFAULT_SW_LEO)
    return hp_ale, hp_leo, sw_ale, sw_leo


if __name__ == "__main__":
    # Defaults defined above need to be visible here
    DEFAULT_HP_ALE = DEFAULT_HP_ALE if 'DEFAULT_HP_ALE' in globals() else None
    DEFAULT_SW_ALE = DEFAULT_SW_ALE if 'DEFAULT_SW_ALE' in globals() else None
    DEFAULT_HP_LEO = DEFAULT_HP_LEO if 'DEFAULT_HP_LEO' in globals() else None
    DEFAULT_SW_LEO = DEFAULT_SW_LEO if 'DEFAULT_SW_LEO' in globals() else None
    HP_ALL = HP_ALL if 'HP_ALL' in globals() else []
    SW_ALL = SW_ALL if 'SW_ALL' in globals() else []
    HP_TITLES = HP_TITLES if 'HP_TITLES' in globals() else {}
    SW_TITLES = SW_TITLES if 'SW_TITLES' in globals() else {}
    main()
