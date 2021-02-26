                                    -- SIGN UP PAGE

-- -- Query to create a new account:
INSERT INTO Reviewers (name, username, email,password) VALUES (:nameInput,:usernameInput,:emailInput,:passwordInput);


-- -- Query to log in:
SELECT * FROM Reviewers WHERE username = :usernameInput

-----------------------------------------------------------------------------------------------------
                                    -- MY HOME PAGE

-- get user's id, email,last name, first name to populate the MY HOME page:
SELECT * FROM Reviewers;

-- get movies, rating, rating data to populate the MY HOME page:
SELECT title,rating,ratingDate 
FROM Ratings 
JOIN Movies ON Ratings.movieId = Movies.movieId 
WHERE Ratings.reviewerId IN (SELECT reviewerId FROM Reviewers WHERE email = :reviewerLoginInput);


-----------------------------------------------------------------------------------------------------
                                    -- MOVIES PAGE

-- get rating, director, boxoffice, budget, genre, year, title, actor to populate the MOVIES page:
SELECT
rating as Ratings, 
directors.firstName, 
directors.lastName, 
boxOffice, 
budget as Budget, 
genre as Genre, 
year as Year, 
title as Title, 
actors.firstName, 
actors.LastName
FROM Movies 
INNER JOIN Ratings ON movies.movieId = ratings.movieId
INNER JOIN DirMovies dm ON movies.movieId = dm.movieId
INNER JOIN Directors ON dm.directorId = directors.directorId
INNER JOIN ActMovies am ON movies.movieId = am.movieId
INNER JOIN Actors ON am.actorId = actors.actorId;

-- add a new movie:
INSERT INTO Movies (title,budget,genre,boxOffice,year) 
VALUES (:titleInput,:budgetInput,:genreInput,:boxOfficeInput,:yearInput);

INSERT INTO Directors (firstName,lastName)
VALUES (:firstnameInput,:lastnameInput);

INSERT INTO Actors (firstName,lastName)
VALUES (:firstnameInput,:lastnameInput);

-- display movie when a user searchs for movie title or director:

SELECT
rating as Ratings, 
d.firstName, 
d.lastName, 
boxOffice, 
budget as Budget, 
genre as Genre, 
year as Year, 
title as Title, 
a.firstName, 
a.lastName
FROM Movies
INNER JOIN DirMovies dm ON movies.movieId = dm.movieId
INNER JOIN Directors d ON dm.directorId = d.directorId
INNER JOIN ActMovies am ON movies.movieId = am.movieId
INNER JOIN Actors a ON am.actorId = a.actorId
WHERE d.firstName LIKE :firstNameSearchParameter
and d.lastName LIKE :lastNameSearchParameter
and title LIKE :movietitleSearchParameter;

-----------------------------------------------------------------------------------------------------
                                    -- REVIEWS page

-- get review, rating to populate the REVIEWS page:
SELECT rating,review FROM Ratings
INNER JOIN Movies
ON Ratings.movieId = Movies.movieId
WHERE title = :movietitleFromURL

INSERT INTO Ratings (movieId, reviewerId, ratingDate, rating, review) VALUES (?, ?, ?, ?, ?);

UPDATE Ratings(
    movieId, 
    reviewerId, 
    ratingDate, 
    rating, 
    review
) 
SET
    movieId = ?, 
    reviewerId = ?, 
    ratingDate = ?, 
    rating = ?, 
    review = ?
WHERE  
    ratings_unique = ?
;
-----------------------------------------------------------------------------------------------------
                                    -- DIRECTORS page
SELECT * FROM Directors;

INSERT INTO Directors (firstName, lastName) VALUES (:fname, :lname);

UPDATE Directors SET firstName = :fname, lastName = :lname WHERE directorId = :dID;

DELETE FROM Directors WHERE directorId = :dID;

-----------------------------------------------------------------------------------------------------
                                -- INDIVIDUAL DIRECTORS page
SELECT title FROM Movies
JOIN DirMovies ON Movies.movieId = DirMovies.movieId
JOIN Directors ON DirMovies.directorId = Directors.directorId
AND Directors.directorId = :dID;

SELECT firstName, lastName FROM Actors
JOIN Directors ON Directors.directorId = DirActors.directorId
LEFT JOIN Directors ON DirActors.directorId = Directors.directorId
AND Directors.directorId = :dID;

INSERT INTO DirMovies (
    (SELECT directorId FROM Directors WHERE directorId = :directorId), 
    (SELECT movieID FROM Movies WHERE title=:inputTitle)
);
INSERT INTO DirActors (
    (SELECT directorId FROM Directors WHERE directorId = :directorId), 
    (SELECT actorId FROM Actors WHERE firstName = :fname AND lastName = :lname)
);

UPDATE DirMovies SET movieId = (SELECT movieID FROM Movies WHERE title=:inputTitle) WHERE directorId = :dID;
UPDATE DirActors SET actorId = (SELECT actorId FROM Actors WHERE firstName = :fname AND lastName = :lname) WHERE directorId = :dID;

DELETE FROM DirMovies WHERE directorId = :dID AND movieId = (SELECT movieID FROM Movies WHERE title=:inputTitle);
DELETE FROM DirActors WHERE directorId = :dID AND actorId = (SELECT actorId FROM Actors WHERE firstName = :fname AND lastName = :lname);

-----------------------------------------------------------------------------------------------------
                                    -- ACTORS page
SELECT * FROM Actors;

INSERT INTO Actors (firstName, lastName) VALUES (:fname, :lname);
UPDATE Actors SET firstName = :fname, lastName = :lname;

DELETE FROM Actors WHERE actorId = aID;

-----------------------------------------------------------------------------------------------------
                                -- INDIVIDUAL ACTOR page
SELECT title FROM Movies
JOIN ActMovies ON Movies.movieId = ActMovies.movieId
JOIN Actors ON ActMovies.actorID = Actors.actorId
AND Actors.actorId = aID;

SELECT firstName, lastName FROM Directors
JOIN DirActors ON Directors.directorId = DirActors.directorId
LEFT JOIN Actors ON DirActors.actorID = Actors.actorId
AND Actors.actorId = aID;

INSERT INTO ActorMovies (
    (SELECT actorId FROM Actors WHERE actorId = :actorId), 
    (SELECT movieID FROM Movies WHERE title=:inputTitle)
);
INSERT INTO DirActors (
    (SELECT directorId FROM Directors WHERE firstName = :fname AND lastName = :lname), 
    (SELECT actorId FROM Actors WHERE actorId = :aID)
);

UPDATE ActMovies SET movieId = (SELECT movieID FROM Movies WHERE title=:inputTitle) WHERE actorId = ?;
UPDATE DirActors SET directorId = (SELECT directorId FROM Directors WHERE firstName = :fname AND lastName = :lname) WHERE actorId = :aID ;

DELETE FROM ActMovies WHERE actorId = :aID AND movieId = (SELECT movieID FROM Movies WHERE title=:inputTitle);
DELETE FROM DirActors WHERE actorId = :aID AND directorId = (SELECT directorId FROM Directors WHERE firstName = :fname AND lastName = :lname);