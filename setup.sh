#!/usr/bin/env bash
# Setup script for Linux (originally written for Termux).
#
# Installs system dependencies, creates the Python virtual environment and
# installs Python dependencies. Safe to re-run (idempotent).
#
# Fixed for Linux:
#   - uses "venv/bin/python -m pip" instead of "source activate && pip"
#     (avoids the PEP 668 "externally-managed-environment" error on Debian/Ubuntu)
#   - detects a stale/moved venv (hardcoded absolute paths in activate/pip)
#     and recreates it automatically
#   - drops the unneeded system "python3-pillow" package
#   - creates .env from .env.template when missing
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

VENV_DIR="venv"
PYTHON="${PYTHON:-python3}"

info() { printf '\n==> %s\n' "$*"; }

# --- Helper: is the existing venv usable (not stale / moved)? -------------
# A venv copied or moved from another folder keeps hardcoded absolute paths
# in bin/activate and bin/pip, which silently breaks "source activate".
venv_is_usable() {
    [ -x "$VENV_DIR/bin/python" ] || return 1
    grep -qF "$PROJECT_DIR/$VENV_DIR" "$VENV_DIR/bin/activate" 2>/dev/null || return 1
    "$VENV_DIR/bin/python" -m pip --version >/dev/null 2>&1 || return 1
}

# --- 1. System dependencies -----------------------------------------------
install_system_deps() {
    local pkg_mgr="" sudo_cmd=""
    command -v apt-get >/dev/null 2>&1 && pkg_mgr="apt"
    command -v dnf     >/dev/null 2>&1 && pkg_mgr="dnf"
    command -v pacman  >/dev/null 2>&1 && pkg_mgr="pacman"
    command -v apk     >/dev/null 2>&1 && pkg_mgr="apk"
    [ "$(id -u)" -ne 0 ] && sudo_cmd="sudo"

    case "$pkg_mgr" in
        apt)
            $sudo_cmd apt-get update -y
            $sudo_cmd apt-get install -y python3 python3-pip python3-venv git
            ;;
        dnf)
            $sudo_cmd dnf install -y python3 python3-pip git
            ;;
        pacman)
            $sudo_cmd pacman -S --noconfirm python python-pip git
            ;;
        apk)
            $sudo_cmd apk add --no-cache python3 py3-pip git
            ;;
        *)
            echo "Package manager not recognized."
            echo "Install python3, pip, and git manually, then re-run this script."
            return 1
            ;;
    esac
}

if ! install_system_deps; then
    echo "Continuing anyway; python3 must already be available."
fi

# --- 2. Python virtual environment -----------------------------------------
if [ -d "$VENV_DIR" ] && ! venv_is_usable; then
    info "Existing '$VENV_DIR' is stale or broken (e.g. moved from another folder). Recreating ..."
    rm -rf "$VENV_DIR"
fi

if [ ! -d "$VENV_DIR" ]; then
    info "Creating Python virtual environment ..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

info "Upgrading pip ..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip

# --- 3. Python dependencies -------------------------------------------------
info "Installing Python dependencies ..."
"$VENV_DIR/bin/python" -m pip install -r requirements.txt

# --- 4. Environment file -----------------------------------------------------
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        cp ".env.template" ".env"
        info "Created '.env' from '.env.template' — edit it and fill in the values."
    else
        echo "Warning: '.env.template' not found, skipping '.env' creation."
    fi
fi

echo ""
echo "Setup selesai. Jalankan dengan:"
echo "  make run"
echo "atau manual:"
echo "  $VENV_DIR/bin/python main.py"