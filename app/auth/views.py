# coding=utf-8
from flask import render_template,url_for,redirect,flash,request
from flask_login import login_user
from . import auth
from ..models import User,Role
from .forms import LoginForm,EditProfileAdminForm,ChangeEmailForm,RegistrationForm,ChangePasswordForm,PasswordResetRequestForm,PasswordResetForm,EditProfileForm
from flask_login import login_required,logout_user,current_user
from ..decorators import admin_required
from .. import db
from ..email import send_email

#访问前动作
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))
#用户登录视图
@auth.route('/login',methods=['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html',form=form)

#用户登出视图
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have been logged out.')
    return redirect(url_for('main.index'))

#用户注册视图
@auth.route('/register',methods=['POST','GET'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,'Confirm Your Account','auth/email/confirm',user=user,token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)
#接受用户认证视图
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash('your are a confirmed user.')
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account.Thinks!')
    else:
        flash('The confirmation link is incalid or has expired.')
    return redirect(url_for('main.index'))

#发送用户认证信息视图
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm your Account','auth/email/confirm',user=current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

#用户为验证默认页面视图
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
#用户修改密码视图
@auth.route('/change_password',methods=['POST','GET'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password=form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template('auth/change_password.html',form=form)

#找回密码--发送验证邮件
@auth.route('/reset',methods=['POST','GET'])
def password_reset_request():
    if not current_user.is_anonymous:
        redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email,
                        'Reset your password',
                        'auth/email/reset_password',
                        user=user,
                        token=token,
                        next=request.args.get('next'))
            flash('An email with instructions to reset your password has been '
            'sent to you.')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)

#找回密码--验证信息及修改密码
@auth.route('/reset/<token>',methods=['POST','GET'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form= PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            redirect(url_for('main.index'))
        if user.reset_password(token,form.password.data):
            flash('Your password has been update.')
            return redirect(url_for('auth.login'))
        else:
            flash('Some errors for change password.')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)

#普通用户修改信息
@auth.route('/edit-profile',methods=['POST','GET'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('main.user',username=current_user.username))
    form.name.data=current_user.name
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('auth/edit_profile.html',form=form)
#管理员修改用户信息
@auth.route('/edit-profile/<int:id>',methods=["POST","GET"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email=form.email.data
        user.username=form.username.data
        user.confirmed=form.confirmed.data
        user.role=Role.query.get(form.role.data)
        user.name=form.name.data
        user.location=form.location.data
        user.about_me=form.about_me.data
        db.session.add(user)
        flash("The Profile has been updated.")
        return redirect(url_for('main.user',username=user.username))
    form.email.data=user.email
    form.username.data=user.username
    form.name.data=user.name
    form.location.data=user.location
    form.role.data=user.role_id
    form.confirmed.data=user.confirmed
    form.about_me.data=user.about_me
    return render_template('auth/edit_profile.html',form=form)

#用户修改邮箱请求
@auth.route('/change_email',methods=['POST','GET'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email,'Confirm your email address','auth/email/change_email',user=current_user,token=token)
            flash('An email with instructions to confirm your new email')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template('auth/change_email.html',form=form)

#修改邮箱信息请求验证及邮箱更改
@auth.route('/change_email/<token>',methods=['POST','GET'])
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))

@auth.route('/insert_roles')
def insert_roles():
    try:
        Role.insert_roles()
        return 'success!'
    except Exception,e:
        return e.message

@auth.route('/test')
def test1():
    return request.endpoint
@auth.route('/test1')
@login_required
def test2():
    return 'you need login to access this page'
@auth.route('/test_admin')
def test_admin():
    return request.environ['wsgi.url_scheme']
    return '%s'%current_user.is_administrator()

