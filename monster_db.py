MONSTERS = {

    "VIREX_HOLLOW": {
        "name": "Virex Hollow",
        "type": "Alien Parasite Mimic",
        "description": "Perfectly copies humans; reflection lags slightly.",

        "powers": [
            "cellular_scan",
            "memory_echo",
            "social_imitation"
        ],

        "kill_signature": "human_like_internal_collapse",

        "forensic_clues": {
            "last_breath_missing": True,
            "organs_liquefied": True,
            "external_wounds_normal": True,
            "spine_crushed": False,
            "reassembled_organs": False,
            "mirrored_wounds": False,
            "precision_cut": False
        },

        "behaviors": {
            "steals_identity": True,
            "steals_face": True
        },

        "weaknesses": {
            "bright_light": True
        }
    },

    "PALE_COURIER": {
        "name": "The Pale Courier",
        "type": "Interdimensional Stalker",
        "description": "Polite messenger; skin never sweats.",

        "powers": [
            "dimensional_slip",
            "silent_movement",
            "predictive_pathfinding"
        ],

        "kill_signature": "phase_strangle",

        "forensic_clues": {
            "last_breath_missing": False,
            "organs_liquefied": False,
            "external_wounds_normal": True,
            "spine_crushed": True,
            "reassembled_organs": False,
            "mirrored_wounds": False,
            "precision_cut": False,
            "no_airway_damage": True
        },

        "behaviors": {
            "steals_identity": False,
            "steals_face": False
        },

        "weaknesses": {
            "running_water": True
        }
    },

    "NYX_DOPPEL": {
        "name": "Nyx Doppel",
        "type": "Shadow Entity",
        "description": "Imitates a single target imperfectly; mirrored actions.",

        "kill_signature": "mirrored_human_method",

        "forensic_clues": {
            "last_breath_missing": False,
            "organs_liquefied": False,
            "external_wounds_normal": True,
            "spine_crushed": False,
            "reassembled_organs": False,
            "mirrored_wounds": True,
            "precision_cut": False
        },

        "behaviors": {
            "copies_single_target": True,
            "mirrors_actions": True
        },

        "weaknesses": {
            "mirrors": True
        }
    },

    "SKINWRIGHT": {
        "name": "Skinwright",
        "type": "Bio-Construct Predator",
        "description": "Wears human skin; rearranges bodies unnaturally.",

        "kill_signature": "reassembled_corpse",

        "forensic_clues": {
            "last_breath_missing": False,
            "organs_liquefied": False,
            "external_wounds_normal": False,
            "spine_crushed": False,
            "reassembled_organs": True,
            "mirrored_wounds": False,
            "precision_cut": False
        },

        "behaviors": {
            "wears_skin": True
        },

        "weaknesses": {
            "fire": True
        }
    },

    "EIDOLON_7": {
        "name": "Eidolon-7",
        "type": "Synthetic Alien Intelligence",
        "description": "Too efficient; kills with calculated minimal force.",

        "kill_signature": "minimal_force_execution",

        "forensic_clues": {
            "last_breath_missing": False,
            "organs_liquefied": False,
            "external_wounds_normal": True,
            "spine_crushed": False,
            "reassembled_organs": False,
            "mirrored_wounds": False,
            "precision_cut": True
        },

        "behaviors": {
            "efficiency_kill": True
        },

        "weaknesses": {
            "irrational_behavior": True
        }
    }
}
