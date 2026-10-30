import os

from flask import (Flask, redirect, render_template, request,
                   session, url_for)

import auth
import budget
import course_generator
import database
import filters
import paths
import ranking
import validation


app = Flask(
    __name__,
    template_folder=paths.resource_path("templates"),
    static_folder=paths.resource_path("static"),
)
app.secret_key = os.urandom(24)      # sessions are per-run, not persisted

DEFAULT_BUDGET = 1_000_000
DEFAULT_MEALS = 3


CSV_PATH = paths.resource_path("restaurants_north_vietnam.csv")


def get_db():
    conn = database.get_connection(paths.database_path())
    database.create_table(conn)
    auth.create_user_tables(conn)

    count = conn.execute(
        "SELECT COUNT(*) AS n FROM restaurants"
    ).fetchone()["n"]

    if count == 0:
        database.load_from_csv(conn, CSV_PATH)

    return conn


def login_required(view):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    wrapper.__name__ = view.__name__
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        conn = get_db()
        ok, message, user_id = auth.authenticate(
            conn, request.form.get("username", ""),
            request.form.get("password", ""))
        conn.close()
        if ok:
            session["user_id"] = user_id
            session["username"] = request.form.get("username", "").strip()
            session["attempts"] = 0
            return redirect(url_for("index"))
        session["attempts"] = session.get("attempts", 0) + 1
        error = message
    return render_template("login.html", error=error,
                           attempts=session.get("attempts", 0),
                           max_attempts=auth.MAX_ATTEMPTS)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        conn = get_db()
        ok, message = auth.register(
            conn, request.form.get("username", ""),
            request.form.get("password", ""),
            request.form.get("confirm", ""))
        conn.close()
        if ok:
            return redirect(url_for("login", created=1))
        error = message
    return render_template("register.html", error=error,
                           min_length=auth.MIN_PASSWORD_LENGTH)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/", methods=["GET"])
@login_required
def index():
    conn = get_db()
    locations = database.get_locations(conn)
    categories = database.get_food_categories(conn)
    dataset_mean = database.get_mean_rating(conn)

    destination = request.args.get("destination") or (locations[0] if locations else "")
    preferences = request.args.getlist("preference")

    ok_budget, budget_error = validation.validate_budget(
        request.args.get("budget", str(DEFAULT_BUDGET)))
    total_budget = float(request.args.get("budget", DEFAULT_BUDGET)) if ok_budget else DEFAULT_BUDGET

    ok_meals, meals_error = validation.validate_num_meals(
        request.args.get("meals", str(DEFAULT_MEALS)))
    num_meals = int(request.args.get("meals", DEFAULT_MEALS)) if ok_meals else DEFAULT_MEALS


    candidates = filters.filter_by_location(database.get_all(conn), destination)
    ranked = ranking.rank_restaurants(candidates, preferences, dataset_mean)
    course = course_generator.generate_course(ranked, num_meals, total_budget)
    conn.close()

    picked_ids = {r.id for r in course}
    spent = budget.calculate_total(course)

    return render_template(
        "index.html",
        username=session.get("username", ""),
        locations=locations,
        categories=categories,
        destination=destination,
        preferences=preferences,
        total_budget=int(total_budget),
        num_meals=num_meals,
        ranked=ranked,
        picked_ids=picked_ids,
        course=course,
        spent=spent,
        remaining=total_budget - spent,
        short_by=num_meals - len(course),
        errors=[e for e in (budget_error, meals_error) if e],
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
