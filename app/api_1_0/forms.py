from flask.ext.wtf import Form
from wtforms import IntegerField,PasswordField,SubmitField,StringField
from wtforms.validators import Required



class LoginForm(Form):
    email = StringField('Email',validators=[Required()])
    password = PasswordField('Password',validators=[Required()])
    submit = SubmitField('submit')