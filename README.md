# Samurai

> This project have been archived and is no longer maintained.
>
> It requires further abstraction and refactoring before continuing development.
>
> This repository serves as a reminder of my progress and where I started.

**IMPORTANT** -- All commands are executed from the root directory of the project.

## Optional

### Ubuntu

```shell
# You may need to install this audio library
# if running the application causes it to throw on
# audio driver not found.
sudo apt update && \
sudo apt install libpulse0
```

## Setup

```shell
# Install dependencies locally
# and activate the virtual environment.
source setup.sh
```

## Usage

```bash
# Run the game using the command:
python3 game.py
```

```bash
# Use the editor (saves and loads "map.json"
# in the same directory as "editor.py"):
python editor.py
```
