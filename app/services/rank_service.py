"""
Rank Service
Automatically derives rank from level.
NO database connections are opened here.
"""

from app.core.constants import RANK_RULES


def derive_rank_from_level(level: int) -> str:
    for rank, rule in RANK_RULES.items():
        min_lvl, max_lvl = rule["levels"]
        if min_lvl <= level <= max_lvl:
            return rank
    return "UNRANKED"


def apply_rank_update(cursor):
    """
    Updates rank using the existing transaction cursor.
    MUST NOT open connections or commit.
    """

    cursor.execute("SELECT id, level, rank FROM player LIMIT 1;")
    player = cursor.fetchone()

    new_rank = derive_rank_from_level(player["level"])

    if new_rank != player["rank"]:
        cursor.execute(
            "UPDATE player SET rank = ? WHERE id = ?;",
            (new_rank, player["id"]),
        )

    return new_rank
