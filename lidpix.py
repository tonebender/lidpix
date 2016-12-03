from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, send_from_directory
from wand.image import Image
import os

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override this config from file in env var
app.config.update(dict(
	PIXDIR='/home/lidbjork/public_html/photos/2011-02/',
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default'
))
app.config.from_envvar('LIDPIX_SETTINGS', silent=True)
app.debug = 1

# imagedir = app.config['PIXDIR']
imagedir = './static/'
thumbdir = imagedir + 'thumbs/'


def prep_images():

	""" Find all images in imagedir and make thumbnails """
	
	prepped = 0
	global thumbdir, imagedir
	
	if not os.path.exists(thumbdir):
		os.mkdir(thumbdir)
		
	# Go through all instances in imagedir. First, check if file,
	# then check existance as a thumb and if thumb is newer;
	# if needed create thumbnails (sized 200*y px)
	for imagefile in os.listdir(imagedir):
		if os.path.isfile(imagedir + imagefile):
			prepped += 1
			if os.path.isfile(thumbdir + imagefile):
				if (os.stat(thumbdir + imagefile).st_mtime >
					os.stat(imagedir + imagefile).st_mtime):
					continue
			try:
				with Image(filename = imagedir + imagefile) as img:
					img.transform(resize='200x')
					img.save(filename = thumbdir + imagefile)
			except Exception:
				print "Error making thumb: ", imagedir+imagefile
			
	return prepped
	

def get_image_info(imagefile):
	
	""" Read the exif info in the image and return it as a dict """
	# http://docs.wand-py.org/en/0.4.4/guide/exif.html
	
	exif = {}
	with Image(filename = imagefile) as img:
		exif.update((k[5:], v) for k, v in img.metadata.items()
									if k.startswith('exif:'))
	return exif
	

@app.route('/gallery', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
	global thumbdir, imagedir
	if request.method == 'POST':
		if request.form['directory']:
			imagedir = os.path.normpath(request.form['directory']) + '/'
			thumbdir = imagedir + 'thumbs/'
		return redirect(url_for('index'))
	if request.method == 'GET':
		prep_images()
		thumbs = os.listdir(thumbdir)
		#get_image_info(imagedir + images[0])
		return render_template('gallery.html', images=sorted(thumbs), thumbdir=thumbdir,
								directory=os.path.abspath(imagedir))
								
@app.route('/thumbs/<filename>')
def download_file(filename):
	print "TD: ", thumbdir
	return send_from_directory(thumbdir, filename)
