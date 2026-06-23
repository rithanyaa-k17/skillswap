from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from database import init_db

app = Flask(__name__)

init_db()

def get_db_connection():
    conn = sqlite3.connect("skillswap.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def home():
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form.get("name")
        teach_skill = request.form.get("teach_skill")
        learn_skill = request.form.get("learn_skill")

        conn.execute(
            "INSERT INTO profiles (name, teach_skill, learn_skill) VALUES (?, ?, ?)",
            (name, teach_skill, learn_skill)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    profiles = conn.execute("SELECT * FROM profiles").fetchall()
    conn.close()

    return render_template("index.html", profiles=profiles)

if __name__ == "__main__":
    app.run(debug=True)