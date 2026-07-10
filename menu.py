import curses
import audio
from config import DIFFICULTY_PRESETS, DEFAULT_DIFFICULTY


DIFFICULTIES = list(DIFFICULTY_PRESETS.keys())
_difficulty_index = DIFFICULTIES.index(DEFAULT_DIFFICULTY)

TAGLINE = "Someone in this city isn't human. Find them before they find you."

CONTROLS = [
    ("W A S D / Arrows", "Move"),
    ("T", "Talk to a nearby person"),
    ("I", "Inspect a body for evidence"),
    ("V", "Check ID / verify a suspect"),
    ("E", "Start an encounter (shoot or leave)"),
    ("C", "Open the monster database"),
    ("Q", "Quit"),
]

HOW_TO_PLAY_TEXT = [
    "An alien is hiding in this city, disguised as an ordinary",
    "civilian. It looks exactly like everyone else on screen.",
    "",
    "Inspect bodies and cross-reference clues in the monster",
    "database to build a theory before you act. Check IDs to look",
    "for a tell -- but a few innocent people can look suspicious",
    "too, so a single odd note isn't proof.",
    "",
    "Watch your ammo, watch your suspicion, and once you're in a",
    "Red Zone -- get out before time runs out.",
]


def run_menu(stdscr):
    global _difficulty_index

    curses.curs_set(0)
    stdscr.keypad(True)

    audio.play_music("menu")

    # Rows: 0 = Start Game, 1 = Difficulty, 2 = How to Play, 3 = Quit
    selected = 0
    row_count = 4

    while True:
        stdscr.clear()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        title = "Alien Catchers"

        h, w = stdscr.getmaxyx()

        x = (w - len(title)) // 2
        stdscr.addstr(5, x, title, curses.color_pair(1))

        tag_x = max(0, (w - len(TAGLINE)) // 2)
        stdscr.addstr(6, tag_x, TAGLINE[:w])

        labels = [
            "Start Game",
            f"Difficulty: < {DIFFICULTIES[_difficulty_index]} >",
            "How to Play",
            "Quit",
        ]

        for i, label in enumerate(labels):
            prefix = "> " if i == selected else "  "
            stdscr.addstr(5 + i + 3, x, prefix + label)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < row_count - 1:
            selected += 1
        elif selected == 1 and key in (curses.KEY_LEFT, curses.KEY_RIGHT):
            step = -1 if key == curses.KEY_LEFT else 1
            _difficulty_index = (_difficulty_index + step) % len(DIFFICULTIES)
        elif key == ord('\n'):
            if selected == 1:
                # Enter also cycles difficulty forward
                _difficulty_index = (_difficulty_index + 1) % len(DIFFICULTIES)
            elif selected == 2:
                show_instructions(stdscr)
            elif selected == 0:
                return "Start Game", DIFFICULTIES[_difficulty_index]
            elif selected == 3:
                return "Quit", DIFFICULTIES[_difficulty_index]
        elif key == ord('q'):
            return "Quit", DIFFICULTIES[_difficulty_index]


def show_instructions(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    y = 2
    heading = "HOW TO PLAY"
    stdscr.addstr(y, (w - len(heading)) // 2, heading, curses.A_BOLD)
    y += 2

    for line in HOW_TO_PLAY_TEXT:
        if y < h - 2:
            stdscr.addstr(y, 4, line[:w - 8])
            y += 1

    y += 1
    if y < h - 2:
        stdscr.addstr(y, 4, "CONTROLS", curses.A_BOLD)
        y += 1

    for keys, desc in CONTROLS:
        if y < h - 2:
            stdscr.addstr(y, 4, f"{keys:<20} {desc}"[:w - 8])
            y += 1

    footer = "Press any key to return"
    if y < h:
        stdscr.addstr(min(y + 2, h - 1), 4, footer[:w - 8])

    stdscr.refresh()
    stdscr.getch()