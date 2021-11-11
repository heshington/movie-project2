import configparser

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import configparser

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

## CREATE DATABASE

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

API_URL="https://api.themoviedb.org/3/search/"

def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['moviedatabase']['api']


# CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(120))
    img_url = db.Column(db.String(120), nullable=False)


db.create_all()


# Edit form
class EditForm(FlaskForm):
    rating = StringField('Your rating out of 10 eg 7.5', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField(label="Done")


# Add form
class AddForm(FlaskForm):
    movie_title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")


@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    if request.method == "POST":
        movie_id = request.args.get('movie_id')
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = request.form['rating']
        movie_to_update.review = request.form['review']
        db.session.commit()
        return redirect(url_for('home'))
    else:
        edit_form = EditForm()
        edit_form.validate_on_submit()
        return render_template("edit.html", form=edit_form)


@app.route('/delete')
def delete():
    movie_id = request.args.get('movie_id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        add_form = AddForm()
        add_form.validate_on_submit()
        return render_template("add.html", form=add_form)
    elif request.method == 'POST':
        movie_title = request.form['movie_title']
        api_key = get_api_key()


        api_search = f"{API_URL}movie?api_key={api_key}&query={movie_title}&language=en-US"
        response = requests.get(api_search)
        movie_response = response.json()['results']
        listed_movies = []
        for movie in movie_response:
            listed_movies.append(movie.get('original_title'))
        return render_template("select.html", movies=movie_response)


@app.route('/movie_id')
def movie_detail():
    movie_id = request.args.get("id")

    if movie_id:
        url = "https://api.themoviedb.org/3/movie/"
        api_key = get_api_key()
        api_search = f"{url}/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(api_search).json()
        print(response)

        #add to the database
        full_poster_path = f"https://image.tmdb.org/t/p/w500/{response.get('poster_path')}"
        new_movie = Movie(id=movie_id, title=response.get('title'), img_url=full_poster_path, year=response.get('release_date').split('-')[0],
                              description=response.get('overview'))
        db.session.add(new_movie)
        db.session.commit()
        #redirect user to edit page to add Rating
        # edit_form = EditForm()
        # edit_form.validate_on_submit()
        return redirect(url_for('edit', movie_id=new_movie.id))




if __name__ == '__main__':
    app.run(debug=True)
