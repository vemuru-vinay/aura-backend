"""
System Initializer
Creates the database and inserts the Player if not present.
This file should be run ONCE.
"""

from app.db.database import initialize_database, get_connection
from app.core.constants import PLAYER_NAME, INITIAL_STATS


def player_exists(cursor):
    cursor.execute("SELECT id FROM player LIMIT 1;")
    return cursor.fetchone() is not None


def create_player(cursor):
    cursor.execute(
        """
        INSERT INTO player (name, level, rank, current_xp, stabilization_days, status)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (PLAYER_NAME, 0, "E", 0, 0, "ACTIVE")
    )

    player_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO stats (player_id, STR, INT, VIT, AGI, PER, CON, CHA, NET)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            player_id,
            INITIAL_STATS["STR"],
            INITIAL_STATS["INT"],
            INITIAL_STATS["VIT"],
            INITIAL_STATS["AGI"],
            INITIAL_STATS["PER"],
            INITIAL_STATS["CON"],
            INITIAL_STATS["CHA"],
            INITIAL_STATS["NET"],
        )
    )


def main():
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()

    if player_exists(cursor):
        print("System already initialized. Player exists.")
    else:
        create_player(cursor)
        conn.commit()
        print("AURA System initialized. Player created.")

    conn.close()


if __name__ == "__main__":
    main()
