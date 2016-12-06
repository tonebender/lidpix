from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, send_from_directory, make_response
from wand.image import Image
import os, string
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


def prep_images(directory):

	""" Find all images in directory and make thumbnails.
	    
	    Args: Directory where the image files lay.
	    Return: number of processed images (even if done before).
	"""
	
	prepped = 0
	directory = os.path.normpath(directory) + '/'
	thumbdir = directory + 'thumbs/'
	
	print "dir: -%s-" % directory
	print "thumbdir: -%s-" % thumbdir
	
	if not os.path.exists(thumbdir):
		os.mkdir(thumbdir)
		
	# Go through all instances in imagedir. First, check if file,
	# then check existance as a thumb and if thumb is newer;
	# if needed create thumbnails (sized 200*y px)
	for imagefile in os.listdir(directory):
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
			
	return prepped
	

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
	the list ['/path', '/path/to', '/path/to/dir'] """
	#functools.reduce(lambda a, b: a+[a[-1]+b+'/'], '/path/to/some/dir'.split('/'), [''])
	#[dir.rsplit("/",n)[0] for n in range(dir.count("/")-1,0,-1)]
	subpath = os.path.dirname(pathname)
	if subpath != '/':
		return get_paths(subpath) + [pathname]
	else:
		return [pathname]
	

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
		showthumbs = int(request.args.get('showthumbs', default='1'))
		imagedir = request.args.get('imagedir', default=pixdirs[0])
		imagedir = os.path.normpath(imagedir)
		p = prep_images(imagedir)
		thumbs = os.listdir(imagedir + '/thumbs/')
		if not p or not thumbs:
			return "Found no valid images at " + imagedir
		dirs = [[d, os.path.basename(d)] for d in get_paths(imagedir)]
		#get_image_info(imagedir + images[0])
		return render_template('gallery.html', thumbs = sorted(thumbs), 
								imagedir = os.path.abspath(imagedir),
								showthumbs = showthumbs,
								dirs = dirs)

								
@app.route('/serveimage')
def serveimage():
	
	""" Get image path & file from url keyword and get the image
	    from nginx server via X-Accel-Redirect response header """
	    
	image = request.args.get('image', default=None) or abort(404)
	response = make_response('')
	response.headers['X-Accel-Redirect'] = image
	del response.headers['Content-Type']
	return response
	
