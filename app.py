

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, NumberRange

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    ratings = db.relationship('Rating', backref='user', lazy=True)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genres = db.Column(db.String(100), nullable=False)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

# Define forms
class RatingForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Submit')

# Routes and views
@app.route('/')
def index():
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

@app.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = RatingForm()

    if form.validate_on_submit():
        rating = form.rating.data
        user_id = 1  # Replace this with actual user authentication
        new_rating = Rating(rating=rating, user_id=user_id, movie_id=movie.id)
        db.session.add(new_rating)
        db.session.commit()
        flash('Rating submitted successfully!', 'success')

    return render_template('movie.html', movie=movie, form=form)

@app.route('/recommendations')
def recommendations():
    user_id = 1  
    user_ratings = Rating.query.filter_by(user_id=user_id).all()
    user_genres = [movie.movie.genres.split('|') for movie in user_ratings]
    user_genres = [genre for sublist in user_genres for genre in sublist]

    
    recommended_movies = Movie.query.filter(Movie.genres.ilike('%' + '%'.join(user_genres) + '%')).limit(10).all()

    return render_template('recommendations.html', recommended_movies=recommended_movies)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
