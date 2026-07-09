import curses
from monster_db import MONSTERS


class Computer:
    def __init__(self):
        self.menu_keys = list(MONSTERS.keys())
        self.current = 0
        self.open = False

        # NEW
        self.view = "LIST"          # LIST | DETAIL
        self.selected_key = None    # monster key being viewed

    # -----------------------------
    def toggle(self):
        self.open = not self.open
        self.view = "LIST"

    def close(self):
        self.open = False
        self.view = "LIST"

    # -----------------------------
    def draw(self, stdscr):
        if self.view == "LIST":
            self.draw_list(stdscr)
        else:
            self.draw_details(stdscr)

    # -----------------------------
    def draw_list(self, stdscr):
        h, w = stdscr.getmaxyx()
        stdscr.clear()

        title = "MONSTER DATABASE"
        stdscr.addstr(2, (w - len(title)) // 2, title, curses.A_BOLD)

        for i, key in enumerate(self.menu_keys):
            label = MONSTERS[key]["name"]
            text = "> " + label if i == self.current else "  " + label
            x = (w - len(text)) // 2
            y = h // 2 - len(self.menu_keys) // 2 + i
            stdscr.addstr(y, x, text)

        hint = "↑ ↓ | Enter: Inspect | S: Select | Q: Close"
        stdscr.addstr(h - 2, (w - len(hint)) // 2, hint)

        stdscr.refresh()

    # -----------------------------
    def draw_details(self, stdscr):
        monster = MONSTERS[self.selected_key]
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        y = 2

        def add(line=""):
            nonlocal y
            if y < h - 2:
                stdscr.addstr(y, 2, line[:w-4])
                y += 1

        add("MONSTER FILE")
        add("=" * 40)
        add(f"Name : {monster['name']}")
        add(f"Type : {monster['type']}")
        add("")
        add("Description:")
        add(f"  {monster.get('description', 'N/A')}")
        add("")

        add("Powers:")
        for p in monster.get("powers", []):
            add(f"  - {p}")
        add("")

        add("Kill Signature:")
        add(f"  {monster.get('kill_signature', 'UNKNOWN')}")
        add("")

        add("Forensic Clues:")
        for k, v in monster.get("forensic_clues", {}).items():
            add(f"  {k.replace('_',' ').title():25}: {'YES' if v else 'NO'}")
        add("")

        add("Weaknesses:")
        for wkn in monster.get("weaknesses", {}):
            add(f"  - {wkn.replace('_',' ').title()}")

        add("")
        add("S: Select this monster")
        add("Q: Back")

        stdscr.refresh()

    # -----------------------------
    def handle_input(self, key):
        # -------- LIST VIEW --------
        if self.view == "LIST":
            if key == curses.KEY_UP and self.current > 0:
                self.current -= 1

            elif key == curses.KEY_DOWN and self.current < len(self.menu_keys) - 1:
                self.current += 1

            elif key == ord('\n'):
                self.selected_key = self.menu_keys[self.current]
                self.view = "DETAIL"

            elif key in (ord('q'), ord('Q')):
                self.close()

        # -------- DETAIL VIEW --------
        elif self.view == "DETAIL":
            if key in (ord('q'), ord('Q')):
                self.view = "LIST"

            elif key in (ord('s'), ord('S')):
                # FINAL SELECTION
                return ("SELECT_MONSTER", self.selected_key)

        return None
