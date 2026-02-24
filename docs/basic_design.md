# 基本設計書：AIニュース自動収集・配信システム

## 1. システムアーキテクチャ
* **バッチ処理（実行基盤）**: GitHub Actions
* **バックエンド言語**: Python 3.x
* **AIモデル**: Gemini API（例：Gemini 2.0 Flash等）
* **データベース**: Supabase（PostgreSQL）
* **通知基盤**: Discord Webhook

## 2. 処理フロー
1. **トリガー実行**: GitHub Actionsのスケジューラが毎日指定時間（例：朝8時）に起動する。（手動実行も可能）
2. **記事収集**:
   - Google News RSS や GNews API といった汎用的なニュース配信元から、「AI」「ChatGPT」「Claude」「Gemini」などのキーワードを含む最新記事リスト（タイトル、URL、公開日等）を取得する。
3. **重複（既読）チェック**:
   - 取得したURLリストを元にSupabaseのテーブルを参照し、既に保存（配信）済みの記事を除外する。
4. **重要度スコアリングと要約（Gemini API）**:
   - 未処理の記事情報をGemini APIに送信し、プロンプトで以下の判定およびスコアリングを指示する：
     - **優先度高**: Claude, Gemini, ChatGPT などの主要AIのアップデート・リリース情報
     - **優先度中**: 無料で使える新しいAIツールやサービスに関する情報
   - 上位のスコアを持つ **3記事** を厳選する。
   - 選ばれた3記事について、日本語で要点をおさえた分かりやすい要約文を生成させる。
5. **データ保存**: 
   - 厳選した3記事のデータ（タイトル、URL、要約内容、公開日時など）をSupabaseにINSERTし、次回以降の重複を回避する。
6. **Discord通知**: 
   - 今回選ばれた3件の記事情報を、Discordリッチメッセージ（Embeds）のフォーマットに整える。
   - Discord WebhookへPOSTリクエストを送信してチャンネルに配信する。
7. **プロセスの終了**: エラーハンドリングとログ出力を終え、プロセスを終了する。

## 3. データベース設計 (Supabase)
### テーブル名: `ai_news_articles`

| カラム名 | データ型 | 制約 | 説明 |
| :--- | :--- | :--- | :--- |
| `id` | uuid | Primary Key, Default: `uuid_generate_v4()` | レコードの一意識別子 |
| `url` | text | Unique, Not Null | 記事のURL（重複判定用） |
| `title` | text | Not Null | 記事のタイトル |
| `summary` | text | | Geminiが生成した要約文 |
| `published_at` | timestamptz | | 記事の公開日時 |
| `created_at` | timestamptz | Default: `now()` | データベースへの保存日時 |

## 4. 外部連携・ライブラリ設計
* **Python パッケージ**:
  * `requests`: 各種API（ニュース元、Gemini API、Discord Webhook）への通信。
  * `feedparser`: RSSフィードを利用する場合のパース処理用。
  * `supabase`: Supabase Python Client。
  * `google-generativeai`: Gemini API 公式ライブラリ。
* **Gemini API**:
  * プロンプト設計で、「指定したAI(Claude, Gemini, ChatGPT)のリリース情報」「新しい無料AIツール」を重み付けしてスコアリング＆Top 3の選出を行わせる。
* **Discord Webhook**:
  * 毎日3件のフォーマット済みメッセージを送信。見やすいUIでの送信を行う。

## 5. GitHub Actions 設定
* **ワークフローファイル**: `.github/workflows/daily_news_bot.yml`
* **トリガー**:
  * `on: schedule` (例： `cron: '0 23 * * *'` ※UTC 23:00 = JST 8:00)
  * `on: workflow_dispatch` (手動実行・テスト用)
* **環境変数（GitHub Secrets）**:
  * `GEMINI_API_KEY`: Gemini APIの認証キー
  * `SUPABASE_URL`: SupabaseプロジェクトのURL
  * `SUPABASE_SERVICE_KEY`: Supabase連携用のサービスキー（DB操作権限）
  * `DISCORD_WEBHOOK_URL`: Discordの通知先Webhook URL
