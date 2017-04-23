from flask import Flask, request, render_template, flash, redirect, \
url_for, abort, Blueprint, current_app
from wtforms import Form, StringField, PasswordField, BooleanField, validators

lsettings = Blueprint('lsettings', __name__)

class SettingsForm(Form):
    """The settings form class, using WTForms."""
    confirmdelete = BooleanField('Confirm file delete')
#    username = StringField('Username', [validators.Required(), 
#                           validators.Length(min=3)], render_kw={"placeholder": "username"})
#    password = PasswordField('Password', [validators.Required(),
#                             validators.InputRequired()], render_kw={"placeholder": "password"})
