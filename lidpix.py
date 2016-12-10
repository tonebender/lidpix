from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, send_from_directory, make_response
from wand.image import Image
import os, string, threading, time
import conf

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override this config from file in env var
app.config.update(dict(
    PIXDIRS='./static;/home/lidbjork/public_html/photos;/home/lidbjork/Bilder/Foton',
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_object('conf.DevelopmentConfig')
#app.config.from_envvar('LIDPIX_SETTINGS', silent=True)

# pixdirs becomes a list of all the paths in PIXDIRS
pixdirs = [os.path.normpath(x) for x in string.split(app.config['PIXDIRS'], ';')]

thumbprepping = threading.Event()


def prep_thumbs(directory):

    """ Find all images in directory and make thumbnails in
        directory/thumbs (create subdir if needed).
        Args: Directory where the image files are """
    
    prepped = 0
    thumbprepping.clear()
    directory = os.path.normpath(directory) + '/'
    thumbdir = directory + 'thumbs/'
        
    if not os.path.exists(thumbdir):
        os.mkdir(thumbdir)
        
    # Go through all instances in imagedir. First, see if file exists,
    # then check if its thumb exists and is newer;
    # if needed create thumbnails (sized 200x px):
    # Since this can be run as a separate thread, set thumbprepping
    # when 4 thumbnails are ready so main thread knows.
    for imagefile in os.listdir(directory):
        if prepped > 3:
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
    thumbprepping.set() # In case there were less than 4 thumbs
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
    return [[d, os.path.basename(d)] for d in pathnames]
    
    

@app.route('/gallery', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def gallery():  
    
    """ 
    Show a gallery with thumbnails 
    
    GET: Get image directory from URL keyword; prep thumbnails;
         show gallery.html with thumbnails
    POST: Get new image directory from form and call this again
    """
    
    if request.method == 'POST':
        if request.form['imagedir']:
            imagedir = os.path.normpath(request.form['imagedir']) + '/'
        return redirect(url_for('gallery', imagedir = imagedir))
        
    if request.method == 'GET':
        
        # Get url keywords
        showthumbs = int(request.args.get('showthumbs', default='1'))
        imagedir = request.args.get('imagedir', default=pixdirs[0])
        imagedir = os.path.abspath(imagedir)
        
        # Create thumbnails
        # This is done in a separate thread so creation can go on in
        # the background while this page loads. Wait until Event 
        # thumbprepping is set (at least 4 thumbs ready) or 8 seconds
        # have passed, then continue.
        thumbthread = threading.Thread(target=prep_thumbs, args=(imagedir,))
        thumbthread.start()
        thumbprepping.wait(8)
        thumbs = os.listdir(imagedir + '/thumbs/')
        if not thumbs:
            return "Found no valid images at " + imagedir
        # SHOULD SHOW FOLDERS & SHIT INSTEAD
        
        # Create a list of directory paths & names  
        dirs = get_paths(imagedir)
        
        #get_image_info(imagedir + images[0])
        
        return render_template('gallery.html', thumbs = sorted(thumbs), 
                                imagedir = imagedir,
                                showthumbs = showthumbs,
                                dirs = dirs)

                                
@app.route('/serveimage')
def serveimage():
    
    """ Get image path & file from url keyword and get the image
        from nginx server via X-Accel-Redirect response header """
        
    image = request.args.get('image', default=None) or abort(404)
    response = make_response('')
    response.headers['X-Accel-Redirect'] = image
    del response.headers['Content-Type'] # Webserver decides type later
    return response
    
