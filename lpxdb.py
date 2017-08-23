#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

# lpxdb
#
# Lidpix database tool
#
# Handles the lidpix user table, gallery tables with images, 
# and the gallery index table which lists all galleries


import argparse, sys, os, time, bcrypt, imghdr
from modules.lidpix_db import *


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


parser = argparse.ArgumentParser(description='Lidpix database editor')

# const is the default when there are zero values given, default is default when no arg is given at all
parser.add_argument('--dbfile', '-d', nargs='?', dest='dbfile', const='lidpix.db', default='lidpix.db', help='sqlite database file')

subparsers = parser.add_subparsers(dest='subparser_name')    

parser_printtable = subparsers.add_parser('printtable', help='print table to stdout')
parser_printtable.add_argument('table', help='name of the table to print') 

parser_findtable = subparsers.add_parser('findtable', help='find table')
parser_findtable.add_argument('table', help='name of table to find')

parser_deltable = subparsers.add_parser('deltable', help='delete table')
parser_deltable.add_argument('table', help='name of table to delete')

parser_search = subparsers.add_parser('search', help='search field in table')
parser_search.add_argument('table', help='name of table to search')
parser_search.add_argument('key', help='name of column to search')
parser_search.add_argument('value', help='column value to find')

parser_edit = subparsers.add_parser('edit', help='edit field in table')
parser_edit.add_argument('table', help='name of table to edit')
parser_edit.add_argument('find_column', help='column(s) that you want to find')
parser_edit.add_argument('find_value', help='value in column(s) to find')
parser_edit.add_argument('edit_column', help='column(s) to edit')
parser_edit.add_argument('edit_value', help='value to insert')

parser_delgallery = subparsers.add_parser('delgallery', help='delete gallery')
parser_delgallery.add_argument('galleryname', help='name of gallery to delete')

parser_delimage = subparsers.add_parser('delimage', help='delete one or more images from gallery')
parser_delimage.add_argument('galleryname', help='name of gallery from which to delete images (table rows)')
parser_delimage.add_argument('images', nargs='+', help='image file name(s) to delete')

parser_adduser = subparsers.add_parser('adduser', help='add new user to user table')
parser_adduser.add_argument('username', help='username of the new user')
parser_adduser.add_argument('--table', '-t', nargs='?', const='lidpixusers', default='lidpixusers', help='table to add user to')

parser_adduser = subparsers.add_parser('deluser', help='delete user from user table')
parser_adduser.add_argument('username', help='username of the user to delete')
parser_adduser.add_argument('--table', '-t', nargs='?', const='lidpixusers', default='lidpixusers', help='table to delete user from')


parser_newgallery = subparsers.add_parser('newgallery', help='create new gallery (add row to gallery index table, and create image gallery table)')
parser_newgallery.add_argument('galleryname', help='name of gallery to add to table')

parser_addimages = subparsers.add_parser('addimages', help='add images to image gallery table')
parser_addimages.add_argument('galleryname', help='name of image gallery table to record images in') # galleryname is also recorded (on a row) in gallery index table
parser_addimages.add_argument('images', nargs='+', help='image file(s) to add')

parser_test = subparsers.add_parser('test', help='for testing')

if len(sys.argv) == 1:
    parser.print_usage()
    sys.exit(1)

args = parser.parse_args()


# "Low level" table operations

if args.subparser_name == 'printtable':
    print(print_table(args.table, args.dbfile))
    
if args.subparser_name == 'deltable':
    if find_table(args.table, args.dbfile):
        if input("Really delete table " + args.table + "? (y/n) ") in 'Yy':
            if delete_table(args.table, args.dbfile):
                print("Deleted table", args.table, "in file", args.dbfile)
    else:
        print("Could not find table", args.table, "in", args.dbfile)
            
if args.subparser_name == 'findtable':
    if find_table(args.table, args.dbfile):
        print("Table", args.table, "exists")
    else:
        print("Table", args.table, "not found")

if args.subparser_name == 'search':
    rows = get_rows(args.key, args.value, args.table, args.dbfile)
    if rows:
        print(len(rows), "results:")
        print(rows)
    else:
        print("Nothing found")
        
if args.subparser_name == 'edit':
    rows = get_rows(args.find_column, args.find_value, args.table, args.dbfile)
    if rows:
        if input("Found " + str(len(rows)) + " matching rows. Insert '" + \
           args.edit_value + "' in column " + args.edit_column + \
           " in all those rows? (y/n) ") in "yY":
            e = edit_column(args.find_column, args.find_value, \
            args.edit_column, args.edit_value, args.table, args.dbfile)
            if e:
                print("Successfully did", e, "edit(s)")
            else:
                print("Nothing edited")

# User operations

if args.subparser_name == 'adduser':
    pw = input("Please give " + args.username + " a password: ")
    hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    fname = input("User's full name (first and last with space between): ")
    groups = input("The groups user is member of (e.g. 'friends,relatives'): ").lower()
    folders = input("The folders the user should have access to, e.g. '/home/a/b;/home/c/d' (leave blank for lidpix's standard folders):") or 'default'
    joined = time.asctime(time.localtime(time.time()))
    
    new_table(args.table, args.dbfile, 'user_db_schema.sql') # In case it doesn't exist
    if add_user(args.username, hashed_pw, fname, joined, groups, folders, 1, 1, 10, 'default', args.table, args.dbfile):
        print("Successfully added user %s to table %s in file %s" \
        % (args.username, args.table, args.dbfile))

if args.subparser_name == 'deluser':  # Add checking if user exists + prompt!
    if delete_user(args.username, args.table, args.dbfile):
        print("Deleted user %s from table %s in file %s" % (args.username, args.table, args.dbfile))
        

# Image gallery operations

if args.subparser_name == 'newgallery':
    desc, tags, zipfile, ur, uw, gr, gw = get_user_input('gallery', args.galleryname)
    create_gallery(args.galleryname, os.getcwd(), desc, tags, zipfile, ur, uw, gr, gw, args.dbfile)
    
if args.subparser_name == 'delgallery':
    if args.galleryname == 'galleryindex':
        print("Can't delete galleryindex table. Use deltable command if you really want to do that.")
    elif input('Proceed with delete gallery? (y/n) ') in 'Yy':
        if find_table(args.galleryname, args.dbfile): # First try to delete the image table
            if delete_table(args.galleryname, args.dbfile):
                print("Deleted image gallery table '" + args.galleryname + "'")
        else:
            print("Could not find image gallery table '" + args.galleryname + "'")
        if get_column('gallery_name', args.galleryname, 'id', 'galleryindex', args.dbfile): # Then the row in galleryindex
            if delete_row('gallery_name', args.galleryname, 'galleryindex', args.dbfile) > 0:
                print("Deleted row '" + args.galleryname + "' in galleryindex table")
        else:
            print("Gallery '" + args.galleryname + "' not found in galleryindex table.")

if args.subparser_name == 'delimage':
    if input('Proceed with delete image(s)? (y/n): ') in 'Yy':
        for img in args.images:
            if delete_row('imagefile', img, args.galleryname, args.dbfile):
                print("Deleted image", img, "from gallery", args.galleryname)
        
if args.subparser_name == 'addimages':
    try:
        imz = list(filter(lambda x: imghdr.what(x) == None, args.images))
    except: # If imghdr.what gives an error, something is not even a file.
        if input("One or more specified files is non existant or not valid images. Continue? (y/n) ") in 'Nn':
            sys.exit(0)
    else:
        if len(imz) > 0:  # If the list has elements, those are non-images according to imghdr.what
            print("These files don't appear to be valid images:", imz)
            if input("Continue? (y/n) ") in 'Nn':
                sys.exit(0)
    if not find_table(args.galleryname, args.dbfile): # Gallery doesn't exist yet
        print("Creating gallery", args.galleryname)
        desc, tags, zipfile, ur, uw, gr, gw = get_user_input('gallery', args.galleryname)
        gpath = get_gpath(os.path.dirname(os.path.realpath(args.images[0]))) # Directory of first image is default gpath
        create_gallery(args.galleryname, gpath, desc, tags, zipfile, ur, uw, gr, gw, args.dbfile)
    else:
        print("Found gallery", args.galleryname)
        #desc, tags, zipfile, ur, uw, gr, gw = get_user_input('images', args.galleryname) # (zipfile not used on this row)
        desc = get_column('gallery_name', args.galleryname, 'description', 'galleryindex', args.dbfile)[0]
        tags = get_column('gallery_name', args.galleryname, 'tags', 'galleryindex', args.dbfile)[0]
        ur = get_column('gallery_name', args.galleryname, 'users_r', 'galleryindex', args.dbfile)[0]
        uw = get_column('gallery_name', args.galleryname, 'users_w', 'galleryindex', args.dbfile)[0]
        gr = get_column('gallery_name', args.galleryname, 'groups_r', 'galleryindex', args.dbfile)[0]
        gw = get_column('gallery_name', args.galleryname, 'groups_w', 'galleryindex', args.dbfile)[0]
        zipfile = get_column('gallery_name', args.galleryname, 'zipfile', 'galleryindex', args.dbfile)[0]
        gpath = os.path.normpath(get_column('gallery_name', args.galleryname, 'gpath', 'galleryindex', args.dbfile)[0])
    add_images(args.images, desc, tags, ur, uw, gr, gw, args.galleryname, args.dbfile) # Finally, add images
    print("Adding to zipfile:")
    add_to_zip(zipfile, gpath, args.images)
    
if args.subparser_name == 'test':
    print(get_column('gallery_name', 'runor', 'id', 'galleryindex', args.dbfile))

# https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/
