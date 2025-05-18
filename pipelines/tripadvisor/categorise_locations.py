import os
import json
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# PostgreSQL connection
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "postgres"),
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", "5432")
)
cur = conn.cursor()

# Step 1: Get all locations without an AI category
cur.execute("""
    SELECT l.location_id, l.name
    FROM tripadvisor_demo.tripadvisor_locations l
    LEFT JOIN tripadvisor_demo.location_categories_ai c ON l.location_id = c.location_id
    WHERE c.location_id IS NULL
""")
locations = cur.fetchall()

# Step 2: For each location, pull recent reviews and call OpenAI
for location_id, name in locations:
    cur.execute("""
        SELECT body FROM tripadvisor_demo.reviews
        WHERE location_id = %s
        ORDER BY published_date DESC
        LIMIT 3
    """, (location_id,))
    reviews = [row[0] for row in cur.fetchall() if row[0]]

    if not reviews:
        continue

    prompt = f"""Based on the venue name and recent customer reviews below, assign a single, clear food category such as "pizza", "traditional pub", "coffee", "vegan", "asian fusion", etc. Respond with only the category name.

Name: {name}
Reviews:
- {reviews[0]}"""
    if len(reviews) > 1:
        prompt += "\n- " + "\n- ".join(reviews[1:])

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        category = response.choices[0].message.content.strip().lower()

        cur.execute("""
            INSERT INTO tripadvisor_demo.location_categories_ai (location_id, ai_category, model_used)
            VALUES (%s, %s, %s)
            ON CONFLICT (location_id) DO UPDATE
            SET ai_category = EXCLUDED.ai_category,
                model_used = EXCLUDED.model_used,
                created_at = now();
        """, (location_id, category, "gpt-4"))
        conn.commit()
        print(f"✅ {location_id} — {category}")
    except Exception as e:
        print(f"❌ {location_id} — Error: {e}")

cur.close()
conn.close()
