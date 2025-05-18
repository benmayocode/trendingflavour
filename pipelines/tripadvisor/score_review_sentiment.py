# pipelines/tripadvisor/score_review_sentiment.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env')

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from dotenv import load_dotenv
from get_connection import get_connection

load_dotenv()

def fetch_unscored_reviews(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT r.review_id, r.body
            FROM tripadvisor_demo.reviews r
            LEFT JOIN tripadvisor_demo.review_sentiment s
            ON r.review_id = s.review_id
            WHERE s.review_id IS NULL AND r.body IS NOT NULL
            LIMIT 50;
        """)
        return cur.fetchall()

def insert_sentiments(conn, sentiments):
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO tripadvisor_demo.review_sentiment (
                review_id, sentiment_label, sentiment_score, analysed_at
            )
            VALUES (%s, %s, %s, now())
            ON CONFLICT (review_id) DO NOTHING;
        """, sentiments)
    conn.commit()

def classify_sentiment(text):
    prompt = (
        "Classify the sentiment of this restaurant review as 'positive', 'neutral', or 'negative'. "
        "Also give a score from 1 (negative) to 5 (positive).\n\n"
        f"Review:\n{text}\n\n"
        "Respond in JSON format:\n"
        '{"label": "positive", "score": 4}'
    )
    try:
        res = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3)
        output = res.choices[0].message.content
        result = eval(output.strip())
        return result['label'], result['score']
    except Exception as e:
        print("OpenAI error:", e)
        return None, None

def main():
    conn = get_connection()
    rows = fetch_unscored_reviews(conn)

    results = []
    for review_id, text in rows:
        label, score = classify_sentiment(text)
        if label and score:
            results.append((review_id, label, score))

    if results:
        insert_sentiments(conn, results)
        print(f"Inserted {len(results)} sentiment scores.")
    else:
        print("No new sentiments inserted.")

    conn.close()

if __name__ == "__main__":
    main()
