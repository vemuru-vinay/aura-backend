"""
PostgreSQL ORM models for AURA System.
These models EXACTLY mirror the live SQLite database schema.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from app.db.postgres_database import Base


# -------------------------------------------------------------------
# PLAYER
# -------------------------------------------------------------------

class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    level = Column(Integer, nullable=False)
    rank = Column(Text, nullable=False)
    current_xp = Column(Integer, nullable=False)

    stabilization_days = Column(Integer, default=0)
    status = Column(Text, default="ACTIVE")
    streak = Column(Integer, default=0)

    reentry_mode = Column(Integer, default=0)
    iron_mode = Column(Integer, default=0)

    rank_eligible = Column(Text, nullable=True)
    rank_locked = Column(Integer, default=1)

    sot = Column(Integer, default=0)
    active_title = Column(Text, nullable=True)


# -------------------------------------------------------------------
# STATS
# -------------------------------------------------------------------

class Stats(Base):
    __tablename__ = "stats"

    player_id = Column(Integer, ForeignKey("player.id"), primary_key=True)

    STR = Column(Integer, nullable=False)
    INT = Column(Integer, nullable=False)
    VIT = Column(Integer, nullable=False)
    AGI = Column(Integer, nullable=False)
    PER = Column(Integer, nullable=False)
    CON = Column(Integer, nullable=False)
    CHA = Column(Integer, nullable=False)
    NET = Column(Integer, nullable=False)
    LB = Column(Integer, nullable=False, default=0)


# -------------------------------------------------------------------
# DAILY REPORTS
# -------------------------------------------------------------------

class DailyReport(Base):
    __tablename__ = "daily_reports"

    date = Column(Text, primary_key=True)

    STR = Column(Integer, nullable=False)
    INT = Column(Integer, nullable=False)
    VIT = Column(Integer, nullable=False)
    AGI = Column(Integer, nullable=False)
    PER = Column(Integer, nullable=False)
    CON = Column(Integer, nullable=False)
    CHA = Column(Integer, nullable=False)
    NET = Column(Integer, nullable=False)

    lust_boss = Column(Integer, nullable=False)
    xp_gained = Column(Integer, nullable=False)
    xp_lost = Column(Integer, nullable=False)


# -------------------------------------------------------------------
# DAILY SYSTEM STATE
# -------------------------------------------------------------------

class DailyState(Base):
    __tablename__ = "daily_state"

    date = Column(Text, primary_key=True)
    resolved = Column(Integer, nullable=False)
    resolution_type = Column(Text, nullable=False)
    penalties_generated = Column(Integer, default=0)


# -------------------------------------------------------------------
# PENALTIES
# -------------------------------------------------------------------

class Penalty(Base):
    __tablename__ = "penalties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quest_key = Column(Text, nullable=False)
    severity = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    applied_date = Column(Text, nullable=False)
    is_completed = Column(Integer, default=0)
    last_updated = Column(Text, nullable=False)


# -------------------------------------------------------------------
# CLAIMED REWARDS
# -------------------------------------------------------------------

class ClaimedReward(Base):
    __tablename__ = "claimed_rewards"
    __table_args__ = (
        UniqueConstraint("reward_type", "reward_key", name="idx_unique_claim"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    reward_type = Column(Text, nullable=False)
    reward_key = Column(Text, nullable=False)
    claimed_at = Column(Text, nullable=False)


# -------------------------------------------------------------------
# BEHAVIOR HISTORY
# -------------------------------------------------------------------

class BehaviorHistory(Base):
    __tablename__ = "behavior_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Text, nullable=False)
    clean_day = Column(Integer, nullable=False)
    lust_boss = Column(Integer, nullable=False)
    xp_gained = Column(Integer, nullable=False)
    xp_lost = Column(Integer, nullable=False)
    streak_after = Column(Integer, nullable=False)
    stabilization_triggered = Column(Integer, nullable=False)
    stabilization_days = Column(Integer, nullable=False)
    created_at = Column(Text, server_default=func.current_timestamp())


# -------------------------------------------------------------------
# BEHAVIOR LOGS
# -------------------------------------------------------------------

class BehaviorLog(Base):
    __tablename__ = "behavior_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Text, nullable=False)
    flag = Column(Text, nullable=False)
    details = Column(Text)
