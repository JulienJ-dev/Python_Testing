import json
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


def is_competition_past(competition):
    competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    return competition_date < datetime.now()


@app.context_processor
def current_time():
    return {'now': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form.get('email', '').strip()
    club = next((club for club in clubs if club['email'] == email), None)
    if club is None:
        flash("Sorry, that email was not found.")
        return redirect(url_for('index'))
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if is_competition_past(foundCompetition):
        flash('You cannot book a past competition.')
        return render_template('welcome.html', club=foundClub, competitions=competitions)
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = next(
        (c for c in competitions if c['name'] == request.form.get('competition')),
        None,
    )
    club = next((c for c in clubs if c['name'] == request.form.get('club')), None)
    if club is None or competition is None:
        flash('Something went wrong-please try again')
        return redirect(url_for('index'))
    try:
        placesRequired = int(request.form.get('places', ''))
    except (TypeError, ValueError):
        flash('Please enter a valid number of places.')
        return render_template('booking.html', club=club, competition=competition)
    if placesRequired <= 0:
        flash('Please enter a positive number of places.')
        return render_template('booking.html', club=club, competition=competition)
    if is_competition_past(competition):
        flash('You cannot book a past competition.')
        return render_template('booking.html', club=club, competition=competition)
    if placesRequired > int(club['points']):
        flash('You do not have enough points.')
        return render_template('booking.html', club=club, competition=competition)
    alreadyBooked = int(competition.get('bookings', {}).get(club['name'], 0))
    if placesRequired > 12 or alreadyBooked + placesRequired > 12:
        flash('This club cannot book more than 12 places in one competition.')
        return render_template('booking.html', club=club, competition=competition)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    bookings = competition.setdefault('bookings', {})
    bookings[club['name']] = alreadyBooked + placesRequired
    club['points'] = str(int(club['points']) - placesRequired)
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
