# -*- coding: utf-8 -*-

import os, string, time
from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, make_response, Blueprint, current_app, json
from flask_login import login_required
import authz, folder
# from modules import authz, folder
from lidpix_db import *  # just select needed ones!

gallery = Blueprint('gallery', __name__)


class Img:
    def __init__(self, image_id, imagefile, desc, tags, time_photo, time_added, 
                 users_r, users_w, groups_r, groups_w):
        self.image_id = image_id
        self.imagefile = imagefile
        self.desc = desc
        self.tags = tags        
        self.time_photo = time_photo
        self.time_added = time_added
        self.users_r = users_r
        self.users_w = users_w
        self.groups_r = groups_r
        self.groups_w = groups_w
        

class Gallery:
    def __init__(self, gallery_id, gallery_name, defpath, desc, tags, time_added, zipfile, users_r, users_w, groups_r, groups_w):
        self.gallery_id = gallery_id
        self.gallery_name = gallery_name
        self.defpath = defpath
        self.desc = desc
        self.tags = tags
        self.time_added = time_added
        self.zipfile = zipfile
        self.users_r = users_r
        self.users_w = users_w
        self.groups_r = groups_r
        self.groups_w = groups_w
        self.images = []
        


def db_get_galleryprops(galleryname):
    
    """ Get row with gallery properties in gallery db """
    
    # Use function in lidpix_db which returns row?
    
    return Gallery_object
    
    
def db_get_img(something):
    
    """ Get row of data for one image in gallery db """
    
    return Img_object


def db_get_images(galleryname):
    
    """ Get all rows (images) from a gallery in db """
    
    return list_of_Img_objects
