from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('ranking', __name__)


@bp.route('/rankings')
def index():
    db = get_db()
    names = db.execute('SELECT name, rating from names ORDER BY rating DESC').fetchall()
    return render_template('ranking/index.html', names=names)

@bp.route('/contest', methods=('GET', 'POST'))
def contest():
    db = get_db()
    rand_names = db.execute('SELECT name from names ORDER BY random() LIMIT 2').fetchall()
    if request.method == 'POST':
        name = request.form['name']
        if name == rand_names[0]['name']:
            not_chosen = rand_names[1]['name']
        else:
            not_chosen = rand_names[0]['name']
        winner_rating = db.execute('SELECT rating from names WHERE name = ?', (name,)).fetchone();
        looser_rating = db.execute('SELECT rating from names WHERE name = ?', (not_chosen,)).fetchone();
        new_winner_rating = winner_rating[0] + 16;
        new_looser_rating = looser_rating[0] - 16;
        db.execute('UPDATE names SET rating = ? WHERE name = ?', (new_winner_rating, name))
        db.commit()
        db.execute('UPDATE names SET rating = ? WHERE name = ?', (new_looser_rating, not_chosen))
        db.commit()

    return render_template('ranking/contest.html', names=rand_names)


@bp.route('/create-player', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        rating = 1700
        error = None

        if not name:
            error = 'Name is required.'

        my_db = get_db()

        if my_db.execute('SELECT name FROM names WHERE name = ?', (name.lower(),)).fetchone():
            flash("Already exists")
        elif error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO names VALUES(?, ?)', (name.lower(), rating))
            db.commit()
            return redirect(url_for('ranking.index'))

    return render_template('ranking/create.html')
