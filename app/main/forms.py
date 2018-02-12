from flask_wtf import Form
from wtforms import StringField,TextAreaField,BooleanField,SelectField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp
from flask_pagedown.fields import PageDownField


class PostForm(Form):
    body = PageDownField('what is your mind?',validators=[Required()])
    submit=SubmitField('Submit')

class CommentForm(Form):
    body = StringField('',validators=[Required()])
    submit = SubmitField('Submit')

