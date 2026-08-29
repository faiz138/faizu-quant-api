import math
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Faizu Quant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def simulate_chase(runs_needed: int, balls_left: int, wickets: int, boundary_factor: float = 1.15):
    if balls_left <= 0 or wickets <= 0:
        return 0.0
    sims = 5000
    norm_weights = [0.32, 0.35, 0.10, 0.11 * boundary_factor, 0.07 * boundary_factor, 0.04]
    total_w = sum(norm_weights)
    weights = [w / total_w for w in norm_weights]
    outcomes = [0, 1, 2, 4, 6, 'W']

    wins = 0
    for _ in range(sims):
        r, w = 0, 0
        for _ in range(balls_left):
            if w >= wickets:
                break
            event = random.choices(outcomes, weights=weights)[0]
            if event == 'W':
                w += 1
            else:
                r += event
            if r >= runs_needed:
                break
        if r >= runs_needed:
            wins += 1
    return wins / sims

def calculate_kelly(win_prob: float, bookie_odds: float, bankroll: float = 10000.0):
    implied_prob = 1.0 / bookie_odds if bookie_odds > 0 else 1.0
    edge = win_prob - implied_prob
    stake = 0.0
    signal = "HOLD / PASS"

    if edge > 0.04 and bookie_odds > 1.0:
        b = bookie_odds - 1.0
        p = win_prob
        q = 1.0 - p
        kelly_fraction = (b * p - q) / b
        stake = max(0.0, round(bankroll * (kelly_fraction / 4), 2))
        signal = "VALUE BET FOUND 🔥"

    return {
        "edge_pct": round(edge * 100, 2),
        "fair_odds": round(1.0 / win_prob, 2) if win_prob > 0 else 0.0,
        "recommended_stake": stake,
        "signal": signal
    }

@app.get("/api/live-quant")
def get_live_quant(runs: int = 40, balls: int = 24, wickets: int = 5, odds: float = 2.10, bankroll: float = 10000.0):
    win_prob = simulate_chase(runs, balls, wickets)
    quant_eval = calculate_kelly(win_prob, odds, bankroll)

    return {
        "status": "success",
        "match_state": {
            "runs_needed": runs,
            "balls_left": balls,
            "wickets_in_hand": wickets,
            "market_odds": odds
        },
        "simulation": {
            "win_probability_pct": round(win_prob * 100, 1),
            "fair_odds": quant_eval["fair_odds"],
            "edge_pct": quant_eval["edge_pct"],
            "kelly_stake": quant_eval["recommended_stake"],
            "signal": quant_eval["signal"]
        }
    }
  
