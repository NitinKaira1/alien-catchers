import random
from config import NPC_CHAR, WALKABLE, NPC_BLOCKED
from maps import MAP_1
from monster import SUBTLE_TELLS

# Global NPC storage
NPCS = {}

# Normal, harmless NPC notes (the common case)
NORMAL_DESCS = [
    "Looks nervous",
    "Calm and quiet",
    "Very talkative",
    "Avoids eye contact",
]

# Chance an innocent NPC gets flagged with a "suspicious" note
# instead — the exact same lines the real monster uses. This is
# what makes verification a real judgment call instead of a
# guaranteed tell: sometimes it's just a nervous civilian.
RED_HERRING_CHANCE = 0.12


# --------------------------------------------------
# WALKABLE TILE SCAN
# --------------------------------------------------
def get_walkable_tiles(chunk):
    tiles = []
    height = len(chunk)
    width = len(chunk[0])

    for y, row in enumerate(chunk):
        for x, ch in enumerate(row):
            if ch in WALKABLE:
                if 1 <= y < height - 1 and 1 <= x < width - 1:
                    tiles.append((y, x))

    return tiles


# --------------------------------------------------
# NPC COUNT
# --------------------------------------------------
def get_total_npc_count():
    return random.randint(70, 80)


# --------------------------------------------------
# DISTRIBUTE NPCs
# --------------------------------------------------
def distribute_npcs_across_chunks():
    total_requested = random.randint(70, 80)
    chunk_keys = list(MAP_1.keys())
    random.shuffle(chunk_keys)

    NPCS.clear()
    placed_total = 0

    base = total_requested // len(chunk_keys)
    remainder = total_requested % len(chunk_keys)

    for chunk_key in chunk_keys:
        count = base + (1 if remainder > 0 else 0)
        remainder -= 1 if remainder > 0 else 0

        placed = spawn_npcs_in_chunk(chunk_key, count)
        placed_total += placed

    return placed_total



# --------------------------------------------------
# SPAWN NPCs IN A CHUNK
# --------------------------------------------------
def spawn_npcs_in_chunk(chunk_key, count):
    chunk = MAP_1[chunk_key]
    walkable = get_walkable_tiles(chunk)
    random.shuffle(walkable)

    npcs = []
    placed = 0

    for i in range(min(count, len(walkable))):
        y, x = walkable[i]

        # Usually a harmless note — occasionally a red herring that
        # reads exactly like the monster's tell. Purely cosmetic:
        # this NPC is 100% innocent either way.
        if random.random() < RED_HERRING_CHANCE:
            desc = random.choice(SUBTLE_TELLS)
        else:
            desc = random.choice(NORMAL_DESCS)

        npcs.append({
            'y': y,
            'x': x,
            'char': NPC_CHAR,
            'alive': True,
            'id': {
                "name": random.choice(["Arjun", "Ravi", "Neha", "Ishaan", "Karan"]),
                "age": random.randint(18, 60),
                "job": random.choice(["Worker", "Guard", "Clerk", "Doctor"]),
                "desc": desc
            },
            "has_face": True
        })
        placed += 1

    NPCS[chunk_key] = npcs
    return placed



# --------------------------------------------------
# NPC MOVEMENT
# --------------------------------------------------
def move_npc(npc, chunk_key, player, npcs):
    game_map = MAP_1[chunk_key]

    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    random.shuffle(directions)

    for dx, dy in directions:
        nx = npc["x"] + dx
        ny = npc["y"] + dy

        # Bounds check
        if ny < 0 or ny >= len(game_map):
            continue
        if nx < 0 or nx >= len(game_map[0]):
            continue

        # ❌ player ke upar mat jao
        if nx == player.x and ny == player.y:
            continue

        # ❌ dusre NPC ke upar mat jao
        occupied = False
        for other in npcs:
            if other is npc:
                continue
            if other["x"] == nx and other["y"] == ny:
                occupied = True
                break
        if occupied:
            continue

        tile = game_map[ny][nx]
        if tile not in NPC_BLOCKED:
            npc["x"] = nx
            npc["y"] = ny
            return


# --------------------------------------------------
# UPDATE NPCs (PER FRAME)
# --------------------------------------------------
def update_npcs(npcs, chunk_key, player):
    for npc in npcs:
        if not npc["alive"]:
            continue  # ❌ dead NPC does nothing

        if random.random() < 0.3:
            move_npc(npc, chunk_key, player, npcs)