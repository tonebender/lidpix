# -*- coding: utf-8 -*-

# lidpix_db.py
#
# Lidpix sqlite3 database functions


import sqlite3, time, os, subprocess, bcrypt
from .image import get_image_info


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
        print("Could not open database:", db_file)
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
            scriptlines = "CREATE TABLE IF NOT EXISTS " + safe(table) + "\n(" + f.read() + ");"
        c.executescript(scriptlines)
        conn.commit()
        conn.close()
    except Exception as e:
        print("Error when trying to create table " + table + " in" + db_file)
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
        print("Error when trying to find table " + table + " in database file " + db_file)
        return False
    else:
        return fetched
        

def delete_table(table, db_file):
    
    """ Delete existing table in database file """
    
    try:
        conn, c = connect_to_db(db_file)
        c.execute("DROP TABLE IF EXISTS " + safe(table) + ";")
        conn.close()
    except Exception as e:
        print("Error when trying to delete table " + table + " in database file " + db_file)
        print(e)
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
        print("Error when trying to delete row in table", table, "in", db_file)
        print(e)
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
        print("Error when trying to fetch row in table", table, "in database file", db_file)
        print(e)
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
        print("Error when trying to get row in table", table, "in", db_file)
        print(e)
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
        print("Error when trying to fetch all rows in table", table, "in", db_file)
        print(e)
        return []
        

def add_gallery(galleryname, gpath, description, tags, zipfile, 
                users_r, users_w, groups_r, groups_w, table, db_file):
    
    """ Add a row with gallery properties to a gallery index table """
    
    try:
        conn, c = connect_to_db(db_file)
        sql_cmd = """INSERT INTO {t}
        (id, gallery_name, gpath, description, tags, 
        time_added, zipfile, users_r, users_w, groups_r, groups_w)
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""".format(t=safe(table))
        c.execute(sql_cmd, (galleryname, gpath, description, tags,
                            time.asctime(time.localtime(time.time())),
                            zipfile, users_r, users_w, groups_r, groups_w,))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Error when trying to add gallery in table " + table + \
        " in " + db_file)
        print(e)
        return False
    else:
        return True


def add_images(imagefiles, description, tags, users_r, 
               users_w, groups_r, groups_w, table, db_file):
    
    """ Add one or more rows with image properties to an image (gallery) table """
    
    try:
        conn, c = connect_to_db(db_file)
        sql_cmd = """INSERT INTO {t} 
            (id, imagefile, description, tags, time_photo, 
            time_added, users_r, users_w, groups_r, groups_w)
            VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?);""".format(t=safe(table))
        time_added = time.asctime(time.localtime(time.time()))
        print("Adding images to table " + table + ":")
        for img in imagefiles:
            if img[-4:].lower() == '.zip': # Don't include our own zip
                continue
            time_photo = folder.get_image_info(img).get('DateTimeOriginal', '(no time)')
            c.execute(sql_cmd, (os.path.basename(img), description, tags, time_photo,
                  time_added, users_r, users_w, groups_r, groups_w,))
            print(img)
        conn.commit()
        conn.close()
    except Exception as e:
        print("Error when trying to add images in table", table, "in", db_file)
        print(e)
        return False
    else:
        return True

    
def add_user(username, password, fullname, joined, groups, table, db_file):
    
    """ Add a lidpix user to the users table """
    
    try:
        conn, c = connect_to_db(db_file)
        sqlcmd = """INSERT INTO {t} (id, username, password,
        fullname, groups, joining, active, confirmdelete, viewmode, theme)
        VALUES (NULL, ?, ?, ?, ?, ?, 1, 1, 10, "default");""".format(t=safe(table))
        #sql_command = format_str.format(table=safe(table), username=username, password=password, \
        #fullname=fullname, joined=joined, groups=groups)
        print(type(password))
        c.execute(sqlcmd, (username, password, fullname, joined, groups,))
        conn.commit()
        conn.close()
    except Exception as e:
        print("add_user(): Error when trying to add user " + username + \
        " in table " + table + " in " + db_file)
        print(e)
        return False
    else:
        return True
        

def delete_user(username, table, db_file):
    
    """ Remove a lidpix user from the users table """
    
    try:
        conn, c = connect_to_db(db_file)
        command = "DELETE FROM {table} WHERE username =?".format(table=safe(table))
        c.execute(command, (username,))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Error when trying to delete user " + username + \
        " from table " + table + " in file " + db_file)
        print(e)
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
        print('\nTABLE           ', table, '\n')
        r = 1
        for row in rows:
            print("ROW", r)
            for i in range(len(cols)):
                print(' ', cols[i][1].ljust(16), (str(row[i]) if isinstance(row[i],int) else row[i]))
            print('')
            r += 1
    except Exception as e:
        print("Error when trying to print table", table)
        print(e)
        

def get_user_input(genre, galleryname):
    
    """ Get input from user and return as a tuple, to use when adding 
    gallery, images, etc.
        
    genre: String to use in message, e.g. 'gallery' or 'images' """
    
    desc = input("Enter description of %s (single line): " % genre)
    tags = input("Enter comma-separated tags describing %s (e.g. 'pets,dogs,cats'): " % genre)
    users_r = input("Users to give read permission to %s (e.g. 'silvio,vladimir'): " % genre)
    users_w = input("Users to give write permission to %s (e.g. 'barack,angela'): " % genre)
    group_r = input("Group to give read permission to %s (e.g. 'colleagues,friends'): " % genre)
    group_w = input("Group to give write permission to %s (e.g. 'management,workers'): " % genre)
    zipfile = ''
    if genre == 'gallery':
        zipfile = input("Create zipfile? (y/n): ").lower()
        if zipfile == '' or zipfile == 'y':
            zipfile = galleryname + '.zip'
        else:
            zipfile = 'n'
    return (desc, tags, zipfile, users_r, users_w, group_r, group_w)


def get_gpath(gpath):
    """ Let user specify default path for images in gallery """
    userpath = input("Base path for images [%s]: " % gpath)
    if userpath == '':
        userpath = gpath
    return userpath
    

def add_to_zip(zipfile, zippath, files):
    if zipfile == 'n' or zipfile == '':
        return False
    zippath = os.path.normpath(zippath) + '/'
    if os.path.isdir(zippath):
        print("Adding to zipfile:")
        z = subprocess.call(['zip', '-0', zippath + zipfile] + files)
        if z != 0:
            print("zip returned", z)
            return False
    else:
        print("Could not create zip. Not a valid directory:", zippath)
        return False
    return True


def create_gallery(galleryname, gpath, desc, tags, zipfile, ur, uw, gr, gw, dbfile):
    """ Create a new gallery """
    new_table('galleryindex', dbfile, 'gallery_db_schema.sql') # Create gallery index table if not existing
    if add_gallery(galleryname, gpath, desc, tags, zipfile, ur, uw, gr, gw, 'galleryindex', dbfile): # Add gallery to gallery index table
        print("Added gallery", galleryname, "to galleryindex table")
        new_table(galleryname, dbfile, 'image_db_schema.sql') # Create empty image gallery table if not existing
            
