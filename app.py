from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from database import init_db

app = Flask(__name__)

init_db()

def get_db_connection():
    conn = sqlite3.connect("skillswap.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/create", methods=["GET", "POST"])
def create_profile():
    if request.method == "POST":
        name = request.form.get("name")
        teach_skill = request.form.get("teach_skill")
        learn_skill = request.form.get("learn_skill")

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO profiles (name, teach_skill, learn_skill) VALUES (?, ?, ?)",
            (name, teach_skill, learn_skill)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("search_profiles"))

    return render_template("create.html")

@app.route("/search")
def search_profiles():
    search_query = request.args.get("search", "")

    conn = get_db_connection()

    if search_query:
        profiles = conn.execute(
            """
            SELECT * FROM profiles
            WHERE teach_skill LIKE ? OR learn_skill LIKE ?
            """,
            (f"%{search_query}%", f"%{search_query}%")
        ).fetchall()
    else:
        profiles = conn.execute("SELECT * FROM profiles").fetchall()

    conn.close()

    return render_template(
        "search.html",
        profiles=profiles,
        search_query=search_query
    )

if __name__ == "__main__":
    app.run(debug=True)