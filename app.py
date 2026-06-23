from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    profile = None

    if request.method == "POST":
        name = request.form.get("name")
        teach_skill = request.form.get("teach_skill")
        learn_skill = request.form.get("learn_skill")

        profile = {
            "name": name,
            "teach_skill": teach_skill,
            "learn_skill": learn_skill
        }

    return render_template("index.html", profile=profile)

if __name__ == "__main__":
    app.run(debug=True)