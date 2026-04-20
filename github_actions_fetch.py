import json
import os
from datetime import datetime
import requests

# テスト用ダミー記事データ
test_articles = [
    {
        "source": "test",
        "title": "GitHub Actions テスト記事 1",
        "url": "https://example.com/article1",
        "snippet": "これはテスト用のダミー記事です。",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "category": "テスト",
        "tags": ["テスト", "自動化"],
        "original_source": "GitHub Actions Test"
    }
]

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

print(f"✓ テスト記事を生成: {len(test_articles)}件")

for article in test_articles:
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/articles",
            json=article,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
        )
        print(f"✓ 登録: {article['title']}")
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
