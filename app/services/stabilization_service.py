"""
Stabilization Service
Applies strict, single-day stabilization on severe failure only.
"""

from app.db.database import get_connection


def evaluate_stabilization(cursor, clean_day, lust_failed):
    # Severe failure definition
    stabilization_triggered = (not clean_day) and lust_failed

    if stabilization_triggered:
        stabilization_days = 1

        cursor.execute(
            "UPDATE player SET stabilization_days = ? WHERE id = 1;",
            (stabilization_days,)
        )
    else:
        cursor.execute(
            "SELECT stabilization_days FROM player LIMIT 1;"
        )
        stabilization_days = cursor.fetchone()["stabilization_days"]

    return {
        "stabilization_triggered": stabilization_triggered,
        "stabilization_days": stabilization_days
    }

