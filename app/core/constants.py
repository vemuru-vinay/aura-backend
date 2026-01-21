"""
AURA SYSTEM — CORE CONSTANTS
These values define the immutable laws of the AURA System.
The Player cannot override these.
"""

# =========================
# PLAYER IDENTITY
# =========================

PLAYER_NAME = "Vinny"

SYSTEM_NAME = "MindX AURA"

# =========================
# CORE STATS (INITIAL VALUES)
# =========================

INITIAL_STATS = {
    "STR": 1,   # Strength
    "INT": 1,   # Intelligence
    "VIT": 1,   # Vitality
    "AGI": 1,   # Agility
    "PER": 1,   # Perception
    "CON": 1,   # Confidence
    "CHA": 1,   # Charisma
    "NET": 0    # Networking
}

# =========================
# DAILY QUEST DEFINITIONS
# =========================

DAILY_QUESTS = {
    "STR": {
        "task": "20 pushups(2 rep) + 25 squats + 20 situps + 20 dumbell raises ",
        "xp": 5
    },
    "INT": {
        "task": "25 min GATE study + explain aloud",
        "xp": 5
    },
    "VIT": {
        "task": "Proper meals + hydration",
        "xp": 5
    },
    "AGI": {
        "task": "Chess or English speaking",
        "xp": 5
    },
    "PER": {
        "task": "10 min meditation",
        "xp": 5
    },
    "CON": {
        "task": "Social exposure / go outside",
        "xp": 5
    },
    "CHA": {
        "task": "Grooming + mirror statement",
        "xp": 5
    },
    "NET": {
        "task": "Content upload or +10 followers",
        "xp": 5
    }
}

# =========================
# LUST BOSS SYSTEM (CRITICAL)
# =========================

LUST_BOSS = {
    "xp_on_success_min": 5,
    "xp_on_success_max": 10,
    "xp_on_failure": -10,
    "always_active": True
}

LUST_EMERGENCY_PROTOCOL = {
    "interrupt_actions": ["push-ups", "cold water", "change room"],
    "screen_lock_minutes": 30,
    "hidden_resistance_credit": True
}

# =========================
# XP & LEVEL PROGRESSION
# (EARLY GAME TABLE)
# =========================

LEVEL_XP_TABLE = {
    0: 30,
    1: 40,
    2: 50,
    3: 60,
    4: 70,
    5: 80,
    6: 90,
    7: 100,
    8: 120,
    9: 150
}

MAX_LEVEL = 100

# =========================
# RANK SYSTEM (NON-AUTOMATIC)
# =========================

# =========================
# RANK SYSTEM (AUTO-DERIVED)
# =========================

RANK_RULES = {
    "E": {
        "levels": (1, 9),
    },
    "D": {
        "levels": (10, 29),
    },
    "C": {
        "levels": (30, 49),
    },
    "B": {
        "levels": (50, 89),
    },
    "A": {
        "levels": (90, 120),
    },
    "S": {
        "levels": (130, 199),
    },
    "S+": {
        "levels": (200, 249),
    },
    "S++": {
        "levels": (250, 299),
    },
    "S+++": {
        "levels": (300, 399),
    },
    "SS": {
        "levels": (400, 499),
    },
    "SS+": {
        "levels": (500, 649),
    },
    "SS++": {
        "levels": (650, 799),
    },
    "SSS": {
        "levels": (800, 899),
    },
    "MONARCH": {
        "levels": (900, 999),
    },
    "SHADOW_MONARCH": {
        "levels": (1000, 1000),
    },
}



# =========================
# STABILIZATION MODE
# =========================

STABILIZATION_MODE = {
    "quests_suspended": True,
    "allowed_actions": [
        "walk",
        "drink water",
        "clean small area",
        "sit quietly"
    ],
    "forbidden_actions": [
        "anime",
        "doom scrolling",
        "fantasy",
        "future planning"
    ]
}

# =========================
# GATES & DUNGEONS
# =========================

GATES = {
    "E": "Goblin King",
    "D": "Lycan Alpha",
    "C": "Hollow Magician",
    "B": "Igris – Blood Red Knight",
    "A": "Baruka",
    "S": "Beru – Ant King"
}

# =========================
# SYSTEM PHILOSOPHY FLAGS
# =========================

SYSTEM_FLAGS = {
    "autonomous": True,
    "player_requests_are_suggestions": True,
    "rewards_can_be_delayed": True,
    "penalties_are_strategic": True
}
