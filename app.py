from flask import Flask, render_template, flash, redirect, url_for, session, request
from db_connector import connect_to_database, execute_query
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField
from passlib.hash import sha256_crypt
from datetime import date
import os

app = Flask(__name__)
app.secret_key = 'thisissecretdontshare'


# Search Form
class SearchForm(Form):
    title = StringField('')


# Index
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(form)
    return render_template('index.html', form=form)


# endpoint for search
@app.route('/search')
def search_results(search):
    db_connection = connect_to_database()
    form = SearchForm(request.form)
    if request.method == "POST":
        title = request.form['title']
        movie_query = "SELECT movieId FROM Movies WHERE title = '%s'" % title
        actor_query = "SELECT actorId FROM Actors WHERE CONCAT(firstName, ' ', lastName) like '%s'" % title
        director_query = "SELECT directorId FROM Directors WHERE CONCAT(firstName, ' ', lastName) like '%s'" % title
        movie_results = execute_query(db_connection, movie_query).fetchone()
        actor_results = execute_query(db_connection, actor_query).fetchone()
        director_results = execute_query(db_connection, director_query).fetchone()
        # print(search_results)
        if movie_results:  # display results
            return redirect(url_for('view_rating', movieId=movie_results[0]))
        if actor_results:  # display results
            return redirect(url_for('view_act', actorId=actor_results[0]))
        if director_results:  # display results
            return redirect(url_for('view_dir', directorId=director_results[0]))
        else:
            flash('No results found! You can help others by adding it')
            return redirect(url_for('add_movie'))


# Register Form
# reference: https://flask.palletsprojects.com/en/1.1.x/patterns/wtforms/
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

        #check if username is already in database
        check_query = "SELECT reviewerId FROM Reviewers WHERE username='%s'" % username
        check = execute_query(db_connection, check_query).fetchone()
        if check:
            error = "Username already taken!"
            flash(error)
        else:
            query = 'INSERT INTO Reviewers (name,username,email,password) VALUES (%s,%s,%s,%s)'
            data = (name, username, email, password)
            execute_query(db_connection, query, data)

            flash('You have successfully signed up. To continue with the site please log in now')
            return redirect(url_for('login'))
    return render_template('register.html', form=form, heaidng="Create a new account")


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    db_connection = connect_to_database()
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        people_query = "SELECT * FROM Reviewers WHERE username = %s"
        people_result = execute_query(db_connection, people_query, [username]).fetchone()
        # print(people_result)
        if people_result != None:
            # Get the correct password from databse
            password = people_result[-1]

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('Welcome')
                return redirect(url_for('dashboard'))
            else:  # password does not match
                error = 'There was a problem, your password is incorrect'
                return render_template('login.html', error=error)
        else:
            error = "Looks like you don't have an account with us, create an account to explore!"
            return render_template('login.html', error=error)

    return render_template('login.html')


# Logout
@app.route('/logout')
def signout():
    session.clear()
    flash('You are now signed out')
    return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(form)
    else:
        db_connection = connect_to_database()
        people_query = "SELECT name,email FROM Reviewers WHERE username = %s"
        people_result = execute_query(db_connection, people_query, [session['username']]).fetchone()
        # print(people_result,people_result[0],people_result[1])
        print(session['username'])
        rating_query = "SELECT title,rating,review,ratingDate, Ratings.movieId FROM Ratings inner join Movies on Ratings.movieId  = Movies.movieId where reviewerId in (SELECT reviewerId FROM Reviewers WHERE username = %s)"
        rating_result = execute_query(db_connection, rating_query, [session['username']]).fetchall()
        # print(rating_result)
        if rating_result:
            return render_template('dashboard.html', results=rating_result, rows=people_result, form=form)

        return render_template('dashboard.html', rows=people_result, form=form)


@app.route('/up_user', methods=['POST'])
def up_user():
    db_connection = connect_to_database()
    form = RegisterForm(request.form)
    select_query = "SELECT * FROM Reviewers WHERE username='%s'" % (session['username'])
    results = execute_query(db_connection, select_query).fetchone()
    form.name.data = results[1]
    form.username.data = results[2]
    form.email.data = results[3]
    if request.method == 'POST' and form.validate():
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = sha256_crypt.encrypt(str(form.password.data))

        #check if username is already in database
        check_query = "SELECT reviewerId FROM Reviewers WHERE username='%s'" % username
        check = execute_query(db_connection, check_query).fetchone()
        if check:
            error = "Username already taken!"
            flash(error)
        else:
            query = "UPDATE Reviewers SET name=%s, username=%s, email=%s, password=%s WHERE reviewerId = (SELECT reviewerId FROM Reviewers WHERE username=%s)"
            data = (name, username, email, password, session['username'])
            execute_query(db_connection, query, data)
            session['username'] = username
            flash('You have successfully updated your information')
            return redirect(url_for('dashboard'))
    return render_template('register.html', form=form, heading="Update your information")

@app.route('/del_user', methods=['POST'])
def del_user():
    username = request.form['user']
    rev_query = "DELETE FROM Reviewers WHERE reviewerId=(SELECT reviewerId FROM Reviewers WHERE username='%s')" % (
        username)
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, rev_query)
        return redirect(url_for('signout'))
    except:
        print('did not work')
        print('username: ', request.form['user'])
        return redirect(request.referrer)

# Movie Form Class
# reference: https://flask.palletsprojects.com/en/1.1.x/patterns/wtforms/
# reference: https://wtforms.readthedocs.io/en/2.3.x/fields/
class MovieForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=100)])
    genre = StringField('Genre', [validators.Length(min=1, max=100)])
    release_year = IntegerField('Release year')
    budget = IntegerField('Budget')
    box_office = IntegerField('Box office')

class castForm(Form):
    fname = StringField('First Name', [validators.Length(min=1, max=100)])
    lname = StringField('Last Name', [validators.Length(min=1, max=100)])

class mov_Form(Form):
    movTitle = StringField('Title of Movie', [validators.Length(min=1, max=100)])

class reviewForm(Form):
    rating = IntegerField('Rating', [validators.NumberRange(min=0, max=10)])
    review = StringField('Review', [validators.Length(min=1, max=10000)])

# Movies
@app.route('/movie', methods=['GET', 'POST'])
def movie():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(form)
    else:
        db_connection = connect_to_database()
        movie_query = "SELECT movieId,title,CONCAT('$', FORMAT(budget,'C0')),genre,CONCAT('$', FORMAT(boxOffice,'C0')),year FROM Movies"
        movie_result = execute_query(db_connection, movie_query).fetchall()
        print(movie_result)

        return render_template('movie.html', rows=movie_result, form=form)
    return render_template('movie.html', form=form)


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

        #check if movie is already in database
        check_query = "SELECT movieId FROM Movies WHERE title='%s'" % (title)
        check = execute_query(db_connection, check_query).fetchone()
        if check:
            return redirect(url_for('view_rating', movieId=check[0]))

        movie_query = 'INSERT INTO Movies (title,budget,genre,boxOffice,year) VALUES (%s,%s,%s,%s,%s)'
        data = (title, budget, genre, box_office, release_year)
        execute_query(db_connection, movie_query, data)

        return redirect(url_for('movie'))

    return render_template('add_movie.html', form=form)

# Update movie
@app.route('/up_mov', methods=['POST'])
def up_mov():
    movID = request.form['movID']
    movie = request.form.get('movie')
    budget = request.form.get('budget')
    genre = request.form.get('genre')
    box = request.form.get('box')
    year = request.form.get('year')
    budget = int(budget.replace('$', '').replace(",", ""))
    box = int(box.replace('$', '').replace(",", ""))
    year = int(year)
    mov_query = "UPDATE Movies SET title='%s', budget=%s, genre='%s', boxOffice=%s, year=%s WHERE movieId=%s" % (
    movie, budget, genre, box, year, movID)
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, mov_query)
        return redirect(request.referrer)
    except:
        print("did not work")
        return redirect(request.referrer)

# Display user reviews
@app.route('/reviews', methods=['GET', 'POST'])
def user_reviews():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(form)
    else:
        db_connection = connect_to_database()
        rating_query = 'SELECT Ratings.movieId,rating,title,username,ratingDate,review FROM Ratings inner join Movies ON Ratings.movieId = Movies.movieId inner join Reviewers on Reviewers.reviewerId = Ratings.reviewerId'
        # print(rating_query)
        results = execute_query(db_connection, rating_query).fetchall()
        return render_template('reviews.html', rows=results, form=form)
    return render_template('reviews.html', form=form)

# add a new review
@app.route('/add_review/<int:movieId>', methods=['GET', 'POST'])
def add_review(movieId):
    form = reviewForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        rating = form.rating.data
        review = form.review.data
        user_query = "SELECT reviewerId FROM Reviewers WHERE username='%s'" % (session['username'])
        user_result = execute_query(db_connection, user_query).fetchone()
        print(user_result[0])
        newReview = "INSERT INTO Ratings (movieId, reviewerId, ratingDate, rating, review) VALUES (%s, %s, CURDATE(), %s, %s)"
        data = (movieId, user_result[0], rating, review)
        execute_query(db_connection, newReview, data)
        return redirect(url_for('view_rating', movieId=movieId))
    return render_template('add_review.html', form=form)

# view ratings of individual movie
@app.route('/view_rating/<int:movieId>')
def view_rating(movieId):
    db_connection = connect_to_database()
    view_query = "SELECT Reviewers.username,rating,review, Ratings.movieId FROM Reviewers inner join Ratings on Reviewers.reviewerId = Ratings.reviewerId WHERE Ratings.movieId = %s" % (
        movieId)
    selectedmovie = "SELECT title,CONCAT('$', FORMAT(budget,'C0')),round(avg(rating),1),genre,CONCAT('$', FORMAT(boxOffice,'C0')),year FROM Movies inner join Ratings on Movies.movieId = Ratings.movieId WHERE Movies.movieId = %s" % (
        movieId)

    results1 = execute_query(db_connection, view_query)
    results2 = execute_query(db_connection, selectedmovie)
    return render_template('view_rating.html', results1=results1, results2=results2, id=movieId)

# Delete Review
@app.route('/del_rev', methods=['POST'])
def del_rev():
    movieId = int(request.form['mov'])
    rev_query = "DELETE FROM Ratings WHERE movieId=%s and reviewerId=(SELECT reviewerId FROM Reviewers WHERE username='%s')" % (
    movieId, session['username'])
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, rev_query)
        return redirect(request.referrer)
    except:
        print('did not work')
        print('movieID: ', request.form['mov'])
        print('username: ', request.form['user'])
        return redirect(request.referrer)

# Update Review
@app.route('/up_rev', methods=['POST'])
def up_rev():
    movieID = request.form['movieID']
    rating = request.form['rating']
    review = request.form['review']

    rev_query = "UPDATE Ratings SET rating=%s, ratingDate=CURDATE(), review='%s' WHERE movieId=%s AND reviewerId=(SELECT reviewerId FROM Reviewers WHERE username='%s')" % (
    rating, review, movieID, session['username'])
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, rev_query)
        return redirect(request.referrer)
    except:
        print("did not work")
        return redirect(request.referrer)

# Display list of directors
@app.route('/director', methods=['GET', 'POST'])
def director():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(form)
    else:
        db_connection = connect_to_database()
        dir_query = "SELECT directorId, firstName, lastName as dir_name FROM Directors ORDER BY lastName"
        dir_results = execute_query(db_connection, dir_query).fetchall()
        return render_template('director.html', rows=dir_results, form=form)
    return render_template('director.html', form=form)

# Display individual director
@app.route('/director/id=<int:directorId>')
def view_dir(directorId):
    db_connection = connect_to_database()
    view_mov_query = "SELECT Movies.movieId, Directors.directorId, Movies.title FROM Movies JOIN DirMovies ON Movies.movieId = DirMovies.movieId JOIN Directors ON DirMovies.directorId = Directors.directorId WHERE Directors.directorId = %s" % (
        directorId)
    view_act_query = "SELECT Actors.actorId, CONCAT(Actors.firstName, ' ', Actors.lastName) as act_name FROM Actors JOIN DirActors ON Actors.actorId = DirActors.actorId LEFT JOIN Directors ON DirActors.directorId = Directors.directorId WHERE Directors.directorId = %s" % (
        directorId)
    dirName = "SELECT CONCAT(Directors.firstName, ' ', Directors.lastName) as dir_name FROM Directors WHERE directorId = %s" % (
        directorId)
    mov_results = execute_query(db_connection, view_mov_query)
    act_results = execute_query(db_connection, view_act_query)
    dir_results = execute_query(db_connection, dirName)
    for rows in dir_results:
        name = rows
    name = name[0]
    return render_template('view_director.html', mov_rows=mov_results, act_rows=act_results, name=name, id=directorId)

# Add Director
@app.route('/add_director', methods=['GET', 'POST'])
def add_director():
    form = castForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        fname = form.fname.data
        lname = form.lname.data

        #check if director is already in database
        check_query = "SELECT directorId FROM Directors WHERE firstName='%s' AND lastName='%s'" % (fname, lname)
        check = execute_query(db_connection, check_query).fetchone()
        if check:
            return redirect(url_for('view_dir', directorId=check[0]))

        dir_query = 'INSERT INTO Directors (lastName, firstName) VALUES (%s,%s)'
        data = (lname, fname)
        execute_query(db_connection, dir_query, data)
        dirID_query = "SELECT directorId FROM Directors WHERE lastName = '%s' AND firstName = '%s'" % (lname, fname)
        result = execute_query(db_connection, dirID_query).fetchall()
        for rows in result:
            dirID = rows
        dirID = dirID[0]
        return redirect(url_for('view_dir', directorId=dirID))

    return render_template('add_director.html', form=form)

# Add Movie to Director's list
@app.route('/add_dir_mov/<int:directorId>', methods=['GET', 'POST'])
def add_dir_mov(directorId):
    form = mov_Form(request.form)
    db_connection = connect_to_database()
    mov_query = "SELECT title, movieId FROM Movies ORDER BY title"
    movies = execute_query(db_connection, mov_query).fetchall()
    if request.method == 'POST':
        movieId = request.form['movie']

        #check if relationship already exists
        check_query = "SELECT movieId FROM DirMovies WHERE movieId=%s" % (movieId)
        check = execute_query(db_connection, check_query).fetchone()
        if check:
            return redirect(url_for('view_dir', directorId=directorId))

        dm_query = "INSERT INTO DirMovies (directorId, movieId) VALUES (%s,%s)" % (directorId, movieId)
        try:
            execute_query(db_connection, dm_query)
            return redirect(url_for('view_dir', directorId=directorId))
        except:
            return render_template('error_add_movie.html')

    return render_template('add_dir_mov.html', form=form, movies=movies)

# Add actor to director
@app.route('/add_dir_act/<int:directorId>', methods=['GET', 'POST'])
def add_dir_act(directorId):
    form = castForm(request.form)
    db_connection = connect_to_database()
    act_query= "SELECT CONCAT(firstName, ' ', lastName), actorId FROM Actors ORDER BY lastName"
    actors = execute_query(db_connection, act_query).fetchall()
    if request.method == 'POST':
        actorId = request.form['actors']

        # check if relationship already exists
        check_query = "SELECT actorId FROM DirActors WHERE actorId=%s AND directorId=%s" % (actorId, directorId)
        check = execute_query(db_connection, check_query).fetchone()
        if check:
            return redirect(url_for('view_act', actorId=actorId))

        ad_query = "INSERT INTO DirActors (actorId, directorId) VALUES (%s,%s)" % (actorId, directorId)
        try:
            execute_query(db_connection, ad_query)
            return redirect(url_for('view_dir', directorId=directorId))
        except:
            return render_template('error_add_actor.html')

    return render_template('add_dir_act.html', form=form, actors=actors)

# Delete Director
@app.route('/del_dir', methods=['POST'])
def del_dir():
    dir_query = "DELETE FROM Directors WHERE directorId=%s" % (request.form['dir'])
    act_query = "DELETE FROM DirActors WHERE directorId=%s" % (request.form['dir'])
    mov_query = "DELETE FROM DirMovies WHERE directorId=%s" % (request.form['dir'])
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, dir_query)
        execute_query(db_connection, act_query)
        execute_query(db_connection, mov_query)
        return redirect(request.referrer)
    except:
        return redirect(request.referrer)

# Delete Actor from Director
@app.route('/director/del_act_dir', methods=['POST'])
def del_act_dir():
    ad_query = "DELETE FROM DirActors WHERE directorId=%s and actorId=%s" % (request.form['dir'], request.form['act'])
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, ad_query)
        return redirect(request.referrer)
    except:
        return redirect(request.referrer)

# Update Director
@app.route('/up_dir', methods=['POST'])
def up_dir():
    dirID = request.form['dirID']
    fname = request.form['fname']
    lname = request.form['lname']
    dir_query = "UPDATE Directors SET firstName='%s', lastName='%s' WHERE directorId=%s" % (fname, lname, dirID)
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, dir_query)
        return redirect(request.referrer)
    except:
        print("did not work")
        return redirect(request.referrer)

# Display list of actors
@app.route('/actor', methods=['GET', 'POST'])
def actor():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(form)
    else:
        db_connection = connect_to_database()
        act_query = "SELECT actorId, firstName, lastName FROM Actors ORDER BY lastName"
        act_results = execute_query(db_connection, act_query).fetchall()
        return render_template('actor.html', rows=act_results, form=form)

# Display individual actor
@app.route('/actor/id=<int:actorId>')
def view_act(actorId):
    db_connection = connect_to_database()
    view_mov_query = "SELECT Movies.movieId, Actors.actorId, Movies.title FROM Movies JOIN ActMovies ON Movies.movieId = ActMovies.movieId JOIN Actors ON ActMovies.actorId = Actors.actorId WHERE Actors.actorId = %s ORDER BY Movies.year" % (
        actorId)

    view_dir_query = "SELECT Directors.directorId, Actors.actorId, CONCAT(Directors.firstName, ' ', Directors.lastName) as dir_name FROM Directors JOIN DirActors ON Directors.directorId = DirActors.directorId LEFT JOIN Actors ON DirActors.actorId = Actors.actorId WHERE Actors.actorId = %s" % (
        actorId)
    actName_query = "SELECT CONCAT(Actors.firstName, ' ', Actors.lastName) as act_name FROM Actors WHERE actorId = %s" % (
        actorId)

    mov_results = execute_query(db_connection, view_mov_query)
    dir_results = execute_query(db_connection, view_dir_query)
    act_results = execute_query(db_connection, actName_query)
    for rows in act_results:
        name = rows
    name = name[0]

    return render_template('view_actor.html', mov_rows=mov_results, dir_rows=dir_results, name=name, id=actorId)

# Add a new actor
@app.route('/add_actor', methods=['GET', 'POST'])
def add_actor():
    form = castForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        fname = form.fname.data
        lname = form.lname.data

        #check if actor already in database
        check_query = "SELECT actorId FROM Actors WHERE firstName='%s' AND lastName='%s'" % (fname, lname)
        check = execute_query(db_connection, check_query).fetchone()
        if check:
            return redirect(url_for('view_act', actorId=check[0]))

        act_query = 'INSERT INTO Actors (lastName, firstName) VALUES (%s,%s)'
        data = (lname, fname)
        execute_query(db_connection, act_query, data)
        actID_query = "SELECT actorId FROM Actors WHERE lastName = '%s' AND firstName = '%s'" % (lname, fname)
        result = execute_query(db_connection, actID_query).fetchall()
        for rows in result:
            actID = rows
        actID = actID[0]
        return redirect(url_for('view_act', actorId=actID))

    return render_template('add_actor.html', form=form)

# Add Movie to Actor
@app.route('/add_act_mov/<int:actorId>', methods=['GET', 'POST'])
def add_act_mov(actorId):
    form = mov_Form(request.form)
    db_connection = connect_to_database()
    mov_query = "SELECT title, movieId FROM Movies ORDER BY title"
    movies = execute_query(db_connection, mov_query).fetchall()
    if request.method == 'POST':
        movieId = request.form['movie']

        # check if relationship already exists
        check_query = "SELECT movieId FROM ActMovies WHERE actorId=%s AND movieId=%s" % (actorId, movieId)
        check = execute_query(db_connection, check_query).fetchone()
        if check:
            return redirect(url_for('view_act', actorId=actorId))

        am_query = "INSERT INTO ActMovies (actorId, movieId) VALUES (%s, %s)" % (actorId, movieId)
        try:
            execute_query(db_connection, am_query)
            return redirect(url_for('view_act', actorId=actorId))
        except:
            return render_template('error_add_movie.html')

    return render_template('add_act_mov.html', form=form, movies=movies)


# Add Director to Actor
@app.route('/add_act_dir/<int:actorId>', methods=['GET', 'POST'])
def add_act_dir(actorId):
    form = castForm(request.form)
    db_connection = connect_to_database()
    dir_query = "SELECT CONCAT(firstName, ' ', lastName), directorId FROM Directors ORDER BY lastName"
    directors = execute_query(db_connection, dir_query).fetchall()
    if request.method == 'POST':
        directorId = request.form['directors']

        # check if relationship already exists
        check_query = "SELECT directorId FROM DirActors WHERE actorId=%s AND directorId=%s" % (actorId, directorId)
        check = execute_query(db_connection, check_query).fetchone()
        if check:
            return redirect(url_for('view_act', actorId=actorId))

        ad_query = "INSERT INTO DirActors (actorId, directorId) VALUES (%s, %s)" % (actorId, directorId)
        try:
            execute_query(db_connection, ad_query)
            return redirect(url_for('view_act', actorId=actorId))
        except:
            return render_template('error_add_director.html')

    return render_template('add_act_dir.html', form=form, directors=directors)


# Delete Director from Actor
@app.route('/actor/del_act_dir', methods=['POST'])
def del_dir_act():
    ad_query = "DELETE FROM DirActors WHERE directorId=%s and actorId=%s" % (request.form['dir'], request.form['act'])
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, ad_query)
        return redirect(request.referrer)
    except:
        return redirect(request.referrer)


# Delete Movie from Actor
@app.route('/actor/del_mov_act', methods=['POST'])
def del_mov_act():
    ad_query = "DELETE FROM ActMovies WHERE movieId=%s and actorId=%s" % (request.form['mov'], request.form['act'])
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, ad_query)
        return redirect(request.referrer)
    except:
        return redirect(request.referrer)


# Delete Movie from Director
@app.route('/director/del_mov_dir', methods=['POST'])
def del_mov_dir():
    ad_query = "DELETE FROM DirMovies WHERE movieId=%s and directorId=%s" % (request.form['mov'], request.form['dir'])
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, ad_query)
        return redirect(request.referrer)
    except:
        return redirect(request.referrer)


# Delete Movie
@app.route('/del_mov', methods=['POST'])
def del_mov():
    mov_query = "DELETE FROM Movies WHERE movieId=%s" % (request.form['mov'])
    dir_query = "DELETE FROM DirMovies WHERE movieId=%s" % (request.form['mov'])
    act_query = "DELETE FROM ActMovies WHERE movieId=%s" % (request.form['mov'])
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, mov_query)
        execute_query(db_connection, dir_query)
        execute_query(db_connection, act_query)
        return redirect(request.referrer)
    except:
        return redirect(request.referrer)


# Delete Actor
@app.route('/del_act', methods=['POST'])
def del_act():
    act_query = "DELETE FROM Actors WHERE actorId=%s" % (request.form['act'])
    dir_query = "DELETE FROM DirActors WHERE actorId=%s" % (request.form['act'])
    mov_query = "DELETE FROM ActMovies WHERE actorId=%s" % (request.form['act'])
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, act_query)
        execute_query(db_connection, dir_query)
        execute_query(db_connection, mov_query)
        return redirect(request.referrer)
    except:
        return redirect(request.referrer)


# Update Actor
@app.route('/up_act', methods=['POST'])
def up_act():
    actID = request.form['actID']
    fname = request.form['fname']
    lname = request.form['lname']
    act_query = "UPDATE Actors SET firstName='%s', lastName='%s' WHERE actorId=%s" % (fname, lname, actID)
    db_connection = connect_to_database()
    try:
        execute_query(db_connection, act_query)
        return redirect(request.referrer)
    except:
        print("did not work")
        return redirect(request.referrer)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6924))
    app.run(port=port, debug=True)

# reference: https://realpython.com/python-web-applications-with-flask-part-ii/