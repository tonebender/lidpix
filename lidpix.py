from flask import Flask

import conf
import string, os

from modules.authz import authz
from modules.folder import folder

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override this config from file in env var
app.config.update(dict(
    PIXDIRS='/home/lidbjork/Bilder/Foton;/home/lidbjork/public_html/photos',
    USERDB='/home/lidbjork/Develop/python/lidpix/users_example.db',
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_object('conf.DevelopmentConfig')
app.config.from_envvar('LIDPIX_SETTINGS', silent=True)


# Make a list of the PIXDIRS config variable
pixdirs = [os.path.abspath(x) 
           for x in string.split(app.config['PIXDIRS'], ';')]
           
# Remove folder names in pixdirs which are subdirs of other folders in pixdirs
# Example: '/abc/def;/abc;/hey/ho' --> '/abc;/hey/ho'
pixdirs = filter(lambda d: 
                 not any(d.startswith(x) and not d == x for x in pixdirs), 
                 pixdirs)

# After this, we will use this config variable instead of PIXDIRS
app.config['PIXDIRSLIST'] = pixdirs


app.register_blueprint(authz)
app.register_blueprint(folder)
