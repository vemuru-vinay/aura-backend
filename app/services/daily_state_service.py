from datetime import datetime, timezone, timedelta
from app.db.database import get_connection

# ─────────────────────────────────────────────
# SYSTEM DAY (IST)
# ─────────────────────────────────────────────
IST = timezone(timedelta(hours=5, minutes=30))


def get_system_day():
    """
    Returns current system day in IST (YYYY-MM-DD).
    """
    return datetime.now(IST).date().isoformat()


def get_previous_system_day():
    """
    Returns previous system day in IST.
    """
    return (datetime.now(IST).date() - timedelta(days=1)).isoformat()


def get_daily_state(cursor, system_day):
    cursor.execute(
        "SELECT resolved, resolution_type FROM daily_state WHERE date = ?;",
        (system_day,)
    )
    return cursor.fetchone()


def assert_day_not_resolved(cursor, system_day):
    state = get_daily_state(cursor, system_day)

    # 🟢 No row means day is NEW → allowed
    if state is None:
        return

    if state["resolved"] == 1:
        raise Exception(
            "DAY ALREADY RESOLVED\n"
            f"Resolution type: {state['resolution_type']}"
        )






def mark_day_resolved(cursor, system_day, resolution_type):
    cursor.execute(
        """
        INSERT OR REPLACE INTO daily_state (date, resolved, resolution_type)
        VALUES (?, 1, ?);
        """,
        (system_day, resolution_type)
    )

def ensure_today_row(cursor, system_day):
    cursor.execute(
        """
        INSERT OR IGNORE INTO daily_state
        (date, resolved, resolution_type, penalties_generated)
        VALUES (?, 0, 'PENDING', 0);
        """,
        (system_day,)
    )



# ─────────────────────────────────────────────
# AUTOMATIC MISSED DAY EVALUATION
# ─────────────────────────────────────────────
def evaluate_missed_day():
    """
    Daily rollover authority.

    Rules:
    - If yesterday is unresolved → mark as MISS + apply miss consequences
    - ALWAYS generate penalties for yesterday if a report exists
    - Safe to call multiple times (idempotent)
    """

    conn = get_connection()
    cursor = conn.cursor()

    yesterday = get_previous_system_day()

    state = get_daily_state(cursor, yesterday)

    # ─────────────────────────────────────────────
    # 1️⃣ HANDLE MISSED DAY (IF UNRESOLVED)
    # ─────────────────────────────────────────────
    if not state:
        # Yesterday does not exist at all → nothing to do
        conn.close()
        return

    if state["resolved"] == 0:
        # Yesterday was missed
        mark_day_resolved(cursor, yesterday, "MISS")

        # Miss consequences
        cursor.execute(
            "UPDATE player SET streak = 0 WHERE id = 1;"
        )

    # ─────────────────────────────────────────────
    # 2️⃣ GENERATE PENALTIES (ALWAYS, ONCE)
    # ─────────────────────────────────────────────
    from app.services.penalty_service import generate_penalties_for_new_day
    generate_penalties_for_new_day()

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# PUBLIC DAILY ROLLOVER ENTRY POINT
# ─────────────────────────────────────────────
def run_daily_rollover():
    """
    Authoritative daily rollover hook.
    Call on app startup or scheduler (cron).
    """
    evaluate_missed_day()
