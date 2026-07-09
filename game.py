import curses
import logging
from config import *
from maps import MAP_1
from player import Player
from renderer import draw
from NPC import update_npcs
from monster import Monster
from computer import Computer
import random
from monster_db import MONSTERS
from game_state import GameState

logging.basicConfig(
    filename="game.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("alien_catchers")


class Game:
    def __init__(self, stdscr, npcs, total_npcs):
        import random
        from monster_db import MONSTERS

        self.stdscr = stdscr
        self.npcs = npcs

        # ---------------- MAP / PLAYER ----------------
        self.map_x = 0
        self.map_y = 0
        self.player = Player()

        # ---------------- NPC COUNTS ----------------
        self.total_npcs = total_npcs
        self.alive_npcs = total_npcs

        # ---------------- 🎭 REAL MONSTER (PEHLE) ----------------
        self.real_monster_key = random.choice(list(MONSTERS.keys()))
        self.real_monster = MONSTERS[self.real_monster_key]

        logger.debug("REAL MONSTER: %s", self.real_monster_key)

        # ---------------- 👹 MONSTER (AB BANAO) ----------------
        self.monster = Monster(self.npcs, self, self.real_monster)

        # ---------------- GAME STATE ----------------
        self.state = GameState.INVESTIGATION
        self.end_reason = None

        # ---------------- COMPUTER ----------------
        self.computer = Computer()
        self.selected_monster = None

        # ---------------- COMBAT ----------------
        self.ammo = 6
        self.in_encounter = False
        self.encounter_choice = 0
        self.encounter_options = ["Shoot", "Leave"]
        self.encounter_target = None

        # ---------------- DEV ----------------
        self.dev_mode = False

        # ---------------- DANGER TRACKING ----------------
        self.monster_touches = 0
        self.max_monster_touches = 3

        # ---------------- RED ZONE ESCAPE TIMER ----------------
        # Starts counting down the moment you enter the monster's
        # chunk. Run out of time before you leave and it catches
        # you — you can't just camp there checking every NPC.
        self.red_zone_timer = None
        self.red_zone_time_limit = 40

        # ---------------- SUSPICION TRACKING ----------------
        # Every ID check nudges this up — you can't tell civilian
        # from monster before checking, so it applies either way.
        # Interrogate too many people and the city turns on you.
        self.suspicion = 0
        self.suspicion_wary_threshold = 8
        self.suspicion_hostile_threshold = 16
        self.suspicion_warned_wary = False
        self.suspicion_warned_hostile = False


    
    def get_adjacent_npc_any(self):
        chunk = (self.map_x, self.map_y)
        px, py = self.player.x, self.player.y

        for npc in self.npcs.get(chunk, []):
            dx = abs(npc['x'] - px)
            dy = abs(npc['y'] - py)
            if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
                return npc
        return None


    def is_adjacent_to_any_npc(self):
        chunk = (self.map_x, self.map_y)
        px, py = self.player.x, self.player.y

        for npc in self.npcs.get(chunk, []):
            dx = abs(npc['x'] - px)
            dy = abs(npc['y'] - py)
            if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
                return True
        return False



    def draw_encounter_menu(self):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        title = "ENCOUNTER"

        if self.encounter_target == "monster":
            subtitle = "Suspect presence detected"
        else:
            subtitle = "Civilian under suspicion"

        # Title
        self.stdscr.addstr(
            2,
            (w - len(title)) // 2,
            title,
            curses.A_BOLD
        )

        # Subtitle
        self.stdscr.addstr(
            4,
            (w - len(subtitle)) // 2,
            subtitle
        )

        # Ammo info
        ammo_text = f"Ammo remaining: {self.ammo}"
        self.stdscr.addstr(
            6,
            (w - len(ammo_text)) // 2,
            ammo_text
        )

        # Options
        for i, option in enumerate(self.encounter_options):
            prefix = "> " if i == self.encounter_choice else "  "
            text = prefix + option

            y = h // 2 + i
            x = (w - len(text)) // 2
            self.stdscr.addstr(y, x, text)

        # Hint
        hint = "↑ ↓ to choose | Enter to confirm"
        self.stdscr.addstr(
            h - 2,
            (w - len(hint)) // 2,
            hint
        )

        self.stdscr.refresh()





    def is_adjacent_to_monster(self):
        if self.monster.current_chunk != (self.map_x, self.map_y):
            return False

        if self.monster.x is None or self.monster.y is None:
            return False

        dx = abs(self.player.x - self.monster.x)
        dy = abs(self.player.y - self.monster.y)

        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)


    def check_monster_touch(self):
        """
        ☠️ LOSE CONDITION: in RED_ZONE, if the monster ends up right
        next to you, there's a chance it brushes past / grazes you.
        Three of those and it finally finishes the job.
        """
        if self.state != GameState.RED_ZONE:
            return
        if not self.is_adjacent_to_monster():
            return

        if random.random() < 0.4:
            self.monster_touches += 1

            if self.monster_touches >= self.max_monster_touches:
                self.state = GameState.END
                self.end_reason = "MONSTER_CAUGHT_YOU"
            else:
                self.show_message(
                    "Something brushed past you in the dark...\n\n"
                    f"Close calls: {self.monster_touches}/{self.max_monster_touches}"
                )

    def update_state(self):
        # Investigation never auto-changes
        if self.state == GameState.INVESTIGATION:
            return

        player_chunk = (self.map_x, self.map_y)
        monster_chunk = self.monster.current_chunk

        if monster_chunk == player_chunk:
            if self.state != GameState.RED_ZONE:
                # Just entered — start the clock fresh.
                self.red_zone_timer = self.red_zone_time_limit
            self.state = GameState.RED_ZONE
        else:
            if self.state == GameState.RED_ZONE:
                # Escaped in time — clock resets for next time.
                self.red_zone_timer = None
            self.state = GameState.HUNT

    def check_red_zone_timer(self):
        """
        ☠️ LOSE CONDITION: if you don't get out of the monster's
        chunk before the timer runs out, it catches up with you.
        """
        if self.state != GameState.RED_ZONE:
            return
        if self.red_zone_timer is None:
            return

        self.red_zone_timer -= 1

        if self.red_zone_timer <= 0:
            self.state = GameState.END
            self.end_reason = "RED_ZONE_TIMEOUT"



    # --------------------------------------------------
    # NPC COLLISION (alive NPCs only)
    # --------------------------------------------------
    def is_npc_at(self, x, y):
        chunk = (self.map_x, self.map_y)
        for npc in self.npcs.get(chunk, []):
            if npc['alive'] and npc['x'] == x and npc['y'] == y:
                return True
        return False

    # --------------------------------------------------
    # PLAYER MOVEMENT
    # --------------------------------------------------
    def handle_movement(self, dx, dy):
        current_map = MAP_1[(self.map_x, self.map_y)]

        nx = self.player.x + dx
        ny = self.player.y + dy

        # ---------------- MAP BOUNDS ----------------
        if ny < 0 or ny >= MAP_HEIGHT or nx < 0 or nx >= MAP_WIDTH:
            return

        tile = current_map[ny][nx]

        # ---------------- WALL ----------------
        if tile == WALL:
            return

        # ---------------- CHUNK TRANSITIONS ----------------
        if tile == EXIT_RIGHT:
            next_chunk = (self.map_x + 1, self.map_y)
            if next_chunk in MAP_1:
                self.map_x += 1
                self.player.x = 1
                self.monster.player_step((self.map_x, self.map_y))
            return

        elif tile == EXIT_LEFT:
            next_chunk = (self.map_x - 1, self.map_y)
            if next_chunk in MAP_1:
                self.map_x -= 1
                self.player.x = MAP_WIDTH - 2
                self.monster.player_step((self.map_x, self.map_y))
            return

        elif tile == EXIT_UP:
            next_chunk = (self.map_x, self.map_y - 1)
            if next_chunk in MAP_1:
                self.map_y -= 1
                self.player.y = MAP_HEIGHT - 2
                self.monster.player_step((self.map_x, self.map_y))
            return

        elif tile == EXIT_DOWN:
            next_chunk = (self.map_x, self.map_y + 1)
            if next_chunk in MAP_1:
                self.map_y += 1
                self.player.y = 1
                self.monster.player_step((self.map_x, self.map_y))
            return

        # ---------------- NPC COLLISION ----------------
        if self.is_npc_at(nx, ny):
            return

        # ---------------- MONSTER COLLISION (FIX) ----------------
        if (
            self.monster.current_chunk == (self.map_x, self.map_y)
            and nx == self.monster.x
            and ny == self.monster.y
        ):
            return

        # ---------------- NORMAL MOVE ----------------
        self.player.x = nx
        self.player.y = ny

        # ---------------- MONSTER STEP ----------------
        self.monster.player_step((self.map_x, self.map_y))


    # --------------------------------------------------
    # NPC INTERACTION
    # --------------------------------------------------
    def get_adjacent_npc(self):
        chunk = (self.map_x, self.map_y)
        px, py = self.player.x, self.player.y

        for npc in self.npcs.get(chunk, []):
            if not npc['alive']:
                continue

            dx = abs(npc['x'] - px)
            dy = abs(npc['y'] - py)

            if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
                return npc

        return None

    def interact(self):
        npc = self.get_adjacent_npc()
        if not npc:
            return

        if self.suspicion >= self.suspicion_hostile_threshold:
            message = "NPC: Stay away from me. People talk, you know."
        elif self.suspicion >= self.suspicion_wary_threshold:
            message = "NPC: ...Why do you keep asking everyone questions?"
        else:
            message = "NPC: Hello... stay safe."

        h, w = self.stdscr.getmaxyx()
        y = h // 2
        x = (w - len(message)) // 2

        self.stdscr.addstr(y, x, message)
        self.stdscr.addstr(y + 2, x, "Press any key to continue")
        self.stdscr.refresh()
        self.stdscr.getch()

    def get_adjacent_dead_npc(self):
        chunk = (self.map_x, self.map_y)
        px, py = self.player.x, self.player.y

        for npc in self.npcs.get(chunk, []):
            if npc['alive']:
                continue

            dx = abs(npc['x'] - px)
            dy = abs(npc['y'] - py)

            if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
                return npc

        return None

    def inspect_body(self):
        npc = self.get_adjacent_dead_npc()
        if not npc or 'evidence' not in npc:
            return

        evidence = npc['evidence']

        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        lines = []
        lines.append("BODY INSPECTION REPORT")
        lines.append("")
        
        # Kill signature (most important)
        lines.append(
            f"Kill Signature : {evidence.get('kill_signature', 'Unknown')}"
        )
        lines.append("")

        # Forensic clues
        lines.append("Observed Forensic Clues:")

        found_any = False
        for clue, value in evidence.items():
            if clue in ("kill_signature", "time"):
                continue
            if value:
                found_any = True
                pretty = clue.replace("_", " ").title()
                lines.append(f"- {pretty}")

        if not found_any:
            lines.append("- No clear forensic markers")

        lines.append("")
        lines.append("Time of Death : Recent")
        lines.append("")
        lines.append("Press any key to close")

        y = h // 2 - len(lines) // 2
        for line in lines:
            if y < h - 1:
                self.stdscr.addstr(y, (w - len(line)) // 2, line)
            y += 1

        self.stdscr.refresh()
        self.stdscr.getch()


    def get_adjacent_alive_npc(self):
        chunk = (self.map_x, self.map_y)
        px, py = self.player.x, self.player.y

        for npc in self.npcs.get(chunk, []):
            if not npc['alive']:
                continue

            dx = abs(npc['x'] - px)
            dy = abs(npc['y'] - py)

            if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
                return npc

        return None

    def build_identity_lines(self, name, age, job, desc, is_real_monster):
        """
        Shared by check_id() and verify_monster() so the card layout
        is IDENTICAL either way — same fields, same optional cross-ref
        line. This is what keeps things blended: seeing a cross-ref
        line (even a "no match") never tells you which one you're
        looking at. Only a genuine match does — and only if your
        theory was actually correct.
        """
        lines = [
            "IDENTITY CARD",
            "",
            f"Name : {name}",
            f"Age  : {age}",
            f"Job  : {job}",
            "",
            f"Note : {desc}",
        ]

        if self.selected_monster:
            if is_real_monster and self.selected_monster == self.real_monster_key:
                sig = self.real_monster.get("kill_signature", "unknown").replace("_", " ")
                lines += [
                    "",
                    f"Cross-ref  : Signature matches \"{sig}\"",
                    "This matches your working theory.",
                ]
            else:
                lines += [
                    "",
                    "Cross-ref  : No match to your working theory.",
                ]

        lines += [
            "",
            "Press any key to close"
        ]
        return lines

    def register_id_check(self):
        """
        Called whenever the player checks someone's ID — civilian or
        monster, doesn't matter, since the player can't tell which
        before checking. Interrogating too many people makes the
        city grow wary of you, and eventually gives the real threat
        more room to operate amid the chaos.
        """
        self.suspicion += 1

        if (
            self.suspicion >= self.suspicion_wary_threshold
            and not self.suspicion_warned_wary
        ):
            self.suspicion_warned_wary = True
            self.show_message(
                "People have started noticing how many IDs you've checked.\n\n"
                "They're growing wary of you."
            )

        if (
            self.suspicion >= self.suspicion_hostile_threshold
            and not self.suspicion_warned_hostile
        ):
            self.suspicion_warned_hostile = True
            self.monster.next_kill = max(40, self.monster.next_kill - 30)
            self.show_message(
                "The streets are tense. Whispers follow you now.\n\n"
                "In the confusion, something else is moving faster."
            )

    def check_id(self):
        npc = self.get_adjacent_alive_npc()
        if not npc:
            return

        self.register_id_check()

        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        id = npc["id"]
        lines = self.build_identity_lines(
            id['name'], id['age'], id['job'], id['desc'],
            is_real_monster=False
        )

        y = h // 2 - len(lines) // 2
        for line in lines:
            self.stdscr.addstr(y, (w - len(line)) // 2, line)
            y += 1

        self.stdscr.refresh()
        self.stdscr.getch()


    def verify_monster(self):
        self.register_id_check()

        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        # Same card layout as check_id() — see build_identity_lines().
        fid = self.monster.fake_id
        lines = self.build_identity_lines(
            fid['name'], fid['age'], fid['job'], fid['desc'],
            is_real_monster=True
        )

        y = h // 2 - len(lines) // 2
        for line in lines:
            self.stdscr.addstr(y, (w - len(line)) // 2, line)
            y += 1

        self.stdscr.refresh()
        self.stdscr.getch()



    def check_lose_condition(self):
        killed = self.total_npcs - self.alive_npcs
        lose_limit = (self.total_npcs // 2) + 1

        if killed >= lose_limit:
            self.state = GameState.END
            self.end_reason = "POPULATION_LOST"

    
    def build_case_report_lines(self):
        """
        A short stats recap shared by both endings, so the systems
        you actually played with — suspicion, close calls, ammo,
        deduction — show up in the outcome instead of vanishing.
        """
        killed = self.total_npcs - self.alive_npcs

        if self.suspicion >= self.suspicion_hostile_threshold:
            trust = "Hostile"
        elif self.suspicion >= self.suspicion_wary_threshold:
            trust = "Wary"
        else:
            trust = "Calm"

        return [
            "--- CASE REPORT ---",
            f"Civilians lost   : {killed}/{self.total_npcs}",
            f"Ammo remaining   : {self.ammo}",
            f"Close calls      : {self.monster_touches}/{self.max_monster_touches}",
            f"Public trust     : {trust}",
        ]

    def show_game_over(self):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        if self.end_reason == "LET_MONSTER_LIVE":
            outcome_lines = [
                "You had it. Face to face.",
                "You thought it was just a scared civilian.",
                "It wasn't.",
            ]
        elif self.end_reason == "MONSTER_CAUGHT_YOU":
            outcome_lines = [
                "It brushed past you one time too many.",
                "By the time you realized, it was already too late.",
            ]
        elif self.end_reason == "RED_ZONE_TIMEOUT":
            outcome_lines = [
                "You stayed too long.",
                "It stopped hiding and came straight for you.",
            ]
        elif self.end_reason == "NO_AMMO":
            outcome_lines = [
                "You ran out of ammo at the worst possible moment.",
            ]
        else:
            outcome_lines = [
                "You failed to stop the monster.",
            ]

        lines = [
            "GAME OVER",
            "",
            *outcome_lines,
            "",
            *self.build_case_report_lines(),
            "",
            "The city has fallen.",
            "",
            "Press any key to exit"
        ]

        y = h // 2 - len(lines) // 2
        for line in lines:
            self.stdscr.addstr(y, (w - len(line)) // 2, line)
            y += 1

        self.stdscr.refresh()
        self.stdscr.getch()

    def handle_encounter(self):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        lines = [
            "ENCOUNTER",
            "",
            "You are face to face with the suspect.",
            "",
            f"Ammo remaining: {self.ammo}",
            "",
            "[1] Shoot",
            "[2] Leave",
            "",
            "Choose wisely..."
        ]

        y = h // 2 - len(lines) // 2
        for line in lines:
            self.stdscr.addstr(y, (w - len(line)) // 2, line)
            y += 1

        self.stdscr.refresh()

        key = self.stdscr.getch()

        if key == ord('1'):
            self.shoot_target()
            self.in_encounter = False
            self.encounter_target = None

        elif key == ord('2'):
            # ☠️ LOSE CONDITION: you had the real monster face to
            # face and let it walk away thinking it was a civilian.
            # It doesn't make the same mistake twice.
            if self.encounter_target == "monster":
                self.state = GameState.END
                self.end_reason = "LET_MONSTER_LIVE"
            self.in_encounter = False
            self.encounter_target = None



    def show_win_screen(self):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        if self.end_reason == "WIN_CORRECT":
            outcome_lines = [
                "Your theory was correct.",
                "You identified the threat and ended it.",
            ]
        else:
            outcome_lines = [
                "The monster is dead... but your theory was wrong.",
                "You got lucky. This time.",
            ]

        lines = [
            "YOU WIN",
            "",
            *outcome_lines,
            "The city survives.",
            "",
            *self.build_case_report_lines(),
            "",
            "Press any key to exit"
        ]

        y = h // 2 - len(lines) // 2
        for line in lines:
            self.stdscr.addstr(y, (w - len(line)) // 2, line)
            y += 1

        self.stdscr.refresh()
        self.stdscr.getch()



    
    def shoot_target(self):
        if self.ammo <= 0:
            self.state = GameState.END
            self.end_reason = "NO_AMMO"
            return

        self.ammo -= 1

        # 🔴 MONSTER
        if self.encounter_target == "monster":
            self.state = GameState.END
            if self.selected_monster == self.real_monster_key:
                self.end_reason = "WIN_CORRECT"
            else:
                self.end_reason = "WIN_LUCKY"
            return

        # ⚪ NPC
        if isinstance(self.encounter_target, dict):
            npc = self.encounter_target
            npc["alive"] = False
            npc["char"] = DEAD_NPC_CHAR
            self.alive_npcs -= 1

            self.show_message(
                "BANG!\n\nInnocent died.\nThis blood is on your hands."
            )





    def show_message(self, text):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        lines = text.split("\n")
        y = h // 2 - len(lines) // 2

        for line in lines:
            self.stdscr.addstr(y, (w - len(line)) // 2, line)
            y += 1

        self.stdscr.addstr(y + 1, (w - 18) // 2, "Press any key")
        self.stdscr.refresh()
        self.stdscr.getch()



    # --------------------------------------------------
    # MAIN GAME LOOP
    # --------------------------------------------------
    def run(self):
        curses.curs_set(0)
        self.stdscr.keypad(True)

        while True:

            # ===============================
            # 🔴 ENCOUNTER MODE (BLOCKING)
            # ===============================
            if self.in_encounter:
                self.handle_encounter()

                # If encounter ended in WIN or LOSS
                if self.state == GameState.END:
                    if self.end_reason in ("WIN_CORRECT", "WIN_LUCKY"):
                        self.show_win_screen()
                    else:
                        self.show_game_over()
                    break

                continue  # ⛔ do NOT run normal game loop


            # ===============================
            # 🗺️ NORMAL GAME LOOP
            # ===============================
            game_map = MAP_1.get((self.map_x, self.map_y))
            if not game_map:
                break

            current_chunk = (self.map_x, self.map_y)
            chunk_npcs = self.npcs.get(current_chunk, [])

            # Update NPCs
            update_npcs(chunk_npcs, current_chunk, self.player)

            # Update state (RED_ZONE / HUNT)
            self.update_state()

            # ⏱ Escape timer (must leave the zone before it runs out)
            self.check_red_zone_timer()

            # ☠️ Close-call check (monster touches you in RED_ZONE)
            self.check_monster_touch()

            # Lose condition
            self.check_lose_condition()
            if self.state == GameState.END:
                self.show_game_over()
                break

            # Draw
            if self.computer.open:
                self.computer.draw(self.stdscr)
            else:
                draw(
                    self.stdscr,
                    game_map,
                    self.player,
                    chunk_npcs,
                    self.map_x,
                    self.map_y,
                    self.total_npcs,
                    self.monster,
                    self.dev_mode,
                    self
                )

            # ===============================
            # ⌨️ INPUT (ONLY ONE getch)
            # ===============================
            key = self.stdscr.getch()

            # ---------- COMPUTER ----------
            if self.computer.open:
                action = self.computer.handle_input(key)
                if action and action[0] == "SELECT_MONSTER":
                    self.selected_monster = action[1]
                    self.state = GameState.HUNT
                    self.computer.close()
                continue

            # ---------- GLOBAL ----------
            if key == ord("q"):
                break
            elif key == ord("c"):
                self.computer.toggle()
            elif key == ord("F"):
                self.dev_mode = not self.dev_mode

            # ---------- MOVEMENT ----------
            elif key in (curses.KEY_UP, ord("w")):
                self.handle_movement(0, -1)
            elif key in (curses.KEY_DOWN, ord("s")):
                self.handle_movement(0, 1)
            elif key in (curses.KEY_LEFT, ord("a")):
                self.handle_movement(-1, 0)
            elif key in (curses.KEY_RIGHT, ord("d")):
                self.handle_movement(1, 0)

            # ---------- INTERACTION ----------
            elif key in (ord("t"), ord("T")):
                self.interact()
            elif key == ord("i"):
                self.inspect_body()
            elif key == ord("v"):
                if self.state == GameState.RED_ZONE and self.is_adjacent_to_monster():
                    self.verify_monster()
                else:
                    self.check_id()

            # ---------- ENCOUNTER TRIGGER ----------
            elif key == ord("e"):
                if self.is_adjacent_to_monster():
                    self.encounter_target = "monster"
                    self.in_encounter = True
                else:
                    npc = self.get_adjacent_alive_npc()
                    if npc:
                        self.encounter_target = npc
                        self.in_encounter = True