"""
ONE-TIME SQLite → PostgreSQL migration.
DO NOT RUN MORE THAN ONCE.
"""

from app.db.database import get_connection as get_sqlite_connection
from app.db.postgres_database import SessionLocal
from app.db.postgres_models import Player, Stats


def migrate_once():
    # ─── READ FROM SQLITE ──────────────────────
    sqlite_conn = get_sqlite_connection()
    sqlite_cur = sqlite_conn.cursor()

    sqlite_cur.execute("SELECT * FROM player LIMIT 1;")
    sqlite_player = dict(sqlite_cur.fetchone())

    sqlite_cur.execute(
        "SELECT * FROM stats WHERE player_id = ?;",
        (sqlite_player["id"],)
    )
    sqlite_stats = dict(sqlite_cur.fetchone())

    sqlite_conn.close()

    # ─── WRITE TO POSTGRES ─────────────────────
    db = SessionLocal()

    # Wipe existing seed (safe, controlled)
    db.query(Stats).delete()
    db.query(Player).delete()
    db.commit()

    player = Player(
        id=sqlite_player["id"],
        name=sqlite_player["name"],
        level=sqlite_player["level"],
        rank=sqlite_player["rank"],
        current_xp=sqlite_player["current_xp"],
        streak=sqlite_player["streak"],
        iron_mode=sqlite_player["iron_mode"],
        sot=sqlite_player["sot"],
        stabilization_days=sqlite_player["stabilization_days"],
        active_title=sqlite_player["active_title"],
    )

    stats = Stats(
        player_id=sqlite_player["id"],
        STR=sqlite_stats["STR"],
        INT=sqlite_stats["INT"],
        VIT=sqlite_stats["VIT"],
        AGI=sqlite_stats["AGI"],
        PER=sqlite_stats["PER"],
        CON=sqlite_stats["CON"],
        CHA=sqlite_stats["CHA"],
        NET=sqlite_stats["NET"],
        LB=sqlite_stats["LB"],
    )

    db.add(player)
    db.add(stats)
    db.commit()
    db.close()

    print("✅ SQLite → PostgreSQL migration complete")


if __name__ == "__main__":
    migrate_once()
