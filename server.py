import json

from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for


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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
    except IndexError:
        flash("Sorry, that email wasn't found")
        return redirect(url_for('index'))
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template('welcome.html', club=club, competitions=competitions, current_time=current_time)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])

    competition_date = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")
    current_date = datetime.now()
    
    if competition_date < current_date:
        flash('Cannot book places for a past competition')
    elif placesRequired > 12:
        flash('Cannot book more than 12 places')
    elif placesRequired > int(competition['numberOfPlaces']):
        flash('Not enough places available in the competition')
    elif placesRequired <= 0:
        flash('Number of places must be positive')
    elif placesRequired > int(club['points']):
        flash('Not enough points available in the club')
    else:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        club['points'] = int(club['points']) - placesRequired
        flash('Great-booking complete!')
        
    competitions_with_dates = [
        {**comp, 'date': datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")}
        for comp in competitions
    ]
    return render_template('welcome.html', club=club, competitions=competitions_with_dates, current_time=current_date)


# [x]: Route added for points display 
@app.route('/viewClubPoints')
def viewClubPoints():
    club = sorted(clubs, key=lambda club: club['name'])
    return render_template('view_club_points.html', clubs=club)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))
