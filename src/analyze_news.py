import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini API の設定
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # Gemini 2.0 Flash をデフォルトで使用
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None
    print("Warning: GEMINI_API_KEY is not set.")

def analyze_and_score_articles(articles: list[dict], top_n: int = 3) -> list[dict]:
    """
    記事リストをGeminiに渡し、重要度を判定・スコアリングして上位N件を要約付きで返す。
    """
    if not articles or not model:
        return []

    # プロンプトに渡すために記事リストをテキスト化
    articles_text = ""
    for i, article in enumerate(articles):
        articles_text += f"[{i}] Title: {article['title']}\n URL: {article['link']}\n\n"

    prompt = f"""
あなたはプロのAIキュレーターです。以下の最新ニュース記事リストから、最も注目すべき重要なAIニュースを厳選し、評価してください。

【評価基準】
以下の要素を持つ記事を高く評価（スコアリング）してください。
- 優先度「高」: ChatGPT, Claude, Gemini のメジャーアップデートや新機能リリース情報
- 優先度「中」: 新しいAIツール・サービス（特に無料で試せるもの）の紹介やリリース情報
- 優先度「低」: 個別企業の小さな導入事例や、一般的なAIのポエム・オピニオン記事

【指示】
1. リストの中から、上記基準に従って最も重要なニュースを「最大 {top_n} 件」選出してください。（該当が少ない場合はそれ以下でも構いません）
2. 選出した各記事について、日本語で3〜5行程度の簡潔で分かりやすい「要約」を作成してください。
3. 以下のJSONフォーマットで出力してください。JSON以外のテキスト（マークダウンの```json等）は含めないでください。

[
  {{
    "title": "元の記事のタイトル",
    "url": "元の記事のURL",
    "summary": "作成した要約文",
    "score": 95
  }},
  ...
]

【記事リスト】
{articles_text}
"""

    print(f"Sending {len(articles)} articles to Gemini for analysis...")
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # ```json などのマークダウン装飾を取り除く
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        result_json = json.loads(text.strip())
        
        # 必要な情報を補完
        final_articles = []
        for item in result_json:
            # 元のpublished情報を結合するための検索
            original_published = ""
            for a in articles:
                if a['link'] == item['url'] or a['title'] == item['title']:
                    original_published = a.get('published', '')
                    break
            
            item['published'] = original_published
            final_articles.append(item)
            
        print(f"Gemini selected {len(final_articles)} important articles.")
        return final_articles[:top_n]
        
    except Exception as e:
        print(f"Error during Gemini analysis: {e}")
        return []
