"""
State Service
Read-only access to the current System state.
"""

from datetime import date, datetime, timezone, timedelta
from app.db.database import get_connection
from app.services.level_service import xp_required_for_next_level
from app.services.daily_state_service import get_system_day, ensure_today_row
from datetime import datetime, timezone, timedelta
from app.core.penalty_definitions import PENALTY_DEFINITIONS
from app.core.constants import DAILY_QUESTS


# ─────────────────────────────────────────────
# SYSTEM TIME (IST)
# ─────────────────────────────────────────────


IST = timezone(timedelta(hours=5, minutes=30))

def get_time_status():
    now = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(IST)


    end_of_day = now.replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=0
    )

    submission_allowed = now <= end_of_day

    remaining = end_of_day - now
    if remaining.total_seconds() < 0:
        remaining = timedelta(seconds=0)

    total_seconds = int(remaining.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return {
        "submission_allowed": submission_allowed,
        "time_remaining": f"{hours:02}:{minutes:02}:{seconds:02}"
    }

def _get_time_remaining_today():
    """
    Returns:
    - remaining_seconds (int)
    - formatted string HH:MM:SS
    - submission_allowed (bool)
    """
    now = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(IST)


    end_of_day = now.replace(
        hour=23, minute=59, second=59, microsecond=0
    )

    remaining = (end_of_day - now).total_seconds()

    remaining_seconds = max(int(remaining), 0)

    hours = remaining_seconds // 3600
    minutes = (remaining_seconds % 3600) // 60
    seconds = remaining_seconds % 60

    formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    submission_allowed = remaining_seconds > 0

    return remaining_seconds, formatted, submission_allowed


def get_player_state():
    """
    Returns full system state:
    - player
    - stats
    - penalties
    - XP progression data
    - daily resolution authority
    - authoritative time window data
    """
    system_day = get_system_day()
    print("🧪 DAILY_QUESTS LOADED:", DAILY_QUESTS)


        # ─── AUTHORITATIVE QUEST AVAILABILITY ───────
    weekday = date.fromisoformat(system_day).weekday()

    active_quests = {}

    for quest_key, quest_def in DAILY_QUESTS.items():
        # STR quest is disabled on Sunday (weekday == 6)
        if quest_key == "STR" and weekday == 6:
            continue

        active_quests[quest_key] = quest_def

            # LUST_BOSS is always active
    active_quests["LUST_BOSS"] = {
        "task": "Lust Resistance Check",
        "xp": None
    }


    conn = get_connection()
    cursor = conn.cursor()

    # ─── PLAYER ────────────────────────────────
    cursor.execute("SELECT * FROM player LIMIT 1;")
    from app.services.rank_service import derive_rank_from_level
    player = cursor.fetchone()

    derived_rank = derive_rank_from_level(player["level"])

    # ─── XP PROGRESSION ─────────────────────────
    xp_required = xp_required_for_next_level(player["level"])
    xp_to_next = (
        max(xp_required - player["current_xp"], 0)
        if xp_required is not None
        else None
    )

    # ─── STATS ──────────────────────────────────
    cursor.execute(
        "SELECT * FROM stats WHERE player_id = ?;",
        (player["id"],)
    )
    stats = cursor.fetchone()

    # ─── PENALTIES ──────────────────────────────
    cursor.execute(
        """
        SELECT quest_key, severity, description, is_completed
        FROM penalties
        WHERE is_completed = 0
        ORDER BY quest_key;
        """
    )
    rows = cursor.fetchall()
    
    penalties = {}
    for r in rows:
        quest_key = r["quest_key"]
        severity = r["severity"]
        
        penalty_entry = {
            "severity": severity,
            "description": r["description"],
            "is_completed": bool(r["is_completed"]),
            }
        penalties.setdefault(quest_key, []).append(penalty_entry)


    # ─── DAILY RESOLUTION STATE ─────────────────
    ensure_today_row(cursor, system_day)
    conn.commit()

    cursor.execute(
        """
        SELECT resolved, resolution_type
        FROM daily_state
        WHERE date = ?;
        """,
        (system_day,)
    )
    daily_row = cursor.fetchone()

    day_resolved = bool(daily_row["resolved"]) if daily_row else False
    resolution_type = daily_row["resolution_type"] if daily_row else None

    # ─── TIME AUTHORITY ─────────────────────────
    remaining_seconds, remaining_formatted, submission_allowed = (
        _get_time_remaining_today()
    )

    # ─── FINAL PLAYER OBJECT ────────────────────
    player = dict(player)
    player["rank"] = derived_rank
    player["day_resolved"] = day_resolved
    player["day_resolution_type"] = resolution_type
    player["time_remaining_seconds"] = remaining_seconds
    player["time_remaining"] = remaining_formatted
    player["submission_allowed"] = submission_allowed

    conn.close()

    time_status = get_time_status()

    return player, stats, penalties, {
        "xp_required_for_next_level": xp_required,
        "xp_to_next_level": xp_to_next,
        "submission_allowed": time_status["submission_allowed"],
        "time_remaining": time_status["time_remaining"],
         "active_quests": active_quests,
    }

# ─────────────────────────────────────────────
# POSTGRESQL (READ-ONLY SNAPSHOT — ADDED)
# ─────────────────────────────────────────────

from app.db.postgres_database import SessionLocal
from app.db.postgres_models import (
    Player as PG_Player,
    Stats as PG_Stats,
    Penalty as PG_Penalty,
    DailyState as PG_DailyState,
)

def read_postgres_state_snapshot():
    """
    READ-ONLY helper.
    Does NOT affect system behavior.
    Does NOT replace SQLite.
    Used only for verification and debugging.
    """

    system_day = get_system_day()
    db = SessionLocal()

    try:
        player = db.query(PG_Player).first()
        stats = (
            db.query(PG_Stats)
            .filter(PG_Stats.player_id == player.id)
            .first()
            if player else None
        )

        penalties = (
            db.query(PG_Penalty)
            .filter(PG_Penalty.is_completed == 0)
            .all()
        )

        daily_state = (
            db.query(PG_DailyState)
            .filter(PG_DailyState.date == system_day)
            .first()
        )

        return {
            "player": player,
            "stats": stats,
            "penalties": penalties,
            "daily_state": daily_state,
        }

    finally:
        db.close()
