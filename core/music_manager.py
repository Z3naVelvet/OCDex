from pathlib import Path
import pygame

EXTENSIONS = (".ogg",".mp3",".wav",".flac",".mid",".midi")

def start_music(base_dir, volume=.90):
    try:
        pygame.mixer.init()
        for ext in EXTENSIONS:
            p = Path(base_dir) / ("ocdex_music" + ext)
            if p.exists():
                pygame.mixer.music.load(str(p))
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)
                return True
    except Exception:
        pass
    return False
