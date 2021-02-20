from flask import Flask, render_template, flash, redirect, url_for, session, request
from db_connector import connect_to_database, execute_query
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key='thisissecretdontshare'

#Search Form
class SearchForm(Form):
    title = StringField('')

#Index
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(form)
    return render_template('index.html',form=form)
    
#endpoint for search
@app.route('/search')
def search_results(search):
    db_connection = connect_to_database()
    form = SearchForm(request.form)
    if request.method == "POST":
        title = request.form['title']
        search_query = "SELECT movieId,title,genre,year FROM movies WHERE title = %s"
        search_results = execute_query(db_connection,search_query,[title]).fetchone()
        # print(search_results)
        if search_results: #display results
            session['title'] = title
            return render_template('search.html',form = form,search_results = search_results)
        else:
            flash('No results found! You can help others by adding it')
            return redirect(url_for('add_movie'))


# Register Form
#reference: https://flask.palletsprojects.com/en/1.1.x/patterns/wtforms/
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    db_connection = connect_to_database()
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        query = 'INSERT INTO reviewers (name,username,email,password) VALUES (%s,%s,%s,%s)'
        data = (name,username,email,password)
        execute_query(db_connection, query, data)

        flash('You have successfully signed up. To continue with the site please log in now')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# # User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    db_connection = connect_to_database()
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        people_query = "SELECT * FROM reviewers WHERE username = %s"
        people_result = execute_query(db_connection,people_query,[username]).fetchone()
        # print(people_result)
        if people_result != None:
            # Get the correct password from databse
            password = people_result[-1]

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('Welcome')
                return redirect(url_for('dashboard'))
            else: #password does not match
                error = 'There was a problem, your password is incorrect'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Logout
@app.route('/logout')
def signout():
    session.clear()
    flash('You are now signed out')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    db_connection = connect_to_database()
    people_query = "SELECT name,email FROM reviewers WHERE username = %s"
    people_result = execute_query(db_connection, people_query,[session['username']]).fetchone()
    # print(people_result,people_result[0],people_result[1])

    rating_query = "SELECT title,rating,review,ratingDate FROM ratings inner join movies on ratings.movieId  = movies.movieId where reviewerId in (SELECT reviewerId FROM reviewers WHERE username = %s)"
    rating_result = execute_query(db_connection, rating_query,[session['username']]).fetchall()
    # print(rating_result)
    if rating_result:
        return render_template('dashboard.html',results=rating_result)

    return render_template('dashboard.html',rows=people_result)

# Movie Form Class
#reference: https://flask.palletsprojects.com/en/1.1.x/patterns/wtforms/
#reference: https://wtforms.readthedocs.io/en/2.3.x/fields/
class MovieForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=100)])
    genre = StringField('Genre', [validators.Length(min=1, max=100)])
    release_year = IntegerField('Release year')
    budget = IntegerField('Budget')
    box_office = IntegerField('Box office')
    rating = IntegerField('Box office',)
    # director = StringField('Director', [validators.Length(min=1, max=200)])
    # actor = StringField('actor', [validators.Length(min=1, max=200)])


# Movies
@app.route('/movie')
def movie():
    db_connection = connect_to_database()
    movie_query = "SELECT movieId,title,budget,avgRating,genre,boxOffice,year FROM movies"
    movie_result = execute_query(db_connection,movie_query).fetchall()
    print(movie_result)

    return render_template('movie.html', rows=movie_result)
    
# Add Movie
@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    form = MovieForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        title = form.title.data
        genre = form.genre.data
        release_year = form.release_year.data
        budget = form.budget.data
        box_office = form.box_office.data
        rating = form.rating.data
        # director = form.director.data
        # actor = form.actor.data

        movie_query = 'INSERT INTO movies (title,budget,avgRating,genre,boxOffice,year) VALUES (%s,%s,%s,%s,%s,%s)'
        data = (title,budget,rating,genre,box_office,release_year)
        execute_query(db_connection, movie_query, data)

        flash('Movie added!', 'success')

        return redirect(url_for('movie'))

    return render_template('add_movie.html', form=form)


# Display user reviews
@app.route('/user_reviews')
def user_reviews():
    db_connection = connect_to_database()
    rating_query = 'SELECT ratings.movieId,rating,title,username,ratingDate,review FROM ratings inner join movies ON ratings.movieId = movies.movieId inner join reviewers on reviewers.reviewerId = ratings.reviewerId'
    # print(rating_query)
    results = execute_query(db_connection, rating_query).fetchall()
    return render_template('user_reviews.html', rows=results)


@app.route('/view_rating/<int:movieId>')
def view_rating(movieId):
    db_connection = connect_to_database()
    view_query = "SELECT reviewers.username,rating,review FROM reviewers inner join ratings ON reviewers.reviewerId = ratings.reviewerId WHERE movieId = %s"  % (movieId)
    # print(view_query)
    selectedmovie = "SELECT title,budget,avgRating,genre,boxOffice,year FROM movies WHERE movieId = %s"  % (movieId)
    # print(selectedmovie)
    results1 = execute_query(db_connection, view_query)
    results2 = execute_query(db_connection, selectedmovie)
    return render_template('view_rating.html', results1=results1, results2=results2)

if __name__ == '__main__':
    app.run(debug=True)


#reference: https://realpython.com/python-web-applications-with-flask-part-ii/