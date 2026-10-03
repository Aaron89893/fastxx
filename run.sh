#!/usr/bin/env bash
# Script chạy cho môi trường WSL / Linux

if command -v python.exe &> /dev/null; then
    echo "[*] Chạy qua Python Windows..."
    python.exe auto_test.py "$@"
elif command -v python3 &> /dev/null; then
    python3 auto_test.py "$@"
else
    python auto_test.py "$@"
fi
