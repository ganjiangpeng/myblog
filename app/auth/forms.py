#coding=utf-8
from flask_wtf import Form
from wtforms import StringField,SubmitField,PasswordField,BooleanField,TextAreaField,SelectField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User,Role

#用户登录表单
class LoginForm(Form):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('keep me logged in')
    submit=SubmitField('Log In')
#用户注册表单
class RegistrationForm(Form):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    username = StringField('Username',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
        'Usernames must have only letters, '
        'numbers, dots or underscores')])
    password = PasswordField('Password',validators=[Required(),EqualTo('password2',message='Passwords must match.')])
    password2=PasswordField('Confirm password',validators=[Required()])
    submit=SubmitField('Register')
    #校验邮箱是否已被注册
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
    #校验用户名是否被占用
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
#密码修改表单
class ChangePasswordForm(Form):
    old_password = PasswordField('Old password',validators=[Required()])
    password=PasswordField('New password',validators=[Required(),EqualTo('password2',message='Passwords must match')])
    password2=PasswordField('Confirm password',validators=[Required()])
    submit=SubmitField('Update Password')

#重置密码请求表单，发送验证的email
class PasswordResetRequestForm(Form):
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    submit = SubmitField('Reset Password')
#重置密码表单
class PasswordResetForm(Form):
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('Password',validators=[Required(),EqualTo('password2',message='Passwords must match.')])
    password2 = PasswordField('Confirm password',validators=[Required()])
    submit = SubmitField('Reset Password')
    # 校验邮箱是否已被注册
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')
#用户信息修改表单
class EditProfileForm(Form):
    name = StringField('Real name',validators=[Required(),Length(2,64)])
    location = StringField('location',validators=[Length(0,64)])
    about_me=TextAreaField('about me')
    submit = SubmitField('Submit')

class EditProfileAdminForm(Form):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    username = StringField('Username',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Username must have only letters,numbers,dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role=SelectField('Role',coerce=int)
    name=StringField('Real name',validators=[Length(2,64)])
    location = StringField('Location',validators=[Length(0,64)])
    about_me=TextAreaField('About me')
    submit=SubmitField('Submit')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data != self.user.email and \
            User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if field.data != self.user.username and \
            User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class ChangeEmailForm(Form):
    email = StringField('Email',validators=[Required(),Length(1.64),Email()])
    password=PasswordField('Password',validators=[Required()])
    submit = SubmitField('Update Email Address')
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
