from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, send_from_directory
from wand.image import Image
import os, string

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override this config from file in env var
app.config.update(dict(
	PIXDIRS='./static;/home/lidbjork/public_html/photos;/home/lidbjork/Bilder/Foton',
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default'
))
app.config.from_envvar('LIDPIX_SETTINGS', silent=True)
app.debug = 1

# pixdirs becomes a list of all the paths in PIXDIRS
pixdirs = [os.path.normpath(x) for x in string.split(app.config['PIXDIRS'], ';')]


def prep_images(directory):

	""" Find all images in directory and make thumbnails """
	
	prepped = 0
	directory = os.path.normpath(directory)
	thumbdir = directory + '/thumbs/'
	
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
	

# MÅSTE nog använda pathname som ?-parameter i urlen...
@app.route('/gallery', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
	imagedir = pixdirs[0]
	thumbdir = pixdirs[0] + '/thumbs/'
	if request.method == 'POST':
		if request.form['directory']:
			imagedir = os.path.normpath(request.form['directory']) + '/'
			thumbdir = imagedir + 'thumbs/'
		return redirect(url_for('index'))
	if request.method == 'GET':
		prep_images(imagedir)
		thumbs = os.listdir(thumbdir)
		#get_image_info(imagedir + images[0])
		return render_template('gallery.html', images=sorted(thumbs), thumbdir=thumbdir,
								directory=os.path.abspath(imagedir))
								
@app.route('/thumbs/<filename>')
def download_file(filename):
	thumbdir = pixdirs[0] + '/thumbs/'
	return send_from_directory(thumbdir, filename)

@app.route('/test/<pathname>')
def testpath(pathname):
	return pathname
