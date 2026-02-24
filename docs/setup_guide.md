# AIニュース自動配信ボット - 動作確認・環境構築手順

本システムを稼働させるためのセットアップ手順です。

## 1. Supabaseの準備 (データベースの構築)
1. [Supabase](https://supabase.com/) にログインし、新しいプロジェクトを作成します。
2. 左メニューの **SQL Editor** を開き、以下のSQLを実行してテーブルを作成してください。

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE ai_news_articles (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    url text UNIQUE NOT NULL,
    title text NOT NULL,
    summary text,
    published_at timestamptz,
    created_at timestamptz DEFAULT now()
);
```

3. 左メニューの **Project Settings** > **API** から以下2つをメモします。
   - `Project URL`
   - `Project API Keys` の `service_role` (Secret)

## 2. APIキーの各種準備
- **Gemini API Key**: [Google AI Studio](https://aistudio.google.com/app/apikey) にて取得（無料）
- **Discord Webhook URL**: ニュースを配信したいDiscordのチャンネル設定 ＞ 連携サービス ＞ ウェブフック を作成し、「ウェブフックURLをコピー」をメモ。

## 3. ローカルでの動作テスト (任意)
開発PC (Mac等) で実際に1回動かしてみる手順です。

1. プロジェクトルート ( `/Users/yoshida/manabi/src/AINFO` 等 ) でターミナルを開き、コマンドを実行します。
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. 同じ階層に `.env` ファイルを新規作成し、以下を記述します。
```env
GEMINI_API_KEY="取得したGemini APIキー"
SUPABASE_URL="取得したSupabaseのURL"
SUPABASE_SERVICE_KEY="取得したSupabaseのService Roleキー"
DISCORD_WEBHOOK_URL="取得したDiscordのWebhook URL"
```

3. スクリプトを実行します。
```bash
python main.py
```
> Discordにニュースが投稿されれば成功です！

## 4. GitHub Actionsでの自動化設定
1. GitHubにログインし、このコードベース (`AINFO`) をリポジトリとしてPushします。
2. GitHubのリポジトリ画面から、**Settings** > **Secrets and variables** > **Actions** に移動します。
3. `New repository secret` ボタンを押し、以下の4つのSecretを登録します。
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `DISCORD_WEBHOOK_URL`
4. ※これで完了です。日本時間の毎朝8:00に自動で起動し、Discordへニュースが3件ずつ配信されるようになります。

（GitHubのリポジトリの「Actions」タブから「Daily AI News Bot」を選択し、「Run workflow」ボタンを押すことでいつでも手動テストが可能です）
