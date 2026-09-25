import json
import os
from datetime import datetime
from pathlib import Path
from threading import Lock

from flask import Flask, flash, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).parent
MAX_PLACES_PER_BOOKING = 12
STATE_FILE = Path(os.environ.get("GUDLFT_STATE_FILE", BASE_DIR / "state.json"))
booking_lock = Lock()


def load_clubs():
    """Load the clubs from the JSON file."""
    with open(BASE_DIR / "clubs.json", encoding="utf-8") as clubs_file:
        return json.load(clubs_file)["clubs"]


def load_competitions():
    """Load the competitions from the JSON file."""
    with open(BASE_DIR / "competitions.json", encoding="utf-8") as competitions_file:
        return json.load(competitions_file)["competitions"]


def load_state():
    """Load saved bookings, or use the original JSON data on first launch."""
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as state_file:
            state = json.load(state_file)
        return state["clubs"], state["competitions"]
    return load_clubs(), load_competitions()


def save_state(new_clubs, new_competitions):
    """Save both balances together, replacing the previous state only when ready."""
    temporary_file = STATE_FILE.with_suffix(".tmp")
    with open(temporary_file, "w", encoding="utf-8") as state_file:
        json.dump(
            {"clubs": new_clubs, "competitions": new_competitions},
            state_file,
            indent=2,
        )
    os.replace(temporary_file, STATE_FILE)


def find_club(value, field="name"):
    """Return a club matching a name or an email address."""
    return next((club for club in clubs if club.get(field) == value), None)


def find_competition(name):
    """Return a competition matching its name."""
    return next(
        (competition for competition in competitions if competition.get("name") == name),
        None,
    )


def is_competition_past(competition, now=None):
    """Tell whether a competition has already started."""
    competition_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")
    return competition_date < (now or datetime.now())


def remaining_booking_limit(club, competition):
    """Return how many more places this club can buy for this competition."""
    already_booked = int(competition.get("bookings", {}).get(club["name"], 0))
    return max(
        0,
        min(
            MAX_PLACES_PER_BOOKING - already_booked,
            int(competition["numberOfPlaces"]),
            int(club["points"]),
        ),
    )


def validate_booking(club, competition, places):
    """Return an error message when a booking is not allowed."""
    if places <= 0:
        return "Please enter a positive number of places."
    if places > MAX_PLACES_PER_BOOKING:
        return "You cannot book more than 12 places."
    if is_competition_past(competition):
        return "You cannot book a past competition."
    if places > int(competition["numberOfPlaces"]):
        return "There are not enough places available."
    if places > int(club["points"]):
        return "You do not have enough points."
    already_booked = int(competition.get("bookings", {}).get(club["name"], 0))
    if already_booked + places > MAX_PLACES_PER_BOOKING:
        return "This club cannot book more than 12 places in one competition."
    return None


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "development-only-secret")

clubs, competitions = load_state()


@app.context_processor
def inject_current_time():
    return {
        "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "remaining_booking_limit": remaining_booking_limit,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def show_summary():
    email = request.form.get("email", "").strip()
    club = find_club(email, field="email")
    if club is None:
        session.pop("club_email", None)
        flash("Sorry, that email was not found.")
        return redirect(url_for("index"))
    session["club_email"] = club["email"]
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    if "club_email" not in session:
        flash("Please log in before booking.")
        return redirect(url_for("index"))
    found_club = find_club(club)
    found_competition = find_competition(competition)
    if (
        found_club is None
        or found_competition is None
        or found_club["email"] != session["club_email"]
    ):
        flash("Something went wrong - please try again.")
        return redirect(url_for("index"))
    if is_competition_past(found_competition):
        flash("You cannot book a past competition.")
        return render_template(
            "welcome.html", club=found_club, competitions=competitions
        )
    return render_template(
        "booking.html", club=found_club, competition=found_competition
    )


@app.route("/purchasePlaces", methods=["POST"])
def purchase_places():
    if "club_email" not in session:
        flash("Please log in before booking.")
        return redirect(url_for("index"))

    club = find_club(session["club_email"], field="email")
    competition = find_competition(request.form.get("competition", ""))

    if club is None or competition is None:
        flash("Something went wrong - please try again.")
        return redirect(url_for("index"))

    try:
        places_required = int(request.form.get("places", ""))
    except (TypeError, ValueError):
        flash("Please enter a valid number of places.")
        return render_template("booking.html", club=club, competition=competition)

    with booking_lock:
        # Read the latest values while holding the lock: another request may
        # have completed a booking since the values were first looked up.
        club = find_club(session["club_email"], field="email")
        competition = find_competition(request.form.get("competition", ""))
        error = validate_booking(club, competition, places_required)
        if error:
            flash(error)
            return render_template("booking.html", club=club, competition=competition)

        new_clubs = [item.copy() for item in clubs]
        new_competitions = [item.copy() for item in competitions]
        updated_club = next(item for item in new_clubs if item["name"] == club["name"])
        updated_competition = next(
            item for item in new_competitions if item["name"] == competition["name"]
        )
        updated_club["points"] = str(int(club["points"]) - places_required)
        updated_competition["numberOfPlaces"] = str(
            int(competition["numberOfPlaces"]) - places_required
        )
        bookings = competition.get("bookings", {}).copy()
        bookings[club["name"]] = int(bookings.get(club["name"], 0)) + places_required
        updated_competition["bookings"] = bookings

        try:
            save_state(new_clubs, new_competitions)
        except OSError:
            flash("Booking could not be saved. Please try again.")
            return render_template("booking.html", club=club, competition=competition)

        clubs[:] = new_clubs
        competitions[:] = new_competitions

    club = find_club(session["club_email"], field="email")
    flash(f"Great - booking complete! {places_required} place(s) booked.")
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/pointsDisplay")
def points_display():
    return render_template("points_display.html", clubs=clubs)


@app.route("/logout")
def logout():
    session.pop("club_email", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
