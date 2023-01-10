#!/bin/sh

rm -rf build
mkdir -p build/windows

find backend/src | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

cp -r etc/default-settings.json build/windows/settings.json
cp -r backend/requirements.txt build/windows
mkdir -p build/windows/backend
cp -r backend/src build/windows/backend/src
# use rm -v
rm build/windows/backend/src/create_dataset.py
cp -r backend/assets build/windows/backend/assets

cd frontend && npm run build
cd ..

cp -r frontend/public build/windows/frontend

mkdir build/windows/resources
mkdir build/windows/resources/video
mkdir build/windows/resources/music

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
