                                    -- SIGN UP PAGE

-- -- Query to create a new account:
INSERT INTO reviewers (name, username, email,password) VALUES (:nameInput,:usernameInput,:emailInput,:passwordInput);


-- -- Query to log in:
SELECT * FROM reviewers WHERE username = :usernameInput

-----------------------------------------------------------------------------------------------------
                                    -- MY HOME PAGE

-- get user's id, email,last name, first name to populate the MY HOME page:
SELECT * FROM reviewers;

-- get movies, rating, rating data to populate the MY HOME page:
SELECT title,rating,ratingDate 
FROM ratings 
JOIN movies ON ratings.movieId = movies.movieId 
WHERE ratings.reviewerId IN (SELECT reviewerId FROM reviewers WHERE email = :reviewerLoginInput);


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
FROM movies 
INNER JOIN ratings ON movies.movieId = ratings.movieId
INNER JOIN dir_mov dm ON movies.movieId = dm.movieId
INNER JOIN directors ON dm.directorId = directors.directorId
INNER JOIN act_mov am ON movies.movieId = am.movieId
INNER JOIN actors ON am.actorId = actors.actorId;

-- add a new movie:
INSERT INTO movies (title,budget,genre,boxOffice,year) 
VALUES (:titleInput,:budgetInput,:genreInput,:boxOfficeInput,:yearInput);

INSERT INTO directors (firstName,lastName)
VALUES (:firstnameInput,:lastnameInput);

INSERT INTO actors (firstName,lastName)
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
FROM movies
INNER JOIN dir_mov dm ON movies.movieId = dm.movieId
INNER JOIN directors d ON dm.directorId = d.directorId
INNER JOIN act_mov am ON movies.movieId = am.movieId
INNER JOIN actors a ON am.actorId = a.actorId
WHERE d.firstName LIKE :firstNameSearchParameter
and d.lastName LIKE :lastNameSearchParameter
and title LIKE :movietitleSearchParameter;

-----------------------------------------------------------------------------------------------------
                                    -- REVIEWS page

-- get review, rating to populate the REVIEWS page:
SELECT rating,review FROM ratings
INNER JOIN movies
ON ratings.movieId = movies.movieId
WHERE title = :movietitleFromURL

INSERT INTO ratings (movieId, reviewerId, ratingDate, rating, review) VALUES (?, ?, ?, ?, ?);

UPDATE ratings(
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
SELECT * FROM directors;

INSERT INTO directors (firstName, lastName) VALUES (:fname, :lname);

UPDATE directors SET firstName = :fname, lastName = :lname WHERE directorId = :dID;

DELETE FROM directors WHERE directorId = :dID;

-----------------------------------------------------------------------------------------------------
                                -- INDIVIDUAL DIRECTORS page
SELECT title FROM movies
JOIN dir_mov ON movies.movieId = dir_mov.movieId
JOIN directors ON dir_mov.directorId = directors.directorId
AND directors.directorId = :dID;

SELECT firstName, lastName FROM actors
JOIN dir_act ON directors.directorId = dir_act.directorId
LEFT JOIN directors ON dir_act.directorId = directors.directorId
AND directors.directorId = :dID;

INSERT INTO dir_mov (
    (SELECT directorId FROM directors WHERE directorId = :directorId), 
    (SELECT movieID FROM movies WHERE title=:inputTitle)
);
INSERT INTO dir_act (
    (SELECT directorId FROM directors WHERE directorId = :directorId), 
    (SELECT actorId FROM actors WHERE firstName = :fname AND lastName = :lname)
);

UPDATE dir_mov SET movieId = (SELECT movieID FROM movies WHERE title=:inputTitle) WHERE directorId = :dID;
UPDATE dir_act SET actorId = (SELECT actorId FROM actors WHERE firstName = :fname AND lastName = :lname) WHERE directorId = :dID;

DELETE FROM dir_mov WHERE directorId = :dID AND movieId = (SELECT movieID FROM movies WHERE title=:inputTitle);
DELETE FROM dir_act WHERE directorId = :dID AND actorId = (SELECT actorId FROM actors WHERE firstName = :fname AND lastName = :lname);

-----------------------------------------------------------------------------------------------------
                                    -- ACTORS page
SELECT * FROM actors;

INSERT INTO actors (firstName, lastName) VALUES (:fname, :lname);
UPDATE actors SET firstName = :fname, lastName = :lname;

DELETE FROM actors WHERE actorId = aID;

-----------------------------------------------------------------------------------------------------
                                -- INDIVIDUAL ACTOR page
SELECT title FROM movies
JOIN act_mov ON movies.movieId = act_mov.movieId
JOIN actors ON act_mov.actorID = actors.actorId
AND actors.actorId = aID;

SELECT firstName, lastName FROM directors
JOIN dir_act ON directors.directorId = dir_act.directorId
LEFT JOIN actors ON dir_act.actorID = actors.actorId
AND actors.actorId = aID;

INSERT INTO act_mov (
    (SELECT actorId FROM actors WHERE actorId = :actorId), 
    (SELECT movieID FROM movies WHERE title=:inputTitle)
);
INSERT INTO dir_act (
    (SELECT directorId FROM directors WHERE firstName = :fname AND lastName = :lname), 
    (SELECT actorId FROM actors WHERE actorId = :aID)
);

UPDATE act_mov SET movieId = (SELECT movieID FROM movies WHERE title=:inputTitle) WHERE actorId = ?;
UPDATE dir_act SET directorId = (SELECT directorId FROM directors WHERE firstName = :fname AND lastName = :lname) WHERE actorId = :aID ;

DELETE FROM act_mov WHERE actorId = :aID AND movieId = (SELECT movieID FROM movies WHERE title=:inputTitle);
DELETE FROM dir_act WHERE actorId = :aID AND directorId = (SELECT directorId FROM directors WHERE firstName = :fname AND lastName = :lname);