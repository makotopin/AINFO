import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_to_discord(articles: list[dict]):
    """
    要約済みの記事リストをDiscord Webhookに送信する。
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
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
        
        embed = {
            "title": f"[{i+1}] {article.get('title', 'No Title')}",
            "url": article.get('url', ''),
            "description": article.get('summary', 'No summary available.'),
            "color": color,
            "footer": {"text": "AI News Bot - Powerd by Gemini"},
            "timestamp": article.get('published', '')
        }
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
