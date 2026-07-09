import curses


MENU_OPTIONS = ["Start Game", "Quit"]

def run_menu(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)

    selected = 0
    
    while True:
        stdscr.clear()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        title= "Alien Catchers"

        h,w = stdscr.getmaxyx()

        x = (w - len(title)) // 2

        stdscr.addstr(5, x, title, curses.color_pair(1))

        for i in range(len(MENU_OPTIONS)):
            if i == selected:
                stdscr.addstr(5 + i + 2, x, "> " + MENU_OPTIONS[i])
            else:
                stdscr.addstr(5 + i + 2, x, "  " + MENU_OPTIONS[i])

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(MENU_OPTIONS) - 1:
            selected += 1
        elif key == ord('\n'):
            break
        elif key == ord('q'):
            break

    return MENU_OPTIONS[selected]