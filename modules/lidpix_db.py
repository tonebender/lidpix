#!/usr/bin/env python

# Here are functions for adding/removing users to the lidpix user database.
# See show_usage() below for how to use it.


import sqlite3, time, sys, bcrypt
#from users import UserDB


def connect_to_db(db_filename):
    
    """ Connect to an SQLite database and return connection
    
    db_filename: File with SQLite database in it
    Return: Tuple with connection and cursor """
    
    try:
        connection = sqlite3.connect(db_filename)
    except:
        print "Could not open database:", db_filename
        return None
    else:
        c = connection.cursor()
        return connection, c


def new_table(table, db_filename, schema_filename):
    
    """ Create a new table in database file
    
    table: Name of table
    db_filename: Database file
    schema_filename: File with SQLite schema """
    
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
    
    """ Add a lidpix user to the users table """
    
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


def add_gallery(gallery_id, description, users_r, users_w, groups_r, 
                groups_w, table, db_filename):
    
    """ Add a row with gallery properties to the galleries table """
    
    conn, c = connect_to_db(db_filename)
    sql_cmd = """INSERT INTO ? (gallery_id, time_added, description, 
    users_r, users_w, groups_r, groups_w)
    VALUES (NULL, ?, ?, ?, ?, ?, ?)"""
    c.execute(sql_cmd, (table, gallery_id,
                        time.asctime(time.localtime(time.time())),
                        description, users_r, users_w, groups_r, groups_w,))
    conn.commit()
    conn.close()
    return True


def add_image(imagefile, time_photo, time_added, description, 
              users_r, users_w, groups_r, groups_w, table, db_filename):
    
    """ Add a row with image properties to an image (gallery) table """
    
    conn, c = connect_to_db(db_filename)
    sql_cmd = """INSERT INTO ? (image_id, imagefile, time_photo, 
    time_added, description, users_r, users_w, groups_r, groups_w)
    VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"""
    c.execute(sql_cmd, (table, imagefile, time_photo,
              time.asctime(time.localtime(time.time())),
              description, users_r, users_w, groups_r, groups_w,))
    conn.commit()
    conn.close()
    return True
    

def delete_user(username, table, db_filename):
    connection, c = connect_to_db(db_filename)
    command = "DELETE FROM {table} WHERE username =?".format(table=table)
    c.execute(command, (username,))
    connection.commit()
    connection.close()
    return True
    
    
def print_table(table, db_filename):
    
    """ Print the table called table in file db_filename """
    
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
    print """Usage: lidpix_db.py command [username|galleryname] table database_file
          command can be:
          adduser      add user with [username] to user table in database_file
          addgallery   add gallery with [galleryname] to gallery table in database_file
          deleteuser   delete user from table in database_file
          newutable    create new table (overwrite existing)
          newgtable    create new table of galleries (overwrite existing)
          printtable   print existing table in database_file"""
    sys.exit(0)


if __name__ == '__main__':
    
    """ This main function handles all the shell commands for
    administering the lidpix database"""
    
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        show_usage()
    
    # Command newutable or newgtable: Create new table of users or galleries
    if sys.argv[1] == 'newutable' or sys.argv[1] == 'newgtable':
        if len(sys.argv) != 4:
            print "Too few or too many arguments. Needs tablename and database_file."
            show_usage()
        try:
            if sys.argv[1] == 'newutable':
                new_table(sys.argv[2], sys.argv[3], 'user_db_schema.sql')
            elif sys.argv[1] == 'newgtable':
                new_table(sys.argv[2], sys.argv[3], 'gallery_db_schema.sql')
            print "Created new table " + sys.argv[2] + " in file", sys.argv[3]
        except:
            print "Error creating table " + sys.argv[2] + " in file", sys.argv[3]
            
    # Command printtable: Show table
    if sys.argv[1] == 'printtable':
        if len(sys.argv) != 4:
            print "Too few or too many arguments."
            show_usage()
        print_table(sys.argv[2], sys.argv[3])
            
    # Command adduser: Add new user to database
    if sys.argv[1] == 'adduser':
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
            print "Successfully added user %s to table %s in file %s" \
            % (sys.argv[2], sys.argv[3], sys.argv[4])
        
    # Command deleteuser: Delete user
    if sys.argv[1] == 'deleteuser':
        if len(sys.argv) != 5:
            print "Incorrect number of arguments after command 'd'"
        if delete_user(sys.argv[2], sys.argv[3], sys.argv[4]):
            print "Deleted user %s from table %s in file %s" % (sys.argv[2], sys.argv[3], sys.argv[4])
