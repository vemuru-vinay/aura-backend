"""
AURA System API
FastAPI entry point.
"""

from fastapi import FastAPI

from app.services.state_service import get_player_state
from app.services.authority_service import check_system_authority
from app.api.schemas import DailyReportSchema
from app.services.daily_report_service import submit_daily_report
from app.api.iron_mode import router as iron_mode_router
from app.api.rewards import router as rewards_router
from datetime import date
from datetime import datetime, timezone, timedelta
from app.services.daily_state_service import get_system_day
from app.services.state_service import read_postgres_state_snapshot


# DAILY STATE (MISS HANDLING)
from app.services.daily_state_service import evaluate_missed_day


app = FastAPI(
    title="AURA System API",
    description="Solo Leveling–inspired autonomous life operating system",
    version="0.1.0"
)

# ─────────────────────────────────────────────
# SYSTEM DAY ENFORCEMENT (SAFE STARTUP HOOK)
# ─────────────────────────────────────────────
@app.on_event("startup")
def system_startup():
    """
    Runs once when the API starts.
    Resolves missed days safely without blocking startup.
    """
    print("⏱️ Running daily rollover check...")
    evaluate_missed_day()
    print("✅ Daily rollover complete")


# ─── ROUTERS ─────────────────────────────────
app.include_router(iron_mode_router)
app.include_router(rewards_router)

print("🚀 main.py loaded")


@app.get("/status")
def system_status():
    print("➡️ /status hit")

    player, stats, penalties, xp_data = get_player_state()


    player["day_resolved"] = False
    player["day_resolution_type"] = None




        # ─── AUTHORITATIVE TIME (BACKEND) ─────────────
    system_day = get_system_day()  # YYYY-MM-DD
    weekday = date.fromisoformat(system_day).weekday()  # Monday = 0

    print("✅ get_player_state done")

    authority = check_system_authority()
    print("✅ check_system_authority done")

    return {
        "player": {
            "name": player["name"],
            "level": player["level"],
            "rank": player["rank"],
            "current_xp": player["current_xp"],
            "xp_required_for_next_level": xp_data["xp_required_for_next_level"],
            "xp_to_next_level": xp_data["xp_to_next_level"],
            "streak": player["streak"],
            "stabilization_days": player["stabilization_days"],
            "iron_mode": player["iron_mode"],
            "sot": player["sot"],
            "active_title": player["active_title"],
            "day_resolved": player["day_resolved"],
            "day_resolution_type": player["day_resolution_type"],
        },
        "stats": stats,
        "authority": authority,
        "penalties": penalties,

        # 🆕 TIME SYSTEM
        "submission_allowed": xp_data["submission_allowed"],
        "time_remaining": xp_data["time_remaining"],
        "system_day": system_day,
        "weekday": weekday,
         "active_quests": xp_data["active_quests"],

    }


from fastapi import Body

@app.post("/daily-report")
def submit_daily_report_api(report: DailyReportSchema):
    authority = check_system_authority()

    if not authority["allowed"]:
        return {
            "status": "REFUSED",
            "reason": authority["message"],
        }

    try:
        report_dict = report.dict()

        penalty_results = report_dict.pop("penalties", {}) or {}

        return submit_daily_report(report_dict, penalty_results)

    except Exception as e:
        return {
            "status": "REFUSED",
            "reason": str(e),
            "judgment": {
                "xp_gained": 0,
                "xp_lost": 0,
                "penalty_xp_lost": 0,
                "leveled_up": False,
                "new_level": 0,
                "clean_day": False,
                "streak": 0,
            }
        }
    
@app.get("/debug/compare-state")
def debug_compare_state():
    """
    Read-only comparison between SQLite and PostgreSQL.
    No mutations. Inspection only.
    """

    # SQLite (authoritative today)
    sqlite_player, sqlite_stats, _, _ = get_player_state()

    # PostgreSQL snapshot
    snapshot = read_postgres_state_snapshot()
    pg_player = snapshot["player"].__dict__
    pg_stats = snapshot["stats"].__dict__ if snapshot["stats"] else {}

    return {
        "sqlite": {
            "player": {
                "name": sqlite_player["name"],
                "level": sqlite_player["level"],
                "current_xp": sqlite_player["current_xp"],
                "rank": sqlite_player["rank"],
                "streak": sqlite_player.get("streak"),
                "iron_mode": sqlite_player.get("iron_mode"),
                "sot": sqlite_player.get("sot"),
                "stabilization_days": sqlite_player.get("stabilization_days"),
                "active_title": sqlite_player.get("active_title"),
            },
            "stats": sqlite_stats,
        },
        "postgresql": {
            "player": {
                "name": pg_player.get("name"),
                "level": pg_player.get("level"),
                "current_xp": pg_player.get("current_xp"),
                "rank": pg_player.get("rank"),
                "streak": pg_player.get("streak"),
                "iron_mode": pg_player.get("iron_mode"),
                "sot": pg_player.get("sot"),
                "stabilization_days": pg_player.get("stabilization_days"),
                "active_title": pg_player.get("active_title"),
            },
            "stats": pg_stats,
        },
    }

