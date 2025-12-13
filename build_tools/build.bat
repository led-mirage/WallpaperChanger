@echo off
setlocal

cd /d %~dp0..

pyivf-make_version ^
    --source-format yaml ^
    --metadata-source build_tools/version.yaml ^
    --outfile build_tools/version.txt

pyinstaller ^
    --clean ^
    --onefile ^
    --version-file=build_tools/version.txt ^
    -n WallpaperChanger ^
    src/main.py
