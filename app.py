from flask import Flask, request, render_template, jsonify
import psycopg2
import os

app = Flask(__name__)

# Supabase / Postgres connection (z environment variables)
DB_URL = os.environ.get("DB_URL")  # něco jako: postgres://user:pass@host:port/dbname

def get_conn():
    return psycopg2.connect(DB_URL)

@app.route("/", methods=["GET"])
def search():
    query = request.args.get("query", "")
    results = []

    if query:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT url, title, description, icon,
                   CASE WHEN LOWER(title) LIKE %s THEN 0 ELSE 1 END AS rank
            FROM pages
            WHERE content ILIKE %s OR title ILIKE %s OR description ILIKE %s
            ORDER BY rank, title ASC
            LIMIT 50
        """, (f'{query.lower()}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        rows = c.fetchall()
        conn.close()

        results = [{"url": r[0], "title": r[1], "description": r[2], "icon": r[3]} for r in rows]

    return render_template("search.html", results=results, query=query)

@app.route("/suggest")
def suggest():
    term = request.args.get("term", "")
    suggestions = []

    if term:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT title
            FROM pages
            WHERE title ILIKE %s OR content ILIKE %s
            LIMIT 10
        """, (f'{term}%', f'%{term}%'))
        suggestions = [row[0] for row in c.fetchall()]
        conn.close()

    suggestions.sort(key=lambda s: (0 if s.lower().startswith(term.lower()) else 1, s))
    return jsonify(suggestions)

if __name__ == "__main__":
    app.run()
