from flask import Flask, request, render_template, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/", methods=["GET"])
def search():
    query = request.args.get("query", "")
    results = []

    if query:
        conn = sqlite3.connect('hrajty.db')
        c = conn.cursor()
        c.execute("""
            SELECT url, title, description, icon,
                   CASE WHEN LOWER(title) LIKE ? THEN 0 ELSE 1 END AS rank
            FROM pages
            WHERE content LIKE ? OR title LIKE ? OR description LIKE ?
            ORDER BY rank, title ASC
            LIMIT 50
        """, ('{}%'.format(query.lower()), '%'+query+'%', '%'+query+'%', '%'+query+'%'))
        rows = c.fetchall()
        conn.close()

        results = [{"url": r[0], "title": r[1], "description": r[2], "icon": r[3]} for r in rows]

    return render_template("search.html", results=results, query=query)


@app.route("/suggest")
def suggest():
    term = request.args.get("term", "")
    suggestions = []

    if term:
        conn = sqlite3.connect('hrajty.db')
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT title
            FROM pages
            WHERE title LIKE ? OR content LIKE ?
            LIMIT 10
        """, ('{}%'.format(term), '%'+term+'%'))
        suggestions = [row[0] for row in c.fetchall()]
        conn.close()

    # Seřadíme návrhy tak, aby začínaly termínem nahoře
    suggestions.sort(key=lambda s: (0 if s.lower().startswith(term.lower()) else 1, s))
    return jsonify(suggestions)


if __name__ == "__main__":
    app.run(debug=True)
