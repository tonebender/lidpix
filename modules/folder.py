# -*- coding: utf-8 -*-

import os, string, threading, time, imghdr
from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, make_response, Blueprint, current_app, json
from werkzeug.utils import secure_filename
from wand.image import Image
from flask_login import login_required
from modules import authz, lsettings

folder = Blueprint('folder', __name__)

thumbprepping = threading.Event()


class Folderfile:
    def __init__(self, name, filetype, datetime):
        self.name = name
        self.filetype = filetype
        self.datetime = datetime
        # (Space for more file/image properties)
    
    def to_json(self):
        return {'name': self.name, 'filetype': self.filetype,
                'datetime': self.datetime}


def allowed_file(filename):
    
    """ Return true if extension in filename is in UPLOAD_EXTENSIONS """
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in \
           current_app.config['UPLOAD_EXTENSIONS']


def prep_thumbs(imgdir, thumbdir, thumbsize):
    
    """ This wrapper for make_thumbs() runs that function as its
    own thread in the background so the webpage won't be held up (too much),
    then looks for created thumbs and returns them as a list.
    
    Args: same as make_thumbs() below.
    Return: list of available thumbnails."""
    
    tthread = threading.Thread(target=make_thumbs, 
                               args=(imgdir, thumbdir, thumbsize,))
    tthread.start()
    thumbprepping.wait(8)  # Wait until thumbprepping is done, or 8 seconds
    
    # Get a list of available thumbnails
    try:
        thumbs = sorted(os.listdir((os.path.abspath(imgdir) + '/' + 
                        thumbdir).decode('utf-8')))
    except OSError:
        thumbs = []
        
    return thumbs


def make_thumbs(imgdir, thumbdir, thumbsize):

    """ Find all images in imgdir and make thumbnails in imgdir/thumbs 
    (create subdir if needed).
    
    imgdir: the directory with the main images.
    thumbdir: the directory inside imgdir where thumbs (should) reside.
    thumbsize: geometry string (e.g. '200x') specifying the thumb size
    Return: nothing """
        
    prepped = 0
    thumbprepping.clear()
    
    # Prepare directories and get absolute paths
    (imgdir, thumbdir) = prep_thumbdir(imgdir, thumbdir)
    if imgdir == None:
        thumbprepping.set()
        return
        
    purge_thumbs(imgdir, thumbdir)
    
    # Go through all instances in imagedir and create thumbs.
    # Since this can be run as a separate thread, set the thumbprepping state 
    # when 6 thumbnails are ready so main thread knows.
    for imagefile in os.listdir(imgdir):
        if prepped > 5:
            thumbprepping.set()
        prepped += create_thumb(imgdir, thumbdir, imagefile, thumbsize)
    
    thumbprepping.set() # In case there were less than 6 thumbs
    return


def prep_thumbdir(imgdir, thumbdir):
    
    """Create thumbdir inside of imgdir if thumbdir ain't already there.
       Return a tuple with the normalized absolute paths of imgdir and
       thumbdir if successful, or (None, None) if unsuccessful."""
    
    try:
        imgdir = os.path.normpath(imgdir) + '/'
        thumbdir = os.path.normpath(imgdir + thumbdir) + '/'
        if not os.path.exists(thumbdir):
            os.mkdir(thumbdir)
    except OSError:
        return (None, None)
    return (imgdir, thumbdir)


def purge_thumbs(imgdir, thumbdir):
    
    """Remove existing old thumbs in thumbdir which don't have corresponding 
       images in imgdir."""
       
    try:
        dirlisting = os.listdir(imgdir)
        for f in os.listdir(thumbdir):
            if f not in dirlisting:
                os.remove(thumbdir + f)
    except:
        pass


def create_thumb(imgdir, thumbdir, imagefile, thumbsize):
    
    """Create a thumbnail from the imagefile.
       If a matching & fresh thumbnail already exists, just return 1.
       If requested thumb is larger than the original, just make a symlink
       to the original in the thumbs directory.
    
    imgdir: directory where image resides (/abs/path/)
    thumbdir: directory where thumb should be placed (/abs/path/)
    imagefile: name of imagefile in imgdir
    thumbsize: string such as "200x" or "175x100". If it's '1' or empty,
               create a symbolic link instead of real thumbnail
    Return: number of thumbnails done (1 or 0) """
    
    if os.path.isfile(imgdir + imagefile): # Image exists?
        if os.path.isfile(thumbdir + imagefile): # Thumb already exists?
            if (os.stat(thumbdir + imagefile).st_mtime > # Thumb newer than img?
                os.stat(imgdir + imagefile).st_mtime):
                return 1                                 # No need to create
        w, h = thumbsize.split('x')
        try:
            if thumbsize == '' or thumbsize == '1': # Full-size thumb = symlink
                os.symlink(imgdir + imagefile, thumbdir + imagefile)
                return 1
            with Image(filename = imgdir + imagefile) as img:  # Create thumb
                if int(img.width) > int(w) or int(img.height) > int(h):    # If requested size is 
                    img.transform(resize = thumbsize)  # smaller than original
                    img.save(filename = thumbdir + imagefile)
                else:                                # Otherwise, make symlink
                    os.symlink(imgdir + imagefile, thumbdir + imagefile)
            return 1
        except Exception:
            pass
    return 0       # If we got this far, thumb creation failed


def get_image_info(imagefile):
    
    """ Read the exif info in the image and return it as a dict.
    
    imagefile: the image file with full path
    Return: dict containing all exif info from image, or empty dict"""
    
    # http://docs.wand-py.org/en/0.4.4/guide/exif.html
    
    exif = {}
    try:
        with Image(filename = imagefile) as img:
            exif.update((k[5:], v) for k, v in img.metadata.items()
                                        if k.startswith('exif:'))
    except:
        pass
    return exif
    

def get_rootdir(imagedir, pixdirs):
    
    """ Find which path in pixdirs is the parent of imagedir, return it.
    
    imagedir: the path to where the images are
    pixdirs: list of paths
    Return: a string containing the rootdir, or None if none was found """
    
    rootdir = filter(lambda d: imagedir.startswith(d), pixdirs)
    return(rootdir[0] if rootdir else None)
    
    
def get_breadcrumbs(pathname, rootdir):
    
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


def create_img_objects(imagedir):
    
    """ Create Folderfile objects of all the files in imagedir and return
    them in a list.
    
    imagedir: Directory containing the images/files
    Return: list of Folderfile objects
    """
        
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
                datetime = exif.get('DateTimeOriginal', '(no time)')
                files.append(Folderfile(n, filetype, datetime))
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
        thumbsize = request.args.get('thumbsize', default='200x')
        imagedir = os.path.abspath(request.args.get('imagedir', default=pixdirs[0]))
        
        # Find the root dir of the image dir, abort if it's not valid
        rootdir = get_rootdir(imagedir, pixdirs)
        if not rootdir:
            flash('Forbidden. Directory not setup for access to lidpix.')
            return redirect(url_for('.folder_view', imagedir = pixdirs[0]))
            
        # Create a list of directory paths & names for the breadcrumbs buttons
        dirs = get_breadcrumbs(imagedir, rootdir)
        
        # Create a list of FolderFile objects from all the files in imagedir
        # (Only used by non-javascript browsers)
        files = create_img_objects(imagedir)
        
        # Create the settings form
        settingsform = lsettings.SettingsForm(request.form)
        
        return render_template('folder.html', username=authz.current_user.username,
                                files = files,
                                imagedir = imagedir,
                                dirs = dirs,
                                thumbsize = thumbsize,
                                settingsform = settingsform)


@folder.route('/getdir', methods=['GET'])
@login_required
def supply_dir():
    
    pixdirs = current_app.config['PIXDIRSLIST']

    # Get url keywords
    thumbsize = request.args.get('thumbsize', default='200x')
    imagedir = os.path.abspath(request.args.get('imagedir', default=pixdirs[0]))
    
    # Find the root dir of the image dir, abort if it's not valid
    rootdir = get_rootdir(imagedir, pixdirs)
    if not rootdir:
        flash('Forbidden. Directory not setup for access to lidpix.')
        return redirect(url_for('.folder_view', imagedir = pixdirs[0]))
    
    # Create a list of FolderFile objects from all the files in imagedir
    files = create_img_objects(imagedir)
    
    print [f.to_json() for f in files]
    # Convert the files list to json format
    json_files = json.dumps([f.to_json() for f in files])

    return json_files


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


@folder.route('/settings')
def settings():
    
    """Show the settings dialog (page) """
    
    return render_template('settings.html')
