import os
import json
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Groq API の設定
api_key = os.environ.get("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
else:
    client = None
    print("Warning: GROQ_API_KEY is not set.")

def analyze_and_score_articles(articles: list[dict], top_n: int = 3) -> list[dict]:
    """
    記事リストを1件ずつGroq (Llama 3.3 70B) に渡し、重要度を判定・スコアリングする。
    スコアが高い上位N件を返す。
    """
    if not articles or not client:
        return []

    print(f"Analyzing {len(articles)} articles individually with Groq (Llama 3.3 70B)...")
    final_articles = []
    
    for i, article in enumerate(articles):
        print(f"[{i+1}/{len(articles)}] Analyzing: {article['title']}")
        prompt = f"""あなたはプロのAIキュレーターです。以下のAI関連ニュース記事を評価してください。

【評価基準】
以下の要素を持つ記事を高く評価（スコアリング）してください。
- 優先度「高」(80-100点): ChatGPT, Claude, Gemini のメジャーアップデートや新機能リリース情報
- 優先度「中」(50-79点): 新しいAIツール・サービス（特に無料で試せるもの）の紹介やリリース情報
- 優先度「低」(0-49点): 個別企業の小さな導入事例や、一般的なAIのポエム・オピニオン記事

【指示】
1. この記事の重要度を0〜100のスコアで評価してください。
2. 日本語で3〜5行程度の簡潔で分かりやすい「要約」を作成してください。
3. 以下のJSONフォーマットで出力してください。JSON以外のテキスト（マークダウンの```json等）は含めないでください。

{{
  "title": "{article['title']}",
  "url": "{article['link']}",
  "summary": "作成した要約文",
  "score": 85
}}

【記事タイトル】
{article['title']}
【記事URL】
{article['link']}"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "あなたはAIニュースの専門キュレーターです。指示された通りにJSONのみを出力してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            text = response.choices[0].message.content.strip()
            
            # ```json などのマークダウン装飾を取り除く
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            result_json = json.loads(text.strip())
            
            # 元のpublished情報を結合
            result_json['published'] = article.get('published', '')
            final_articles.append(result_json)
            
        except Exception as e:
            print(f"Error analyzing article '{article['title']}': {e}")
            
        # Rate limit回避のためのウェイト (最後以外)
        if i < len(articles) - 1:
            time.sleep(2)

    print(f"Analyzed {len(final_articles)} articles successfully.")
    
    # スコアで降順にソートし、上位N件を返す
    final_articles.sort(key=lambda x: x.get('score', 0), reverse=True)
    return final_articles[:top_n]
