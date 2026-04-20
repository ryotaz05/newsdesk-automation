# GitHub Actions で NewsDesk を自動化

## 📋 セットアップ手順（5分で完了）

### 1️⃣ GitHub リポジトリを作成

```bash
# リポジトリ名: newsdesk-automation
# 説明: NewsDesk メール自動取得・記事登録システム
# 公開/非公開: 非公開（推奨）
```

**GitHub Web UI で作成:**
1. https://github.com/new にアクセス
2. Repository name: `newsdesk-automation`
3. Description: `NewsDesk automated mail import system`
4. Private をチェック
5. Create repository

---

### 2️⃣ ローカルリポジトリを初期化

```bash
cd /Users/ryotaz05/Library/CloudStorage/Dropbox/デスクトップ/0_知識/Claude/NewsDesk

# Git 初期化
git init
git add .
git commit -m "Initial commit: NewsDesk automation system"

# リモートリポジトリを追加
git remote add origin https://github.com/YOUR_USERNAME/newsdesk-automation.git
git branch -M main
git push -u origin main
```

---

### 3️⃣ GitHub Secrets を設定

**リポジトリ設定 > Secrets and variables > Actions から以下を追加:**

```
SUPABASE_URL
  値: https://tpxeepjrowcgqptqqxpa.supabase.co

SUPABASE_KEY
  値: sb_publishable_8u_TjqY5h456FwL3Us7lEA_sHCvB3Vj

ANTHROPIC_API_KEY（Phase 3用）
  値: sk-...（Anthropic APIキー）
```

**設定方法:**
```
GitHub リポジトリ
  ↓
Settings
  ↓
Secrets and variables
  ↓
Actions
  ↓
New repository secret
```

---

### 4️⃣ ワークフロー確認

```
GitHub リポジトリ
  ↓
Actions タブ
  ↓
NewsDesk Daily Automation が表示される
  ↓
「Run workflow」で手動実行可能
```

---

## ⏰ 実行スケジュール

```
毎日 8:30 AM JST に自動実行
  ↓
UTC 23:30（前日）に実行
  ↓
GitHub Actions ログに結果が記録される
```

**手動実行も可能:**
```
GitHub > Actions > NewsDesk Daily Automation
  ↓
「Run workflow」ボタン
```

---

## 📊 実行フロー（GitHub Actions版）

```
1️⃣ メール取得・記事抽出
   Python + Claude API で実行
   （スキルの代わりに API 直接呼び出し）
   
2️⃣ 記事登録
   newsdesk-fetch.py で Supabase に INSERT
   
3️⃣ 統計確認
   newsdesk-check.py で自動集計
   
4️⃣ ログ保存
   実行結果を GitHub Artifacts に保存
```

---

## ✅ 動作確認

### 初回テスト（手動実行）

```
GitHub Actions > NewsDesk Daily Automation
  ↓
「Run workflow」をクリック
  ↓
2-3分後に実行完了
  ↓
✅ で成功を確認
```

### ログ確認

```
GitHub Actions > 実行結果
  ↓
「newsdesk-update」ジョブをクリック
  ↓
各ステップのログを確認
```

### Artifacts 確認

```
GitHub Actions > 実行結果
  ↓
「Artifacts」セクション
  ↓
「newsdesk-logs」をダウンロード
  ↓
fetch_output.json と履歴ファイルを確認
```

---

## 🚨 トラブルシューティング

### ❌ 実行失敗（エラー）

**原因1: Secrets が設定されていない**
```
Settings > Secrets and variables > Actions
で以下を確認：
  ✓ SUPABASE_URL
  ✓ SUPABASE_KEY
  ✓ ANTHROPIC_API_KEY
```

**原因2: リポジトリへのアクセス権限**
```
Settings > Actions > General
  ↓
「Workflow permissions」
  ↓
「Read and write permissions」に変更
```

**原因3: Python パッケージ不足**
```
workflow ファイルで pip install を確認：
  pip install anthropic
```

---

## 📈 メリット

```
✅ PC の電源状態に関わらず動作
✅ クラウド上で常時稼働
✅ 毎日確実に 8:30 AM に実行
✅ GitHub で実行ログが保存される
✅ 無料で利用可能（GitHub Actions）
✅ 実行結果を確認・ダウンロード可能
```

---

## 📝 注意事項

- **初回実行時** は手動テストを推奨
- **ログはGitHub上に7日間保持**（Artifacts 設定による）
- **Secrets は絶対にコミットしない**（GitHub が自動防止）
- **リポジトリを非公開に設定**（セキュリティ）

---

## 🎯 さらなる改善（オプション）

### Slack 通知を追加

```yaml
- name: Slack通知（成功時）
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "📊 NewsDesk 日次更新が完了しました"
      }
```

### メール通知を追加

```yaml
- name: メール通知
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
```

---

**セットアップ完了で、完全な自動化が実現します！** 🎉

