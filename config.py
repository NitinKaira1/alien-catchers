MAP_WIDTH = 60
MAP_HEIGHT = 20

PLAYER_CHAR = "@"
NPC_CHAR = "O"
WALKABLE = {'.', '-', '='}
WALL = "#"

DEAD_NPC_CHAR = 'X'
MONSTER_CHAR = 'M'   

NPC_BLOCKED = {'#', '<', '>', '↑', '↓', '_','|'}


EXIT_RIGHT = ">"
EXIT_LEFT = "<"
EXIT_UP = "↑"
EXIT_DOWN = "↓"



# DIFFICULTY PRESETS

DIFFICULTY_PRESETS = {
    "Easy": {
        "ammo": 8,
        "max_monster_touches": 4,
        "monster_touch_chance": 0.25,
        "red_zone_time_limit": 55,
        "suspicion_wary_threshold": 12,
        "suspicion_hostile_threshold": 22,
    },
    "Normal": {
        "ammo": 6,
        "max_monster_touches": 3,
        "monster_touch_chance": 0.40,
        "red_zone_time_limit": 40,
        "suspicion_wary_threshold": 8,
        "suspicion_hostile_threshold": 16,
    },
    "Hard": {
        "ammo": 4,
        "max_monster_touches": 2,
        "monster_touch_chance": 0.55,
        "red_zone_time_limit": 28,
        "suspicion_wary_threshold": 5,
        "suspicion_hostile_threshold": 10,
    },
}

DEFAULT_DIFFICULTY = "Normal"