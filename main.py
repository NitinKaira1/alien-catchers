import curses
from menu import run_menu
from game import Game
from NPC import distribute_npcs_across_chunks, NPCS




def main(stdscr):
    while True:
        choice = run_menu(stdscr)

        if choice == "Start Game":
            # 🔁 NEW GAME = NEW WORLD
            NPCS.clear()

            total_npcs = distribute_npcs_across_chunks()
            game = Game(stdscr, NPCS, total_npcs)
            game.run()

        elif choice == "Quit":
            break


def run():
    """Entry point used by the installed `alien-catchers` command."""
    # audio.init()
    try:
        curses.wrapper(main)
    finally:
        # audio.quit()
        pass


if __name__ == "__main__":
    run()