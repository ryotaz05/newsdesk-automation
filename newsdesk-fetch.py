#!/usr/bin/env python3
"""
NewsDesk メール取り込み自動化スクリプト
- Claude Code スキル /newsdesk-fetch から JSON を stdin で受け取る
- 記事を Supabase に INSERT（重複チェック含む）
- トークン削減：スキルは Haiku で記事抽出を完了
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import base64

# 環境変数から Supabase 認証情報を取得
SB_URL = 'https://tpxeepjrowcgqptqqxpa.supabase.co'
SB_KEY = 'sb_publishable_8u_TjqY5h456FwL3Us7lEA_sHCvB3Vj'

# 差分取得用の履歴ファイル
FETCH_HISTORY_FILE = os.path.expanduser('~/.newsdesk_fetch_history.json')

# ===== 差分取得機能 =====

def get_last_fetch_date() -> str:
    """前回のフェッチ日付を取得"""
    if os.path.exists(FETCH_HISTORY_FILE):
        try:
            with open(FETCH_HISTORY_FILE, 'r') as f:
                history = json.load(f)
                return history.get('last_fetch_date')
        except:
            pass
    return None

def save_fetch_date(date_str: str):
    """フェッチ日付を保存"""
    try:
        with open(FETCH_HISTORY_FILE, 'w') as f:
            json.dump({'last_fetch_date': date_str}, f)
    except Exception as e:
        log(f'履歴ファイル保存失敗: {e}', 'warn')

def get_gmail_query_params() -> dict:
    """
    Gmail取得用のクエリパラメータを生成
    差分取得: 前回フェッチ日から本日までのメールのみ
    """
    last_date = get_last_fetch_date()
    today = datetime.now().date().isoformat()

    if last_date:
        # 前回フェッチ日以降のメールのみ
        return {
            'after': last_date,
            'before': today
        }
    else:
        # 初回は過去3日分
        three_days_ago = (datetime.now() - timedelta(days=3)).date().isoformat()
        return {
            'after': three_days_ago,
            'before': today
        }

# ===== ヘルパー関数 =====

def log(msg, level='info'):
    """ログ出力"""
    now = datetime.now().strftime('%H:%M:%S')
    prefix = {'info': 'ℹ ', 'ok': '✓ ', 'warn': '⚠ ', 'err': '✗ '}
    print(f'[{now}] {prefix.get(level, "")}{msg}')

def gen_external_id(url: str) -> str:
    """URLベースの重複チェック用ID生成"""
    if not url:
        return None
    try:
        encoded = base64.b64encode(url.encode()).decode().replace('+', '').replace('/', '').replace('=', '')
        return encoded[:80]
    except:
        return None

def extract_domain(url: str) -> str:
    """URLからドメインを抽出"""
    if not url:
        return None
    try:
        parsed = urlparse(url)
        return parsed.netloc or None
    except:
        return None

def guess_region(text: str) -> str:
    """テキストから地域を推定"""
    regions = {
        '北海道': ['北海道'],
        '青森': ['青森県', '青森'],
        '岩手': ['岩手県', '岩手'],
        '宮城': ['宮城県', '宮城'],
        '秋田': ['秋田県', '秋田'],
        '山形': ['山形県', '山形'],
        '福島': ['福島県', '福島'],
        '茨城': ['茨城県', '茨城'],
        '栃木': ['栃木県', '栃木'],
        '群馬': ['群馬県', '群馬'],
        '埼玉': ['埼玉県', '埼玉'],
        '千葉': ['千葉県', '千葉'],
        '東京': ['東京都', '東京'],
        '神奈川': ['神奈川県', '神奈川'],
        '新潟': ['新潟県', '新潟'],
        '富山': ['富山県', '富山'],
        '石川': ['石川県', '石川'],
        '福井': ['福井県', '福井'],
        '山梨': ['山梨県', '山梨'],
        '長野': ['長野県', '長野'],
        '岐阜': ['岐阜県', '岐阜'],
        '静岡': ['静岡県', '静岡'],
        '愛知': ['愛知県', '愛知'],
        '三重': ['三重県', '三重'],
        '滋賀': ['滋賀県', '滋賀'],
        '京都': ['京都府', '京都'],
        '大阪': ['大阪府', '大阪'],
        '兵庫': ['兵庫県', '兵庫'],
        '奈良': ['奈良県', '奈良'],
        '和歌山': ['和歌山県', '和歌山'],
        '鳥取': ['鳥取県', '鳥取'],
        '島根': ['島根県', '島根'],
        '岡山': ['岡山県', '岡山'],
        '広島': ['広島県', '広島'],
        '山口': ['山口県', '山口'],
        '徳島': ['徳島県', '徳島'],
        '香川': ['香川県', '香川'],
        '愛媛': ['愛媛県', '愛媛'],
        '高知': ['高知県', '高知'],
        '福岡': ['福岡県', '福岡'],
        '佐賀': ['佐賀県', '佐賀'],
        '長崎': ['長崎県', '長崎'],
        '熊本': ['熊本県', '熊本'],
        '大分': ['大分県', '大分'],
        '宮崎': ['宮崎県', '宮崎'],
        '鹿児島': ['鹿児島県', '鹿児島'],
        '沖縄': ['沖縄県', '沖縄'],
    }

    for region, keywords in regions.items():
        for kw in keywords:
            if kw in text:
                return region
    return '全国'

def domain_to_source(domain: str) -> str:
    """ドメイン→メディア名マッピング"""
    mapping = {
        'asahi.com': '朝日新聞',
        'nhk.or.jp': 'NHK',
        'yomiuri.co.jp': '読売新聞',
        'mainichi.jp': '毎日新聞',
        'nikkei.com': '日本経済新聞',
        'agrinews.co.jp': '日本農業新聞',
        'chugoku-np.co.jp': '中国新聞',
        'sanyonews.jp': '山陽新聞',
        'nishinippon.co.jp': '西日本新聞',
        'kobe-np.co.jp': '神戸新聞',
        'kahoku.com': '河北新報',
        'yamagata-np.jp': '山形新聞',
        'hokkaido-np.co.jp': '北海道新聞',
        'fnn.jp': 'FNNプライム',
        'yahoo.co.jp': 'Yahoo!ニュース',
        'prtimes.jp': 'PRTimes',
        'travelvoice.jp': 'トラベルボイス',
        'nankainn.com': '南海日日新聞',
        'minamishinshu.jp': '南信州新聞',
        'soumu.go.jp': '総務省',
        'maff.go.jp': '農林水産省',
        'chunichi.co.jp': '中日新聞',
        '47gyosei.jp': '47行政ジャーナル',
        'ijamp.jiji.com': 'iJAMP（時事通信）',
        'turns.jp': 'TURNS',
        'furusatokaiki.net': 'ふるさと回帰支援センター',
        'jcrd.jp': '地域活性化センター',
    }

    if not domain:
        return 'その他'

    for dm, label in mapping.items():
        if dm in domain.lower():
            return label
    return domain

def decode_google_alert_url(redirect_url: str) -> str:
    """GoogleアラートのリダイレクトURLから実URLを抽出"""
    try:
        parsed = parse_qs(urlparse(redirect_url).query)
        if 'url' in parsed:
            return parsed['url'][0]
    except:
        pass
    return redirect_url

# ===== 47行政ジャーナル テンプレートパーサー =====

def parse_47gyosei_email(email_body: str) -> list:
    """
    47行政ジャーナルのメール本文から記事を抽出
    プレーンテキスト形式のメールを正規表現で解析
    """
    articles = []

    if not email_body:
        return articles

    # セクション分割
    lines = email_body.split('\n')

    current_category = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # カテゴリ行を検出
        category_match = re.match(r'^◆(.+?)\s+\((\d+)件\)$', line)
        if category_match:
            current_category = category_match.group(1)
            i += 1
            continue

        # 「新着記事はありません」をスキップ
        if '新着記事はありません' in line:
            i += 1
            continue

        # 記事タイトル行を検出 [MM/DD HH:MM] Title
        title_match = re.match(r'^\[(\d{2}/\d{2}\s+\d{2}:\d{2})\]\s+(.+)$', line)
        if title_match and i + 1 < len(lines):
            pub_time = title_match.group(1)
            title = title_match.group(2)

            # 次の行がURLか確認
            next_line = lines[i + 1].strip()
            url_match = re.search(r'https://47gyosei\.jp/article/\?id=(\d+)', next_line)

            if url_match:
                url = next_line.split()[0]  # URLのみ抽出
                article_id = url_match.group(1)

                # 日付をYYYY-MM-DD形式に変換（メール送信日付からの推定）
                # メールは翌日朝に送信されるため、調整
                month, day = pub_time.split('/')[0], pub_time.split()[0]
                from datetime import datetime
                today = datetime.now()
                pub_date = f"{today.year:04d}-{month}-{day}"

                article = {
                    'source': '47',
                    'title': title.strip(),
                    'url': url,
                    'snippet': title.strip()[:100],  # タイトルがスニペット
                    'date': pub_date,
                    'category': '地域づくり',  # デフォルト（カテゴリ名をマップ可能）
                    'tags': [current_category] if current_category else ['47行政ジャーナル'],
                    'original_source': '47行政ジャーナル'
                }
                articles.append(article)
                i += 2
                continue

        i += 1

    return articles

def fetch_47gyosei_emails() -> list:
    """
    Gmail MCPで47行政ジャーナルのメールを取得し、記事抽出
    スキルを使わずPythonで直接抽出（トークン0）
    """
    import urllib.request

    articles = []

    # Gmail APIでメール検索
    try:
        # 昨日～今日のメールを取得
        from_addr = 'mytopics@47gyosei.jp'
        query = f'from:{from_addr} after:yesterday'

        # 注：実装ではGmail MCP経由で取得する必要があるが、
        # Python直接ではできないため、スキルと組み合わせるか
        # メールをテキストファイルで受け取る方法が必要

        # 現時点ではスキップ（Phase 2での実装予定）
        pass
    except Exception as e:
        log(f'47gyosei メール取得失敗: {e}', 'warn')

    return articles

# ===== Supabase REST API =====

def sb_get(path: str):
    """Supabase GET"""
    import urllib.request
    url = f'{SB_URL}/rest/v1/{path}'
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
        log(f'SB GET失敗 {path}: {e}', 'err')
        return []

def sb_post(table: str, data):
    """Supabase POST（単一 or 複数）"""
    import urllib.request
    url = f'{SB_URL}/rest/v1/{table}'
    body = json.dumps(data if isinstance(data, list) else [data])
    req = urllib.request.Request(
        url,
        data=body.encode(),
        headers={
            'apikey': SB_KEY,
            'Authorization': f'Bearer {SB_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        # 重複制約エラー（code 23505）をチェック
        try:
            error_json = json.loads(error_body)
            if error_json.get('code') == '23505':
                log(f'重複制約エラー（既に登録済み）: {table}', 'warn')
                return None  # 重複なので None を返す（スキップ扱い）
        except:
            pass
        log(f'SB POST失敗 {table}: {error_body[:100]}', 'err')
        return None
    except Exception as e:
        log(f'SB POST失敗 {table}: {e}', 'err')
        return None

# ===== メール取得・処理 =====

def read_articles_from_stdin() -> list:
    """
    スキル /newsdesk-fetch から JSON を stdin で受け取る
    スキルが既に記事抽出を完了しているため、ここは単に JSON をパースするのみ
    """
    articles = []
    log('スキルからの入力を受け取り中...', 'info')

    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            log('入力なし（スキルが実行されていない可能性）', 'warn')
            return []

        # JSONパース
        try:
            clean = input_data.replace('```json', '').replace('```', '').strip()
            match = re.search(r'\{[\s\S]*\}', clean)
            parsed = json.loads(match.group(0) if match else '{}')
            articles = parsed.get('articles', [])
            summary = parsed.get('summary', '')
            count = parsed.get('count', 0)

            log(f'取得完了: {count}件 — {summary}', 'ok' if articles else 'warn')
        except json.JSONDecodeError as e:
            log(f'JSON parse失敗: {str(e)[:80]}', 'warn')
            articles = []

    except EOFError:
        log('入力ストリームが閉じられました（スキル実行が必要）', 'warn')
    except Exception as e:
        log(f'入力読み込みエラー: {e}', 'err')

    return articles

def check_duplicates(external_ids: list) -> set:
    """Supabaseで既存の external_id をチェック（1件ずつ）"""
    if not external_ids:
        return set()

    existing_ids = set()
    for eid in external_ids:
        try:
            result = sb_get(f'articles?select=external_id&external_id.eq.{eid}')
            if result:
                existing_ids.add(result[0]['external_id'])
        except:
            # エラーでも続行
            pass
    return existing_ids

def register_articles(articles: list) -> dict:
    """
    取得した記事をSupabaseに登録
    重複チェック → 新規レコードのみINSERT
    """
    if not articles:
        log('登録対象なし', 'warn')
        return {'registered': 0, 'duplicates': 0, 'errors': 0}

    # 1. 重複チェック用IDを生成
    ext_ids = []
    for a in articles:
        ext_id = gen_external_id(a.get('url', ''))
        a['_external_id'] = ext_id
        if ext_id:
            ext_ids.append(ext_id)

    # 2. 既存レコードをチェック
    existing = check_duplicates(ext_ids)
    log(f'重複チェック: {len(existing)}件は既存', 'info')

    # 3. 新規レコードのみを抽出
    source_ids = {'47': 8, 'ijamp': 9, 'google': 10, 'hiroshima': 11, 'agri': 20}
    tag_rows = sb_get('tags?select=id,name')
    tag_map = {t['name']: t['id'] for t in (tag_rows or [])}

    to_register = []
    article_tags = []

    for a in articles:
        if a['_external_id'] in existing:
            log(f'⚠ 重複スキップ: {a["title"][:40]}...', 'warn')
            continue

        domain = extract_domain(a.get('url', ''))
        url = a.get('url', '')

        # Googleアラートの場合はURLをデコード
        if a['source'] == 'google' and 'google.com/url' in url:
            url = decode_google_alert_url(url)

        row = {
            'title': a['title'],
            'body': a.get('snippet', None),
            'source_id': source_ids.get(a['source'], 5),
            'source_url': url,
            'info_type': 'news',
            'region': guess_region(a['title'] + ' ' + a.get('snippet', '')),
            'published_at': a.get('date'),
            'alert_keyword': a.get('category'),
            'original_source': domain_to_source(domain) if domain else None,
            'external_id': a['_external_id'],
            'importance': 3
        }

        to_register.append(row)

        # タグリンク用に article_id プレースホルダー追加
        for tag_name in a.get('tags', []):
            if tag_name in tag_map:
                article_tags.append({'article_id': None, 'tag_id': tag_map[tag_name], '_title': a['title'], '_tag_name': tag_name})

    # 4. INSERT実行（1件ずつ重複制約エラーをハンドル）
    stats = {'registered': 0, 'duplicates': len(existing), 'errors': 0}

    if to_register:
        for article in to_register:
            try:
                inserted = sb_post('articles', article)
                if inserted:
                    stats['registered'] += 1
                    log(f'✓ 登録: {article["title"][:40]}', 'ok')

                    # タグリンク登録
                    if article_tags and isinstance(inserted, list) and len(inserted) > 0:
                        article_id = inserted[0]['id']
                        relevant_tags = [t for t in article_tags if t['_title'] == article['title']]
                        if relevant_tags:
                            tags_to_insert = [{'article_id': article_id, 'tag_id': t['tag_id']} for t in relevant_tags]
                            sb_post('article_tags', tags_to_insert)
                else:
                    # 重複制約エラー
                    stats['duplicates'] += 1
                    log(f'⚠ 重複スキップ: {article["title"][:40]}', 'warn')
            except Exception as e:
                stats['errors'] += 1
                log(f'✗ エラー: {article["title"][:40]} — {str(e)[:50]}', 'err')

    return stats

# ===== メイン処理 =====

def main():
    log('===== NewsDesk メール取り込み（Supabase登録） =====', 'info')

    # 差分取得の期間情報を表示
    query_params = get_gmail_query_params()
    if query_params.get('after'):
        log(f'差分取得期間: {query_params["after"]} ～ {query_params["before"]}', 'info')

    # 1. スキルからJSON入力を受け取る
    articles = read_articles_from_stdin()

    if not articles:
        log('登録対象なし（スキル /newsdesk-fetch を実行してください）', 'warn')
        log('使用例: /newsdesk-fetch', 'info')
        return

    log(f'受け取った記事数: {len(articles)}件', 'info')

    # 2. 記事登録
    stats = register_articles(articles)

    # 3. フェッチ日付を保存（差分取得用）
    today = datetime.now().date().isoformat()
    save_fetch_date(today)
    log(f'差分取得日付を記録: {today}', 'ok')

    # 4. サマリー
    log('===== 処理完了 =====', 'ok')
    log(f'登録: {stats["registered"]}件 / 重複: {stats["duplicates"]}件 / エラー: {stats["errors"]}件', 'info')

if __name__ == '__main__':
    main()
