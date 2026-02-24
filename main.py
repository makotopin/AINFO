import sys
from src.fetch_news import fetch_latest_news
from src.db_manager import filter_unprocessed_articles, save_articles
from src.analyze_news import analyze_and_score_articles
from src.discord_notifier import send_to_discord

def main():
    print("--- ニュース収集処理を開始します ---")
    
    # 1. ニュースの取得
    raw_articles = fetch_latest_news()
    if not raw_articles:
        print("新規ニュースが見つかりませんでした。終了します。")
        return
        
    print(f"取得元から計 {len(raw_articles)} 件の記事を見つけました。")
    
    # 2. すでに処理した（DBにある）記事を弾く
    # ※ 初回実行時やDB設定前はすべて新規扱いにする等の対応も可能ですが
    # ここでは仕様通りDBチェックを走らせます
    try:
        new_articles = filter_unprocessed_articles(raw_articles)
    except Exception as e:
        print(f"DB確認中にエラーが発生しました。DBが未設定の可能性があります: {e}")
        print("未処理として全件を進めます。")
        new_articles = raw_articles
        
    if not new_articles:
        print("すべての記事が既に処理・配信済みでした。終了します。")
        return
        
    # 3. Geminiにスコアリングと要約を依頼 (上位3件を取得)
    print("Gemini APIで記事の重要度を判定し、要約を生成します...")
    selected_articles = analyze_and_score_articles(new_articles, top_n=3)
    
    if not selected_articles:
        print("配信すべき重要な記事が抽出されませんでした。")
        return
        
    # 4. 選ばれた記事をDiscordに送信
    print(f"選出された {len(selected_articles)} 件の記事をDiscordへ送信します。")
    send_to_discord(selected_articles)
    
    # 5. DBに保存して次回から弾けるようにする
    print("送信した情報をデータベースに保存します...")
    try:
        save_articles(selected_articles)
    except Exception as e:
        print(f"DB保存でエラーが発生しました。環境変数が未設定の可能性があります。: {e}")
        
    print("--- すべての処理が完了しました ---")

if __name__ == "__main__":
    main()
