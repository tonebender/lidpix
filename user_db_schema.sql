user_nr INTEGER PRIMARY KEY,
username VARCHAR(30),
password BINARY(60),
fullname VARCHAR(30),
groups VARCHAR(30),
joining DATE,
active BOOLEAN DEFAULT TRUE,
viewlayout INTEGER,
confirmdelete BOOLEAN DEFAULT TRUE
