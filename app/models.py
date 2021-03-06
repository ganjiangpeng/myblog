# coding=utf-8
from flask_wtf import Form
from werkzeug.security import generate_password_hash,check_password_hash
from . import db
from flask_login import UserMixin,AnonymousUserMixin
from . import login_manager
from flask import current_app,request,url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib
from datetime import datetime
import hashlib
import bleach
from markdown import markdown
from app.exceptioins import ValidationError

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#定义权限常量
class Permission:
    FOLLOW=0x01
    COMMENT=0x02
    WRITE_ARTICLES=0x03
    MODERATE_COMMENTS=0x04
    ADMINISTER=0x80
#权限表模型
class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True,index=True)
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User',backref='role',lazy='dynamic')
    def __repr__(self):
        return '<Role %r>' %self.name
    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.FLLOW|
                    Permission.COMMENT|
                    Permission.WRITE_ARTICLES,True),
            'Moderator':(
                    Permission.FLLOW|
                    Permission.COMMENT|
                    Permission.WRITE_ARTICLES|
                    Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
        }
        for r in roles:
            role=Role.query.filter_by(name=r).first()
            if role is None:
                role=Role(name=r)
            role.permissions=roles[r][0]
            role.default=roles[r][1]
            db.session.add(role)
        db.session.commit()

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html=db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment',backref='post',lazy='dynamic')
    #数据转换成json
    def to_json(self):
        json_post = {
            'url':url_for('api.get_post',id=self.id,_external=True),
            'body':self.body,
            'body_html':self.body_html,
            'timestamp':self.timestamp,
            'author':url_for('api.get_user',id=self.author_id,_external=True),
            'comments':url_for('api.get_post_comments',id=self.id,_external=True),
            'comment_count':self.comments.count()
        }
        return json_post
    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == "":
            raise ValidationError('post does not have a body')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
            timestamp=forgery_py.date.date(True),
            author=u)
            db.session.add(p)
            db.session.commit()
    @staticmethod
    def on_change_body(target,value,oldvalue,initiator):
        allowed_tags=['a','addr','acronym','b', 'blockquote', 'code',
            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
            'h1', 'h2', 'h3', 'p']
        target.body_html= bleach.linkify(bleach.clean(markdown(value,output_format='html'),
                                                      tags=allowed_tags,strip=True))
db.event.listen(Post.body,'set',Post.on_change_body)


class Follow(db.Model):
    __tablename__ = "follows"
    follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow(),index=True)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a','abbr','acronym','b','code','em','i','strong']
        target.body_html=bleach.linkify(bleach.clean(
            markdown(value,output_format='html'),
            tags=allowed_tags,strip=True))
db.event.listen(Comment.body,'set',Comment.on_changed_body)
#用户表模型
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id=db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    email=db.Column(db.String(64),unique=True,index=True)
    password_hash=db.Column(db.String(128))
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean,default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    create_at = db.Column(db.DateTime,default=datetime.utcnow)
    last_seen = db.Column(db.DateTime,default=datetime.utcnow)
    avatar_hash=db.Column(db.String(32))
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    comments = db.relationship('Comment',backref='author',lazy='dynamic')
    #关注了谁
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower',lazy='joined'),
                               lazy='dynamic',
                               cascade='all,delete-orphan')
    #谁关注了我
    followers = db.relationship('Follow',
                               foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed',lazy='joined'),
                               lazy='dynamic',
                               cascade='all,delete-orphan')
    #json数据转换
    def to_json(self):
        json_user = {
            'url': url_for('api.get_post',id=self.id,_external=True),
            'username':self.username,
            'create_at':self.create_at,
            'last_seen':self.last_seen,
            'posts':url_for('api.get_user_posts',id=self.id,_external=True),
            'followed_posts':url_for('api.get_user_followed_posts',id=self.id,_external=True),
            'post_count':self.posts.count()
        }

    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower=self,followed=user)
            db.session.add(f)

    def unfollow(self,user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def __repr__(self):
        return '<User %r>' %self.username

    #设置密码方法
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    #验证密码
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    #生成token邮件
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})
    #验证token
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    #重新生成验证token
    def generate_reset_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'reset':self.id})
    #验证token，更改密码
    def reset_password(self,token,new_password):
        s = Serializer(current_app.config['SECRET_KEY'],3)
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password=new_password
        db.session.add(self)
        return True
    #生成邮件修改验证token
    def generate_email_change_token(self,new_email,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'change_email':self.id,'new_email':new_email})
    #校验邮件修改请求的验证token并修改用户邮箱
    def change_email(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True




    #构造函数，用户初始化角色定义
    def __init__(self,**wargs):
        super(User, self).__init__(**wargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role=Role.query.filter_by(permissions=0xff).forst()
            else:
                self.role=Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
    #权限校验
    def can(self,permission):
        return self.role is not None and (self.role.permissions & permission) == permission
    #管理员权限校验
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
    #更新用户最后访问时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    #获取头像
    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,hash=hash,size=size,default=default,rating=rating)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(),
                     password_hash=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence())
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    #查询关注的用户的所有文章
    @property
    def followed_posts(self):
        return Post.query.join(Follow,Follow.followed_id==Post.author_id).filter(Follow.follower_id==self.id)

    #生成api令牌token
    def generate_auth_token(self,expiration):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'id':self.id})

    #校验api发送的token
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])
class AnonymousUser(AnonymousUserMixin):
    def can(self,permission):
        return False

    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser






registrations = db.Table('registrations',
                         db.Column('students_id',db.Integer,db.ForeignKey('students.id')),
                         db.Column('classes_id',db.Integer,db.ForeignKey('classes.id'))
                         )

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String)
    classes = db.relationship('Class',
                              secondary=registrations,
                              backref=db.backref('students',lazy='dynamic'),
                              lazy='dynamic')

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String)



