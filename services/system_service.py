import os
import subprocess
import sys
from pathlib import Path


def open_folder(path):
    folder = Path(path).resolve()

    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError("La carpeta de resultados todavía no existe.")

    if sys.platform.startswith("win"):
        os.startfile(str(folder))
        return

    if sys.platform == "darwin":
        subprocess.Popen(["open", str(folder)])
        return

    subprocess.Popen(["xdg-open", str(folder)])
