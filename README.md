# Hunt: Showdown Outfitter

A tool to manage item presets for Hunt: Showdown and semi-automatically
equip them in the game by automating mouse and keyboard against
preconfigured coordinates.

### Prerequisites

```bash
$ pip install -r requirements
```

### Run local instance
```bash
$ python main.py
```

### Build single file .exe

```bash
$ pip install pyinstaller
$ python -m eel --onefile --noconsole main.py frontend
```
