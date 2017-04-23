from flask import Flask, request, render_template, flash, redirect, \
url_for, abort, Blueprint, current_app
from wtforms import Form, StringField, PasswordField, BooleanField, validators
from flask_login import (LoginManager, current_user, login_required, \
login_user, logout_user, UserMixin, confirm_login, login_url, \
fresh_login_required)
import sqlite3, bcrypt


authz = Blueprint('authz', __name__)
