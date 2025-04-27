
# 📋 QuickToDo

QuickToDo is a simple, lightweight, and ultra-fast desktop app for managing tasks and notes.  
Designed to stay always on top, easy to open, quick to add tasks — without disturbing your workflow.

**Built with Python and Tkinter. Packaged as an EXE for Windows.**

---

## ✨ Features

- 📝 Minimalistic and clean UI
- 🚀 Instant window toggle via **ALT+Q**
- ✨ Click-through transparent mode (**ALT+T**)
- 🔲 Quick toggle task done/undone by clicking
- 💬 Multi-language support: **English** and **German**
- 🛠️ Full settings menu:
  - Window position (spawn corner)
  - Margin settings
  - Transparency adjustment
  - Enable/Disable window click-through
  - Language selection
  - Auto-start toggle (launch with Windows)
- 💾 Tasks and settings are saved locally
- 📋 Fully portable after installation
- 🔎 Searchable via Windows Start Menu ("Quick", "ToDo", "QuickToDo", etc.)

---

## 🛠️ Installation

**First Launch** installs QuickToDo automatically:

1. Download and run **QuickToDo.exe**.
2. On the first start:
   - The app installs itself to  
     `C:\Users\<YourUsername>\AppData\Local\QuickToDo\`
   - A Start Menu shortcut is created under  
     `Start > Programs > QuickToDo`
   - Windows search will find it by typing **Quick**, **ToDo**, or **QuickToDo**.
3. The app launches immediately after installation.

✅ That's it! No complicated setup needed.

---

## ⌨️ Hotkeys

| Key Combo     | Action                          |
|---------------|----------------------------------|
| `ALT + Q`     | Toggle the QuickToDo window      |
| `ALT + T`     | Toggle transparency mode         |
| `ALT + C`     | Force-disable click-through mode |

---

## ⚙️ Settings Menu

Accessible by clicking the **⚙️ Settings** button at the top.

Customize:

- Spawn corner: Top Left / Top Right / Bottom Left / Bottom Right
- Window margins
- Transparency (10% - 100%)
- Enable/Disable click-through
- Enable/Disable autostart with Windows
- Language selection

Settings are automatically saved and restored on next launch.

---

## 📂 Data Storage

QuickToDo stores your tasks and settings here:

- Tasks:  
  `C:\Users\<YourUsername>\AppData\Local\QuickToDo\todos.json`
- Settings:  
  `C:\Users\<YourUsername>\AppData\Local\QuickToDo\settings.json`

---

## 🚀 Build Your Own EXE (Optional)

If you want to build the executable manually:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=icon.png main.py
```

- `--onefile`: Packs into a single `.exe`
- `--noconsole`: Hides the terminal window
- `--icon=icon.png`: Adds a custom app icon

> ⚡ The `main.py` file already includes the self-installation mechanism.

---

## 🛡️ Requirements (for building)

- Python 3.10+  
- Required Python packages:
  - `tkinter` (comes pre-installed)
  - `keyboard`
  - `pywin32`
  - `winshell`

Install missing packages via:

```bash
pip install keyboard pywin32 winshell
```

---

## 📄 License

This project is **free to use**.  
Feel free to modify and improve it!

---
