#!/usr/bin/env python

# Here are functions for adding/removing users to the lidpix user database.


import sqlite3, time, sys, bcrypt
#from users import UserDB


def connect_to_db(db_filename):
    try:
        connection = sqlite3.connect(db_filename)
    except:
        print "Could not open database:", db_filename
        sys.exit(0)
    else:
        return connection


def create_new_user_db(db_filename):
    connection = connect_to_db(db_filename)
    c = connection.cursor()
    
    # Delete existing
    c.execute("""DROP TABLE IF EXISTS flaskusers;""")
    
    # Create new database from schema file
    with open('user_db_schema.sql', mode='r') as f:
        c.executescript(f.read())
    connection.commit()
    connection.close()
    return True


def add_user(username, password, fname, lname, joining, db_filename):
    connection = connect_to_db(db_filename)
    c = connection.cursor()
    
    format_str = """INSERT INTO flaskusers (user_nr, username, password,
    fname, lname, joining)
    VALUES (NULL, "{username}", "{password}", "{first}", "{last}", "{joined}");"""
    sql_command = format_str.format(username=username, password=password, \
    first=fname, last=lname, joined=joining)
    c.execute(sql_command)
    connection.commit()
    connection.close()
    return True
    
    
def delete_user(username, db_filename):
    connection = connect_to_db(db_filename)
    c = connection.cursor()
    command = "DELETE FROM flaskusers WHERE username =?"
    c.execute(command, (username,))
    connection.commit()
    connection.close()
    return True
    
    
def print_db(db_filename):
    connection = connect_to_db(db_filename)
    c = connection.cursor()
    c.execute('SELECT * FROM flaskusers')
    rows = c.fetchall()
    connection.close()
    for r in rows:
        print ""
        print "User number:", r[0]
        print "Username:", r[1]
        print "Password:", r[2]
        print "First name:", r[3]
        print "Last name:", r[4]
        print "Joined date:", r[5]
        print "Active:", r[6]


def show_usage():
    print """Usage: edit_users.py command [username] database_file
          command can be:
          a   add user to database
          d   delete user from database
          c   create new database (existing will be deleted)
          p   print existing database"""
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        show_usage()
    
    # Command c: Create new database
    if sys.argv[1] == 'c':
        if len(sys.argv) != 3:
            print "Too few or too many arguments."
            show_usage()
        if create_new_user_db(sys.argv[2]):
            print "Created new database", sys.argv[2]
        else:
            print "Error creating database", sys.argv[2]
            
    # Command p: Show database
    if sys.argv[1] == 'p':
        if len(sys.argv) != 3:
            print "Too few or too many arguments."
            show_usage()
        print_db(sys.argv[2])
            
    # Command a: Add new user to database
    if sys.argv[1] == 'a':
        if len(sys.argv) != 4:
            print "Incorrect number of arguments after command 'a'"
            sys.exit(0)
        print "Adding user {u} ...".format(u=sys.argv[2])
        pw = raw_input("Please enter user's new password: ")
        pa = raw_input("Repeat password: ")
        if pw != pa:
            print "Passwords don't match"
            sys.exit(0)
        hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
        f = raw_input("User's first name: ")
        l = raw_input("User's last name: ")
        j = time.asctime(time.localtime(time.time()))
        
        if add_user(sys.argv[2], hashed_pw, f, l, j, sys.argv[3]):
            print "Successfully added user %s to database %s" % (sys.argv[2],
            sys.argv[3])
        
    # Command d: Delete user
    if sys.argv[1] == 'd':
        if len(sys.argv) != 4:
            print "Incorrect number of arguments after command 'd'"
        if delete_user(sys.argv[2], sys.argv[3]):
            print "Deleted user %s from %s" % (sys.argv[2], sys.argv[3])
