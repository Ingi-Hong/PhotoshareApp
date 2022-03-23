CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS pictures CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS likes CASCADE;
DROP TABLE IF EXISTS friends CASCADE;
DROP TABLE IF EXISTS tagged_photos CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS photos CASCADE;
DROP TABLE IF EXISTS albums CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
first_name VARCHAR(11),
last_name VARCHAR(11),
gender VARCHAR(11),
dob DATE,
hometown VARCHAR(11),
email VARCHAR (30) UNIQUE,
password CHAR(64),
is_registered BIT NOT NULL,  
PRIMARY KEY (email)
);

CREATE TABLE albums (
a_id int AUTO_INCREMENT,
Name VARCHAR (11),
owner_id VARCHAR (30),
date DATE,
PRIMARY KEY (a_id),

FOREIGN KEY (owner_id) REFERENCES users(email) ON DELETE CASCADE
);

INSERT INTO users (first_name, last_name, email, password, is_registered) VALUE ('Guest', 'User', 'guest', 'p', 0);
INSERT INTO users (first_name, last_name, email, password, is_registered) VALUE ('Ingi', 'Hong', 'ingihong@bu.edu', 'p', 1);  
INSERT INTO albums (Name, owner_id) VALUES ('album', 'ingihong@bu.edu');

CREATE TABLE photos (
p_id int  AUTO_Increment,
caption VARCHAR (50),
data MEDIUMBLOB,
a_id int,
owner_id VARCHAR(30),
FOREIGN KEY (owner_id) REFERENCES users(email) ON DELETE CASCADE,
FOREIGN KEY (a_id) REFERENCES albums(a_id) ON DELETE CASCADE,
PRIMARY KEY (p_id)
);

CREATE TABLE comments ( 
c_id int NOT NULL auto_increment,
text CHAR(100) NOT NULL,
date DATE NOT NULL, 
uid VARCHAR(30) NOT NULL,
pid int NOT NULL,
PRIMARY KEY (c_id),
FOREIGN KEY (uid) REFERENCES users(email),
FOREIGN KEY (pid) REFERENCES photos(p_id)
);

CREATE TABLE likes(
userid VARCHAR(30),
photoid int,
PRIMARY KEY (userid,photoid),
FOREIGN KEY (userid) REFERENCES users(email),
FOREIGN KEY (photoid) REFERENCES photos(p_id)
);

CREATE TABLE friends (
user1 VARCHAR(30) NOT NULL,
user2 VARCHAR(30) NOT NULL,
FOREIGN KEY (user1) REFERENCES users(email),
PRIMARY KEY (user1, user2));

CREATE TABLE tags(
tag VARCHAR (10),
PRIMARY KEY (tag)
);

CREATE TABLE tagged_photos(
p_id int auto_increment, 
tags VARCHAR(10), 
FOREIGN KEY (p_id) REFERENCES photos(p_id),
FOREIGN KEY (tags) REFERENCES tags(tag),
PRIMARY KEY (p_id,tags)
);
