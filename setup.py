import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine-tuning.
build_exe_options = {
    "packages": [
        "keyboard", "pygame", "os", "json", "flask", "logging",
        "PyQt5", "threading", "sys", "time", "subprocess"
    ],
    "include_files": ["Images/", "Audio/"],  # Adding Image and Audio directories
    "excludes": [],  # Optionally exclude certain packages/modules if not needed
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Dota2Timer",
    version="1.2",
    description="app Dota2Timer",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)
