from flask import Flask, request, session, redirect, url_for, abort, \
  render_template, flash, send_from_directory, make_response
import flask.globals as flask_global
from wand.image import Image
import os, string, threading, time, sqlite3
import conf

from modules import authz
#from modules.gallery import gallery

if __name__ == '__main__':
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
    
    # flask-login initialization
    #login_manager = LoginManager()
    #login_manager.login_view = "login"
    #login_manager.login_message = u"Please log in to access this page."
    #login_manager.refresh_view = "reauth"
    #login_manager.init_app(app)

    app.register_blueprint(authz)
    app.register_blueprint(gallery)
