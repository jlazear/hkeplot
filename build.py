"""
Script for building the single-file binary on Windows 7.
"""

import subprocess

commands = [
"git clone git://github.com/pyinstaller/pyinstaller.git ../pyinstaller",
"mkdir build",
"python ../pyinstaller/utils/Makespec.py -F -w -o build -n hkeplot gui.py",
"python ../pyinstaller/utils/Build.py build/hkeplot.spec",
"copy build\dist\hkeplot.exe .\hkeplot.exe",
"rmdir /Q /S build"]

for command in commands:
    try:
        print subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError:
        pass

print(
"""../pyinstaller left alone. Delete it if you do not want it."""
)
