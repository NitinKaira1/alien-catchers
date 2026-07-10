# Changelog

## v0.2.0 — Sound, Difficulty & Onboarding

### Added
- **Audio system** — background music that shifts with game state
  (menu / investigation / hunt / red zone), win/lose stingers, gunshot
  and close-call SFX. Fully optional — the game runs silently if
  `pygame` isn't installed or audio files are missing.
- **Difficulty presets** — Easy / Normal / Hard, selectable from the
  main menu. Scales ammo, Red Zone touch chance, escape timer length,
  and suspicion thresholds.
- **How to Play screen** — accessible from the main menu, explains the
  premise and lists every control. No more guessing.
- **Menu tagline** for a bit more atmosphere on the title screen.
- Difficulty now shown in the end-of-game case report.

## v0.1.0 — Initial Release

### Added
- Core investigation-horror loop: an alien disguised as a civilian,
  hidden among identical-looking NPCs.
- Forensic investigation — inspect bodies, cross-reference clues in
  the monster database, and build a working theory.
- Blend-in disguise mechanic — the real monster is visually and
  structurally indistinguishable from a normal NPC until you dig.
- Red-herring NPCs that share the same "suspicious" tells as the real
  threat, so a single odd note isn't proof.
- Multiple lose conditions: population loss, mistaking the monster for
  a civilian, 3 close calls in a Red Zone, and a Red Zone escape timer.
- Suspicion system — over-interrogating civilians makes the city wary
  of you and speeds up the real threat.
- Dynamic case report on every ending.