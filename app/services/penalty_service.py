"""
Penalty Generation Service — SIMPLE & FINAL

Rules:
- Only ONE penalty per quest can exist at a time
- If quest was not done yesterday → penalty exists today
- Penalty repeats daily until BOTH quest and penalty are done
- If penalty was not done → −50 XP
"""

from datetime import datetime, timedelta
from app.db.database import get_connection
from app.core.penalty_definitions import PENALTY_DEFINITIONS
from app.services.daily_state_service import get_system_day


def generate_penalties_for_new_day():

    print("🚨 PENALTY GEN INVOKED AT:", datetime.now(), "SYSTEM DAY:", get_system_day())
    conn = get_connection()
    cursor = conn.cursor()

    # ─────────────────────────────────────────────
    # DAY AUTHORITY
    # ─────────────────────────────────────────────
    today = get_system_day()
    yesterday = (
        datetime.fromisoformat(today) - timedelta(days=1)
    ).date().isoformat()

    # ─────────────────────────────────────────────
    # RUN ONCE PER DAY (BASED ON YESTERDAY)
    # ─────────────────────────────────────────────
    cursor.execute(
        """
        SELECT penalties_generated
        FROM daily_state
        WHERE date = ?;
        """,
        (yesterday,),
    )
    row = cursor.fetchone()
    if row and row["penalties_generated"] == 1:
        conn.close()
        return

    # ─────────────────────────────────────────────
    # GET YESTERDAY REPORT
    # ─────────────────────────────────────────────
    cursor.execute(
        "SELECT * FROM daily_reports WHERE date = ?;",
        (yesterday,),
    )
    report = cursor.fetchone()
    if not report:
        conn.close()
        return

    # ─────────────────────────────────────────────
    # PROCESS EACH QUEST (ISOLATED)
    # ─────────────────────────────────────────────
    for quest_key, definition in PENALTY_DEFINITIONS.items():

        report_column = (
            "lust_boss" if quest_key == "LUST_BOSS" else quest_key
        )
        if report_column not in report.keys():
            continue

        quest_done = report[report_column] == 1


        cursor.execute(
            """
            SELECT id, is_completed
            FROM penalties
            WHERE quest_key = ?
            AND applied_date = ?;
            """,
            (quest_key, yesterday)
        )
        
        yesterday_penalty = cursor.fetchone()


        

        penalty_should_exist = False
        
        if not quest_done:
            # Quest not done → penalty must exist
            penalty_should_exist = True
        elif yesterday_penalty and yesterday_penalty["is_completed"] == 0:
            # Quest done but penalty NOT completed → penalty must continue
            penalty_should_exist = True
            
        # else:
        # Quest done AND penalty completed → no penalty
        # ─────────────────────────────────────────
        # GET ACTIVE PENALTY (IF ANY)
        # ────────────────────────────────────────

        

        # ─────────────────────────────────────────
        # CREATE TODAY'S PENALTY (AT MOST ONE)
        # ─────────────────────────────────────────
        if penalty_should_exist:
            cursor.execute(
                """
                SELECT id
                FROM penalties
                WHERE quest_key = ?
                AND is_completed = 0;
                """,
                (quest_key,)
            )
            
            active_penalty = cursor.fetchone()
            
            if active_penalty:
                 # 🔒 Reuse existing penalty, DO NOT create new one
                cursor.execute(
                    """
                    UPDATE penalties
                    SET last_updated = ?
                    WHERE id = ?;
                    """,
                    (today, active_penalty["id"])
                )
                continue
             # ✅ Create penalty ONLY if none exists
            cursor.execute(
                """
                INSERT INTO penalties (
                quest_key,
                severity,
                description,
                applied_date,
                is_completed,
                last_updated
            )
            VALUES (?, 1, ?, ?, 0, ?);
            """,
            (
                quest_key,
                definition["base"]["description"],
                today,
                today,
            ),
        )


    # ─────────────────────────────────────────────
    # MARK YESTERDAY AS PROCESSED
    # ─────────────────────────────────────────────
    cursor.execute(
        """
        UPDATE daily_state
        SET penalties_generated = 1
        WHERE date = ?;
        """,
        (yesterday,),
    )

    conn.commit()
    conn.close()
