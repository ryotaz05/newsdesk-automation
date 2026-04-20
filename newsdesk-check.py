#!/usr/bin/env python3
"""
NewsDesk 複数日確認スクリプト
前回確認日から本日までの全てのデータを確認表示
"""

import json
import urllib.request
import os
from datetime import datetime, timedelta

SB_URL = 'https://tpxeepjrowcgqptqqxpa.supabase.co'
SB_KEY = 'sb_publishable_8u_TjqY5h456FwL3Us7lEA_sHCvB3Vj'

# 確認履歴ファイル
HISTORY_FILE = os.path.expanduser('~/.newsdesk_check_history.json')

def log(msg, level='info'):
    """ログ出力"""
    now = datetime.now().strftime('%H:%M:%S')
    prefix = {'info': 'ℹ ', 'ok': '✓ ', 'warn': '⚠ ', 'err': '✗ '}
    print(f'[{now}] {prefix.get(level, "")}{msg}')

def get_last_check_date():
    """前回確認日を取得"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
                return history.get('last_check_date', None)
        except:
            pass
    return None

def save_check_date(date_str):
    """確認日を保存"""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump({'last_check_date': date_str}, f)
    except Exception as e:
        log(f'履歴ファイル保存失敗: {e}', 'err')

def get_articles(date_from, date_to):
    """指定期間の記事を取得"""
    url = f"{SB_URL}/rest/v1/articles?select=id,title,source_id,region,published_at,original_source,created_at,info_type&published_at.gte.{date_from}&published_at.lt.{date_to}&order=published_at.desc&limit=1000"

    req = urllib.request.Request(
        url,
        headers={
            'apikey': SB_KEY,
            'Authorization': f'Bearer {SB_KEY}',
            'Accept': 'application/json'
        }
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        log(f'データ取得失敗: {e}', 'err')
        return []

def main():
    today = datetime.now().date().isoformat()
    last_check = get_last_check_date()

    # 確認期間を決定
    if last_check:
        date_from = last_check
        days_since = (datetime.fromisoformat(today) - datetime.fromisoformat(last_check)).days
        if days_since == 0:
            log('本日既に確認済みです', 'warn')
            return
    else:
        # 初回実行時は過去7日間
        date_from = (datetime.fromisoformat(today) - timedelta(days=7)).date().isoformat()
        days_since = 7

    date_to_next = (datetime.fromisoformat(today) + timedelta(days=1)).date().isoformat()

    log('===== NewsDesk 複数日確認開始 =====', 'info')
    log(f'確認期間: {date_from} ～ {today} ({days_since}日分)', 'info')
    print()

    # 記事取得
    articles = get_articles(date_from, date_to_next)

    if not articles:
        log('該当記事なし', 'warn')
        return

    log(f'取得記事数: {len(articles)}件', 'ok')
    print()

    # ===== 日別集計 =====
    print('=' * 80)
    print('📅 日別統計')
    print('=' * 80)
    print()

    by_date = {}
    for article in articles:
        date = article.get('published_at', 'N/A')[:10]
        by_date[date] = by_date.get(date, 0) + 1

    for date in sorted(by_date.keys(), reverse=True):
        count = by_date[date]
        bar = '▓' * min(count // 10, 40)
        print(f'  {date}  {count:3}件  {bar}')

    print()

    # ===== 地域別集計 =====
    print('=' * 80)
    print('🗺️ 地域別統計')
    print('=' * 80)
    print()

    by_region = {}
    for article in articles:
        region = article.get('region', '不明')
        by_region[region] = by_region.get(region, 0) + 1

    sorted_regions = sorted(by_region.items(), key=lambda x: x[1], reverse=True)

    total = sum(v for k, v in sorted_regions)
    for region, count in sorted_regions[:15]:
        pct = (count / total * 100) if total > 0 else 0
        bar = '▓' * min(count // 5, 30)
        print(f'  {region:15} {count:3}件  {pct:5.1f}%  {bar}')

    if len(sorted_regions) > 15:
        other_count = sum(v for k, v in sorted_regions[15:])
        print(f'  {f"その他({len(sorted_regions)-15})":15} {other_count:3}件')

    print()

    # ===== 情報種別 =====
    print('=' * 80)
    print('📰 情報種別')
    print('=' * 80)
    print()

    by_type = {}
    for article in articles:
        info_type = article.get('info_type', '不明')
        by_type[info_type] = by_type.get(info_type, 0) + 1

    for info_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        print(f'  {info_type:20} {count:3}件')

    print()

    # ===== 配信元別 =====
    print('=' * 80)
    print('📡 配信元別（上位10）')
    print('=' * 80)
    print()

    by_source = {}
    for article in articles:
        source = article.get('original_source', '不明')
        by_source[source] = by_source.get(source, 0) + 1

    sorted_sources = sorted(by_source.items(), key=lambda x: x[1], reverse=True)
    for source, count in sorted_sources[:10]:
        source_name = source if source else '（未分類）'
        bar = '▓' * min(count // 5, 25)
        print(f'  {source_name:25} {count:3}件  {bar}')

    print()

    # ===== サマリー =====
    print('=' * 80)
    print('📊 確認サマリー')
    print('=' * 80)
    print()
    print(f'  確認期間: {date_from} ～ {today}')
    print(f'  対象日数: {days_since}日')
    print(f'  合計記事数: {len(articles)}件')
    print(f'  地域数: {len(by_region)}地域')
    print(f'  配信元数: {len(by_source)}社')
    print()

    # 次回確認日を保存
    save_check_date(today)
    log('確認日を記録しました', 'ok')
    log('===== 確認完了 =====', 'info')

if __name__ == '__main__':
    main()
