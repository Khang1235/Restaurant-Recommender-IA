@echo off
REM ---------------------------------------------------------------------------
REM build_windows.bat
REM
REM Builds RestaurantRecommender.exe from this folder.
REM Double-click this file, or run it from Command Prompt inside this folder.
REM
REM The finished program appears in the dist folder as:
REM     dist\RestaurantRecommender.exe
REM ---------------------------------------------------------------------------

echo Installing build requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo.
echo Building the executable. This takes a few minutes.
python -m PyInstaller --noconfirm --clean RestaurantRecommender.spec

echo.
if exist dist\RestaurantRecommender.exe (
    echo Done. The program is at dist\RestaurantRecommender.exe
) else (
    echo Build did not produce an executable. Read the messages above for the reason.
)
pause
