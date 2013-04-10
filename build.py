"""
Script for building the single-file binary on Windows 7.
"""

import subprocess
import sys

# Win7 build procedure
if sys.platform == 'win32':
    commands = [
    "git clone git://github.com/pyinstaller/pyinstaller.git ../pyinstaller",
    "mkdir build",
    "python ../pyinstaller/utils/Makespec.py -F -w -o build -n hkeplot gui.py",
    "python ../pyinstaller/utils/Build.py build/hkeplot.spec",
    "copy build\dist\hkeplot.exe .\hkeplot.exe",
    "rmdir /Q /S build"]

# OS X build procedure
elif sys.platform == 'darwin':
    commands = [
        "echo 'Build requires py2app -- install with pip py2app if not yet installed'",
        "rm -r dist build",
        "py2applet --make-setup gui.py",
        "python setup.py py2app",
        "cp -r dist/gui.app ./hkeplot.app",
        "rm -r dist build",
        "rm setup.py"]


for command in commands:
    try:
        print subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError:
        pass

if sys.platform == 'win32':
    print("../pyinstaller left alone. Delete it if you do not want"
          " it.")
