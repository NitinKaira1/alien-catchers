import random
import logging
from config import DEAD_NPC_CHAR, NPC_BLOCKED, NPC_CHAR
from world_graph import WORLD_GRAPH
from maps import MAP_1

logger = logging.getLogger("alien_catchers")


# --------------------------------------------------
# SUBTLE "TELLS" — used instead of an obvious warning
# so the monster's fake ID reads almost like a normal
# NPC's, just slightly off if you're paying attention.
# --------------------------------------------------
SUBTLE_TELLS = [
    "Hasn't blinked once",
    "Shadow seems a beat behind",
    "Voice sounds slightly flat",
    "Skin looks unnaturally smooth",
    "Doesn't seem to breathe much",
    "Reflection looked a little off",
    "Stands a little too still",
    "Smiles a half-second too late",
]


class Monster:
    def __init__(self, npcs, game, monster_data):
        # Shared NPC storage
        self.npcs = npcs

        # Reference to Game
        self.game = game

        # Spawn monster somewhere in the world
        self.current_chunk = random.choice(list(WORLD_GRAPH.keys()))

        # Position (inside chunk)
        self.x = None
        self.y = None

        # Step timing
        self.step_counter = 0
        self.next_kill = random.randint(100, 125)

        # Debug / stats
        self.last_kill_chunk = None
        self.total_kills = 0

        # Initialize position
        self._spawn_inside_chunk()

        self.monster_data = monster_data

        # --------------------------------------------------
        # BLEND-IN: monster looks exactly like an NPC on the map
        # --------------------------------------------------
        self.char = NPC_CHAR

        # --------------------------------------------------
        # FAKE ID: looks just like a normal NPC's identity card,
        # except the "note" field is a subtle tell instead of
        # a normal NPC quirk. Nothing here screams "MONSTER".
        # --------------------------------------------------
        self.fake_id = {
            "name": random.choice(["Arjun", "Ravi", "Neha", "Ishaan", "Karan"]),
            "age": random.randint(18, 60),
            "job": random.choice(["Worker", "Guard", "Clerk", "Doctor"]),
            "desc": random.choice(SUBTLE_TELLS),
        }


        
    def generate_forensic_evidence(self):
        clues = self.monster_data["forensic_clues"]

        evidence = {}
        for clue, value in clues.items():
            if value:
                evidence[clue] = True

        evidence["kill_signature"] = self.monster_data["kill_signature"]
        evidence["time"] = "Recent"

        return evidence


    # --------------------------------------------------
    # INITIAL SPAWN / BLEND-IN
    # --------------------------------------------------
    def _spawn_inside_chunk(self):
        npcs_here = [
            n for n in self.npcs.get(self.current_chunk, [])
            if n["alive"]
        ]

        if npcs_here:
            npc = random.choice(npcs_here)
            self.x = npc["x"]
            self.y = npc["y"]
        else:
            self.x = None
            self.y = None

    # --------------------------------------------------
    # MOVE INSIDE CURRENT CHUNK (NO PLAYER OVERLAP)
    # --------------------------------------------------
    def move_inside_chunk(self):
        if self.current_chunk is None or self.x is None or self.y is None:
            return

        game_map = MAP_1[self.current_chunk]
        px, py = self.game.player.x, self.game.player.y
        player_chunk = (self.game.map_x, self.game.map_y)

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx = self.x + dx
            ny = self.y + dy

            # Bounds
            if ny < 0 or ny >= len(game_map):
                continue
            if nx < 0 or nx >= len(game_map[0]):
                continue

            # ❌ Do not step on player
            if (
                self.current_chunk == player_chunk
                and nx == px
                and ny == py
            ):
                continue

            tile = game_map[ny][nx]
            if tile not in NPC_BLOCKED:
                self.x = nx
                self.y = ny
                return

    # --------------------------------------------------
    # MOVE BETWEEN CHUNKS (WORLD GRAPH ONLY)
    # --------------------------------------------------
    def move_chunk(self):
        neighbors = WORLD_GRAPH.get(self.current_chunk, [])
        if not neighbors:
            return

        self.current_chunk = random.choice(neighbors)
        self._spawn_inside_chunk()

    # --------------------------------------------------
    # CALLED ON EVERY SUCCESSFUL PLAYER MOVE
    # --------------------------------------------------
    def player_step(self, player_chunk):
        # 👣 Move locally often
        if random.random() < 0.6:
            self.move_inside_chunk()

        # ⏱ Kill timer
        self.step_counter += 1

        if self.step_counter >= self.next_kill:
            self.step_counter = 0
            self.next_kill = random.randint(100, 125)

            # Move chunk sometimes before kill
            if random.random() < 0.7:
                self.move_chunk()

            self.kill_random_npc(player_chunk)

    # --------------------------------------------------
    # KILL LOGIC (NO KILL IN PLAYER CHUNK)
    # --------------------------------------------------
    def kill_random_npc(self, player_chunk):
        # ❌ Never kill in player chunk
        if self.current_chunk == player_chunk:
            return

        npcs_here = self.npcs.get(self.current_chunk, [])
        alive_npcs = [n for n in npcs_here if n["alive"]]

        if not alive_npcs:
            return

        victim = random.choice(alive_npcs)

        # Kill victim
        victim["alive"] = False
        victim["char"] = DEAD_NPC_CHAR

        # 🔍 Forensic data (temporary)
        victim["evidence"] = self.generate_forensic_evidence()


        # Update game state
        self.game.alive_npcs -= 1
        self.total_kills += 1
        self.last_kill_chunk = self.current_chunk

        logger.debug(
            "[MONSTER] Kill #%s in chunk %s at (%s,%s)",
            self.total_kills, self.current_chunk, victim['x'], victim['y']
        )