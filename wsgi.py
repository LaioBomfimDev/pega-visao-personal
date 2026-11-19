from pathlib import Path
import sys

SISTEMA_DIR = Path(__file__).resolve().parent / "anamnesePersonal" / "sistema"
if str(SISTEMA_DIR) not in sys.path:
    sys.path.insert(0, str(SISTEMA_DIR))

from app import app  # noqa: E402, F401
