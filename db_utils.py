from openai import OpenAI
import psycopg2
from psycopg2.extras import Json
import os

DB_NAME = os.getenv("DB_NAME", "code_review_ai")
DB_USER = os.getenv("DB_USER", "postgres")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")

def connect_db():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

def insert_review_result(review_results):
    project_name = review_results["repo_path"]
    comments = review_results["comments"]
    file_name = review_results["file_path"]
    suggestions = review_results["suggestions"]
    code = review_results["code"]
    language = review_results["language"]

    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO code_snippets (file_name, code, language)
                VALUES (%s, %s, %s)
                RETURNING snippet_id
            """, (file_name, code, language))
            snippet_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO reviews (project_name, comments, suggestions)
                VALUES (%s, %s, %s)
                RETURNING review_id
            """, (project_name, comments, suggestions))
            review_id = cur.fetchone()[0]

        conn.commit()
        return review_id, snippet_id
    finally:
        conn.close()

def retrieve_relevant_context(query_embedding, top_n=5):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            query_vector = f"[{','.join(map(str, query_embedding))}]"

            cur.execute("""
                SELECT review_id, snippet_id, raw_text
                FROM knowledge_base
                ORDER BY embedding <=> %s
                LIMIT %s
            """, (query_vector, top_n))
            results = cur.fetchall()
    finally:
        conn.close()
    return results

def generate_embedding(text):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )

    embedding = response.data[0].embedding
    return embedding

def insert_into_knowledge_base(review_id, snippet_id, raw_text):
    embedding = generate_embedding(raw_text)

    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO knowledge_base (review_id, snippet_id, embedding, raw_text)
                VALUES (%s, %s, %s, %s)
            """, (review_id, snippet_id, embedding, raw_text))
        conn.commit()
    finally:
        conn.close()