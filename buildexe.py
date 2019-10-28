import sys, os
import os.path
import git
from cx_Freeze import setup, Executable

r = git.repo.Repo('./')

targetName="wowviewer"
__version__ = r.git.describe("--tags", "--dirty")

split_ver = __version__.split(".")
split_ver_last = split_ver[2].split("-")
if len(split_ver_last) < 3:
    commit_ver = 0
else:
    commit_ver = split_ver_last[1]
win_ver = "{maj}.{min}.{mic}.{commit}".format(maj=split_ver[0][1:],
                                              min=split_ver[1],
                                              mic=split_ver_last[0],
                                              commit=commit_ver
                                              )

copyright = "(c) 2018 986-Studio"
packages = ["datetime", "PIL", "tkinter", "WowFile"]

includes = []

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

constants="BUILD_VERSION='{ver}'".format(ver=__version__)

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    includes = [
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
         ]
    targetName = targetName + ".exe"

options = {
    'build_exe': {
        'include_files': includes,
        'packages': packages,
        'include_msvcr': True,
        'constants': constants,
    },
}

executable = [
    Executable("main.py",
               base=base,
               targetName=targetName,
               copyright=copyright,
               )
]

setup(
    name = "WOWFileViewer",
    description='Viewer for SparkMaker WOW files',
    version=win_ver,
    options=options,
    executables=executable
)