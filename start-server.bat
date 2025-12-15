@echo off
cd /d "%~dp0"

echo.
echo ==============================================
echo バイク安全運転支援アプリ - サーバー起動
echo ==============================================
echo.

REM Pythonが利用可能か確認
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo HTTPサーバーを起動しています...
    echo.
    python server-http.py
    exit /b
)

REM Pythonが見つからない場合
echo.
echo エラー: Pythonが見つかりません
echo.
echo Pythonをインストールしてください:
echo https://www.python.org/downloads/
echo.
pause
