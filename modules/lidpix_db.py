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


def add_images([imagefiles], description, tags, time_photo, time_added, 
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
        

def show_usage():
    print """Usage: lidpix_db.py command [username|galleryname] [-t table] [-d database_file] [images]
          command can be:
          addimages    add [images] to image gallery table with [galleryname]
          addgallery   add gallery with [galleryname] to gallery table in database_file
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
    
    # https://stackoverflow.com/questions/8423895/using-argparse-in-conjunction-with-sys-argv-in-python
    # https://stackoverflow.com/questions/4480075/argparse-optional-positional-arguments

    parser = argparse.ArgumentParser(description='Lidpix database editor')
    parser.add_argument('cmd', metavar='command', help='command')
    parser.add_argument('name', metavar='username|galleryname', nargs='?', help='username or galleryname')
    parser.add_argument('--table', '-t', nargs='?', dest='table', help='table to use')
    parser.add_argument('--dbfile', '-d', nargs='?', dest='dbfile', const='lidpix_users.db', default='lidpix_users.db', help='sqlite database file')
    parser.add_argument('images', nargs='*', help='images')
    args = parser.parse_args()
    
    # Create new table of users or galleries
    if args.cmd == 'newutable':
        if new_table(args.table, args.dbfile, 'user_db_schema.sql'):
            print "Created new user table " + args.table + " in file", args.dbfile
    elif args.cmd == 'newgtable':
        if new_table(args.table, args.dbfile, 'gallery_db_schema.sql'):
            print "Created new gallery table " + args.table + " in file", args.dbfile
            
    #def add_images([imagefiles], description, tags, time_photo, time_added, 
              # users_r, users_w, groups_r, groups_w, table, db_filename):
              
    if args.cmd == 'add_images':
        if add_images():
            print "Added images"
    
    if args.cmd == 'printtable':
        print_table(args.table, args.dbfile)

    if args.cmd == 'adduser':
        print "Adding user {u} ...".format(u=args.name)
        pw = raw_input("Please enter user's new password: ")
        pa = raw_input("Repeat password: ")
        if pw != pa:
            print "Passwords don't match"
            sys.exit(0)
        hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
        f = raw_input("User's full name (first and last with space between): ")
        gr = raw_input("The groups user is member of (lower case with ; between): ")
        j = time.asctime(time.localtime(time.time()))
        
        if add_user(args.name, hashed_pw, f, j, gr, args.table, args.dbfile):
            print "Successfully added user %s to table %s in file %s" \
            % (args.name, args.table, args.dbfile)

    if args.cmd == 'deleteuser':
        if delete_user(args.name, args.table, args.dbfile):
            print "Deleted user %s from table %s in file %s" % (args.name, args.table, args.dbfile)
