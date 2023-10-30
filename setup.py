import os

from cx_Freeze import Executable, setup

include_files = ['Audio', 'Images']

# Make sure to provide the full path for each folder
include_files = [(folder, os.path.join(folder)) for folder in include_files]

executables = [
    Executable("main.py"),
    Executable("flask_server.py"),
    Executable("menu.py"),
]

setup(
    name="Dota2Gsi",
    version="1.2",
    description="Dota2Gsi",
    executables=executables,
    options={
        'build_exe': {
            'include_files': include_files,
        },
    }
)
