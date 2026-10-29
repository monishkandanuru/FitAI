"""
Static Asset Build Helper for Vercel Deployment
Copies static assets into public/static when used in static-separated build pipelines.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATIC_SRC = ROOT / "static"
PUBLIC_STATIC_DST = ROOT / "public" / "static"


def main() -> None:
    if STATIC_SRC.exists():
        PUBLIC_STATIC_DST.parent.mkdir(parents=True, exist_ok=True)
        if PUBLIC_STATIC_DST.exists():
            shutil.rmtree(PUBLIC_STATIC_DST)
        shutil.copytree(STATIC_SRC, PUBLIC_STATIC_DST)
        print(f"Copied static assets to {PUBLIC_STATIC_DST}")


if __name__ == "__main__":
    main()
