# -*- coding: utf-8 -*-

import os, string, time
from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, make_response, Blueprint, current_app, json
from flask_login import login_required
import authz, folder
# from modules import authz, folder
from lidpix_db import *

gallery = Blueprint('gallery', __name__)


class Galleryprop:
    def __init__(self, gallery_name, users_r, users_w, groups_r, groups_w):
        self.gallery_name = gallery_name
        self.users_r = users_r
        self.users_w = users_w
        self.groups_r = groups_r
        self.groups_w = groups_w
        
class Galleryfile:
    def __init__(self, image_id, imagefile, time_photo, time_added, 
                 users_r, users_w, groups_r, groups_w):
        self.image_id = image_id
        self.imagefile = imagefile
        self.time_photo = time_photo
        self.time_added = time_added
        self.users_r = users_r
        self.users_w = users_w
        self.groups_r = groups_r
        self.groups_w = groups_w


def gb_get_gallery_properties():
    
    """ Get row with gallery properties in gallery db """
    
    return Galleryprop_object
    
    
def db_get_image():
    
    """ Get row of data for one image in gallery db """
    
    return Galleryfile_object
