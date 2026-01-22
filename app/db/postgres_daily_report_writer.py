"""
PostgreSQL Daily Report Writer
ADD-ONLY helper. Mirrors SQLite write behavior.
"""

from sqlalchemy.orm import Session
from app.db.postgres_database import SessionLocal
from app.db.postgres_models import (
    Player,
    Stats,
    DailyReport,
    Penalty,
    DailyState,
)
from datetime import datetime


def write_daily_report_postgres(payload: dict):
    """
    Executes daily report write operations using PostgreSQL.
    Payload is assumed AUTHORITATIVE and PRE-VALIDATED.
    """

    session: Session = SessionLocal()

    try:
        system_day = payload["system_day"]

        # ─── DAILY REPORT INSERT ───────────────────
        daily = DailyReport(
            date=system_day,
            STR=payload["STR"],
            INT=payload["INT"],
            VIT=payload["VIT"],
            AGI=payload["AGI"],
            PER=payload["PER"],
            CON=payload["CON"],
            CHA=payload["CHA"],
            NET=payload["NET"],
            lust_boss=payload["LUST_BOSS"],
            xp_gained=payload["xp_gained"],
            xp_lost=payload["xp_lost"],
        )
        session.add(daily)

        # ─── PLAYER XP UPDATE ─────────────────────
        player = session.query(Player).filter(Player.id == 1).one()
        player.current_xp += (
            payload["xp_gained"]
            - payload["xp_lost"]
            - payload["penalty_xp_lost"]
        )

        # ─── STATS UPDATE ─────────────────────────
        stats = session.query(Stats).filter(Stats.player_id == 1).one()

        for stat, delta in payload["stat_deltas"].items():
            new_value = max(getattr(stats, stat) + delta, 0)
            setattr(stats, stat, new_value)

        # ─── PENALTY CLOSURE ──────────────────────
        for quest_key in payload["closed_penalties"]:
            session.query(Penalty).filter(
                Penalty.quest_key == quest_key,
                Penalty.is_completed == 0
            ).update(
                {
                    Penalty.is_completed: 1,
                    Penalty.last_updated: system_day
                }
            )

        # ─── DAILY STATE ──────────────────────────
        state = session.query(DailyState).filter(
            DailyState.date == system_day
        ).one()

        state.resolved = 1
        state.resolution_type = "REPORT"

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
