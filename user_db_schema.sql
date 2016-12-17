DROP TABLE IF EXISTS flaskusers;
CREATE TABLE flaskusers (
user_nr INTEGER PRIMARY KEY,
username VARCHAR(30),
password BINARY(60),
fname VARCHAR(30),
lname VARCHAR(30),
joining DATE,
active BOOLEAN DEFAULT TRUE);
