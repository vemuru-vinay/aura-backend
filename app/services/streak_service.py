"""
Streak Service
Tracks consecutive clean days for the AURA System.
"""

from app.db.database import get_connection


def update_streak(cursor, report):
    cursor.execute("SELECT streak FROM player LIMIT 1;")
    row = cursor.fetchone()

    current_streak = row["streak"]

    from app.core.constants import DAILY_QUESTS

    clean_day = all(
        report.get(q) == 1 for q in DAILY_QUESTS.keys()
    ) and report.get("LUST_BOSS") == 1

    if clean_day:
        new_streak = current_streak + 1
    else:
        new_streak = 0

    cursor.execute(
        """
        UPDATE player
        SET streak = ?
        WHERE id = 1;
        """,
        (new_streak,),
    )

    return {
        "clean_day": clean_day,
        "new_streak": new_streak,
    }

