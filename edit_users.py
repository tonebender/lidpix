#!/usr/bin/python

# Here are functions for adding/removing users to the lidpix user database.


import sqlite3
from users import UserDB


def create_new_user_db(db_filename):
    
    try:
        connection = sqlite3.connect(db_filename)
    except:
        print "Could not open database:", db_filename
        return False
        
    cursor = connection.cursor()
    
    # Delete existing
    cursor.execute("""DROP TABLE IF EXISTS flaskusers;""")
    
    sql_command = """
    CREATE TABLE flaskusers (
    user_nr INTEGER PRIMARY KEY,
    username VARCHAR(30),
    password BINARY(60),
    fname VARCHAR(30),
    lname VARCHAR(30),
    joining DATE,
    active BOOLEAN DEFAULT TRUE);"""
    
    cursor.execute(sql_command)
    
    connection.commit()
    connection.close()
    
    return True


def add_user(user, db_filename):
    flaskusers = [('steve', 'Steve', 'Jobs'),
    ('woz', 'Steve', 'Wozniak'), ('bob', 'Robert', 'Noyce')]
    
    for p in flaskusers:
        format_str = """
        INSERT INTO flaskusers (user_nr, username, fname, lname)
        VALUES (NULL, "{username}", "{first}", "{last}");"""
        sql_command = format_str.format(username=p[0], first=p[1], \
        last=p[2])
        cursor.execute(sql_command)
