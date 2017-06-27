#!/usr/bin/env python

# Here are functions for adding/removing users to the lidpix user database.
# See show_usage() below for how to use it.


import sqlite3, time, sys, argparse, os, subprocess
import bcrypt
import folder
#from folder import get_image_info
#from users import UserDB



def safe(s):
    """ Sanitize string s. Only allow a-z, A-Z, 0-9 and _ """
    return ("".join(c for c in s if c.isalnum() or c == '_').rstrip())

    
def connect_to_db(db_file):
    
    """ Connect to an SQLite database and return connection
    
    db_file: File with SQLite database in it
    Return: Tuple with connection and cursor """
    
    try:
        connection = sqlite3.connect(db_file)
    except Exception as e:
        print "Could not open database:", db_file
        return None
    else:
        c = connection.cursor()
        return connection, c


def new_table(table, db_file, schema_filename):
    
    """ Create a new table in database file. Do nothing if specified
    table already exists.
    
    table: Name of table
    db_file: Database file
    schema_filename: File with SQLite schema """
    
    try:
        conn, c = connect_to_db(db_file)
        with open(schema_filename, mode='r') as f:
            scriptlines = "CREATE TABLE IF NOT EXISTS " + table + "\n(" + f.read() + ");"
        c.executescript(scriptlines)
        conn.commit()
        conn.close()
    except Exception as e:
        print "Error when trying to create table " + table + " in db file " + db_file
        return False
    else:
        return True


def find_table(table, db_file):
    
    """ Return true if table exists in db_file, false if not """
    
    try:
        conn, c = connect_to_db(db_file)
        if table == '*':
            tb_exists = "SELECT name FROM sqlite_master WHERE type='table'"
        else:
            tb_exists = "SELECT name FROM sqlite_master WHERE type='table' AND name='" + table + "'"
        fetched = conn.execute(tb_exists).fetchone()
        conn.close()
    except Exception as e:
        print "Error when trying to find table " + table + " in database file " + db_file
        return False
    else:
        return fetched
        

#def find_row(column_to_search, value_to_match, table, db_file):
#    
#    """ Find first row where column_to_search has value_to_match in table.
#    Return  """
#    
#    try:
#        conn, c = connect_to_db(db_file)
#        v = c.execute('DELETE FROM {t} WHERE {cs}="{vm}"'.format(t=safe(table),
#                  cs=safe(column_to_search), vm=value_to_match))
#        deleted = c.rowcount
#        conn.commit()
#        conn.close()
#    except Exception as e:
#        print "Error when trying to delete row in table", table, "in db file", db_file
#        print e
#        return 0
#    else:
#        return deleted
        

def delete_table(table, db_file):
    
    """ Delete existing table in database file """
    
    try:
        conn, c = connect_to_db(db_file)
        c.execute("DROP TABLE IF EXISTS " + safe(table) + ";")
        conn.close()
    except Exception as e:
        print "Error when trying to delete table " + table + " in database file " + db_file
        print e
        return False
    else:
        return True


def delete_row(column_to_search, value_to_match, table, db_file):
    
    """ Delete row(s) from a table.
    Return number of deleted rows. """
    
    try:
        conn, c = connect_to_db(db_file)
        v = c.execute('DELETE FROM {t} WHERE {cs}="{vm}"'.format(t=safe(table),
                  cs=safe(column_to_search), vm=value_to_match))
        deleted = c.rowcount
        conn.commit()
        conn.close()
    except Exception as e:
        print "Error when trying to delete row in table", table, "in db file", db_file
        print e
        return 0
    else:
        return deleted


def get_column(col_to_search, value_to_match, col_to_get, table, db_file):

    """ Get contents of one column in the first row that match a certain value in 1 column.
    Return as a tuple. """
    
    try:
        conn, c = connect_to_db(db_file)    
        c.execute('SELECT {cg} FROM {t} WHERE {col}="{value}"'.format(t=safe(table), 
                  cg=safe(col_to_get), col=safe(col_to_search), value=safe(value_to_match)))
        column = c.fetchone()
        conn.close()
        return column
    except Exception as e:
        print "Error when trying to fetch row in table", table, "in database file", db_file
        print e
        return None


def get_row(column_to_search, value_to_match, table, db_file):

    """ Get contents of all columns in the first row that match a certain value in 1 column.
    Return as a tuple. """
    
    try:
        conn, c = connect_to_db(db_file)    
        c.execute('SELECT * FROM {t} WHERE {col}="{value}"'.format(t=safe(table), 
                  col=safe(column_to_search), value=safe(value_to_match)))
        row = c.fetchone()
        conn.close()
        return row
    except Exception as e:
        print "Error when trying to fetch row in table", table, "in database file", db_file
        print e
        return None


def get_all_rows(table, db_file):

    """ Get all rows in table, return it as a list with a tuple for each row """
    
    try:
        conn, c = connect_to_db(db_file)    
        c.execute('SELECT * FROM {t}'.format(t=safe(table)))
        allrows = c.fetchall()
        conn.close()
        return allrows
    except Exception as e:
        print "Error when trying to fetch all rows in table", table, "in database file", db_file
        print e
        return []
        

def add_gallery(galleryname, defpath, description, tags, zipfile, 
                users_r, users_w, groups_r, groups_w, table, db_file):
    
    """ Add a row with gallery properties to a gallery index table """
    
    try:
        conn, c = connect_to_db(db_file)
        sql_cmd = """INSERT INTO {t}
        (gallery_id, gallery_name, defpath, description, tags, 
        time_added, zipfile, users_r, users_w, groups_r, groups_w)
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""".format(t=safe(table))
        c.execute(sql_cmd, (galleryname, defpath, description, tags,
                            time.asctime(time.localtime(time.time())),
                            zipfile, users_r, users_w, groups_r, groups_w,))
        conn.commit()
        conn.close()
    except Exception as e:
        print "Error when trying to add gallery in table " + table + \
        " in db file " + db_file
        print e
        return False
    else:
        return True


def add_images(imagefiles, description, tags, users_r, 
               users_w, groups_r, groups_w, table, db_file):
    
    """ Add one or more rows with image properties to an image (gallery) table """
    
    try:
        conn, c = connect_to_db(db_file)
        sql_cmd = """INSERT INTO {t} 
            (image_id, imagefile, description, tags, time_photo, 
            time_added, users_r, users_w, groups_r, groups_w)
            VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?);""".format(t=safe(table))
        time_added = time.asctime(time.localtime(time.time()))
        print "Adding images to table " + table + ":"
        for img in imagefiles:
            if img[-4:].lower() == '.zip': # Don't include our own zip
                continue
            time_photo = folder.get_image_info(img).get('DateTimeOriginal', '(no time)')
            c.execute(sql_cmd, (os.path.basename(img), description, tags, time_photo,
                  time_added, users_r, users_w, groups_r, groups_w,))
            print img
        conn.commit()
        conn.close()
    except Exception as e:
        print "Error when trying to add images in table", table, "in db file", db_file
        print e
        return False
    else:
        return True

    
# Improve this - remove format, etc.
def add_user(username, password, fullname, joined, groups, table, db_file):
    
    """ Add a lidpix user to the users table """
    
    try:
        conn, c = connect_to_db(db_file)
        format_str = """INSERT INTO {table} (user_nr, username, password,
        fullname, groups, joining, active, confirmdelete, viewmode, theme)
        VALUES (NULL, "{username}", "{password}", "{fullname}", "{groups}", "{joined}", 1, 1, 10, "default");"""
        sql_command = format_str.format(table=table, username=username, password=password, \
        fullname=fullname, joined=joined, groups=groups)
        c.execute(sql_command)
        conn.commit()
        conn.close()
    except Exception as e:
        print "Error when trying to add user " + username + \
        " in table " + table + " in db file " + db_file
        print e
        return False
    else:
        return True
        

# Improve this one too
def delete_user(username, table, db_file):
    
    """ Remove a lidpix user from the users table """
    
    try:
        conn, c = connect_to_db(db_file)
        command = "DELETE FROM {table} WHERE username =?".format(table=table)
        c.execute(command, (username,))
        conn.commit()
        conn.close()
    except Exception as e:
        print "Error when trying to delete user " + username + \
        " from table " + table + " in file " + db_file
        print e
        return False
    else:
        return True
    

def print_table(table, db_file):
    
    """ Print the table called table in file db_file """
    
    try:
        conn, c = connect_to_db(db_file)
        rows = c.execute('SELECT * FROM {t}'.format(t=safe(table))).fetchall()
        cols = c.execute("PRAGMA table_info({t})".format(t=safe(table))).fetchall()
        conn.close()
        print '\nTABLE           ', table, '\n'
        r = 1
        for row in rows:
            print "ROW", r
            for i in range(len(cols)):
                print ' ', cols[i][1].ljust(16), (str(row[i]) if isinstance(row[i],(int,long)) else row[i])
            print ''
            r += 1
    except Exception as e:
        print "Error when trying to print table", table
        print e
        

# Delete this function and/or make something more generally explaining...
# Maybe readme/doc is enough
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
    

def get_user_input(genre, galleryname):
    
    """ Get input from user and return as a tuple, to use when adding 
    gallery, images, etc.
        
    genre: String to use in message, e.g. 'gallery' or 'images' """
    
    desc = raw_input("Enter description of %s (single line): " % genre)
    tags = raw_input("Enter comma-separated tags describing %s (e.g. 'pets,dogs,cats'): " % genre)
    users_r = raw_input("Users to give read permission to %s (e.g. 'silvio,vladimir'): " % genre)
    users_w = raw_input("Users to give write permission to %s (e.g. 'barack,angela'): " % genre)
    group_r = raw_input("Group to give read permission to %s (e.g. 'colleagues,friends'): " % genre)
    group_w = raw_input("Group to give write permission to %s (e.g. 'management,workers'): " % genre)
    zipfile = ''
    if genre == 'gallery':
        zipfile = raw_input("Create zipfile? (y/n): ").lower()
        if zipfile == '' or zipfile == 'y':
            zipfile = galleryname + '.zip'
        else:
            zipfile = 'n'
    return (desc, tags, zipfile, users_r, users_w, group_r, group_w)


def get_defpath(defpath):
    """ Let user specify default path for images in gallery """
    userpath = raw_input("Base path for images [%s]: " % defpath)
    if userpath == '':
        userpath = defpath
    return userpath
    

def add_to_zip(zipfile, zippath, files):
    if zipfile == 'n' or zipfile == '':
        return False
    zippath = os.path.normpath(zippath) + '/'
    if os.path.isdir(zippath):
        print "Adding to zipfile:"
        z = subprocess.call(['zip', '-0', zippath + zipfile] + files)
        if z != 0:
            print "zip returned", z
            return False
    else:
        print "Could not create zip. Not a valid directory:", zippath
        return False
    return True


def new_gallery(galleryname, defpath, desc, tags, zipfile, ur, uw, gr, gw, dbfile):
    """ Create a new gallery """
    new_table('galleryindex', dbfile, 'gallery_db_schema.sql') # Create gallery index table if not existing
    if add_gallery(galleryname, defpath, desc, tags, zipfile, ur, uw, gr, gw, 'galleryindex', dbfile): # Add gallery to gallery index table
        print "Added gallery", galleryname, "to galleryindex table"
        new_table(galleryname, dbfile, 'image_db_schema.sql') # Create empty image gallery table if not existing
            


if __name__ == '__main__':
    
    """ This main function handles all the shell commands for
    administering the lidpix database"""

    parser = argparse.ArgumentParser(description='Lidpix database editor')
    
    # const is the default when there are zero values given, default is default when no arg is given at all
    parser.add_argument('--dbfile', '-d', nargs='?', dest='dbfile', const='lidpix.db', default='lidpix.db', help='sqlite database file')
    
    subparsers = parser.add_subparsers(dest='subparser_name')    
    
    parser_printtable = subparsers.add_parser('printtable', help='print table to stdout')
    parser_printtable.add_argument('table', help='name of the table to print') 
    
    parser_findtable = subparsers.add_parser('findtable', help='find table')
    parser_findtable.add_argument('table', help='name of table to find')
    
    parser_newutable = subparsers.add_parser('newutable', help='create new user table')
    parser_newutable.add_argument('table', help='name of the table to create')
    
    parser_newgtable = subparsers.add_parser('newgtable', help='create new gallery index table')
    #parser_newgtable.add_argument('table', help='name of the table to create')
    
    # maybe remove this command and let it be done through other commands below
    parser_newitable = subparsers.add_parser('newitable', help='create new image gallery table')
    parser_newitable.add_argument('table', help='name of the table to create')
    
    parser_deltable = subparsers.add_parser('deltable', help='delete table')
    parser_deltable.add_argument('table', help='name of table to delete')
    
    parser_delgallery = subparsers.add_parser('delgallery', help='delete gallery')
    parser_delgallery.add_argument('galleryname', help='name of gallery to delete')
    
    parser_delimage = subparsers.add_parser('delimage', help='delete one or more images from gallery')
    parser_delimage.add_argument('galleryname', help='name of gallery from which to delete images (table rows)')
    parser_delimage.add_argument('images', nargs='*', help='image file name(s) to delete')  # Fix so it can't be none ??? --------------------
    
    parser_adduser = subparsers.add_parser('adduser', help='add new user to user table')
    parser_adduser.add_argument('username', help='username of the new user')
    parser_adduser.add_argument('--table', '-t', nargs='?', const='lidpixusers', default='lidpixusers', help='table to add user to')
    
    parser_newgallery = subparsers.add_parser('newgallery', help='create new gallery (add row to gallery index table, and create image gallery table)')
    parser_newgallery.add_argument('galleryname', help='name of gallery to add to table')
    
    parser_addimages = subparsers.add_parser('addimages', help='add images to image gallery table')
    parser_addimages.add_argument('galleryname', help='name of image gallery table to record images in') # galleryname is also recorded (on a row) in gallery index table
    parser_addimages.add_argument('images', nargs='*', help='image file(s) to add')
    
    parser_test = subparsers.add_parser('test', help='for testing')
    
    args = parser.parse_args()
    
    
    # "Low level" table operations
    # DELETE some of these, as they're never used by the user anyway
    
    if args.subparser_name == 'printtable':
        print_table(args.table, args.dbfile)
        
    if args.subparser_name == 'deltable':
        if raw_input("Really delete table " + args.table + "? (y/n) ") in 'Yy':
            if delete_table(args.table, args.dbfile):
                print "Deleted table", args.table, "in file", args.dbfile
                
    if args.subparser_name == 'findtable':
        if find_table(args.table, args.dbfile):
            print "Table", args.table, "exists"
        else:
            print "Table", args.table, "not found"
        
    if args.subparser_name == 'newutable':
        if new_table(args.table, args.dbfile, 'user_db_schema.sql'):
            print "Created new user table", args.table, "in file", args.dbfile
            
    if args.subparser_name == 'newgtable':
        if new_table('galleryindex', args.dbfile, 'gallery_db_schema.sql'):
            print "Created new gallery index table 'galleryindex' in file", args.dbfile
            
    if args.subparser_name == 'newitable':
        if new_table(args.table, args.dbfile, 'image_db_schema.sql'):
            print "Created new image gallery table", args.table, "in file", args.dbfile
    
    
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
        gr = raw_input("The groups user is member of (e.g. 'friends,relatives'): ").lower()
        j = time.asctime(time.localtime(time.time()))
        
        if add_user(args.username, hashed_pw, f, j, gr, args.table, args.dbfile):
            print "Successfully added user %s to table %s in file %s" \
            % (args.name, args.table, args.dbfile)

    if args.subparser_name == 'deleteuser':
        if delete_user(args.username, args.table, args.dbfile):
            print "Deleted user %s from table %s in file %s" % (args.name, args.table, args.dbfile)
            
    
    # Image gallery operations
    
    if args.subparser_name == 'newgallery':
        desc, tags, zipfile, ur, uw, gr, gw = get_user_input('gallery', args.galleryname)
        new_gallery(args.galleryname, os.getcwd(), desc, tags, zipfile, ur, uw, gr, gw, args.dbfile)
        
    if args.subparser_name == 'delgallery':
        if args.galleryname == 'galleryindex':
            print "Can't delete galleryindex table. Use deltable command if you really want to do that."
        elif raw_input('Proceed with delete gallery? (y/n) ') in 'Yy':
            if find_table(args.galleryname, args.dbfile): # First try to delete the image table
                if delete_table(args.galleryname, args.dbfile):
                    print "Deleted image gallery table '" + args.galleryname + "'"
            else:
                print "Could not find image gallery table '" + args.galleryname + "'"
            if get_column('gallery_name', args.galleryname, 'gallery_id', 'galleryindex', args.dbfile): # Then the row in galleryindex
                if delete_row('gallery_name', args.galleryname, 'galleryindex', args.dbfile) > 0:
                    print "Deleted row '" + args.galleryname + "' in galleryindex table"
            else:
                print "Gallery '" + args.galleryname + "' not found in galleryindex table."

    if args.subparser_name == 'delimage':
        if raw_input('Really delete image(s)? (y/n): ') in 'Yy':
            for img in args.images:
                if delete_row('imagefile', img, args.galleryname, args.dbfile):
                    print "Deleted image", img, "from gallery", args.galleryname
            
    if args.subparser_name == 'addimages':
        if not find_table(args.galleryname, args.dbfile): # Gallery doesn't exist yet
            print "Creating gallery", args.galleryname
            desc, tags, zipfile, ur, uw, gr, gw = get_user_input('gallery', args.galleryname)
            defpath = get_defpath(os.path.dirname(os.path.realpath(args.images[0]))) # Directory of first image is default defpath
            new_gallery(args.galleryname, defpath, desc, tags, zipfile, ur, uw, gr, gw, args.dbfile)
        else:
            print "Found gallery", args.galleryname
            desc, tags, zipfile, ur, uw, gr, gw = get_user_input('images', args.galleryname) # (zipfile not used on this row)
            zipfile = get_column('galleryname', args.galleryname, 'zipfile', 'galleryindex', args.dbfile)
            defpath = os.path.normpath(get_column('galleryname', args.galleryname, 'defpath', 'galleryindex', args.dbfile))
        add_images(args.images, desc, tags, ur, uw, gr, gw, args.galleryname, args.dbfile) # Finally, add images
        add_to_zip(zipfile, defpath, args.images)
        
    if args.subparser_name == 'test':
        print get_column('gallery_name', 'runor', 'gallery_id', 'galleryindex', args.dbfile)
