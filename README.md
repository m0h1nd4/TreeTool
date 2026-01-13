# TreeTool 🌲

Ein professionelles CLI-Tool zur Visualisierung von Ordnerstrukturen als ASCII/Unicode-Art für Dokumentationszwecke.

## Features

- **Mehrere Ausgabestile:** ASCII, Unicode, Bold, Minimal
- **Flexible Filter:** Presets, Ignore-Dateien, einzelne Patterns
- **Tiefenbegrenzung:** Beliebige Verschachtelungstiefe wählbar
- **Sortierung:** Ordner zuerst (default) oder alphabetisch
- **Ausgabeformate:** stdout, `.txt`, `.md` (mit Code-Block)
- **Statistiken:** Optionale Anzeige von Ordner-/Dateianzahl
- **Farbausgabe:** Optional grün auf schwarz

## Installation

```bash
# Keine externen Abhängigkeiten erforderlich!
# Einfach die Datei herunterladen und ausführen:

chmod +x treetool.py
./treetool.py --help
```

## Verwendung

### Grundlegende Beispiele

```bash
# Aktuelles Verzeichnis anzeigen
python treetool.py .

# Bestimmtes Verzeichnis mit Tiefenbegrenzung
python treetool.py /pfad/zum/projekt --depth 3

# Als Markdown-Datei speichern
python treetool.py ./src --output struktur.md

# Als Textdatei speichern
python treetool.py ./src --output struktur.txt
```

### Stil-Optionen

```bash
# Unicode-Stil (├── └──)
python treetool.py . --style unicode

# Bold-Stil (┣━━ ┗━━)
python treetool.py . --style bold

# Minimal-Stil (|-- `--)
python treetool.py . --style minimal

# Mit Farbausgabe (grün auf schwarz)
python treetool.py . --style unicode --color
```

### Filter-Optionen

```bash
# Python-Preset (ignoriert __pycache__, .venv, etc.)
python treetool.py . --preset python

# Node-Preset (ignoriert node_modules, etc.)
python treetool.py . --preset node

# Mehrere Presets kombinieren
python treetool.py . --preset python --preset git --preset ide

# Alle Presets aktivieren
python treetool.py . --preset all

# Eigene Ignore-Datei verwenden
python treetool.py . --ignore-file .treeignore

# Einzelne Patterns ausschließen
python treetool.py . --exclude "*.log" --exclude "temp/"

# Versteckte Dateien ausblenden
python treetool.py . --no-hidden
```

### Sortierung & Filterung

```bash
# Nur Ordner anzeigen
python treetool.py . --dirs-only

# Nur Dateien anzeigen
python treetool.py . --files-only

# Alphabetisch sortieren (statt Ordner zuerst)
python treetool.py . --alphabetic
```

### Mit Statistiken

```bash
# Statistiken am Ende anzeigen
python treetool.py . --stats

# Vollständiges Beispiel
python treetool.py ./mein-projekt \
    --preset python \
    --depth 4 \
    --style unicode \
    --stats \
    --output dokumentation.md
```

## Ignore-Datei Format

Erstelle eine `.treeignore` Datei im gitignore-Stil:

```gitignore
# Kommentare beginnen mit #
__pycache__
*.pyc
*.log

# Ordner mit / am Ende
node_modules/
.git/
dist/
build/

# Glob-Patterns
*.tmp
test_*
```

## Ausgabebeispiele

### ASCII (Default)

```
mein-projekt/
|-- src/
|   |-- main.py
|   +-- utils.py
|-- tests/
|   +-- test_main.py
|-- README.md
+-- setup.py
```

### Unicode

```
mein-projekt/
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
├── README.md
└── setup.py
```

### Bold

```
mein-projekt/
┣━━ src/
┃   ┣━━ main.py
┃   ┗━━ utils.py
┣━━ tests/
┃   ┗━━ test_main.py
┣━━ README.md
┗━━ setup.py
```

## Verfügbare Presets

| Preset | Ignoriert |
|--------|-----------|
| `python` | `__pycache__`, `*.pyc`, `.venv`, `venv`, `*.egg-info`, `dist`, `build`, `.pytest_cache`, `.mypy_cache` |
| `node` | `node_modules`, `npm-debug.log*`, `.npm`, `dist`, `build`, `.next`, `.nuxt` |
| `git` | `.git`, `.gitignore`, `.gitattributes`, `.gitmodules` |
| `ide` | `.idea`, `.vscode`, `*.swp`, `.project`, `*.sublime-*` |
| `all` | Alle obigen kombiniert |

## CLI-Referenz

```
usage: treetool [-h] [-V] [-o FILE] [--stats] [--color] [-d N] [--dirs-only]
                [--files-only] [--no-hidden] [-p {python,node,git,ide,all}]
                [-i FILE] [-e PATTERN] [-s {ascii,unicode,bold,minimal}] [-a]
                [path]

Generate beautiful ASCII tree representations of directory structures.

positional arguments:
  path                  Root directory path (default: current directory)

Output Options:
  -o, --output FILE     Output file (.txt or .md)
  --stats               Show statistics (directory/file counts)
  --color               Enable colored output (green on black)

Filter Options:
  -d, --depth N         Maximum depth to display
  --dirs-only           Show only directories
  --files-only          Show only files
  --no-hidden           Exclude hidden files and directories

Ignore Patterns:
  -p, --preset          Use preset ignore patterns
  -i, --ignore-file     Path to ignore file
  -e, --exclude         Exclude pattern (repeatable)

Style Options:
  -s, --style           Tree drawing style (default: ascii)
  -a, --alphabetic      Sort alphabetically
```

## Lizenz

Apache-2.0

---

*Made with ❤️ for documentation purposes*

