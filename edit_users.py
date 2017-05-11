#!/usr/bin/env python

# Here are functions for adding/removing users to the lidpix user database.
# See show_usage() below for how to use it.


import sqlite3, time, sys, bcrypt
#from users import UserDB

schemafile = 'user_db_schema.sql'


def connect_to_db_file(db_filename):
    try:
        connection = sqlite3.connect(db_filename)
    except:
        print "Could not open database:", db_filename
        sys.exit(0)
    else:
        return connection


def create_new_user_db(db_name, db_filename):
    connection = connect_to_db_file(db_filename)
    c = connection.cursor()
    
    # Delete existing
    c.execute("DROP TABLE IF EXISTS " + db_name + ";")
    
    # Create new database from schema file
    with open(schemafile, mode='r') as f:
        scriptlines = "CREATE TABLE " + db_name + " (" + f.read() + ");"
    
    c.execute("DROP TABLE IF EXISTS " + db_name + ";")
    c.executescript(scriptlines)
    connection.commit()
    connection.close()
    return True


def add_user(username, password, fullname, joined, groups, db_name, db_filename):
    connection = connect_to_db(db_filename)
    c = connection.cursor()
    
    format_str = """INSERT INTO {db_name} (user_nr, username, password,
    fullname, groups, joining, active, confirmdelete, viewmode, theme)
    VALUES (NULL, "{username}", "{password}", "{fullname}", "{groups}", "{joined}", TRUE, TRUE, 10, "default");"""
    sql_command = format_str.format(db_name=db_name, username=username, password=password, \
    fullname=fullname, joined=joined, groups=groups)
    c.execute(sql_command)
    connection.commit()
    connection.close()
    return True
    
    
def delete_user(username, db_name, db_filename):
    connection = connect_to_db(db_filename)
    c = connection.cursor()
    command = "DELETE FROM {db_name} WHERE username =?".format(db_name=db_name)
    c.execute(command, (username,))
    connection.commit()
    connection.close()
    return True
    
    
def print_db(db_name, db_filename):
    connection = connect_to_db(db_filename)
    c = connection.cursor()
    c.execute('SELECT * FROM {db_name}'.format(db_name=db_name))
    rows = c.fetchall()
    connection.close()
    for r in rows:
        print ""
        print "User number:", r[0]
        print "Username:", r[1]
        print "Password:", r[2]
        print "Full name:", r[3]
        print "Joined date:", r[4]
        print "Member of groups:", r[5]
        print "Active:", r[6]


def show_usage():
    print """Usage: edit_users.py command [username] database_name database_file
          command can be:
          a   add user to database
          d   delete user from database
          c   create new database (existing will be deleted)
          p   print existing database"""
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        show_usage()
    
    # Command c: Create new database
    if sys.argv[1] == 'c':
        if len(sys.argv) != 4:
            print "Too few or too many arguments."
            show_usage()
        if create_new_user_db(sys.argv[2]):
            print "Created new database " + sys.argv[2] + " in file", sys.argv[3]
        else:
            print "Error creating database " + sys.argv[2] + " in file", sys.argv[3]
            
    # Command p: Show database
    if sys.argv[1] == 'p':
        if len(sys.argv) != 4:
            print "Too few or too many arguments."
            show_usage()
        print_db(sys.argv[2], sys.argv[3])
            
    # Command a: Add new user to database
    if sys.argv[1] == 'a':
        if len(sys.argv) != 5:
            print "Incorrect number of arguments after command 'a'"
            sys.exit(0)
        print "Adding user {u} ...".format(u=sys.argv[2])
        pw = raw_input("Please enter user's new password: ")
        pa = raw_input("Repeat password: ")
        if pw != pa:
            print "Passwords don't match"
            sys.exit(0)
        hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
        f = raw_input("User's full name (first and last with space between): ")
        gr = raw_input("The groups user is member of (lower case with ; between): ")
        j = time.asctime(time.localtime(time.time()))
        
        if add_user(sys.argv[2], hashed_pw, f, j, gr, sys.argv[3], sys.argv[4]):
            print "Successfully added user %s to database %s in file" % 
            (sys.argv[2], sys.argv[3], sys.argv[4])
        
    # Command d: Delete user
    if sys.argv[1] == 'd':
        if len(sys.argv) != 5:
            print "Incorrect number of arguments after command 'd'"
        if delete_user(sys.argv[2], sys.argv[3], sys.argv[4]):
            print "Deleted user %s from database %s in file %s" % (sys.argv[2], sys.argv[3], sys.argv[4])
