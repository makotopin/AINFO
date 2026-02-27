import os
import requests
from datetime import datetime
import dateutil.parser
from dotenv import load_dotenv

load_dotenv()

def send_to_discord(articles: list[dict]):
    """
    要約済みの記事リストをDiscord Webhookに送信する。
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook_url:
        print("Warning: DISCORD_WEBHOOK_URL is not set. Skipping Discord notification.")
        return
        
    if not articles:
        print("No articles to send to Discord.")
        return
        
    embeds = []
    for i, article in enumerate(articles):
        # 色をつける（1位: 金, 2位: 銀, 3位: 銅）
        colors = [0xFFD700, 0xC0C0C0, 0xCD7F32]
        color = colors[i] if i < len(colors) else 0x5865F2 # デフォルト色
        
        # 日付をISO 8601形式に変換（Discordの仕様）
        iso_timestamp = ""
        pub_date = article.get('published', '')
        if pub_date:
            try:
                # どんな形式の日付でもパースを試みる
                parsed_date = dateutil.parser.parse(pub_date)
                iso_timestamp = parsed_date.isoformat()
            except Exception:
                # パース失敗時は現在時刻を代わりに入れる（空文字だとDiscordに蹴られるため）
                iso_timestamp = datetime.utcnow().isoformat() + "Z"
        
        embed = {
            "title": f"[{i+1}] {article.get('title', 'No Title')}",
            "url": article.get('url', ''),
            "description": article.get('summary', 'No summary available.'),
            "color": color,
            "footer": {"text": "AI News Bot - Powered by Llama 3.3 (Groq)"}
        }
        
        # timestampが有効な場合のみ追加
        if iso_timestamp:
            embed["timestamp"] = iso_timestamp
            
        embeds.append(embed)
        
    payload = {
        "content": "✨ **本日の重要AIニュース** ✨",
        "embeds": embeds
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("Successfully sent message to Discord.")
    except Exception as e:
        print(f"Failed to send message to Discord: {e}")
        # 詳細なエラー情報を出す
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response body: {e.response.text}")
