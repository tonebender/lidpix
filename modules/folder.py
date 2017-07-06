# -*- coding: utf-8 -*-

import os, string, threading, time, imghdr, sys
from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, make_response, Blueprint, current_app, json
from werkzeug.utils import secure_filename
from flask_login import login_required
from wtforms import Form, StringField, BooleanField, validators
from .image import *
from .lidpix_db import get_row, get_all_rows
from . import authz


folder = Blueprint('folder', __name__)


class Imagefile:
    def __init__(self, file_id, name, desc, tags, time_photo, 
    time_added, users_r, users_w, groups_r, groups_w, filetype=''):
        self.file_id = file_id
        self.name = name
        self.desc = desc
        self.tags = tags
        self.time_photo = time_photo
        self.time_added = time_added
        self.users_r = users_r
        self.users_w = users_w
        self.groups_r = groups_r
        self.groups_w = groups_w
        self.filetype = filetype
    
    def to_dict(self):
        return {'file_id': self.file_id, 'name': self.name, 
        'desc': self.desc, 'tags': self.tags,
        'time_photo': self.time_photo, 'time_added': self.time_added, 
        'users_r': self.users_r, 'users_w': self.users_w, 
        'groups_r': self.groups_r, 'groups_w': self.groups_w,
        'filetype': self.filetype}
        
class Gallery:
    def __init__(self, gallery_id, gallery_name, gpath, desc, tags, 
    time_added, zipfile, users_r, users_w, groups_r, groups_w):
        self.gallery_id = gallery_id
        self.gallery_name = gallery_name
        self.gpath = gpath
        self.desc = desc
        self.tags = tags
        self.time_added = time_added
        self.zipfile = zipfile
        self.users_r = users_r
        self.users_w = users_w
        self.groups_r = groups_r
        self.groups_w = groups_w
        self.images = []
        
    def to_dict(self):
        return {'gallery_id': self.gallery_id, 'gallery_name': self.gallery_name,
        'gpath': self.gpath, 'desc': self.desc, 'tags': self.tags,
        'time_added': self.time_added, 'zipfile': self.zipfile,
        'users_r': self.users_r, 'users_w': self.users_w, 'groups_r':
        self.groups_r, 'groups_w': self.groups_w, 'images': [i.to_dict() for i in self.images]}

        
class SettingsForm(Form):
    """The settings form, a subclass of Form (using WTForms)."""
    settingsconfirmdelete = BooleanField('Confirm file delete')
        


def allowed_file(filename):
    
    """ Return true if extension in filename is in UPLOAD_EXTENSIONS """
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in \
           current_app.config['UPLOAD_EXTENSIONS']
    

def get_rootdir(imagedir, pixdirs):
    
    """ Find which path in pixdirs is the parent of imagedir, return it.
    
    imagedir: the path to where the images are
    pixdirs: list of paths
    Return: a string containing the rootdir, or None if none was found """
    
    rootdir = [d for d in pixdirs if imagedir.startswith(d)]
    return(rootdir[0] if rootdir else None)
    
    
def get_breadcrumbs(pathname, rootdir):
    
    """ If pathname is the string '/path/to/dir', this returns
    [['/path', 'path'], ['/path/to', 'to'], ['/path/to/dir', 'dir']] 
    Only pathnames which are children of rootdir are kept.
    
    pathname: string containing a pathname to process
    rootdir: string with pathname that should be a subset of pathname
    Return: list with lists (see above) 
    """
    
    pathnames = [pathname.rsplit("/",n)[0]
         for n in range(pathname.count("/")-1,-1,-1)]
    pathnames = [l for l in pathnames if l.startswith(rootdir)]
    pathnames = [[d, os.path.basename(d)] for d in pathnames]
    return pathnames


def dir_to_img_objects(imagedir):
    
    """ Create Imagefile objects of all the files in imagedir and return
    them in a list.
    
    imagedir: Directory containing the images/files
    Return: list of Imagefile objects
    """
        
    try:
        files = []
        i = 0
        for n in sorted(os.listdir(imagedir)):
            if n[0] != '.':
                if os.path.isdir(imagedir + '/' + n):
                    filetype = 'DIR'
                elif os.path.ismount(imagedir + '/' + n):
                    filetype = 'MNT'
                else:
                    filetype = os.path.splitext(n)[1][1:] # Get file extension
                if filetype in 'jpg jpeg png gif tiff pcx bmp':
                    datetime = get_image_info(imagedir + '/' + n).get('DateTimeOriginal', '(no time)')
                else:
                    datetime = '(no time)'
                files.append(Imagefile(i, n, '', '', datetime, '', '', 
                '', '', '', filetype))
                i += 1
    except OSError:
        pass
    except UnicodeError:  # This is from the python 2.7 period ... probably obsolete now
        flash('Unicode error. Directory reading aborted. Encoding: ' + 
              err.encoding + '. Reason: ' + err.reason + '. Object: ' + 
              err.object + '.')
    return files
              

@folder.route('/get_app_settings', methods=['GET'])
def get_app_settings():
    
    """ Supply this app's settings via json for the javascript """
    
    appsettings = {'tumbdirbase': current_app.config['THUMBDIR_BASE'],
                   'imageext': list(current_app.config['IMAGE_EXT']),
                   'viewmode': current_app.config['VIEWMODE']}
    if authz.current_user.is_authenticated:
        appsettings.update({'pixdirs': current_app.config['PIXDIRSLIST']})
    return json.dumps(appsettings)

    
@folder.route('/serveimage')
def serveimage():
    
    """ Get image path & file from url keyword and get the image
        from nginx server via X-Accel-Redirect response header """
        
    image = request.args.get('image', default=None) or abort(404)
    response = make_response('')
    response.headers['X-Accel-Redirect'] = image
    del response.headers['Content-Type'] # Webserver decides type later
    return response


@folder.route('/servethumb')
def servethumb():
    
    """ Create & serve thumbnail on the fly!
    
    Takes two url keys: image (required), thumbsize
    'image' key should have full /path/with/imagefilename """
    
    image = request.args.get('image', default=None) or abort(404)
    (imgdir, imagefile) = os.path.split(image)
    thumbsize = request.args.get('thumbsize', default='200x')
        
    # thumbdir is based on config and thumbsize, e.g. '.lidpixthumbs_200x'
    thumbdir = current_app.config['THUMBDIR_BASE']
    (imgdir, thumbdir) = prep_thumbdir(imgdir, thumbdir + '_' + thumbsize)
    
    if create_thumb(imgdir, thumbdir, imagefile, thumbsize):
        return redirect(url_for('.serveimage', image=thumbdir+'/'+imagefile))
    else:
        abort(404)


@folder.route('/folder_json', methods=['GET'])
@folder.route('/folder', methods=['GET', 'POST'])
@login_required
def folder_view():
    
    """ 
    Render folder with thumbnails (/folder)
    or provide thumbnails as JSON (/folder_json)
    (Some of the stuff in the non-json case is just for 
    non-javascript users.)
    
    GET: Get image directory and thumbsize from URL keyword; 
         prep thumbnails;
           show folder.html
           or
           send json object with thumbnails
             
    POST: Get new image directory from form and call this again
    """
    
    if request.method == 'POST':
        if request.form['imagedir']:
            imagedir = os.path.normpath(request.form['imagedir']) + '/'
        return redirect(url_for('.folder_view', name = imagedir))
        
        
    if request.method == 'GET':
        
        pixdirs = current_app.config['PIXDIRSLIST']
        imagedir = request.args.get('name') # URL keyword
        #thumbsize = request.args.get('thumbsize', default='200x')   # Only used for noscript
        if not imagedir:  # Need to reload page if no imagedir, because JS needs proper URL keyword
            return redirect(url_for('.folder_view', imagedir=pixdirs[0], thumbsize=thumbsize))
        if imagedir == 'null':    # Can be null when JS is getting json and lacks url keyword
            imagedir = pixdirs[0] # (shouldn't really happen if the redirect above works)
        imagedir = os.path.abspath(imagedir)
        
        # Find the root dir of the image dir, abort if it's not authorized (in pixdirs)
        rootdir = get_rootdir(imagedir, pixdirs)
        if not rootdir:
            flash('Forbidden. Directory not setup for access to lidpix.')
            return redirect(url_for('.folder_view', name = pixdirs[0]))
        
        # Create a list of Imagefile objects from all the files in imagedir
        files = dir_to_img_objects(imagedir)
        
        if 'folder_json' in request.path: # Supply JSON
            json_files = json.dumps([f.to_dict() for f in files])
            return json_files
        else:                  # Supply folder view
            dirs = get_breadcrumbs(imagedir, rootdir)
            settingsform = SettingsForm(request.form)
            return render_template('folder.html', username=authz.current_user.username,
                                    files = files,
                                    imagedir = imagedir,
                                    dirs = dirs,
                                    settingsform = settingsform)


@folder.route('/gallery', methods=['GET'])
@folder.route('/gallery_json', methods=['GET'])
@login_required
def gallery_view():
    
    """Show a gallery with thumbnails/images found through database
    
    GET: Get gallery name from URL keyword and look it up in the db, und zo weiter
    """
    
    galleryname = request.args.get('name') #, default='defaultgallery')
    if not galleryname:  # Need to reload page if no name, because JS needs proper URL keyword
        return redirect(url_for('.gallery', name='defaultgallery'))
    if galleryname == 'null':    # Can be null when JS is getting json and lacks url keyword
        galleryname = 'defaultgallery' # (shouldn't really happen if the redirect above works)
        
    gallery_row = get_row('gallery_name', galleryname, 'galleryindex', 'lidpix.db')
    gallery = Gallery(*gallery_row) # Make one Gallery object from galleryindex database row
    
    if not authz.user_access(gallery):
        if 'gallery_json' in request.path:
            abort(403) # Maybe change to something jsonish that JS can interpret
        else:
            flash('Sorry. User ' + current_user.username + ' does not have read access to this gallery.')
            return redirect(url_for('/', name='defaultgallery'))
    
    image_rows = get_all_rows(galleryname, 'lidpix.db') # Get list with one tuple for every row in image db
    for i in image_rows:
        gallery.images.append(Imagefile(*i)) # Make Imagefile object of every tuple
    
    if 'gallery_json' in request.path: # Supply JSON
        return json.dumps(gallery.to_dict())
    else:
        settingsform = SettingsForm(request.form)
        return render_template('folder.html', username=authz.current_user.username,
                                files=[],
                                imagedir='',
                                dirs=[],
                                settingsform=settingsform)


# This function is not finished!
@folder.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))
    return false
