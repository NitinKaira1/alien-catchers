# 👽 Alien Catchers

*Someone in this city isn't human. Find them before they find you.*

A terminal-based investigation-horror game built with Python's `curses`
library. An alien is hiding in plain sight, disguised as an ordinary
civilian. You have to gather forensic evidence, cross-reference a monster
database, and check people's IDs — all while the thing you're hunting
might be checking you back.

```
##########################################################
#..........................................................#
#...OOOO...........@........................................#
#..........................................................#
```
*(the `@` is you — one of the `O`s nearby is not what it seems)*

## Features

- **Blend-in disguise mechanic** — the alien looks and moves exactly like
  any other NPC. No red flags, no glowing outline.
- **Forensic investigation** — inspect bodies, cross-reference clues
  against a monster database, and build a real theory before you act.
- **Red herrings** — some innocent civilians share the same "suspicious"
  tells as the real threat. A single odd note isn't enough to convict.
- **Multiple ways to lose**:
  - Population drops below 50% survival
  - You mistake the real monster for a civilian and let it go
  - It brushes past you 3 times in a Red Zone
  - You linger in a Red Zone too long and it catches up to you
- **Suspicion system** — interrogate too many people and the city turns
  wary of you, giving the real threat more room to move.
- **Dynamic case report** — every ending recaps your ammo, civilian
  casualties, close calls, and public trust.


## Installation

### Option 1 — clone and install (recommended)

```bash
git clone https://github.com/NitinKaira1/alien-catchers.git
cd alien-catchers
pip install -e .
alien-catchers
```

### Option 2 — install directly from GitHub, no clone needed

```bash
pipx install git+https://github.com/NitinKaira1/alien-catchers.git
alien-catchers
```

*(`pipx` keeps it in its own isolated environment — install with
`pip install pipx` first if you don't have it.)*

### Option 3 — just run it, no install

```bash
git clone https://github.com/NitinKaira1/alien-catchers.git
cd alien-catchers
pip install -r requirements.txt   # Windows only actually needs this
python main.py
```

> **Windows users:** the standard library's `curses` module doesn't exist
> on Windows. `windows-curses` (pulled in automatically above) fixes that.
> A modern terminal (Windows Terminal) is recommended.

## Controls

| Key | Action |
|---|---|
| `W`/`A`/`S`/`D` or Arrow Keys | Move |
| `T` | Talk to an adjacent NPC |
| `I` | Inspect a dead body |
| `V` | Check ID / verify a suspect |
| `E` | Start an encounter (shoot or leave) |
| `C` | Open the monster database (Computer) |
| `F` | Toggle dev/debug panel |
| `Q` | Quit |



## Tech

Pure Python standard library (`curses`) for rendering, no external
dependencies required to play. Optional `pygame` for audio.

## License

MIT — see [LICENSE](LICENSE).
