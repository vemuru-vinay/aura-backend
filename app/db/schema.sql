-- =========================
-- AURA SYSTEM DATABASE SCHEMA
-- =========================

-- PLAYER CORE STATE
CREATE TABLE IF NOT EXISTS player (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    level INTEGER NOT NULL,
    rank TEXT NOT NULL,
    current_xp INTEGER NOT NULL,
    status TEXT DEFAULT 'ACTIVE',
    iron_mode INTEGER DEFAULT 0,
    sot INTEGER DEFAULT 0,
    active_title TEXT DEFAULT NULL,

    -- ─── DAILY AUTHORITY STATE ───────────────
    daily_date TEXT DEFAULT NULL,           -- YYYY-MM-DD (IST)
    daily_submitted INTEGER DEFAULT 0,       -- 0 = no, 1 = yes
    daily_sot_used INTEGER DEFAULT 0         -- 0 = no, 1 = yes
);

-- PLAYER STATS
CREATE TABLE IF NOT EXISTS stats (
    player_id INTEGER PRIMARY KEY,
    STR INTEGER NOT NULL,
    INT INTEGER NOT NULL,
    VIT INTEGER NOT NULL,
    AGI INTEGER NOT NULL,
    PER INTEGER NOT NULL,
    CON INTEGER NOT NULL,
    CHA INTEGER NOT NULL,
    NET INTEGER NOT NULL,
    LB INTEGER NOT NULL,
    FOREIGN KEY (player_id) REFERENCES player(id)
);

-- DAILY REPORTS
CREATE TABLE IF NOT EXISTS daily_reports (
    date TEXT PRIMARY KEY,
    STR INTEGER NOT NULL,
    INT INTEGER NOT NULL,
    VIT INTEGER NOT NULL,
    AGI INTEGER NOT NULL,
    PER INTEGER NOT NULL,
    CON INTEGER NOT NULL,
    CHA INTEGER NOT NULL,
    NET INTEGER NOT NULL,
    lust_boss INTEGER NOT NULL,
    xp_gained INTEGER NOT NULL,
    xp_lost INTEGER NOT NULL
);

-- PENALTIES
CREATE TABLE IF NOT EXISTS penalties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quest_key TEXT NOT NULL,
    severity INTEGER NOT NULL,
    description TEXT NOT NULL,
    applied_date TEXT NOT NULL,
    is_completed INTEGER DEFAULT 0,
    last_updated TEXT NOT NULL
);

-- CLAIMED REWARDS (GLOBAL LEDGER)
CREATE TABLE IF NOT EXISTS claimed_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reward_type TEXT NOT NULL,
    reward_key TEXT NOT NULL,
    claimed_at TEXT NOT NULL
);

-- Prevent duplicate claims
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_claim
ON claimed_rewards (reward_type, reward_key);

-- DAILY SYSTEM STATE (AUTHORITATIVE)
CREATE TABLE IF NOT EXISTS daily_state (
    date TEXT PRIMARY KEY,
    resolved INTEGER NOT NULL DEFAULT 0 CHECK (resolved IN (0, 1)),
    resolution_type TEXT NOT NULL CHECK (
        resolution_type IN ('REPORT', 'SOT', 'MISS')
    )
);

ALTER TABLE daily_state
ADD COLUMN penalties_generated INTEGER NOT NULL DEFAULT 0;
