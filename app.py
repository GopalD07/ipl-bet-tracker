"""
IPL 2026 Bet Tracker — Flask Backend
Storage: Supabase (Postgres via supabase-py)

Tables needed (run the SQL in SETUP.md first):
  - match_configs  (match_no, home_wallet, away_wallet, result)
  - bets           (id, match_no, side, placed, win, odd, created_at)
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from datetime import datetime, timezone

# ── APP SETUP ──────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── IPL SCHEDULE ───────────────────────────────────────────
IPL_SCHEDULE = [
    {"match":1,  "date":"2026-03-28","day":"Sat","time":"7:30 PM","home":"Royal Challengers Bengaluru","away":"Sunrisers Hyderabad",        "venue":"Bengaluru",       "home_abbr":"RCB", "away_abbr":"SRH", "home_color":"#EC1C24","away_color":"#F7A721"},
    {"match":2,  "date":"2026-03-29","day":"Sun","time":"7:30 PM","home":"Mumbai Indians",              "away":"Kolkata Knight Riders",      "venue":"Mumbai",          "home_abbr":"MI",  "away_abbr":"KKR", "home_color":"#005DA0","away_color":"#3A225D"},
    {"match":3,  "date":"2026-03-30","day":"Mon","time":"7:30 PM","home":"Rajasthan Royals",           "away":"Chennai Super Kings",         "venue":"Guwahati",        "home_abbr":"RR",  "away_abbr":"CSK", "home_color":"#EA1A85","away_color":"#F9CD05"},
    {"match":4,  "date":"2026-03-31","day":"Tue","time":"7:30 PM","home":"Punjab Kings",               "away":"Gujarat Titans",              "venue":"New Chandigarh",  "home_abbr":"PBKS","away_abbr":"GT",  "home_color":"#ED1B24","away_color":"#1C1C57"},
    {"match":5,  "date":"2026-04-01","day":"Wed","time":"7:30 PM","home":"Lucknow Super Giants",       "away":"Delhi Capitals",              "venue":"Lucknow",         "home_abbr":"LSG", "away_abbr":"DC",  "home_color":"#A72B2A","away_color":"#0078BC"},
    {"match":6,  "date":"2026-04-02","day":"Thu","time":"7:30 PM","home":"Kolkata Knight Riders",      "away":"Sunrisers Hyderabad",         "venue":"Kolkata",         "home_abbr":"KKR", "away_abbr":"SRH", "home_color":"#3A225D","away_color":"#F7A721"},
    {"match":7,  "date":"2026-04-03","day":"Fri","time":"7:30 PM","home":"Chennai Super Kings",        "away":"Punjab Kings",                "venue":"Chennai",         "home_abbr":"CSK", "away_abbr":"PBKS","home_color":"#F9CD05","away_color":"#ED1B24"},
    {"match":8,  "date":"2026-04-04","day":"Sat","time":"3:30 PM","home":"Delhi Capitals",             "away":"Mumbai Indians",              "venue":"Delhi",           "home_abbr":"DC",  "away_abbr":"MI",  "home_color":"#0078BC","away_color":"#005DA0"},
    {"match":9,  "date":"2026-04-04","day":"Sat","time":"7:30 PM","home":"Gujarat Titans",             "away":"Rajasthan Royals",            "venue":"Ahmedabad",       "home_abbr":"GT",  "away_abbr":"RR",  "home_color":"#1C1C57","away_color":"#EA1A85"},
    {"match":10, "date":"2026-04-05","day":"Sun","time":"3:30 PM","home":"Sunrisers Hyderabad",        "away":"Lucknow Super Giants",        "venue":"Hyderabad",       "home_abbr":"SRH", "away_abbr":"LSG", "home_color":"#F7A721","away_color":"#A72B2A"},
    {"match":11, "date":"2026-04-05","day":"Sun","time":"7:30 PM","home":"Royal Challengers Bengaluru","away":"Chennai Super Kings",         "venue":"Bengaluru",       "home_abbr":"RCB", "away_abbr":"CSK", "home_color":"#EC1C24","away_color":"#F9CD05"},
    {"match":12, "date":"2026-04-06","day":"Mon","time":"7:30 PM","home":"Kolkata Knight Riders",      "away":"Punjab Kings",                "venue":"Kolkata",         "home_abbr":"KKR", "away_abbr":"PBKS","home_color":"#3A225D","away_color":"#ED1B24"},
    {"match":13, "date":"2026-04-07","day":"Tue","time":"7:30 PM","home":"Rajasthan Royals",           "away":"Mumbai Indians",              "venue":"Guwahati",        "home_abbr":"RR",  "away_abbr":"MI",  "home_color":"#EA1A85","away_color":"#005DA0"},
    {"match":14, "date":"2026-04-08","day":"Wed","time":"7:30 PM","home":"Delhi Capitals",             "away":"Gujarat Titans",              "venue":"Delhi",           "home_abbr":"DC",  "away_abbr":"GT",  "home_color":"#0078BC","away_color":"#1C1C57"},
    {"match":15, "date":"2026-04-09","day":"Thu","time":"7:30 PM","home":"Kolkata Knight Riders",      "away":"Lucknow Super Giants",        "venue":"Kolkata",         "home_abbr":"KKR", "away_abbr":"LSG", "home_color":"#3A225D","away_color":"#A72B2A"},
    {"match":16, "date":"2026-04-10","day":"Fri","time":"7:30 PM","home":"Rajasthan Royals",           "away":"Royal Challengers Bengaluru", "venue":"Guwahati",        "home_abbr":"RR",  "away_abbr":"RCB", "home_color":"#EA1A85","away_color":"#EC1C24"},
    {"match":17, "date":"2026-04-11","day":"Sat","time":"3:30 PM","home":"Punjab Kings",               "away":"Sunrisers Hyderabad",         "venue":"New Chandigarh",  "home_abbr":"PBKS","away_abbr":"SRH", "home_color":"#ED1B24","away_color":"#F7A721"},
    {"match":18, "date":"2026-04-11","day":"Sat","time":"7:30 PM","home":"Chennai Super Kings",        "away":"Delhi Capitals",              "venue":"Chennai",         "home_abbr":"CSK", "away_abbr":"DC",  "home_color":"#F9CD05","away_color":"#0078BC"},
    {"match":19, "date":"2026-04-12","day":"Sun","time":"3:30 PM","home":"Lucknow Super Giants",       "away":"Gujarat Titans",              "venue":"Lucknow",         "home_abbr":"LSG", "away_abbr":"GT",  "home_color":"#A72B2A","away_color":"#1C1C57"},
    {"match":20, "date":"2026-04-12","day":"Sun","time":"7:30 PM","home":"Mumbai Indians",             "away":"Royal Challengers Bengaluru", "venue":"Mumbai",          "home_abbr":"MI",  "away_abbr":"RCB", "home_color":"#005DA0","away_color":"#EC1C24"},
]

# ── SUPABASE HELPERS ────────────────────────────────────────

def get_config(match_no: int) -> dict:
    res = supabase.table("match_configs").select("*").eq("match_no", match_no).execute()
    if res.data:
        return res.data[0]
    row = {"match_no": match_no, "home_wallet": 0, "away_wallet": 0, "result": "pending"}
    supabase.table("match_configs").insert(row).execute()
    return row

def upsert_config(match_no: int, **kwargs):
    existing = supabase.table("match_configs").select("match_no").eq("match_no", match_no).execute()
    if existing.data:
        supabase.table("match_configs").update(kwargs).eq("match_no", match_no).execute()
    else:
        supabase.table("match_configs").insert({"match_no": match_no, **kwargs}).execute()

def get_bets(match_no: int, side: str = None) -> list:
    q = supabase.table("bets").select("*").eq("match_no", match_no).order("id")
    if side:
        q = q.eq("side", side)
    return q.execute().data or []

# ── STATS COMPUTATION ──────────────────────────────────────

def compute_match_stats(config: dict, home_bets: list, away_bets: list) -> dict:
    def team_stats(bets):
        placed  = sum(float(b["placed"]) for b in bets)
        win     = sum(float(b["win"])    for b in bets)
        count   = len(bets)
        avg_odd = (win / placed) if placed > 0 else 0
        return {"count": count, "placed": round(placed,4), "win": round(win,4),
                "avg_odd": round(avg_odd,4), "profit": round(win - placed, 4)}

    home = team_stats(home_bets)
    away = team_stats(away_bets)
    total_placed = home["placed"] + away["placed"]
    hw = float(config.get("home_wallet") or 0)
    aw = float(config.get("away_wallet") or 0)
    result = config.get("result", "pending")

    if result == "home":
        net_pnl = round(home["win"] - total_placed, 4)
    elif result == "away":
        net_pnl = round(away["win"] - total_placed, 4)
    else:
        net_pnl = 0

    return {
        "home": home, "away": away,
        "total_placed":     round(total_placed, 4),
        "home_wallet":      hw,
        "away_wallet":      aw,
        "home_wallet_left": round(hw - home["placed"], 4),
        "away_wallet_left": round(aw - away["placed"], 4),
        "result":           result,
        "net_pnl":          net_pnl,
    }

def compute_global_analytics() -> dict:
    all_configs = supabase.table("match_configs").select("*").execute().data or []
    all_bets    = supabase.table("bets").select("*").execute().data or []

    bets_by_match = {}
    for b in all_bets:
        mn = b["match_no"]
        bets_by_match.setdefault(mn, {"home": [], "away": []})
        bets_by_match[mn][b["side"]].append(b)

    total_placed = all_net = 0
    wins = losses = pending = 0
    cumulative, running = [], 0
    team_pnl = {}

    for cfg in all_configs:
        mn    = cfg["match_no"]
        bmap  = bets_by_match.get(mn, {"home": [], "away": []})
        stats = compute_match_stats(cfg, bmap["home"], bmap["away"])
        total_placed += stats["total_placed"]
        result = stats["result"]

        if result == "pending":
            pending += 1
        else:
            running  += stats["net_pnl"]
            all_net  += stats["net_pnl"]
            wins += 1 if stats["net_pnl"] >= 0 else 0
            losses += 0 if stats["net_pnl"] >= 0 else 1
            cumulative.append({"label": f"M{mn}", "value": round(running, 4)})

        mi = next((m for m in IPL_SCHEDULE if m["match"] == mn), None)
        if mi:
            for side, team in [("home", mi["home"]), ("away", mi["away"])]:
                s = stats[side]
                team_pnl.setdefault(team, {"placed": 0, "win": 0, "bets": 0})
                team_pnl[team]["placed"] += s["placed"]
                team_pnl[team]["win"]    += s["win"]
                team_pnl[team]["bets"]   += s["count"]

    roi = (all_net / total_placed * 100) if total_placed > 0 else 0
    return {
        "total_placed":  round(total_placed, 2),
        "net_pnl":       round(all_net, 2),
        "roi":           round(roi, 2),
        "wins": wins, "losses": losses, "pending": pending,
        "win_rate":      round(wins / max(wins + losses, 1) * 100, 1),
        "cumulative_pnl": cumulative,
        "team_pnl":      team_pnl,
    }

# ── ROUTES ─────────────────────────────────────────────────

@app.route("/")
def health():
    return jsonify({"status": "ok", "service": "IPL Bet Tracker"})

@app.route("/schedule")
def get_schedule():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return jsonify([
        dict(m, is_today=m["date"] == today, is_past=m["date"] < today)
        for m in IPL_SCHEDULE
    ])

@app.route("/match/<int:match_no>")
def get_match(match_no):
    config     = get_config(match_no)
    home_bets  = get_bets(match_no, "home")
    away_bets  = get_bets(match_no, "away")
    stats      = compute_match_stats(config, home_bets, away_bets)
    mi         = next((m for m in IPL_SCHEDULE if m["match"] == match_no), None)
    doc = {
        "home_bets":   home_bets,
        "away_bets":   away_bets,
        "home_wallet": config.get("home_wallet", 0),
        "away_wallet": config.get("away_wallet", 0),
        "result":      config.get("result", "pending"),
    }
    return jsonify({"match_info": mi, "doc": doc, "stats": stats})

@app.route("/match/<int:match_no>/wallet", methods=["PUT"])
def set_wallet(match_no):
    b = request.json
    upsert_config(match_no,
        home_wallet=float(b.get("home_wallet", 0)),
        away_wallet=float(b.get("away_wallet", 0)),
        result="pending")
    config    = get_config(match_no)
    stats     = compute_match_stats(config, get_bets(match_no,"home"), get_bets(match_no,"away"))
    return jsonify({"stats": stats})

@app.route("/match/<int:match_no>/bet", methods=["POST"])
def add_bet(match_no):
    b      = request.json
    side   = b.get("side")
    placed = float(b.get("placed", 0))
    win    = float(b.get("win", 0))

    if side not in ("home", "away"):
        return jsonify({"error": "side must be home or away"}), 400
    if placed <= 0:
        return jsonify({"error": "placed must be > 0"}), 400
    if win < 0:
        return jsonify({"error": "win must be >= 0"}), 400

    get_config(match_no)  # ensure config exists

    new_bet = {
        "match_no":   match_no,
        "side":       side,
        "placed":     placed,
        "win":        win,
        "odd":        round(win / placed, 4) if placed > 0 else 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ins = supabase.table("bets").insert(new_bet).execute()
    saved_bet = ins.data[0] if ins.data else new_bet

    config = get_config(match_no)
    stats  = compute_match_stats(config, get_bets(match_no,"home"), get_bets(match_no,"away"))
    return jsonify({"bet": saved_bet, "stats": stats}), 201

@app.route("/match/<int:match_no>/bet/<side>/<int:bet_id>", methods=["DELETE"])
def delete_bet(match_no, side, bet_id):
    if side not in ("home", "away"):
        return jsonify({"error": "bad side"}), 400
    supabase.table("bets").delete().eq("id", bet_id).eq("match_no", match_no).execute()
    config = get_config(match_no)
    stats  = compute_match_stats(config, get_bets(match_no,"home"), get_bets(match_no,"away"))
    return jsonify({"stats": stats})

@app.route("/match/<int:match_no>/result", methods=["PUT"])
def settle_match(match_no):
    b      = request.json
    result = b.get("result")
    if result not in ("home", "away", "void", "pending"):
        return jsonify({"error": "result: home/away/void/pending"}), 400
    upsert_config(match_no, result=result)
    config    = get_config(match_no)
    stats     = compute_match_stats(config, get_bets(match_no,"home"), get_bets(match_no,"away"))
    analytics = compute_global_analytics()
    return jsonify({"stats": stats, "analytics": analytics})

@app.route("/analytics")
def get_analytics():
    analytics   = compute_global_analytics()
    all_configs = supabase.table("match_configs").select("*").execute().data or []
    all_bets    = supabase.table("bets").select("*").execute().data or []

    bets_by_match = {}
    for bet in all_bets:
        mn = bet["match_no"]
        bets_by_match.setdefault(mn, {"home": [], "away": []})
        bets_by_match[mn][bet["side"]].append(bet)

    all_matches = []
    for cfg in all_configs:
        mn    = cfg["match_no"]
        bmap  = bets_by_match.get(mn, {"home": [], "away": []})
        stats = compute_match_stats(cfg, bmap["home"], bmap["away"])
        mi    = next((m for m in IPL_SCHEDULE if m["match"] == mn), None)
        all_matches.append({
            "match_no":   str(mn),
            "match_info": mi,
            "stats":      stats,
            "doc": {
                "home_bets":   bmap["home"],
                "away_bets":   bmap["away"],
                "home_wallet": cfg.get("home_wallet", 0),
                "away_wallet": cfg.get("away_wallet", 0),
                "result":      cfg.get("result", "pending"),
            },
        })
    return jsonify({"analytics": analytics, "matches": all_matches})

@app.route("/reset", methods=["POST"])
def reset():
    supabase.table("bets").delete().neq("id", 0).execute()
    supabase.table("match_configs").delete().neq("match_no", 0).execute()
    return jsonify({"message": "All data reset"})

# ── RUN ────────────────────────────────────────────────────
if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5050))
    debug = os.environ.get("FLASK_ENV", "production") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
