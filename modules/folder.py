# -*- coding: utf-8 -*-

from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, make_response, Blueprint, current_app, json
from wand.image import Image
import os, string, threading, time, imghdr
from flask_login import login_required
from modules import authz

folder = Blueprint('folder', __name__)

thumbprepping = threading.Event()


class Folderfile:
    def __init__(self, name, thumb, filetype, datetime):
        self.name = name
        self.thumb = thumb
        self.filetype = filetype
        self.datetime = datetime
        # (Space for more file/image properties)
    
    def to_json(self):
        return {'name': self.name, 'thumb': self.thumb, 
                'filetype': self.filetype, 'datetime': self.datetime}


def prep_thumbs(directory, thumbdir, thumbsize):
    
    """ This wrapper for make_thumbs() runs that function as its
    own thread in the background so the webpage won't be held up (too much),
    then looks for created thumbs and returns them as a list.
    
    Args: same as make_thumbs() below.
    Return: list of available thumbnails."""
    
    tthread = threading.Thread(target=make_thumbs, 
                               args=(directory, thumbdir, thumbsize,))
    tthread.start()
    thumbprepping.wait(8)  # Wait until thumbprepping is done, or 8 seconds
    
    # Get a list of available thumbnails
    try:
        thumbs = sorted(os.listdir((os.path.abspath(directory) + '/' + 
                        thumbdir).decode('utf-8')))
    except OSError:
        thumbs = []
        
    return thumbs


def make_thumbs(directory, thumbdir, thumbsize):

    """ Find all images in directory and make thumbnails in directory/thumbs 
    (create subdir if needed).
    
    directory: the directory with the main images.
    thumbdir: the directory inside directory where thumbs (should) reside.
    thumbsize: a string (e.g. '200') specifying the width of the thumbs
    Return: nothing """
        
    prepped = 0
    thumbprepping.clear()
    
    # Check/prepare directories
    try:
        directory = os.path.normpath(directory) + '/'
        thumbdir = os.path.normpath(directory + thumbdir) + '/'
        if not os.path.exists(thumbdir):
            os.mkdir(thumbdir)
    except OSError:
        return
        
    # Remove existing old thumbs which don't have corresponding images
    try:
        dirlisting = os.listdir(directory)
        for f in os.listdir(thumbdir):
            if f not in dirlisting:
                os.remove(thumbdir + f)
    except:
        pass
    
    # Go through all instances in imagedir. First see if it's a valid file,
    # then check if its thumb exists and is newer; if needed create thumbnails 
    # (sized 200x px). Since this can be run as a separate thread, set the
    # thumbprepping state when 6 thumbnails are ready so main thread knows.
    for imagefile in os.listdir(directory):
        if prepped > 5:
            thumbprepping.set()
        if os.path.isfile(directory + imagefile):
            prepped += 1
            if os.path.isfile(thumbdir + imagefile):
                if (os.stat(thumbdir + imagefile).st_mtime >
                    os.stat(directory + imagefile).st_mtime):
                    continue
            try:
                with Image(filename = directory + imagefile) as img:
                    img.transform(resize = thumbsize + 'x')
                    img.save(filename = thumbdir + imagefile)
            except Exception:
                pass
    thumbprepping.set() # In case there were less than 6 thumbs
    return
    

def get_image_info(imagefile):
    
    """ Read the exif info in the image and return it as a dict.
    
    imagefile: the image file with full path
    Return: dict containing all exif info from image."""
    
    # http://docs.wand-py.org/en/0.4.4/guide/exif.html
    
    try:
        exif = {}
        with Image(filename = imagefile) as img:
            exif.update((k[5:], v) for k, v in img.metadata.items()
                                        if k.startswith('exif:'))
    except:
        return None
    return exif
    

def get_rootdir(imagedir, pixdirs):
    
    """ Find which path in pixdirs is the parent of imagedir, return it.
    
    imagedir: the path to where the images are
    pixdirs: list of paths
    Return: a string containing the rootdir, or None if none was found """
    
    rootdir = filter(lambda d: imagedir.startswith(d), pixdirs)
    return(rootdir[0] if rootdir else None)
    
    
def get_paths(pathname, rootdir):
    
    """ If pathname is the string '/path/to/dir', this returns
    [['/path', 'path'], ['/path/to', 'to'], ['/path/to/dir', 'dir']] 
    Only pathnames which are children of rootdir are kept.
    
    pathname: string containing a pathname to process
    rootdir: string with pathname that should be a subset of pathname
    Return: list with lists (see above) """
    
    pathnames = [pathname.rsplit("/",n)[0]
         for n in range(pathname.count("/")-1,-1,-1)]
    pathnames = filter(lambda l: l.startswith(rootdir), pathnames)
    pathnames = [[d, os.path.basename(d)] for d in pathnames]
    return pathnames


def create_img_objects(imagedir, thumbs):
    
    """ Create Folderfile objects of all the files in imagedir and return
    them in a list.
    
    imagedir: Directory containing the images/files
    thumbs: A list of thumbnail names which hopefully matches the images
    Return: list of Folderfile objects
    """
    
    # Get image info /////////////////////////////////
    #i = get_image_info(imagedir + '/' + sorted(os.listdir(imagedir.decode('utf-8')))[1])
    #for k, v in i.iteritems():
    #    print k, '--', v
        
    try:
        files = []
        for n in sorted(os.listdir(imagedir.decode('utf-8'))):
            if n[0] != '.':
                if os.path.isdir(imagedir + '/' + n):
                    filetype = 'DIR'
                elif os.path.ismount(imagedir + '/' + n):
                    filetype = 'MNT'
                else:
                    filetype = os.path.splitext(n)[1][1:] # Get file extension
                exif = get_image_info(imagedir + '/' + n)
                files.append(Folderfile(n, n if n in thumbs else None, 
                                        filetype, exif['DateTimeOriginal'] if exif else None))
    except OSError:
        pass
    except UnicodeError:
        flash('Unicode error. Directory reading aborted. Encoding: ' + 
              err.encoding + '. Reason: ' + err.reason + '. Object: ' + 
              err.object + '.')
    return files
              

@folder.route('/folder', methods=['GET', 'POST'])
@login_required
def folder_view():
    
    """ 
    Show a folder with thumbnails 
    
    GET: Get image directory from URL keyword; prep thumbnails;
         show folder.html with thumbnails
    POST: Get new image directory from form and call this again
    """
    
    if request.method == 'POST':
        if request.form['imagedir']:
            imagedir = os.path.normpath(request.form['imagedir']) + '/'
        return redirect(url_for('.folder_view', imagedir = imagedir))
        
        
    if request.method == 'GET':
        
        pixdirs = current_app.config['PIXDIRSLIST']
    
        # Get url keywords
        showthumbs = int(request.args.get('showthumbs', default='1'))
        thumbsize = request.args.get('thumbsize', default='200')
        imagedir = os.path.abspath(request.args.get('imagedir', default=pixdirs[0]))
        
        # Find the root dir of the image dir, abort if it's not valid
        rootdir = get_rootdir(imagedir, pixdirs)
        if not rootdir:
            flash('Forbidden. Directory not setup for access to lidpix.')
            return redirect(url_for('.folder_view', imagedir = pixdirs[0]))
            
        # Create a list of directory paths & names for the pathname buttons
        dirs = get_paths(imagedir, rootdir)
            
        # Create thumbnails if needed and get a list of them
        thumbs = prep_thumbs(imagedir, '.lidpixthumbs', thumbsize)
        
        # Create a list of FolderFile objects from all the files in imagedir
        files = create_img_objects(imagedir, thumbs)
        
        return render_template('folder.html', username=authz.current_user.username,
                                files = files,
                                thumbs = thumbs, 
                                imagedir = imagedir,
                                showthumbs = showthumbs,
                                dirs = dirs)


@folder.route('/folderjs', methods=['GET', 'POST'])
@login_required
def folder_view_js():
    
    """ 
    Show a folder with thumbnails 
    This produces a page that JS can fill with thumbnails
    
    GET: Get image directory from URL keyword; prep thumbnails;
         show folder.html with thumbnails
    POST: Get new image directory from form and call this again
    """
    
    if request.method == 'POST':
        if request.form['imagedir']:
            imagedir = os.path.normpath(request.form['imagedir']) + '/'
        return redirect(url_for('.folder_view', imagedir = imagedir))
        
        
    if request.method == 'GET':
        
        pixdirs = current_app.config['PIXDIRSLIST']
    
        # Get url keywords
        showthumbs = int(request.args.get('showthumbs', default='1'))
        thumbsize = request.args.get('thumbsize', default='200')
        imagedir = os.path.abspath(request.args.get('imagedir', default=pixdirs[0]))
        
        # Find valid root dir of the image dir, redirect to default if none
        rootdir = get_rootdir(imagedir, pixdirs)
        if not rootdir:
            flash('Forbidden. Directory not setup for access to lidpix.')
            return redirect(url_for('.folder_view', imagedir = pixdirs[0]))
            
        # Create a list of directory paths & names for the pathname buttons
        dirs = get_paths(imagedir, rootdir)
            
        # Create thumbnails if needed and get a list of them
        thumbs = prep_thumbs(imagedir, '.lidpixthumbs', thumbsize)
        
        # Create a list of FolderFile objects from all the files in imagedir
        files = create_img_objects(imagedir, thumbs)
        
        return render_template('folderjs.html', username=authz.current_user.username,
                                files = files,
                                thumbs = thumbs, 
                                imagedir = imagedir,
                                showthumbs = showthumbs,
                                dirs = dirs)


@folder.route('/supplythumbs', methods=['GET'])
@login_required
def supply_thumbs():
    
    pixdirs = current_app.config['PIXDIRSLIST']

    # Get url keywords
    thumbsize = request.args.get('thumbsize', default='200')
    imagedir = os.path.abspath(request.args.get('imagedir', default=pixdirs[0]))
    
    # Find the root dir of the image dir, abort if it's not valid
    rootdir = get_rootdir(imagedir, pixdirs)
    if not rootdir:
        flash('Forbidden. Directory not setup for access to lidpix.')
        return redirect(url_for('.folder_view', imagedir = pixdirs[0]))
        
    # Create thumbnails if needed and get a list of them
    thumbs = prep_thumbs(imagedir, '.lidpixthumbs', thumbsize)
    
    # Create a list of FolderFile objects from all the files in imagedir
    files = create_img_objects(imagedir, thumbs)
    
    # Convert the files list to json format
    json_files = json.dumps([f.to_json() for f in files])

    return json_files


@folder.route('/serveimage')
def serveimage():
    
    """ Get image path & file from url keyword and get the image
        from nginx server via X-Accel-Redirect response header """
        
    image = request.args.get('image', default=None) or abort(404)
    response = make_response('')
    response.headers['X-Accel-Redirect'] = image
    del response.headers['Content-Type'] # Webserver decides type later
    return response
    
