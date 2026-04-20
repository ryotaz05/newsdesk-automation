#!/bin/bash
# ===== NewsDesk メール取り込み実行スクリプト =====
# 使用方法：
#   1. Claude Code で /newsdesk-fetch を実行
#   2. JSONが出力されたら、このスクリプトにコピー＆ペーストするか、
#      以下のコマンドで実行：
#      /newsdesk-fetch | python3 newsdesk-fetch.py

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/newsdesk-fetch.py"

# Pythonスクリプトの存在確認
if [ ! -f "$PYTHON_SCRIPT" ]; then
  osascript -e 'display alert "エラー" message "newsdesk-fetch.py が同じフォルダに見つかりません。"'
  exit 1
fi

# 実行
echo "============================="
echo "  NewsDesk メール取り込み実行"
echo "============================="
echo ""
echo "使用方法："
echo "  /newsdesk-fetch | python3 newsdesk-fetch.py"
echo ""
echo "または Claude Code で以下を実行："
echo "  /newsdesk-fetch"
echo "============================="
echo ""

# stdin から入力を受け取る場合
python3 "$PYTHON_SCRIPT"

RESULT=$?

if [ $RESULT -eq 0 ]; then
  echo ""
  echo "✓ 完了。ウィンドウを閉じてください"
  sleep 3
else
  echo ""
  echo "✗ エラーが発生しました（終了コード: $RESULT）"
  sleep 5
fi
