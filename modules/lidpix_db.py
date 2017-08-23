# -*- coding: utf-8 -*-

# lidpix_db.py
#
# Lidpix sqlite3 database functions


import sqlite3, time, os, subprocess, bcrypt
from .image import get_image_info


def safe(s):
    """ Sanitize string s. Only allow a-z, A-Z, 0-9 and _- """
    return ("".join(c for c in s if c.isalnum() or c == '_' or c == '-').rstrip())

    
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


def get_rows(column_to_search, value_to_match, table, db_file):

    """ Get all rows that match a certain value in 1 column.
    Return a list with a tuple for each row. """
    
    try:
        conn, c = connect_to_db(db_file)    
        c.execute('SELECT * FROM {t} WHERE {col}="{value}"'.format(t=safe(table), 
                  col=safe(column_to_search), value=value_to_match))
        row = c.fetchall()
        conn.close()
        return row
    except Exception as e:
        print("Error when trying to get row in table", table, "in", db_file)
        print(e)
        return None


def edit_column(col_to_search, value_to_match, col_to_edit, new_value, table, db_file):
    
    """ On the row(s) where col_to_search has value_to_match, set col_to_edit to new_value. """
    
    try:
        conn, c = connect_to_db(db_file)
        c.execute('UPDATE {t} SET {ce}="{newval}" WHERE {cs}="{vm}"'.format(t=safe(table), 
                  ce=col_to_edit, newval=new_value, cs=col_to_search, vm=value_to_match))
        conn.commit()
        conn.close()
        return c.rowcount
    except Exception as e:
        print("Error when trying to edit row in table", table, "in database file", db_file)
        print(e)
        return 0
    return 0
   

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
            time_photo = get_image_info(img).get('DateTimeOriginal', '(no time)')
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

    
def add_user(username, password, fullname, joined, groups, folders, active, confirmdelete, viewmode, theme, table, db_file):
    
    """ Add a lidpix user to the users table """
    
    try:
        conn, c = connect_to_db(db_file)
        sqlcmd = """INSERT INTO {t} (id, username, password,
        fullname, joined, groups, folders, active, confirmdelete, viewmode, theme)
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""".format(t=safe(table))
        c.execute(sqlcmd, (username, password, fullname, joined, groups, folders, active, confirmdelete, viewmode, theme,))
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
    
    """ Return string with the whole table 'table' in file db_file """
    
    try:
        conn, c = connect_to_db(db_file)
        rows = c.execute('SELECT * FROM {t}'.format(t=safe(table))).fetchall()
        cols = c.execute("PRAGMA table_info({t})".format(t=safe(table))).fetchall()
        conn.close()
        pstring = '\nTABLE            ' + table + '\n'
        r = 1
        for row in rows:
            pstring += '\nROW ' + str(r)
            for i in range(len(cols)):
                pstring += '\n  ' + cols[i][1].ljust(16) + ' '
                if isinstance(row[i], int):
                    pstring += str(row[i])
                elif isinstance(row[i], bytes):
                    pstring += row[i].decode('utf-8')
                else:
                    pstring += row[i]
            pstring += '\n'
            r += 1
        return pstring
    except Exception as e:
        print("Error when trying to print table", table)
        print(e)
        


def add_to_zip(zipfile, zippath, files):
    
    """ Add files to zipfile in zippath. If zipfile exists, and if
    applicable, its contents will be updated. The standard unix
    application zip is used. """
    
    if zipfile == 'n' or zipfile == '':
        return False
    zippath = os.path.normpath(zippath) + '/'
    if os.path.isdir(zippath):
        z = subprocess.call(['zip', '-0', zippath + zipfile] + files)
        if z != 0:
            print("zip returned", z)
            return False
    else:
        print("Could not create zip. Not a valid directory:", zippath)
        return False
    return True


def create_gallery(galleryname, gpath, desc, tags, zipfile, ur, uw, gr, gw, dbfile):
    
    """ Create a new (empty) gallery """
    
    new_table('galleryindex', dbfile, 'gallery_db_schema.sql') # Create gallery index table if not existing
    if add_gallery(galleryname, gpath, desc, tags, zipfile, ur, uw, gr, gw, 'galleryindex', dbfile): # Add gallery to gallery index table
        new_table(galleryname, dbfile, 'image_db_schema.sql') # Create empty image gallery table if not existing
            
