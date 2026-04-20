#!/bin/bash
# ===== NewsDesk 起動スクリプト =====
# このファイルをダブルクリックすると自動で起動します

# NewsDesk.htmlの場所（このファイルと同じフォルダ）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HTML_FILE="$SCRIPT_DIR/NewsDesk.html"

# HTMLファイルの存在確認
if [ ! -f "$HTML_FILE" ]; then
  osascript -e 'display alert "エラー" message "NewsDesk.html が同じフォルダに見つかりません。\nNewsDesk.html と NewsDesk起動.command を同じフォルダに置いてください。"'
  exit 1
fi

# ポート8080が使用中なら終了
lsof -ti:8080 | xargs kill -9 2>/dev/null

# ブラウザで開く（少し待ってから）
sleep 0.8
open "http://localhost:8080/NewsDesk.html"

# Pythonサーバー起動
echo "============================="
echo "  中山間地域 NewsDesk 起動中"
echo "============================="
echo ""
echo "  URL: http://localhost:8080/NewsDesk.html"
echo ""
echo "  終了するにはこのウィンドウを閉じてください"
echo "============================="
cd "$SCRIPT_DIR"
python3 -m http.server 8080
