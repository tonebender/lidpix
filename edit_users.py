#!/usr/bin/env python

# Here are functions for adding/removing users to the lidpix user database.
# See show_usage() below for how to use it.


import sqlite3, time, sys, bcrypt
#from users import UserDB


def connect_to_db(db_filename):
    try:
        connection = sqlite3.connect(db_filename)
    except:
        print "Could not open database:", db_filename
        sys.exit(0)
    else:
        c = connection.cursor()
        return connection, c


def create_new_db(table, db_filename, schema_filename):
    connection, c = connect_to_db(db_filename)
    
    c.execute("DROP TABLE IF EXISTS " + table + ";") # Delete existing
    
    with open(schema_filename, mode='r') as f:
        scriptlines = "CREATE TABLE " + table + " (" + f.read() + ");"
    
    c.execute("DROP TABLE IF EXISTS " + table + ";")
    c.executescript(scriptlines)
    connection.commit()
    connection.close()
    return True


def add_user(username, password, fullname, joined, groups, table, db_filename):
    connection, c = connect_to_db(db_filename)
    
    format_str = """INSERT INTO {table} (user_nr, username, password,
    fullname, groups, joining, active, confirmdelete, viewmode, theme)
    VALUES (NULL, "{username}", "{password}", "{fullname}", "{groups}", "{joined}", 1, 1, 10, "default");"""
    sql_command = format_str.format(table=table, username=username, password=password, \
    fullname=fullname, joined=joined, groups=groups)
    c.execute(sql_command)
    connection.commit()
    connection.close()
    return True
    
    
def delete_user(username, table, db_filename):
    connection, c = connect_to_db(db_filename)
    command = "DELETE FROM {table} WHERE username =?".format(table=table)
    c.execute(command, (username,))
    connection.commit()
    connection.close()
    return True
    
    
def print_db(table, db_filename):
    connection, c = connect_to_db(db_filename)
    c.execute('SELECT * FROM {table}'.format(table=table))
    rows = c.fetchall()
    connection.close()
    for r in rows:
        print ""
        print "User number:", r[0]
        print "Username:", r[1]
        print "Password:", r[2]
        print "Full name:", r[3]
        print "Member of groups:", r[4]
        print "Joined date:", r[5]
        print "Active:", r[6]
        print "Confirm deletions:", r[7]
        print "View mode (thumbnail columns):", r[8]
        print "GUI Theme:", r[9]


def show_usage():
    print """Usage: edit_users.py command [username] table database_file
          command can be:
          a   add user with [username] to table in database_file
          d   delete user from database
          c   create new table (existing will be deleted)
          p   print existing table in database_file"""
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        show_usage()
    
    # Command c: Create new database
    if sys.argv[1] == 'c':
        if len(sys.argv) != 4:
            print "Too few or too many arguments."
            show_usage()
        if create_new_db(sys.argv[2], sys.argv[3], 'user_db_schema.sql'):
            print "Created new database " + sys.argv[2] + " in file", sys.argv[3]
        else:
            print "Error creating database " + sys.argv[2] + " in file", sys.argv[3]
            
    # Command p: Show table
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
            print "Successfully added user %s to database %s in file %s" \
            % (sys.argv[2], sys.argv[3], sys.argv[4])
        
    # Command d: Delete user
    if sys.argv[1] == 'd':
        if len(sys.argv) != 5:
            print "Incorrect number of arguments after command 'd'"
        if delete_user(sys.argv[2], sys.argv[3], sys.argv[4]):
            print "Deleted user %s from database %s in file %s" % (sys.argv[2], sys.argv[3], sys.argv[4])
