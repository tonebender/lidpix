# -*- coding: utf-8 -*-

# image.py
# Lidpix image/thumbnail functions


import os, threading, imghdr
from wand.image import Image

thumbprepping = threading.Event()


def prep_thumbs(imgdir, thumbdir, thumbsize):
    
    """ A wrapper for make_thumbs() that runs that function as its
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
        thumbs = sorted(os.listdir(os.path.abspath(imgdir) + '/' + thumbdir))
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
        imgdir = os.path.normpath(imgdir)
        thumbdir = os.path.normpath(imgdir + '/' + thumbdir)
        if not os.path.exists(thumbdir):
            os.mkdir(thumbdir)
    except OSError as e:
        print(e)
        return (None, None)
    print("THUMBDIRRRR", thumbdir)
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
            print("EXCEPT")
            pass
    return 0       # If we got this far, thumb creation failed


def get_image_info(imagefile):
    
    """ Read the exif info in the image and return it as a dict.
    
    imagefile: the image file with full path
    Return: dict containing all exif info from image, or empty dict """
    
    # http://docs.wand-py.org/en/0.4.4/guide/exif.html
    
    exif = {}
    try:
        with Image(filename = imagefile) as img:
            exif.update((k[5:], v) for k, v in list(img.metadata.items())
                                        if k.startswith('exif:'))
    except:
        pass
    return exif
