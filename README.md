# The Sims 3 Management Program

[![license](https://img.shields.io/github/license/jonaheinke/sims-3-clear-cache)](LICENSE)
[![code size](https://img.shields.io/github/languages/code-size/jonaheinke/sims-3-clear-cache)](#)

This is a simple python script to clear all the caches of The Sims 3. It is written in python 3.10 and uses tkinter for the GUI.

It is intended to launch before every gameplay. You have to take care of that yourself. Instructions on how to do that are listed at Create a desktop shortcut.

## Screenshots

Light Mode                | Dark Screenshot
:------------------------:|:-----------------------:
![](screenshot_light.png) | ![](screenshot_dark.png)

## Usage

### Clone repository

```bash
git clone --recurse-submodules https://github.com/jonaheinke/sims-3-clear-cache.git
```

### Run script

```bash
python main.py [--dark]
```

No external dependencies are needed.

### Alternative: Create a desktop shortcut

Add a `The Sims 3.cmd` file to your desktop and put the following lines in it:

```bash
python ABSOLUTE_PATH_TO_MAIN_PY [--dark]
ABSOLUTE_PATH_TO_Sims3LauncherW.exe_IN_QUOTATION_MARKS
```

### All Command line arguments

| Name     | Option       | Description                         |
|----------|--------------|-------------------------------------|
| Help     | `-h, --help` | show help message                   |
| Darkmode | `--dark`     | enable dark mode                    |
| Debug    | `--debug`    | enable debug mode (not recommended) |

## Known Issues

Planned:
- Can't detect the game folders automatically. Currently they have to be set manually.
- Can't detect the installed expansion packs. It would disable the unavailable expansion and stuff checkbox options.
- Can't detect if Cache files are present. It would disable the unavailable cache clearing options.

Waiting list:
- The main menu logo is still the latest installed expansion or stuff pack logo.

Won't be fixed:
- None

## Credits

used tkinter theme: [Forest theme by rdbende](https://github.com/rdbende/Forest-ttk-theme)