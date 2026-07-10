import os
 
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
 
try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False
 
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio")
 
# Looping background tracks, keyed by a short name the game code uses.
MUSIC_TRACKS = {
    "menu": "menu.ogg",
    "investigation": "investigation.ogg",
    "hunt": "hunt.ogg",
    "red_zone": "red_zone.ogg",
}
 
# One-shot tracks (played once, not looped).
STINGER_TRACKS = {
    "win": "win.ogg",
    "lose": "lose.ogg",
}
 
# Short sound effects.
SFX_FILES = {
    "gunshot": "gunshot.wav",
    "close_call": "close_call.wav",
}
 
_enabled = _PYGAME_AVAILABLE
_current_music = None
_sfx_cache = {}
 
 
def init():
    """Call once at startup, before curses takes over the screen."""
    global _enabled
    if not _PYGAME_AVAILABLE:
        _enabled = False
        return
    try:
        pygame.mixer.init()
    except Exception:
        # No audio device available, or SDL not set up — game just
        # runs silently instead of crashing.
        _enabled = False
 
 
def _resolve(table, name):
    filename = table.get(name)
    if not filename:
        return None
    path = os.path.join(AUDIO_DIR, filename)
    return path if os.path.exists(path) else None
 
 
def play_music(name, loop=True, volume=0.6):
    """Play a looping background track. No-ops if already playing it."""
    global _current_music
    if not _enabled:
        return
    if _current_music == name:
        return  # already the active track — don't restart it
 
    path = _resolve(MUSIC_TRACKS, name)
    if not path:
        _current_music = name  # remember intent even if file's missing
        return
 
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)
        _current_music = name
    except Exception:
        pass
 
 
def play_stinger(name, volume=0.7):
    """Play a one-shot track (win/lose jingle) once, no looping."""
    global _current_music
    if not _enabled:
        return
 
    path = _resolve(STINGER_TRACKS, name)
    _current_music = None
    if not path:
        return
 
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(0)
    except Exception:
        pass
 
 
def stop_music():
    global _current_music
    if not _enabled:
        return
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    _current_music = None
 
 
def play_sfx(name, volume=0.8):
    """Play a short one-shot sound effect. Can overlap with music."""
    if not _enabled:
        return
 
    if name not in _sfx_cache:
        path = _resolve(SFX_FILES, name)
        if not path:
            _sfx_cache[name] = None
        else:
            try:
                _sfx_cache[name] = pygame.mixer.Sound(path)
            except Exception:
                _sfx_cache[name] = None
 
    sound = _sfx_cache[name]
    if sound:
        try:
            sound.set_volume(volume)
            sound.play()
        except Exception:
            pass
 
 
def quit():
    if not _enabled:
        return
    try:
        pygame.mixer.quit()
    except Exception:
        pass