# NewsDesk 引き継ぎメモ
作成日：2026年4月11日  
作成元：Claude Chat（claude.ai）  
引き継ぎ先：Claude Code

---

## 1. プロジェクト概要

中山間地域・農山村に関するニュースをGmailから自動収集し、Supabaseに蓄積・閲覧するシステム。

**構成：**
```
Gmail（3ソース＋新規メルマガ）
  ↓ Claude Chat で取り込み・AI解析
Supabase（NewsDesk プロジェクト）
  ↓ REST API
NewsDesk.html（閲覧・取り込みUI）
  http://localhost:8080 で起動
```

---

## 2. ファイルパス

| ファイル | パス |
|---|---|
| **メインHTML** | `/Users/ryotaz05/Library/CloudStorage/Dropbox/デスクトップ/0_知識/Claude/NewsDesk/NewsDesk.html` |
| **起動スクリプト** | `/Users/ryotaz05/Library/CloudStorage/Dropbox/デスクトップ/0_知識/Claude/NewsDesk/NewsDesk起動.command` |

**起動方法：**
```bash
# NewsDesk起動.command をダブルクリック、または
cd ~/Library/CloudStorage/Dropbox/デスクトップ/0_知識/Claude/NewsDesk
python3 -m http.server 8080
# → http://localhost:8080/NewsDesk.html をブラウザで開く
```

---

## 3. Supabase接続情報

| 項目 | 値 |
|---|---|
| プロジェクト名 | NewsDesk |
| プロジェクトID | `tpxeepjrowcgqptqqxpa` |
| API URL | `https://tpxeepjrowcgqptqqxpa.supabase.co` |
| Publishable Key | `sb_publishable_8u_TjqY5h456FwL3Us7lEA_sHCvB3Vj` |
| リージョン | ap-southeast-1 |

---

## 4. DBテーブル構成

### 主要テーブル

```
articles          -- 記事本体（132件・2026/4/1〜）
sources           -- 情報源（20件）
tags              -- タグ（15件）
article_tags      -- 記事↔タグ中間テーブル（271件）
alert_keyword_sets -- Googleアラートキーワードセット（6件）
raw_emails        -- 生メール保管（未使用）
```

### articles テーブルの主要カラム

| カラム | 内容 |
|---|---|
| title | 記事タイトル |
| source_id | sources.id への外部キー |
| source_url | 元記事URL |
| info_type | news/policy/report/event/other |
| region | 対象地域（都道府県名 or 全国） |
| published_at | 記事の日付 |
| mail_date | メール配信日 |
| topic_category | 47行政ジャーナルのトピック分類 |
| ijamp_keyword | iJAMPのキーワード |
| alert_keyword | Googleアラートのキーワード |
| keyword_set_id | alert_keyword_sets.id |
| original_source | 元メディア名（朝日新聞等） |
| importance | 重要度 1〜5 |
| external_id | 重複防止用ユニークID |

### RLSポリシー
全テーブルに anon ユーザーの SELECT/INSERT を許可済み。

---

## 5. 情報ソース一覧（sources テーブル）

### 稼働中（Gmail配信確認済み）

| ID | ソース名 | 送信元アドレス | 備考 |
|---|---|---|---|
| 8 | 47行政ジャーナル | mytopics@47gyosei.jp | 毎朝8時 |
| 9 | iJAMP（時事通信社） | news@ijamp.jiji.com | 毎朝6時 |
| 10 | Googleアラート | googlealerts-noreply@google.com | 毎朝 |
| 11 | 広島県地域力創造課 | noreply@team500.sakura.ne.jp | 不定期 |
| 12 | G空間情報センター | info@geospatial.jp | 不定期 |
| 13 | 九経調ニュースレター | qnews@kerc.or.jp | 毎日（地域交通・過疎関連のみ取り込み） |

### 配信待ち（登録済み・実際の配信アドレス未確認）

| ID | ソース名 | 登録完了アドレス | 実配信アドレス |
|---|---|---|---|
| 14 | 農林水産省メルマガ | maff_mg@maff.go.jp | 要確認 |
| 15 | JOIN移住・交流ナビ | info@iju-koryu.jp | 要確認 |
| 16 | TURNS（ターンズ） | info@turns.jp | 要確認 |
| 18 | ふるさと回帰支援センター | mail-mag@furusatokaiki.net | 要確認 |
| 19 | 地域活性化センター（JCRD） | kouhou@jcrd.jp | 要確認 |
| 20 | 日本農業新聞メルマガ | mail_magazine@agrinews.co.jp | 定期配信待ち。号外は取り込まない |

---

## 6. NewsDesk.html の構成

### タブ構成
- **📰 閲覧・検索タブ**：Supabaseから記事を取得・表示
  - 検索・フィルター（ソース/地域/種別/重要度/メディア/タグ）
  - リスト表示 / カード表示切り替え
  - ページネーション（30件/ページ）
  - 起動時自動更新・↻更新ボタン
- **📥 メール取り込みタブ**：Gmail MCP経由でメールを解析・DB登録
  - Claude API + Gmail MCP でメール解析
  - チェックボックスで選別後にSupabaseへ一括登録

### HTML内の重要定数

```javascript
const SB_URL = 'https://tpxeepjrowcgqptqqxpa.supabase.co';
const SB_KEY = 'sb_publishable_8u_TjqY5h456FwL3Us7lEA_sHCvB3Vj';
const SOURCE_IDS = {
  '47': 8, 'ijamp': 9, 'google': 10, 'hiroshima': 11,
  'geospatial': 12, 'kyukeityo': 13, 'maff': 14,
  'turns': 16, 'furusato': 18, 'jcrd': 19, 'other': 5
};
```

---

## 7. 毎朝の運用手順

```
① NewsDesk起動.command をダブルクリック
② http://localhost:8080/NewsDesk.html が自動で開く
   → 起動時に自動でSupabaseから最新データを取得・表示
③ Claude Chat で「今日のメールを取り込んでください」と指示
   → Gmail MCP でメール取得 → SQL INSERT
④ NewsDeskの ↻ 更新ボタンをクリック → 最新記事が表示
```

---

## 8. Claude Code で引き継ぐべき作業

### 優先度高
- [ ] 配信待ちソース（農水省・TURNS・JOIN等）の実配信アドレス確認・更新
- [ ] 毎朝の取り込みをより自動化（スクリプト化）
- [ ] 日本農業新聞の定期配信開始時の取り込み対応

### 優先度中
- [ ] タグ自動付与ロジックの精度向上
- [ ] 取り込みUIをClaude Chatから独立させる（Gmail MCPをClaude Desktop経由で呼び出す）
- [ ] original_sourceのドメインマッピング追加（新メディア対応）

### 優先度低
- [ ] n8nによる完全自動化（Gmail監視→Supabase自動登録）
- [ ] GitHubによるHTMLのバージョン管理

---

## 9. Googleアラートの設定キーワード（6セット）

| ID | キーワード |
|---|---|
| 1 | 関係人口 OR 他出子 OR 二地域居住 OR 定住未満関係人口 |
| 2 | 人口減少 OR 地域づくり OR 農村振興 |
| 3 | 地区防災計画 OR 自主防災 OR 生活支援 OR 移動支援 |
| 4 | 小さな拠点 OR 地域運営組織 OR 集落支援員 |
| 5 | 過疎 OR 限界集落 OR 小規模集落 OR 中山間地域 |
| 6 | 総務省 AND 地域 |

---

## 10. 参考：ドメイン→メディア名マッピング（主要）

```
asahi.com → 朝日新聞
nhk.or.jp → NHK
yomiuri.co.jp → 読売新聞
mainichi.jp → 毎日新聞
nikkei.com → 日本経済新聞
agrinews.co.jp → 日本農業新聞
chugoku-np.co.jp → 中国新聞
sanyonews.jp → 山陽新聞
nishinippon.co.jp → 西日本新聞
kobe-np.co.jp → 神戸新聞
fnn.jp → FNNプライム
yahoo.co.jp → Yahoo!ニュース
prtimes.jp → PRTimes
soumu.go.jp → 総務省
maff.go.jp → 農林水産省
pref.shimane → 島根県
pref.tottori → 鳥取県
pref.hiroshima → 広島県
47gyosei.jp → 47行政ジャーナル
ijamp.jiji.com → iJAMP（時事通信）
turns.jp → TURNS
furusatokaiki.net → ふるさと回帰支援センター
jcrd.jp → 地域活性化センター
```
