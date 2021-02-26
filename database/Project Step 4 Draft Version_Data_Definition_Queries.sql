-- MySQL dump 10.13  Distrib 5.1.66, for redhat-linux-gnu (x86_64)
--
-- Host: classmysql.engr.oregonstate.edu/    Database: cs340_wangjin3
-- ------------------------------------------------------
-- Server version	5.1.65-community-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


--
-- Table structure for table `reviewers`
--

DROP TABLE IF EXISTS `reviewers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reviewers` (
  `reviewerId` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(100),
  PRIMARY KEY (`reviewerid`),
  UNIQUE KEY `reviewerId` (`reviewerId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviewers`
--

LOCK TABLES `reviewers` WRITE;
/*!40000 ALTER TABLE `reviewers` DISABLE KEYS */;
INSERT INTO `reviewers` VALUES 
(1,'Adams Sean','sean','sadams@gmail.com','111'),
(2,'Banks Colin','colin','cbanks@aol.com','222'),
(3,'Casto Taylor','taylor','tcasto@outlook.com','333'),
(4,'Davis Jake','jake','jdavis@gmail.com','444'),
(5,'Elmer Shelby','shelby','selmer@icloud.com','555'),
(6,'Forbes Arielle','arielle','aforbes@outlook.com','666');
/*!40000 ALTER TABLE `reviewers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movies`
--

DROP TABLE IF EXISTS `movies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `movies` (
  `title` varchar(100) NOT NULL,
  `movieId` int(11) NOT NULL AUTO_INCREMENT,
  `budget` bigint(20) DEFAULT NULL,
  `avgRating` decimal(2,1) DEFAULT NULL,
  `genre` varchar(50) NOT NULL,
  `boxOffice` bigint(20) DEFAULT NULL,
  `year` int(11) NOT NULL,
  PRIMARY KEY (`movieid`),
  UNIQUE KEY `movieId` (`movieId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movies`
--

LOCK TABLES `movies` WRITE;
/*!40000 ALTER TABLE `movies` DISABLE KEYS */;
INSERT INTO `movies` VALUES 
('Soul',2948372,NULL,8.1,'animation,adventure,comedy',96200000,2020),
('Hamilton',8503618,40000000,8.5,'animation,adventure,comedy',NULL,2019),
('1917',8579674,95000000,8.2,'drama,thriller,war',384877547,2019),
('Joker',7286456,55000000,8.2,'crime,drama,thriller',1074251311,2019),
('Avengers: Endgame',4154796,356000000,8.4,'action,adventure,drama',2797800564,2019),
('Andhadhun',4500000,356000000,8.3,'crime,drama,music',62475342,2018);
/*!40000 ALTER TABLE `movies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratings`
--

DROP TABLE IF EXISTS `ratings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratings` (
  `movieId` int(11) NOT NULL AUTO_INCREMENT,
  `reviewerId` int(11) NOT NULL,
  `ratingDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `rating` decimal(2,1) DEFAULT NULL,
  `review` varchar(255) DEFAULT NULL,
  UNIQUE KEY `ratings_unique` (`movieId`,`reviewerId`),
  KEY `ratings_fk_movie` (`movieId`),
  KEY `ratings_fk_reviewer` (`reviewerId`),
  CONSTRAINT `ratings_fk_movie` FOREIGN KEY (`movieId`) REFERENCES `movies` (`movieId`) ON UPDATE CASCADE,
  CONSTRAINT `ratings_fk_reviewer` FOREIGN KEY (`reviewerId`) REFERENCES `reviewers` (`reviewerId`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratings`
--

LOCK TABLES `ratings` WRITE;
/*!40000 ALTER TABLE `ratings` DISABLE KEYS */;
INSERT INTO `ratings` VALUES 
(2948372,1,'2020-02-15 13:32:42',8.0,'Just do yourself a favour and watch it, it is unmissable.'),
(8503618,2,'2020-03-10 3:40:32',7.0,'Awesome screenplay Good story written Awesome acting'),
(8579674,3,'2020-04-20 12:03:22',8.0,'This movie is a perfect example of how you can tell a nail-consuming thriller in a comedic way'),
(7286456,4,'2020-05-31 15:10:12',9.0,'It is a very good movie'),
(4154796,5,'2020-06-02 22:20:23',7.0,'First half is extraordinary, climax below ordinary.'),
(4500000,6,'2020-07-07 10:40:55',8.0,'Brilliant acting');
/*!40000 ALTER TABLE `ratings` ENABLE KEYS */;
UNLOCK TABLES;

DROP TABLE IF EXISTS `directors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `directors` (
  `directorId` int(11) NOT NULL AUTO_INCREMENT,
  `lastName` varchar(50) NOT NULL,
  `firstName` varchar(50) NOT NULL,
  PRIMARY KEY(`directorId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `directors` (`lastName`, `firstName`) VALUES 
('Docter', 'Pete'),
('Kail', 'Thomas'),
('Mendes', 'Sam'),
('Phillips', 'Todd'),
('Russo', 'Joe'),
('Russo', 'Anthony'),
('Raghavan', 'Siriam');
/*!40000 ALTER TABLE `directors` ENABLE KEYS */;


DROP TABLE IF EXISTS `dir_mov`;
CREATE TABLE `dir_mov` (
  `directorId` int(11) NOT NULL,
  `movieId` int(11) NOT NULL,
  -- PRIMARY KEY(`directorId`, `movieId`),
  FOREIGN KEY (`directorId`) REFERENCES `directors` (`directorId`) ON DELETE CASCADE,
  FOREIGN KEY (`movieId`) REFERENCES `movies` (`movieId`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO `dir_mov` (`directorId`, `movieId`) VALUES 
(1, 2948372),
(2, 8503618),
(3, 8579674),
(4, 7286456),
(5, 4154796),
(6, 4154796),
(7, 4500000);


DROP TABLE IF EXISTS `actors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actors` (
  `actorId` int(11) NOT NULL AUTO_INCREMENT,
  `lastName` varchar(50) NOT NULL,
  `firstName` varchar(50) NOT NULL,
  PRIMARY KEY(`actorId`)  
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `actors` (`lastName`, `firstName`) VALUES 
('Foxx', 'Jamie'),
('Tina', 'Fey'),
('Diggs', 'Daveed'),
('Groff', 'Jonathan'),
('MacKay', 'Gerge'),
('Strong', 'Mark'),
('Phoenix', 'Joaquin'),
('De Niro', 'Robert'),
('Downey Jr.', 'Robert'),
('Evans', 'Chris'),
('Ruffalo', 'Mark'),
('Hemsworth', 'Chris'),
('Hashmi ', 'Tabassum '),
('Khurrana', 'Ayushmann');
/*!40000 ALTER TABLE `actors` ENABLE KEYS */;

DROP TABLE IF EXISTS `act_mov`;
CREATE TABLE `act_mov` (
  `actorId` int(11) NOT NULL,
  `movieId` int(11) NOT NULL,
  -- PRIMARY KEY(`actorId`, `movieId`),
  FOREIGN KEY (`actorId`) REFERENCES `actors` (`actorId`) ON DELETE CASCADE,
  FOREIGN KEY (`movieId`) REFERENCES `movies` (`movieId`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO `act_mov` (`actorId`, `movieId`) VALUES 
(1, 2948372),
(2, 2948372),
(3, 8503618),
(4, 8503618),
(5, 8579674),
(6, 8579674),
(7, 7286456),
(8, 7286456),
(9, 4154796),
(10, 4154796),
(11, 4154796),
(12, 4154796),
(13, 4500000),
(14, 4500000);

DROP TABLE IF EXISTS `dir_act`;
CREATE TABLE `dir_act` (
  `directorId` int(11) NOT NULL,
  `actorId` int(11) NOT NULL,
  -- PRIMARY KEY(`directorId`, `actorId`),
  FOREIGN KEY (`directorId`) REFERENCES `directors` (`directorId`) ON DELETE CASCADE,
  FOREIGN KEY (`actorId`) REFERENCES `actors` (`actorId`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO `dir_act` (`directorId`, `actorId`) VALUES 
(1,1),
(1,2),
(2,3),
(2,4),
(3,5),
(3,6),
(4,7),
(4,8),
(5,9),
(5,10),
(5,11),
(5,12),
(6,9),
(6,10),
(6,11),
(6,12),
(7,13),
(7,14);