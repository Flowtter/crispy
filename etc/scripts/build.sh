#!/bin/sh

rm -rf build
mkdir -p build/windows

find crispy-api | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
find crispy-api | grep -E "(/\.mypy_cache$)" | xargs rm -rf

cp -r etc/default-settings.json build/windows/settings.json
cp -r crispy-api/requirements.txt build/windows
cp -r crispy-api/api build/windows/
cp -r crispy-api/assets build/windows/

cd crispy-frontend && npm run build
cd ..

cp -r crispy-frontend/public build/windows/frontend

mkdir build/windows/resources
mkdir build/windows/resources/videos
mkdir build/windows/resources/musics

# -----------
mkdir build/linux
cp -r build/windows/* build/linux
# -----------

cp -r etc/scripts/windows/* build/windows/
cp -r etc/scripts/linux/* build/linux/

cd build
zip -r windows.zip windows/ >/dev/null
zip -r linux.zip linux/ >/dev/null
cd ..
