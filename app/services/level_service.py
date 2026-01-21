"""
Level Service
Handles XP-based level progression for the AURA System.
NO database connections are opened here.
"""

from app.services.rank_service import derive_rank_from_level
from app.services.rank_service import apply_rank_update


def xp_required_for_next_level(level: int) -> int | None:
    """
    Returns XP required to advance from the given level to the next.
    Encodes the full AURA progression law.
    """

    if level <= 9:
        return 100
    elif level <= 19:
        return 200
    elif level <= 29:
        return 250
    elif level <= 49:
        return 300
    elif level <= 69:
        return 350
    elif level <= 99:
        return 400
    elif level <= 129:
        return 500
    elif level <= 149:
        return 1000
    elif level <= 169:
        return 2000
    elif level <= 198:
        return 2000
    elif level == 199:
        return 5000
    # ─── HIGH LEVEL PROGRESSION ──────────────────
    elif 200 <= level <= 499:
        return 10000
    elif 500 <= level <= 999:
        return 50000
    elif level == 999:
        return 100000
    else:
        return None
    


def apply_level_progression(cursor):
    """
    Applies XP-based level progression using an existing transaction cursor.
    MUST NOT open connections or commit.
    """

    cursor.execute(
        "SELECT id, level, current_xp FROM player LIMIT 1;"
    )
    player = cursor.fetchone()

    player_id = player["id"]
    level = player["level"]
    xp = player["current_xp"]

    leveled_up = False

    while True:
        xp_needed = xp_required_for_next_level(level)

        if xp_needed is None:
            break

        if xp >= xp_needed:
            xp -= xp_needed
            level += 1
            leveled_up = True
        else:
            break

    new_rank = derive_rank_from_level(level)

    cursor.execute(
        """
        UPDATE player
        SET level = ?, current_xp = ?, rank = ?
        WHERE id = ?;
        """,
        (level, xp, new_rank, player_id),
    )

    # 🔒 Rank consistency enforced inside same transaction
    apply_rank_update(cursor)

    return leveled_up, level, new_rank
