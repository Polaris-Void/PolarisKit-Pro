#!/bin/bash
# Build PolarisKit.exe (Windows x64) with mingw-w64 cross-compiler.
set -e
cd "$(dirname "$0")/src"
echo "[1/4] self-test (patch engine + payload integrity)..."
gcc -DPOLARIS_TEST_HARNESS -Wall -Wextra -o /tmp/polaris_selftest test_patch.c
(cd /home/user/polaris-kit/src && /tmp/polaris_selftest)
echo "[2/4] compiling resources (icon + manifest + version info)..."
x86_64-w64-mingw32-windres app.rc -O coff -o app.res
echo "[3/4] compiling PolarisKit.exe..."
x86_64-w64-mingw32-gcc -std=c11 -Os -s -mwindows -municode \
  -Wall -Wextra -Wno-unused-parameter \
  -o ../PolarisKit.exe polaris_kit.c app.res \
  -lshell32 -lole32 -luuid
rm -f app.res
echo "[4/4] verifying PE..."
file ../PolarisKit.exe
x86_64-w64-mingw32-objdump -p ../PolarisKit.exe | grep -E "DLL Name" | sort -u
ls -la ../PolarisKit.exe
echo "BUILD OK"
