# aps-kiosk

Build for Raspberry pi 4b:
```
apt-get update -q -y
apt-get install -q -y build-essential cmake golang libuv1-dev libz-dev git
git clone --recursive https://github.com/cirospaciari/socketify.py.git
CFLAGS="-Wno-error=stringop-overflow" make linux PLATFORM=aarch64

edit .venv\lib\python3.11\site-packages\socketify\native.py
```