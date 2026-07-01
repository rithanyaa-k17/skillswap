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

@app.route("/request/<int:profile_id>", methods=["GET", "POST"])
def send_request(profile_id):
    conn = get_db_connection()

    profile = conn.execute(
        "SELECT * FROM profiles WHERE id = ?",
        (profile_id,)
    ).fetchone()

    if request.method == "POST":
        requester_name = request.form.get("requester_name")
        message = request.form.get("message")

        existing_request = conn.execute(
            """
            SELECT * FROM requests
            WHERE profile_id = ?
            AND requester_name = ?
            AND status != 'Rejected'
            """,
            (profile_id, requester_name)
        ).fetchone()

        if existing_request:
            conn.close()
            return render_template(
                "request.html",
                profile=profile,
                error="You already have an active request for this profile. You can request again only if the previous request is rejected."
            )

        conn.execute(
            """
            INSERT INTO requests (profile_id, requester_name, message)
            VALUES (?, ?, ?)
            """,
            (profile_id, requester_name, message)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("view_requests"))

    conn.close()

    return render_template("request.html", profile=profile)

@app.route("/requests")
def view_requests():
    status_filter = request.args.get("status", "All")

    conn = get_db_connection()

    if status_filter == "All":
        requests = conn.execute("""
            SELECT 
                requests.id,
                requests.requester_name,
                requests.message,
                requests.status,
                profiles.name AS profile_name,
                profiles.teach_skill,
                profiles.learn_skill
            FROM requests
            JOIN profiles ON requests.profile_id = profiles.id
        """).fetchall()
    else:
        requests = conn.execute("""
            SELECT 
                requests.id,
                requests.requester_name,
                requests.message,
                requests.status,
                profiles.name AS profile_name,
                profiles.teach_skill,
                profiles.learn_skill
            FROM requests
            JOIN profiles ON requests.profile_id = profiles.id
            WHERE requests.status = ?
        """, (status_filter,)).fetchall()

    conn.close()

    return render_template(
        "requests.html",
        requests=requests,
        status_filter=status_filter
    )

@app.route("/requests/<int:request_id>/<new_status>", methods=["POST"])
def update_request_status(request_id, new_status):
    if new_status not in ["Accepted", "Rejected"]:
        return redirect(url_for("view_requests"))

    conn = get_db_connection()

    conn.execute(
        "UPDATE requests SET status = ? WHERE id = ?",
        (new_status, request_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("view_requests"))

@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()

    total_profiles = conn.execute(
        "SELECT COUNT(*) FROM profiles"
    ).fetchone()[0]

    total_requests = conn.execute(
        "SELECT COUNT(*) FROM requests"
    ).fetchone()[0]

    pending_requests = conn.execute(
        "SELECT COUNT(*) FROM requests WHERE status = 'Pending'"
    ).fetchone()[0]

    accepted_requests = conn.execute(
        "SELECT COUNT(*) FROM requests WHERE status = 'Accepted'"
    ).fetchone()[0]

    rejected_requests = conn.execute(
        "SELECT COUNT(*) FROM requests WHERE status = 'Rejected'"
    ).fetchone()[0]

    most_taught_skills = conn.execute("""
    SELECT teach_skill, COUNT(*) AS count
    FROM profiles
    GROUP BY LOWER(teach_skill)
    ORDER BY count DESC
    LIMIT 5
""").fetchall()

    most_wanted_skills = conn.execute("""
    SELECT learn_skill, COUNT(*) AS count
    FROM profiles
    GROUP BY LOWER(learn_skill)
    ORDER BY count DESC
    LIMIT 5
""").fetchall()
    conn.close()

    stats = {
        "total_profiles": total_profiles,
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "accepted_requests": accepted_requests,
        "rejected_requests": rejected_requests
    }

    return render_template(
    "dashboard.html",
    stats=stats,
    most_taught_skills=most_taught_skills,
    most_wanted_skills=most_wanted_skills
)
@app.route("/matches")
def smart_matches():
    conn = get_db_connection()

    matches = conn.execute("""
        SELECT
            learner.id AS learner_id,
            learner.name AS learner_name,
            learner.learn_skill AS skill_needed,
            teacher.id AS teacher_id,
            teacher.name AS teacher_name,
            teacher.teach_skill AS skill_offered
        FROM profiles learner
        JOIN profiles teacher
        ON LOWER(learner.learn_skill) = LOWER(teacher.teach_skill)
        WHERE learner.id != teacher.id
    """).fetchall()

    conn.close()

    return render_template("matches.html", matches=matches)

if __name__ == "__main__":
    app.run(debug=True)