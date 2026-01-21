from datetime import date
from app.db.database import get_connection
from app.core.rewards_definitions import (
    TITLES,
    LEVEL_XP_REWARDS,
    RANK_XP_REWARDS,
)
from app.services.level_service import apply_level_progression

# Rank hierarchy for comparison
RANK_ORDER = {
    "D": 1,
    "C": 2,
    "B": 3,
    "A": 4,
    "S": 5,
    "S+": 6,
    "S++": 7,
    "S+++": 8,
    "SS": 9,
    "SS+": 10,
    "SSS": 11,
    "MONARCH": 12,
    "SHADOW_MONARCH": 13,
}


def _is_claimed(cursor, reward_type: str, reward_key: str) -> bool:
    cursor.execute(
        """
        SELECT 1 FROM claimed_rewards
        WHERE reward_type = ? AND reward_key = ?;
        """,
        (reward_type, reward_key),
    )
    return cursor.fetchone() is not None


def get_rewards_state():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT level, rank, sot, streak FROM player LIMIT 1;"
    )
    player = cursor.fetchone()

    rewards = {
        "titles": [],
        "level_xp": [],
        "rank_xp": [],
        "sot": {
            "count": player["sot"],
            "conditions": [],
        },
    }

    # ─── TITLES ─────────────────────────
    for t in TITLES:
        if _is_claimed(cursor, "TITLE", t["key"]):
            continue

        rewards["titles"].append({
            "key": t["key"],
            "title": t["title"],
            "level_required": t["level"],
            "state": "CLAIMABLE"
            if player["level"] >= t["level"]
            else "LOCKED",
        })

    # ─── LEVEL XP ───────────────────────
    for r in LEVEL_XP_REWARDS:
        if _is_claimed(cursor, "LEVEL_XP", r["key"]):
            continue

        rewards["level_xp"].append({
            "key": r["key"],
            "level": r["level"],
            "xp": r["xp"],
            "state": "CLAIMABLE"
            if player["level"] >= r["level"]
            else "LOCKED",
        })

    # ─── RANK XP ────────────────────────
    player_rank_value = RANK_ORDER.get(player["rank"], 0)

    for r in RANK_XP_REWARDS:
        if _is_claimed(cursor, "RANK_XP", r["key"]):
            continue

        reward_rank_value = RANK_ORDER.get(r["rank"], 0)

        rewards["rank_xp"].append({
            "key": r["key"],
            "rank": r["rank"],
            "xp": r["xp"],
            "state": "CLAIMABLE"
            if player_rank_value >= reward_rank_value
            else "LOCKED",
        })

    conn.close()
    return rewards


def claim_reward(reward_type: str, reward_key: str) -> str:
    """
    Claims a reward using a SINGLE atomic transaction.
    Enforces repeatable SOT logic.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT streak FROM player LIMIT 1;"
        )
        current_streak = cursor.fetchone()["streak"]

        # ─── DUPLICATE GUARD (NON-SOT) ────────────
        if reward_type != "SOT":
            if _is_claimed(cursor, reward_type, reward_key):
                raise Exception("Reward already claimed.")

        system_message = "Authorization granted."

        if reward_type in ("LEVEL_XP", "RANK_XP"):
            source = (
                LEVEL_XP_REWARDS
                if reward_type == "LEVEL_XP"
                else RANK_XP_REWARDS
            )

            reward = next(r for r in source if r["key"] == reward_key)

            cursor.execute(
                "UPDATE player SET current_xp = current_xp + ? WHERE id = 1;",
                (reward["xp"],),
            )

            apply_level_progression(cursor)

            system_message = f"XP registered: +{reward['xp']}"

        elif reward_type == "TITLE":
            reward = next(t for t in TITLES if t["key"] == reward_key)

            # ✅ ONLY ADDITION: activate title
            cursor.execute(
                "UPDATE player SET active_title = ? WHERE id = 1;",
                (reward["title"],),
            )

            system_message = "Title acquired."


        if reward_type == "SOT":
            cursor.execute(
                """
                INSERT INTO claimed_rewards (reward_type, reward_key, claimed_at)
                VALUES (?, ?, ?);
                """,
                (
                    reward_type,
                    f"{reward_key}@{current_streak}",
                    date.today().isoformat(),
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO claimed_rewards (reward_type, reward_key, claimed_at)
                VALUES (?, ?, ?);
                """,
                (reward_type, reward_key, date.today().isoformat()),
            )


        conn.commit()
        return system_message

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
