"""
Penalty Definitions — AURA System

This file defines ALL penalty rules.
No logic. No database. No side effects.

The System reads from here and enforces behavior.
"""

PENALTY_DEFINITIONS = {

    "STR": {
        "base": {
            "description": "100 squats + 100 Pushups ",
            "effects": [
                "Strength XP locked for 24 hours",
                "STR stat increase disabled"
            ]
        }
    },

    "INT": {
        "base": {
            "description": "5 hours focused study and Entertainment Banned for total day",
            "effects": [
                "No entertainment for 24 hours"
            ]
        }
    },

    "VIT": {
        "base": {
            "description": "Forced Wake-up 120 min earlier and no sleep at morning + hydation tracking",
            "effects": [
                "Vitality stat temporarily debuffed"
            ]
        }
    },

    "AGI": {
        "base": {
            "description": "60 min recorded english speaking(no script) + 5 additional chess games",
            "effects": [
                "AGI stat stagnates"
            ]
        }
    },

    "PER": {
        "base": {
            "description": "Meditation duration 60 min + Reading tripled",
            "effects": [
                "Focus debuff applied to all tasks"
            ]
        }
    },

    "CON": {
        "base": {
            "description": "Go outside and speak to any one stranger girl something for sometime(own ideas) or Dance in the public place",
            "effects": [
                "Avoidance flag recorded"
            ]
        }
    },

    "CHA": {
        "base": {
            "description": "2 times cold shower + 4-hour dopamine silence",
            "effects": [
                "CHA stat stagnates"
            ]
        }
    },

    "NET": {
        "base": {
            "description": "Social media consumption banned for entire day + Record yourself and upload it on youtube",
            "effects": [
                "Scrolling forbidden, creation allowed"
            ]
        }
    },

    "LUST_BOSS": {
        "base": {
            "description": "Physical penance(50 pushups, 50 situps, 50 squats) + 24-hour entertainment ban + Ask a stranger girl for DATE",
            "effects": [
                "-10 XP",
                "Lust debuff applied",
                "Accountability flag stored"
            ]
        }
    }
}
