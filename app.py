from flask import Flask, render_template, flash, redirect, url_for, session, request
from db_connector import connect_to_database, execute_query
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField
from passlib.hash import sha256_crypt
from datetime import date

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


# User login
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
        return render_template('dashboard.html',results=rating_result, rows=people_query)

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
    rating = IntegerField('Rating',)

class castForm(Form):
    fname = StringField('First Name', [validators.Length(min=1, max=100)])
    lname = StringField('Last Name', [validators.Length(min=1, max=100)])

class mov_Form(Form):
    movTitle = StringField('Title of Movie', [validators.Length(min=1, max=100)])

class reviewForm(Form):
    rating = IntegerField('Rating', [validators.NumberRange(min=0, max=10)])
    review = StringField('Review', [validators.Length(min=1, max=10000)])

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

@app.route('/add_review/<int:movieId>', methods=['GET', 'POST'])
def add_review(movieId):
    form = reviewForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        rating = form.rating.data
        review = form.review.data
        newReview = "INSERT INTO ratings (movieId, reviewerId, ratingDate, rating, review) VALUES (%s, (SELECT reviewerId FROM reviewers WHERE username = %s), CURDATE(), %s, %s)"
        data = (movieId, [session['username']], rating, review)
        execute_query(db_connection, newReview, data)
        return view_rating(movieId)
    return render_template('add_review.html', form=form)

@app.route('/view_rating/<int:movieId>')
def view_rating(movieId):
    db_connection = connect_to_database()
    view_query = "SELECT reviewers.username,rating,review FROM reviewers inner join ratings ON reviewers.reviewerId = ratings.reviewerId WHERE movieId = %s"  % (movieId)
    # print(view_query)
    selectedmovie = "SELECT title,budget,avgRating,genre,boxOffice,year FROM movies WHERE movieId = %s"  % (movieId)
    # print(selectedmovie)
    results1 = execute_query(db_connection, view_query)
    results2 = execute_query(db_connection, selectedmovie)
    return render_template('view_rating.html', results1=results1, results2=results2, id=movieId)


#Display list of directors
@app.route('/director')
def director():
    db_connection = connect_to_database()
    dir_query = "SELECT directorId, CONCAT(firstName, ' ', lastName) as dir_name FROM directors ORDER BY lastName"
    dir_results = execute_query(db_connection, dir_query).fetchall()
    return render_template('director.html', rows=dir_results)

#Display individual director
@app.route('/director/id=<int:directorId>')
def view_dir(directorId):
    db_connection = connect_to_database()
    view_mov_query = "SELECT movies.movieId, movies.title FROM movies JOIN dir_mov ON movies.movieId = dir_mov.movieId JOIN directors ON dir_mov.directorId = directors.directorId WHERE directors.directorId = %s" % (directorId)
    view_act_query = "SELECT actors.actorId, CONCAT(actors.firstName, ' ', actors.lastName) as act_name FROM actors JOIN dir_act ON actors.actorId = dir_act.actorId LEFT JOIN directors ON dir_act.directorId = directors.directorId WHERE directors.directorId = %s"  % (directorId)
    dirName = "SELECT CONCAT(directors.firstName, ' ', directors.lastName) as dir_name FROM directors WHERE directorId = %s" % (directorId)
    mov_results = execute_query(db_connection, view_mov_query)
    act_results = execute_query(db_connection, view_act_query)
    dir_results = execute_query(db_connection, dirName)
    for rows in dir_results:
        name = rows
    name = name[0]
    return render_template('view_director.html', mov_rows=mov_results, act_rows=act_results, name = name, id = directorId)

# Add Director
@app.route('/add_director', methods=['GET', 'POST'])
def add_director():
    form = castForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        fname = form.fname.data
        lname = form.lname.data
        dir_query = 'INSERT INTO directors (lastName, firstName) VALUES (%s,%s)'
        data = (lname, fname)
        execute_query(db_connection, dir_query, data)
        dirID_query = "SELECT directorId FROM directors WHERE lastName = '%s' AND firstName = '%s'" %(lname, fname)
        result = execute_query(db_connection, dirID_query).fetchall()
        for rows in result:
            dirID = rows
        dirID = dirID[0]
        return view_dir(dirID)

    return render_template('add_director.html', form=form)

# Add Movie to Director's list
@app.route('/add_dir_mov/<int:directorId>', methods=['GET', 'POST'])
def add_dir_mov(directorId):
    form = mov_Form(request.form)
    errorform = MovieForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        movTitle = form.movTitle.data
        dm_query = "INSERT INTO dir_mov (directorId, movieId) VALUES (%s,(SELECT movieID FROM movies WHERE title='%s'))" % (directorId, movTitle)
        try:
            execute_query(db_connection, dm_query)
            return view_act(directorId)
        except:
            return render_template('error_add_movie.html')

    return render_template('add_dir_mov.html', form=form)

#Add actor to director
@app.route('/add_dir_act/<int:directorId>', methods=['GET', 'POST'])
def add_dir_act(directorId):
    form = castForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        fname = form.fname.data
        lname = form.lname.data
        ad_query = "INSERT INTO dir_act (directorId, actorId) VALUES (%s,(SELECT actorId FROM actors WHERE firstName = '%s' AND lastName = '%s'))" % (directorId, fname, lname)
        try:
            execute_query(db_connection, ad_query)
            return view_act(directorId)
        except:
            return render_template('error_add_actor.html')

    return render_template('add_dir_act.html', form=form)

#Display list of actors
@app.route('/actor')
def actor():
    db_connection = connect_to_database()
    act_query = "SELECT actorId, CONCAT(firstName, ' ', lastName) as act_name FROM actors ORDER BY lastName"
    act_results = execute_query(db_connection, act_query).fetchall()
    return render_template('actor.html', rows=act_results)

#Display individual actor
@app.route('/actor/id=<int:actorId>')
def view_act(actorId):
    db_connection = connect_to_database()
    view_mov_query = "SELECT movies.movieId, movies.title FROM movies JOIN act_mov ON movies.movieId = act_mov.movieId JOIN actors ON act_mov.actorId = actors.actorId WHERE actors.actorId = %s ORDER BY movies.year" % (actorId)
    view_dir_query = "SELECT actors.actorId, CONCAT(directors.firstName, ' ', directors.lastName) as dir_name FROM directors JOIN dir_act ON directors.directorId = dir_act.directorId LEFT JOIN actors ON dir_act.actorId = actors.actorId WHERE actors.actorId = %s" % (actorId)
    actName_query = "SELECT CONCAT(actors.firstName, ' ', actors.lastName) as act_name FROM actors WHERE actorId = %s" % (actorId)
    # print(selectedmovie)
    mov_results = execute_query(db_connection, view_mov_query)
    dir_results = execute_query(db_connection, view_dir_query)
    act_results = execute_query(db_connection, actName_query)
    for rows in act_results:
        name = rows
    name = name[0]

    return render_template('view_actor.html', mov_rows=mov_results, dir_rows=dir_results, name=name, id=actorId)

#Add a new actor
@app.route('/add_actor', methods=['GET', 'POST'])
def add_actor():
    form = castForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        fname = form.fname.data
        lname = form.lname.data
        # director = form.director.data
        # actor = form.actor.data

        act_query = 'INSERT INTO actors (lastName, firstName) VALUES (%s,%s)'
        data = (lname, fname)
        execute_query(db_connection, act_query, data)
        actID_query = "SELECT actorId FROM actors WHERE lastName = '%s' AND firstName = '%s'" %(lname, fname)
        result = execute_query(db_connection, actID_query).fetchall()
        for rows in result:
            actID = rows
        actID = actID[0]
        return view_act(actID)

    return render_template('add_actor.html', form=form)

# Add Movie to Actor
@app.route('/add_act_mov/<int:actorId>', methods=['GET', 'POST'])
def add_act_mov(actorId):
    form = mov_Form(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        movTitle = form.movTitle.data
        am_query = "INSERT INTO act_mov (actorId, movieId) VALUES (%s,(SELECT movieID FROM movies WHERE title='%s'))" % (actorId, movTitle)
        try:
            execute_query(db_connection, am_query)
            return view_act(actorId)
        except:
            return render_template('error_add_movie.html')

    return render_template('add_act_mov.html', form=form)

# Add Director to Actor
@app.route('/add_act_dir/<int:actorId>', methods=['GET', 'POST'])
def add_act_dir(actorId):
    form = castForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        fname = form.fname.data
        lname = form.lname.data
        ad_query = "INSERT INTO dir_act (actorId, directorId) VALUES (%s,(SELECT directorId FROM directors WHERE firstName = '%s' AND lastName = '%s'))" % (actorId, fname, lname)
        try:
            execute_query(db_connection, ad_query)
            return view_act(actorId)
        except:
            return render_template('error_add_director.html')


    return render_template('add_act_dir.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)


#reference: https://realpython.com/python-web-applications-with-flask-part-ii/