# -*- coding: utf-8 -*-

from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, make_response, Blueprint, current_app
from wand.image import Image
import os, string, threading, time, imghdr
from flask_login import login_required
from modules import authz

folder = Blueprint('folder', __name__)

thumbprepping = threading.Event()


def prep_thumbs(directory, thumbnaildir):

    """ Find all images in directory and make thumbnails in
        directory/thumbs (create subdir if needed).
        Args: Directory where the image files are """
    
    try:
        directory = os.path.normpath(directory) + '/'
        thumbdir = os.path.normpath(directory + thumbnaildir) + '/'
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
        
    prepped = 0
    thumbprepping.clear()
    
    # Go through all instances in imagedir. First, see if file exists,
    # then check if its thumb exists and is newer;
    # if needed create thumbnails (sized 200x px):
    # Since this can be run as a separate thread, set thumbprepping
    # when 6 thumbnails are ready so main thread knows.
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
    

def get_paths(pathname):
    
    """ If pathname is the string '/path/to/dir', this returns
    [['/path', 'path'], ['/path/to', 'to'], ['/path/to/dir', 'dir]] """
    
    pathnames = [pathname.rsplit("/",n)[0]
         for n in range(pathname.count("/")-1,-1,-1)]
    return pathnames
    #return [[d, os.path.basename(d)] for d in pathnames]
    
    

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
    
    class Folderfile:
        def __init__(self, name, thumb):
            self.name = name
            self.thumb = thumb
            # (Space for more file/image properties)

    
    if request.method == 'POST':
        if request.form['imagedir']:
            imagedir = os.path.normpath(request.form['imagedir']) + '/'
        return redirect(url_for('.folder_view', imagedir = imagedir))
        
        
    if request.method == 'GET':
        
        pixdirs = current_app.config['PIXDIRSLIST']
    
        # Get url keywords
        showthumbs = int(request.args.get('showthumbs', default='1'))
        imagedir = os.path.abspath(request.args.get('imagedir', default=pixdirs[0]))
        
        # Get the first folder in pixdirs which is the parent of imagedir
        rootdir = filter(lambda d: imagedir.startswith(d), pixdirs)
        rootdir = rootdir[0] if rootdir else None
        
        # If no rootdir was found, imagedir is not valid, so get outta here
        if not rootdir:
            flash('Forbidden. Directory not setup for access to lidpix.')
            return redirect(url_for('.folder_view', imagedir = pixdirs[0]))
            
        # Create thumbnails
        # This is done in a separate thread so creation can go on in
        # the background while this page loads. Wait until the Event 
        # thumbprepping is set (== at least 4 thumbs done) or 8 seconds
        # have passed, then continue.
        thumbthread = threading.Thread(target=prep_thumbs, args=(imagedir,
                                       'lidpixthumbs',))
        thumbthread.start()
        thumbprepping.wait(8)
        
        # Get a list of available thumbnails
        try:
            thumbs = sorted(os.listdir((imagedir + '/lidpixthumbs/').decode('utf-8')))
        except OSError:
            thumbs = []
        
        # Traverse files in imagedir and create list of file objects
        try:
            files = []
            for n in sorted(os.listdir(imagedir.decode('utf-8'))):
                files.append(Folderfile(n, n if n in thumbs else None))
        except OSError:
            pass
        
        # Create a list of directory paths & names for the pathname buttons
        dirs = get_paths(imagedir)
        dirs = filter(lambda l: l.startswith(rootdir), dirs)
        dirs = [[d, os.path.basename(d)] for d in dirs]
        
        #get_image_info(imagedir + images[0])
        
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
    
