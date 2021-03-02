from flask import Flask, render_template, flash, redirect, url_for, session, request
from db_connector import connect_to_database, execute_query
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField
from passlib.hash import sha256_crypt
from datetime import date
from functools import wraps

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
        search_query = "SELECT movieId,title,genre,year FROM Movies WHERE title = %s"
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

        query = 'INSERT INTO Reviewers (name,username,email,password) VALUES (%s,%s,%s,%s)'
        data = (name,username,email,password)
        execute_query(db_connection, query, data)

        flash('You have successfully signed up. To continue with the site please log in now')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, heaidng="Create a new account")


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_connection = connect_to_database()
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        people_query = "SELECT * FROM Reviewers WHERE username = %s"
        people_result = execute_query(db_connection,people_query,[username]).fetchone()
        # print(people_result)
        if people_result != None:
            # Get the correct password from databse
            password = people_result[-1]

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))
            else: #password does not match
                error = 'There was a problem, your password is incorrect'
                return render_template('login.html', error=error)
        else:
            error = "Looks like you don't have an account with us, create an account to explore!"
            return render_template('login.html',error=error)

    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please login to continue')
            return redirect(url_for('login'))
    return wrap

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
        people_query = "SELECT reviewerId,name,email FROM Reviewers WHERE username = %s"
        people_result = execute_query(db_connection, people_query,[session['username']]).fetchone()
        print(people_result,people_result[0],people_result[1])

        rating_query = "SELECT Ratings.movieId, title,rating,review,ratingDate FROM Ratings join Movies on Ratings.movieId  = Movies.movieId where reviewerId in (SELECT reviewerId FROM Reviewers WHERE username = %s)"
        rating_result = execute_query(db_connection, rating_query,[session['username']]).fetchall()
        # print(rating_result)
        if rating_result:
            return render_template('dashboard.html',results=rating_result, rows=people_result,form=form)

        return render_template('dashboard.html',rows=people_result,form=form)
    return render_template('dashboard.html',form=form)

# Movie Form Class
#reference: https://flask.palletsprojects.com/en/1.1.x/patterns/wtforms/
#reference: https://wtforms.readthedocs.io/en/2.3.x/fields/
class MovieForm(Form):
    title = StringField('Title',[validators.DataRequired()])
    genre = StringField('Genre',[validators.DataRequired()])
    # release_year = IntegerField('Release year')
    # budget = IntegerField('Budget')
    # box_office = IntegerField('Box office')
    release_year = IntegerField('Release year',[validators.DataRequired()])
    budget = IntegerField('Budget',[validators.DataRequired()])
    box_office = IntegerField('Box office',[validators.DataRequired()])
    firstName = StringField('First name',[validators.DataRequired()])
    lastName = StringField('Last name',[validators.DataRequired()])

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
        movie_query = "SELECT movieId,title,CONCAT('$', FORMAT(budget,'C0')),genre,CONCAT('$', FORMAT(boxOffice,'C0')),year,CONCAT(firstName, ' ', lastName) as dir_name FROM Movies"
        movie_result = execute_query(db_connection,movie_query).fetchall()
        print(movie_result)

        return render_template('movie.html', rows=movie_result,form=form)
    return render_template('movie.html',form=form)

# Add movie
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
        firstName = form.firstName.data
        lastName = form.lastName.data

        movie_query = 'INSERT INTO Movies (title,budget,genre,boxOffice,year,firstName,lastName) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        data_movie = (title,budget,genre,box_office,release_year,firstName,lastName)
        execute_query(db_connection, movie_query, data_movie)

        director_query = 'INSERT INTO Directors (firstName,lastName) VALUES (%s,%s)'
        data_director = (firstName,lastName)
        execute_query(db_connection, director_query, data_director)

        return redirect(url_for('movie'))

    return render_template('add_movie.html', form=form)


# Display user reviews
@app.route('/reviews', methods=['GET', 'POST'])
@is_logged_in
def reviews():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(form)
    else:
        db_connection = connect_to_database()
        rating_query = 'SELECT Ratings.movieId,rating,title,username,ratingDate,review FROM Ratings inner join Movies ON Ratings.movieId = Movies.movieId inner join Reviewers on Reviewers.reviewerId = Ratings.reviewerId'
        # print(rating_query)
        results = execute_query(db_connection, rating_query).fetchall()
        return render_template('reviews.html', rows=results,form=form)
    return render_template('reviews.html', form=form)


@app.route('/view_rating/<int:movieId>')
def view_rating(movieId):
    db_connection = connect_to_database()
    view_query = "SELECT Reviewers.username,rating,review FROM Reviewers inner join Ratings on Reviewers.reviewerId = Ratings.reviewerId WHERE Ratings.movieId = %s"  % (movieId)
    # print(view_query)
    selectedmovie = "SELECT title,CONCAT('$', FORMAT(budget,'C0')),round(avg(rating),1),genre,CONCAT('$', FORMAT(boxOffice,'C0')),year FROM Movies inner join Ratings on Movies.movieId = Ratings.movieId WHERE Movies.movieId = %s"  % (movieId)
    # print(selectedmovie)
    results1 = execute_query(db_connection, view_query)
    results2 = execute_query(db_connection, selectedmovie)
    return render_template('view_rating.html', results1=results1, results2=results2, id=movieId)


@app.route('/add_review/<int:movieId>', methods=['GET', 'POST'])
def add_review(movieId):
    form = reviewForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        rating = form.rating.data
        review = form.review.data
        currentID = 'SELECT reviewerId FROM Reviewers WHERE username=%s'
        people_result = execute_query(db_connection, currentID,[session['username']]).fetchone()
        print(people_result)
       
        insert_reviews = 'INSERT INTO Ratings (movieId, reviewerId, ratingDate, rating, review) VALUES (%s, %s, CURDATE(),%s,%s)'
        reviewdata = (movieId,people_result,rating,review )
        execute_query(db_connection,insert_reviews,reviewdata)
        return view_rating(movieId)
    return render_template('add_review.html', form=form)


#Display list of directors
@app.route('/director', methods=['GET', 'POST'])
def director():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(form)
    else:
        db_connection = connect_to_database()
        dir_query = "SELECT directorId, firstName,lastName FROM Directors ORDER BY lastName"
        dir_results = execute_query(db_connection, dir_query).fetchall()
        print(dir_results[0],dir_results[1],dir_results[2])
        return render_template('director.html', rows=dir_results,form=form)
    return render_template('director.html', form=form)

#Display individual director
@app.route('/director/id=<int:directorId>')
def view_dir(directorId):
    db_connection = connect_to_database()
    view_mov_query = "SELECT movieId,title FROM Movies join Directors on Movies.firstName = Directors.firstName and Movies.lastName = Directors.lastName WHERE Directors.directorId = %s" % (directorId)
    dirName = "SELECT CONCAT(Directors.firstName, ' ', Directors.lastName) as dir_name FROM Directors WHERE Directors.directorId = %s" % (directorId)
    mov_results = execute_query(db_connection, view_mov_query).fetchall()
    print(mov_results)
    dir_results = execute_query(db_connection, dirName)
    for rows in dir_results:
        name = rows
    name = name[0]
    return render_template('view_director.html', mov_rows=mov_results, name = name, id = directorId)


#Display list of actors
@app.route('/actor', methods=['GET', 'POST'])
def actor():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(form)
    else:
        db_connection = connect_to_database()
        act_query = "SELECT actorId, firstName, lastName FROM Actors ORDER BY lastName"
        act_results = execute_query(db_connection, act_query).fetchall()
        return render_template('actor.html', rows=act_results,form=form)
    return render_template('actor.html', form=form)


#Display individual actor
@app.route('/actor/id=<int:actorId>')
def view_act(actorId):
    db_connection = connect_to_database()
    view_mov_query = "SELECT Movies.movieId, Movies.title FROM Movies JOIN ActMovies ON Movies.movieId = ActMovies.movieId JOIN Actors ON ActMovies.actorId = Actors.actorId WHERE Actors.actorId = %s ORDER BY Movies.year" % (actorId)
    view_dir_query = "SELECT Actors.actorId, CONCAT(Directors.firstName, ' ', Directors.lastName) as dir_name FROM Directors JOIN DirActors ON Directors.directorId = DirActors.directorId LEFT JOIN Actors ON DirActors.actorId = Actors.actorId WHERE Actors.actorId = %s" % (actorId)
    actName_query = "SELECT CONCAT(Actors.firstName, ' ', Actors.lastName) as dir_name FROM Actors WHERE actorId = %s" % (actorId)
    mov_results = execute_query(db_connection, view_mov_query)
    dir_results = execute_query(db_connection, view_dir_query)
    print(mov_results)
    print(dir_results)
    act_results = execute_query(db_connection, actName_query)
    for rows in act_results:
        name = rows
        print(name)
    name = name[0]

    return render_template('view_actor.html', mov_rows=mov_results, dir_rows=dir_results, name=name, id=actorId)



# Add Director
@app.route('/add_director', methods=['GET', 'POST'])
def add_director():
    form = castForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        fname = form.fname.data
        lname = form.lname.data
        dir_query = 'INSERT INTO Directors (lastName, firstName) VALUES (%s,%s)'
        data = (lname, fname)
        execute_query(db_connection, dir_query, data)
        dirID_query = "SELECT directorId FROM Directors WHERE lastName = '%s' AND firstName = '%s'" %(lname, fname)
        result = execute_query(db_connection, dirID_query).fetchall()
        for rows in result:
            dirID = rows
        dirID = dirID[0]
        return view_dir(dirID)

    return render_template('add_director.html', form=form)

#Add a new actor
@app.route('/add_actor', methods=['GET', 'POST'])
def add_actor():
    form = castForm(request.form)
    db_connection = connect_to_database()
    if request.method == 'POST':
        fname = form.fname.data
        lname = form.lname.data

        act_query = 'INSERT INTO Actors (lastName, firstName) VALUES (%s,%s)'
        data = (lname, fname)
        execute_query(db_connection, act_query, data)
        actID_query = "SELECT actorId FROM Actors WHERE lastName = '%s' AND firstName = '%s'" %(lname, fname)
        result = execute_query(db_connection, actID_query).fetchall()
        for rows in result:
            actID = rows
        actID = actID[0]
        return view_act(actID)

    return render_template('add_actor.html', form=form)


#Edit movie
@app.route('/edit_movie/<int:movieId>', methods=['GET', 'POST'])
@is_logged_in
def edit_movie(movieId):
    db_connection = connect_to_database()
    select_query = 'SELECT * FROM Movies WHERE movieId = %s' % (movieId)
    select_results = execute_query(db_connection,select_query).fetchone()
    print(select_results)
    
    # Get form
    form = MovieForm(request.form)

    # Populate movies form fields
    form.title.data = select_results[0]
    form.genre.data = select_results[3]
    form.release_year.data = select_results[5]
    form.budget.data = select_results[2]
    form.box_office.data = select_results[4]
    form.firstName.data = select_results[6]
    form.lastName.data = select_results[7]

    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        release_year = request.form['release_year']
        budget = request.form['budget']
        box_office = request.form['box_office']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        budget = int(budget)
        box_office = int(box_office)
        release_year = int(release_year)
    
        mov_query = "UPDATE Movies SET title='%s', budget=%s, genre='%s', boxOffice=%s, year=%s, firstName='%s', lastName='%s' WHERE movieId=%s" % (title, budget, genre, box_office, release_year, firstName,lastName, movieId)
        execute_query(db_connection, mov_query)
        return redirect(url_for('movie'))

    return render_template('edit_movie.html', form=form)



#Edit review
@app.route('/edit_review/<int:movieId>', methods=['GET', 'POST'])
@is_logged_in
def edit_review(movieId):
    db_connection = connect_to_database()
    selectrev_query = 'SELECT rating,review FROM Ratings WHERE movieId = %s' % (movieId)
    selectrev_results = execute_query(db_connection,selectrev_query).fetchall()
    # print(select_results)
    
    # Get form
    review_form = reviewForm(request.form)
    print(selectrev_results)
   
    if request.method == 'POST':
        rating = request.form['rating']
        review = request.form['review']
        print(rating,review)

        currentID = 'SELECT reviewerId FROM Reviewers WHERE username=%s'
        people_result = execute_query(db_connection, currentID,[session['username']]).fetchone()

        test = 'SELECT reviewerID FROM Ratings'
        test_result = execute_query(db_connection,test).fetchone()

        print(people_result,test_result)

        insert_reviewerId = 'INSERT INTO Ratings (reviewerId) VALUES (%s)'
        iddata = (people_result)
        execute_query(db_connection,insert_reviewerId,iddata)
    
        review_query = "UPDATE Ratings SET rating='%s',review='%s' ,ratingDate = NOW() WHERE movieId=%s" % (rating, review, movieId)
        execute_query(db_connection, review_query)
        return redirect(url_for('dashboard'))

    return render_template('edit_review.html', form=review_form)

#Edit director-movie
@app.route('/edit_director_movie/id=<int:movieId>', methods=['GET', 'POST'])
@is_logged_in
def edit_director_movie(movieId):
    db_connection = connect_to_database()
    selectmov_query = 'SELECT title FROM Movies WHERE movieId = %s' % (movieId)
    selectmov_results = execute_query(db_connection,selectmov_query).fetchall()
    # print(select_results)
    
    # Get form
    mov_form = mov_Form(request.form)
    print(selectmov_results)
    # Populate movies form fields
    mov_form.movTitle.data = selectmov_results[0][0]

   
    if request.method == 'POST':
        title = request.form['movTitle']
        print(title)
    
        dirmov_query = "UPDATE Movies SET title='%s' WHERE movieId=%s" % (title, movieId)
        execute_query(db_connection, dirmov_query)
        return redirect(url_for('director'))


    return render_template('edit_director_movie.html', form=mov_form)


# Delete movie
@app.route('/delete_movie/<int:movieId>', methods=['POST'])
@is_logged_in
def delete_movie(movieId):
    db_connection = connect_to_database()
    deldir_query = 'DELETE Directors FROM Directors JOIN Movies ON Directors.firstName=Movies.firstName and Directors.lastName=Movies.lastName WHERE Movies.movieId = %s' % (movieId)
    delmov_query = 'DELETE Movies FROM Movies WHERE movieId = %s' % (movieId)
    execute_query(db_connection,deldir_query)
    execute_query(db_connection,delmov_query)

    return redirect(url_for('movie'))


# Delete director
@app.route('/delete_director/<int:directorId>', methods=['POST'])
@is_logged_in
def delete_director(directorId):
    db_connection = connect_to_database()
    del_inmovie_query = 'DELETE Movies FROM Movies JOIN Directors ON Directors.firstName=Movies.firstName and Directors.lastName=Movies.lastName WHERE Directors.directorId = %s' % (directorId)
    deldir_query = 'DELETE Directors FROM Directors WHERE directorId = %s' % (directorId)
    execute_query(db_connection,del_inmovie_query).fetchall()
    execute_query(db_connection,deldir_query).fetchall()

    return redirect(url_for('director'))


# Delete actor
@app.route('/delete_actor/<int:actorId>', methods=['POST'])
@is_logged_in
def delete_actor(actorId):
    db_connection = connect_to_database()
    delactor_query = 'DELETE FROM Actors WHERE actorId = %s' % (actorId)
    delact_results = execute_query(db_connection,delactor_query).fetchone()

    flash('Actor Deleted')

    return redirect(url_for('actor'))

# Delete actor
@app.route('/delete_review/<int:movidId>', methods=['POST'])
@is_logged_in
def delete_review(movieId):
    db_connection = connect_to_database()
    delreview_query = 'DELETE Ratings FROM Ratings WHERE movieId = %s' % (movieId)
    delreview_results = execute_query(db_connection,delreview_query).fetchone()

    flash('Actor Deleted')

    return redirect(url_for('actor'))

if __name__ == '__main__':
    app.run(debug=True)


#reference: https://realpython.com/python-web-applications-with-flask-part-ii/