#!/usr/bin/env python

# Here are functions for adding/removing users to the lidpix user database.
# See show_usage() below for how to use it.


import sqlite3, time, sys, argparse
import bcrypt
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
    
    try:
        conn, c = connect_to_db(db_filename)
        
        c.execute("DROP TABLE IF EXISTS " + table + ";") # Delete existing
        
        with open(schema_filename, mode='r') as f:
            scriptlines = "CREATE TABLE " + table + " (" + f.read() + ");"
        
        c.execute("DROP TABLE IF EXISTS " + table + ";")
        c.executescript(scriptlines)
        conn.commit()
        conn.close()
    except:
        print "Error when trying to create table " + table + " in db file " + db_filename
        return False
    else:
        return True


def add_gallery(galleryname, description, tags, users_r, users_w, 
                groups_r, groups_w, table, db_filename):
    
    """ Add a row with gallery properties to a gallery index table """
    
    try:
        conn, c = connect_to_db(db_filename)
        sql_cmd = """INSERT INTO ? (gallery_id, gallery_name, description, 
        tags, time_added, users_r, users_w, groups_r, groups_w)
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?);"""
        c.execute(sql_cmd, (table, galleryname, description, tags,
                            time.asctime(time.localtime(time.time())),
                            users_r, users_w, groups_r, groups_w,))
        conn.commit()
        conn.close()
    except:
        print "Error when trying to add gallery in table " + table + \
        " in db file " + db_filename
        return False
    else:
        return True


def add_images(imagefiles, description, tags, time_photo, time_added, 
              users_r, users_w, groups_r, groups_w, table, db_filename):
    
    """ Add one or more rows with image properties to an image (gallery) table """
    
    try:
        conn, c = connect_to_db(db_filename)
        sql_cmd = """INSERT INTO ? (image_id, imagefile, description, tags,
            time_photo, time_added, users_r, users_w, groups_r, groups_w)
            VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        tyme = time.asctime(time.localtime(time.time()))
        for i in imagefiles:
            c.execute(sql_cmd, (table, i, time_photo, description, tags,
                  tyme, users_r, users_w, groups_r, groups_w,))
        conn.commit()
        conn.close()
    except:
        print "Error when trying to add image " + imagefile + \
        " in table " + table + " in db file " + db_filename
        return False
    else:
        return True
    

def fill_gallery(images, table, db_filename):
    
    """ Add a number of images to a gallery """
    return True
    

def add_user(username, password, fullname, joined, groups, table, db_filename):
    
    """ Add a lidpix user to the users table """
    
    try:
        conn, c = connect_to_db(db_filename)
        format_str = """INSERT INTO {table} (user_nr, username, password,
        fullname, groups, joining, active, confirmdelete, viewmode, theme)
        VALUES (NULL, "{username}", "{password}", "{fullname}", "{groups}", "{joined}", 1, 1, 10, "default");"""
        sql_command = format_str.format(table=table, username=username, password=password, \
        fullname=fullname, joined=joined, groups=groups)
        c.execute(sql_command)
        conn.commit()
        conn.close()
    except:
        print "Error when trying to add user " + username + \
        " in table " + table + " in db file " + db_filename
        return False
    else:
        return True
        

def delete_user(username, table, db_filename):
    
    """ Remove a lidpix user from the users table """
    
    try:
        conn, c = connect_to_db(db_filename)
        command = "DELETE FROM {table} WHERE username =?".format(table=table)
        c.execute(command, (username,))
        conn.commit()
        conn.close()
    except:
        print "Error when trying to delete user " + username + \
        " from table " + table + " in file " + db_filename
        return False
    else:
        return True
    

# Make more general "print table" function, 
# perhaps with schema as argument for formatting?
# Or maybe it's possible to print cols from table?
def print_usertable(table, db_filename):
    
    """ Print the table called table in file db_filename """
    
    try:
        conn, c = connect_to_db(db_filename)
        c.execute('SELECT * FROM {table}'.format(table=table))
        rows = c.fetchall()
        conn.close()
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
    except:
        print "Error when trying to print table " + table + \
        " in database file " + db_filename
        return False
    else:
        return True
        

# Delete this function and/or make something more generally explaining...
def show_usage():
    print """Usage: lidpix_db.py command [username|galleryname] [-t table] [-d database_file] [images]
          command can be:
          addimages    add [images] to image gallery table with [galleryname]
          addgallery   add gallery with [galleryname] to gallery index table in database_file
          adduser      add user with [username] to user table in database_file
          deleteuser   delete user from table in database_file
          newutable    create new table (overwrite existing)
          newgtable    create new table of galleries (overwrite existing)
          printtable   print existing table in database_file
          
          Options:
          --table -t   specify which table (with galleries, users) to use
          --dbfile -d  specify which sqlite database file to use
          """
    sys.exit(0)
    

if __name__ == '__main__':
    
    """ This main function handles all the shell commands for
    administering the lidpix database"""

    parser = argparse.ArgumentParser(description='Lidpix database editor')
    
    parser.add_argument('--dbfile', '-d', nargs='?', dest='dbfile', const='lidpix.db', default='lidpix.db', help='sqlite database file')
    
    subparsers = parser.add_subparsers(dest='subparser_name')    
    
    parser_printtable = subparsers.add_parser('printtable', help='print table to stdout')
    parser_printtable.add_argument('table', help='name of the table to print') 
    
    parser_newutable = subparsers.add_parser('newutable', help='create new user table')
    parser_newutable.add_argument('table', help='name of the table to create')
    
    parser_newgtable = subparsers.add_parser('newgtable', help='create new gallery index table')
    parser_newgtable.add_argument('table', help='name of the table to create')
    
    parser_newitable = subparsers.add_parser('newitable', help='create new image gallery table')
    parser_newitable.add_argument('table', help='name of the table to create')
    
    parser_adduser = subparsers.add_parser('adduser', help='add new user to user table')
    parser_adduser.add_argument('username', help='username of the new user')
    parser_adduser.add_argument('--table', '-t', nargs='?', const='lidpixusers', default='lidpixusers', help='table to add user to')
    
    parser_addimages = subparsers.add_parser('addimages', help='add images to image gallery table')
    parser_addimages.add_argument('table', help='name of table to record images in')
    parser_addimages.add_argument('images', nargs='*', help='image files to add')
    
    args = parser.parse_args()
    
    
    # Table operations
    
    if args.subparser_name == 'printtable':
        print_usertable(args.table, args.dbfile)
        
    if args.subparser_name == 'newutable':
        if new_table(args.table, args.dbfile, 'user_db_schema.sql'):
            print "Created new user table " + args.table + " in file", args.dbfile
            
    if args.subparser_name == 'newgtable':
        if new_table(args.table, args.dbfile, 'gallery_db_schema.sql'):
            print "Created new gallery index table " + args.table + " in file", args.dbfile
            
    if args.subparser_name == 'newitable':
        if new_table(args.table, args.dbfile, 'image_db_schema.sql'):
            print "Created new image gallery table " + args.table + " in file", args.dbfile
    
    
    # User operations
    
    if args.subparser_name == 'adduser':
        print "Adding user " + args.username + " ..."
        pw = raw_input("Please enter user's new password: ")
        pa = raw_input("Repeat password: ")
        if pw != pa:
            print "Passwords don't match"
            sys.exit(0)
        hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
        f = raw_input("User's full name (first and last with space between): ")
        gr = raw_input("The groups user is member of (lower case with ; between): ")
        j = time.asctime(time.localtime(time.time()))
        
        if add_user(args.username, hashed_pw, f, j, gr, args.table, args.dbfile):
            print "Successfully added user %s to table %s in file %s" \
            % (args.name, args.table, args.dbfile)

    if args.subparser_name == 'deleteuser':
        if delete_user(args.username, args.table, args.dbfile):
            print "Deleted user %s from table %s in file %s" % (args.name, args.table, args.dbfile)
            
    
    # Image gallery operations
    
    if args.subparser_name == 'addimages':
        print "Going to add images to table " + args.table + ": "
        print args.images
        
        # Here add some Q & A input, as with adduser above, then call add_images(...)
    
    #def add_images([imagefiles], description, tags, time_photo, time_added, 
              # users_r, users_w, groups_r, groups_w, table, db_filename):
