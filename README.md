# Virtual Drum Server

Uses PyGame to play sounds, Websocket to connect to ESP32, eel for UI

# Development

## Setup virtual environment

FOllow the instructions [here](https://docs.python.org/3/library/venv.html)

```bash
python -m venv venv
```

## Activate the virtual environment

```bash
source venv/bin/activate
```

## Install dependencies
```bash
pip install -r requirements.txt
```

## Build Tailwind
```bash
cd web
npm i
npm build
```

## Run the server
```bash
python main.py
```

## Build the executable
```bash
pyinstaller main.spec
```
