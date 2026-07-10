# v0.2.0 — Sound, Difficulty & Onboarding

Alien Catchers now has sound, adjustable difficulty, and an actual
in-game explanation of how to play. 🎧🎚️

## What's new

**🔊 Audio** — background music now shifts with the tension: calm in
Investigation, tenser in Hunt, a dissonant heartbeat pulse once you're
in a Red Zone. Win/lose stingers, gunshot and close-call SFX included.
Everything is optional — no `pygame`? No audio files? The game just
runs silently, no crashes.

**🎚️ Difficulty presets** — pick Easy, Normal, or Hard right from the
main menu. Scales ammo, how forgiving Red Zone close calls are, how
long you have to escape, and how fast the city turns on you for
over-interrogating civilians.

| | Easy | Normal | Hard |
|---|---|---|---|
| Ammo | 8 | 6 | 4 |
| Close calls before death | 4 | 3 | 2 |
| Red zone escape time | 55 | 40 | 28 |

**📖 How to Play screen** — a new menu option explains the premise and
lists every control, so you're not guessing what `V` or `C` does.

## Install / update

```bash
git pull
pip install -e . --upgrade
alien-catchers
```

Full details in [CHANGELOG.md](changelog.md).
