# -*- coding: utf-8 -*-

from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, make_response, Blueprint, current_app
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


def prep_thumbs(directory, thumbdir):
    
    """ This wrapper for make_thumbs() runs that function as its
    own thread in the background so the webpage won't be held up (too much),
    then looks for created thumbs and returns them as a list.
    
    Args: same as make_thumbs() below.
    Return: list of available thumbnails."""
    
    tthread = threading.Thread(target=make_thumbs, args=(directory, thumbdir,))
    tthread.start()
    thumbprepping.wait(8)  # Wait until thumbprepping is done, or 8 seconds
    
    # Get a list of available thumbnails
    try:
        thumbs = sorted(os.listdir((os.path.abspath(directory) + '/' + 
                        thumbdir).decode('utf-8')))
    except OSError:
        thumbs = []
        
    return thumbs


def make_thumbs(directory, thumbdir):

    """ Find all images in directory and make thumbnails in directory/thumbs 
    (create subdir if needed).
    
    directory: the directory with the main images.
    thumbdir: the directory inside directory where thumbs (should) reside."""
        
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
                    img.transform(resize='200x')
                    img.save(filename = thumbdir + imagefile)
            except Exception:
                pass
    thumbprepping.set() # In case there were less than 6 thumbs
    return
    

def get_image_info(imagefile):
    
    """ Read the exif info in the image and return it as a dict """
    # http://docs.wand-py.org/en/0.4.4/guide/exif.html
    
    exif = {}
    with Image(filename = imagefile) as img:
        exif.update((k[5:], v) for k, v in img.metadata.items()
                                    if k.startswith('exif:'))
    return exif
    

def get_rootdir(imagedir, pixdirs):
    
    """ Find which folder in pixdirs is the parent of imagedir, return it """
    
    rootdir = filter(lambda d: imagedir.startswith(d), pixdirs)
    return(rootdir[0] if rootdir else None)
    
    
def get_paths(pathname, rootdir):
    
    """ If pathname is the string '/path/to/dir', this returns
    [['/path', 'path'], ['/path/to', 'to'], ['/path/to/dir', 'dir']] 
    Only pathnames which are children of rootdir are kept."""
    
    pathnames = [pathname.rsplit("/",n)[0]
         for n in range(pathname.count("/")-1,-1,-1)]
    pathnames = filter(lambda l: l.startswith(rootdir), pathnames)
    pathnames = [[d, os.path.basename(d)] for d in pathnames]
    return pathnames


def create_img_objects(imagedir, thumbs):
    
    """ Create FolderFile objects of all the files in imagedir and return
    them in a list.
    
    imagedir: Directory containing the images/files
    thumbs: A list of thumbnail names which hopefully matches the images
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
                                        filetype, exif['DateTimeOriginal']))
    except OSError:
        pass
    except UnicodeError:
        flash('Unicode error. Directory reading aborted. Encoding: ' + 
              err.encoding + '. Reason: ' + err.reason + '. Object: ' + 
              err.object + '.')
    return files
              

@folder.route('/folder', methods=['GET', 'POST'])
@folder.route('/', methods=['GET', 'POST'])
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
        imagedir = os.path.abspath(request.args.get('imagedir', default=pixdirs[0]))
        
        # Find the root dir of the image dir, abort if it's not valid
        rootdir = get_rootdir(imagedir, pixdirs)
        if not rootdir:
            flash('Forbidden. Directory not setup for access to lidpix.')
            return redirect(url_for('.folder_view', imagedir = pixdirs[0]))
            
        # Create a list of directory paths & names for the pathname buttons
        dirs = get_paths(imagedir, rootdir)
            
        # Create thumbnails if needed and get a list of them
        thumbs = prep_thumbs(imagedir, '.lidpixthumbs')
        
        # Create a list of FolderFile objects from all the files in imagedir
        files = create_img_objects(imagedir, thumbs)
        
        return render_template('folder.html', username=authz.current_user.username,
                                files = files,
                                thumbs = thumbs, 
                                imagedir = imagedir,
                                showthumbs = showthumbs,
                                dirs = dirs)


@folder.route('/serveimage')
def serveimage():
    
    """ Get image path & file from url keyword and get the image
        from nginx server via X-Accel-Redirect response header """
        
    image = request.args.get('image', default=None) or abort(404)
    response = make_response('')
    response.headers['X-Accel-Redirect'] = image
    del response.headers['Content-Type'] # Webserver decides type later
    return response
    
