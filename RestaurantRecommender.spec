# RestaurantRecommender.spec
#
# PyInstaller build recipe for the Restaurant Recommender.
#
# Build with:   pyinstaller RestaurantRecommender.spec
#
# The three data entries below copy the read-only files into the executable.
# Each entry is (source on this machine, folder name inside the bundle), so
# paths.resource_path("templates/index.html") resolves correctly at run time.
#
# ---------------------------------------------------------------------------
# AI acknowledgement: this build file was written with assistance from Claude
# (Anthropic) on 2026-10-13, then read, tested and adapted by me. The assessed
# algorithms in ranking.py, course_generator.py, filters.py, database.py and
# validation.py are my own work.
# [Replace with the exact wording your school requires.]
# ---------------------------------------------------------------------------

from PyInstaller.utils.hooks import collect_all

# pywebview loads the native window library (WebView2 on Windows) at run time,
# so PyInstaller cannot see it by following imports. collect_all gathers those
# files explicitly; without this the program builds but no window appears.
webview_datas, webview_binaries, webview_hidden = collect_all('webview')

block_cipher = None

a = Analysis(
    ['desktop.py'],
    pathex=[],
    binaries=webview_binaries,
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('restaurants_north_vietnam.csv', '.'),
    ] + webview_datas,
    hiddenimports=[
        'auth',
        'budget',
        'course_generator',
        'database',
        'filters',
        'paths',
        'ranking',
        'restaurant',
        'validation',
    ] + webview_hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'pytest'],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='RestaurantRecommender',
    debug=False,
    strip=False,
    upx=False,
    console=False,          # no black command window behind the app
    disable_windowed_traceback=False,
)
