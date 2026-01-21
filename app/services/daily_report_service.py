"""
Daily Report Service
Handles submission and validation of daily quest reports.
"""

from datetime import datetime, timezone, timedelta
from app.db.database import get_connection
from app.core.constants import DAILY_QUESTS, LUST_BOSS
from app.services.daily_state_service import (
    get_system_day,
    assert_day_not_resolved,
    mark_day_resolved,
    ensure_today_row,   
)

# ─────────────────────────────────────────────
# SYSTEM DAY AUTHORITY (IST)
# ─────────────────────────────────────────────
IST = timezone(timedelta(hours=5, minutes=30))


def is_within_submission_window() -> bool:
    now = datetime.now(IST)

    print("⏱️ IST NOW:", now)
    start_of_day = now.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_of_day = now.replace(
        hour=23, minute=59, second=59, microsecond=0
    )

    return start_of_day <= now <= end_of_day



def report_exists(cursor, report_date):
    cursor.execute(
        "SELECT date FROM daily_reports WHERE date = ?;",
        (report_date,)
    )
    return cursor.fetchone() is not None


def calculate_xp(report):
    gained = 0
    lost = 0

    for quest, config in DAILY_QUESTS.items():
        if report.get(quest) == 1:
            gained += config["xp"]
        else:
            lost += config["xp"]

    if report.get("LUST_BOSS") == 1:
        gained += LUST_BOSS["xp_on_success_min"]
    else:
        lost += abs(LUST_BOSS["xp_on_failure"])

    return gained, lost


def submit_daily_report(report, penalty_results):

    from app.services.authority_service import check_system_authority
    authority = check_system_authority()

    if not authority["allowed"]:
        raise Exception("SYSTEM LOCKED")

    if not is_within_submission_window():
        raise Exception(
            "TIME WINDOW CLOSED\n"
            "Daily submission period has ended.\n"
            "System reset required."
        )
    
    system_day = get_system_day()

   
    # ─────────────────────────────────────────────
    # NORMALIZE & VALIDATE REPORT (AUTHORITATIVE)
    # Missing quests = NOT DONE (0)
    # ─────────────────────────────────────────────
    # ─────────────────────────────────────────────
    # NORMALIZE & VALIDATE REPORT (AUTHORITATIVE)
    # Accepts int or bool, coerces to int
    # Missing or invalid → NOT DONE (0)
    # ─────────────────────────────────────────────
    required_keys = list(DAILY_QUESTS.keys()) + ["LUST_BOSS"]

    for key in required_keys:
        value = report.get(key)

        if value is True:
            report[key] = 1
        elif value is False:
            report[key] = 0
        elif value in (0, 1):
            report[key] = value
        else:
            report[key] = 0




    


    conn = get_connection()
    cursor = conn.cursor()

    ensure_today_row(cursor, system_day)

    cursor.execute(
        "SELECT resolved FROM daily_state WHERE date = ?;",
        (system_day,)
    )
    row = cursor.fetchone()
    
    if row and row["resolved"] == 1:
        raise Exception("DAY ALREADY RESOLVED")
    
    conn.commit()




    print("🧾 SUBMIT DAILY REPORT — SYSTEM DAY:", system_day)

    try:
        # ─── AUTHORITATIVE DAY LOCK ────────────────

        if report_exists(cursor, system_day):
            raise Exception("Daily report already submitted.")

        cursor.execute(
            "SELECT iron_mode, level FROM player WHERE id = 1;"
        )
        row = cursor.fetchone()
        iron_mode = row["iron_mode"] == 1
        current_level = int(row["level"])

        all_completed = all(
            report.get(q) == 1 for q in DAILY_QUESTS.keys()
        ) and report.get("LUST_BOSS") == 1

        iron_penalty_applied = False
        iron_penalty_reason = None
        
        if iron_mode and not all_completed:
            xp_gained = 0
            xp_lost = 50  # FLAT IRON MODE PENALTY
            clean_day = False
            
            iron_penalty_applied = True
            iron_penalty_reason = "IRON MODE VIOLATION"

        else:
            xp_gained, xp_lost = calculate_xp(report)
            clean_day = all_completed

        cursor.execute(
            """
            INSERT INTO daily_reports (
                date, STR, INT, VIT, AGI, PER, CON, CHA, NET,
                lust_boss, xp_gained, xp_lost
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                system_day,
                report["STR"],
                report["INT"],
                report["VIT"],
                report["AGI"],
                report["PER"],
                report["CON"],
                report["CHA"],
                report["NET"],
                report["LUST_BOSS"],
                xp_gained,
                xp_lost,
            )
        )

        # ─────────────────────────────────────────────
        # CLOSE PENALTIES BASED ON PENALTY DECISION
        # ─────────────────────────────────────────────
        for quest_key, decision in penalty_results.items():
            if decision == 1:  # penalty DONE
                cursor.execute(
                    """
                    UPDATE penalties
                    SET is_completed = 1,
                    last_updated = ?
                    WHERE quest_key = ?
                    AND is_completed = 0;
                    """,
                (system_day, quest_key)
            )

        penalty_xp_lost = 0

        # ─────────────────────────────────────────────
        # CALCULATE PENALTY XP LOSS (AFTER CLOSING)
        # ─────────────────────────────────────────────
        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM penalties
            WHERE is_completed = 0;
            """
        )

        row = cursor.fetchone()
        penalty_xp_lost = row["count"] * 50




        cursor.execute(
             """
             UPDATE player
             SET current_xp = current_xp + ? - ? - ?
             WHERE id = 1;
             """,
            (xp_gained, xp_lost, penalty_xp_lost)
        )

                # ─────────────────────────────────────────────
        # STAT PROGRESSION (AUTHORITATIVE → STATS TABLE)
        # +1 if DONE, -1 if NOT DONE, floor at 0
        # ─────────────────────────────────────────────

        stat_column_map = {
            "STR": "STR",
            "INT": "INT",
            "VIT": "VIT",
            "AGI": "AGI",
            "PER": "PER",
            "CON": "CON",
            "CHA": "CHA",
            "NET": "NET",
            "LUST_BOSS": "LB",
            }
        for report_key, column in stat_column_map.items():
            delta = 1 if report.get(report_key) == 1 else -1

            cursor.execute(
                f"""
                UPDATE stats
                SET {column} = MAX({column} + ?, 0)
                WHERE player_id = 1;
                """,
                (delta,)
            )
        
        



        # ─── FINAL AUTHORITATIVE RESOLUTION ───────
        mark_day_resolved(cursor, system_day, "REPORT")

        

        from app.services.level_service import apply_level_progression
        leveled_up, new_level, new_rank = apply_level_progression(cursor)

        final_level = (
            int(new_level)
            if new_level is not None
            else current_level
        )

        from app.services.streak_service import update_streak
        streak_result = update_streak(cursor, report)
        streak_value = int(streak_result.get("new_streak", 0))      

        conn.commit()


        print("✅ COMMITTING DAILY REPORT FOR:", system_day)

        print("🧪 JUDGMENT PAYLOAD:", {
            "xp_gained": xp_gained,
            "xp_lost": xp_lost,
            "penalty_xp_lost": penalty_xp_lost,
        })


        # ─── POST-COMMIT LOGIC ────────────────────
        

        return {
            "status": "ACCEPTED",
            "judgment": {
                "xp_gained": int(xp_gained),
                "xp_lost": int(xp_lost),
                "penalty_xp_lost": int(penalty_xp_lost),
                "leveled_up": bool(leveled_up),
                "new_level": final_level,
                "clean_day": bool(clean_day),
                "streak": streak_value,
                "iron_mode_active": bool(iron_mode),
                "iron_penalty_applied": bool(iron_penalty_applied),
                "iron_penalty_reason": iron_penalty_reason,
            }
        }

    except Exception as e:
        conn.rollback()
        print("❌ DAILY REPORT ERROR:", e)
        raise


    finally:
        conn.close()
