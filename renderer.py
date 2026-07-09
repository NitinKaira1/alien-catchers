import curses
from config import PLAYER_CHAR, MAP_HEIGHT
from monster_db import MONSTERS
from game_state import GameState

SIDEBAR_WIDTH = 32


def draw(stdscr, game_map, player, npcs, map_x, map_y,
         total_npcs, monster, dev_mode, game):

    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Shift map when in HUNT (left theory panel visible)
    map_offset_x = SIDEBAR_WIDTH if game.state == GameState.HUNT else 0

    # =================================================
    # DRAW MAP
    # =================================================
    for y, row in enumerate(game_map):
        if y >= h:
            break
        stdscr.addstr(y, map_offset_x, row[:w - map_offset_x])

    # =================================================
    # DRAW NPCs
    # =================================================
    for npc in npcs:
        y, x = npc["y"], npc["x"]
        draw_x = x + map_offset_x
        if 0 <= y < h and 0 <= draw_x < w:
            stdscr.addch(y, draw_x, npc["char"])

    # =================================================
    # DRAW PLAYER
    # =================================================
    px = player.x + map_offset_x
    if 0 <= player.y < h and 0 <= px < w:
        stdscr.addch(player.y, px, PLAYER_CHAR)

    # =================================================
    # HUD
    # =================================================
    hud_y = MAP_HEIGHT
    if hud_y < h:
        hud = (
            f"Map: ({map_x},{map_y}) | "
            f"Alive: {monster.game.alive_npcs}/{total_npcs} | "
            f"WASD / Arrows | Q quit"
        )
        if game.state == GameState.RED_ZONE:
            hud += f" | Close calls: {game.monster_touches}/{game.max_monster_touches}"
            if game.red_zone_timer is not None:
                hud += f" | Escape in: {game.red_zone_timer}"
        stdscr.addstr(hud_y, map_offset_x, hud[:w - map_offset_x])

    # =================================================
    # LEFT PANEL — PLAYER THEORY (HUNT PHASE)
    # =================================================
    if game.state == GameState.HUNT and game.selected_monster:
        monster_data = MONSTERS[game.selected_monster]

        panel_lines = [
            "YOUR THEORY",
            "",
            f"Name : {monster_data['name']}",
            f"Type : {monster_data['type']}",
            "",
            monster_data["description"]
        ]

        y = 2
        x = 2
        for line in panel_lines:
            if y < h:
                stdscr.addstr(y, x, line[:SIDEBAR_WIDTH - 4])
                y += 1

    # =================================================
    # DEV PANEL (RIGHT SIDE)
    # =================================================
    if dev_mode:
        dev_lines = [
            "[DEV MODE]",
            f"Player Chunk : ({map_x},{map_y})",
            f"Monster Chunk: {monster.current_chunk}",
            "",
            "ACTIVE MONSTER:",
            f"  {game.real_monster['name']}",
            f"  {game.real_monster['type']}",
            "",
            f"Last Kill   : {monster.last_kill_chunk}",
            f"Kills Done  : {monster.total_kills}",
            f"Steps → Kill: {monster.next_kill - monster.step_counter}",
            f"STATE       : {game.state}"
        ]

        start_y = 1
        start_x = max(0, w - 35)

        for i, line in enumerate(dev_lines):
            y = start_y + i
            if y < h:
                stdscr.addstr(y, start_x, line[:35])

    # =================================================
    # RED ZONE WARNING (escalates with close calls)
    # =================================================
    if game.state == GameState.RED_ZONE:
        if game.monster_touches <= 0:
            warning = "!!! STRONG BLOOD SMELL !!!"
        elif game.monster_touches == 1:
            warning = "!!! SOMETHING IS VERY CLOSE !!!"
        else:
            warning = "!!! IT KNOWS YOU'RE HERE !!!"
        y = h // 2
        x = (w - len(warning)) // 2
        stdscr.addstr(y, x, warning, curses.A_BOLD)

        # Extra urgency once the escape timer is running low —
        # separate line so it doesn't collide with the warning above.
        if game.red_zone_timer is not None and game.red_zone_timer <= 10:
            urgent = f"⏱ ESCAPE THE ZONE — {game.red_zone_timer} LEFT"
            y2 = y + 2
            x2 = (w - len(urgent)) // 2
            stdscr.addstr(y2, x2, urgent, curses.A_BOLD)

    # =================================================
    # DRAW MONSTER — BLENDED IN LIKE ANY OTHER NPC
    # No bold, no special color, no "M". If it's in your
    # chunk, it just looks like one more person on the street.
    # =================================================
    if game.state == GameState.RED_ZONE:
        if monster.current_chunk == (map_x, map_y):
            if monster.x is not None and monster.y is not None:
                draw_x = monster.x + map_offset_x
                if 0 <= monster.y < h and 0 <= draw_x < w:
                    stdscr.addch(monster.y, draw_x, monster.char)

    stdscr.refresh()