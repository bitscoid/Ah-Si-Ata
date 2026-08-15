#!/usr/bin/env bash
# Setup script for Linux (originally written for Termux)
set -e

PYTHON="python3"

# --- Install system dependencies -------------------------------------------
if command -v apt-get >/dev/null 2>&1; then
    SUDO=""
    [ "$(id -u)" -ne 0 ] && SUDO="sudo"
    $SUDO apt-get update -y
    $SUDO apt-get install -y python3 python3-pip python3-venv git python3-pillow
elif command -v dnf >/dev/null 2>&1; then
    SUDO=""
    [ "$(id -u)" -ne 0 ] && SUDO="sudo"
    $SUDO dnf install -y python3 python3-pip git python3-pillow
elif command -v pacman >/dev/null 2>&1; then
    SUDO=""
    [ "$(id -u)" -ne 0 ] && SUDO="sudo"
    $SUDO pacman -S --noconfirm python python-pip git python-pillow
else
    echo "Package manager not recognized."
    echo "Install python3, pip, git, and pillow manually, then re-run this script."
fi

# --- Python virtual environment --------------------------------------------
if [ ! -d "venv" ]; then
    $PYTHON -m venv venv
fi
source venv/bin/activate

# --- Install Python dependencies -------------------------------------------
pip install -r requirements.txt

echo ""
echo "Setup selesai. Jalankan dengan:"
echo "  source venv/bin/activate"
echo "  python main.py"