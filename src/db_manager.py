import os
from supabase import create_client, Client
from dotenv import load_dotenv

# ローカルテスト用に.envがあれば読み込む
load_dotenv()

def get_supabase_client() -> Client:
    """Supabaseクライアントを初期化して返す"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise ValueError("Supabaseの環境変数 (SUPABASE_URL, SUPABASE_SERVICE_KEY) が設定されていません。")
    return create_client(url, key)

def filter_unprocessed_articles(articles: list[dict]) -> list[dict]:
    """
    取得した記事リストのうち、既にDBに存在する(処理済みの)ものを除外する。
    """
    if not articles:
        return []
        
    supabase = get_supabase_client()
    
    # URLのリストを作成
    urls = [article['link'] for article in articles]
    
    # DBに存在するURLを一括取得
    # in_() フィルタを使用して複数URLを一度に検索
    response = supabase.table("ai_news_articles").select("url").in_("url", urls).execute()
    
    # 既存URLのSetを作成
    existing_urls = {record['url'] for record in response.data}
    
    # 新規に処理すべき記事だけを残す
    unprocessed = [a for a in articles if a['link'] not in existing_urls]
    
    print(f"Total fetched: {len(articles)}, Already processed: {len(existing_urls)}, New: {len(unprocessed)}")
    return unprocessed

def save_articles(processed_articles: list[dict]):
    """
    要約・スコアリング済みの記事データをDBに保存する。
    processed_articles: [
        {'title': ..., 'url': ..., 'summary': ..., 'published_at': ...}
    ]
    """
    if not processed_articles:
        return
        
    supabase = get_supabase_client()
    
    # DB挿入用のフォーマットに整形
    records = []
    for article in processed_articles:
        records.append({
            "title": article['title'],
            "url": article['url'],
            "summary": article.get('summary', ''),
            "published_at": article.get('published', '')
        })
        
    # 一括挿入
    try:
        response = supabase.table("ai_news_articles").insert(records).execute()
        print(f"Successfully saved {len(response.data)} articles to Supabase.")
    except Exception as e:
        print(f"Failed to save articles to Supabase: {e}")
