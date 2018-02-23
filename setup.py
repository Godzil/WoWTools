import sys, osimport os.path
import git
from cx_Freeze import setup, Executable


targetName="wowviewer"
__version__ = "0.1.0"
copyright = "(c) 2018 986-Studio"
packages = ["datetime", "PIL", "tkinter", "wow"]

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    targetName = targetName + ".exe"

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

options = {
    'build_exe': {
        'include_files':[
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
         ],
        'packages': packages,
        'include_msvcr': True,
    },
}

executable = [
    Executable("main.py", base=base, targetName=targetName, copyright=copyright)
]

setup(
    name = "WOWFileViewer",
    description='Viewer for SparkMaker WOW files',
    version=__version__,
    options=options,
    executables=executable
)