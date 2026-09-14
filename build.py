"""Copy Flask assets into Vercel's public directory using Python only."""
from pathlib import Path
from shutil import copytree
if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    copytree(root / 'static', root / 'public' / 'static', dirs_exist_ok=True)
